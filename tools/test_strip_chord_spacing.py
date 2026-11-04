"""Unit tests for the chord-spacing migration (C3a, D-123).

Examples are taken from D-123 and docs/C1-review-lists.md (song ids in the test names).
Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from chord_lists import chord_names, chordify_lines, chordify_textbf, join_chords
from chord_syntax import ends_with_chord, has_autochords
from migration_report import Report
from strip_chord_spacing import (
    add_autochords,
    chord_inside_word,
    convert,
    corpus,
    fragment,
    strip_spacing,
)
from word_decisions import JOINED_BY_OWNER, KEPT_APART_BY_OWNER

WORDS = {"tomu", "dává", "grave", "can", "fare", "and"}


def strip(src: str, words: set[str] = WORDS) -> tuple[str, Report]:
    report = Report()
    return strip_spacing(src, "song", report, words), report


def labels(report: Report) -> set[str]:
    return set(report.stats)


class ChordNames(unittest.TestCase):
    def test_a_list_of_chords(self):
        self.assertEqual(chord_names("E F\\kk m\\7 Am\\6\\bas{E} E"), "E F\\kk m\\7 Am\\6\\bas{E} E")

    def test_spacing_macros_become_single_spaces(self):  # nekdopijelih
        self.assertEqual(chord_names("D D\\7 G F\\kk F E \\nc D A D"), "D D\\7 G F\\kk F E D A D")

    def test_bass_runs_and_brackets(self):  # layla, tenkdoneduma
        self.assertIsNotNone(chord_names("\\bas{A C} Dm\\bas{D D C}"))
        self.assertIsNotNone(chord_names("F (D\\7)"))

    def test_glued_chords_and_a_trailing_dots(self):  # herecomesthesun, povestehovejs
        self.assertIsNotNone(chord_names("A\\7A\\7 F"))
        self.assertIsNotNone(chord_names("Em D Em D\\dots"))

    def test_bold_words_and_labels_are_not_chords(self):
        for text in ("Ahoj", "1.", "R.", "Tex", "I.", "Hm and more"):
            self.assertIsNone(chord_names(text), text)


class JoinChords(unittest.TestCase):
    def test_a_name_ending_with_a_control_word_keeps_its_space(self):
        self.assertEqual(join_chords(["F\\maj", "C"]), "F\\maj{} C")

    def test_the_last_name_and_plain_names_are_unchanged(self):
        self.assertEqual(join_chords(["Dm\\7", "C\\maj"]), "Dm\\7 C\\maj")


class TextbfChords(unittest.TestCase):
    def test_lonelystranger_intro(self):
        report = Report()
        out = chordify_textbf("\\intro{\\textbf{E F\\kk m\\7 Am\\6\\bas{E} E}}", "song", report)
        self.assertEqual(out, "\\intro{\\chords{E F\\kk m\\7 Am\\6\\bas{E} E}}")
        self.assertEqual(report.stats["textbf"], 1)

    def test_spacing_inside_the_list_is_dropped(self):  # majak
        out = chordify_textbf("\\textbf{C\\mm F\\mm C\\7\\mm F}", "song", Report())
        self.assertEqual(out, "\\chords{C F C\\7 F}")

    def test_bold_text_stays(self):
        src = "\\textbf{Pozor} a \\textbf{1.}"
        self.assertEqual(chordify_textbf(src, "song", Report()), src)

    def test_chords_with_a_line_break_stay_and_are_reported(self):  # blackbird, kluziste
        src = "\\textbf{C G\\\\\nD Em}"
        report = Report()
        self.assertEqual(chordify_textbf(src, "song", report), src)
        self.assertEqual(report.stats["textbf-left"], 1)

    def test_two_chords_glued_by_tex_are_reported(self):  # timeinabottle: Dm Dm\maj Dm\7
        report = Report()
        chordify_textbf("\\textbf{Dm Dm\\maj Dm\\7}", "song", report)
        self.assertEqual(report.stats["glued"], 1)
        self.assertIn("CHECK", report.lines[0])


class ChordOnlyLines(unittest.TestCase):
    def chordify(self, src: str) -> str:
        return chordify_lines(src, "song", Report())

    def test_a_bare_line(self):  # allmyloving
        self.assertEqual(self.chordify("\\chord{G}\\nc\\chord{D}\\nc\\chord{Em}"), "\\chords{G D Em}")

    def test_inside_intro(self):  # hejnovran
        self.assertEqual(self.chordify("\\intro{\\chord{F}\\nc\\chord{B}\\nc\\chord{F}}"), "\\intro{\\chords{F B F}}")

    def test_inside_solo_and_cod_wrappers_with_arguments(self):
        self.assertEqual(self.chordify("\\vers{1}{\\chord{A}\\mm\\chord{B}"), "\\vers{1}{\\chords{A B}")

    def test_nested_wrappers(self):  # jastebouzitnebudu
        self.assertEqual(self.chordify("\\intro{\\rep{\\chord{Em}\\nc\\chord{F\\kk}}}"), "\\intro{\\rep{\\chords{Em F\\kk}}}")

    def test_line_break_and_open_brace_after_the_chords(self):  # zafukane
        self.assertEqual(self.chordify("\\solo{\\chord{Em}\\nc\\chord{D}\\\\"), "\\solo{\\chords{Em D}\\\\")
        self.assertEqual(self.chordify("\\chord{G}\\nc\\chord{D}\\\\"), "\\chords{G D}\\\\")

    def test_a_name_ending_with_a_control_word_keeps_its_space(self):  # nejlipjimbylo
        self.assertEqual(self.chordify("\\chord{F\\maj}\\nc\\chord{C}"), "\\chords{F\\maj{} C}")

    def test_a_chord_with_a_space_inside_keeps_it(self):
        self.assertEqual(self.chordify("\\chord{F\\kk m\\7}\\nc\\chord{Am}"), "\\chords{F\\kk m\\7 Am}")

    def test_chords_with_lyrics_are_left_alone(self):
        for src in ("\\chord{E}I must \\chord{F}be", "knees. \\chord{F}\\nc\\chord{Am}", "\\rep{\\chord{A}text}"):
            self.assertEqual(self.chordify(src), src)

    def test_only_the_chord_line_changes(self):
        self.assertEqual(self.chordify("text\n\\chord{A}\\nc\\chord{B}\nmore"), "text\n\\chords{A B}\nmore")


class SpacingAfterChords(unittest.TestCase):
    def test_a_pause_after_a_chord_becomes_a_gap(self):  # andelska
        self.assertEqual(strip("\\refrainn{1}{\n\\chord{A}\\sm počítám \\chord{Hm}ne")[0],
                         "\\refrainn{1}{\n\\chord{A}\\gap{1}počítám \\chord{Hm}ne")

    def test_a_run_of_macros_adds_up(self):  # \sm 1, \mm 2, \nc 4, \bc 8
        self.assertEqual(strip("\\chord{A}\\nc\\mm\\sm text")[0], "\\chord{A}\\gap{7}text")
        self.assertEqual(strip("\\chord{A}\\bc text")[0], "\\chord{A}\\gap{8}text")

    def test_pause_after_a_chord_run_before_lyrics(self):  # aintnograve: two words, the pause stays
        out, _ = strip("grave\\chord{A\\4}\\mm\\chord{A}\\mm can't")
        self.assertEqual(out, "grave\\chord{A\\4}\\chord{A}\\gap{2}can't")

    def test_a_pause_inside_a_word_is_removed(self):  # letadozravani: tomu, not "to - mu"
        out, report = strip("se \\chord{G}to\\sm\\chord{G\\dm}\\sm mu\\mm \\chord{C}se")
        self.assertEqual(out, "se \\chord{G}to\\chord{G\\dm}mu \\chord{C}se")
        self.assertEqual(report.stats["pause inside a word"], 1)

    def test_a_pause_inside_a_word_known_from_the_songbook(self):  # kockanaokne
        out, _ = strip("\\chord{G}zpí\\chord{G\\kk\\dm}\\sm val", {"zpíval"})
        self.assertEqual(out, "\\chord{G}zpí\\chord{G\\kk\\dm}val")

    def test_a_pause_between_letters_nobody_decided_is_kept_and_listed(self):  # conselho
        out, report = strip("gar\\chord{G7}\\mm xyz quem")
        self.assertEqual(out, "gar\\chord{G7}\\gap{2}xyz quem")
        self.assertEqual(report.stats["CHECK, pause between letters"], 1)

    def test_a_control_word_before_the_chord_is_not_a_letter(self):  # changetheworld
        out, _ = strip("nge\\dots\\chord{F\\kk m}\\nc the")
        self.assertEqual(out, "nge\\dots\\chord{F\\kk m}\\gap{4}the")

    def test_chord_inside_word_needs_letters_on_both_sides(self):
        self.assertTrue(chord_inside_word("to\\chord{G}", "mu"))
        self.assertFalse(chord_inside_word("to \\chord{G}", "mu"))
        self.assertFalse(chord_inside_word("to\\chord{G} ", "mu"))
        self.assertFalse(chord_inside_word("to\\chord{G}", "...u"))

    def test_spacing_between_chords_is_removed(self):  # lonelystranger
        out, report = strip("\\chord{F\\kk m\\7}\\nc\\mm \\chord{Am\\6}\\nc\\mm\\sm\\chord{E}\\\\")
        self.assertEqual(out, "\\chord{F\\kk m\\7}\\chord{Am\\6}\\chord{E}\\\\")
        self.assertEqual(report.stats["run of chords"], 2)

    def test_spacing_after_the_last_chord_of_a_line_is_removed(self):
        self.assertEqual(strip("a \\chord{A}\\mm\\\\")[0], "a \\chord{A}\\\\")
        self.assertEqual(strip("{\\chord{A}\\mm}")[0], "{\\chord{A}}")


class SpacingBetweenLyrics(unittest.TestCase):
    def test_a_gap_inside_lyrics_becomes_a_gap(self):
        self.assertEqual(strip("hello\\sm world")[0], "hello\\gap{1}world")

    def test_a_gap_at_a_line_start_becomes_a_gap(self):
        self.assertEqual(strip("text\n\\mm start")[0], "text\n\\gap{2}start")

    def test_a_gap_before_inline_chords_is_deliberate(self):  # cervenareka
        out, _ = strip("nebaví.\\mm\\chords{H\\7}")
        self.assertEqual(out, "nebaví.\\gap{2}\\chords{H\\7}")


class SpacingBeforeChords(unittest.TestCase):
    def test_after_a_space_or_brace_it_is_removed(self):
        self.assertEqual(strip("a \\mm\\chord{C}x")[0], "a \\chord{C}x")
        self.assertEqual(strip("\\vers{1}{\\mm\\chord{C}x")[0], "\\vers{1}{\\chord{C}x")

    def test_a_space_typed_after_the_macro_is_a_word_gap(self):  # je\nc \chord{Am}hojnost
        self.assertEqual(strip("je\\nc \\chord{Am}hojnost")[0], "je \\chord{Am}hojnost")

    def test_after_punctuation_a_space_is_kept(self):
        self.assertEqual(strip("knows,\\mm\\chord{H}me")[0], "knows, \\chord{H}me")

    def test_inside_a_word_known_from_the_songbook_it_is_removed(self):
        out, report = strip("to\\sm\\chord{G}mu")
        self.assertEqual(out, "to\\chord{G}mu")
        self.assertEqual(report.stats["removed inside a word"], 1)

    def test_no_letter_after_means_inside_a_word(self):  # batalion: po\sm\chord{Em}\sm há
        self.assertEqual(strip("po\\sm\\chord{Em}\\sm há")[0], "po\\chord{Em}há")

    def test_two_words_known_from_the_songbook_keep_a_space(self):
        out, report = strip("grave\\sm\\chord{G}can")
        self.assertEqual(out, "grave \\chord{G}can")
        self.assertEqual(report.stats["kept apart"], 1)

    def test_owner_joined_invisible(self):  # lonelystranger
        self.assertEqual(strip("invisi\\sm\\chord{F\\kk \\7}ble")[0], "invisi\\chord{F\\kk \\7}ble")

    def test_owner_joined_goliáš_in_two_steps(self):  # davidagolias
        out, _ = strip("Go\\sm\\chord{G\\7}li\\mm\\chord{C}áš!")
        self.assertEqual(out, "Go\\chord{G\\7}li\\chord{C}áš!")

    def test_owner_kept_apart_pairs(self):  # sirokyhluboky, chattanoogachoochoo
        self.assertEqual(strip("jsem já\\sm\\chord{C}panenku")[0], "jsem já \\chord{C}panenku")
        self.assertEqual(strip("fare\\mm\\chord{E\\7}and")[0], "fare \\chord{E\\7}and")

    def test_the_owner_overrules_the_songbook(self):
        out, _ = strip("go\\mm\\chord{G}li", {"goli", "go", "li"})
        self.assertEqual(out, "go\\chord{G}li")

    def test_anything_else_keeps_a_space_and_is_listed(self):  # never join words on a guess
        out, report = strip("abc\\sm\\chord{G}def")
        self.assertEqual(out, "abc \\chord{G}def")
        self.assertEqual(report.stats["CHECK, kept a space"], 1)
        self.assertIn("CHECK", report.lines[0])

    def test_every_owner_answer_is_covered(self):
        self.assertEqual(len(JOINED_BY_OWNER & KEPT_APART_BY_OWNER), 0)
        for left, right in KEPT_APART_BY_OWNER:
            out, _ = strip(f"{left}\\mm\\chord{{G}}{right}", set())
            self.assertEqual(out, f"{left} \\chord{{G}}{right}")


class Fragments(unittest.TestCase):
    def test_letters_next_to_the_gap_skip_chords(self):
        self.assertEqual(fragment("a Go\\chord{G}li", True), "goli")
        self.assertEqual(fragment("li\\chord{C}áš!", False), "liáš")

    def test_other_spacing_is_a_word_boundary(self):
        self.assertEqual(fragment("x\\sm ab", True), "ab")
        self.assertEqual(fragment("\\chord{A}\\sm há", False), "")

    def test_macros_end_a_fragment(self):
        self.assertEqual(fragment("nge\\dots", True), "")


class Corpus(unittest.TestCase):
    def test_words_touching_spacing_or_gaps_are_skipped(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "song.tex"
            path.write_text("\\chord{A}tomu je\\sm jinak dále ab\\gap{2}cd ef % tajné\n", encoding="utf-8")
            self.assertEqual(corpus([path]), {"tomu", "dále", "ef"})


class Autochords(unittest.TestCase):
    def test_after_the_song_line(self):
        self.assertEqual(add_autochords("\\song{A} \\artist{b}\n\n\\vers{1}{x}\n"),
                         "\\song{A} \\artist{b}\n\\autochords\n\n\\vers{1}{x}\n")

    def test_after_a_title_with_a_footnote(self):  # bellaciao
        self.assertEqual(add_autochords("\\song{A\\footnote{x {y}}}\n\\artist{}\nz"),
                         "\\song{A\\footnote{x {y}}}\n\\autochords\n\\artist{}\nz")

    def test_it_is_added_once(self):
        once = add_autochords("\\song{A}\nx\n")
        self.assertEqual(add_autochords(once), once)

    def test_a_song_without_a_title_is_left_alone(self):
        self.assertEqual(add_autochords("x\n"), "x\n")

    def test_the_song_line_is_the_last_line(self):
        self.assertEqual(add_autochords("\\song{A}"), "\\song{A}\n\\autochords")

    def test_detection(self):
        self.assertTrue(has_autochords("\\song{A}\n\\autochords\n"))
        self.assertFalse(has_autochords("\\song{A}\n% \\autochords\n"))
        self.assertFalse(has_autochords("\\song{A}\n\\autochordsx\n"))


class ChordSyntax(unittest.TestCase):
    def test_a_text_ending_with_a_chord(self):
        self.assertTrue(ends_with_chord("a\\chord{A\\bas{F\\kk}}"))
        self.assertTrue(ends_with_chord("a\\chord{A} \t"))
        self.assertFalse(ends_with_chord("a\\chord{A}b"))


class WholeSong(unittest.TestCase):
    def test_lonelystranger(self):  # the example of docs/C1-chord-spacing.md
        src = ("\\song{Lonely Stranger} \\artist{ericclapton}\n\n"
               "\\intro{\\textbf{E F\\kk m\\7 Am\\6\\bas{E} E}}\n\n"
               "\\vers{1}{\n"
               "\\chord{E}I must \\chord{F\\kk m\\7}\\sm be\\mm\\sm \\chord{C\\kk m\\7}\\mm invisi\\sm\\chord{F\\kk \\7}ble, \\chord{G}no\\\\\n"
               "\\chord{E}I have \\chord{F\\kk m\\7}\\nc\\mm \\chord{Am\\6\\bas{E}}\\nc\\mm\\sm\\chord{E}\n"
               "}\n")
        expected = ("\\song{Lonely Stranger} \\artist{ericclapton}\n\n"
                    "\\intro{\\chords{E F\\kk m\\7 Am\\6\\bas{E} E}}\n\n"
                    "\\vers{1}{\n"
                    "\\chord{E}I must \\chord{F\\kk m\\7}\\gap{1}be \\chord{C\\kk m\\7}\\gap{2}invisi\\chord{F\\kk \\7}ble, \\chord{G}no\\\\\n"
                    "\\chord{E}I have \\chord{F\\kk m\\7}\\chord{Am\\6\\bas{E}}\\chord{E}\n"
                    "}\n")
        report = Report()
        self.assertEqual(convert(src, "lonelystranger", report, set()), expected)
        self.assertEqual(add_autochords(expected).splitlines()[1], "\\autochords")

    def test_the_converted_text_is_stable(self):
        src = "\\song{A}\n\\chord{A}\\sm x \\chord{B}y\n"
        once = convert(src, "a", Report(), set())
        self.assertEqual(convert(once, "a", Report(), set()), once)


if __name__ == "__main__":
    unittest.main()
