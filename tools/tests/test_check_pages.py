"""Unit tests for reading the include order and the page checkpoints.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from check_pages import checkpoint_page, included_files, song_id, song_pages
from paths import BOOK_AUX_NAME


def write_compiled_book(output_dir: Path, files: list[tuple[str, int | None]]) -> None:
    """The auxiliary files of a compiled book: the main .aux lists the included files
    in order, and each has its own .aux with the page counter after it (None: no .aux)."""
    (output_dir / BOOK_AUX_NAME).write_text(
        "\\relax\n" + "".join(f"\\@input{{{name}.aux}}\n" for name, _ in files))
    for name, page_after in files:
        if page_after is not None:
            aux = output_dir / f"{name}.aux"
            aux.parent.mkdir(parents=True, exist_ok=True)
            aux.write_text(f"\\relax\n\\@setckpt{{{name}}}{{\n\\setcounter{{page}}{{{page_after}}}\n}}\n")


class SongId(unittest.TestCase):
    def test_a_file_of_the_song_folder_is_a_song(self):
        self.assertEqual(song_id("songs/alfa"), "alfa")

    def test_other_included_files_are_not_songs(self):
        self.assertIsNone(song_id("shared-pages/contents"))
        self.assertIsNone(song_id("editions/full/introduction"))


class SongPages(unittest.TestCase):
    def pages(self, files: list[tuple[str, int | None]]) -> tuple[list, list[str]]:
        with tempfile.TemporaryDirectory() as tmp:
            write_compiled_book(Path(tmp), files)
            return song_pages(Path(tmp))

    def test_a_song_starts_where_the_file_before_it_ends(self):
        songs, errors = self.pages([("shared-pages/cover", 3), ("editions/full/introduction", 5),
                                    ("songs/one", 6), ("songs/two", 8), ("shared-pages/contents", 10)])
        self.assertEqual(errors, [])
        self.assertEqual(songs, [("one", 5, 1), ("two", 6, 2)])

    def test_files_are_read_in_the_order_of_the_main_aux(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_compiled_book(Path(tmp), [("songs/b", 3), ("songs/a", 4)])
            self.assertEqual(included_files(Path(tmp)), ["songs/b", "songs/a"])

    def test_a_missing_checkpoint_is_reported(self):
        _songs, errors = self.pages([("shared-pages/cover", 2), ("songs/one", None)])
        self.assertEqual(errors, ["songs/one: no page checkpoint in songs/one.aux"])

    def test_a_song_with_nothing_before_it_is_reported(self):
        _songs, errors = self.pages([("songs/one", 2)])
        self.assertEqual(errors, ["one: no included file before it to start from"])

    def test_a_book_that_is_not_compiled_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            songs, errors = song_pages(Path(tmp))
        self.assertEqual(songs, [])
        self.assertIn("not compiled?", errors[0])

    def test_the_checkpoint_of_another_file_is_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_compiled_book(Path(tmp), [("songs/one", 3)])
            (Path(tmp) / "songs" / "two.aux").write_text("\\@setckpt{songs/one}{\n\\setcounter{page}{9}\n}\n")
            self.assertIsNone(checkpoint_page(Path(tmp), "songs/two"))
