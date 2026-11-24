"""Unit tests for the output formats.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from formats import PRINT, PRINT_BLACK, PRINT_CMYK, SCREEN, is_black_ink, is_cmyk, needs_black_scores, pretex


class Definitions(unittest.TestCase):
    def test_the_screen_format_defines_nothing_so_the_book_stays_as_it_is(self):
        self.assertEqual(pretex(SCREEN), "")

    def test_the_print_format_only_says_that_the_book_is_for_paper(self):
        self.assertEqual(pretex(PRINT), "\\def\\zpprint{}")

    def test_the_black_print_format_makes_the_chords_and_the_scores_black(self):
        self.assertEqual(pretex(PRINT_BLACK),
                         "\\def\\zpprint{}\\def\\zpchordcolor{black}\\def\\zpscoresuffix{-black}")

    def test_the_cmyk_print_format_has_the_chords_in_cmyk_and_the_scores_black(self):
        self.assertEqual(pretex(PRINT_CMYK),
                         "\\def\\zpprint{}\\def\\zpchordcolor{chordcmyk}\\def\\zpscoresuffix{-black}")


ALL = (SCREEN, PRINT, PRINT_BLACK, PRINT_CMYK)


class Inks(unittest.TestCase):
    def test_only_the_black_print_format_is_in_one_ink(self):
        self.assertEqual([name for name in ALL if is_black_ink(name)], [PRINT_BLACK])

    def test_only_the_cmyk_print_format_is_in_cmyk(self):
        self.assertEqual([name for name in ALL if is_cmyk(name)], [PRINT_CMYK])

    def test_the_formats_for_one_ink_and_for_cmyk_take_the_black_scores(self):
        self.assertEqual([name for name in ALL if needs_black_scores(name)], [PRINT_BLACK, PRINT_CMYK])
