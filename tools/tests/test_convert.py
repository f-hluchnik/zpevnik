"""Unit tests of the converter on the whole book: speed.

Run from the repository root: python3 -m unittest discover -s tools
"""
import time
import unittest

from paths import REPO_ROOT
from songs import read_songs, song_paths

MAX_SECONDS = 5  # the whole book (J1)


class WholeBook(unittest.TestCase):
    def test_every_song_is_read_in_time(self):
        start = time.perf_counter()
        songs = read_songs(REPO_ROOT)
        self.assertLess(time.perf_counter() - start, MAX_SECONDS)
        self.assertEqual(len(songs), len(song_paths(REPO_ROOT)))
