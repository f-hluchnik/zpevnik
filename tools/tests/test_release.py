"""Unit tests for the release assets and notes.

Run from the repository root: python3 -m unittest discover -s tools
"""
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from edition import edition_names
from paths import BOOK_PDF_NAME, REPO_ROOT, SCORE_OUTPUT_DIR, SONGS_JSON_FILE, edition_output_dir
from release import (SCORES_ASSET, SONGS_JSON_ASSET, asset_name, edition_line, edition_notes, songs_phrase,
                     stage_assets, stage_web_assets, zip_scores)

VERSION = "8.38.2"
BUILD_EDITION = REPO_ROOT / "tools" / "build_edition.py"


class Names(unittest.TestCase):
    def test_the_asset_name_has_the_edition_and_the_version(self):
        self.assertEqual(asset_name("lidovky", VERSION), "zpevnik-lidovky-8.38.2.pdf")

    def test_czech_plural_of_song(self):
        self.assertEqual([songs_phrase(n) for n in (1, 2, 4, 5, 76, 738)],
                         ["1 píseň", "2 písně", "4 písně", "5 písní", "76 písní", "738 písní"])

    def test_a_line_names_the_subtitle_only_when_there_is_one(self):
        self.assertEqual(edition_line("lidovky", "lidové písničky", 76, "a.pdf"),
                         "- `lidovky` (lidové písničky): 76 písní, `a.pdf`")
        self.assertEqual(edition_line("full", None, 738, "b.pdf"), "- `full`: 738 písní, `b.pdf`")


class Staging(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ("alfa", "beta"):
            (self.root / "editions" / name).mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, name: str, content: bytes):
        output = self.root / edition_output_dir(name)
        output.mkdir(parents=True)
        (output / BOOK_PDF_NAME).write_bytes(content)

    def test_every_edition_is_copied_under_its_asset_name(self):
        self.build("alfa", b"a")
        self.build("beta", b"b")
        staged = stage_assets(self.root, VERSION)
        self.assertEqual([path.name for path in staged], ["zpevnik-alfa-8.38.2.pdf", "zpevnik-beta-8.38.2.pdf"])
        self.assertEqual([path.read_bytes() for path in staged], [b"a", b"b"])

    def test_an_edition_that_was_not_built_fails_and_is_named(self):
        self.build("alfa", b"a")
        with self.assertRaisesRegex(FileNotFoundError, "beta"):
            stage_assets(self.root, VERSION)


class WebAssets(unittest.TestCase):
    """songs.json and the score images, which the website reads from the release (J4)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.scores = self.root / SCORE_OUTPUT_DIR
        self.scores.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def build_songs_json(self):
        (self.root / SONGS_JSON_FILE).write_bytes(b'{"songs":[]}\n')

    def build_score(self, stem: str):
        for suffix in (".svg", ".pdf", ".tex"):
            (self.scores / f"{stem}{suffix}").write_bytes(suffix.encode())

    def names_in(self, archive: Path) -> list[str]:
        with zipfile.ZipFile(archive) as opened:
            return opened.namelist()

    def test_songs_json_and_the_zip_of_scores_are_staged_under_fixed_names(self):
        self.build_songs_json()
        self.build_score("one")
        json_asset, scores_asset = stage_web_assets(self.root)
        self.assertEqual((json_asset.name, scores_asset.name), (SONGS_JSON_ASSET, SCORES_ASSET))
        self.assertEqual(json_asset.read_bytes(), (self.root / SONGS_JSON_FILE).read_bytes())

    def test_the_zip_holds_only_the_svg_images_by_name_in_order(self):
        for stem in ("b", "a"):
            self.build_score(stem)
        target = self.root / SCORES_ASSET
        zip_scores(self.root, target)
        self.assertEqual(self.names_in(target), ["a.svg", "b.svg"])

    def test_the_same_scores_give_the_same_bytes(self):
        self.build_score("one")
        first, second = self.root / "first.zip", self.root / "second.zip"
        zip_scores(self.root, first)
        zip_scores(self.root, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_scores_that_were_not_exported_fail(self):
        self.build_songs_json()
        with self.assertRaisesRegex(FileNotFoundError, "make scores"):
            stage_web_assets(self.root)

    def test_songs_json_that_was_not_built_fails(self):
        self.build_score("one")
        with self.assertRaisesRegex(FileNotFoundError, "make json"):
            stage_web_assets(self.root)


class Repository(unittest.TestCase):
    def test_the_notes_list_every_edition_of_the_repository(self):
        notes = edition_notes(REPO_ROOT, VERSION)
        for name in edition_names(REPO_ROOT):
            self.assertIn(f"`{asset_name(name, VERSION)}`", notes)

    def test_build_edition_lists_the_editions_one_per_line(self):
        out = subprocess.run([sys.executable, str(BUILD_EDITION), "--list"], capture_output=True,
                             text=True, check=True).stdout
        self.assertEqual(out.splitlines(), edition_names(REPO_ROOT))
