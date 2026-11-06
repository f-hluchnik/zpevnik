#!/usr/bin/env python3
"""Fail if a song takes more than one page.

Every song is pulled in with ``\\songinclude{<id>}``, which ends in
``\\include{pisnicky/<id>}``, and LaTeX writes
``pisnicky/<id>.aux`` with a checkpoint that records the page counter *after*
the song. The pages of a song are therefore the difference between its
checkpoint and the previous one. Songs listed in
``tools/multipage-allowlist.txt`` may take two pages.

Usage: python3 tools/check_pages.py [repo-root]   (run after compiling)
Python >= 3.11, standard library only.
"""
import argparse
import re
import sys
from pathlib import Path

from paths import BOOK_TEX, INCLUDE_TEX, MULTIPAGE_ALLOWLIST, SONGS_DIR, add_root_argument

MAX_PAGES = 1
MAX_PAGES_ALLOWLISTED = 2
SONG_INCLUDE = re.compile(r"\\songinclude\{([^}]+)\}")
INPUT_INCLUDE_LIST = re.compile(r"\\input\{" + re.escape(str(INCLUDE_TEX.with_suffix(""))) + r"\}")
PAGE_COUNTER = re.compile(r"\\setcounter\{page\}\{(\d+)\}")


def read_allowlist(path: Path) -> set[str]:
    ids = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                ids.add(line)
    return ids


def checkpoint_page(aux: Path, song: str) -> int | None:
    """Page counter recorded by the song's own \\@setckpt block."""
    text = aux.read_text(encoding="utf-8", errors="replace")
    block = re.search(
        r"\\@setckpt\{" + re.escape(f"{SONGS_DIR}/{song}") + r"\}\{(.*?)\n\}", text, re.S
    )
    if not block:
        return None
    page = PAGE_COUNTER.search(block.group(1))
    return int(page.group(1)) if page else None


def book_lines(root: Path) -> list[str]:
    """Lines of zpevnik.tex, with \\input{generated/include} expanded."""
    lines: list[str] = []
    for raw in (root / BOOK_TEX).read_text(encoding="utf-8").splitlines():
        if INPUT_INCLUDE_LIST.match(raw):
            lines += (root / INCLUDE_TEX).read_text(encoding="utf-8").splitlines()
        else:
            lines.append(raw)
    return lines


def song_pages(root: Path) -> tuple[list[tuple[str, int, int]], list[str]]:
    """(song id, first page, page count) in include order, plus problems.

    Page numbers are the LaTeX page counter, which equals the PDF page index.
    Shared with tools/pdfdiff.py.
    """
    songs: list[tuple[str, int, int]] = []
    errors: list[str] = []
    prev: int | None = None
    for raw in book_lines(root):
        line = raw.split("%", 1)[0]  # commented-out includes do not count
        counter = PAGE_COUNTER.search(line)
        if counter:
            prev = int(counter.group(1))  # the first song starts here
        include = SONG_INCLUDE.search(line)
        if not include:
            continue
        song = include.group(1)
        if prev is None:
            errors.append(f"{song}: no \\setcounter{{page}} before the first song")
            continue
        cur = checkpoint_page(root / SONGS_DIR / f"{song}.aux", song)
        if cur is None:
            errors.append(f"{song}: no page checkpoint in {SONGS_DIR}/{song}.aux (not compiled?)")
            continue
        songs.append((song, prev, cur - prev))
        prev = cur
    return songs, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_root_argument(parser)
    root = parser.parse_args().root
    allow = read_allowlist(root / MULTIPAGE_ALLOWLIST)
    songs, errors = song_pages(root)
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
        notes.append(f"{song}: in allow-list but not included in the book")

    for n in notes:
        print(f"note: {n}")
    for e in errors:
        print(f"ERROR: {e}")
    checked = len(songs)
    if checked == 0:
        print(f"ERROR: no \\songinclude{{...}} found in {BOOK_TEX} or {INCLUDE_TEX}")
        return 1
    print(f"checked {checked} songs, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
