"""Unit tests for the single-song build.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from build_song import build, main_file_text
from paths import REPO_ROOT, SINGLE_SONG_TEMPLATE


class MainFile(unittest.TestCase):
    def test_the_song_is_swapped_in(self):
        text = main_file_text("a\n\\include{pisnicky/abychtuzil}\nb\n", "lonelystranger")
        self.assertEqual(text, "a\n\\include{pisnicky/lonelystranger}\nb\n")

    def test_the_real_template_has_one_include_line(self):
        text = main_file_text((REPO_ROOT / SINGLE_SONG_TEMPLATE).read_text(encoding="utf-8"), "x")
        self.assertEqual(text.count("\\include{pisnicky/x}"), 1)

    def test_a_template_without_or_with_two_includes_is_rejected(self):
        for template in ("no include", "\\include{pisnicky/a}\n\\include{pisnicky/b}"):
            with self.assertRaises(ValueError):
                main_file_text(template, "x")


class UnknownSong(unittest.TestCase):
    def test_an_unknown_id_is_reported_before_anything_is_written(self):
        with self.assertRaises(FileNotFoundError):
            build(REPO_ROOT, "no-such-song-id")


if __name__ == "__main__":
    unittest.main()
