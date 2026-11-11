"""The output formats of a book: one edition, typeset with different switches of zpevnik.sty.

A format is a set of TeX macros that the build defines before the document is read
(`-usepretex`, next to the edition's \\zpgenerated); zpevnik.sty reads them and gives each a
default, so the screen format defines nothing and the book stays as it was. Formats never
choose songs or front matter (that is an edition) and never change the page size (the print
step scales the finished PDF afterwards).

  screen       the PDF of the download page: links inside the book, red chords
  print        for paper: no links to follow, chords in colour
  print-black  the same with black chords (one ink)

Python >= 3.11, standard library only.
"""
import argparse

SCREEN = "screen"
PRINT = "print"
PRINT_BLACK = "print-black"

# Macro name -> body; \zpprint only has to exist, \zpchordcolor names an xcolor colour.
FORMATS: dict[str, dict[str, str]] = {
    SCREEN: {},
    PRINT: {"zpprint": ""},
    PRINT_BLACK: {"zpprint": "", "zpchordcolor": "black"},
}


def pretex(format_name: str) -> str:
    """The \\def of every macro of the format, to put before the document."""
    return "".join(f"\\def\\{name}{{{body}}}" for name, body in FORMATS[format_name].items())


def add_format_argument(parser: argparse.ArgumentParser, default: str = SCREEN) -> None:
    """The --format option of the tools that work on one built format."""
    parser.add_argument("--format", default=default, choices=sorted(FORMATS),
                        help=f"the output format (default: {default})")
