"""Where things live in the repository, and the command-line argument every tool shares.

All paths are relative to the repository root; a tool joins them with the root it
was given, so it works on a checkout other than its own (the PDF diff compares two).

Python >= 3.11, standard library only.
"""
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SONGS_DIR = Path("songs")
REGISTRY_FILE = Path("data/artists.toml")
BOOK_FILE = Path("data/book.toml")      # facts of the songbook every edition shares
EDITIONS_DIR = Path("editions")         # editions/<name>/edition.toml and its own pages
EDITION_FILE_NAME = "edition.toml"
SHARED_PAGES_DIR = Path("shared-pages")  # pages an edition can share, and the imprint core
BOOK_TEX = Path("zpevnik.tex")
BOOK_PDF_NAME = "zpevnik.pdf"           # the PDF of every edition, in its output directory
BOOK_AUX_NAME = "zpevnik.aux"           # its main auxiliary file, which lists every \include
BOOK_LOG_NAME = "zpevnik.log"           # the log of its last LaTeX run
CHORD_TRACE_NAME = "zpevnik.chords"     # written by every build, see \chord in zpevnik.sty
MULTIPAGE_ALLOWLIST = Path("tools/multipage-allowlist.txt")
SINGLE_SONG_TEMPLATE = Path("tests/single-song.tex")
STYLE_FILE = Path("zpevnik.sty")
SCORES_DIR = Path("scores")              # MuseScore sources, one .mscz per image
SCORE_STYLE = SCORES_DIR / "zpevnik.mss"  # shared MuseScore style, applied on every export

# Everything derived lives under one root (gitignored), deleted by `make clean`.
BUILD_DIR = Path("build")
SCORE_OUTPUT_DIR = BUILD_DIR / "scores"  # <name>.svg (web), .pdf (pdfLaTeX), .tex (placement)
SONG_BUILD_DIR = BUILD_DIR / "songs"     # make song: <id>.pdf
EDITION_BUILD_DIR = BUILD_DIR / "editions"
DEFAULT_EDITION = "full"

# The files tools/generate.py writes into an edition's generated/ directory.
ARTISTS_TEX = Path("artists.tex")
INCLUDE_TEX = Path("include.tex")
SONG_LIST_TEX = Path("song-list.tex")
LETTERS_TEX = Path("obsah-letters.tex")
ARTIST_PART_TEX = Path("obsah-artists.tex")
VERSION_TEX = Path("version.tex")
MACROS_TEX = Path("macros.tex")
PAGES_TEX = Path("pages.tex")


def edition_output_dir(edition: str) -> Path:
    """Where an edition is built: its PDF, LaTeX's auxiliary files and generated/."""
    return EDITION_BUILD_DIR / edition


def generated_dir(edition: str) -> Path:
    """The generated .tex files of an edition."""
    return edition_output_dir(edition) / "generated"


def add_edition_argument(parser: argparse.ArgumentParser) -> None:
    """The --edition option of the tools that work on one edition."""
    parser.add_argument("--edition", default=DEFAULT_EDITION,
                        help=f"the edition, a folder of {EDITIONS_DIR}/ (default: {DEFAULT_EDITION})")


def resolved_path(text: str) -> Path:
    return Path(text).resolve()


def add_root_argument(parser: argparse.ArgumentParser) -> None:
    """The optional repository root every tool takes; it defaults to this checkout."""
    parser.add_argument("root", nargs="?", type=resolved_path, default=REPO_ROOT,
                        help="repository root (default: the checkout this tool is in)")
