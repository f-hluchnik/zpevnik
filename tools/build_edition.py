#!/usr/bin/env python3
"""Compile an edition into build/editions/<edition>/ and print the path of its PDF.

A link to a missing target fails the build (D-139): pdfTeX warns about it in the log
("name{...} has been referenced but does not exist"), which covers the contents, the
\\seealso links and the artist links of every edition. TeX runs with long log lines,
so a warning is never split.

The edition's generated files must exist (tools/generate.py --edition <edition>; `make`
runs both). LaTeX writes the auxiliary file of every \\include-d file into the output
directory under the file's own folder, but does not create that folder, so the build
creates one for each folder an \\include can come from: the songs, the shared pages and
the edition folders (edition.py keeps an edition's files directly in one of them).
The edition reaches zpevnik.tex as one definition before the document, \\zpgenerated.

`--list` prints the editions, one per line: the one place that says what an edition is (a folder of
editions/), so the CI builds every edition without a list of its own.

Usage: python3 tools/build_edition.py [--edition NAME | --list] [repo-root]   (or: make [EDITION=<name>])
Python >= 3.11, standard library only.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from edition import edition_names
from paths import (BOOK_LOG_NAME, BOOK_PDF_NAME, BOOK_TEX, EDITIONS_DIR, PAGES_TEX, SHARED_PAGES_DIR,
                   SONGS_DIR, add_edition_argument, add_root_argument, edition_output_dir, generated_dir)

LATEXMK = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error"]
# TeX Live reads its settings from the environment too; one log line per message.
LONG_LOG_LINES = {"max_print_line": "10000"}
MISSING_TARGET = re.compile(r"name\{([^}]*)\} has been referenced but does not exist")


class MissingLinkTargets(Exception):
    """Links of the compiled edition that point nowhere."""

    def __init__(self, pdf: Path, targets: list[str]):
        super().__init__(f"{pdf}: links to missing targets: {', '.join(targets)}")


def include_folders(root: Path) -> list[Path]:
    """Every folder an \\include-d file can be in, relative to the root."""
    return [SONGS_DIR, SHARED_PAGES_DIR, *(EDITIONS_DIR / name for name in edition_names(root))]


def latexmk_command(edition: str) -> list[str]:
    definition = f"\\def\\zpgenerated{{{generated_dir(edition).as_posix()}}}"
    return [*LATEXMK, f"-outdir={edition_output_dir(edition)}", f"-usepretex={definition}", str(BOOK_TEX)]


def missing_link_targets(log: str) -> list[str]:
    """The targets pdfTeX reports as referenced but missing, each once."""
    return sorted(set(MISSING_TARGET.findall(log)))


def build(root: Path, edition: str) -> Path:
    """Compile the edition and check its links; the path of its PDF, relative to the root."""
    if not (root / generated_dir(edition) / PAGES_TEX).is_file():
        raise FileNotFoundError(f"{generated_dir(edition)} is missing: "
                                f"run tools/generate.py --edition {edition} first")
    output = root / edition_output_dir(edition)
    for folder in include_folders(root):
        (output / folder).mkdir(parents=True, exist_ok=True)
    subprocess.run(latexmk_command(edition), cwd=root, check=True, env={**os.environ, **LONG_LOG_LINES})
    pdf = edition_output_dir(edition) / BOOK_PDF_NAME
    log = (output / BOOK_LOG_NAME).read_text(encoding="utf-8", errors="replace")
    missing = missing_link_targets(log)
    if missing:
        raise MissingLinkTargets(pdf, missing)
    return pdf


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_root_argument(parser)
    parser.add_argument("--list", action="store_true", help="print the editions, one per line, and exit")
    args = parser.parse_args()
    if args.list:
        print(*edition_names(args.root), sep="\n")
        return 0
    try:
        print(build(args.root, args.edition))
    except (FileNotFoundError, MissingLinkTargets) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
