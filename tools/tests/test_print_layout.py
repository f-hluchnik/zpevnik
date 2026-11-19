"""Unit tests for the placement of the book's pages on the printer's A5 pages.

Run from the repository root: python3 -m unittest discover -s tools
"""
import unittest

from pdf_programs import Span
from print_layout import (A5_SCALE, A5_WIDTH_PT, LayoutError, Margins, Placement, Reach, fit,
                          is_right_hand, page_margins, reach)

A4_WIDTH = 595.0
EDGE = 28.0  # how far the letters of a symmetric test page stay from both A4 edges
SYMMETRIC = Reach(EDGE, A4_WIDTH - EDGE)


def placed(page: Reach, position: int, placement: Placement) -> Reach:
    """Where the letters of an A4 page land on A5: scaled around the centre, moved from the spine."""
    shift = placement.shift if is_right_hand(position) else -placement.shift
    def x(value: float) -> float:
        return (value - A4_WIDTH / 2) * placement.scale + A5_WIDTH_PT / 2 + shift
    return Reach(x(page.left), x(page.right))


def printed_margins(pages: list[Reach | None], placement: Placement) -> list[Margins]:
    return [page_margins(placed(page, position, placement), position, 0, A5_WIDTH_PT)
            for position, page in enumerate(pages, start=1) if page is not None]


class Fit(unittest.TestCase):
    def test_margins_wider_than_the_book_has_shrink_it_until_they_fit_exactly(self):
        required = Margins(spine=35.0, outer=13.0)
        placement = fit([SYMMETRIC, SYMMETRIC], A4_WIDTH, A5_WIDTH_PT, required)
        self.assertLess(placement.scale, A5_SCALE)
        for margins in printed_margins([SYMMETRIC, SYMMETRIC], placement):
            self.assertAlmostEqual(margins.spine, required.spine)
            self.assertAlmostEqual(margins.outer, required.outer)

    def test_the_book_never_grows_beyond_a4_to_a5_and_the_spare_room_is_split_evenly(self):
        required = Margins(spine=10.0, outer=2.0)
        placement = fit([SYMMETRIC], A4_WIDTH, A5_WIDTH_PT, required)
        self.assertEqual(placement.scale, A5_SCALE)
        margins = printed_margins([SYMMETRIC], placement)[0]
        self.assertAlmostEqual(margins.spine - required.spine, margins.outer - required.outer)

    def test_the_spine_is_on_the_left_of_a_right_hand_page_and_on_the_right_of_a_left_hand_one(self):
        # A letter far to the left faces the spine on page 1 and the outer edge on page 2,
        # so only in the first case does the book move further away from the spine.
        wide_left = Reach(5.0, A4_WIDTH - EDGE)
        required = Margins(spine=35.0, outer=13.0)
        layouts = {"spine": [wide_left, SYMMETRIC], "outer": [SYMMETRIC, wide_left]}
        placements = {side: fit(pages, A4_WIDTH, A5_WIDTH_PT, required) for side, pages in layouts.items()}
        self.assertGreater(placements["spine"].shift, placements["outer"].shift)
        for side, pages in layouts.items():
            for margins in printed_margins(pages, placements[side]):
                self.assertGreaterEqual(margins.spine, required.spine - 1e-9)
                self.assertGreaterEqual(margins.outer, required.outer - 1e-9)

    def test_pages_without_letters_are_left_out(self):
        required = Margins(spine=35.0, outer=13.0)
        self.assertEqual(fit([None, SYMMETRIC, None], A4_WIDTH, A5_WIDTH_PT, required),
                         fit([SYMMETRIC, SYMMETRIC], A4_WIDTH, A5_WIDTH_PT, required))

    def test_a_book_without_letters_cannot_be_placed(self):
        with self.assertRaisesRegex(LayoutError, "no page"):
            fit([None, None], A4_WIDTH, A5_WIDTH_PT, Margins(10.0, 10.0))

    def test_margins_wider_than_the_page_are_an_error(self):
        with self.assertRaisesRegex(LayoutError, "leave no room"):
            fit([SYMMETRIC], A4_WIDTH, A5_WIDTH_PT, Margins(A5_WIDTH_PT, 0.0))


class Reaches(unittest.TestCase):
    def test_the_reach_of_a_page_spans_all_its_words(self):
        self.assertEqual(reach([Span(30, 40), Span(10, 20), Span(50, 60)]), Reach(10, 60))

    def test_a_page_without_words_has_no_reach(self):
        self.assertIsNone(reach([]))

    def test_the_margins_of_a_printed_page_count_from_its_trimmed_edges(self):
        self.assertEqual(page_margins(Reach(40, 380), 1, trim_left=10, trim_width=400), Margins(30, 30))
        self.assertEqual(page_margins(Reach(20, 380), 2, trim_left=10, trim_width=400), Margins(30, 10))
