"""Unit tests for escaping plain text as TeX.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from tex_text import escape_tex


class EscapeTex(unittest.TestCase):
    def test_special_characters_are_escaped(self):
        self.assertEqual(escape_tex("R&B 100% #1 a_b {x} ~ ^ $ \\"),
                         r"R\&B 100\% \#1 a\_b \{x\} \textasciitilde{} \textasciicircum{} \$ \textbackslash{}")

    def test_non_breaking_space_is_a_tie(self):
        self.assertEqual(escape_tex("a\u00a0b"), "a~b")

    def test_plain_text_and_accents_stay(self):
        self.assertEqual(escape_tex("Eště, Žaba - Praha--Prčice"), "Eště, Žaba - Praha--Prčice")
