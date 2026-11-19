"""What the tools ask of a finished PDF, through poppler and Ghostscript.

- pdfinfo (poppler): the page count and the page boxes of the first page;
- pdftoppm (poppler): a page rendered in shades of grey, to measure where its ink is: letters,
  scores and lines alike, as the printer's margins count them;
- Ghostscript's inkcov device: how much of each ink (cyan, magenta, yellow, black) every page
  takes when printed, to check a print in one ink;
- Ghostscript's pdfwrite device: a copy of a PDF in shades of grey only (DeviceGray), which
  prints in black ink alone.

Every function raises PdfProgramError with a message that says what to install or what failed.
Python >= 3.11, standard library only.
"""
import re
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

PDFINFO = "pdfinfo"
PDFTOPPM = "pdftoppm"
GHOSTSCRIPT = "gs"
INSTALL_HINTS = {PDFINFO: "install poppler", PDFTOPPM: "install poppler", GHOSTSCRIPT: "install Ghostscript"}
SETUP_HINT = "(README, Nastavení lokální kopie)"

PAGES_LINE = re.compile(r"^Pages:\s+(\d+)$", re.M)
NUMBER = r"(-?[\d.]+)"
BOX_LINE = re.compile(rf"^(MediaBox|TrimBox):\s+{NUMBER}\s+{NUMBER}\s+{NUMBER}\s+{NUMBER}$", re.M)
MEDIA_BOX, TRIM_BOX = "MediaBox", "TrimBox"
POINTS_PER_INCH = 72
# A binary greymap as pdftoppm -gray writes it: "P5", width, height, the largest value, then a
# byte per pixel, row after row.
GREYMAP_HEADER = re.compile(rb"P5\s+(\d+)\s+(\d+)\s+(\d+)\s")
WHITE = 255

# inkcov prints one line per page: the share of the page each ink covers, "c m y k CMYK OK".
# Ghostscript's own warnings about the PDF can come between the lines, so only these count.
INK_COVERAGE_LINE = re.compile(r"^\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+CMYK OK\s*$", re.M)
# inkcov counts the pixels of a rendered page: fine enough that a thin coloured line shows.
INK_COVERAGE_DPI = 150
GHOSTSCRIPT_BATCH = [GHOSTSCRIPT, "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE"]
GREY_CONVERSION = ["-sDEVICE=pdfwrite", "-sColorConversionStrategy=Gray", "-dProcessColorModel=/DeviceGray"]


class PdfProgramError(Exception):
    """A PDF program is missing, failed, or printed something unexpected."""


@dataclass(frozen=True)
class Box:
    """A page box in pt, from the bottom-left corner of the page."""
    left: float
    bottom: float
    right: float
    top: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom


@dataclass(frozen=True)
class Greymap:
    """A rendered page: one byte per pixel, 0 black to 255 white, row after row."""
    width: int
    height: int
    pixels: bytes

    def rows(self) -> Iterator[bytes]:
        return (self.pixels[start:start + self.width] for start in range(0, len(self.pixels), self.width))


@dataclass(frozen=True)
class InkColumns:
    """The first and the last column of pixels with any ink: any pixel that is not pure white."""
    first: int
    last: int


@dataclass(frozen=True)
class PageBoxes:
    media: Box
    trim: Box  # the page after the cut; the media box itself if the PDF names no trim box


@dataclass(frozen=True)
class InkCoverage:
    """The share of the page (0 to 1) each ink covers."""
    cyan: float
    magenta: float
    yellow: float
    black: float

    @property
    def is_black_only(self) -> bool:
        return self.cyan == self.magenta == self.yellow == 0


def run_binary(command: list[str]) -> bytes:
    """The standard output of a program; PdfProgramError if it is missing or fails."""
    try:
        result = subprocess.run(command, capture_output=True)
    except FileNotFoundError as error:
        raise PdfProgramError(f"{command[0]} not found: {INSTALL_HINTS[command[0]]} {SETUP_HINT}") from error
    if result.returncode != 0:
        output = result.stderr.strip() or result.stdout.strip()[-500:]
        raise PdfProgramError(f"{command[0]} failed ({result.returncode}) on {command[-1]}: "
                              f"{output.decode(errors='replace')}")
    return result.stdout


def run(command: list[str]) -> str:
    """The standard output of a program that writes text."""
    return run_binary(command).decode(errors="replace")


def page_count(info: str) -> int:
    """The page count from pdfinfo's output."""
    match = PAGES_LINE.search(info)
    if not match:
        raise PdfProgramError(f"{PDFINFO} did not report the number of pages")
    return int(match.group(1))


def page_boxes(info: str) -> PageBoxes:
    """The media and trim box from the output of pdfinfo -box (the first page's)."""
    boxes = {match.group(1): Box(*map(float, match.groups()[1:])) for match in BOX_LINE.finditer(info)}
    if MEDIA_BOX not in boxes or TRIM_BOX not in boxes:
        raise PdfProgramError(f"{PDFINFO} -box did not report the media box and the trim box")
    return PageBoxes(media=boxes[MEDIA_BOX], trim=boxes[TRIM_BOX])


def pdfinfo(pdf: Path) -> str:
    """pdfinfo's report with the page boxes of the first page."""
    return run([PDFINFO, "-box", str(pdf)])


def greymap(data: bytes) -> Greymap:
    """A page as pdftoppm -gray writes it (a binary PGM)."""
    match = GREYMAP_HEADER.match(data)
    if not match or int(match.group(3)) != WHITE:
        raise PdfProgramError(f"{PDFTOPPM} did not write an 8-bit greymap")
    width, height = int(match.group(1)), int(match.group(2))
    pixels = data[match.end():]
    if len(pixels) != width * height:
        raise PdfProgramError(f"{PDFTOPPM} wrote {len(pixels)} pixels for a page of {width} x {height}")
    return Greymap(width, height, pixels)


def ink_columns(page: Greymap) -> InkColumns | None:
    """Where the ink of a rendered page starts and ends across it; None for a blank page.
    A pixel that the edge of a letter covers only in part is not pure white, so it counts as ink."""
    white = bytes([WHITE])
    first, last = page.width, -1
    for row in page.rows():
        blank_start = len(row) - len(row.lstrip(white))
        if blank_start < len(row):
            first, last = min(first, blank_start), max(last, len(row.rstrip(white)) - 1)
    return InkColumns(first, last) if last >= 0 else None


def render_page(pdf: Path, page: int, dpi: int, area: Box, page_height: float) -> Greymap:
    """One page in shades of grey at `dpi`, only the area of it (a box of the page, in pt)."""
    scale = dpi / POINTS_PER_INCH
    crop = {"-x": area.left * scale, "-y": (page_height - area.top) * scale,
            "-W": area.width * scale, "-H": area.height * scale}
    options = [str(part) for option, pixels in crop.items() for part in (option, round(pixels))]
    pages = ["-f", str(page), "-l", str(page)]
    # Without an output name, pdftoppm writes the one page to its standard output.
    return greymap(run_binary([PDFTOPPM, "-gray", "-r", str(dpi), *options, *pages, "-singlefile", str(pdf)]))


def ink_coverages(inkcov_output: str) -> list[InkCoverage]:
    return [InkCoverage(*map(float, match.groups())) for match in INK_COVERAGE_LINE.finditer(inkcov_output)]


def ink_coverage(pdf: Path) -> list[InkCoverage]:
    """The inks each page takes when printed, page by page."""
    return ink_coverages(run([*GHOSTSCRIPT_BATCH, "-sDEVICE=inkcov", f"-r{INK_COVERAGE_DPI}",
                              "-sOutputFile=-", str(pdf)]))


def convert_to_grey(source: Path, target: Path) -> None:
    """Write `source` as a PDF in shades of grey only: it prints in black ink alone."""
    run([*GHOSTSCRIPT_BATCH, *GREY_CONVERSION, f"-sOutputFile={target}", str(source)])
