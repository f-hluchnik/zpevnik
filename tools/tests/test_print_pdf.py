"""Unit tests for the A5 print PDF (no TeX, poppler or Ghostscript needed).

Run from the repository root: python3 -m unittest discover -s tools
"""
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import print_pdf
from edition import PrintSettings
from pdf_programs import Greymap, InkCoverage
from print_layout import A5_HEIGHT_PT, A5_WIDTH_PT, Placement, millimetres, points
from pdf_programs import Box
from print_pdf import (CROP_MARK_ROOM_MM, INK_DPI, INK_PIXEL_PT, PrintError, check_print_pdf, kept_pages,
                       placement_for, print_settings, wrapper_tex)

SOURCE = Path("build/editions/lite/print/zpevnik.pdf")
PLACEMENT = Placement(scale=0.69, shift=points(4.0))
SETTINGS = PrintSettings(spine_margin_mm=12.5, outer_margin_mm=4.5, skip_first_pages=2, crop_marks=True)
ROOM = points(CROP_MARK_ROOM_MM)


def pdfinfo_report(pages: int = 4, trim_width: float = A5_WIDTH_PT, room: float = ROOM) -> str:
    """What pdfinfo -box says about a PDF with the A5 page in the middle of room on every side."""
    trim = f"{room:.2f} {room:.2f} {room + trim_width:.2f} {room + A5_HEIGHT_PT:.2f}"
    return (f"Pages: {pages}\nMediaBox: 0 0 {trim_width + 2 * room:.2f} {A5_HEIGHT_PT + 2 * room:.2f}\n"
            f"TrimBox: {trim}\n")


PIXELS_PER_MM = INK_DPI / 25.4
TRIMMED_WIDTH_PIXELS = round(A5_WIDTH_PT * INK_DPI / 72)


def rendered(spine_mm: float, outer_mm: float, position: int) -> Greymap:
    """A trimmed page rendered with its ink that far from the spine and from the outer edge (one row)."""
    left, right = (spine_mm, outer_mm) if position % 2 else (outer_mm, spine_mm)
    first = math.ceil(left * PIXELS_PER_MM)
    after = TRIMMED_WIDTH_PIXELS - math.ceil(right * PIXELS_PER_MM)
    row = b"\xff" * first + b"\x80" * (after - first) + b"\xff" * (TRIMMED_WIDTH_PIXELS - after)
    return Greymap(TRIMMED_WIDTH_PIXELS, 1, row)


BLANK = Greymap(TRIMMED_WIDTH_PIXELS, 1, b"\xff" * TRIMMED_WIDTH_PIXELS)
GOOD_PAGES = tuple(rendered(13, 5, position) for position in range(1, 5))  # inside 12.5 and 4.5 mm
BLACK = InkCoverage(0, 0, 0, 0.02)


class Wrapper(unittest.TestCase):
    def includes(self, tex: str) -> list[str]:
        return [line for line in tex.splitlines() if line.startswith("\\includepdf")]

    def test_every_page_is_scaled_and_shifted_away_from_the_spine(self):
        lines = self.includes(wrapper_tex(SOURCE, range(1, 5), PLACEMENT, crop_marks=False))
        self.assertEqual([line.split("pages=")[1].split(",")[0] for line in lines], ["1", "2", "3", "4"])
        self.assertEqual([line.split("offset=")[1].split(" ")[0] for line in lines],
                         ["4.000mm", "-4.000mm", "4.000mm", "-4.000mm"])
        self.assertTrue(all("scale=0.69000000" in line and "noautoscale=true" in line for line in lines))
        self.assertTrue(all(line.endswith("{build/editions/lite/print/zpevnik.pdf}") for line in lines))

    def test_the_sides_follow_the_position_in_the_new_book_not_the_source_page(self):
        lines = self.includes(wrapper_tex(SOURCE, range(3, 6), PLACEMENT, crop_marks=False))
        self.assertEqual([line.split("offset=")[1].split(" ")[0] for line in lines],
                         ["4.000mm", "-4.000mm", "4.000mm"])

    def test_an_odd_number_of_pages_gets_a_blank_page_at_the_end(self):
        self.assertIn("\\null\n\\end{document}", wrapper_tex(SOURCE, range(1, 4), PLACEMENT, False))
        self.assertNotIn("\\null", wrapper_tex(SOURCE, range(1, 5), PLACEMENT, False))

    def test_the_paper_is_a5_and_crop_marks_add_room_and_the_trim_box(self):
        plain = wrapper_tex(SOURCE, range(1, 3), PLACEMENT, crop_marks=False)
        marked = wrapper_tex(SOURCE, range(1, 3), PLACEMENT, crop_marks=True)
        self.assertTrue(plain.startswith("\\documentclass[a5paper]{article}"))
        self.assertNotIn("crop", plain)
        self.assertIn("{crop}", marked)
        self.assertIn("width=168.000mm,height=230.000mm", marked)
        box = f"[{ROOM:.3f} {ROOM:.3f} {ROOM + A5_WIDTH_PT:.3f} {ROOM + A5_HEIGHT_PT:.3f}]"
        self.assertIn(f"/TrimBox {box} /BleedBox {box}", marked)


class KeptPages(unittest.TestCase):
    def test_the_first_pages_are_left_out(self):
        self.assertEqual(kept_pages(164, 2), range(3, 165))
        self.assertEqual(kept_pages(164, 0), range(1, 165))

    def test_leaving_out_everything_is_an_error(self):
        with self.assertRaisesRegex(PrintError, "leaves nothing"):
            kept_pages(4, 4)


class Check(unittest.TestCase):
    def check(self, info: str = pdfinfo_report(), pages: tuple[Greymap, ...] = GOOD_PAGES,
              inks: tuple[InkCoverage, ...] = (BLACK,) * 4, black_ink: bool = True):
        def render_page(pdf: Path, position: int, dpi: int, area, page_height: float) -> Greymap:
            return pages[position - 1]

        with (mock.patch.object(print_pdf, "pdfinfo", return_value=info),
              mock.patch.object(print_pdf, "render_page", side_effect=render_page),
              mock.patch.object(print_pdf, "ink_coverage", return_value=list(inks))):
            return check_print_pdf(Path("x.pdf"), SETTINGS, black_ink)

    def test_an_a5_book_inside_the_margins_in_black_ink_passes_and_reports_its_narrowest_margins(self):
        checked = self.check(pages=(rendered(13, 5, 1), rendered(14, 6, 2), rendered(13.2, 4.8, 3), BLANK))
        self.assertEqual(checked.pages, 4)
        self.assertAlmostEqual(millimetres(checked.narrowest.spine), 13, delta=0.1)
        self.assertAlmostEqual(millimetres(checked.narrowest.outer), 4.8, delta=0.1)

    def test_another_trimmed_page_is_refused(self):
        with self.assertRaisesRegex(PrintError, "not A5"):
            self.check(info=pdfinfo_report(trim_width=595.0))

    def test_crop_marks_without_room_for_them_are_refused(self):
        with self.assertRaisesRegex(PrintError, "room for the crop marks"):
            self.check(info=pdfinfo_report(room=0))

    def test_an_odd_page_count_is_refused(self):
        with self.assertRaisesRegex(PrintError, "odd number"):
            self.check(info=pdfinfo_report(pages=3))

    def test_ink_too_close_to_the_spine_or_the_edge_names_its_page_and_what_was_measured(self):
        pages = (rendered(13, 5, 1), rendered(12.3, 5, 2), rendered(13, 5, 3), rendered(13, 4.2, 4))
        with self.assertRaises(PrintError) as caught:
            self.check(pages=pages)
        message = str(caught.exception)
        self.assertRegex(message, r"pages 2 \(12\.\d\d mm at the spine, 5\.\d\d mm outside\), "
                                  r"4 \(13\.\d\d mm at the spine, 4\.\d\d mm outside\) of")

    def test_the_spine_is_on_the_left_of_odd_pages_and_on_the_right_of_even_ones(self):
        # 5 mm left and 13 mm right: inside the margins on an even page, not on an odd one.
        mirrored = rendered(13, 5, 2)
        self.check(pages=(GOOD_PAGES[0], mirrored, GOOD_PAGES[2], mirrored))
        with self.assertRaisesRegex(PrintError, "on pages 1 "):
            self.check(pages=(mirrored, GOOD_PAGES[1], GOOD_PAGES[2], GOOD_PAGES[3]))

    def test_a_book_without_ink_is_refused(self):
        with self.assertRaisesRegex(PrintError, "no ink"):
            self.check(pages=(BLANK,) * 4)

    def test_a_page_in_colour_names_its_page(self):
        with self.assertRaisesRegex(PrintError, "pages 3 of .* colour inks"):
            self.check(inks=(BLACK, BLACK, InkCoverage(0.01, 0, 0, 0), BLACK))

    def test_a_format_in_colour_is_not_checked_for_one_ink(self):
        self.assertEqual(self.check(inks=(InkCoverage(0.5, 0.5, 0, 0),) * 4, black_ink=False).pages, 4)


class Placing(unittest.TestCase):
    def test_the_pages_are_placed_with_the_pixel_the_check_may_lose_to_spare(self):
        # An A4 page (595 pt, 2480 pixels at 300 dpi) with ink 28 pt from both edges.
        a4 = Box(0, 0, 595.0, 842.0)
        width = round(a4.width / INK_PIXEL_PT)
        first = round(28 / INK_PIXEL_PT)
        row = b"\xff" * first + b"\x00" * (width - 2 * first) + b"\xff" * first
        with mock.patch.object(print_pdf, "render_page", return_value=Greymap(width, 1, row)):
            placement = placement_for(Path("a4.pdf"), a4, range(1, 3), SETTINGS)
        centre, reach = A5_WIDTH_PT / 2, a4.width / 2 - first * INK_PIXEL_PT
        spine = centre - placement.scale * reach + placement.shift  # the left of the first, a right-hand page
        outer = centre - placement.scale * reach - placement.shift
        self.assertAlmostEqual(spine, points(SETTINGS.spine_margin_mm) + INK_PIXEL_PT)
        self.assertAlmostEqual(outer, points(SETTINGS.outer_margin_mm) + INK_PIXEL_PT)


class Settings(unittest.TestCase):
    def test_an_edition_without_a_print_table_cannot_go_to_a_printer(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "editions" / "lite"
            folder.mkdir(parents=True)
            (folder / "edition.toml").write_text('all = true\n[pages]\ncover = "shared"\n', encoding="utf-8")
            with self.assertRaisesRegex(PrintError, "editions/lite/edition.toml has no \\[print\\] table"):
                print_settings(Path(tmp), "lite")
