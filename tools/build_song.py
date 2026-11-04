#!/usr/bin/env python3
"""Build a single song without the rest of the book (ticket R14).

Usage: python3 tools/build_song.py SONG_ID      (or: make song SONG=<id>)

Run from the repository root. Writes build/<id>.tex, a main file made from
tests/single-song.tex with the song swapped in (the Overleaf setup, D-005: zpevnik.sty
and one song, so no table of contents and no artist links), compiles it with latexmk and
prints the path of build/<id>.pdf. A local build with a newer TeX Live than CI's can
differ slightly; CI stays the reference. Python >= 3.11, standard library only.
"""
import re
import subprocess
import sys
from pathlib import Path

SONGS_DIR = Path("pisnicky")
BUILD_DIR = Path("build")
TEMPLATE = Path("tests/single-song.tex")
INCLUDE_LINE = re.compile(r"\\include\{pisnicky/[^}]+\}")
LATEXMK = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error"]


def main_file_text(template: str, song: str) -> str:
    """The template with its one \\include line pointing at `song`."""
    text, replaced = INCLUDE_LINE.subn(lambda _: f"\\include{{pisnicky/{song}}}", template)
    if replaced != 1:
        raise ValueError(f"{TEMPLATE} must contain exactly one \\include{{pisnicky/...}} line")
    return text


def build(song: str) -> Path:
    if not (SONGS_DIR / f"{song}.tex").is_file():
        raise FileNotFoundError(f"no song {SONGS_DIR / (song + '.tex')} (the id is the file name without .tex)")
    (BUILD_DIR / SONGS_DIR).mkdir(parents=True, exist_ok=True)  # \include writes its .aux there
    main = BUILD_DIR / f"{song}.tex"
    main.write_text(main_file_text(TEMPLATE.read_text(encoding="utf-8"), song), encoding="utf-8")
    subprocess.run([*LATEXMK, f"-outdir={BUILD_DIR}", str(main)], check=True)
    return main.with_suffix(".pdf")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        print(build(sys.argv[1]))
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
