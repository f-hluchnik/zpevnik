#!/usr/bin/env python3
"""Export the score images from MuseScore, so that every score places itself in the book.

For each scores/<name>.mscz this writes into build/scores/:
  <name>.svg  the image for the web: transparent, chord names in the songbook's
              chord colour;
  <name>.pdf  the same image for pdfLaTeX, which cannot include SVG;
  <name>.tex  where the staff is in the image, for \\score in zpevnik.sty;
and with --format print-black (a format in one ink, formats.py) also
  <name>-black.pdf  the image in black ink only: the SVG with black chord names, in
              shades of grey. rsvg-convert writes RGB (cairo), which a printer separates
              into four inks, so Ghostscript converts it (D-188).

Every score is exported with the shared style scores/zpevnik.mss, which overrides
the style saved in the file: all scores get the same staff size, fonts and system
width. MuseScore trims the SVG to its ink (-T 0); the tool reads the left end and
the middle of the first staff from the staff lines, which MuseScore marks with
class="StaffLines". \\score uses them to put the staff at the start of the text
column and the block label level with the middle of the staff, so no song needs
hand-tuned offsets. A score must be a single page.

Usage: python3 tools/scores.py [--format NAME] [repo-root] [--force]
Exports only scores whose image is older than the .mscz, the shared style, the
chord colour or this tool, unless --force; a black-ink image is made again when it
is older than its SVG.

Needs MuseScore 4 (the MSCORE environment variable or on the PATH; on a Linux
machine without a display, run under xvfb-run) and rsvg-convert (librsvg); the
black-ink images also Ghostscript.
Python >= 3.11, standard library only.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pdf_programs
from formats import BLACK_SCORE_SUFFIX, add_format_argument, is_black_ink
from paths import SCORE_OUTPUT_DIR, SCORE_STYLE, SCORES_DIR, STYLE_FILE, add_root_argument
from pdf_programs import PdfProgramError, convert_to_grey

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
STAFF_LINE_CLASS = "StaffLines"
CHORD_NAME_CLASS = "Harmony"
# MuseScore paints the page white before anything else, with an element of empty class
# (there is no export option for a transparent page). The image must be transparent so
# that it works on a dark web page too.
PAGE_BACKGROUND_CLASS = ""
PAGE_BACKGROUND_FILL = "#ffffff"
POINTS_PER_INCH = 72.0
MILLIMETRES_PER_INCH = 25.4
# Lines of one staff are evenly spaced; the next staff starts after a different gap.
STAFF_SPACING_TOLERANCE = 0.01
# The book's staves have 5 lines (notation) or 4 to 6 (tab). Fewer evenly spaced lines at
# the top mean the first staff was not found, which must fail rather than misplace a score.
MIN_STAFF_LINES = 4

BLACK_INK_CHORD_COLOUR = "#000000"
CHORD_COLOUR = re.compile(r"\\definecolor\{chordred\}\{RGB\}\{\s*(\d+),\s*(\d+),\s*(\d+)\s*\}")
PRINTABLE_WIDTH = re.compile(r"<pagePrintableWidth>([\d.]+)</pagePrintableWidth>")
SVG_LENGTH_MM = re.compile(r"([\d.]+)mm")
# What MuseScore writes before the drawing.
SVG_METADATA_TAGS = frozenset(f"{{{SVG_NAMESPACE}}}{name}" for name in ("title", "desc"))

# MuseScore prints these warnings on every start, however the run ends; left in, they fill
# the end of the output and hide the message that says why an export failed.
MSCORE_STARTUP_NOISE = "qt.qml.typeregistration"
FAILURE_LINES = 5

# MuseScore's converter exits with its error code (src/converter/convertercodes.h) modulo
# 256, and for a score it cannot open it prints no reason (checked with 4.6.5). So the
# message of a known code says what it means instead of quoting the output.
EXIT_STATUS_RANGE = 256
MSCORE_CONVERSION_FAILED = 1303 % EXIT_STATUS_RANGE
MSCORE_SCORE_NOT_LOADED = 1320 % EXIT_STATUS_RANGE
MSCORE_OUTPUT_NOT_OPENED = 1330 % EXIT_STATUS_RANGE
MSCORE_OUTPUT_NOT_WRITTEN = 1331 % EXIT_STATUS_RANGE
MSCORE_EXIT_REASONS = {
    MSCORE_CONVERSION_FAILED: "the conversion failed",
    MSCORE_SCORE_NOT_LOADED: "MuseScore could not open the score",
    MSCORE_OUTPUT_NOT_OPENED: "the output file could not be opened",
    MSCORE_OUTPUT_NOT_WRITTEN: "the output file could not be written",
}
NEWER_VERSION_HINT = ("MuseScore cannot open a score saved by a newer version than itself "
                      "(the CI's version: MUSESCORE_URL in the workflow)")
SCORE_FILE_SUFFIX = ".mscx"
PROGRAM_VERSION = re.compile(r"<programVersion>([^<]+)</programVersion>")

MSCORE_ENVIRONMENT_VARIABLE = "MSCORE"
MSCORE_COMMANDS = ("mscore4portable", "mscore", "mscore4", "musescore")
MSCORE_MACOS_APPS = (Path("/Applications/MuseScore 4.app/Contents/MacOS/mscore"),
                     Path("/Applications/MuseScore Studio 4.app/Contents/MacOS/mscore"))
RSVG_CONVERT = "rsvg-convert"
# A fixed creation date (cairo reads it from SOURCE_DATE_EPOCH) makes the PDF the
# same bytes on every export.
REPRODUCIBLE_DATE = {"SOURCE_DATE_EPOCH": "0"}
# What a black-ink image is made from, besides its SVG: the code that makes it.
BLACK_INK_DEPENDENCIES = (Path(__file__), Path(pdf_programs.__file__))


# Written SVGs keep MuseScore's plain <svg> and xlink: prefixes instead of ns0:.
ElementTree.register_namespace("", SVG_NAMESPACE)
ElementTree.register_namespace("xlink", XLINK_NAMESPACE)


class ScoreError(Exception):
    """A score cannot be exported or placed; the message says which and why."""


class CommandError(ScoreError):
    """A program the export runs failed; returncode is its exit status."""

    def __init__(self, message: str, returncode: int):
        super().__init__(message)
        self.returncode = returncode


@dataclass(frozen=True)
class StaffLine:
    """One line of a staff in SVG units: where it starts and how far down it is."""
    left: float
    y: float


@dataclass(frozen=True)
class SvgFrame:
    """MuseScore gives the size of the image in mm and draws in its own units (the viewBox)."""
    origin_x: float
    origin_y: float
    points_per_unit: float

    def x_points(self, x: float) -> float:
        return (x - self.origin_x) * self.points_per_unit

    def y_points(self, y: float) -> float:
        return (y - self.origin_y) * self.points_per_unit


@dataclass(frozen=True)
class StaffPosition:
    """Where the first staff of a score is, in pt from the top-left corner of its image."""
    left: float
    middle: float


def chord_colour(style_text: str) -> str:
    """The chord colour of zpevnik.sty as an SVG colour (#rrggbb)."""
    match = CHORD_COLOUR.search(style_text)
    if not match:
        raise ScoreError(f"no \\definecolor{{chordred}}{{RGB}}{{...}} in {STYLE_FILE}")
    return "#" + "".join(f"{int(channel):02X}" for channel in match.groups())


def system_width_pt(mss_text: str) -> float:
    """The width of a full system: the printable width of the shared MuseScore style."""
    match = PRINTABLE_WIDTH.search(mss_text)
    if not match:
        raise ScoreError(f"no <pagePrintableWidth> in {SCORE_STYLE}")
    return float(match.group(1)) * POINTS_PER_INCH


def svg_frame(svg: ElementTree.Element) -> SvgFrame:
    width = SVG_LENGTH_MM.fullmatch(svg.get("width", ""))
    view_box = svg.get("viewBox", "").split()
    if not width or len(view_box) != 4:
        raise ScoreError("the SVG has no width in mm or no viewBox")
    origin_x, origin_y, view_width, _ = map(float, view_box)
    width_points = float(width.group(1)) / MILLIMETRES_PER_INCH * POINTS_PER_INCH
    return SvgFrame(origin_x, origin_y, width_points / view_width)


def polyline_points(element: ElementTree.Element) -> list[tuple[float, float]]:
    """The points of a polyline: "x1,y1 x2,y2 ..." in SVG units."""
    pairs = (pair.split(",") for pair in element.get("points", "").split())
    try:
        return [(float(x), float(y)) for x, y in pairs]
    except ValueError as error:
        raise ScoreError(f"a staff line has malformed points: {element.get('points')!r}") from error


def staff_lines(svg: ElementTree.Element) -> list[StaffLine]:
    """Every staff line, top to bottom. MuseScore draws each line of a system as a horizontal
    polyline of class StaffLines; segments at the same height count as one line."""
    left_by_height: dict[float, float] = {}
    for element in svg.iter():
        if element.get("class") != STAFF_LINE_CLASS:
            continue
        points = polyline_points(element)
        if not points:
            raise ScoreError("a staff line has no points")
        y = points[0][1]
        left = min(x for x, _ in points)
        left_by_height[y] = min(left, left_by_height.get(y, left))
    return [StaffLine(left, y) for y, left in sorted(left_by_height.items())]


def first_staff(lines: list[StaffLine]) -> list[StaffLine]:
    """The top run of evenly spaced lines: the first staff of the first system."""
    if len(lines) < MIN_STAFF_LINES:
        raise ScoreError(f"the SVG has {len(lines)} staff lines, a staff has at least {MIN_STAFF_LINES}")
    spacing = lines[1].y - lines[0].y
    staff = lines[:2]
    for line in lines[2:]:
        if abs(line.y - staff[-1].y - spacing) > STAFF_SPACING_TOLERANCE * spacing:
            break
        staff.append(line)
    if len(staff) < MIN_STAFF_LINES:
        raise ScoreError(f"the first staff has {len(staff)} evenly spaced lines, "
                         f"expected at least {MIN_STAFF_LINES}")
    return staff


def staff_position(svg: ElementTree.Element) -> StaffPosition:
    frame = svg_frame(svg)
    staff = first_staff(staff_lines(svg))
    return StaffPosition(left=frame.x_points(min(line.left for line in staff)),
                         middle=frame.y_points((staff[0].y + staff[-1].y) / 2))


def is_page_background(element: ElementTree.Element) -> bool:
    return (element.get("class") == PAGE_BACKGROUND_CLASS
            and element.get("fill", "").lower() == PAGE_BACKGROUND_FILL)


def remove_page_background(svg: ElementTree.Element) -> None:
    """Remove the white page MuseScore paints first, so that the image is transparent."""
    drawn = [element for element in svg if element.tag not in SVG_METADATA_TAGS]
    if drawn and is_page_background(drawn[0]):
        svg.remove(drawn[0])


def paint_chord_names(svg: ElementTree.Element, colour: str) -> None:
    for element in svg.iter():
        if element.get("class") == CHORD_NAME_CLASS:
            element.set("fill", colour)


def placement_tex(position: StaffPosition, system_width: float) -> str:
    """The generated file \\score reads: \\zpscoregeometry{staff left}{staff middle}{system width}."""
    return (f"\\zpscoregeometry{{{position.left:.2f}pt}}{{{position.middle:.2f}pt}}"
            f"{{{system_width:.2f}pt}}\n")


def find_mscore() -> str:
    """The MSCORE environment variable, a MuseScore command on the PATH, or the macOS app."""
    candidates = [os.environ.get(MSCORE_ENVIRONMENT_VARIABLE),
                  *(shutil.which(command) for command in MSCORE_COMMANDS),
                  *(str(app) for app in MSCORE_MACOS_APPS if app.exists())]
    for candidate in candidates:
        if candidate:
            return candidate
    raise ScoreError(f"MuseScore 4 not found: install it or set {MSCORE_ENVIRONMENT_VARIABLE} "
                     "to its executable (README, Nastavení lokální kopie)")


def failure_details(output: str) -> str:
    """The last lines of what a failed program printed, without MuseScore's start-up warnings."""
    lines = [line.strip() for line in output.splitlines()
             if line.strip() and MSCORE_STARTUP_NOISE not in line]
    return " | ".join(lines[-FAILURE_LINES:]) or "no other output"


def run(command: list[str], what: str, extra_environment: dict[str, str] | None = None) -> None:
    environment = {**os.environ, **(extra_environment or {})}
    try:
        result = subprocess.run(command, capture_output=True, text=True, env=environment)
    except FileNotFoundError as error:
        raise ScoreError(f"{what}: {command[0]} not found (README, Nastavení lokální kopie)") from error
    if result.returncode != 0:
        details = failure_details(result.stderr + result.stdout)
        raise CommandError(f"{what} failed ({result.returncode}) with {command[0]}: {details}",
                           result.returncode)


def saved_by(score: Path) -> str | None:
    """The MuseScore version that saved a .mscz (a zip with the score's .mscx at its top level)."""
    try:
        with zipfile.ZipFile(score) as archive:
            name = next(name for name in archive.namelist()
                        if name.endswith(SCORE_FILE_SUFFIX) and "/" not in name)
            match = PROGRAM_VERSION.search(archive.read(name).decode("utf-8", errors="replace"))
    except (OSError, zipfile.BadZipFile, StopIteration):
        return None
    return match.group(1) if match else None


def mscore_reason(score: Path, returncode: int) -> str | None:
    """What MuseScore's exit status means for this score, or None for an unknown status."""
    reason = MSCORE_EXIT_REASONS.get(returncode)
    if returncode == MSCORE_SCORE_NOT_LOADED and (version := saved_by(score)):
        return f"{reason}, saved by MuseScore {version}; {NEWER_VERSION_HINT}"
    return reason


def export_svg(mscore: str, score: Path, style: Path, work_dir: Path) -> Path:
    """Trimmed SVG of a one-page score; MuseScore names the pages <name>-<page>.svg."""
    what = f"MuseScore export of {score.name}"
    try:
        run([mscore, "-S", str(style), "-T", "0", "-o", str(work_dir / f"{score.stem}.svg"), str(score)],
            what)
    except CommandError as error:
        reason = mscore_reason(score, error.returncode)
        if reason is None:
            raise
        raise ScoreError(f"{what} failed ({error.returncode}): {reason}") from error
    pages = sorted(work_dir.glob(f"{score.stem}-*.svg"))
    if len(pages) != 1:
        raise ScoreError(f"{score.name}: {len(pages)} pages; a score must be a single page")
    return pages[0]


def export_score(score: Path, root: Path, mscore: str, colour: str, system_width: float) -> None:
    output_dir = root / SCORE_OUTPUT_DIR
    with tempfile.TemporaryDirectory() as work_dir:
        page = export_svg(mscore, score, root / SCORE_STYLE, Path(work_dir))
        tree = ElementTree.parse(page)
    svg = tree.getroot()
    try:
        position = staff_position(svg)
    except ScoreError as error:
        raise ScoreError(f"{score.name}: {error}") from error
    remove_page_background(svg)
    paint_chord_names(svg, colour)
    svg_file = output_dir / f"{score.stem}.svg"
    tree.write(svg_file, encoding="UTF-8", xml_declaration=True)
    svg_to_pdf(svg_file, svg_file.with_suffix(".pdf"))
    svg_file.with_suffix(".tex").write_text(placement_tex(position, system_width), encoding="utf-8")


def svg_to_pdf(svg_file: Path, pdf_file: Path) -> None:
    run([RSVG_CONVERT, "-f", "pdf", "-o", str(pdf_file), str(svg_file)],
        f"PDF conversion of {svg_file.name}", REPRODUCIBLE_DATE)


def black_ink_pdf(svg_file: Path) -> Path:
    """The black-ink image of an exported score, next to its SVG (\\zpscoresuffix in zpevnik.sty)."""
    return svg_file.with_name(f"{svg_file.stem}{BLACK_SCORE_SUFFIX}.pdf")


def export_black_ink_pdf(svg_file: Path) -> None:
    """The image of an exported score in black ink only: its SVG with black chord names,
    as a PDF in shades of grey."""
    tree = ElementTree.parse(svg_file)
    paint_chord_names(tree.getroot(), BLACK_INK_CHORD_COLOUR)
    with tempfile.TemporaryDirectory() as work_dir:
        black_svg = Path(work_dir) / svg_file.name
        tree.write(black_svg, encoding="UTF-8", xml_declaration=True)
        rgb_pdf = black_svg.with_suffix(".pdf")
        svg_to_pdf(black_svg, rgb_pdf)
        try:
            convert_to_grey(rgb_pdf, black_ink_pdf(svg_file))
        except PdfProgramError as error:
            raise ScoreError(f"black-ink image of {svg_file.name}: {error}") from error


def outputs(score: Path, root: Path) -> list[Path]:
    base = root / SCORE_OUTPUT_DIR / score.stem
    return [base.with_suffix(suffix) for suffix in (".svg", ".pdf", ".tex")]


def newer_than(files: list[Path], inputs: list[Path]) -> bool:
    """Every file exists and none is older than the newest input."""
    if not all(file.exists() for file in files):
        return False
    newest_input = max(path.stat().st_mtime for path in inputs)
    return min(file.stat().st_mtime for file in files) >= newest_input


def is_up_to_date(score: Path, root: Path, dependencies: list[Path]) -> bool:
    return newer_than(outputs(score, root), [score, *dependencies])


def black_ink_pdf_is_up_to_date(svg_file: Path) -> bool:
    return newer_than([black_ink_pdf(svg_file)], [svg_file, *BLACK_INK_DEPENDENCIES])


def export_scores(scores: list[Path], root: Path) -> None:
    """Export the scores with the settings every export shares; ScoreError on the first failure."""
    mscore = find_mscore()
    colour = chord_colour((root / STYLE_FILE).read_text(encoding="utf-8"))
    width = system_width_pt((root / SCORE_STYLE).read_text(encoding="utf-8"))
    (root / SCORE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    for score in scores:
        export_score(score, root, mscore, colour, width)


def export_black_ink_pdfs(scores: list[Path], root: Path, force: bool) -> int:
    """Make the black-ink images that are missing or older than their SVG; how many were made."""
    svg_files = [root / SCORE_OUTPUT_DIR / f"{score.stem}.svg" for score in scores]
    pending = [svg for svg in svg_files if force or not black_ink_pdf_is_up_to_date(svg)]
    for svg_file in pending:
        export_black_ink_pdf(svg_file)
    return len(pending)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_format_argument(parser)
    add_root_argument(parser)
    parser.add_argument("--force", action="store_true", help="export every score, even if up to date")
    args = parser.parse_args()
    root = args.root
    dependencies = [root / SCORE_STYLE, root / STYLE_FILE, Path(__file__)]
    scores = sorted((root / SCORES_DIR).glob("*.mscz"))
    pending = [score for score in scores if args.force or not is_up_to_date(score, root, dependencies)]
    try:
        if pending:
            export_scores(pending, root)
        black_ink = export_black_ink_pdfs(scores, root, args.force) if is_black_ink(args.format) else None
    except ScoreError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    report = f"{SCORE_OUTPUT_DIR}: {len(pending)} exported, {len(scores) - len(pending)} up to date"
    print(report + (f", {black_ink} black-ink images made" if black_ink is not None else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
