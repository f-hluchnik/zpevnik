"""Unit tests for the A5 print PDF.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest
from pathlib import Path
from unittest import mock

import print_pdf
from print_pdf import (A5_SCALE, PrintError, check_print_pdf, kept_pages, page_count, page_size,
                       wrapper_tex)

PDFINFO = "Title: x\nPages:           164\nPage size:       419.528 x 595.276 pts (A5)\n"
SOURCE = Path("build/editions/lite/print/zpevnik.pdf")


class Wrapper(unittest.TestCase):
    def includes(self, tex: str) -> list[str]:
        return [line for line in tex.splitlines() if line.startswith("\\includepdf")]

    def test_every_page_is_scaled_and_shifted_away_from_the_spine(self):
        lines = self.includes(wrapper_tex(SOURCE, range(1, 5), 3.0))
        self.assertEqual([line.split("pages=")[1].split(",")[0] for line in lines], ["1", "2", "3", "4"])
        self.assertEqual([line.split("offset=")[1].split(" ")[0] for line in lines],
                         ["3.000mm", "-3.000mm", "3.000mm", "-3.000mm"])
        self.assertTrue(all(f"scale={A5_SCALE:.8f}" in line and "noautoscale=true" in line for line in lines))
        self.assertTrue(all(line.endswith("{build/editions/lite/print/zpevnik.pdf}") for line in lines))

    def test_the_sides_follow_the_position_in_the_new_book_not_the_source_page(self):
        lines = self.includes(wrapper_tex(SOURCE, range(3, 6), 2.0))
        self.assertEqual([line.split("offset=")[1].split(" ")[0] for line in lines],
                         ["2.000mm", "-2.000mm", "2.000mm"])

    def test_an_odd_number_of_pages_gets_a_blank_page_at_the_end(self):
        self.assertIn("\\null\n\\end{document}", wrapper_tex(SOURCE, range(1, 4), 0.0))
        self.assertNotIn("\\null", wrapper_tex(SOURCE, range(1, 5), 0.0))

    def test_the_paper_is_a5(self):
        self.assertTrue(wrapper_tex(SOURCE, range(1, 3), 0.0).startswith("\\documentclass[a5paper]{article}"))


class KeptPages(unittest.TestCase):
    def test_all_pages_by_default(self):
        self.assertEqual(kept_pages(164, 0), range(1, 165))

    def test_the_cover_can_be_dropped_in_pairs(self):
        self.assertEqual(kept_pages(164, 2), range(3, 165))

    def test_an_odd_number_would_move_every_page_to_the_other_side(self):
        with self.assertRaisesRegex(PrintError, "must be even"):
            kept_pages(164, 1)

    def test_dropping_everything_is_an_error(self):
        with self.assertRaisesRegex(PrintError, "leaves nothing"):
            kept_pages(4, 4)


class Pdfinfo(unittest.TestCase):
    def test_the_page_count_and_the_page_size_are_read(self):
        self.assertEqual(page_count(PDFINFO), 164)
        self.assertEqual(page_size(PDFINFO), (419.528, 595.276))

    def test_missing_lines_are_an_error(self):
        with self.assertRaises(PrintError):
            page_count("Title: x\n")
        with self.assertRaises(PrintError):
            page_size("Title: x\n")


class Check(unittest.TestCase):
    def check(self, info: str) -> int:
        with mock.patch.object(print_pdf, "pdfinfo", return_value=info):
            return check_print_pdf(Path("x.pdf"))

    def test_an_a5_pdf_with_an_even_page_count_passes(self):
        self.assertEqual(self.check(PDFINFO), 164)

    def test_another_page_size_is_refused(self):
        with self.assertRaisesRegex(PrintError, "not A5"):
            self.check(PDFINFO.replace("419.528 x 595.276", "595.276 x 841.89"))

    def test_an_odd_page_count_is_refused(self):
        with self.assertRaisesRegex(PrintError, "odd number"):
            self.check(PDFINFO.replace("164", "163"))
