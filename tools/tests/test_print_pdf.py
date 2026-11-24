"""Unit tests for the book block for the printer (no TeX, poppler or Ghostscript needed).

Run from the repository root: python3 -m unittest discover -s tools
"""
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import print_pdf
from edition import BlockSettings
from formats import PRINT, PRINT_BLACK, PRINT_CMYK
from pdf_programs import Box, Greymap, InkCoverage
from print_layout import A4, A5, CROP_MARK_ROOM_MM, PAPERS, Placement, millimetres, points
from print_pdf import (INK_DPI, INK_PIXEL_PT, PrintError, check_print_pdf, deliver, delivered_path, placement_for,
                       print_format, wrapper_tex)

SOURCE = Path("build/editions/lite/print/zpevnik.pdf")
PLACEMENT = Placement(scale=0.69, shift=points(4.0))
A5_PAPER = PAPERS[A5]
BLOCK = BlockSettings(paper=A5, ink="black", cover=False, crop_marks=True, spine_margin_mm=12.5, outer_margin_mm=4.5)
PLAIN = BlockSettings(paper=A5)
ROOM = points(CROP_MARK_ROOM_MM)


def box_line(name: str, left: float, bottom: float, right: float, top: float) -> str:
    return f"{name}: {left:.2f} {bottom:.2f} {right:.2f} {top:.2f}\n"


def pdfinfo_report(pages: int = 4, trim_width: float = A5_PAPER.width, room: float = ROOM, bleed: float = 0) -> str:
    """What pdfinfo -box says about a PDF with the A5 page in the middle of room on every side."""
    height = A5_PAPER.height
    return (f"Pages: {pages}\n" + box_line("MediaBox", 0, 0, trim_width + 2 * room, height + 2 * room)
            + box_line("BleedBox", room - bleed, room - bleed, room + trim_width + bleed, room + height + bleed)
            + box_line("TrimBox", room, room, room + trim_width, room + height))


PIXELS_PER_MM = INK_DPI / 25.4
TRIMMED_WIDTH_PIXELS = round(A5_PAPER.width * INK_DPI / 72)


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


class Format(unittest.TestCase):
    def test_the_ink_and_the_colour_choose_the_format(self):
        self.assertEqual(print_format(BlockSettings(ink="black")), PRINT_BLACK)
        self.assertEqual(print_format(BlockSettings()), PRINT)
        self.assertEqual(print_format(BlockSettings(colour="cmyk")), PRINT_CMYK)


class Wrapper(unittest.TestCase):
    def includes(self, tex: str) -> list[str]:
        return [line for line in tex.splitlines() if line.startswith("\\includepdf")]

    def test_every_page_is_scaled_and_shifted_away_from_the_spine(self):
        lines = self.includes(wrapper_tex(SOURCE, 4, PLACEMENT, PLAIN))
        self.assertEqual([line.split("pages=")[1].split(",")[0] for line in lines], ["1", "2", "3", "4"])
        self.assertEqual([line.split("offset=")[1].split(" ")[0] for line in lines],
                         ["4.000mm", "-4.000mm", "4.000mm", "-4.000mm"])
        self.assertTrue(all("scale=0.69000000" in line and "noautoscale=true" in line for line in lines))
        self.assertTrue(all(line.endswith("{build/editions/lite/print/zpevnik.pdf}") for line in lines))

    def test_an_odd_number_of_pages_gets_a_blank_page_at_the_end(self):
        self.assertIn("\\null\n\\end{document}", wrapper_tex(SOURCE, 3, PLACEMENT, PLAIN))
        self.assertNotIn("\\null", wrapper_tex(SOURCE, 4, PLACEMENT, PLAIN))

    def test_the_paper_is_the_blocks(self):
        self.assertTrue(wrapper_tex(SOURCE, 2, PLACEMENT, PLAIN).startswith("\\documentclass[a5paper]{article}"))
        self.assertTrue(wrapper_tex(SOURCE, 2, PLACEMENT, BlockSettings(paper=A4))
                        .startswith("\\documentclass[a4paper]{article}"))

    def test_without_crop_marks_and_bleed_the_pdf_page_is_the_trimmed_page(self):
        self.assertNotIn("crop", wrapper_tex(SOURCE, 2, PLACEMENT, PLAIN))

    def test_crop_marks_add_room_and_the_page_names_its_trim_and_bleed(self):
        tex = wrapper_tex(SOURCE, 2, PLACEMENT, BlockSettings(paper=A5, crop_marks=True, bleed_mm=3))
        self.assertIn("\\usepackage[cam,noinfo,center,pdftex,width=178.000mm,height=240.000mm]{crop}", tex)
        bleed = points(3)
        trim = f"[{ROOM:.3f} {ROOM:.3f} {ROOM + A5_PAPER.width:.3f} {ROOM + A5_PAPER.height:.3f}]"
        bleed_box = (f"[{ROOM - bleed:.3f} {ROOM - bleed:.3f} {ROOM + A5_PAPER.width + bleed:.3f} "
                     f"{ROOM + A5_PAPER.height + bleed:.3f}]")
        self.assertIn(f"/TrimBox {trim} /BleedBox {bleed_box}", tex)

    def test_a_bleed_without_crop_marks_is_the_room_around_the_page(self):
        tex = wrapper_tex(SOURCE, 2, PLACEMENT, BlockSettings(paper=A5, bleed_mm=3))
        self.assertIn("\\usepackage[off,noinfo,center,pdftex,width=154.000mm,height=216.000mm]{crop}", tex)
        self.assertIn(f"/BleedBox [0.000 0.000 {A5_PAPER.width + 2 * points(3):.3f}", tex)


class Check(unittest.TestCase):
    def check(self, info: str = pdfinfo_report(), pages: tuple[Greymap, ...] = GOOD_PAGES,
              inks: tuple[InkCoverage, ...] = (BLACK,) * 4, block: BlockSettings = BLOCK,
              format_name: str = PRINT_BLACK, fonts: tuple[str, ...] = (),
              images: tuple[tuple[int, str], ...] = ((5, "gray"),)):
        def render_page(pdf: Path, position: int, dpi: int, area, page_height: float) -> Greymap:
            return pages[position - 1]

        with (mock.patch.object(print_pdf, "pdfinfo", return_value=info),
              mock.patch.object(print_pdf, "render_page", side_effect=render_page),
              mock.patch.object(print_pdf, "ink_coverage", return_value=list(inks)),
              mock.patch.object(print_pdf, "unembedded_fonts", return_value=list(fonts)),
              mock.patch.object(print_pdf, "image_colours", return_value=list(images))):
            return check_print_pdf(Path("x.pdf"), block, format_name)

    def test_an_a5_block_inside_the_margins_in_black_ink_passes_and_reports_its_narrowest_margins(self):
        checked = self.check(pages=(rendered(13, 5, 1), rendered(14, 6, 2), rendered(13.2, 4.8, 3), BLANK))
        self.assertEqual(checked.pages, 4)
        self.assertAlmostEqual(millimetres(checked.narrowest.spine), 13, delta=0.1)
        self.assertAlmostEqual(millimetres(checked.narrowest.outer), 4.8, delta=0.1)

    def test_another_trimmed_page_is_refused(self):
        with self.assertRaisesRegex(PrintError, "not A5"):
            self.check(info=pdfinfo_report(trim_width=595.0))

    def test_crop_marks_without_room_for_them_are_refused(self):
        with self.assertRaisesRegex(PrintError, "with 15.0 mm around it"):
            self.check(info=pdfinfo_report(room=0))

    def test_a_bleed_box_other_than_the_table_says_is_refused(self):
        with self.assertRaisesRegex(PrintError, "the bleed box"):
            self.check(info=pdfinfo_report(bleed=points(3)))
        bled = BlockSettings(paper=A5, ink="black", crop_marks=True, bleed_mm=3, spine_margin_mm=12.5,
                             outer_margin_mm=4.5)
        self.assertEqual(self.check(info=pdfinfo_report(bleed=points(3)), block=bled).pages, 4)

    def test_an_odd_page_count_is_refused(self):
        with self.assertRaisesRegex(PrintError, "odd number"):
            self.check(info=pdfinfo_report(pages=3))

    def test_a_font_that_is_not_embedded_is_refused(self):
        with self.assertRaisesRegex(PrintError, "does not embed: Helvetica"):
            self.check(fonts=("Helvetica",))

    def test_ink_too_close_to_the_spine_or_the_edge_names_its_page_and_what_was_measured(self):
        pages = (rendered(13, 5, 1), rendered(12.3, 5, 2), rendered(13, 5, 3), rendered(13, 4.2, 4))
        with self.assertRaises(PrintError) as caught:
            self.check(pages=pages)
        self.assertRegex(str(caught.exception), r"pages 2 \(12\.\d\d mm at the spine, 5\.\d\d mm outside\), "
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

    def test_an_rgb_image_is_refused_in_black_ink_and_in_cmyk(self):
        for format_name in (PRINT_BLACK, PRINT_CMYK):
            with self.subTest(format_name), self.assertRaisesRegex(PrintError, "pages 2 of .* images in RGB"):
                self.check(format_name=format_name, images=((2, "rgb"), (3, "cmyk")))

    def test_a_block_in_rgb_colour_is_checked_for_neither_one_ink_nor_its_images(self):
        checked = self.check(inks=(InkCoverage(0.5, 0.5, 0, 0),) * 4, format_name=PRINT, images=((1, "rgb"),))
        self.assertEqual(checked.pages, 4)


class Placing(unittest.TestCase):
    def test_the_pages_are_placed_with_the_pixel_the_check_may_lose_to_spare(self):
        # An A4 page (595 pt, 2480 pixels at 300 dpi) with ink 28 pt from both edges.
        a4 = Box(0, 0, 595.0, 842.0)
        width = round(a4.width / INK_PIXEL_PT)
        first = round(28 / INK_PIXEL_PT)
        row = b"\xff" * first + b"\x00" * (width - 2 * first) + b"\xff" * first
        with mock.patch.object(print_pdf, "render_page", return_value=Greymap(width, 1, row)):
            placement = placement_for(Path("a4.pdf"), a4, 2, BLOCK)
        centre, reach = A5_PAPER.width / 2, a4.width / 2 - first * INK_PIXEL_PT
        spine = centre - placement.scale * reach + placement.shift  # the left of the first, a right-hand page
        outer = centre - placement.scale * reach - placement.shift
        self.assertAlmostEqual(spine, points(BLOCK.spine_margin_mm) + INK_PIXEL_PT)
        self.assertAlmostEqual(outer, points(BLOCK.outer_margin_mm) + INK_PIXEL_PT)

    def test_without_margins_a_page_inked_to_its_edges_keeps_its_size_on_a4(self):
        a4 = Box(0, 0, 595.0, 842.0)
        width = math.ceil(a4.width / INK_PIXEL_PT)  # the last pixel reaches beyond the page
        with mock.patch.object(print_pdf, "render_page", return_value=Greymap(width, 1, b"\x00" * width)):
            self.assertEqual(placement_for(Path("a4.pdf"), a4, 2, BlockSettings()), Placement(scale=1.0, shift=0.0))


class Delivery(unittest.TestCase):
    def test_the_file_for_the_printer_names_the_edition_and_the_version(self):
        self.assertEqual(delivered_path("lite", "8.49.3", "blok"),
                         Path("build/print/lite/zpevnik-lite-8.49.3-blok.pdf"))

    def test_a_new_version_replaces_the_earlier_ones_of_the_same_part(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "build/print/lite"
            folder.mkdir(parents=True)
            for name in ("zpevnik-lite-8.48.1-blok.pdf", "zpevnik-lite-8.48.1-obalka.pdf"):
                (folder / name).write_text("old", encoding="utf-8")
            (root / "made.pdf").write_text("new", encoding="utf-8")
            with mock.patch.object(print_pdf, "current_version", return_value="8.49.?"):
                target = deliver(root, Path("made.pdf"), "lite", "blok")
            self.assertEqual(target, Path("build/print/lite/zpevnik-lite-8.49.x-blok.pdf"))
            self.assertEqual(sorted(path.name for path in folder.iterdir()),
                             ["zpevnik-lite-8.48.1-obalka.pdf", "zpevnik-lite-8.49.x-blok.pdf"])
            self.assertEqual((root / target).read_text(encoding="utf-8"), "new")
