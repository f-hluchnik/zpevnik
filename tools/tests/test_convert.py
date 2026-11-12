"""Unit tests of the converter on the whole book: speed, and the same metadata as songs.py.

Run from the repository root: python3 -m unittest discover -s tools
"""
import time
import unittest

from paths import REPO_ROOT
from songbook import read_song
from songbook.model import Score, plain
from songbook.text import printed_text
from songs import parse_song, song_paths
from tex_text import plain_text

MAX_SECONDS = 5  # the whole book (J1)


class WholeBook(unittest.TestCase):
    def test_every_song_is_read_in_time(self):
        start = time.perf_counter()
        songs = [read_song(path) for path in song_paths(REPO_ROOT)]
        self.assertLess(time.perf_counter() - start, MAX_SECONDS)
        self.assertEqual(len(songs), len(song_paths(REPO_ROOT)))

    def test_the_metadata_is_what_songs_py_reads(self):
        """Two readers of the song metadata until the generator uses the converter (backlog).
        songs.py keeps the TeX characters (`'`), the converter the printed ones (’)."""
        for path in song_paths(REPO_ROOT):
            with self.subTest(path.stem):
                text = path.read_text(encoding="utf-8")
                generator, converter = parse_song(path.stem, text), read_song(path)
                self.assertEqual(plain(converter.title), printed_text(generator.plain_title))
                self.assertEqual(converter.toc_title,
                                 None if generator.toctitle is None else printed_text(generator.sort_title))
                self.assertEqual(converter.alt_titles,
                                 tuple(printed_text(plain_text(title)) for title in generator.alttitles))
                self.assertEqual(tuple(artist.slug for artist in converter.artists), generator.artists)
                self.assertEqual(converter.collections, generator.collections)
                self.assertEqual(scores(converter), generator.scores)


def scores(song) -> tuple[str, ...]:
    """The score names of a song in its order."""
    return tuple(item.name for block in song.body for line in getattr(block, "lines", ())
                 for item in line.items if isinstance(item, Score))
