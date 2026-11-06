"""Unit tests for the artists registry.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from paths import REPO_ROOT
from registry import check_entries, derive_label, normalise, read_entries


class DeriveLabel(unittest.TestCase):
    def test_a_person_is_written_first_name_first(self):
        self.assertEqual(derive_label("Plíhal, Karel"), "Karel Plíhal")

    def test_any_other_name_is_its_own_label(self):
        self.assertEqual(derive_label("Simon & Garfunkel"), "Simon & Garfunkel")


class Normalise(unittest.TestCase):
    def test_defaults_are_filled_in(self):
        artist = normalise({"slug": "kryl", "name": "Kryl, Karel"})
        self.assertEqual(artist, {"slug": "kryl", "name": "Kryl, Karel", "label": "Karel Kryl",
                                  "link_label": "Karel Kryl", "sort": "Kryl, Karel",
                                  "kind": "artist", "section": True})


class CheckEntries(unittest.TestCase):
    def test_valid_entries_have_no_errors(self):
        self.assertEqual(check_entries([{"slug": "abba", "name": "ABBA", "section": False}]), [])

    def test_each_kind_of_problem_is_reported(self):
        errors = check_entries([
            {"name": "No slug"},
            {"slug": "a", "name": " "},
            {"slug": "b", "name": "B", "section": "yes"},
            {"slug": "c", "name": "C", "kind": "band"},
            {"slug": "c", "name": "C again"},
            {"slug": "d", "name": "D", "colour": "red"},
        ])
        self.assertEqual(len(errors), 6)
        for part in ("missing 'slug'", "'name' is empty", "'section' must be bool",
                     "'kind' must be one of", "duplicate slug", "unknown field 'colour'"):
            self.assertTrue(any(part in error for error in errors), part)


class TheRealRegistry(unittest.TestCase):
    def test_it_is_valid(self):
        self.assertEqual(check_entries(read_entries(REPO_ROOT)), [])


if __name__ == "__main__":
    unittest.main()
