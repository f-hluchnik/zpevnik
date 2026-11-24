#!/usr/bin/env python3
"""Make the cover a printer gets separately, as the edition's [print.cover] table asks (`make print`).

The cover is four pages: the front, the inside of the front, the inside of the back and the back.
Its design is the edition's own .tex file (`design` in the table; docs/printing.md), read into a
small pdfLaTeX document made here. The design defines \\zpcoverfront and \\zpcoverback, and may
define \\zpcoverinsidefront and \\zpcoverinsideback (a page it leaves undefined stays white). Each
draws one page inside a TikZ picture over the whole page, where the coordinate (zpcovertrim) is
the lower left corner of the trimmed page; \\zpcovertrimwidth, \\zpcovertrimheight and
\\zpcoverbleed are its size and the bleed, as lengths. TikZ, graphicx and xcolor are loaded; the
design loads anything else it needs.

The pictures of the design are found by name in its folder. For a cover in CMYK, every RGB JPEG of
that folder is first converted to the table's profile (colours.py) into the build, where the
design finds it before the original: the design is drawn from RGB ingredients and the printer
gets CMYK. The page around the trimmed page, the crop marks, the bleed and the boxes are those of
the block (print_output.py).

The finished cover is checked (four pages, the page boxes, every font embedded, no RGB picture in a
cover in CMYK) and goes to build/print/<edition>/ as zpevnik-<edition>-<version>-obalka.pdf. Next to
it, zpevnik-<edition>-<version>-nahled.pdf is the book as the reader will see it: the cover round
the block, every page cut to its trimmed page, without marks; for looking at, not for the printer.

An edition without a [print.cover] table has nothing to make here.

Usage: python3 tools/print_cover.py [--edition NAME] [repo-root]   (after print_pdf.py; or: make print)
Needs pdflatex with crop, pdfpages and TikZ, and poppler (pdfinfo, pdffonts, pdfimages); a cover in
CMYK needs Pillow (colours.py). Python >= 3.11.
"""
import argparse
import shutil
import sys
from pathlib import Path, PurePosixPath

from colours import ColourError, convert_picture, profile_file
from edition import CMYK, BlockSettings, CoverSettings, EditionError, read_print_settings
from paths import PRINT_COVER_PART, PRINT_PREVIEW_PART, add_edition_argument, add_root_argument, print_cover_dir
from pdf_programs import PdfProgramError, page_boxes, page_count, pdfinfo
from print_layout import PAPERS, millimetres
from print_output import (END_DOCUMENT, PrintError, check_boxes, check_fonts_embedded, check_no_rgb_images,
                          compile_document, deliver, document_class, document_start, page_room_mm, used_packages)
from print_pdf import block_pdf

COVER_TEX = Path("cover.tex")
PREVIEW_TEX = Path("preview.tex")
PICTURES_DIR = Path("pictures")  # the design's pictures in CMYK
CONVERTED_SUFFIXES = (".jpg", ".jpeg")  # the pictures converted to CMYK: RGB JPEGs
COVER_PACKAGES = ("tikz", "graphicx", "xcolor")
PREVIEW_PACKAGES = ("pdfpages",)
FRONT, INSIDE_FRONT, INSIDE_BACK, BACK = "zpcoverfront", "zpcoverinsidefront", "zpcoverinsideback", "zpcoverback"
COVER_PAGES = (FRONT, INSIDE_FRONT, INSIDE_BACK, BACK)  # in the order the printer gets them
REQUIRED_PAGES = (FRONT, BACK)
OUTSIDE_PAGES, INSIDE_PAGES = "1-2", "3-4"  # around the block: before it, after it

# One page of the cover: the design's command, if it defines it, in a TikZ picture over the page.
COVER_PAGE_TEX = r"""\newcommand{\printcoverpage}[1]{%
  \begin{tikzpicture}[remember picture, overlay]
    \coordinate (zpcovertrim) at ([shift={(-0.5\zpcovertrimwidth, -0.5\zpcovertrimheight)}]current page.center);
    \ifdefined#1#1\fi
  \end{tikzpicture}\mbox{}\newpage}
"""


def picture_files(design: Path) -> list[Path]:
    """The pictures of the design's folder that a cover in CMYK converts."""
    return sorted(path for path in design.parent.iterdir() if path.suffix.lower() in CONVERTED_SUFFIXES)


def prepare_pictures(root: Path, cover: CoverSettings, target: Path) -> None:
    """Fill the target folder with the design's RGB pictures in the cover's CMYK, by name; for a
    cover in RGB leave it empty. Nothing of an earlier build stays, so the design finds no picture
    it no longer has or that is in the wrong colours."""
    shutil.rmtree(root / target, ignore_errors=True)
    (root / target).mkdir(parents=True)
    if cover.colour != CMYK:
        return
    profile = profile_file(root, cover.profile)
    for picture in picture_files(root / cover.design):
        convert_picture(picture, root / target / picture.name, profile)


def length_tex(name: str, length_mm: float) -> str:
    return f"\\newlength{{\\{name}}}\\setlength{{\\{name}}}{{{length_mm:.3f}mm}}\n"


def required_page_tex(command: str, design: str) -> str:
    """Stop with a message if the design does not define one of the pages every cover has."""
    return (f"\\ifdefined\\{command}\\else\\errmessage{{{design} defines no \\string\\{command}}}\\fi\n")


def cover_tex(cover: CoverSettings, pictures: Path) -> str:
    """The cover's document: the four pages of the design, on the cover's page."""
    paper = PAPERS[cover.paper]
    design = PurePosixPath(cover.design)
    folders = "".join(f"{{{folder}/}}" for folder in (pictures.as_posix(), design.parent))
    return (document_start(cover, COVER_PACKAGES)
            + length_tex("zpcovertrimwidth", millimetres(paper.width))
            + length_tex("zpcovertrimheight", millimetres(paper.height))
            + length_tex("zpcoverbleed", cover.bleed_mm)
            + f"\\graphicspath{{{folders}}}\n"
            + f"\\input{{{design.with_suffix('')}}}\n"
            + "".join(required_page_tex(command, cover.design) for command in REQUIRED_PAGES)
            + COVER_PAGE_TEX
            + "\\pagestyle{empty}\n\\begin{document}\n"
            + "".join(f"\\printcoverpage{{\\{command}}}\n" for command in COVER_PAGES)
            + END_DOCUMENT)


def cut_pages_tex(pages: str, pdf: Path, room_mm: float) -> str:
    """The pages of a PDF for the printer cut to the trimmed page: without the room around it."""
    room = f"{room_mm:.3f}mm"
    return f"\\includepdf[pages={{{pages}}},trim={room} {room} {room} {room},clip]{{{pdf.as_posix()}}}\n"


def preview_tex(cover_pdf: Path, cover: CoverSettings, block: Path, block_settings: BlockSettings) -> str:
    """The book as the reader will see it: the outside of the cover, the block, the inside of the back."""
    cover_room, block_room = page_room_mm(cover), page_room_mm(block_settings)
    return (document_class(block_settings.paper) + used_packages(PREVIEW_PACKAGES)
            + "\\begin{document}\n"
            + cut_pages_tex(OUTSIDE_PAGES, cover_pdf, cover_room)
            + cut_pages_tex("-", block, block_room)
            + cut_pages_tex(INSIDE_PAGES, cover_pdf, cover_room)
            + END_DOCUMENT)


def check_cover(pdf: Path, cover: CoverSettings) -> None:
    """PrintError unless the cover is what the printer asked for."""
    info = pdfinfo(pdf)
    check_boxes(page_boxes(info), cover)
    if page_count(info) != len(COVER_PAGES):
        raise PrintError(f"{pdf} has {page_count(info)} pages, not the {len(COVER_PAGES)} of a cover")
    check_fonts_embedded(pdf)
    if cover.colour == CMYK:
        check_no_rgb_images(pdf)


def make_cover(root: Path, edition: str) -> list[Path] | None:
    """Make, check and deliver the edition's cover and the preview of the book with it; their paths
    for the printer (relative to the root), or None for an edition without a [print.cover] table."""
    settings = read_print_settings(root, edition)
    cover = settings.cover
    if cover is None:
        return None
    folder = print_cover_dir(edition)
    pictures = folder / PICTURES_DIR
    prepare_pictures(root, cover, pictures)
    cover_pdf = compile_document(root, folder / COVER_TEX, cover_tex(cover, pictures))
    check_cover(root / cover_pdf, cover)
    block = block_pdf(edition, settings.block)
    if not (root / block).is_file():
        raise PrintError(f"{block} is missing: print_pdf.py makes it first (make print EDITION={edition})")
    preview = compile_document(root, folder / PREVIEW_TEX, preview_tex(cover_pdf, cover, block, settings.block))
    return [deliver(root, cover_pdf, edition, PRINT_COVER_PART), deliver(root, preview, edition, PRINT_PREVIEW_PART)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_root_argument(parser)
    args = parser.parse_args()
    try:
        made = make_cover(args.root, args.edition)
    except (PrintError, EditionError, ColourError, PdfProgramError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if made is None:
        print(f"{args.edition}: no separate cover (no [print.cover] table)")
    for path in made or ():
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
