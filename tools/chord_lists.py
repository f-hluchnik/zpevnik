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
GLUED_CHORDS = re.compile(r"\\[A-Za-z]+ (?=[A-H(\\])")  # TeX swallows that space


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


def chordify_textbf(src: str, song: str, report: Report) -> str:
    def convert(m: re.Match) -> str:
        names = chord_names(m.group(1))
        line = line_of(src, m.start())
        if names is None:
            if "\\\\" in m.group(1) and chord_names(m.group(1).replace("\\\\", " ")):
                report.note("textbf-left", song, line, "chords with a line break, left as \\textbf",
                            clean(m.group()[:60]))
            return m.group()
        if GLUED_CHORDS.search(names):
            report.note("glued", song, line, "CHECK, TeX glues two chords (a control word swallows the space)",
                        clean(names))
        report.note("textbf", song, line, "\\textbf of chord names -> \\chords", clean(names))
        return f"\\chords{{{names}}}"

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
