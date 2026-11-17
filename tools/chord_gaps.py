#!/usr/bin/env python3
"""Check that no two chords on the same line overlap and that no chord runs into the margin.

Every build writes the position of each chord to <job>.chords (\\chord does it, see
zpevnik.sty): one line "x y page width edge" in sp per chord, in document order, where edge
is the right edge of the text block. Two consecutive chords with the same y on the same page
stand on one line; they overlap when the second starts before the first one ends. A chord
whose right end is past the edge runs into the margin, towards the edge of the paper.

Book mode (default, run after compiling an edition, the full book by default): any
overlap or chord in the margin is an error (exit 1).

    python3 tools/chord_gaps.py [--edition NAME] [repo-root]

Trace mode: print every overlapping pair and chord in the margin of one trace file, exit 1
if there is any.

    python3 tools/chord_gaps.py --trace FILE.chords

Python >= 3.11, standard library only.
"""
import argparse
import sys
from pathlib import Path
from typing import NamedTuple

from check_pages import song_name, song_of_page
from formats import SCREEN, add_format_argument
from paths import CHORD_TRACE_NAME, add_edition_argument, add_root_argument, edition_output_dir
from positions import SP_PER_PT, past


class Chord(NamedTuple):
    x: int
    y: int
    page: int
    width: int
    edge: int  # the right edge of the text block

    def past_edge(self) -> float:
        """How far the chord runs past the right edge of the text, in pt (negative: inside)."""
        return (self.x + self.width - self.edge) / SP_PER_PT


class Overhang(NamedTuple):
    """A chord that runs past the right edge of the text by `amount` pt."""
    page: int
    amount: float


class Pair(NamedTuple):
    """Two neighbouring chords on one line: the space between them, in pt (negative: overlap)."""
    page: int
    gap: float


def read_trace(path: Path) -> list[Chord]:
    return [Chord(*map(int, line.split())) for line in path.read_text().splitlines()]


def same_line_pairs(chords: list[Chord]) -> list[Pair]:
    return [
        Pair(second.page, (second.x - first.x - first.width) / SP_PER_PT)
        for first, second in zip(chords, chords[1:])
        if (first.y, first.page) == (second.y, second.page)
    ]


def overlapping(pairs: list[Pair]) -> list[Pair]:
    return sorted(pair for pair in pairs if pair.gap < 0)


def in_margin(chords: list[Chord]) -> list[Overhang]:
    return sorted(Overhang(c.page, c.past_edge()) for c in chords if past(c.x + c.width, c.edge))


def check_book(root: Path, edition: str, format_name: str = SCREEN) -> int:
    output_dir = root / edition_output_dir(edition, format_name)
    chords = read_trace(output_dir / CHORD_TRACE_NAME)
    pairs = same_line_pairs(chords)
    overlaps = overlapping(pairs)
    overhangs = in_margin(chords)
    song_at = song_of_page(output_dir)
    print(f"{len(chords)} chords, {len(pairs)} pairs on the same line, {len(overlaps)} overlapping, "
          f"{len(overhangs)} in the margin")
    for pair in overlaps:
        print(f"ERROR: {song_name(song_at, pair.page)}: chords overlap by {-pair.gap:.2f} pt "
              f"on p. {pair.page}")
    for overhang in overhangs:
        print(f"ERROR: {song_name(song_at, overhang.page)}: a chord runs {overhang.amount:.2f} pt "
              f"into the margin on p. {overhang.page}")
    return 1 if overlaps or overhangs else 0


def check_trace(trace: Path) -> int:
    chords = read_trace(trace)
    overlaps = overlapping(same_line_pairs(chords))
    overhangs = in_margin(chords)
    for pair in overlaps:
        print(f"p. {pair.page}: overlap {-pair.gap:.2f} pt")
    for overhang in overhangs:
        print(f"p. {overhang.page}: a chord {overhang.amount:.2f} pt in the margin")
    return 1 if overlaps or overhangs else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_format_argument(parser)
    add_root_argument(parser)
    parser.add_argument("--trace", type=Path, metavar="FILE",
                        help="check this trace file instead of the book")
    args = parser.parse_args()
    return check_trace(args.trace) if args.trace else check_book(args.root, args.edition, args.format)


if __name__ == "__main__":
    sys.exit(main())
