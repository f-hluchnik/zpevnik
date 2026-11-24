"""Unit tests for what the tools read from poppler and Ghostscript (no program needed).

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest
from pathlib import Path
from unittest import mock

import pdf_programs
from pdf_programs import (Box, Greymap, InkColumns, InkCoverage, PdfProgramError, greymap, image_colours,
                          ink_columns, ink_coverages, page_boxes, page_count, render_page, rendered_left, unembedded_fonts)

PDFINFO_BOX = """Pages:           182
Page size:       476.22 x 651.968 pts
MediaBox:            0.00     0.00   476.22   651.97
CropBox:             0.00     0.00   476.22   651.97
BleedBox:           25.51    25.51   450.71   626.46
TrimBox:            28.35    28.35   447.87   623.62
"""
PDFFONTS = """name                                 type              encoding         emb sub uni object ID
------------------------------------ ----------------- ---------------- --- --- --- ---------
HLYIQL+LCIRCLE10                     Type 1            Builtin          yes yes yes      8  0
Helvetica-Bold                       Type 1            Custom           no  no  no      14  0
"""
PDFIMAGES = """page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio
--------------------------------------------------------------------------------------------
   1     0 image    1819  2551  rgb     3   8  jpeg   no         7  0   211   211 1430K  11%
  12     1 image     900   300  gray    1   8  image  no        40  0   300   300   12K   4%
"""
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
        self.assertEqual(boxes.bleed, Box(25.51, 25.51, 450.71, 626.46))

    def test_missing_lines_are_an_error(self):
        with self.assertRaises(PdfProgramError):
            page_count("Title: x\n")
        with self.assertRaises(PdfProgramError):
            page_boxes("Pages: 1\nMediaBox: 0 0 1 1\n")


class Tables(unittest.TestCase):
    def test_a_font_that_is_not_embedded_is_named_whatever_its_type(self):
        with mock.patch.object(pdf_programs, "run", return_value=PDFFONTS):
            self.assertEqual(unembedded_fonts(Path("x.pdf")), ["Helvetica-Bold"])

    def test_every_image_has_its_page_and_colour_space(self):
        with mock.patch.object(pdf_programs, "run", return_value=PDFIMAGES):
            self.assertEqual(image_colours(Path("x.pdf")), [(1, "rgb"), (12, "gray")])


class Inks(unittest.TestCase):
    def test_one_coverage_per_page_and_ghostscript_warnings_between_them_are_skipped(self):
        coverages = ink_coverages(INKCOV)
        self.assertEqual(coverages, [InkCoverage(0, 0, 0, 0.02525), InkCoverage(0.03008, 0.03008, 0.03008, 0.03008)])
        self.assertEqual([coverage.is_black_only for coverage in coverages], [True, False])


class Rendering(unittest.TestCase):
    def test_a_greymap_from_pdftoppm_is_read(self):
        self.assertEqual(greymap(b"P5\n3 2\n255\n" + bytes(range(6))), Greymap(3, 2, bytes(range(6))))

    def test_a_greymap_that_is_not_8_bit_or_is_cut_short_is_an_error(self):
        with self.assertRaisesRegex(PdfProgramError, "8-bit"):
            greymap(b"P5\n1 1\n65535\n\x00\x00")
        with self.assertRaisesRegex(PdfProgramError, "pixels"):
            greymap(b"P5\n2 2\n255\n\x00")

    def test_the_ink_spans_every_row_and_a_pixel_that_is_only_grey_counts(self):
        white, grey = b"\xff", b"\xfe"
        page = Greymap(6, 2, white * 2 + grey + white * 3 + white * 4 + b"\x00" + white)
        self.assertEqual(ink_columns(page), InkColumns(first=2, last=4))

    def test_a_blank_page_has_no_ink(self):
        self.assertIsNone(ink_columns(Greymap(3, 2, b"\xff" * 6)))

    def test_a_page_is_rendered_inside_the_box_asked_for(self):
        with mock.patch.object(pdf_programs, "run_binary", return_value=b"P5\n1 1\n255\n\xff") as run:
            render_page(Path("x.pdf"), 7, 72, Box(10, 20, 110, 220), page_height=300)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("-x"):command.index("-x") + 8],
                         ["-x", "10", "-y", "80", "-W", "100", "-H", "200"])
        self.assertEqual(command[command.index("-f"):command.index("-f") + 4], ["-f", "7", "-l", "7"])

    def test_a_box_between_pixels_is_rendered_with_every_pixel_it_touches(self):
        with mock.patch.object(pdf_programs, "run_binary", return_value=b"P5\n1 1\n255\n\xff") as run:
            render_page(Path("x.pdf"), 1, 72, Box(10.6, 20.2, 110.4, 220.9), page_height=300)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("-x"):command.index("-x") + 8],
                         ["-x", "10", "-y", "79", "-W", "101", "-H", "201"])
        self.assertEqual(rendered_left(Box(10.6, 20.2, 110.4, 220.9), 72), 10)


class Programs(unittest.TestCase):
    def test_a_missing_program_says_what_to_install(self):
        with mock.patch.object(pdf_programs.subprocess, "run", side_effect=FileNotFoundError("gs")):
            with self.assertRaisesRegex(PdfProgramError, "gs not found: install Ghostscript"):
                pdf_programs.ink_coverage(Path("x.pdf"))
            with self.assertRaisesRegex(PdfProgramError, "pdfinfo not found: install poppler"):
                pdf_programs.pdfinfo(Path("x.pdf"))
