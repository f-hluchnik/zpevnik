"""Unit tests for the output formats.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from formats import PRINT, PRINT_BLACK, SCREEN, pretex


class Definitions(unittest.TestCase):
    def test_the_screen_format_defines_nothing_so_the_book_stays_as_it_is(self):
        self.assertEqual(pretex(SCREEN), "")

    def test_the_print_format_only_says_that_the_book_is_for_paper(self):
        self.assertEqual(pretex(PRINT), "\\def\\zpprint{}")

    def test_the_black_print_format_adds_the_chord_colour(self):
        self.assertEqual(pretex(PRINT_BLACK), "\\def\\zpprint{}\\def\\zpchordcolor{black}")


if __name__ == "__main__":
    unittest.main()
