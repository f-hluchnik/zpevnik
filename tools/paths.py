"""Where things live in the repository, and the command-line argument every tool shares.

All paths are relative to the repository root; a tool joins them with the root it
was given, so it works on a checkout other than its own (the PDF diff compares two).

Python >= 3.11, standard library only.
"""
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SONGS_DIR = Path("pisnicky")
REGISTRY_FILE = Path("data/artists.toml")
BOOK_TEX = Path("zpevnik.tex")
BOOK_PDF = Path("zpevnik.pdf")
CHORD_TRACE = Path("zpevnik.chords")  # written by every build, see \chord in zpevnik.sty
MULTIPAGE_ALLOWLIST = Path("tools/multipage-allowlist.txt")
SINGLE_SONG_TEMPLATE = Path("tests/single-song.tex")
BUILD_DIR = Path("build")

GENERATED_DIR = Path("generated")
ARTISTS_TEX = GENERATED_DIR / "artists.tex"
INCLUDE_TEX = GENERATED_DIR / "include.tex"
LETTERS_TEX = GENERATED_DIR / "obsah-letters.tex"
ARTIST_PART_TEX = GENERATED_DIR / "obsah-artists.tex"
VERSION_TEX = GENERATED_DIR / "version.tex"


def resolved_path(text: str) -> Path:
    return Path(text).resolve()


def add_root_argument(parser: argparse.ArgumentParser) -> None:
    """The optional repository root every tool takes; it defaults to this checkout."""
    parser.add_argument("root", nargs="?", type=resolved_path, default=REPO_ROOT,
                        help="repository root (default: the checkout this tool is in)")
