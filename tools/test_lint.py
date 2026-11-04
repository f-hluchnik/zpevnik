"""Unit tests for the lints (R12).

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from check_registry import Artist
from lint import (artists_ready_for_section, duplicate_titles, empty_artist_info, empty_sections,
                  lint, text_problems, unknown_slugs)
from songs import Song


def artist(slug: str, section: bool = True) -> Artist:
    return Artist(slug=slug, name=slug, label=slug, link_label=slug, sort=slug,
                  kind="artist", section=section)


def song(song_id: str, title: str = "T", toctitle: str | None = None,
         artists: tuple[str, ...] = (), collections: tuple[str, ...] = ()) -> Song:
    return Song(song_id, title, toctitle, (), artists, collections)


class TextProblems(unittest.TestCase):
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
        root = self.make('[[entry]]\nslug = "abba"\nname = "ABBA"\n', a="\\song{A} \\artist{abba}\n")
        findings = lint(root)
        self.assertEqual((findings.errors, findings.warnings), ([], []))

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
