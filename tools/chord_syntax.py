"""Patterns of the chord notation, shared by the chord-spacing tools (D-123).

Used by strip_chord_spacing.py (rewrites songs) and chord_gaps.py (checks the
build). Python >= 3.11, standard library only.
"""
import re

AUTOCHORDS = "\\autochords"  # per-song switch of the automatic spacing, removed in C4
AUTOCHORDS_LINE = re.compile(r"^\\autochords\b", re.MULTILINE)

# Manual spacing macros and their width in characters of 0.5 em (D-123).
SPACING_UNITS = {"sm": 1, "mm": 2, "nc": 4, "bc": 8}
SPACING_MACRO = r"\\(?:nc|mm|sm|bc)(?![A-Za-z])"
SPACING_RUN = re.compile(rf"(?:{SPACING_MACRO}[ \t]*)+")
GAP_MACRO = re.compile(r"\\gap\{\d+\}")
ENDS_WITH_CONTROL_WORD = re.compile(r"\\[A-Za-z]+$")  # TeX swallows a space after it

# A braced argument; nested braces up to three levels (\chord{A\bas{F\kk}}).
BRACED = r"\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}"
PLAIN_CHORD_PATTERN = r"\\chord" + BRACED  # without an alignment option
PLAIN_CHORD_ARGUMENT = re.compile(r"\\chord(" + BRACED + ")")
CHORD_PATTERN = r"\\chord(?:\[[a-z]\])?" + BRACED
CHORD = re.compile(CHORD_PATTERN)
CHORD_AT_END = re.compile(rf"(?:{CHORD_PATTERN})+$")  # chords right before the end of a text
CHORD_START = re.compile(r"\\chords?[\[{]")  # \chord or \chords
INLINE_CHORDS_START = re.compile(r"\\chords\{")  # \chords: inline, no collision handling

# One chord name as it is typed in a plain \textbf{...}: a base note (H = B natural,
# B = B flat) with suffixes such as m, 7, \kk, \maj, \sus{4}, \bas{E}, or a bass run \bas{A C}.
# A control word may be followed by a space when an `m` comes next: `F\kk m` is F sharp minor.
_CHORD_NAME = r"\(?(?:\\bas\{[^{}]*\}|[A-H])(?:m|\d|\\[A-Za-z]+(?:\{[^{}]*\})?(?: (?=m))?|\\[\d+]|[),])*"
CHORD_NAMES = re.compile(rf"\s*(?:{_CHORD_NAME}\s*)+")


def ends_with_chord(text: str) -> bool:
    """Is the last thing in `text` a \\chord (typed blanks after it do not count)?"""
    return CHORD_AT_END.search(text.rstrip(" \t")) is not None


def has_autochords(song_text: str) -> bool:
    """Does the song opt in to the automatic spacing?"""
    return AUTOCHORDS_LINE.search(song_text) is not None
