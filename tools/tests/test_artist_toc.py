"""Unit tests for the artist part of the contents .

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from artist_toc import artist_part_tex, heading_tex, index_tex, index_text, ordered_artists, sections_tex
from registry import Artist
from songbook import Song
from .songs_builder import make_song


def artist(slug: str, name: str, label: str | None = None, kind: str = "artist",
           section: bool = True, sort: str | None = None) -> Artist:
    return Artist(slug=slug, name=name, label=label or name, link_label=label or name,
                  sort=sort or name, kind=kind, section=section)


def song(song_id: str, title: str, *, toctitle: str | None = None, alttitles: tuple[str, ...] = (),
         artists: tuple[str, ...] = (), collections: tuple[str, ...] = ()) -> Song:
    return make_song(song_id, title, toctitle, alt_titles=alttitles, artists=artists, collections=collections)


KRYL = artist("karelkryl", "Kryl, Karel", "Karel Kryl")
ABBA = artist("abba", "ABBA")
FILMY = artist("filmy", "z pohádek,\nher", "filmová hudba", kind="collection", sort="filmy")
CASH = artist("johnnycash", "Cash, Johnny", "Johnny Cash")
CHOMOR = artist("cechomor", "Čechomor")


def songs_of(*artists: Artist) -> list[Song]:
    """One song for each artist (in a collection, if it is one)."""
    return [song(a["slug"], "Song", **{"collections" if a["kind"] == "collection" else "artists": (a["slug"],)})
            for a in artists]


class OrderedArtists(unittest.TestCase):
    def test_sorted_by_czech_collation_of_the_sort_key(self):
        registry = [CHOMOR, KRYL, CASH, ABBA]
        self.assertEqual([a["slug"] for a in ordered_artists(registry, songs_of(*registry))],
                         ["abba", "johnnycash", "cechomor", "karelkryl"])

    def test_collections_come_last(self):
        zz = artist("zz", "Zz")
        registry = [FILMY, zz, ABBA]
        self.assertEqual([a["slug"] for a in ordered_artists(registry, songs_of(*registry))],
                         ["abba", "zz", "filmy"])

    def test_entry_without_section_is_left_out(self):
        no_section = artist("x", "X", section=False)
        self.assertEqual(ordered_artists([no_section, ABBA], songs_of(no_section, ABBA)), [ABBA])

    def test_artist_without_a_song_among_the_songs_is_left_out(self):
        self.assertEqual(ordered_artists([KRYL, ABBA], songs_of(ABBA)), [ABBA])


class IndexText(unittest.TestCase):
    def test_artist_is_indexed_under_its_heading(self):
        self.assertEqual(index_text(KRYL), "Kryl, Karel")

    def test_collection_uses_its_short_label(self):
        self.assertEqual(index_text(FILMY), "filmová hudba")


class IndexTex(unittest.TestCase):
    def test_one_linked_line_per_artist_in_two_columns(self):
        tex = index_tex([ABBA, artist("simongarfunkel", "Simon & Garfunkel")])
        self.assertIn("\\zptarget{podleinterpreta}\n", tex)
        self.assertIn("\\begin{multicols}{2}", tex)
        self.assertIn("\\zpcontentsentry{abba}{ABBA}\\par\n\\zpcontentsentry{simongarfunkel}{Simon \\& Garfunkel}\\par\n", tex)


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
        self.assertIn("\\subsection*{ABBA}\n\\zptarget{abba}\n\\zpcontentsentry{a}{Alfa}\n\n\\zpcontentsentry{b}{Beta}\n\n", tex)
        self.assertNotIn("Other", tex)

    def test_songs_are_listed_under_their_page_title_not_the_toc_title(self):
        tex = sections_tex([ABBA], [song("w", "Waterloo", toctitle="Waterloo (ABBA)", artists=("abba",))])
        self.assertIn("\\zpcontentsentry{w}{Waterloo}\n", tex)

    def test_alternative_title_has_its_own_entry_in_order(self):
        songs = [song("a", "Zebra", alttitles=("Alfa",), artists=("abba",)),
                 song("b", "Beta", artists=("abba",))]
        tex = sections_tex([ABBA], songs)
        self.assertLess(tex.index("\\emph{Alfa} (Zebra)"), tex.index("{Beta}"))
        self.assertLess(tex.index("{Beta}"), tex.index("{Zebra}"))

    def test_song_with_two_artists_is_listed_in_both_sections(self):
        songs = [song("m", "Mojí", artists=("abba", "karelkryl"))]
        tex = sections_tex([ABBA, KRYL], songs)
        self.assertEqual(tex.count("\\zpcontentsentry{m}{Mojí}"), 2)

    def test_collection_songs_are_listed_in_the_collection_section(self):
        tex = sections_tex([FILMY], [song("t", "Theme", artists=(), collections=("filmy",))])
        self.assertIn("\\subsection*{z pohádek,\\\\her}\n\\zptarget{filmy}\n\\zpcontentsentry{t}{Theme}\n", tex)

    def test_the_columns_are_not_stretched_to_the_page_bottom(self):
        self.assertIn("\\begin{multicols}{2}\\raggedcolumns\n", sections_tex([ABBA], []))

    def test_song_without_artist_is_in_no_section(self):
        self.assertNotIn("\\zpcontentsentry", sections_tex([ABBA], [song("a", "Alfa")]))

    def test_artist_without_songs_keeps_its_heading(self):
        self.assertIn("\\zptarget{abba}\n\\end{multicols}", sections_tex([ABBA], []))


class ArtistPartTex(unittest.TestCase):
    def test_index_rule_sections_in_this_order(self):
        tex = artist_part_tex([KRYL, ABBA], [song("a", "Alfa", artists=("abba",)),
                                             song("k", "Kryl", artists=("karelkryl",))])
        self.assertLess(tex.index("\\zpcontentsentry{abba}{ABBA}\\par"), tex.index("\\zprule{\\textwidth}"))
        self.assertLess(tex.index("\\zprule{\\textwidth}"), tex.index("\\subsection*{ABBA}"))
        self.assertLess(tex.index("\\subsection*{ABBA}"), tex.index("\\subsection*{Kryl, Karel}"))
