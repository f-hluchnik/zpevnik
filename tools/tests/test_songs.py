"""Unit tests for reading the songs in songs/ and leaving out the hidden ones.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from paths import HIDDEN_SONGS, SONGS_DIR
from songs import SongReadError, published, read_songs, song_paths
from songbook.model import plain
from .songs_builder import make_song


def write_songs(root: str, **songs: str) -> Path:
    """A repository with the given song files (`id=text`)."""
    songs_dir = Path(root) / SONGS_DIR
    songs_dir.mkdir()
    for song_id, text in songs.items():
        (songs_dir / f"{song_id}.tex").write_text(text, encoding="utf-8")
    return Path(root)


class ReadSongs(unittest.TestCase):
    def test_reads_all_songs_in_file_name_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_songs(tmp, b="\\song{B}\n\\toctitle{B (x)}\n\\alttitle{b1}\n\\alttitle{b2}\n",
                               a="\\song{A}\n")
            a, b = read_songs(root)
            self.assertEqual([song.id for song in (a, b)], ["a", "b"])
            self.assertEqual((plain(b.title), b.toc_title, b.alt_titles), ("B", "B (x)", ("b1", "b2")))
            self.assertEqual([path.stem for path in song_paths(root)], ["a", "b"])

    def test_a_song_the_converter_rejects_is_an_error_naming_its_file_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_songs(tmp, a="\\song{A}\n\\vers{a}\n\n\\vers{\\foo{b}}\n")
            with self.assertRaisesRegex(SongReadError, r"^songs/a\.tex:4: "):
                read_songs(root)

    def test_song_without_title_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SongReadError):
                read_songs(write_songs(tmp, a="no title here\n"))


class Published(unittest.TestCase):
    SONGS = [make_song("alfa", "Alfa"), make_song("beta", "Beta")]

    def test_hidden_songs_are_left_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / HIDDEN_SONGS).parent.mkdir(parents=True)
            (Path(tmp) / HIDDEN_SONGS).write_text("# why\nalfa  # the rights holder asked\n")
            self.assertEqual([song.id for song in published(self.SONGS, Path(tmp))], ["beta"])

    def test_without_the_list_every_song_is_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(published(self.SONGS, Path(tmp)), self.SONGS)
