#!/usr/bin/env python3
"""Scale the PDF of an edition's print format to A5 for a printer.

The book is typeset on A4 (zpevnik.tex); the printer gets the same pages scaled by 1/sqrt(2),
which is exactly A4 to A5 (D-142), so every song still fits its page. The scaling is a small
LaTeX document of pdfpages (`zpevnik-a5.tex`, written next to the PDF it scales), so nothing
but TeX Live is needed. Vector text and fonts stay as they are.

Binding: the book has one set of margins for every page. Its ink (the hanging labels R., 1., ...
included) is 7.1 mm from both edges at A5, so there are 14.2 mm to share between the spine side and
the outer edge. In a bound, double-sided book the right-hand pages have the spine on their left and
the left-hand pages on their right: --spine-shift-mm moves every page away from the spine by that
much (right on the right-hand pages, left on the left-hand ones). 3 mm give 10.1 mm at the spine
and 4.1 mm at the outer edge; the printer says how much room its binding needs and how close to
the edge it prints. The first page is a right-hand one. The cover may be handed over separately:
--skip-first drops that many pages from the start, an even number so that no page changes sides.
An odd page count gets a blank page at the end.

Usage: python3 tools/print_pdf.py [--edition NAME] [--format NAME] [--skip-first N]
           [--spine-shift-mm MM] [repo-root]
       (run after building the format: make EDITION=... FORMAT=...; `make print` does both)
Needs pdflatex with pdfpages and pdfinfo (poppler). Python >= 3.11, standard library only.
"""
import argparse
import math
import re
import subprocess
import sys
from pathlib import Path

from build_edition import LatexError, run_latexmk
from formats import PRINT, add_format_argument
from paths import (BOOK_PDF_NAME, PRINT_PDF_NAME, PRINT_WRAPPER_NAME, add_edition_argument,
                   add_root_argument, edition_output_dir)

A5_SCALE = 1 / math.sqrt(2)  # A4 to A5 (and A5 to A6): the sides of ISO paper differ by this factor
A5_SIZE_PT = (419.53, 595.28)
SIZE_TOLERANCE_PT = 1.0
PAPER_OPTION = "a5paper"
DEFAULT_SPINE_SHIFT_MM = 0.0  # the book as it is scaled; the printer's binding decides
PAGES_LINE = re.compile(r"^Pages:\s+(\d+)$", re.M)
PAGE_SIZE_LINE = re.compile(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", re.M)
PDFLATEX = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error"]

WRAPPER_PREAMBLE = (r"\documentclass[" + PAPER_OPTION + r"]{article}" + "\n"
                    r"\usepackage{pdfpages}" + "\n"
                    r"\pagestyle{empty}" + "\n"
                    r"\begin{document}" + "\n")
WRAPPER_END = r"\end{document}" + "\n"


class PrintError(Exception):
    """The print PDF cannot be made, or is not what a printer expects."""


def wrapper_tex(source: Path, pages: range, spine_shift_mm: float) -> str:
    """The wrapper document: one \\includepdf per page, scaled and shifted away from the spine
    (to the right on a right-hand page, to the left on a left-hand one), and a blank page at the
    end if the count is odd."""
    lines = [WRAPPER_PREAMBLE]
    for position, page in enumerate(pages, start=1):
        shift = spine_shift_mm if position % 2 else -spine_shift_mm
        lines.append(f"\\includepdf[pages={page},fitpaper=false,noautoscale=true,scale={A5_SCALE:.8f},"
                     f"offset={shift:.3f}mm 0mm]{{{source.as_posix()}}}\n")
    if len(pages) % 2:
        lines.append("\\null\n")
    lines.append(WRAPPER_END)
    return "".join(lines)


def kept_pages(total: int, skip_first: int) -> range:
    """The pages of the source that go to the printer. PrintError if dropping them would move a
    page to the other side of the spine, or leave nothing."""
    if skip_first % 2:
        raise PrintError(f"--skip-first must be even (got {skip_first}): an odd number would put "
                         "every page on the other side of the spine")
    if skip_first >= total:
        raise PrintError(f"--skip-first {skip_first} leaves nothing of {total} pages")
    return range(skip_first + 1, total + 1)


def page_count(pdfinfo: str) -> int:
    match = PAGES_LINE.search(pdfinfo)
    if not match:
        raise PrintError("pdfinfo did not report the number of pages")
    return int(match.group(1))


def page_size(pdfinfo: str) -> tuple[float, float]:
    match = PAGE_SIZE_LINE.search(pdfinfo)
    if not match:
        raise PrintError("pdfinfo did not report one page size")
    return float(match.group(1)), float(match.group(2))


def pdfinfo(pdf: Path) -> str:
    result = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        raise PrintError(f"pdfinfo failed on {pdf}: {result.stderr.strip()}")
    return result.stdout


def check_print_pdf(pdf: Path) -> int:
    """The page count of the made PDF; PrintError unless it is A5 with an even number of pages."""
    info = pdfinfo(pdf)
    width, height = page_size(info)
    if any(abs(actual - expected) > SIZE_TOLERANCE_PT for actual, expected in zip((width, height), A5_SIZE_PT)):
        raise PrintError(f"{pdf} is {width} x {height} pt, not A5")
    count = page_count(info)
    if count % 2:
        raise PrintError(f"{pdf} has an odd number of pages ({count})")
    return count


def make_print_pdf(root: Path, edition: str, format_name: str, skip_first: int,
                   spine_shift_mm: float) -> Path:
    """Scale the built format of the edition to A5; the path of the new PDF, relative to the root."""
    folder = edition_output_dir(edition, format_name)
    source = folder / BOOK_PDF_NAME
    if not (root / source).is_file():
        raise PrintError(f"{source} is missing: build it first (make EDITION={edition} FORMAT={format_name})")
    pages = kept_pages(page_count(pdfinfo(root / source)), skip_first)
    wrapper = folder / PRINT_WRAPPER_NAME
    (root / wrapper).write_text(wrapper_tex(source, pages, spine_shift_mm), encoding="utf-8")
    try:
        run_latexmk([*PDFLATEX, f"-output-directory={folder}", str(wrapper)], root,
                    folder / wrapper.with_suffix(".log").name)
    except LatexError as error:
        raise PrintError(str(error)) from error
    result = folder / PRINT_PDF_NAME
    check_print_pdf(root / result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_format_argument(parser, default=PRINT)
    add_root_argument(parser)
    parser.add_argument("--skip-first", type=int, default=0, metavar="N",
                        help="drop the first N pages, an even number (the cover, handed over separately)")
    parser.add_argument("--spine-shift-mm", type=float, default=DEFAULT_SPINE_SHIFT_MM, metavar="MM",
                        help="move every page this far away from the spine, to widen the margin the "
                             f"binding needs (default: {DEFAULT_SPINE_SHIFT_MM})")
    args = parser.parse_args()
    try:
        print(make_print_pdf(args.root, args.edition, args.format, args.skip_first, args.spine_shift_mm))
    except PrintError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
