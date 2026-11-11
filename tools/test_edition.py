"""Unit tests for the book facts and the edition files.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from edition import Book, EditionError, read_book, read_edition
from paths import BOOK_FILE
from songs import Song

BOOK_TOML = '''title = "Kniha"
author = "Autor"
start_year = 2019
source = "https://example.org/kniha"
base_edition = "full"
'''
FULL_TOML = '''all = true
cover_image = "../../images/cover.jpg"
before_songs = []
after_contents = []
[pages]
cover = "shared"
halftitle = "shared"
titlepage = "shared"
'''
BOOK = Book("Kniha", "Autor", 2019, "https://example.org/kniha", "full")
SONGS = [Song("alfa", "Alfa", None, artists=("kryl",)), Song("beta", "Beta", None),
         Song("gama", "Gama", None, collections=("filmy",))]
SLUGS = {"kryl", "filmy", "abba"}
PAGES_SHARED = '[pages]\ncover = "shared"\nhalftitle = "shared"\ntitlepage = "shared"\n'


class Repository:
    """A temporary checkout with the book file, the full edition and a cover image."""

    def __init__(self, tmp: str):
        self.root = Path(tmp)
        self.write(str(BOOK_FILE), BOOK_TOML)
        self.write("editions/full/edition.toml", FULL_TOML)
        self.write("images/cover.jpg", "")

    def write(self, path: str, text: str) -> None:
        (self.root / path).parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).write_text(text, encoding="utf-8")

    def edition(self, toml: str, name: str = "lite", **files: str):
        """Write editions/<name>/edition.toml and the given files of its folder, then read it."""
        self.write(f"editions/{name}/edition.toml", toml)
        for file, text in files.items():
            self.write(f"editions/{name}/{file}", text)
        return read_edition(self.root, name, BOOK, SONGS, SLUGS)


def lite(selection: str = 'songs = ["alfa"]', extra: str = "", pages: str = PAGES_SHARED,
         cover_image: str = 'cover_image = "../../images/cover.jpg"\n') -> str:
    """An edition file: the selection, extra keys, a cover image and the pages."""
    return f"{selection}\n{extra}{cover_image}before_songs = []\nafter_contents = []\n{pages}"


class ReadBook(unittest.TestCase):
    def test_the_book_file_is_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read_book(Repository(tmp).root), BOOK)

    def test_missing_unknown_and_wrong_keys_are_reported_together(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Repository(tmp)
            repo.write(str(BOOK_FILE), BOOK_TOML.replace("2019", '"2019"').replace('author = "Autor"\n', "")
                       + 'place = "Brno"\n')
            with self.assertRaises(EditionError) as caught:
                read_book(repo.root)
        self.assertEqual(caught.exception.errors, ["missing key 'author'", "unknown key 'place'",
                                                   "'start_year' must be an integer"])

    def test_the_base_edition_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Repository(tmp)
            repo.write(str(BOOK_FILE), BOOK_TOML.replace('"full"', '"none"'))
            with self.assertRaises(EditionError) as caught:
                read_book(repo.root)
        self.assertIn("base_edition 'none'", caught.exception.errors[0])


class ReadEdition(unittest.TestCase):
    def read(self, toml: str, name: str = "lite", **files: str):
        with tempfile.TemporaryDirectory() as tmp:
            return Repository(tmp).edition(toml, name, **files)

    def errors(self, toml: str, name: str = "lite", **files: str) -> list[str]:
        with self.assertRaises(EditionError) as caught:
            self.read(toml, name, **files)
        return caught.exception.errors

    def test_the_full_book_takes_every_song_and_the_shared_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            edition = read_edition(Repository(tmp).root, "full", BOOK, SONGS, SLUGS)
        self.assertEqual(edition.select(SONGS), SONGS)
        self.assertEqual(edition.pages, {"cover": "shared-pages/cover", "halftitle": "shared-pages/halftitle",
                                         "titlepage": "shared-pages/titlepage"})
        self.assertEqual(edition.cover_image, "images/cover.jpg")
        self.assertEqual((edition.title, edition.subtitle, edition.editors), ("Kniha", None, ()))

    def test_songs_by_id_and_by_artist_or_collection(self):
        edition = self.read(lite('songs = ["beta"]\nartists = ["filmy"]'))
        self.assertEqual([song.id for song in edition.select(SONGS)], ["beta", "gama"])

    def test_own_pages_and_listed_files_resolve_to_tex_paths(self):
        toml = lite(extra='title = "Lite"\nsubtitle = "výběr"\neditors = ["A", "B"]\nimprint = "credits.tex"\n',
                    pages='[pages]\ncover = "own"\nhalftitle = "shared"\ntitlepage = "own"\n', cover_image="")
        toml = toml.replace("before_songs = []", 'before_songs = ["intro.tex", "../full/foreword.tex"]')
        with tempfile.TemporaryDirectory() as tmp:
            repo = Repository(tmp)
            repo.write("editions/full/foreword.tex", "")
            edition = repo.edition(toml, **{"cover.tex": "", "titlepage.tex": "", "credits.tex": "", "intro.tex": ""})
        self.assertEqual(edition.pages["cover"], "editions/lite/cover")
        self.assertEqual(edition.pages["titlepage"], "editions/lite/titlepage")
        self.assertEqual(edition.imprint, "editions/lite/credits")
        self.assertEqual(edition.before_songs, ("editions/lite/intro", "editions/full/foreword"))
        self.assertEqual((edition.title, edition.subtitle, edition.editors), ("Lite", "výběr", ("A", "B")))
        self.assertIsNone(edition.cover_image)

    def test_a_bad_edition_name_is_an_error(self):
        self.assertIn("must match", self.errors(lite(), name="Lite Edition")[0])

    def test_a_missing_edition_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(EditionError) as caught:
                read_edition(Repository(tmp).root, "none", BOOK, SONGS, SLUGS)
        self.assertEqual(caught.exception.errors, ["no such file"])

    def test_missing_unknown_and_wrong_keys(self):
        toml = 'songs = "alfa"\nfile = "x"\n'
        self.assertEqual(self.errors(toml), ["missing key 'pages'", "unknown key 'file'",
                                             "'songs' must be a list of non-empty strings"])

    def test_before_songs_and_after_contents_may_be_left_out(self):
        edition = self.read(lite().replace("before_songs = []\nafter_contents = []\n", ""))
        self.assertEqual((edition.before_songs, edition.after_contents), ((), ()))

    def test_every_page_must_be_declared_shared_or_own(self):
        pages = '[pages]\ncover = "shared"\nhalftitle = "mine"\nback = "own"\n'
        self.assertEqual(self.errors(lite(pages=pages)), ["pages: missing key 'titlepage'",
                                                          "pages: unknown key 'back'",
                                                          "pages: 'halftitle' must be \"shared\" or \"own\""])

    def test_all_must_be_true(self):
        self.assertEqual(self.errors(lite("all = false")), ["'all' must be true"])

    def test_all_goes_without_a_selection(self):
        self.assertIn("'all' goes without 'songs' and 'artists'", self.errors(lite('all = true\nsongs = ["alfa"]')))

    def test_a_selection_is_required(self):
        self.assertIn("no selection", self.errors(lite(""))[0])

    def test_unknown_song_ids_and_slugs(self):
        self.assertEqual(self.errors(lite('songs = ["alfa", "nic"]\nartists = ["nikdo"]')),
                         ["'songs': unknown song id 'nic'", "'artists': unknown registry slug 'nikdo'"])

    def test_a_selection_without_songs(self):
        self.assertEqual(self.errors(lite('artists = ["abba"]')), ["the selection has no songs"])

    def test_a_shared_cover_needs_an_existing_image(self):
        self.assertEqual(self.errors(lite(cover_image="")), ["a shared cover needs 'cover_image'"])
        self.assertEqual(self.errors(lite(cover_image='cover_image = "nic.jpg"\n')),
                         ["'cover_image': nic.jpg is not a file of the repository"])

    def test_an_own_cover_takes_no_cover_image(self):
        pages = '[pages]\ncover = "own"\nhalftitle = "shared"\ntitlepage = "shared"\n'
        self.assertEqual(self.errors(lite(pages=pages), **{"cover.tex": ""}),
                         ["'cover_image' goes with a shared cover only"])

    def test_an_own_page_must_exist(self):
        pages = '[pages]\ncover = "shared"\nhalftitle = "own"\ntitlepage = "shared"\n'
        self.assertEqual(self.errors(lite(pages=pages)), ["'pages.halftitle': halftitle.tex does not exist"])

    def test_a_listed_file_must_exist(self):
        self.assertEqual(self.errors(lite(extra='imprint = "credits.tex"\n')),
                         ["'imprint': credits.tex does not exist"])

    def test_a_listed_file_must_be_a_tex_file_directly_in_an_edition_folder(self):
        for reference in ("notes.txt", "../../shared-pages/cover.tex", "sub/page.tex"):
            with self.subTest(reference=reference):
                errors = self.errors(lite().replace("before_songs = []", f'before_songs = ["{reference}"]'))
                self.assertEqual(errors, [f"'before_songs': {reference} must be a .tex file in an edition folder"])

    def test_an_unreferenced_tex_file_in_the_folder_is_an_error(self):
        self.assertEqual(self.errors(lite(), **{"titulnilist.tex": ""}),
                         ["titulnilist.tex is not referenced by edition.toml"])


if __name__ == "__main__":
    unittest.main()
