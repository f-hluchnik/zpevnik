"""Unit tests for the letter part of the contents .

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from letter_toc import anchor, entries, letters_tex
from songs import Song


def song(song_id: str, title: str, toctitle: str | None = None, *alttitles: str) -> Song:
    return Song(song_id, title, toctitle, alttitles)


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

    def test_footnote_is_dropped_and_special_characters_are_escaped(self):
        (entry,) = entries([song("a", r"Rock \& Roll\footnote{about it}")])
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
        order = [line for line in tex.splitlines() if line.startswith("\\hyt{")]
        self.assertEqual(order, ["\\hyt{A}", "\\hyt{C}", "\\hyt{Cc}", "\\hyt{D}", "\\hyt{CH}", "\\hyt{Z}"])

    def test_no_section_for_d_caron(self):
        self.assertNotIn("\\subsection*{Ď}", letters_tex(self.SONGS))

    def test_letter_row_links_to_every_section_and_the_artist_index(self):
        tex = letters_tex(self.SONGS)
        self.assertIn(r"\hylo{A}{A}\hfill \hylo{C}{C}\hfill \hylo{Cc}{Č}\hfill "
                      r"\hylo{D}{D}\hfill \hylo{CH}{CH}\hfill \hylo{Z}{Z}", tex)
        self.assertIn(r"\hylo{podleinterpreta}{řazení podle interpretů}", tex)

    def test_alternative_title_is_listed_under_its_own_letter(self):
        tex = letters_tex(self.SONGS)
        a_section = tex.split("\\hyt{A}")[1].split("\\hyt{C}")[0]
        self.assertIn(r"\hylo{cerny}{\emph{Abeceda} (Černá)}", a_section)

    def test_entries_are_ordered_within_a_section(self):
        tex = letters_tex([song("b", "Beta"), song("a", "Alfa"), song("ab", "A beta")])
        entry_lines = [line for line in tex.splitlines() if line.startswith("\\hylo{") and "}{" in line][-3:]
        self.assertEqual(entry_lines, [r"\hylo{ab}{A beta}", r"\hylo{a}{Alfa}", r"\hylo{b}{Beta}"])


if __name__ == "__main__":
    unittest.main()
