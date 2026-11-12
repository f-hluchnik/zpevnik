"""Unit tests for assembling songs.json (tools/songs_json.py).

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest

from paths import HIDDEN_SONGS, REGISTRY_FILE, edition_output_dir
from songs_json import SCHEMA_VERSION, WEBSITE_EDITION, SongsJsonError, songs_document
from .test_check_pages import write_compiled_book
from .test_edition import Repository

REGISTRY = '[[entry]]\nslug = "abba"\nname = "ABBA"\n\n[[entry]]\nslug = "kryl"\nname = "Kryl, Karel"\n'
SONGS = {
    "alfa": "\\song{Alfa} \\artist{abba}\n\\alttitle{Zeta}\n\\seealso{beta}{Beta}\n\\seealso{gama}{Gama}\n\n\\vers{a}\n",
    "beta": "\\song{Beta} \\artist{kryl}\n\n\\vers{b}\n",
    "gama": "\\song{Gama} \\artist{abba}\n\n\\vers{c}\n",
}
FRONT_MATTER = ("editions/full/introduction", 9)  # a checkpoint: the page the next file starts on


class SongsDocument(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Repository(self.tmp.name)
        self.repo.write(str(REGISTRY_FILE), REGISTRY)
        for song_id, source in SONGS.items():
            self.repo.write(f"songs/{song_id}.tex", source)
        self.repo.write(str(HIDDEN_SONGS), "beta  # a test\n")

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, *song_ids: str) -> None:
        """The .aux files of a full book with these songs, one page each from page 9."""
        output = self.repo.root / edition_output_dir(WEBSITE_EDITION)
        output.mkdir(parents=True)
        after_first = FRONT_MATTER[1] + 1
        write_compiled_book(output, [FRONT_MATTER, *((f"songs/{song_id}", after_first + n)
                                                     for n, song_id in enumerate(song_ids))])

    def test_the_published_songs_in_book_order_with_their_pages(self):
        self.build("alfa", "gama")
        document = songs_document(self.repo.root)
        self.assertEqual(document["schemaVersion"], SCHEMA_VERSION)
        self.assertEqual([(song["id"], song["page"]) for song in document["songs"]], [("alfa", 9), ("gama", 10)])

    def test_a_hidden_song_is_nowhere(self):
        self.build("alfa", "gama")
        document = songs_document(self.repo.root)
        self.assertEqual([see["id"] for see in document["songs"][0]["see"]], ["gama"])
        self.assertEqual([artist["slug"] for artist in document["artists"]], ["abba"])
        self.assertNotIn("beta", str(document["contents"]))

    def test_the_contents_list_other_titles_under_their_own_letter(self):
        self.build("alfa", "gama")
        contents = songs_document(self.repo.root)["contents"]
        self.assertEqual(contents, [
            {"letter": "A", "entries": [{"id": "alfa", "title": "Alfa", "alternative": False}]},
            {"letter": "G", "entries": [{"id": "gama", "title": "Gama", "alternative": False}]},
            {"letter": "Z", "entries": [{"id": "alfa", "title": "Zeta", "alternative": True}]},
        ])

    def test_an_artist_lists_its_entries_in_book_order(self):
        self.build("alfa", "gama")
        [abba] = songs_document(self.repo.root)["artists"]
        self.assertEqual({key: abba[key] for key in ("name", "label", "linkLabel", "kind", "section")},
                         {"name": "ABBA", "label": "ABBA", "linkLabel": "ABBA", "kind": "artist", "section": True})
        self.assertEqual([(entry["title"], entry["alternative"]) for entry in abba["entries"]],
                         [("Alfa", False), ("Gama", False), ("Zeta", True)])

    def test_a_book_built_from_other_songs_is_an_error(self):
        self.build("alfa", "beta", "gama")
        with self.assertRaisesRegex(SongsJsonError, "other songs"):
            songs_document(self.repo.root)

    def test_an_unbuilt_book_is_an_error(self):
        with self.assertRaisesRegex(SongsJsonError, "not built"):
            songs_document(self.repo.root)


if __name__ == "__main__":
    unittest.main()
