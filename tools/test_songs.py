"""Unit tests for reading the songs in pisnicky/.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from songs import Song, find_arguments, read_songs, read_title


class ReadTitle(unittest.TestCase):
    def test_title_with_nested_braces(self):
        text = "\\hyt{x}\n\\song{Bella ciao\\footnote{\\uv{a}}} \\artist{}\n"
        self.assertEqual(read_title(text, "song", "x.tex"), "Bella ciao\\footnote{\\uv{a}}")

    def test_missing_command_is_none(self):
        self.assertIsNone(read_title("\\song{A}\n", "toctitle", "x.tex"))

    def test_command_must_start_a_line(self):
        self.assertIsNone(read_title("% \\song{A}\n", "song", "x.tex"))

    def test_two_lines_are_an_error(self):
        with self.assertRaises(ValueError):
            read_title("\\song{A}\n\\song{B}\n", "song", "x.tex")


class FindArguments(unittest.TestCase):
    def test_every_line_with_the_command(self):
        text = "\\song{A}\n\\alttitle{B {c}}\nx \\alttitle{no}\n\\alttitle{D}\n"
        self.assertEqual(find_arguments(text, "alttitle"), ["B {c}", "D"])


class Groups(unittest.TestCase):
    def test_artists_then_collections_without_repeats(self):
        self.assertEqual(Song("a", "A", None, (), ("x", "y"), ("filmy", "x")).groups, ("x", "y", "filmy"))

    def test_song_without_tags_has_no_group(self):
        self.assertEqual(Song("a", "A", None).groups, ())


class SortTitle(unittest.TestCase):
    def test_toctitle_wins_over_song(self):
        self.assertEqual(Song("a", "Marie", "Marie (Klus)").sort_title, "Marie (Klus)")

    def test_song_without_toctitle(self):
        self.assertEqual(Song("a", "Felicit\\`{a}", None).sort_title, "Felicità")


class ReadSongs(unittest.TestCase):
    def test_reads_all_songs_in_file_name_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            songs_dir = Path(tmp) / "pisnicky"
            songs_dir.mkdir()
            (songs_dir / "b.tex").write_text(
                "\\song{B}\n\\toctitle{B (x)}\n\\alttitle{b1}\n\\alttitle{b2}\n", encoding="utf-8")
            (songs_dir / "a.tex").write_text("\\song{A}\n", encoding="utf-8")
            self.assertEqual(read_songs(Path(tmp)),
                             [Song("a", "A", None), Song("b", "B", "B (x)", ("b1", "b2"))])

    def test_reads_the_artist_and_collection_tags(self):
        with tempfile.TemporaryDirectory() as tmp:
            songs_dir = Path(tmp) / "pisnicky"
            songs_dir.mkdir()
            (songs_dir / "a.tex").write_text(
                "\\song{A} \\artist[Label]{x}\\artist{y}\n\\collection{filmy}\n", encoding="utf-8")
            (songs_dir / "b.tex").write_text("\\song{B}\n\\artist{}\n", encoding="utf-8")
            a, b = read_songs(Path(tmp))
            self.assertEqual((a.artists, a.collections), (("x", "y"), ("filmy",)))
            self.assertEqual((b.artists, b.collections), ((), ()))

    def test_song_without_title_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            songs_dir = Path(tmp) / "pisnicky"
            songs_dir.mkdir()
            (songs_dir / "a.tex").write_text("no title here\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                read_songs(Path(tmp))


if __name__ == "__main__":
    unittest.main()
