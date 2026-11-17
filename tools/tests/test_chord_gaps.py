"""Unit tests for the chord-overlap check.

Run from the repository root: python3 -m unittest discover -s tools
"""
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from chord_gaps import (Chord, Overhang, Pair, check_book, check_trace, in_margin, overlapping,
                        read_trace, same_line_pairs)
from paths import CHORD_TRACE_NAME, DEFAULT_EDITION, edition_output_dir
from positions import SP_PER_PT
from .test_check_pages import write_compiled_book


EDGE = 500  # pt: the right edge of the text block in these tests


def pt(points: float) -> int:
    return round(points * SP_PER_PT)


def chord(x: float, y: int, page: int, width: float) -> Chord:
    """A chord at x pt, width pt wide, in a text block whose right edge is EDGE."""
    return Chord(pt(x), y, page, pt(width), pt(EDGE))


def trace_text(chords: list[Chord]) -> str:
    return "".join(" ".join(map(str, c)) + "\n" for c in chords)


class Pairs(unittest.TestCase):
    def test_the_gap_is_the_distance_minus_the_first_width(self):
        chords = [chord(10, 5, 1, 8), chord(30, 5, 1, 8)]
        self.assertEqual(same_line_pairs(chords), [Pair(1, 12.0)])

    def test_chords_on_different_lines_or_pages_are_not_a_pair(self):
        chords = [chord(0, 5, 1, 0), chord(30, 6, 1, 0), chord(40, 6, 2, 0)]
        self.assertEqual(same_line_pairs(chords), [])

    def test_only_negative_gaps_overlap(self):
        pairs = [Pair(1, 3.0), Pair(2, -1.5), Pair(3, 0.0)]
        self.assertEqual(overlapping(pairs), [Pair(2, -1.5)])


class Margin(unittest.TestCase):
    def test_a_chord_that_ends_past_the_edge_is_in_the_margin(self):
        chords = [chord(EDGE - 10, 5, 1, 12), chord(EDGE - 10, 6, 2, 10), chord(10, 7, 3, 8)]
        self.assertEqual(in_margin(chords), [Overhang(1, 2.0)])

    def test_the_trace_mode_fails_on_a_chord_in_the_margin(self):
        with TemporaryDirectory() as tmp:
            trace = Path(tmp) / CHORD_TRACE_NAME
            trace.write_text(trace_text([chord(EDGE - 4, 5, 1, 8)]))
            with redirect_stdout(io.StringIO()) as report:
                status = check_trace(trace)
        self.assertEqual(status, 1)
        self.assertIn("p. 1: a chord 4.00 pt in the margin", report.getvalue())


class Book(unittest.TestCase):
    """A two-song full book (`one` on page 2, `two` on page 3); the trace has an overlap on
    `overlap_page` and a chord in the margin on `margin_page`."""

    def build(self, root: Path, overlap_page: int | None, margin_page: int | None = None) -> None:
        output_dir = root / edition_output_dir(DEFAULT_EDITION)
        output_dir.mkdir(parents=True)
        write_compiled_book(output_dir, [("shared-pages/cover", 2), ("songs/one", 3), ("songs/two", 4)])
        rows = [chord(0, 5, 2, 8), chord(20, 5, 2, 8)]  # no overlap
        if overlap_page is not None:
            rows += [chord(0, 5, overlap_page, 8), chord(4, 5, overlap_page, 8)]
        if margin_page is not None:
            rows.append(chord(EDGE - 5, 9, margin_page, 8))
        (output_dir / CHORD_TRACE_NAME).write_text(trace_text(rows))

    def check(self, root: Path) -> tuple[int, str]:
        """The exit status and the report of the book check; the report is captured, not printed."""
        with redirect_stdout(io.StringIO()) as report:
            status = check_book(root, DEFAULT_EDITION)
        return status, report.getvalue()

    def test_an_overlap_in_any_song_fails(self):
        for page, song in ((2, "one"), (3, "two")):
            with self.subTest(page=page), TemporaryDirectory() as tmp:
                self.build(Path(tmp), overlap_page=page)
                status, report = self.check(Path(tmp))
                self.assertEqual(status, 1)
                self.assertIn(f"ERROR: {song}: chords overlap by 4.00 pt on p. {page}", report)

    def test_an_overlap_outside_the_songs_fails(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), overlap_page=1)
            status, report = self.check(Path(tmp))
        self.assertEqual(status, 1)
        self.assertIn("ERROR: outside the songs: chords overlap by 4.00 pt on p. 1", report)

    def test_a_chord_in_the_margin_fails(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), overlap_page=None, margin_page=3)
            status, report = self.check(Path(tmp))
        self.assertEqual(status, 1)
        self.assertIn("ERROR: two: a chord runs 3.00 pt into the margin on p. 3", report)

    def test_a_book_without_overlaps_passes(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), overlap_page=None)
            status, report = self.check(Path(tmp))
        self.assertEqual(status, 0)
        self.assertNotIn("ERROR", report)

    def test_the_trace_is_read_in_order(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), overlap_page=2)
            trace = Path(tmp) / edition_output_dir(DEFAULT_EDITION) / CHORD_TRACE_NAME
            self.assertEqual(len(read_trace(trace)), 4)
