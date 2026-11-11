"""Unit tests for the output formats.

Run from the repository root: python3 -m unittest discover -s tools
"""
import argparse
import contextlib
import io
import unittest

from formats import FORMATS, PRINT, PRINT_BLACK, SCREEN, add_format_argument, pretex


class Definitions(unittest.TestCase):
    def test_the_screen_format_defines_nothing_so_the_book_stays_as_it_is(self):
        self.assertEqual(pretex(SCREEN), "")

    def test_the_print_format_only_says_that_the_book_is_for_paper(self):
        self.assertEqual(pretex(PRINT), "\\def\\zpprint{}")

    def test_the_black_print_format_adds_the_chord_colour(self):
        self.assertEqual(pretex(PRINT_BLACK), "\\def\\zpprint{}\\def\\zpchordcolor{black}")


class Argument(unittest.TestCase):
    def parse(self, *arguments: str) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        add_format_argument(parser)
        return parser.parse_args(arguments)

    def test_the_default_format_is_the_screen_one(self):
        self.assertEqual(self.parse().format, SCREEN)

    def test_every_format_can_be_chosen(self):
        for name in FORMATS:
            self.assertEqual(self.parse("--format", name).format, name)

    def test_an_unknown_format_is_refused(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.parse("--format", "poster")


if __name__ == "__main__":
    unittest.main()
