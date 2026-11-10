#!/usr/bin/env python3
"""Fail if a song takes more than one page.

LaTeX lists every \\include-d file in the book's main .aux file, in book order, and
writes a checkpoint into each file's own .aux that records the page counter *after*
the file. A song (a file of songs/) therefore starts at the checkpoint of the file
included before it and takes the difference to its own checkpoint. The page counter
is never set by hand, so it equals the PDF page index. Songs listed in
``tools/multipage-allowlist.txt`` may take two pages.

Usage: python3 tools/check_pages.py [--edition NAME] [repo-root]   (run after compiling)
Python >= 3.11, standard library only.
"""
import argparse
import re
import sys
from pathlib import Path, PurePosixPath

from paths import (BOOK_AUX_NAME, MULTIPAGE_ALLOWLIST, SONGS_DIR, add_edition_argument,
                   add_root_argument, edition_output_dir)

MAX_PAGES = 1
MAX_PAGES_ALLOWLISTED = 2
INCLUDED_FILE = re.compile(r"^\\@input\{(.+)\.aux\}$", re.M)  # \@input{songs/alfa.aux}
PAGE_COUNTER = re.compile(r"\\setcounter\{page\}\{(\d+)\}")


def read_allowlist(path: Path) -> set[str]:
    ids = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                ids.add(line)
    return ids


def included_files(output_dir: Path) -> list[str]:
    """The \\include-d files in book order, as named in the \\include (no .aux)."""
    return INCLUDED_FILE.findall((output_dir / BOOK_AUX_NAME).read_text(encoding="utf-8", errors="replace"))


def checkpoint_page(output_dir: Path, name: str) -> int | None:
    """Page counter recorded by the file's own \\@setckpt block, or None if there is none."""
    aux = output_dir / f"{name}.aux"
    if not aux.is_file():
        return None
    text = aux.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"\\@setckpt\{" + re.escape(name) + r"\}\{(.*?)\n\}", text, re.S)
    page = PAGE_COUNTER.search(block.group(1)) if block else None
    return int(page.group(1)) if page else None


def song_id(name: str) -> str | None:
    """The song id of an included file, or None if it is not a song."""
    path = PurePosixPath(name)
    return path.name if path.parent == PurePosixPath(SONGS_DIR) else None


def song_pages(output_dir: Path) -> tuple[list[tuple[str, int, int]], list[str]]:
    """(song id, first page, page count) in book order, plus problems.

    `output_dir` holds the compiled book (its main .aux file). Shared with tools/pdfdiff.py.
    """
    if not (output_dir / BOOK_AUX_NAME).is_file():
        return [], [f"no {output_dir / BOOK_AUX_NAME} (not compiled?)"]
    songs: list[tuple[str, int, int]] = []
    errors: list[str] = []
    previous: int | None = None  # the checkpoint of the file before
    for name in included_files(output_dir):
        page = checkpoint_page(output_dir, name)
        song = song_id(name)
        if page is None:
            errors.append(f"{name}: no page checkpoint in {name}.aux")
        elif song is not None and previous is None:
            errors.append(f"{song}: no included file before it to start from")
        elif song is not None:
            songs.append((song, previous, page - previous))
        previous = page
    return songs, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_edition_argument(parser)
    add_root_argument(parser)
    args = parser.parse_args()
    allow = read_allowlist(args.root / MULTIPAGE_ALLOWLIST)
    output_dir = args.root / edition_output_dir(args.edition)
    songs, errors = song_pages(output_dir)
    notes: list[str] = []
    seen_allowed: set[str] = set()

    for song, _start, pages in songs:
        limit = MAX_PAGES_ALLOWLISTED if song in allow else MAX_PAGES
        if song in allow:
            seen_allowed.add(song)
        if pages < 1:
            errors.append(f"{song}: {pages} pages (checkpoint went backwards; parse problem?)")
        elif pages > limit:
            errors.append(f"{song}: takes {pages} pages (limit {limit})")
        elif song in allow and pages == 1:
            notes.append(f"{song}: allow-listed but fits on one page")

    for song in sorted(allow - seen_allowed):
        notes.append(f"{song}: in allow-list but not included in the edition")

    for n in notes:
        print(f"note: {n}")
    for e in errors:
        print(f"ERROR: {e}")
    if not songs and not errors:
        print(f"ERROR: no song found in {output_dir / BOOK_AUX_NAME}")
        return 1
    print(f"checked {len(songs)} songs, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
