#!/usr/bin/env python3
"""Check that no two chords on the same line overlap (tickets C3a and C4, D-123).

Every build writes the position of each chord to <job>.chords (\\chord does it, see
zpevnik.sty): one line "x y page width" in sp per chord, in document order. Two
consecutive chords with the same y on the same page stand on one line; they overlap when
the second starts before the first one ends.

Book mode (default, run after compiling zpevnik.tex): any overlap in the book is an
error (exit 1).

    python3 tools/chord_gaps.py [repo-root]

Trace mode: print every overlapping pair of one trace file, exit 1 if there is any.

    python3 tools/chord_gaps.py --trace FILE.chords

Python >= 3.11, standard library only.
"""
import sys
from pathlib import Path
from typing import NamedTuple

from check_pages import song_pages

SP_PER_PT = 65536
TRACE_NAME = "zpevnik.chords"


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


def song_of_page(root: Path) -> dict[int, str]:
    songs, _errors = song_pages(root)
    return {page: song for song, first, count in songs for page in range(first, first + count)}


def check_book(root: Path) -> int:
    chords = read_trace(root / TRACE_NAME)
    pairs = same_line_pairs(chords)
    overlaps = overlapping(pairs)
    song_at = song_of_page(root)
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
    args = sys.argv[1:]
    if "--trace" in args:
        return check_trace(Path(args[args.index("--trace") + 1]))
    return check_book(Path(args[0] if args else ".").resolve())


if __name__ == "__main__":
    sys.exit(main())
