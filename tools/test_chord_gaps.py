"""Unit tests for the chord-overlap check.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from chord_gaps import SP_PER_PT, Chord, Pair, check_book, overlapping, read_trace, same_line_pairs
from paths import CHORD_TRACE_NAME, DEFAULT_EDITION, edition_output_dir
from test_check_pages import write_compiled_book


def pt(points: float) -> int:
    return round(points * SP_PER_PT)


class Pairs(unittest.TestCase):
    def test_the_gap_is_the_distance_minus_the_first_width(self):
        chords = [Chord(pt(10), 5, 1, pt(8)), Chord(pt(30), 5, 1, pt(8))]
        self.assertEqual(same_line_pairs(chords), [Pair(1, 12.0)])

    def test_chords_on_different_lines_or_pages_are_not_a_pair(self):
        chords = [Chord(0, 5, 1, 0), Chord(pt(30), 6, 1, 0), Chord(pt(40), 6, 2, 0)]
        self.assertEqual(same_line_pairs(chords), [])

    def test_only_negative_gaps_overlap(self):
        pairs = [Pair(1, 3.0), Pair(2, -1.5), Pair(3, 0.0)]
        self.assertEqual(overlapping(pairs), [Pair(2, -1.5)])


class Book(unittest.TestCase):
    """A two-song full book (`one` on page 2, `two` on page 3); the trace has an overlap on `page`."""

    def build(self, root: Path, overlap_page: int | None) -> None:
        output_dir = root / edition_output_dir(DEFAULT_EDITION)
        output_dir.mkdir(parents=True)
        write_compiled_book(output_dir, [("shared-pages/cover", 2), ("songs/one", 3), ("songs/two", 4)])
        rows = [Chord(0, 5, 2, pt(8)), Chord(pt(20), 5, 2, pt(8))]  # no overlap
        if overlap_page is not None:
            rows += [Chord(0, 5, overlap_page, pt(8)), Chord(pt(4), 5, overlap_page, pt(8))]
        (output_dir / CHORD_TRACE_NAME).write_text("".join(f"{c.x} {c.y} {c.page} {c.width}\n" for c in rows))

    def test_an_overlap_in_any_song_fails(self):
        for page in (2, 3):
            with self.subTest(page=page), TemporaryDirectory() as tmp:
                self.build(Path(tmp), overlap_page=page)
                self.assertEqual(check_book(Path(tmp)), 1)

    def test_an_overlap_outside_the_songs_fails(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), overlap_page=1)
            self.assertEqual(check_book(Path(tmp)), 1)

    def test_a_book_without_overlaps_passes(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), overlap_page=None)
            self.assertEqual(check_book(Path(tmp)), 0)

    def test_the_trace_is_read_in_order(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), overlap_page=2)
            trace = Path(tmp) / edition_output_dir(DEFAULT_EDITION) / CHORD_TRACE_NAME
            self.assertEqual(len(read_trace(trace)), 4)


if __name__ == "__main__":
    unittest.main()
