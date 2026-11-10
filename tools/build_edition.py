#!/usr/bin/env python3
"""Compile an edition into build/editions/<edition>/ and print the path of its PDF.

The edition's generated files must exist (tools/generate.py --edition <edition>; `make`
runs both). LaTeX writes the auxiliary file of every \\include-d file into the output
directory under the file's own folder, but does not create that folder, so the build
creates one for each folder an \\include can come from: the songs, the shared pages and
the edition folders (edition.py keeps an edition's files directly in one of them).
The edition reaches zpevnik.tex as one definition before the document, \\zpgenerated.

Usage: python3 tools/build_edition.py [--edition NAME] [repo-root]   (or: make [EDITION=<name>])
Python >= 3.11, standard library only.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from paths import (BOOK_PDF_NAME, BOOK_TEX, EDITIONS_DIR, PAGES_TEX, SHARED_PAGES_DIR, SONGS_DIR,
                   add_edition_argument, add_root_argument, edition_output_dir, generated_dir)

LATEXMK = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error"]


def include_folders(root: Path) -> list[Path]:
    """Every folder an \\include-d file can be in, relative to the root."""
    editions = sorted(path.relative_to(root) for path in (root / EDITIONS_DIR).iterdir() if path.is_dir())
    return [SONGS_DIR, SHARED_PAGES_DIR, *editions]


def latexmk_command(edition: str) -> list[str]:
    definition = f"\\def\\zpgenerated{{{generated_dir(edition).as_posix()}}}"
    return [*LATEXMK, f"-outdir={edition_output_dir(edition)}", f"-usepretex={definition}", str(BOOK_TEX)]


def build(root: Path, edition: str) -> Path:
    """Compile the edition; the path of its PDF, relative to the root."""
    if not (root / generated_dir(edition) / PAGES_TEX).is_file():
        raise FileNotFoundError(f"{generated_dir(edition)} is missing: "
                                f"run tools/generate.py --edition {edition} first")
    output = root / edition_output_dir(edition)
    for folder in include_folders(root):
        (output / folder).mkdir(parents=True, exist_ok=True)
    subprocess.run(latexmk_command(edition), cwd=root, check=True)
    return edition_output_dir(edition) / BOOK_PDF_NAME


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_root_argument(parser)
    args = parser.parse_args()
    try:
        print(build(args.root, args.edition))
    except FileNotFoundError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
