"""Unit tests for the artist part of the contents (R11).

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from artist_toc import artist_part_tex, heading_tex, index_tex, index_text, ordered_artists, sections_tex
from check_registry import Artist
from songs import Song


def artist(slug: str, name: str, label: str | None = None, kind: str = "artist",
           section: bool = True, sort: str | None = None) -> Artist:
    return Artist(slug=slug, name=name, label=label or name, link_label=label or name,
                  sort=sort or name, kind=kind, section=section)


def song(song_id: str, title: str, *, toctitle: str | None = None, alttitles: tuple[str, ...] = (),
         artists: tuple[str, ...] = (), collections: tuple[str, ...] = ()) -> Song:
    return Song(song_id, title, toctitle, alttitles, artists, collections)


KRYL = artist("karelkryl", "Kryl, Karel", "Karel Kryl")
ABBA = artist("abba", "ABBA")
FILMY = artist("filmy", "z pohádek,\nher", "filmová hudba", kind="collection", sort="filmy")
CASH = artist("johnnycash", "Cash, Johnny", "Johnny Cash")
CHOMOR = artist("cechomor", "Čechomor")


class OrderedArtists(unittest.TestCase):
    def test_sorted_by_czech_collation_of_the_sort_key(self):
        self.assertEqual([a["slug"] for a in ordered_artists([CHOMOR, KRYL, CASH, ABBA])],
                         ["abba", "johnnycash", "cechomor", "karelkryl"])

    def test_collections_come_last(self):
        zz = artist("zz", "Zz")
        self.assertEqual([a["slug"] for a in ordered_artists([FILMY, zz, ABBA])], ["abba", "zz", "filmy"])

    def test_entry_without_section_is_left_out(self):
        self.assertEqual(ordered_artists([artist("x", "X", section=False), ABBA]), [ABBA])


class IndexText(unittest.TestCase):
    def test_artist_is_indexed_under_its_heading(self):
        self.assertEqual(index_text(KRYL), "Kryl, Karel")

    def test_collection_uses_its_short_label(self):
        self.assertEqual(index_text(FILMY), "filmová hudba")


class IndexTex(unittest.TestCase):
    def test_one_linked_line_per_artist_in_two_columns(self):
        tex = index_tex([ABBA, artist("simongarfunkel", "Simon & Garfunkel")])
        self.assertIn("\\hyt{podleinterpreta}\n", tex)
        self.assertIn("\\begin{multicols}{2}", tex)
        self.assertIn("\\hylo{abba}{ABBA}\\par\n\\hylo{simongarfunkel}{Simon \\& Garfunkel}\\par\n", tex)


class HeadingTex(unittest.TestCase):
    def test_line_break_in_the_name_is_a_forced_break(self):
        self.assertEqual(heading_tex(FILMY), "z pohádek,\\\\her")

    def test_special_characters_are_escaped(self):
        self.assertEqual(heading_tex(artist("x", "Suchý & Šlitr")), "Suchý \\& Šlitr")


class SectionsTex(unittest.TestCase):
    def test_heading_target_and_songs_in_title_order(self):
        songs = [song("b", "Beta", artists=("abba",)), song("a", "Alfa", artists=("abba",)),
                 song("c", "Other", artists=("karelkryl",))]
        tex = sections_tex([ABBA], songs)
        self.assertIn("\\subsection*{ABBA}\n\\hyt{abba}\n\\hylo{a}{Alfa}\n\n\\hylo{b}{Beta}\n\n", tex)
        self.assertNotIn("Other", tex)

    def test_songs_are_listed_under_their_page_title_not_the_toc_title(self):
        tex = sections_tex([ABBA], [song("w", "Waterloo", toctitle="Waterloo (ABBA)", artists=("abba",))])
        self.assertIn("\\hylo{w}{Waterloo}\n", tex)

    def test_alternative_title_has_its_own_entry_in_order(self):
        songs = [song("a", "Zebra", alttitles=("Alfa",), artists=("abba",)),
                 song("b", "Beta", artists=("abba",))]
        tex = sections_tex([ABBA], songs)
        self.assertLess(tex.index("\\emph{Alfa} (Zebra)"), tex.index("{Beta}"))
        self.assertLess(tex.index("{Beta}"), tex.index("{Zebra}"))

    def test_song_with_two_artists_is_listed_in_both_sections(self):
        songs = [song("m", "Mojí", artists=("abba", "karelkryl"))]
        tex = sections_tex([ABBA, KRYL], songs)
        self.assertEqual(tex.count("\\hylo{m}{Mojí}"), 2)

    def test_collection_songs_are_listed_in_the_collection_section(self):
        tex = sections_tex([FILMY], [song("t", "Theme", artists=(), collections=("filmy",))])
        self.assertIn("\\subsection*{z pohádek,\\\\her}\n\\hyt{filmy}\n\\hylo{t}{Theme}\n", tex)

    def test_song_without_artist_is_in_no_section(self):
        self.assertNotIn("\\hylo", sections_tex([ABBA], [song("a", "Alfa")]))

    def test_artist_without_songs_keeps_its_heading(self):
        self.assertIn("\\hyt{abba}\n\\end{multicols}", sections_tex([ABBA], []))


class ArtistPartTex(unittest.TestCase):
    def test_index_rule_sections_in_this_order(self):
        tex = artist_part_tex([KRYL, ABBA], [song("a", "Alfa", artists=("abba",))])
        self.assertLess(tex.index("\\hylo{abba}{ABBA}\\par"), tex.index("\\rule{10cm}"))
        self.assertLess(tex.index("\\rule{10cm}"), tex.index("\\subsection*{ABBA}"))
        self.assertLess(tex.index("\\subsection*{ABBA}"), tex.index("\\subsection*{Kryl, Karel}"))


if __name__ == "__main__":
    unittest.main()
