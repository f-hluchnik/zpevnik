"""The output formats of a book: one edition, typeset with different switches of zpevnik.sty.

A format is a set of TeX macros that the build defines before the document is read
(`-usepretex`, next to the edition's \\zpgenerated); zpevnik.sty reads them and gives each a
default, so the screen format defines nothing and the book stays as it was. Formats never
choose songs or front matter (that is an edition) and never change the page size (the print
step scales the finished PDF afterwards).

  screen       the PDF of the download page: links inside the book, red chords
  print        for paper: no links to follow, chords in colour
  print-black  for paper in one ink, black (D-188): black chords, and the scores from their
               black-ink images (scores.py); the A5 step checks that no page uses another ink

Python >= 3.11, standard library only.
"""
import argparse
from dataclasses import dataclass

SCREEN = "screen"
PRINT = "print"
PRINT_BLACK = "print-black"

# The macros zpevnik.sty reads. \zpprint only has to exist; \zpchordcolor names an xcolor colour;
# \zpscoresuffix is added to a score's file name in build/scores/.
PAPER_MACRO = "zpprint"
CHORD_COLOUR_MACRO = "zpchordcolor"
SCORE_SUFFIX_MACRO = "zpscoresuffix"
BLACK = "black"
BLACK_SCORE_SUFFIX = "-black"  # build/scores/<name>-black.pdf, the score in black ink only


@dataclass(frozen=True)
class Format:
    paper: bool      # typeset for paper: nothing that only exists to be clicked
    black_ink: bool  # everything in one ink, black: the chords and the scores too


FORMATS: dict[str, Format] = {
    SCREEN: Format(paper=False, black_ink=False),
    PRINT: Format(paper=True, black_ink=False),
    PRINT_BLACK: Format(paper=True, black_ink=True),
}


def macros(format_name: str) -> dict[str, str]:
    """Macro name -> body, for every macro the format defines."""
    chosen = FORMATS[format_name]
    definitions = {PAPER_MACRO: ""} if chosen.paper else {}
    if chosen.black_ink:
        definitions |= {CHORD_COLOUR_MACRO: BLACK, SCORE_SUFFIX_MACRO: BLACK_SCORE_SUFFIX}
    return definitions


def pretex(format_name: str) -> str:
    """The \\def of every macro of the format, to put before the document."""
    return "".join(f"\\def\\{name}{{{body}}}" for name, body in macros(format_name).items())


def is_black_ink(format_name: str) -> bool:
    return FORMATS[format_name].black_ink


def add_format_argument(parser: argparse.ArgumentParser, default: str = SCREEN) -> None:
    """The --format option of the tools that work on one built format."""
    parser.add_argument("--format", default=default, choices=sorted(FORMATS),
                        help=f"the output format (default: {default})")
