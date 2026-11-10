"""Unit tests for the generated front-matter macros and pages.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from edition import Book, Edition, Selection
from edition_tex import macros_tex, pages_tex, source_text

BOOK = Book("Ještě mi chvilku zpívej", "František Hluchník", 2019, "https://github.com/f-hluchnik/zpevnik", "full")
SHARED_PAGES = {"cover": "shared-pages/cover", "halftitle": "shared-pages/halftitle",
                "titlepage": "shared-pages/titlepage"}


def edition(name: str, **changes) -> Edition:
    """An edition with the shared pages and nothing else, changed as given."""
    fields = dict(name=name, title=BOOK.title, subtitle=None, editors=(), pages=SHARED_PAGES,
                  cover_image="images/cover_image.jpg", imprint=None, before_songs=(), after_contents=(),
                  selection=Selection(True, frozenset(), frozenset()))
    return Edition(**{**fields, **changes})


class Macros(unittest.TestCase):
    def test_the_base_edition_is_not_derived(self):
        tex = macros_tex(BOOK, edition("full"), 733)
        self.assertIn("\\newif\\ifzpderived\n", tex)
        self.assertNotIn("\\zpderivedtrue", tex)
        self.assertIn("\\newcommand*{\\zpeditionsubtitle}{}\n", tex)

    def test_any_other_edition_is_derived_and_has_its_own_facts(self):
        tex = macros_tex(BOOK, edition("lite", title="Lite & co", subtitle="výběr", editors=("A", "B")), 25)
        self.assertIn("\\zpderivedtrue\n", tex)
        self.assertIn("\\newcommand*{\\zpeditiontitle}{Lite \\& co}\n", tex)
        self.assertIn("\\newcommand*{\\zpeditionsubtitle}{výběr}\n", tex)
        self.assertIn("\\newcommand*{\\zpeditioneditors}{A, B}\n", tex)
        self.assertIn("\\newcommand*{\\zpeditionsongcount}{25}\n", tex)
        self.assertIn("\\newcommand*{\\zpbooktitle}{Ještě mi chvilku zpívej}\n", tex)

    def test_the_source_is_printed_without_its_scheme(self):
        self.assertEqual(source_text("https://github.com/f-hluchnik/zpevnik"), "github.com/f-hluchnik/zpevnik")


class Pages(unittest.TestCase):
    def test_pages_are_included_and_the_imprint_fragment_is_input(self):
        tex = pages_tex(edition("lite", imprint="editions/lite/credits",
                                before_songs=("editions/lite/a", "editions/full/b")))
        self.assertIn("\\newcommand*{\\zptitlepage}{\\include{shared-pages/titlepage}}\n", tex)
        self.assertIn("\\newcommand*{\\zpimprintslot}{\\input{editions/lite/credits}}\n", tex)
        self.assertIn("\\newcommand*{\\zpbeforesongs}{\\include{editions/lite/a}\\include{editions/full/b}}\n", tex)
        self.assertIn("\\newcommand*{\\zpaftercontents}{}\n", tex)

    def test_no_imprint_fragment_leaves_the_slot_empty(self):
        self.assertIn("\\newcommand*{\\zpimprintslot}{}\n", pages_tex(edition("lite")))


if __name__ == "__main__":
    unittest.main()
