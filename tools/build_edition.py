#!/usr/bin/env python3
"""Compile an edition into build/editions/<edition>/ and print the path of its PDF.

latexmk runs quietly: its output is the same as the log's, so it is printed only when the run
fails, cut down to the TeX error; the full log stays in the output folder.

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

`--path` prints where the edition's PDF is (built or not), so the Makefile does not repeat the layout of build/.

Usage: python3 tools/build_edition.py [--edition NAME | --list | --path] [repo-root]   (or: make [EDITION=<name>])
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
TEX_ERROR_PREFIX = "! "  # TeX starts every error message with it
TEX_FATAL_PREFIX = "!  ==>"  # and ends a run that -halt-on-error stopped with this line
ERROR_EXCERPT_LINES = 10  # at most: the message, the line of the source it points at, the fatal line
FALLBACK_EXCERPT_LINES = 20  # the end of the output, when it holds no TeX error
TEX_OUTPUT_ENCODING = "utf-8"  # the log and the terminal output; a stray byte from TeX must not stop the build
# TeX Live reads its settings from the environment too; one log line per message.
LONG_LOG_LINES = {"max_print_line": "10000"}
MISSING_TARGET = re.compile(r"name\{([^}]*)\} has been referenced but does not exist")


class LatexError(Exception):
    """latexmk failed; the message holds the part of its output that says why."""


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


def failure_excerpt(output: str) -> str:
    """The first TeX error of latexmk's output, or the end of the output if there is none."""
    lines = output.splitlines()
    first_error = next((n for n, line in enumerate(lines) if line.startswith(TEX_ERROR_PREFIX)), None)
    if first_error is None:
        return "\n".join(lines[-FALLBACK_EXCERPT_LINES:])
    excerpt = lines[first_error:first_error + ERROR_EXCERPT_LINES]
    fatal = next((n for n, line in enumerate(excerpt) if line.startswith(TEX_FATAL_PREFIX)), len(excerpt) - 1)
    return "\n".join(excerpt[:fatal + 1])


def run_latexmk(command: list[str], root: Path, log: Path, environment: dict[str, str] | None = None) -> None:
    """Run latexmk in the root, silently; LatexError (with the excerpt and `log`) if it fails."""
    result = subprocess.run(command, cwd=root, capture_output=True,
                            encoding=TEX_OUTPUT_ENCODING, errors="replace",
                            env={**os.environ, **(environment or {})})
    if result.returncode != 0:
        raise LatexError(f"latexmk failed ({result.returncode}); the full log is {log}\n"
                         + failure_excerpt(result.stdout + result.stderr))


def missing_link_targets(log: str) -> list[str]:
    """The targets pdfTeX reports as referenced but missing, each once."""
    return sorted(set(MISSING_TARGET.findall(log)))


def pdf_path(edition: str) -> Path:
    """The PDF of an edition, relative to the root; it exists once the edition is built."""
    return edition_output_dir(edition) / BOOK_PDF_NAME


def build(root: Path, edition: str) -> Path:
    """Compile the edition and check its links; the path of its PDF, relative to the root."""
    if not (root / generated_dir(edition) / PAGES_TEX).is_file():
        raise FileNotFoundError(f"{generated_dir(edition)} is missing: "
                                f"run tools/generate.py --edition {edition} first")
    output = root / edition_output_dir(edition)
    for folder in include_folders(root):
        (output / folder).mkdir(parents=True, exist_ok=True)
    run_latexmk(latexmk_command(edition), root, edition_output_dir(edition) / BOOK_LOG_NAME, LONG_LOG_LINES)
    pdf = pdf_path(edition)
    log = (output / BOOK_LOG_NAME).read_text(encoding=TEX_OUTPUT_ENCODING, errors="replace")
    missing = missing_link_targets(log)
    if missing:
        raise MissingLinkTargets(pdf, missing)
    return pdf


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_root_argument(parser)
    what = parser.add_mutually_exclusive_group()
    what.add_argument("--list", action="store_true", help="print the editions, one per line, and exit")
    what.add_argument("--path", action="store_true", help="print the path of the edition's PDF and exit")
    args = parser.parse_args()
    if args.list:
        print(*edition_names(args.root), sep="\n")
        return 0
    if args.path:
        print(pdf_path(args.edition))
        return 0
    try:
        print(build(args.root, args.edition))
    except (FileNotFoundError, LatexError, MissingLinkTargets) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
