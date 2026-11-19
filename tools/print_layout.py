"""Where the pages of the book go on the printer's A5 pages: one scale and one shift (D-188).

The book is typeset on A4. Every page is scaled around its centre and then moved away from
the spine: to the right on a right-hand page (the spine on its left), to the left on a
left-hand one. The first page of the printed book is a right-hand page.

The printer asks that no letter comes closer than a margin to the spine and to the outer edge.
`fit` takes how far the ink of every page reaches across it (measured on the A4 pages) and
returns the largest scale that leaves both margins on every page, with the shift that splits
any room left over evenly between them. The scale is never above A4 to A5 (1/sqrt(2)), so the
book only shrinks and every song still fits its page.

All lengths are in pt, across the page from its left edge. Python >= 3.11, standard library only.
"""
import math
from dataclasses import dataclass

A5_SCALE = 1 / math.sqrt(2)  # A4 to A5: the sides of ISO paper differ by this factor
MM_PER_PT = 25.4 / 72
A5_WIDTH_PT = 148 / MM_PER_PT
A5_HEIGHT_PT = 210 / MM_PER_PT


class LayoutError(Exception):
    """The pages cannot be placed with the margins asked for."""


@dataclass(frozen=True)
class Reach:
    """How far the ink of one page reaches across it."""
    left: float
    right: float


@dataclass(frozen=True)
class Margins:
    spine: float
    outer: float


@dataclass(frozen=True)
class Placement:
    scale: float  # of the A4 page
    shift: float  # away from the spine, after scaling


def millimetres(points: float) -> float:
    return points * MM_PER_PT


def points(millimetres: float) -> float:
    return millimetres / MM_PER_PT


def is_right_hand(position: int) -> bool:
    """A page of the printed book, counted from 1: the odd ones have the spine on their left."""
    return position % 2 == 1


def side_reaches(reaches: list[Reach | None], page_width: float) -> Margins:
    """How far the ink reaches from the centre of the page, towards the spine and towards the
    outer edge, at most over all pages (counted from the first printed page)."""
    centre = page_width / 2
    towards_spine, towards_outer = [], []
    for position, page in enumerate(reaches, start=1):
        if page is None:
            continue
        left, right = centre - page.left, page.right - centre
        spine, outer = (left, right) if is_right_hand(position) else (right, left)
        towards_spine.append(spine)
        towards_outer.append(outer)
    if not towards_spine:
        raise LayoutError("no page has any ink to place")
    return Margins(spine=max(towards_spine), outer=max(towards_outer))


def fit(reaches: list[Reach | None], source_width: float, target_width: float, margins: Margins) -> Placement:
    """The scale and the shift that keep all ink the margins away from the spine and the outer
    edge of the target page (the trimmed page)."""
    room = target_width - margins.spine - margins.outer
    if room <= 0:
        raise LayoutError(f"the margins ({millimetres(margins.spine):.1f} and {millimetres(margins.outer):.1f} mm) "
                          f"leave no room on a page {millimetres(target_width):.1f} mm wide")
    ink = side_reaches(reaches, source_width)
    scale = min(A5_SCALE, room / (ink.spine + ink.outer))
    centre = target_width / 2
    exact_spine = margins.spine - (centre - scale * ink.spine)  # the shift that leaves exactly the spine margin
    exact_outer = (centre - scale * ink.outer) - margins.outer  # ... and exactly the outer margin
    return Placement(scale=scale, shift=(exact_spine + exact_outer) / 2)


def page_margins(page: Reach, position: int, trim_left: float, trim_width: float) -> Margins:
    """The margins of the ink of a printed page, inside its trimmed page."""
    left, right = page.left - trim_left, trim_left + trim_width - page.right
    return Margins(spine=left, outer=right) if is_right_hand(position) else Margins(spine=right, outer=left)
