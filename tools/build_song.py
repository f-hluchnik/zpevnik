#!/usr/bin/env python3
"""Build a single song without the rest of the book.

Usage: python3 tools/build_song.py SONG_ID [repo-root]      (or: make song SONG=<id>)

Writes build/songs/<id>.tex, a main file made from
tests/single-song.tex with the song swapped in (the Overleaf setup: zpevnik.sty
and one song, so no table of contents and no artist links), compiles it with latexmk and
prints the path of build/songs/<id>.pdf. A local build with a newer TeX Live than CI's can
differ slightly; CI stays the reference. Python >= 3.11, standard library only.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from build_edition import LATEXMK
from paths import SINGLE_SONG_TEMPLATE, SONG_BUILD_DIR, SONGS_DIR, add_root_argument

INCLUDE_LINE = re.compile(r"\\include\{" + re.escape(str(SONGS_DIR)) + r"/[^}]+\}")


def main_file_text(template: str, song: str) -> str:
    """The template with its one \\include line pointing at `song`."""
    text, replaced = INCLUDE_LINE.subn(lambda _: f"\\include{{{SONGS_DIR}/{song}}}", template)
    if replaced != 1:
        raise ValueError(f"{SINGLE_SONG_TEMPLATE} must contain exactly one \\include{{songs/...}} line")
    return text


def build(root: Path, song: str) -> Path:
    """Compile the song; the path of its PDF, relative to the root."""
    song_file = SONGS_DIR / f"{song}.tex"
    if not (root / song_file).is_file():
        raise FileNotFoundError(f"no song {song_file} (the id is the file name without .tex)")
    (root / SONG_BUILD_DIR / SONGS_DIR).mkdir(parents=True, exist_ok=True)  # \include writes its .aux there
    main = SONG_BUILD_DIR / f"{song}.tex"
    template = (root / SINGLE_SONG_TEMPLATE).read_text(encoding="utf-8")
    (root / main).write_text(main_file_text(template, song), encoding="utf-8")
    subprocess.run([*LATEXMK, f"-outdir={SONG_BUILD_DIR}", str(main)], cwd=root, check=True)
    return main.with_suffix(".pdf")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("song", help="the song id: the file name without .tex")
    add_root_argument(parser)
    args = parser.parse_args()
    try:
        print(build(args.root, args.song))
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
