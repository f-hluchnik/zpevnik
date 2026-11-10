"""Unit tests for the edition build command.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from build_edition import build, include_folders, latexmk_command


class Command(unittest.TestCase):
    def test_the_edition_reaches_the_document_as_one_definition(self):
        command = latexmk_command("lite")
        self.assertIn("-outdir=build/editions/lite", command)
        self.assertIn("-usepretex=\\def\\zpgenerated{build/editions/lite/generated}", command)
        self.assertEqual(command[-1], "zpevnik.tex")


class Folders(unittest.TestCase):
    def test_songs_shared_pages_and_every_edition_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            for folder in ("editions/full", "editions/lite"):
                (Path(tmp) / folder).mkdir(parents=True)
            (Path(tmp) / "editions" / "README.md").write_text("")
            self.assertEqual([str(f) for f in include_folders(Path(tmp))],
                             ["songs", "shared-pages", "editions/full", "editions/lite"])

    def test_an_edition_that_is_not_generated_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                build(Path(tmp), "full")


if __name__ == "__main__":
    unittest.main()
