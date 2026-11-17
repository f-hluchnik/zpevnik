"""Unit tests for the check that every song line is one printed line inside the text.

Run from the repository root: python3 -m unittest discover -s tools
"""
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from paths import DEFAULT_EDITION, LINE_TRACE_NAME, edition_output_dir
from positions import SP_PER_PT
from song_lines import Block, LineEnd, check_book, check_trace, in_margin, read_trace, wrapped
from .test_check_pages import write_compiled_book

EDGE = 500  # pt: the right edge of the text block in these tests


def pt(points: float) -> int:
    return round(points * SP_PER_PT)


def end(page: int, x: float) -> LineEnd:
    """A line on `page` that ends at x pt, in a text block whose right edge is EDGE."""
    return LineEnd(page, pt(x), pt(EDGE))


def trace_text(blocks: list[Block], ends: list[LineEnd]) -> str:
    rows = [f"block {b.page} {b.source} {b.printed} {int(b.prose)}" for b in blocks]
    rows += [f"end {e.page} {e.x} {e.edge}" for e in ends]
    return "".join(row + "\n" for row in rows)


class Wraps(unittest.TestCase):
    def test_a_block_printed_in_more_lines_than_its_source_wrapped(self):
        blocks = [Block(1, 4, 4, False), Block(1, 2, 3, False), Block(2, 3, 2, False)]
        self.assertEqual(wrapped(blocks), [Block(1, 2, 3, False), Block(2, 3, 2, False)])

    def test_a_recitative_may_wrap(self):
        self.assertEqual(wrapped([Block(1, 2, 5, True)]), [])


class Margin(unittest.TestCase):
    def test_a_line_that_ends_past_the_edge_is_in_the_margin(self):
        ends = [end(1, EDGE + 2), end(1, EDGE), end(2, EDGE - 30)]
        self.assertEqual(in_margin(ends), [end(1, EDGE + 2)])

    def test_a_line_1_sp_past_the_edge_is_at_the_edge(self):
        at_edge, past_edge = LineEnd(1, pt(EDGE) + 1, pt(EDGE)), LineEnd(1, pt(EDGE) + 2, pt(EDGE))
        self.assertEqual(in_margin([at_edge, past_edge]), [past_edge])


class Trace(unittest.TestCase):
    def test_the_trace_is_read_by_kind(self):
        blocks, ends = [Block(3, 4, 5, False), Block(4, 2, 6, True)], [end(3, 120), end(4, EDGE + 1)]
        with TemporaryDirectory() as tmp:
            trace = Path(tmp) / LINE_TRACE_NAME
            trace.write_text(trace_text(blocks, ends))
            self.assertEqual(read_trace(trace), (blocks, ends))

    def test_the_trace_mode_fails_on_a_wrap_or_a_line_in_the_margin(self):
        with TemporaryDirectory() as tmp:
            trace = Path(tmp) / LINE_TRACE_NAME
            trace.write_text(trace_text([Block(1, 2, 3, False)], [end(1, EDGE + 4)]))
            with redirect_stdout(io.StringIO()) as report:
                status = check_trace(trace)
        self.assertEqual(status, 1)
        self.assertIn("2 line(s) of the source printed as 3 on p. 1", report.getvalue())
        self.assertIn("a line runs 4.00 pt into the margin on p. 1", report.getvalue())


class Book(unittest.TestCase):
    """A two-song full book (`one` on page 2, `two` on page 3)."""

    def build(self, root: Path, blocks: list[Block], ends: list[LineEnd]) -> None:
        output_dir = root / edition_output_dir(DEFAULT_EDITION)
        output_dir.mkdir(parents=True)
        write_compiled_book(output_dir, [("shared-pages/cover", 2), ("songs/one", 3), ("songs/two", 4)])
        (output_dir / LINE_TRACE_NAME).write_text(trace_text(blocks, ends))

    def check(self, root: Path) -> tuple[int, str]:
        """The exit status and the report of the book check; the report is captured, not printed."""
        with redirect_stdout(io.StringIO()) as report:
            status = check_book(root, DEFAULT_EDITION)
        return status, report.getvalue()

    def test_a_wrapped_line_fails_and_names_the_song(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), [Block(2, 4, 4, False), Block(3, 2, 3, False)], [end(2, 100)])
            status, report = self.check(Path(tmp))
        self.assertEqual(status, 1)
        self.assertIn("ERROR: two: 2 line(s) of the source printed as 3 on p. 3", report)

    def test_a_line_in_the_margin_fails_and_names_the_song(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), [Block(2, 1, 1, False)], [end(2, EDGE + 3)])
            status, report = self.check(Path(tmp))
        self.assertEqual(status, 1)
        self.assertIn("ERROR: one: a line runs 3.00 pt into the margin on p. 2", report)

    def test_a_book_whose_lines_fit_passes(self):
        with TemporaryDirectory() as tmp:
            self.build(Path(tmp), [Block(2, 4, 4, False), Block(3, 2, 5, True)], [end(2, EDGE), end(3, 10)])
            status, report = self.check(Path(tmp))
        self.assertEqual(status, 0)
        self.assertIn("2 song blocks, 2 lines, 0 wrapped, 0 in the margin", report)


if __name__ == "__main__":
    unittest.main()
