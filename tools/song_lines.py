#!/usr/bin/env python3
"""Check that every line of a song is one printed line and ends inside the text.

Every build writes the song blocks (verse, chorus, ...) to <job>.lines (\\zp@songblock in
zpevnik.sty, D-183), in sp:
    "block page source printed prose"  per block: its lines in the source, as TeX printed
                                        them, and 1 if it holds a recitative (prose)
    "end page x edge"                   per line end: where the line ends, the right edge
                                        of the text
A block printed in more lines than its source has a line that wrapped; a recitative may
wrap. A line whose end is past the edge runs into the margin. A line that is too long is
squeezed first (its spaces shrink); one that still does not fit is a failure for the
person writing the song to solve in the source.

Book mode (default, run after compiling an edition, the full book by default): any wrapped
line or line in the margin is an error (exit 1).

    python3 tools/song_lines.py [--edition NAME] [--format FORMAT] [repo-root]

Trace mode: print every wrapped block and line in the margin of one trace file, exit 1 if
there is any.

    python3 tools/song_lines.py --trace FILE.lines
"""
import argparse
import sys
from pathlib import Path
from typing import NamedTuple

from check_pages import song_name, song_of_page
from formats import SCREEN, add_format_argument
from paths import LINE_TRACE_NAME, add_edition_argument, add_root_argument, edition_output_dir
from positions import SP_PER_PT, past

BLOCK, LINE_END = "block", "end"


class Block(NamedTuple):
    page: int
    source: int   # lines in the source
    printed: int  # lines as TeX printed them
    prose: bool   # holds a recitative, whose lines may wrap

    def wrapped(self) -> bool:
        return self.printed != self.source and not self.prose


class LineEnd(NamedTuple):
    page: int
    x: int
    edge: int

    def past_edge(self) -> float:
        """How far the line runs past the right edge of the text, in pt (negative: inside)."""
        return (self.x - self.edge) / SP_PER_PT


def read_trace(path: Path) -> tuple[list[Block], list[LineEnd]]:
    blocks, ends = [], []
    for line in path.read_text().splitlines():
        kind, *fields = line.split()
        if kind == BLOCK:
            page, source, printed, prose = map(int, fields)
            blocks.append(Block(page, source, printed, bool(prose)))
        elif kind == LINE_END:
            ends.append(LineEnd(*map(int, fields)))
    return blocks, ends


def wrapped(blocks: list[Block]) -> list[Block]:
    return [block for block in blocks if block.wrapped()]


def in_margin(ends: list[LineEnd]) -> list[LineEnd]:
    return [end for end in ends if past(end.x, end.edge)]


def wrap_message(block: Block) -> str:
    return f"{block.source} line(s) of the source printed as {block.printed} on p. {block.page}"


def margin_message(end: LineEnd) -> str:
    return f"a line runs {end.past_edge():.2f} pt into the margin on p. {end.page}"


def check_book(root: Path, edition: str, format_name: str = SCREEN) -> int:
    output_dir = root / edition_output_dir(edition, format_name)
    blocks, ends = read_trace(output_dir / LINE_TRACE_NAME)
    wraps, overflows = wrapped(blocks), in_margin(ends)
    song_at = song_of_page(output_dir)
    print(f"{len(blocks)} song blocks, {len(ends)} lines, {len(wraps)} wrapped, "
          f"{len(overflows)} in the margin")
    for block in wraps:
        print(f"ERROR: {song_name(song_at, block.page)}: {wrap_message(block)}")
    for end in overflows:
        print(f"ERROR: {song_name(song_at, end.page)}: {margin_message(end)}")
    return 1 if wraps or overflows else 0


def check_trace(trace: Path) -> int:
    blocks, ends = read_trace(trace)
    wraps, overflows = wrapped(blocks), in_margin(ends)
    for message in [wrap_message(b) for b in wraps] + [margin_message(e) for e in overflows]:
        print(message)
    return 1 if wraps or overflows else 0


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
