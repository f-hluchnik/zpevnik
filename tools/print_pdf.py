#!/usr/bin/env python3
"""Make the PDF a printer gets: an edition's print format on A5, as its [print] table asks.

The book is typeset on A4 (zpevnik.tex). The printer gets the same pages, vector and with every
font embedded, scaled down and placed on A5 by a small LaTeX document of pdfpages
(`zpevnik-a5.tex`, written next to the PDF it scales), so nothing but TeX Live is needed for it.
The edition's `[print]` table (edition.toml) says what the printer needs:

- the margins: no letter closer than `spine_margin_mm` to the bound edge and `outer_margin_mm`
  to the outer edge. Every page of the A4 PDF is rendered at 300 dpi and its ink measured
  (letters, scores and lines alike; any pixel that is not pure white), and print_layout.py works
  out the scale and the shift away from the spine. The scale is at most A4 to A5 (1/sqrt(2)), so
  every song still fits its page;
- `skip_first_pages`: pages left out of the book block, an even number (a cover the printer gets
  separately);
- `crop_marks`: the PDF page is the A5 page with 15 mm around it for crop marks (the crop
  package) and names the A5 page as its trim box. Nothing is printed to the edge, so there is
  no bleed: the bleed box is the trim box.

An odd page count gets a blank page at the end. The finished PDF is checked: the trimmed page is
A5, the page count even, and a format in one ink (formats.py) uses black ink alone on every page
(Ghostscript's ink coverage). The margins are measured again on the finished PDF, after the
scaling, the shift and the crop marks: every page is rendered at 300 dpi inside its trim box and
its ink must keep both margins. The measure is good to about a pixel (0.085 mm), and a pixel the
ink only touches counts as ink; the pages are placed with a pixel to spare, so that a book placed
right passes and one that is not fails. Anything else stops with a message that names the pages; the
narrowest margins measured are printed with the result.

`--path` prints where the A5 PDF is (made or not), so the Makefile does not repeat the layout of build/.

Usage: python3 tools/print_pdf.py [--edition NAME] [--format NAME] [--path] [repo-root]
       (run after building the format: make EDITION=... FORMAT=print CHORDS=black; adding
       SIZE=A5 does both)
Needs pdflatex with pdfpages and crop, poppler (pdfinfo, pdftoppm) and, for a format in one ink,
Ghostscript. Python >= 3.11, standard library only.
"""
import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from build_edition import LatexError, run_latexmk
from edition import EditionError, PrintSettings, edition_file, read_print_settings
from formats import PRINT, add_format_argument, is_black_ink
from paths import (BOOK_PDF_NAME, PRINT_PDF_NAME, PRINT_WRAPPER_NAME, add_edition_argument,
                   add_root_argument, edition_output_dir)
from pdf_programs import (POINTS_PER_INCH, Box, InkCoverage, PageBoxes, PdfProgramError, ink_columns,
                          ink_coverage, page_boxes, page_count, pdfinfo, render_page)
from print_layout import (A5_HEIGHT_PT, A5_WIDTH_PT, LayoutError, Margins, Placement, Reach, fit,
                          millimetres, page_margins, points)

# On every side of the A5 page, for the crop marks: the crop package's `cam' marks reach 35 pt
# (12.3 mm) from the trim. The cover of skaut-kravare uses the same room (print-cover/).
CROP_MARK_ROOM_MM = 15.0
SIZE_TOLERANCE_PT = 1.0
INK_DPI = 300  # the resolution the ink is measured at
INK_PIXEL_PT = POINTS_PER_INCH / INK_DPI  # 0.085 mm: a margin is measured at most that much too narrow
REPORTED_PAGES = 10  # an error names at most this many pages
PDFLATEX = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error"]
SETUP_HINT = "(README, Tisk)"

WRAPPER_START = r"\documentclass[a5paper]{article}" + "\n" + r"\usepackage{pdfpages}" + "\n"
WRAPPER_BODY = r"\pagestyle{empty}" + "\n" + r"\begin{document}" + "\n"
WRAPPER_END = r"\end{document}" + "\n"


class PrintError(Exception):
    """The print PDF cannot be made, or is not what the printer asked for."""


@dataclass(frozen=True)
class CheckedPdf:
    """A print PDF that passed the checks: its page count and the narrowest margins of its ink."""
    pages: int
    narrowest: Margins


def crop_marks_tex() -> str:
    """Crop marks around the A5 page (cam: corner marks, noinfo: no file name and date beside them),
    and the A5 page as the trim box and the bleed box, in PDF points from the bottom-left corner."""
    room = points(CROP_MARK_ROOM_MM)
    width_mm, height_mm = (millimetres(side) + 2 * CROP_MARK_ROOM_MM for side in (A5_WIDTH_PT, A5_HEIGHT_PT))
    box = f"[{room:.3f} {room:.3f} {room + A5_WIDTH_PT:.3f} {room + A5_HEIGHT_PT:.3f}]"
    return (f"\\usepackage[cam,noinfo,center,pdftex,width={width_mm:.3f}mm,height={height_mm:.3f}mm]{{crop}}\n"
            f"\\pdfpageattr{{/TrimBox {box} /BleedBox {box}}}\n")


def wrapper_tex(source: Path, pages: range, placement: Placement, crop_marks: bool) -> str:
    """The wrapper document: one \\includepdf per page, scaled and shifted away from the spine
    (to the right on a right-hand page, to the left on a left-hand one), and a blank page at the
    end if the count is odd."""
    lines = [WRAPPER_START, crop_marks_tex() if crop_marks else "", WRAPPER_BODY]
    for position, page in enumerate(pages, start=1):
        shift = millimetres(placement.shift if position % 2 else -placement.shift)
        lines.append(f"\\includepdf[pages={page},fitpaper=false,noautoscale=true,scale={placement.scale:.8f},"
                     f"offset={shift:.3f}mm 0mm]{{{source.as_posix()}}}\n")
    if len(pages) % 2:
        lines.append("\\null\n")
    lines.append(WRAPPER_END)
    return "".join(lines)


def kept_pages(total: int, skip_first: int) -> range:
    """The pages of the source that go into the book block; PrintError if none is left."""
    if skip_first >= total:
        raise PrintError(f"skip_first_pages = {skip_first} leaves nothing of {total} pages")
    return range(skip_first + 1, total + 1)


def required_margins(settings: PrintSettings) -> Margins:
    return Margins(spine=points(settings.spine_margin_mm), outer=points(settings.outer_margin_mm))


def page_ink(pdf: Path, page: int, area: Box, page_height: float) -> Reach | None:
    """How far the ink of a page reaches inside the area, in pt from its left edge; None for no ink."""
    columns = ink_columns(render_page(pdf, page, INK_DPI, area, page_height))
    if columns is None:
        return None
    return Reach(left=columns.first * INK_PIXEL_PT, right=(columns.last + 1) * INK_PIXEL_PT)


def placement_for(source: Path, page_area: Box, pages: range, settings: PrintSettings) -> Placement:
    """The scale and the shift that keep the ink of the kept pages inside the margins, with the
    pixel the check of the finished PDF may lose to spare."""
    required = required_margins(settings)
    placed = Margins(spine=required.spine + INK_PIXEL_PT, outer=required.outer + INK_PIXEL_PT)
    reaches = [page_ink(source, page, page_area, page_area.height) for page in pages]
    return fit(reaches, page_area.width, A5_WIDTH_PT, placed)


def listed(pages: Sequence[object]) -> str:
    more = f" and {len(pages) - REPORTED_PAGES} more" if len(pages) > REPORTED_PAGES else ""
    return ", ".join(map(str, pages[:REPORTED_PAGES])) + more


def is_close(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= SIZE_TOLERANCE_PT


def check_boxes(boxes: PageBoxes, crop_marks: bool) -> None:
    """The trimmed page is A5; the PDF page is that, or with the room for the crop marks."""
    trim, media = boxes.trim, boxes.media
    if not (is_close(trim.width, A5_WIDTH_PT) and is_close(trim.height, A5_HEIGHT_PT)):
        raise PrintError(f"the trimmed page is {trim.width:.1f} x {trim.height:.1f} pt, not A5")
    room = 2 * points(CROP_MARK_ROOM_MM) if crop_marks else 0
    if not (is_close(media.width, trim.width + room) and is_close(media.height, trim.height + room)):
        raise PrintError(f"the PDF page is {media.width:.1f} x {media.height:.1f} pt, expected the A5 page "
                         + ("with room for the crop marks" if crop_marks else "alone"))


def ink_margins(pdf: Path, count: int, boxes: PageBoxes) -> dict[int, Margins]:
    """The margins of the ink of every printed page with any ink, measured on the page rendered
    inside its trim box (so the crop marks around it do not count)."""
    margins = {}
    for position in range(1, count + 1):
        ink = page_ink(pdf, position, boxes.trim, boxes.media.height)
        if ink is not None:
            margins[position] = page_margins(ink, position, 0, boxes.trim.width)
    return margins


def too_narrow(margins: dict[int, Margins], required: Margins) -> list[str]:
    """The pages whose ink comes closer to the spine or the outer edge than required, with what was measured."""
    return [f"{position} ({millimetres(page.spine):.2f} mm at the spine, {millimetres(page.outer):.2f} mm outside)"
            for position, page in margins.items() if page.spine < required.spine or page.outer < required.outer]


def narrowest(margins: dict[int, Margins]) -> Margins:
    return Margins(spine=min(page.spine for page in margins.values()),
                   outer=min(page.outer for page in margins.values()))


def pages_not_in_black_ink(coverages: list[InkCoverage]) -> list[int]:
    return [position for position, coverage in enumerate(coverages, start=1) if not coverage.is_black_only]


def check_print_pdf(pdf: Path, settings: PrintSettings, black_ink: bool) -> CheckedPdf:
    """What the checks measured on the made PDF; PrintError unless it is what the printer asked for."""
    info = pdfinfo(pdf)
    boxes = page_boxes(info)
    check_boxes(boxes, settings.crop_marks)
    count = page_count(info)
    if count % 2:
        raise PrintError(f"{pdf} has an odd number of pages ({count})")
    margins = ink_margins(pdf, count, boxes)
    if not margins:
        raise PrintError(f"{pdf} has no ink on any page")
    outside = too_narrow(margins, required_margins(settings))
    if outside:
        raise PrintError(f"ink closer to the spine than {settings.spine_margin_mm} mm or to the outer edge "
                         f"than {settings.outer_margin_mm} mm on pages {listed(outside)} of {pdf}")
    if black_ink:
        coverages = ink_coverage(pdf)
        if len(coverages) != count:
            raise PrintError(f"Ghostscript reported the inks of {len(coverages)} pages, {pdf} has {count}")
        coloured = pages_not_in_black_ink(coverages)
        if coloured:
            raise PrintError(f"pages {listed(coloured)} of {pdf} use colour inks, not black alone "
                             "(a colour image, e.g. a cover: leave it out with skip_first_pages)")
    return CheckedPdf(pages=count, narrowest=narrowest(margins))


def print_pdf_path(edition: str, format_name: str) -> Path:
    """Where the A5 PDF of the edition's format is, relative to the root: next to the PDF it scales."""
    return edition_output_dir(edition, format_name) / PRINT_PDF_NAME


def print_settings(root: Path, edition: str) -> PrintSettings:
    settings = read_print_settings(root, edition)
    if settings is None:
        raise PrintError(f"{edition_file(edition)} has no [print] table: the A5 PDF is made for a printer, "
                         f"and the table says what the printer needs {SETUP_HINT}")
    return settings


def make_print_pdf(root: Path, edition: str, format_name: str) -> tuple[Path, Placement, CheckedPdf]:
    """Place the built format of the edition on A5; the path of the new PDF (relative to the root),
    the placement used and what the checks measured."""
    settings = print_settings(root, edition)
    folder = edition_output_dir(edition, format_name)
    source = folder / BOOK_PDF_NAME
    if not (root / source).is_file():
        raise PrintError(f"{source} is missing: build it first (make EDITION={edition} FORMAT={PRINT} SIZE=A5 "
                         "does both; the Makefile lists the options)")
    info = pdfinfo(root / source)
    pages = kept_pages(page_count(info), settings.skip_first_pages)
    placement = placement_for(root / source, page_boxes(info).media, pages, settings)
    wrapper = folder / PRINT_WRAPPER_NAME
    (root / wrapper).write_text(wrapper_tex(source, pages, placement, settings.crop_marks), encoding="utf-8")
    try:
        run_latexmk([*PDFLATEX, f"-output-directory={folder}", str(wrapper)], root,
                    folder / wrapper.with_suffix(".log").name)
    except LatexError as error:
        raise PrintError(str(error)) from error
    result = print_pdf_path(edition, format_name)
    return result, placement, check_print_pdf(root / result, settings, is_black_ink(format_name))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_format_argument(parser, default=PRINT)
    add_root_argument(parser)
    parser.add_argument("--path", action="store_true", help="print the path of the A5 PDF and exit")
    args = parser.parse_args()
    if args.path:
        print(print_pdf_path(args.edition, args.format))
        return 0
    try:
        result, placement, checked = make_print_pdf(args.root, args.edition, args.format)
    except (PrintError, EditionError, LayoutError, PdfProgramError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"{result}: {checked.pages} pages, the A4 pages scaled to {placement.scale:.4f} and moved "
          f"{millimetres(placement.shift):.2f} mm away from the spine; the ink is at least "
          f"{millimetres(checked.narrowest.spine):.2f} mm from the spine and "
          f"{millimetres(checked.narrowest.outer):.2f} mm from the outer edge")
    return 0


if __name__ == "__main__":
    sys.exit(main())
