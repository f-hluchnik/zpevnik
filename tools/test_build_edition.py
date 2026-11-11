"""Unit tests for the edition build command.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from build_edition import build, include_folders, latexmk_command, missing_link_targets


class Command(unittest.TestCase):
    def test_the_edition_reaches_the_document_as_one_definition(self):
        command = latexmk_command("lite")
        self.assertIn("-outdir=build/editions/lite", command)
        self.assertIn("-usepretex=\\def\\zpgenerated{build/editions/lite/generated}", command)
        self.assertEqual(command[-1], "zpevnik.tex")


class LinkCheck(unittest.TestCase):
    def test_every_missing_target_is_reported_once(self):
        log = ("pdfTeX warning (dest): name{beta} has been referenced but does not exist, replaced by a fixed one\n"
               "pdfTeX warning (dest): name{artist-abba} has been referenced but does not exist, replaced by a fixed one\n"
               "pdfTeX warning (dest): name{beta} has been referenced but does not exist, replaced by a fixed one\n")
        self.assertEqual(missing_link_targets(log), ["artist-abba", "beta"])

    def test_a_clean_log_has_none(self):
        self.assertEqual(missing_link_targets("Output written on zpevnik.pdf (757 pages).\n"), [])


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
