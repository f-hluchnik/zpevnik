"""Positions that TeX records with \\pdfsavepos for the build checks (chord_gaps, song_lines)."""

SP_PER_PT = 65536
# TeX rounds the positions on a squeezed or stretched line to whole sp: a position 1 sp past
# the edge is at the edge.
POSITION_PRECISION_SP = 1


def past(position_sp: int, edge_sp: int) -> bool:
    """Whether a position lies past an edge, beyond the rounding of the positions."""
    return position_sp - edge_sp > POSITION_PRECISION_SP
