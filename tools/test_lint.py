"""Unit tests for the lints .

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from registry import Artist
from lint import (artists_ready_for_section, duplicate_titles, empty_artist_info, empty_sections,
                  chord_warnings, lint, text_problems, unknown_slugs)
from songs import Song


def artist(slug: str, section: bool = True) -> Artist:
    return Artist(slug=slug, name=slug, label=slug, link_label=slug, sort=slug,
                  kind="artist", section=section)


def song(song_id: str, title: str = "T", toctitle: str | None = None,
         artists: tuple[str, ...] = (), collections: tuple[str, ...] = ()) -> Song:
    return Song(song_id, title, toctitle, (), artists, collections)


class TextProblems(unittest.TestCase):
    def test_manual_chord_spacing_is_an_error(self):
        for macro in ("\\nc", "\\mm", "\\sm", "\\bc"):
            with self.subTest(macro=macro):
                (problem,) = text_problems("a", f"\\song{{A}} \\artist{{x}}\n\\chord{{C}}a{macro} b\n")
                self.assertIn("manual chord spacing", problem)

    def test_commands_that_only_start_like_the_old_macros_are_fine(self):
        self.assertEqual(text_problems("a", "\\song{A} \\artist{x}\n\\smash{a}\\ncol \\subtitle{b}\\coda{c}\n"), [])

    def test_renamed_commands_are_errors(self):
        for old, new in (("\\refrain{a}", "\\chorus"), ("\\refrainn{1}{a}", "\\chorus[n]"),
                         ("\\solon{1}{a}", "\\solo[n]"), ("\\cod{a}", "\\coda"),
                         ("\\sub{a}", "\\subtitle"), ("\\spk{On}{a}", "\\speaker"),
                         ("\\hyl{x}{a}", "\\seealso"), ("\\refsm{}", "\\cue{R}"),
                         ("\\refsme{}", "\\cue{R}"), ("\\bridgesm{}", "\\cue{B}"),
                         ("\\solosm{1}", "\\cue{S}"), ("\\hyt{x}", "\\hypertarget"),
                         ("\\hylo{x}{a}", "\\hyperlink"),
                         ("\\nv{a}", "\\vers{...}"), ("\\lbl{A:}", "\\speaker{A}{...}")):
            with self.subTest(old=old):
                (problem,) = text_problems("a", f"\\song{{A}} \\artist{{x}}\n{old}\n")
                self.assertIn(f"removed {old.split('{')[0]}", problem)
                self.assertIn(f"write {new}", problem)

    def test_renamed_commands_are_counted_per_command(self):
        (problem,) = text_problems("a", "\\song{A} \\artist{x}\n\\cod{a}\\cod{b}\n")
        self.assertIn("2 uses", problem)

    def test_renamed_commands_in_comments_or_after_a_line_break_are_fine(self):
        self.assertEqual(text_problems("a", "\\song{A} \\artist{x}\n% \\sub{a}\n\\vers{a}\\\\sub\n"), [])

    def test_text_outside_a_block_is_an_error(self):
        for stray in ("plain text", "\\rec{a}", "\\chords{A E}", "\\emph{rec.} a", "\\rep{\\chords{A}}"):
            with self.subTest(stray=stray):
                problems = text_problems("a", f"\\song{{A}} \\artist{{x}}\n\n\\vers{{a}}\n\n{stray}\n")
                self.assertTrue(any("outside a block" in problem for problem in problems))

    def test_blocks_separators_and_layout_are_not_outside_a_block(self):
        text = ("\\song{A} \\artist{x}\n\\note{capo 2}\n\n\\vers{a\n\nstill the verse}\n\n\\cue{R}\n\n"
                "\\begin{multicols}{2}\n\\vers{a}\n\n\\columnbreak\n\n\\vers{b}\n\n\\end{multicols}\n")
        self.assertEqual(text_problems("a", text), [])

    def test_text_inside_an_environment_is_still_outside_a_block(self):
        text = "\\song{A} \\artist{x}\n\n\\begin{multicols}{2}\n\\vers{a}\n\nloose text\n\\end{multicols}\n"
        (problem,) = text_problems("a", text)
        self.assertIn("outside a block ('loose text')", problem)

    def test_hand_written_echo_and_repeat_signs_are_errors(self):
        for written, command in (("a\\textsuperscript{\\emph{(echo)}}", "\\echo{...}"),
                                 ("$\\backslash$: a :$\\backslash$", "\\rep{...}"),
                                 ("\\textbackslash: a :\\textbackslash", "\\rep{...}")):
            with self.subTest(written=written):
                (problem,) = text_problems("a", f"\\song{{A}} \\artist{{x}}\n\\vers{{{written}}}\n")
                self.assertIn("2 uses" if "backslash" in written else "1 uses", problem)
                self.assertIn(f"write {command}", problem)

    def test_old_two_brace_verse_is_an_error(self):
        for old in ("\\vers{1}{a}", "\\vers{}{a}", "\\vers{1}\n{a}"):
            with self.subTest(old=old):
                problems = text_problems("a", f"\\song{{A}} \\artist{{x}}\n{old}\n")
                self.assertTrue(any("old \\vers" in problem for problem in problems))

    def test_block_without_text_is_an_error(self):
        for empty in ("\\bridge{}", "\\vers[3]{}", "\\chorus[2]{ }", "\\solo[1]{\n}", "\\chorus{}{text}"):
            with self.subTest(empty=empty):
                (problem,) = text_problems("a", f"\\song{{A}} \\artist{{x}}\n{empty}\n")
                self.assertIn("without text", problem)

    def test_cues_and_blocks_with_text_are_fine(self):
        self.assertEqual(text_problems("a", "\\song{A} \\artist{x}\n\\cue{B}\n\\bridge{\\cue{R}}\n\\vers[3]{=\\gap{2}\\cue{1}}\n"), [])

    def test_new_verses_are_fine(self):
        self.assertEqual(text_problems("a", "\\song{A} \\artist{x}\n\\vers[1]{a {b}}\n\\vers{a}\n"), [])

    def test_chords_or_chord_rows_silence_the_chord_warning(self):
        self.assertEqual(chord_warnings("a", "\\chord{C}x"), [])
        self.assertEqual(chord_warnings("a", "\\chords{C G}"), [])
        self.assertEqual(len(chord_warnings("a", "\\textbf{C G}")), 1)

    def test_valid_song(self):
        self.assertEqual(text_problems("a", "\\song{A} \\artist{x}\\artist{y}\n"), [])

    def test_empty_artist_is_valid(self):
        self.assertEqual(text_problems("a", "\\song{A}\n\\artist{}\n"), [])

    def test_missing_artist_line(self):
        self.assertEqual(len(text_problems("a", "\\song{A}\n")), 1)

    def test_two_artist_lines(self):
        self.assertEqual(len(text_problems("a", "\\song{A} \\artist{x}\n\\artist{y}\n")), 1)

    def test_three_artists(self):
        (problem,) = text_problems("a", "\\song{A} \\artist{x}\\artist{y}\\artist{z}\n")
        self.assertIn("3 artists", problem)

    def test_old_macro(self):
        (problem,) = text_problems("a", "\\song{A} \\artist{x}\n\\interpret{X}\n")
        self.assertIn("interpret", problem)


class RegistryLints(unittest.TestCase):
    REGISTRY = [artist("abba"), artist("filmy"), artist("small", section=False)]

    def test_unknown_slug_in_artist_or_collection(self):
        songs = [song("a", artists=("nobody",)), song("b", collections=("nothing",)), song("c", artists=("abba",))]
        found = unknown_slugs(songs, self.REGISTRY)
        self.assertEqual(len(found), 2)
        self.assertIn("'nobody' used by 1 song(s), e.g. a", found[0])

    def test_known_slugs_are_fine(self):
        self.assertEqual(unknown_slugs([song("a", artists=("abba",), collections=("filmy",))], self.REGISTRY), [])

    def test_section_without_songs_is_an_error(self):
        found = empty_sections([song("a", artists=("abba",))], self.REGISTRY)
        self.assertEqual(found, ["entry 'filmy' has a section (section = true) but no songs"])

    def test_collection_songs_fill_a_section(self):
        songs = [song("a", artists=("abba",)), song("b", collections=("filmy",))]
        self.assertEqual(empty_sections(songs, self.REGISTRY), [])

    def test_entry_without_section_needs_no_songs(self):
        self.assertNotIn("small", " ".join(empty_sections([], self.REGISTRY)))

    def test_artist_without_section_is_reported_from_the_minimum(self):
        two = [song(str(n), artists=("small",)) for n in range(2)]
        self.assertEqual(artists_ready_for_section(two, self.REGISTRY), [])
        three = two + [song("x", artists=("small",))]
        (found,) = artists_ready_for_section(three, self.REGISTRY)
        self.assertIn("'small' has no section but 3 songs", found)

    def test_artist_with_section_is_never_reported(self):
        many = [song(str(n), artists=("abba",)) for n in range(5)]
        self.assertEqual(artists_ready_for_section(many, self.REGISTRY), [])


class TitleLints(unittest.TestCase):
    def test_same_title_without_toctitle_is_reported(self):
        (found,) = duplicate_titles([song("a", "Marie"), song("b", "marie"), song("c", "Jana")])
        self.assertIn("a, b", found)

    def test_toctitle_tells_songs_apart(self):
        self.assertEqual(duplicate_titles([song("a", "Marie", "Marie (Klus)"), song("b", "Marie", "Marie (Navarová)")]), [])


class EmptyArtistInfo(unittest.TestCase):
    def test_counts_songs_without_artist_and_those_in_a_collection(self):
        songs = [song("a"), song("b", collections=("filmy",)), song("c", artists=("abba",))]
        self.assertEqual(empty_artist_info(songs), "2 songs have an empty \\artist{} (1 of them are in a collection)")


class LintTree(unittest.TestCase):
    def make(self, registry: str, **songs: str) -> Path:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp))
        (tmp / "data").mkdir()
        (tmp / "pisnicky").mkdir()
        (tmp / "data" / "artists.toml").write_text(registry, encoding="utf-8")
        for name, text in songs.items():
            (tmp / "pisnicky" / f"{name}.tex").write_text(text, encoding="utf-8")
        return tmp

    def test_clean_tree(self):
        root = self.make('[[entry]]\nslug = "abba"\nname = "ABBA"\n', a="\\song{A} \\artist{abba}\n\\chord{C}a\n")
        findings = lint(root)
        self.assertEqual((findings.errors, findings.warnings), ([], []))

    def test_song_without_chords_is_a_warning(self):
        root = self.make('[[entry]]\nslug = "abba"\nname = "ABBA"\n', a="\\song{A} \\artist{abba}\n")
        findings = lint(root)
        self.assertEqual(findings.errors, [])
        self.assertEqual(findings.warnings, ["a: no \\chord or \\chords"])

    def test_song_without_song_command_is_an_error_and_does_not_stop_the_others(self):
        root = self.make('[[entry]]\nslug = "abba"\nname = "ABBA"\n',
                         a="no title\n\\artist{abba}\n", b="\\song{B} \\artist{}\n\\artist{x}\n")
        errors = lint(root).errors
        self.assertTrue(any("a.tex: no \\song" in e for e in errors))
        self.assertTrue(any("b: 2 lines with \\artist" in e for e in errors))

    def test_unknown_slug_and_empty_section_fail(self):
        root = self.make('[[entry]]\nslug = "abba"\nname = "ABBA"\n', a="\\song{A} \\artist{nobody}\n")
        errors = lint(root).errors
        self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
