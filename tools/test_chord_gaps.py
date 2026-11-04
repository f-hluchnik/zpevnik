"""Unit tests for the chord-overlap check (C3a).

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from chord_gaps import SP_PER_PT, Chord, Pair, check_book, overlapping, read_trace, same_line_pairs


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
    """A two-song book: `ok` has \\autochords, `old` has not; both have an overlap on page 2/3."""

    def build(self, root: Path, auto_song_overlaps: bool) -> None:
        (root / "pisnicky").mkdir()
        (root / "generated").mkdir()
        (root / "zpevnik.tex").write_text("\\setcounter{page}{2}\n\\input{generated/include}\n")
        (root / "generated" / "include.tex").write_text("\\songinclude{auto}\n\\songinclude{old}\n")
        for song, after in (("auto", 3), ("old", 4)):
            (root / "pisnicky" / f"{song}.aux").write_text(
                f"\\@setckpt{{pisnicky/{song}}}{{\n\\setcounter{{page}}{{{after}}}\n}}\n")
        (root / "pisnicky" / "auto.tex").write_text("\\song{A}\n\\autochords\n")
        (root / "pisnicky" / "old.tex").write_text("\\song{B}\n")
        first_page = 2 if auto_song_overlaps else 1
        rows = [Chord(0, 5, first_page, pt(8)), Chord(pt(4), 5, first_page, pt(8)),  # overlap
                Chord(0, 5, 3, pt(8)), Chord(pt(4), 5, 3, pt(8))]  # overlap in `old`
        (root / "zpevnik.chords").write_text("".join(f"{c.x} {c.y} {c.page} {c.width}\n" for c in rows))

    def test_an_overlap_in_an_autochords_song_fails(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), auto_song_overlaps=True)
            self.assertEqual(check_book(Path(tmp), 10), 1)

    def test_an_overlap_in_a_manual_song_is_only_reported(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), auto_song_overlaps=False)  # page 1 is outside the songs
            self.assertEqual(check_book(Path(tmp), 10), 0)

    def test_the_trace_is_read_in_order(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), auto_song_overlaps=True)
            self.assertEqual(len(read_trace(Path(tmp) / "zpevnik.chords")), 4)


if __name__ == "__main__":
    unittest.main()
