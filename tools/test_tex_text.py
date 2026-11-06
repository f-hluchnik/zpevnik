"""Unit tests for the TeX-to-text conversion of titles.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from tex_text import brace_group, escape_tex, plain_text


class PlainText(unittest.TestCase):
    def test_footnote_removed(self):
        self.assertEqual(plain_text(r"Bella ciao\footnote{\textit{\uv{Sbohem, krásko}} - italská {píseň}}"),
                         "Bella ciao")

    def test_uv_and_textit_unwrapped(self):
        self.assertEqual(plain_text(r"\uv{Ahoj} \textit{světe}"), "Ahoj světe")

    def test_accent_macros(self):
        self.assertEqual(plain_text(r"Felicit\`{a}"), "Felicità")
        self.assertEqual(plain_text(r"\'a \v{c}\v r \c{c}"), "á čř ç")
        self.assertEqual(plain_text(r"Caf\'e"), "Café")

    def test_ties_and_groups(self):
        self.assertEqual(plain_text("Praha--Prčice"), "Praha--Prčice")
        self.assertEqual(plain_text("A~B {C}"), "A B C")

    def test_escapes(self):
        self.assertEqual(plain_text(r"Rock \& Roll"), "Rock & Roll")

    def test_unknown_macro_is_an_error(self):
        with self.assertRaises(ValueError):
            plain_text(r"Title \foo{x}")


class Tex(unittest.TestCase):
    def test_special_characters_are_escaped(self):
        self.assertEqual(escape_tex("R&B 100% #1 a_b {x} ~ ^ $ \\"),
                         r"R\&B 100\% \#1 a\_b \{x\} \textasciitilde{} \textasciicircum{} \$ \textbackslash{}")

    def test_non_breaking_space_is_a_tie(self):
        self.assertEqual(escape_tex("a\u00a0b"), "a~b")

    def test_plain_text_and_accents_stay(self):
        self.assertEqual(escape_tex("Eště, Žaba - Praha--Prčice"), "Eště, Žaba - Praha--Prčice")


class BraceGroup(unittest.TestCase):
    def test_nested_and_escaped_braces(self):
        self.assertEqual(brace_group(r"x{a{b}\}c}d", 1), (r"a{b}\}c", 10))

    def test_unbalanced_is_an_error(self):
        with self.assertRaises(ValueError):
            brace_group("{abc", 0)


if __name__ == "__main__":
    unittest.main()
