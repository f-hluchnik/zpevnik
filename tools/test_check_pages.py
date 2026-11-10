"""Unit tests for reading the include lines and the page checkpoints.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from check_pages import SONG_INCLUDE, song_pages
from paths import LEGACY_SONGS_DIR, SONGS_DIR


class SongInclude(unittest.TestCase):
    def test_songinclude(self):
        self.assertEqual(SONG_INCLUDE.search("\\songinclude{alfa}").group(1), "alfa")

    def test_a_plain_include_is_not_a_song(self):
        self.assertIsNone(SONG_INCLUDE.search("\\include{songs/alfa}"))

    def test_other_includes_are_not_songs(self):
        self.assertIsNone(SONG_INCLUDE.search("\\include{shared-pages/introduction}"))


class SongPages(unittest.TestCase):
    def pages_in(self, folder: Path) -> list[tuple[str, int, int]]:
        """song_pages of a one-song checkout whose song folder is `folder`."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / folder).mkdir()
            (root / "generated").mkdir()
            (root / "zpevnik.tex").write_text("\\setcounter{page}{2}\n\\input{generated/include}\n")
            (root / "generated" / "include.tex").write_text("\\songinclude{one}\n")
            (root / folder / "one.aux").write_text(
                f"\\@setckpt{{{folder}/one}}{{\n\\setcounter{{page}}{{3}}\n}}\n")
            songs, errors = song_pages(root)
            self.assertEqual(errors, [])
            return songs

    def test_reads_the_song_folder(self):
        self.assertEqual(self.pages_in(SONGS_DIR), [("one", 2, 1)])

    def test_reads_a_checkout_from_before_the_rename(self):
        self.assertEqual(self.pages_in(LEGACY_SONGS_DIR), [("one", 2, 1)])


if __name__ == "__main__":
    unittest.main()
