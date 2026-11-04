"""Unit tests for the include list (R9, H3).

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from generate import include_tex
from songs import Song


def song(song_id: str, title: str) -> Song:
    return Song(song_id, title, None)


class IncludeTex(unittest.TestCase):
    def test_one_songinclude_per_song_in_collation_order(self):
        tex = include_tex([song("beta", "Beta"), song("alfa", "Alfa")])
        lines = [line for line in tex.splitlines() if line.startswith("\\")]
        self.assertEqual(lines, ["\\songinclude{alfa}", "\\songinclude{beta}"])

    def test_each_first_pass_letter_gets_a_comment(self):
        tex = include_tex([song("beta", "Beta"), song("alfa", "Alfa")])
        self.assertIn("%A\n\\songinclude{alfa}\n\n%B\n\\songinclude{beta}\n", tex)

    def test_song_files_are_not_included_directly(self):
        self.assertNotIn("\\include{", include_tex([song("alfa", "Alfa")]))


if __name__ == "__main__":
    unittest.main()
