#!/usr/bin/env python3
"""Make the book block a printer gets, as the edition's [print.block] table asks (`make print`).

The book is typeset on A4 (zpevnik.tex). The printer gets the same pages, vector and with every
font embedded, placed on the block's paper by a small LaTeX document of pdfpages
(`zpevnik-block.tex`, written next to the PDF it places), so nothing but TeX Live is needed for
it. The [print.block] table (edition.py; docs/printing.md) says what the printer needs:

- `paper`: A4 or A5. Every page of the A4 PDF is rendered at 300 dpi and its ink measured
  (letters, scores and lines alike; any pixel that is not pure white), and print_layout.py works
  out the scale and the shift away from the spine that keep the margins. The book never grows,
  so every song still fits its page;
- `spine_margin_mm`, `outer_margin_mm`: no ink closer to the bound edge and the outer edge;
- `ink` and `colour`: the format the book is typeset in (formats.py): `black` is print-black,
  everything in black ink alone; `colour` is print, or print-cmyk with `colour = "cmyk"`: the
  chords in the CMYK of the edition's `profile`, the scores in black ink;
- `cover`: false leaves the book's own cover and its back out of the block (zpevnik.sty), for a
  printer who gets the cover separately;
- `crop_marks`: the PDF page is the trimmed page with 15 mm around it for crop marks (the crop
  package); `bleed_mm`: the bleed box, that far beyond the trimmed page. The PDF names both.

An odd page count gets a blank page at the end. The finished PDF is checked, and anything wrong
stops with a message that names the pages: the trimmed page is the paper, the bleed box what the
table says, the page count even, every font embedded; the margins are measured again on the
finished PDF, inside its trim box (every pixel that is not pure white is ink, measured to about
a pixel, 0.085 mm, so the pages are placed with a pixel to spare for every margin asked for); a
black-ink block uses black ink alone on every page (Ghostscript's ink coverage), and a black-ink
or CMYK block has no image in RGB. The checked PDF goes to the folder of the files for the
printer, build/print/<edition>/, as zpevnik-<edition>-<version>-blok.pdf, in place of what was
there (print_output.py, which also has the page boxes and the checks the cover shares).

For the Makefile, `--block-format` prints the format the edition's block is typeset in, and
`--path` the folder of the files for the printer, so the Makefile does not repeat the layout of
build/.

Usage: python3 tools/print_pdf.py [--edition NAME] [--block-format | --path] [repo-root]
       (run after building the block's format; make print does both)
Needs pdflatex with pdfpages and crop, poppler (pdfinfo, pdftoppm, pdffonts, pdfimages) and
Ghostscript. Python >= 3.11, standard library only.
"""
import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from edition import BLACK_INK, CMYK, BlockSettings, EditionError, read_print_settings
from formats import PRINT, PRINT_BLACK, PRINT_CMYK, is_black_ink, is_cmyk
from paths import (BOOK_PDF_NAME, PRINT_BLOCK_PART, PRINT_WRAPPER_NAME, add_edition_argument, add_root_argument,
                   edition_output_dir)
from pdf_programs import (POINTS_PER_INCH, Box, InkCoverage, PageBoxes, PdfProgramError, ink_columns, ink_coverage,
                          page_boxes, page_count, pdfinfo, render_page, rendered_left)
from print_layout import PAPERS, LayoutError, Margins, Placement, Reach, fit, millimetres, page_margins, points
from print_output import (END_DOCUMENT, PrintError, check_boxes, check_fonts_embedded, check_no_rgb_images,
                          clear_delivery, compile_document, deliver, delivery_dir, document_start, listed)

INK_DPI = 300  # the resolution the ink is measured at
INK_PIXEL_PT = POINTS_PER_INCH / INK_DPI  # 0.085 mm: a margin is measured at most that much too narrow
WRAPPER_PACKAGES = ("pdfpages",)
WRAPPER_BODY = r"\pagestyle{empty}" + "\n" + r"\begin{document}" + "\n"


@dataclass(frozen=True)
class CheckedPdf:
    """A print PDF that passed the checks: its page count and the narrowest margins of its ink."""
    pages: int
    narrowest: Margins


def print_format(block: BlockSettings) -> str:
    """The format the block is typeset in (formats.py)."""
    if block.ink == BLACK_INK:
        return PRINT_BLACK
    return PRINT_CMYK if block.colour == CMYK else PRINT


def wrapper_tex(source: Path, pages: int, placement: Placement, block: BlockSettings) -> str:
    """The wrapper document: one \\includepdf per page, scaled and shifted away from the spine
    (to the right on a right-hand page, to the left on a left-hand one), and a blank page at the
    end if the count is odd."""
    lines = [document_start(block, WRAPPER_PACKAGES), WRAPPER_BODY]
    for page in range(1, pages + 1):
        shift = millimetres(placement.shift if page % 2 else -placement.shift)
        lines.append(f"\\includepdf[pages={page},fitpaper=false,noautoscale=true,scale={placement.scale:.8f},"
                     f"offset={shift:.3f}mm 0mm]{{{source.as_posix()}}}\n")
    if pages % 2:
        lines.append("\\null\n")
    lines.append(END_DOCUMENT)
    return "".join(lines)


def required_margins(block: BlockSettings) -> Margins:
    return Margins(spine=points(block.spine_margin_mm), outer=points(block.outer_margin_mm))


def page_ink(pdf: Path, page: int, area: Box, page_height: float) -> Reach | None:
    """How far the ink of a page reaches inside the area, in pt from the page's left edge; None for no ink."""
    columns = ink_columns(render_page(pdf, page, INK_DPI, area, page_height))
    if columns is None:
        return None
    # The pixels at the area's edges reach beyond it by less than a pixel: ink there is at the edge.
    left = rendered_left(area, INK_DPI)
    return Reach(left=max(area.left, left + columns.first * INK_PIXEL_PT),
                 right=min(area.right, left + (columns.last + 1) * INK_PIXEL_PT))


def with_spare_pixel(margin: float) -> float:
    """A margin with the pixel the check of the finished PDF may lose to spare; no margin needs none."""
    return margin + INK_PIXEL_PT if margin else margin


def placement_for(source: Path, page_area: Box, pages: int, block: BlockSettings) -> Placement:
    """The scale and the shift that keep the ink of every page inside the margins."""
    required = required_margins(block)
    placed = Margins(spine=with_spare_pixel(required.spine), outer=with_spare_pixel(required.outer))
    reaches = [page_ink(source, page, page_area, page_area.height) for page in range(1, pages + 1)]
    return fit(reaches, page_area.width, PAPERS[block.paper], placed)


def ink_margins(pdf: Path, count: int, boxes: PageBoxes) -> dict[int, Margins]:
    """The margins of the ink of every printed page with any ink, measured on the page rendered
    inside its trim box (so the crop marks around it do not count)."""
    margins = {}
    for position in range(1, count + 1):
        ink = page_ink(pdf, position, boxes.trim, boxes.media.height)
        if ink is not None:
            margins[position] = page_margins(ink, position, boxes.trim.left, boxes.trim.width)
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


def check_black_ink(pdf: Path, count: int) -> None:
    coverages = ink_coverage(pdf)
    if len(coverages) != count:
        raise PrintError(f"Ghostscript reported the inks of {len(coverages)} pages, {pdf} has {count}")
    coloured = pages_not_in_black_ink(coverages)
    if coloured:
        raise PrintError(f"pages {listed(coloured)} of {pdf} use colour inks, not black alone")


def check_print_pdf(pdf: Path, block: BlockSettings, format_name: str) -> CheckedPdf:
    """What the checks measured on the made PDF; PrintError unless it is what the printer asked for."""
    info = pdfinfo(pdf)
    boxes = page_boxes(info)
    check_boxes(boxes, block)
    count = page_count(info)
    if count % 2:
        raise PrintError(f"{pdf} has an odd number of pages ({count})")
    check_fonts_embedded(pdf)
    margins = ink_margins(pdf, count, boxes)
    if not margins:
        raise PrintError(f"{pdf} has no ink on any page")
    outside = too_narrow(margins, required_margins(block))
    if outside:
        raise PrintError(f"ink closer to the spine than {block.spine_margin_mm} mm or to the outer edge "
                         f"than {block.outer_margin_mm} mm on pages {listed(outside)} of {pdf}")
    if is_black_ink(format_name):
        check_black_ink(pdf, count)
    if is_black_ink(format_name) or is_cmyk(format_name):
        check_no_rgb_images(pdf)
    return CheckedPdf(pages=count, narrowest=narrowest(margins))


def block_wrapper(edition: str, block: BlockSettings) -> Path:
    """The document that places the block on its paper, relative to the root: next to the book."""
    return edition_output_dir(edition, print_format(block)) / PRINT_WRAPPER_NAME


def block_pdf(edition: str, block: BlockSettings) -> Path:
    """The block placed on its paper, relative to the root."""
    return block_wrapper(edition, block).with_suffix(".pdf")


def make_print_pdf(root: Path, edition: str) -> tuple[Path, Placement, CheckedPdf]:
    """Place the edition's built print format on the block's paper, check it and deliver it, in
    place of what an earlier make print delivered; the path of the file for the printer (relative
    to the root), the placement used and what the checks measured."""
    block = read_print_settings(root, edition).block
    format_name = print_format(block)
    folder = edition_output_dir(edition, format_name)
    source = folder / BOOK_PDF_NAME
    if not (root / source).is_file():
        raise PrintError(f"{source} is missing: make print EDITION={edition} builds it first")
    info = pdfinfo(root / source)
    pages = page_count(info)
    placement = placement_for(root / source, page_boxes(info).media, pages, block)
    placed = compile_document(root, block_wrapper(edition, block), wrapper_tex(source, pages, placement, block))
    checked = check_print_pdf(root / placed, block, format_name)
    clear_delivery(root, edition)
    return deliver(root, placed, edition, PRINT_BLOCK_PART), placement, checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_root_argument(parser)
    what = parser.add_mutually_exclusive_group()
    what.add_argument("--block-format", action="store_true",
                      help="print the format the edition's block is typeset in and exit")
    what.add_argument("--path", action="store_true", help="print the folder of the files for the printer and exit")
    args = parser.parse_args()
    try:
        if args.block_format:
            print(print_format(read_print_settings(args.root, args.edition).block))
            return 0
        if args.path:
            print(delivery_dir(args.edition))
            return 0
        result, placement, checked = make_print_pdf(args.root, args.edition)
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
