#!/usr/bin/env python3
"""Check that no two chords on the same line overlap.

Every build writes the position of each chord to <job>.chords (\\chord does it, see
zpevnik.sty): one line "x y page width" in sp per chord, in document order. Two
consecutive chords with the same y on the same page stand on one line; they overlap when
the second starts before the first one ends.

Book mode (default, run after compiling the full book): any overlap in the book is an
error (exit 1). Only the full book is checked: the spacing depends on the page format,
not on which songs an edition selects.

    python3 tools/chord_gaps.py [repo-root]

Trace mode: print every overlapping pair of one trace file, exit 1 if there is any.

    python3 tools/chord_gaps.py --trace FILE.chords

Python >= 3.11, standard library only.
"""
import argparse
import sys
from pathlib import Path
from typing import NamedTuple

from check_pages import song_pages
from paths import CHORD_TRACE_NAME, DEFAULT_EDITION, add_root_argument, edition_output_dir

SP_PER_PT = 65536


class Chord(NamedTuple):
    x: int
    y: int
    page: int
    width: int


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


def song_of_page(output_dir: Path) -> dict[int, str]:
    songs, _errors = song_pages(output_dir)
    return {page: song for song, first, count in songs for page in range(first, first + count)}


def check_book(root: Path) -> int:
    output_dir = root / edition_output_dir(DEFAULT_EDITION)
    chords = read_trace(output_dir / CHORD_TRACE_NAME)
    pairs = same_line_pairs(chords)
    overlaps = overlapping(pairs)
    song_at = song_of_page(output_dir)
    print(f"{len(chords)} chords, {len(pairs)} pairs on the same line, {len(overlaps)} overlapping")
    for pair in overlaps:
        song = song_at.get(pair.page) or "outside the songs"
        print(f"ERROR: {song}: chords overlap by {-pair.gap:.2f} pt on p. {pair.page}")
    return 1 if overlaps else 0


def check_trace(trace: Path) -> int:
    overlaps = overlapping(same_line_pairs(read_trace(trace)))
    for pair in overlaps:
        print(f"p. {pair.page}: overlap {-pair.gap:.2f} pt")
    return 1 if overlaps else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_root_argument(parser)
    parser.add_argument("--trace", type=Path, metavar="FILE",
                        help="check this trace file instead of the book")
    args = parser.parse_args()
    return check_trace(args.trace) if args.trace else check_book(args.root)


if __name__ == "__main__":
    sys.exit(main())
