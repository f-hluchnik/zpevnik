#!/usr/bin/env python3
"""Export the score images from MuseScore, so that every score places itself in the book.

For each scores/<name>.mscz this writes into build/scores/:
  <name>.svg  the image for the web: transparent, chord names in the songbook's
              chord colour;
  <name>.pdf  the same image for pdfLaTeX, which cannot include SVG;
  <name>.tex  where the staff is in the image, for \\score in zpevnik.sty.

Every score is exported with the shared style scores/zpevnik.mss, which overrides
the style saved in the file: all scores get the same staff size, fonts and system
width. MuseScore trims the SVG to its ink (-T 0); the tool reads the left end and
the middle of the first staff from the staff lines, which MuseScore marks with
class="StaffLines". \\score uses them to put the staff at the start of the text
column and the block label level with the middle of the staff, so no song needs
hand-tuned offsets. A score must be a single page.

Usage: python3 tools/scores.py [repo-root] [--force]
Exports only scores whose image is older than the .mscz, the shared style, the
chord colour or this tool, unless --force.

Needs MuseScore 4 (the MSCORE environment variable or on the PATH; on a Linux
machine without a display, run under xvfb-run) and rsvg-convert (librsvg).
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
from dataclasses import dataclass
from pathlib import Path

from paths import SCORE_OUTPUT_DIR, SCORE_STYLE, SCORES_DIR, STYLE_FILE, add_root_argument

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

CHORD_COLOUR = re.compile(r"\\definecolor\{chordred\}\{RGB\}\{\s*(\d+),\s*(\d+),\s*(\d+)\s*\}")
PRINTABLE_WIDTH = re.compile(r"<pagePrintableWidth>([\d.]+)</pagePrintableWidth>")
SVG_LENGTH_MM = re.compile(r"([\d.]+)mm")
# What MuseScore writes before the drawing.
SVG_METADATA_TAGS = frozenset(f"{{{SVG_NAMESPACE}}}{name}" for name in ("title", "desc"))

MSCORE_ENVIRONMENT_VARIABLE = "MSCORE"
MSCORE_COMMANDS = ("mscore4portable", "mscore", "mscore4", "musescore")
MSCORE_MACOS_APPS = (Path("/Applications/MuseScore 4.app/Contents/MacOS/mscore"),
                     Path("/Applications/MuseScore Studio 4.app/Contents/MacOS/mscore"))
RSVG_CONVERT = "rsvg-convert"
# A fixed creation date (cairo reads it from SOURCE_DATE_EPOCH) makes the PDF the
# same bytes on every export.
REPRODUCIBLE_DATE = {"SOURCE_DATE_EPOCH": "0"}


# Written SVGs keep MuseScore's plain <svg> and xlink: prefixes instead of ns0:.
ElementTree.register_namespace("", SVG_NAMESPACE)
ElementTree.register_namespace("xlink", XLINK_NAMESPACE)


class ScoreError(Exception):
    """A score cannot be exported or placed; the message says which and why."""


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
                     "to its executable (README, section Noty)")


def run(command: list[str], what: str, extra_environment: dict[str, str] | None = None) -> None:
    environment = {**os.environ, **(extra_environment or {})}
    try:
        result = subprocess.run(command, capture_output=True, text=True, env=environment)
    except FileNotFoundError as error:
        raise ScoreError(f"{what}: {command[0]} not found (README, section Noty)") from error
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip().splitlines()[-5:]
        raise ScoreError(f"{what} failed ({result.returncode}): " + " | ".join(output))


def export_svg(mscore: str, score: Path, style: Path, work_dir: Path) -> Path:
    """Trimmed SVG of a one-page score; MuseScore names the pages <name>-<page>.svg."""
    run([mscore, "-S", str(style), "-T", "0", "-o", str(work_dir / f"{score.stem}.svg"), str(score)],
        f"MuseScore export of {score.name}")
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
    run([RSVG_CONVERT, "-f", "pdf", "-o", str(svg_file.with_suffix(".pdf")), str(svg_file)],
        f"PDF conversion of {svg_file.name}", REPRODUCIBLE_DATE)
    svg_file.with_suffix(".tex").write_text(placement_tex(position, system_width), encoding="utf-8")


def outputs(score: Path, root: Path) -> list[Path]:
    base = root / SCORE_OUTPUT_DIR / score.stem
    return [base.with_suffix(suffix) for suffix in (".svg", ".pdf", ".tex")]


def is_up_to_date(score: Path, root: Path, dependencies: list[Path]) -> bool:
    files = outputs(score, root)
    if not all(file.exists() for file in files):
        return False
    newest_input = max(path.stat().st_mtime for path in [score, *dependencies])
    return min(file.stat().st_mtime for file in files) >= newest_input


def export_scores(scores: list[Path], root: Path) -> None:
    """Export the scores with the settings every export shares; ScoreError on the first failure."""
    mscore = find_mscore()
    colour = chord_colour((root / STYLE_FILE).read_text(encoding="utf-8"))
    width = system_width_pt((root / SCORE_STYLE).read_text(encoding="utf-8"))
    (root / SCORE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    for score in scores:
        export_score(score, root, mscore, colour, width)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_root_argument(parser)
    parser.add_argument("--force", action="store_true", help="export every score, even if up to date")
    args = parser.parse_args()
    root = args.root
    dependencies = [root / SCORE_STYLE, root / STYLE_FILE, Path(__file__)]
    scores = sorted((root / SCORES_DIR).glob("*.mscz"))
    pending = [score for score in scores if args.force or not is_up_to_date(score, root, dependencies)]
    if pending:
        try:
            export_scores(pending, root)
        except ScoreError as error:
            print(f"error: {error}", file=sys.stderr)
            return 1
    print(f"{SCORE_OUTPUT_DIR}: {len(pending)} exported, {len(scores) - len(pending)} up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
