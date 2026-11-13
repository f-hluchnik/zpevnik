"""Unit tests for the letter part of the contents .

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from letter_toc import anchor, entries, letters_tex
from songbook import Song

from .songs_builder import make_song


def song(song_id: str, title: str, toctitle: str | None = None, *alttitles: str) -> Song:
    return make_song(song_id, title, toctitle, alt_titles=alttitles)


class Anchor(unittest.TestCase):
    def test_plain_letters_and_ch(self):
        self.assertEqual(anchor("A"), "A")
        self.assertEqual(anchor("CH"), "CH")

    def test_letters_with_caron_are_doubled(self):
        self.assertEqual([anchor(x) for x in "ČŘŠŽ"], ["Cc", "Rr", "Ss", "Zz"])


class Entries(unittest.TestCase):
    def test_song_and_alternative_title(self):
        found = list(entries([song("a", "Keď som išiel", None, "Čerešně")]))
        self.assertEqual([(e.song_id, e.text, e.sort_text) for e in found],
                         [("a", "Keď som išiel", "Keď som išiel"),
                          ("a", r"\emph{Čerešně} (Keď som išiel)", "Čerešně")])

    def test_toctitle_is_printed_and_orders_the_song(self):
        (entry,) = entries([song("a", "Marie", "Marie (Klus)")])
        self.assertEqual((entry.text, entry.sort_text), ("Marie (Klus)", "Marie (Klus)"))

    def test_special_characters_are_escaped(self):
        (entry,) = entries([song("a", "Rock & Roll")])
        self.assertEqual(entry.text, r"Rock \& Roll")


class LettersTex(unittest.TestCase):
    SONGS = [
        song("zebra", "Zebra"),
        song("cerny", "Černá", None, "Abeceda"),
        song("chata", "Chata"),
        song("dablova", "Ďáblova"),
        song("cizi", "Cizí"),
    ]

    def test_sections_follow_the_alphabet_and_ch_follows_h(self):
        tex = letters_tex(self.SONGS)
        order = [line for line in tex.splitlines() if line.startswith("\\zptarget{")]
        self.assertEqual(order, ["\\zptarget{A}", "\\zptarget{C}", "\\zptarget{Cc}", "\\zptarget{D}", "\\zptarget{CH}", "\\zptarget{Z}"])

    def test_no_section_for_d_caron(self):
        self.assertNotIn("\\subsection*{Ď}", letters_tex(self.SONGS))

    def test_letter_row_links_to_every_section_and_the_artist_index(self):
        tex = letters_tex(self.SONGS)
        self.assertIn(r"\hyperlink{A}{A}\hfill \hyperlink{C}{C}\hfill \hyperlink{Cc}{Č}\hfill "
                      r"\hyperlink{D}{D}\hfill \hyperlink{CH}{CH}\hfill \hyperlink{Z}{Z}", tex)
        self.assertIn(r"\zpscreenorprint{\hyperlink{podleinterpreta}{řazení podle interpretů}}{}", tex)

    def test_the_letter_row_is_for_the_screen_only(self):
        tex = letters_tex(self.SONGS)
        self.assertLess(tex.index("\\zpscreenorprint{\\hyperlink{A}{A}"), tex.index("\\vspace{5pt}\n\n}{}"))

    def test_alternative_title_is_listed_under_its_own_letter(self):
        tex = letters_tex(self.SONGS)
        a_section = tex.split("\\zptarget{A}")[1].split("\\zptarget{C}")[0]
        self.assertIn(r"\zpcontentsentry{cerny}{\emph{Abeceda} (Černá)}", a_section)

    def test_entries_are_ordered_within_a_section(self):
        tex = letters_tex([song("b", "Beta"), song("a", "Alfa"), song("ab", "A beta")])
        entry_lines = [line for line in tex.splitlines() if line.startswith("\\zpcontentsentry{") and "}{" in line][-3:]
        self.assertEqual(entry_lines, [r"\zpcontentsentry{ab}{A beta}", r"\zpcontentsentry{a}{Alfa}", r"\zpcontentsentry{b}{Beta}"])
