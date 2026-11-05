"""Chords written without \\chord become \\chords{...} (ticket C3, D-123).

Two cases: a plain \\textbf{...} that holds only chord names, and a whole chord-only line
(also inside \\intro{}, \\solo{}, ...). Python >= 3.11, standard library only.
"""
import re

from chord_syntax import (
    CHORD_NAMES,
    ENDS_WITH_CONTROL_WORD,
    PLAIN_CHORD_ARGUMENT,
    PLAIN_CHORD_PATTERN,
    SPACING_MACRO,
    SPACING_RUN,
)
from migration_report import Report, clean, line_of

# Opening of a wrapper before chords on a line: `\intro{`, `\vers{1}{`, `\rep{`, ...
_LINE_OPENERS = r"(?:\\(?!chords?\b)[A-Za-z]+(?:\{[^{}]*\})*\{)*"
_BLANKS = rf"(?:{SPACING_MACRO}|[ \t])*"
CHORD_ONLY_LINE = re.compile(
    rf"^(?P<head>[ \t]*{_LINE_OPENERS})"
    rf"(?P<body>{_BLANKS}(?:{PLAIN_CHORD_PATTERN}{_BLANKS})+)"
    r"(?P<tail>(?:\\\\)?[ \t]*\}*[ \t]*(?:%.*)?)$"
)
TEXTBF = re.compile(r"\\textbf\{((?:[^{}]|\{[^{}]*\})*)\}")
LINE_BREAK = re.compile(r"(\\\\\s*)")  # keeps the line break and the blanks after it
GLUED_CHORDS = re.compile(r"(\\[A-Za-z]+) (?=[A-H(\\])")  # TeX swallows that space


def chord_names(body: str) -> str | None:
    """The chord names of a plain `\\textbf{body}` with the spacing removed, or None."""
    text = " ".join(SPACING_RUN.sub(" ", body).split())
    return text if CHORD_NAMES.fullmatch(text) else None


def join_chords(names: list[str]) -> str:
    """Chord names for \\chords{...}: a name that ends with a control word gets `{}`, or
    TeX would swallow the space that separates it from the next name."""
    return " ".join(
        name + "{}" if ENDS_WITH_CONTROL_WORD.search(name) and i < len(names) - 1 else name
        for i, name in enumerate(names)
    )


def unglue(names: str, song: str, line: int, report: Report) -> str:
    """`{}` after a control word that TeX would glue to the next chord (owner's answer, D-123)."""
    fixed = GLUED_CHORDS.sub(r"\1{} ", names)
    if fixed != names:
        report.note("glued", song, line, "TeX glued two chords (a control word swallows the space) -> {}", clean(fixed))
    return fixed


def chord_rows(body: str) -> list[str] | None:
    """The chord names of each line of a plain `\\textbf{body}` (lines end at `\\\\`), or None."""
    rows = [chord_names(row) for row in LINE_BREAK.split(body)[::2]]
    return None if None in rows else rows


def chordify_textbf(src: str, song: str, report: Report) -> str:
    def convert(m: re.Match) -> str:
        rows = chord_rows(m.group(1))
        if rows is None:
            return m.group()
        line = line_of(src, m.start())
        rows = [unglue(names, song, line, report) for names in rows]
        report.note("textbf", song, line, "\\textbf of chord names -> \\chords", clean(" \\\\ ".join(rows)))
        breaks = LINE_BREAK.split(m.group(1))[1::2]
        return "".join(f"{sep}\\chords{{{names}}}" for sep, names in zip(["", *breaks], rows))

    return TEXTBF.sub(convert, src)


def chordify_lines(src: str, song: str, report: Report) -> str:
    out = []
    for number, line in enumerate(src.split("\n"), 1):
        m = CHORD_ONLY_LINE.match(line)
        if m:
            names = join_chords([arg[1:-1] for arg in PLAIN_CHORD_ARGUMENT.findall(m.group("body"))])
            report.note("chord-line", song, number, "chord-only line -> \\chords", clean(line.strip()[:70]))
            line = f"{m.group('head')}\\chords{{{names}}}{m.group('tail')}"
        out.append(line)
    return "\n".join(out)
