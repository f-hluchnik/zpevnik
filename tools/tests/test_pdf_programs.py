"""Unit tests for what the tools read from poppler and Ghostscript (no program needed).

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest
from pathlib import Path
from unittest import mock

import pdf_programs
from pdf_programs import (Box, InkCoverage, PdfProgramError, Span, ink_coverages, page_boxes, page_count,
                          word_spans)

PDFINFO_BOX = """Pages:           182
Page size:       476.22 x 651.968 pts
MediaBox:            0.00     0.00   476.22   651.97
CropBox:             0.00     0.00   476.22   651.97
BleedBox:           28.35    28.35   447.87   623.62
TrimBox:            28.35    28.35   447.87   623.62
"""
BBOX_HTML = """<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml"><head><title></title></head><body><doc>
  <page width="419.5" height="595.3">
    <word xMin="40.5" yMin="20.0" xMax="60.25" yMax="30.0">R&amp;B</word>
    <word xMin="70.0" yMin="20.0" xMax="90.0" yMax="30.0">&lt;C&gt;</word>
  </page>
  <page width="419.5" height="595.3">
  </page>
</doc></body></html>"""
INKCOV = """ 0.00000  0.00000  0.00000  0.02525 CMYK OK
   **** Error: Unknown operator: '-25.-2', processed as number, value: -25.0
 0.03008  0.03008  0.03008  0.03008 CMYK OK
"""


class Pdfinfo(unittest.TestCase):
    def test_the_page_count_and_the_boxes_are_read(self):
        self.assertEqual(page_count(PDFINFO_BOX), 182)
        boxes = page_boxes(PDFINFO_BOX)
        self.assertEqual(boxes.media, Box(0, 0, 476.22, 651.97))
        self.assertEqual(boxes.trim, Box(28.35, 28.35, 447.87, 623.62))

    def test_missing_lines_are_an_error(self):
        with self.assertRaises(PdfProgramError):
            page_count("Title: x\n")
        with self.assertRaises(PdfProgramError):
            page_boxes("Pages: 1\nMediaBox: 0 0 1 1\n")


class Words(unittest.TestCase):
    def test_every_page_gets_its_words_and_a_page_without_text_gets_none(self):
        self.assertEqual(word_spans(BBOX_HTML), [[Span(40.5, 60.25), Span(70.0, 90.0)], []])


class Inks(unittest.TestCase):
    def test_one_coverage_per_page_and_ghostscript_warnings_between_them_are_skipped(self):
        coverages = ink_coverages(INKCOV)
        self.assertEqual(coverages, [InkCoverage(0, 0, 0, 0.02525), InkCoverage(0.03008, 0.03008, 0.03008, 0.03008)])
        self.assertEqual([coverage.is_black_only for coverage in coverages], [True, False])


class Programs(unittest.TestCase):
    def test_a_missing_program_says_what_to_install(self):
        with mock.patch.object(pdf_programs.subprocess, "run", side_effect=FileNotFoundError("gs")):
            with self.assertRaisesRegex(PdfProgramError, "gs not found: install Ghostscript"):
                pdf_programs.ink_coverage(Path("x.pdf"))
            with self.assertRaisesRegex(PdfProgramError, "pdfinfo not found: install poppler"):
                pdf_programs.pdfinfo(Path("x.pdf"))
