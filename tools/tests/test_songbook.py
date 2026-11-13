"""Unit tests of the converter (tools/songbook/): the structure rules (D-163), the model (D-164)
and the TeX rules the songs rely on; snapshots of real songs, frozen as fixtures.

Run from the repository root: python3 -m unittest discover -s tools
Update the snapshots after an intended change of the model:
    UPDATE_SNAPSHOTS=1 python3 -m unittest discover -s tools -p test_songbook.py
"""
import json
import os
import unittest
from pathlib import Path

from songbook import SongSyntaxError, grammar, parse_song, read_song
from songbook.inline import MUSIC
from songbook.parser import SONG_LEVEL, STANDALONE
from songbook.dump import to_json
from songbook.model import (Block, ChordPart, ChordPosition, CueBlock, FootnoteRef, Note, Remark, RepeatEnd,
                            RepeatStart, Rule, RuleKind, Run, Segment, Speaker, SpeakerBlock, Style, plain)

SNAPSHOT_DIR = Path(__file__).parent / "songbook_snapshots"
UPDATE = os.environ.get("UPDATE_SNAPSHOTS") == "1"
JSON_INDENT = 1


def song(body: str, title: str = "Title"):
    return parse_song("test", f"\\song{{{title}}} \\artist{{}}\n\n{body}\n")


def first_block(body: str) -> Block:
    return song(body).body[0]


def line_texts(block) -> list[str]:
    """Each line as text, a chord written [X] before its text."""
    def segment(item):
        chord = "[" + "".join(part.text for part in item.chord.parts) + "]" if item.chord else ""
        return chord + plain(item.text)
    return ["".join(segment(item) if isinstance(item, Segment) else "|" for item in line.items)
            for line in block.lines]


class TexRules(unittest.TestCase):
    def test_a_space_after_a_control_word_is_skipped(self):
        [chord] = [item.chord for item in first_block(r"\vers{\chord{F\kk m}a}").lines[0].items]
        self.assertEqual(chord.parts, (ChordPart("F"), ChordPart("♯", ChordPosition.SUPERSCRIPT), ChordPart("m")))

    def test_braces_keep_the_space_after_a_chord_symbol(self):
        row = first_block(r"\vers{\chords{Dm\maj{} Dm} in C\kk{} dur}").lines[0].items
        self.assertEqual(len([item for item in row if item.chord]), 2)
        self.assertEqual(plain(row[-1].text), " in C♯ dur")

    def test_a_slash_before_anything_but_a_note_name_is_text(self):
        row = first_block(r"\vers{\chord{D\add{6/9}}a \chord{1. E\7 / 2. C}b}").lines[0].items
        self.assertEqual([part.text for item in row for part in item.chord.parts], ["D", "6/9", "1. E", "7", " / 2. C"])

    def test_a_mark_at_the_end_of_a_line_leaves_no_empty_segment(self):
        lines = first_block("\\vers{\\rep{a} \\\\\nb}").lines
        self.assertEqual([type(item).__name__ for item in lines[0].items], ["RepeatStart", "Segment", "RepeatEnd"])

    def test_a_chord_inside_a_word_as_zpevnik_sty_tests_it(self):
        """A character right before the chord and a letter right after it; checked against TeX's
        own test on every chord of the book (session 24, D-165)."""
        cases = {
            r"slip a\chord{A}way": True,
            r"slip a \chord{A}away": False,                  # a space before the chord
            r"la-\chord{A}la": False,                        # TeX puts a discretionary after a hyphen
            r"\emph{yester\chord{A}day}": True,             # inside one group
            r"\emph{dotý}\chord{A}\emph{ká}": False,         # the italic correction ends the group
            r"wor\chord{A}\emph{d}": False,                  # the next token is a command
            r"\rec{\chord{A}Co}": True,                      # the "/" of \rec is a character
            r"ab\gap{1}\chord{A}cd": False,
            r"ab\chords{A}cd": False,                        # \chords never splits a word
            r"a\chord{A}čas": True,                           # a two-byte letter
            r"a\chord{A}2": False,
        }
        for source, expected in cases.items():
            with self.subTest(source):
                items = first_block(f"\\vers{{{source}}}").lines[0].items
                self.assertEqual(any(item.in_word for item in items if isinstance(item, Segment)), expected)

    def test_a_chord_ends_at_the_end_of_its_group(self):
        block = first_block(r"\vers{\rep{\chord{A}la} da \chord{B}di}")
        self.assertEqual(line_texts(block), ["|[A]la| da [B]di"])

    def test_a_chord_reaches_over_a_group_that_starts_after_it(self):
        self.assertEqual(line_texts(first_block(r"\vers{\chord{A}la \emph{da} di}")), ["[A]la da di"])

    def test_spaces_collapse_and_lines_are_trimmed(self):
        self.assertEqual(line_texts(first_block("\\vers{\n  a   b \\\\\n  c  \n}")), ["a b", "c"])

    def test_ligatures_and_quotes_as_the_pdf_prints_them(self):
        block = first_block(r"\vers{a -- b, it's \uv{c} \enquote{d} \enquote*{e} x~y}")
        self.assertEqual(line_texts(block), ["a – b, it’s „c“ ‘d’ “e” x\u00a0y"])


class Structure(unittest.TestCase):
    def test_a_cue_refers_to_the_last_part_with_its_label(self):
        body = song("\\chorus{a}\n\n\\vers[1]{b}\n\n\\chorus{c}\n\n\\cue{R}").body
        self.assertEqual(body[3].cue.target, 2)

    def test_a_cue_without_an_earlier_part_is_an_error(self):
        with self.assertRaisesRegex(SongSyntaxError, "no part"):
            song("\\chorus[1]{a}\n\n\\cue{R}")

    def test_a_cue_after_an_empty_line_is_a_block_with_the_rest_of_its_line(self):
        body = song("\\chorus{a}\n\n\\cue{R} \\ntimes{2}").body
        self.assertIsInstance(body[1], CueBlock)
        self.assertEqual(plain(body[1].line.items[0].text), "×2")

    def test_what_follows_a_part_in_its_paragraph_goes_on_its_last_line(self):
        body = song("\\chorus{a}\n\n\\vers[1]{b\\\\c} \\cue{R} \\note{fade}").body
        self.assertEqual(len(body), 2)
        *_, cue, note = [item for item in body[1].lines[-1].items if not isinstance(item, Segment)]
        self.assertEqual((cue.label, cue.target), ("R", 0))
        self.assertEqual(note, Note((Run("fade"),)))

    def test_two_parts_in_one_paragraph_are_two_blocks(self):
        body = song("\\intro{\\chords{A}} \\solo[1]{\\chords{B}}").body
        self.assertEqual([item.key for item in body], ["I", "S1"])

    def test_a_speaker_alone_and_inside_a_part(self):
        body = song("\\speaker{A}{hi}\n\n\\vers[1]{\\speaker{B}{yo}}").body
        self.assertEqual(body[0], SpeakerBlock("A", body[0].lines))
        self.assertEqual(body[1].lines[0].items[0], Speaker("B"))

    def test_a_remark_is_lines_of_text_between_the_parts(self):
        body = song("\\chorus{a}\n\n\\remark{Tuning \\emph{D}\\\\\nthe second line}\n\n\\vers[1]{b}").body
        self.assertEqual([type(item) for item in body], [Block, Remark, Block])
        self.assertEqual([plain(line) for line in body[1].lines], ["Tuning D", "the second line"])

    def test_a_remark_takes_no_text_after_it_in_its_paragraph(self):
        with self.assertRaisesRegex(SongSyntaxError, "follows no part"):
            song("\\remark{a} b")

    def test_a_remark_holds_no_music(self):
        with self.assertRaisesRegex(SongSyntaxError, "only in a part"):
            song("\\remark{\\chord{A}a}")

    def test_a_repeat_may_span_lines(self):
        items = [item for line in first_block("\\vers{\\rep{a\\\\b}}").lines for item in line.items]
        self.assertIsInstance(items[0], RepeatStart)
        self.assertIsInstance(items[-1], RepeatEnd)

    def test_rules_and_group_breaks(self):
        body = song("\\vers{a\n\\groupbreak\nb}\n\n\\blockrule{10}\n\n\\vers{c}\n\n\\partrule\n\\vers{d}").body
        self.assertEqual([line.group_start for line in body[0].lines], [False, True])
        self.assertEqual([item.kind for item in body if isinstance(item, Rule)], [RuleKind.DASHED, RuleKind.SOLID])

    def test_footnotes_are_numbered_per_song_the_title_first(self):
        parsed = song("\\vers{a\\footnote{two\\\\lines}}", title="T\\footnote{one}")
        self.assertEqual(parsed.title[-1], FootnoteRef(1))
        self.assertEqual(len(parsed.footnotes), 2)
        self.assertEqual([plain(line) for line in parsed.footnotes[1]], ["two", "lines"])

    def test_echo_and_a_chord_named_in_the_text_are_styles(self):
        runs = first_block("\\vers{a\\echo{b} \\emph{in C\\kk}}").lines[0].items[0].text
        self.assertIn(Run("b", Style.ECHO), runs)
        self.assertIn(Run("♯", Style.ITALIC | Style.SUPERSCRIPT), runs)

    def test_metadata_and_layout(self):
        parsed = parse_song("x", "\\song{T} \\artist[Label]{slug}\\artist{}\n\\alttitle{A}\\toctitle{T (x)}\n"
                                 "\\collection{c}\n\\subtitle{S}\n\\seealso{other}{Other}\n\\large\n"
                                 "\\begin{multicols}{2}\n\\vers{a}\n\\columnbreak\n\\vers{b}\n\\end{multicols}\n")
        self.assertEqual((parsed.artists[0].slug, parsed.artists[0].label, len(parsed.artists)), ("slug", "Label", 1))
        self.assertEqual((parsed.alt_titles, parsed.toc_title, parsed.collections), (("A",), "T (x)", ("c",)))
        self.assertEqual((parsed.see[0].song_id, parsed.columns, len(parsed.body)), ("other", 2, 2))


class SongFacts(unittest.TestCase):
    """What the tools ask of a song that its fields do not say directly."""

    def test_groups_are_artists_then_collections_without_repeats(self):
        parsed = parse_song("x", "\\song{T} \\artist{a}\\artist{b}\\artist{}\n\\collection{c}\n\\collection{a}\n")
        self.assertEqual(parsed.groups, ("a", "b", "c"))

    def test_a_song_without_tags_has_no_group(self):
        self.assertEqual(song("\\vers{a}").groups, ())

    def test_score_names_are_in_the_order_of_the_song(self):
        parsed = song("\\intro{\n\\score{a_intro}\n}\n\\vers[a]{x\n\\score{a_riff}\n}")
        self.assertEqual(parsed.score_names, ("a_intro", "a_riff"))

    def test_a_song_without_scores_has_none(self):
        self.assertEqual(song("\\vers{a}\n\n\\note{b}").score_names, ())


class Errors(unittest.TestCase):
    """What the converter rejects: each was in the songs once (D-135, D-163) or would print wrong."""
    CASES = {
        "unknown command": "\\vers{\\textit{a}}",
        "ends with a line break": "\\vers{a\\\\\n}",
        "empty line inside a part": "\\vers{a\n\nb}",
        "text outside a part": "\\score{x}",
        "drops the space after \\\\maj": "\\vers{\\chords{Dm\\maj Dm}}",
        "drops the space after \\\\kk": "\\vers{\\chord{\\bas{C\\kk F}}a}",
        "drops the space after \\\\bb": "\\note{in E\\bb dur}",
        "not allowed in a chord": "\\vers{\\chord{D\\gap{1}}a}",
        "math may only hold": "\\vers{$x^2$}",
        "is only in a part": "\\note{\\chord{A}a}",
        "a backslash at the end of a line": "\\vers{a\\\nchord{A}b}",
        "a sharp is": "\\vers{\\chord{\\bas{A A\\#}}a}",
        "a bass note written as": "\\vers{\\chords{C/G}}",
        "unknown environment": "\\begin{center}\\vers{a}\\end{center}",
        "after an empty line": "\\vers{a\\\\\n\\\\\nb}",
    }

    def test_each_is_an_error_with_its_line(self):
        for message, body in self.CASES.items():
            with self.subTest(message), self.assertRaisesRegex(SongSyntaxError, message) as caught:
                song(body)
            self.assertGreaterEqual(caught.exception.line, 3)

    def test_a_song_needs_a_title(self):
        with self.assertRaisesRegex(SongSyntaxError, "no \\\\song"):
            parse_song("x", "\\vers{a}")


class Grammar(unittest.TestCase):
    def test_every_command_of_the_grammar_has_exactly_one_handler(self):
        song_level = (grammar.METADATA | grammar.BLOCKS | grammar.REMARKS | grammar.RULES
                      | grammar.ENVIRONMENT_COMMANDS | grammar.LAYOUT_COMMANDS)
        self.assertEqual(set(SONG_LEVEL), set(song_level))
        self.assertEqual(set(MUSIC), set(grammar.PART_COMMANDS))
        self.assertEqual(set(STANDALONE), set(grammar.MODE_DEPENDENT))


class Snapshots(unittest.TestCase):
    """Ten songs that together use every construct, frozen as fixtures so editing a song does not
    break the test; the expected model is their JSON dump."""

    def test_each_fixture_matches_its_snapshot(self):
        fixtures = sorted(SNAPSHOT_DIR.glob("*.tex"))
        self.assertEqual(len(fixtures), 10)
        for fixture in fixtures:
            with self.subTest(fixture.stem):
                actual = json.dumps(to_json(read_song(fixture)), ensure_ascii=False, indent=JSON_INDENT) + "\n"
                expected_path = fixture.with_suffix(".json")
                if UPDATE:
                    expected_path.write_text(actual, encoding="utf-8")
                self.assertEqual(actual, expected_path.read_text(encoding="utf-8"))
