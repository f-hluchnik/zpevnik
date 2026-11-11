"""Unit tests for the parts of the PDF diff that need no PDF.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from pdfdiff import names_the_build


class NamesTheBuild(unittest.TestCase):
    def test_the_version_with_or_without_the_build_number(self):
        self.assertTrue(names_the_build("8.33.71"))
        self.assertTrue(names_the_build("8.33.?"))

    def test_the_month_of_the_build_date(self):
        self.assertTrue(names_the_build("listopadu"))

    def test_other_words_are_compared(self):
        for word in ("verze", "8.33", "11.", "2019–2026", "1.2.3a"):
            with self.subTest(word=word):
                self.assertFalse(names_the_build(word))


if __name__ == "__main__":
    unittest.main()
