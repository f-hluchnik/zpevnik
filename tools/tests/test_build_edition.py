"""Unit tests for the edition build command.

Run from the repository root: python3 -m unittest discover -s tools
"""
import sys
import tempfile
import unittest
from pathlib import Path

from build_edition import (LatexError, build, failure_excerpt, include_folders, latexmk_command,
                           missing_link_targets, pdf_path, run_latexmk, undefined_labels)
from formats import PRINT, PRINT_BLACK
from paths import generated_dir


class Command(unittest.TestCase):
    def test_the_edition_reaches_the_document_as_one_definition(self):
        command = latexmk_command("lite")
        self.assertIn("-outdir=build/editions/lite", command)
        self.assertIn("-usepretex=\\def\\zpgenerated{build/editions/lite/generated}", command)
        self.assertEqual(command[-1], "zpevnik.tex")

    def test_a_format_adds_its_definitions_and_has_its_own_output_folder(self):
        command = latexmk_command("lite", PRINT_BLACK)
        self.assertIn("-outdir=build/editions/lite/print-black", command)
        self.assertIn("-usepretex=\\def\\zpgenerated{build/editions/lite/generated}"
                      "\\def\\zpprint{}\\def\\zpchordcolor{black}", command)


class Paths(unittest.TestCase):
    def test_the_pdf_is_in_the_output_folder_of_its_edition(self):
        self.assertEqual(pdf_path("lite"), Path("build/editions/lite/zpevnik.pdf"))

    def test_the_pdf_of_another_format_is_in_a_folder_of_that_format(self):
        self.assertEqual(pdf_path("lite", PRINT), Path("build/editions/lite/print/zpevnik.pdf"))

    def test_all_formats_of_an_edition_share_its_generated_files(self):
        self.assertEqual(generated_dir("lite"), Path("build/editions/lite/generated"))


class Failure(unittest.TestCase):
    TEX_OUTPUT = ("(./zpevnik.tex (o/zpevnik.aux)\n! Undefined control sequence.\nl.1 Hello \\undefined\n"
                  "                        world\n!  ==> Fatal error occurred, no output PDF file produced!\n"
                  "Transcript written on o/zpevnik.log.\nCollected error summary\n")

    def test_the_excerpt_starts_at_the_first_tex_error_and_ends_with_the_fatal_line(self):
        excerpt = failure_excerpt(self.TEX_OUTPUT).splitlines()
        self.assertEqual(excerpt[0], "! Undefined control sequence.")
        self.assertTrue(excerpt[-1].startswith("!  ==> Fatal error"))
        self.assertEqual(len(excerpt), 4)

    def test_without_a_tex_error_the_excerpt_is_the_end_of_the_output(self):
        output = "".join(f"line {n}\n" for n in range(100))
        self.assertEqual(failure_excerpt(output).splitlines(), [f"line {n}" for n in range(80, 100)])

    def test_a_successful_run_raises_nothing(self):
        run_latexmk([sys.executable, "-c", "print('lots of output')"], Path("."), Path("build/x.log"))

    def test_a_failed_run_names_the_log_and_shows_the_tex_error(self):
        code = "import sys; print('(./a.tex)\\n! Missing $ inserted.'); sys.exit(12)"
        with self.assertRaises(LatexError) as caught:
            run_latexmk([sys.executable, "-c", code], Path("."), Path("build/x.log"))
        message = str(caught.exception)
        self.assertIn("failed (12)", message)
        self.assertIn("build/x.log", message)
        self.assertIn("! Missing $ inserted.", message)
        self.assertNotIn("(./a.tex)", message)

    def test_a_stray_byte_in_the_output_does_not_stop_the_build(self):
        code = "import sys; sys.stdout.buffer.write(b'caf\\xba\\n'); sys.exit(0)"
        run_latexmk([sys.executable, "-c", code], Path("."), Path("build/x.log"))


class LinkCheck(unittest.TestCase):
    def test_every_missing_target_is_reported_once(self):
        log = ("pdfTeX warning (dest): name{beta} has been referenced but does not exist, replaced by a fixed one\n"
               "pdfTeX warning (dest): name{artist-abba} has been referenced but does not exist, replaced by a fixed one\n"
               "pdfTeX warning (dest): name{beta} has been referenced but does not exist, replaced by a fixed one\n")
        self.assertEqual(missing_link_targets(log), ["artist-abba", "beta"])

    def test_a_clean_log_has_none(self):
        self.assertEqual(missing_link_targets("Output written on zpevnik.pdf (757 pages).\n"), [])


class UndefinedLabels(unittest.TestCase):
    def test_each_unresolved_page_number_is_reported_once(self):
        log = ("LaTeX Warning: Reference `zp:beta' on page 3 undefined on input line 9.\n"
               "LaTeX Warning: Reference `zp:alfa' on page 4 undefined on input line 9.\n"
               "LaTeX Warning: Reference `zp:beta' on page 8 undefined on input line 9.\n")
        self.assertEqual(undefined_labels(log), ["zp:alfa", "zp:beta"])

    def test_a_log_without_the_warning_has_none(self):
        self.assertEqual(undefined_labels("Output written on zpevnik.pdf (757 pages).\n"), [])


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
