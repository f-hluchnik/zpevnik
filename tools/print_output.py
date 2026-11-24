"""What every PDF for the printer shares: its page, how it is made, its checks and its delivery.

A PDF for the printer (the book block, print_pdf.py; the cover, print_cover.py) is a small LaTeX
document compiled with pdfLaTeX. Its trimmed page is the paper of its [print.*] table; around it,
the PDF page has room for the crop marks (the crop package's `cam' marks) or for the bleed alone,
and it names its trim box and its bleed box. The checks here are those that do not depend on what
is printed: the page boxes, every font embedded, no RGB image where the printer takes none.

The checked PDFs are copied to build/print/<edition>/ under the names the printer gets,
zpevnik-<edition>-<version>-<part>.pdf; make print empties the folder first (print_pdf.py), so it
holds what the last make print made and nothing else.

Python >= 3.11, standard library only.
"""
import shutil
from collections.abc import Sequence
from pathlib import Path

from build_edition import LATEXMK, LatexError, run_latexmk
from build_version import UNKNOWN_PATCH
from edition import PageSettings
from generate import current_version
from paths import PRINT_DIR
from pdf_programs import Box, PageBoxes, image_colours, unembedded_fonts
from print_layout import CROP_MARK_ROOM_MM, PAPERS, millimetres, points

SIZE_TOLERANCE_PT = 1.0
REPORTED_PAGES = 10  # an error names at most this many pages
PRINTABLE_IMAGE_COLOURS = {"gray", "cmyk"}  # what a printer who wants no RGB accepts
UNKNOWN_VERSION_IN_NAME = "x"  # the build number in a file name when the history is incomplete
DELIVERED_SUFFIX = ".pdf"
END_DOCUMENT = r"\end{document}" + "\n"


class PrintError(Exception):
    """A PDF for the printer cannot be made, or is not what the printer asked for."""


def document_class(paper: str) -> str:
    return f"\\documentclass[{paper.lower()}paper]{{article}}\n"


def used_packages(packages: Sequence[str]) -> str:
    return "".join(f"\\usepackage{{{package}}}\n" for package in packages)


def document_start(settings: PageSettings, packages: Sequence[str]) -> str:
    """The preamble of a document for the printer: its paper, its page boxes and the packages."""
    return document_class(settings.paper) + page_boxes_tex(settings) + used_packages(packages)


def page_room_mm(settings: PageSettings) -> float:
    """The room around the trimmed page on the PDF page: for crop marks, or for the bleed alone."""
    return CROP_MARK_ROOM_MM if settings.crop_marks else settings.bleed_mm


def page_boxes_tex(settings: PageSettings) -> str:
    """The PDF page around the trimmed page (the crop package: `cam' corner marks, or `off' for the
    bleed alone; noinfo: no file name and date beside them), and its trim box and bleed box, in PDF
    points from the bottom-left corner. Nothing for a page that is the trimmed page itself."""
    room_mm = page_room_mm(settings)
    if not room_mm:
        return ""
    paper = PAPERS[settings.paper]
    room, bleed = points(room_mm), points(settings.bleed_mm)
    width_mm, height_mm = (millimetres(side) + 2 * room_mm for side in (paper.width, paper.height))
    marks = "cam" if settings.crop_marks else "off"
    trim = f"[{room:.3f} {room:.3f} {room + paper.width:.3f} {room + paper.height:.3f}]"
    bleed_box = (f"[{room - bleed:.3f} {room - bleed:.3f} "
                 f"{room + paper.width + bleed:.3f} {room + paper.height + bleed:.3f}]")
    return (f"\\usepackage[{marks},noinfo,center,pdftex,width={width_mm:.3f}mm,height={height_mm:.3f}mm]{{crop}}\n"
            f"\\pdfpageattr{{/TrimBox {trim} /BleedBox {bleed_box}}}\n")


def compile_document(root: Path, tex: Path, text: str) -> Path:
    """Write the document and compile it next to itself (latexmk runs pdfLaTeX as often as the
    document needs); the PDF's path relative to the root."""
    (root / tex).write_text(text, encoding="utf-8")
    try:
        run_latexmk([*LATEXMK, f"-outdir={tex.parent}", str(tex)], root, tex.with_suffix(".log"))
    except LatexError as error:
        raise PrintError(str(error)) from error
    return tex.with_suffix(".pdf")


def listed(pages: Sequence[object]) -> str:
    more = f" and {len(pages) - REPORTED_PAGES} more" if len(pages) > REPORTED_PAGES else ""
    return ", ".join(map(str, pages[:REPORTED_PAGES])) + more


def is_close(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= SIZE_TOLERANCE_PT


def has_size(box: Box, width: float, height: float) -> bool:
    return is_close(box.width, width) and is_close(box.height, height)


def check_boxes(boxes: PageBoxes, settings: PageSettings) -> None:
    """The trimmed page is the paper; the bleed box and the PDF page are as large as the table says."""
    paper = PAPERS[settings.paper]
    if not has_size(boxes.trim, paper.width, paper.height):
        raise PrintError(f"the trimmed page is {boxes.trim.width:.1f} x {boxes.trim.height:.1f} pt, "
                         f"not {settings.paper}")
    bleed = 2 * points(settings.bleed_mm)
    if not has_size(boxes.bleed, paper.width + bleed, paper.height + bleed):
        raise PrintError(f"the bleed box is {boxes.bleed.width:.1f} x {boxes.bleed.height:.1f} pt, "
                         f"not the trimmed page with {settings.bleed_mm} mm around it")
    room = 2 * points(page_room_mm(settings))
    if not has_size(boxes.media, paper.width + room, paper.height + room):
        raise PrintError(f"the PDF page is {boxes.media.width:.1f} x {boxes.media.height:.1f} pt, expected the "
                         f"trimmed page with {page_room_mm(settings)} mm around it")


def check_fonts_embedded(pdf: Path) -> None:
    missing = unembedded_fonts(pdf)
    if missing:
        raise PrintError(f"{pdf} uses fonts it does not embed: {listed(missing)}")


def check_no_rgb_images(pdf: Path) -> None:
    pages = sorted({page for page, colour in image_colours(pdf) if colour not in PRINTABLE_IMAGE_COLOURS})
    if pages:
        raise PrintError(f"pages {listed(pages)} of {pdf} have images in RGB, which the printer does not take")


def file_version(root: Path) -> str:
    """The build's version, as a file name can carry it."""
    return current_version(root).replace(UNKNOWN_PATCH, UNKNOWN_VERSION_IN_NAME)


def delivery_dir(edition: str) -> Path:
    """The folder of the files for the edition's printer, relative to the root."""
    return PRINT_DIR / edition


def delivered_path(edition: str, book_version: str, part: str) -> Path:
    """A file for the printer, relative to the root."""
    return delivery_dir(edition) / f"zpevnik-{edition}-{book_version}-{part}{DELIVERED_SUFFIX}"


def clear_delivery(root: Path, edition: str) -> None:
    """Empty the folder of the files for the edition's printer, so that only new ones go there."""
    for earlier in (root / delivery_dir(edition)).glob("*" + DELIVERED_SUFFIX):
        earlier.unlink()


def deliver(root: Path, source: Path, edition: str, part: str) -> Path:
    """Copy a checked PDF to the folder of the files for the edition's printer; the copy's path
    relative to the root."""
    target = delivered_path(edition, file_version(root), part)
    (root / target.parent).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / source, root / target)
    return target
