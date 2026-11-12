"""Unit tests for the song order.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from collation import section, sort_key


def order(*titles: str) -> list[str]:
    return sorted(titles, key=sort_key)


class Collation(unittest.TestCase):
    def assertSorted(self, *titles: str) -> None:
        """The titles are given in the expected order."""
        self.assertEqual(order(*reversed(titles)), list(titles))
        self.assertEqual(order(*titles), list(titles))

    def test_space_before_letter(self):
        self.assertSorted("A Horse With No Name", "Abych tu žil")
        self.assertSorted("A pak", "Alberta", "Až nám přijdou míru brát")

    def test_ch_after_h(self):
        self.assertSorted("Hurikán", "Hzzz", "Change the World", "Chodím po Praze", "Ivan")
        self.assertEqual(section("Change the World"), "CH")
        self.assertEqual(section("Hurikán"), "H")

    def test_ch_inside_a_word(self):
        # "ch" is one letter between h and i, also inside words
        self.assertSorted("Mack", "Mach", "Mai")

    def test_ch_needs_adjacent_letters(self):
        # "c h" across a space is not the digraph
        self.assertSorted("C hrabě", "Cz", "Ch")  # Ch is a later letter than c+z

    def test_caron_letters_are_first_pass(self):
        self.assertSorted("Cyril", "Čerešně", "Dalibor")
        self.assertSorted("Rum", "Řeka", "Sam")
        self.assertSorted("Sůl", "Šlapej dál", "Tam")
        self.assertSorted("Zima", "Žaba")
        self.assertEqual(section("Čerešně"), "Č")
        self.assertEqual(section("Řeka"), "Ř")
        self.assertEqual(section("Šlapej dál"), "Š")
        self.assertEqual(section("Žaba"), "Ž")

    def test_d_caron_sorts_with_d(self):
        self.assertSorted("Ďáblovy námluvy", "Dalibor", "Dobrý den")
        self.assertEqual(section("Ďáblovy námluvy"), "D")

    def test_digits_after_z_caron(self):
        self.assertSorted("Žaba", "1605")

    def test_punctuation_ignored(self):
        self.assertSorted("Praha--Prčice", "Prahy")
        self.assertSorted("Ain't No Grave", "Alberta")  # Aint < Albe
        self.assertSorted("Beskyde, Beskyde", "Beskydy")
        self.assertEqual(sort_key("Praha--Prčice")[:3], sort_key("PrahaPrčice")[:3])

    def test_second_pass_accents(self):
        self.assertSorted("Mama", "Máma", "Mamba")
        self.assertSorted("Pes", "Pés", "Pěs", "Pet")
        self.assertSorted("Sun", "Sún", "Sůn", "Sup")

    def test_first_pass_beats_second(self):
        # a different letter outweighs any accent difference
        self.assertSorted("Máma", "Mamba")

    def test_third_pass_case(self):
        self.assertSorted("mama", "Mama")

    def test_last_pass_punctuation_breaks_ties(self):
        self.assertEqual(len({sort_key(t) for t in ("Hej hej", "Hej, hej", "Hej. hej")}), 3)
        self.assertSorted("Hej hej", "Hej, hej", "Hej. hej")  # code point order

    def test_l_stroke(self):
        self.assertSorted("Lam", "Łam", "Lan")

    def test_unknown_letter_is_an_error(self):
        with self.assertRaises(ValueError):
            sort_key("Ωmega")
