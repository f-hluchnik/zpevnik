"""Unit tests for reading the include lines (H3).

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from check_pages import SONG_INCLUDE


class SongInclude(unittest.TestCase):
    def test_songinclude(self):
        self.assertEqual(SONG_INCLUDE.search("\\songinclude{alfa}").group(1), "alfa")

    def test_include_before_h3(self):
        self.assertEqual(SONG_INCLUDE.search("\\include{pisnicky/alfa}").group(1), "alfa")

    def test_other_includes_are_not_songs(self):
        self.assertIsNone(SONG_INCLUDE.search("\\include{preamble/uvod}"))


if __name__ == "__main__":
    unittest.main()
