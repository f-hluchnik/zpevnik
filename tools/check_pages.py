#!/usr/bin/env python3
"""Fail if a song takes more than one page (D-105, ticket S2).

Every song is pulled in with ``\\include{pisnicky/<id>}``, and LaTeX writes
``pisnicky/<id>.aux`` with a checkpoint that records the page counter *after*
the song. The pages of a song are therefore the difference between its
checkpoint and the previous one. Songs listed in
``tools/multipage-allowlist.txt`` may take two pages.

Usage: python3 tools/check_pages.py [repo-root]   (run after compiling)
Python >= 3.11, standard library only.
"""
import re
import sys
from pathlib import Path

MAX_PAGES = 1
MAX_PAGES_ALLOWLISTED = 2


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
    m = re.search(
        r"\\@setckpt\{pisnicky/" + re.escape(song) + r"\}\{(.*?)\n\}", text, re.S
    )
    if not m:
        return None
    p = re.search(r"\\setcounter\{page\}\{(\d+)\}", m.group(1))
    return int(p.group(1)) if p else None


def song_pages(root: Path) -> tuple[list[tuple[str, int, int]], list[str]]:
    """(song id, first page, page count) in include order, plus problems.

    Page numbers are the LaTeX page counter, which equals the PDF page index.
    Shared with tools/pdfdiff.py.
    """
    songs: list[tuple[str, int, int]] = []
    errors: list[str] = []
    prev: int | None = None
    for raw in (root / "zpevnik.tex").read_text(encoding="utf-8").splitlines():
        line = raw.split("%", 1)[0]  # commented-out includes do not count
        m = re.search(r"\\setcounter\{page\}\{(\d+)\}", line)
        if m:
            prev = int(m.group(1))  # the first song starts here
        m = re.search(r"\\include\{pisnicky/([^}]+)\}", line)
        if not m:
            continue
        song = m.group(1)
        if prev is None:
            errors.append(f"{song}: no \\setcounter{{page}} before the first song")
            continue
        cur = checkpoint_page(root / "pisnicky" / f"{song}.aux", song)
        if cur is None:
            errors.append(f"{song}: no page checkpoint in pisnicky/{song}.aux (not compiled?)")
            continue
        songs.append((song, prev, cur - prev))
        prev = cur
    return songs, errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    allow = read_allowlist(root / "tools" / "multipage-allowlist.txt")
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
        notes.append(f"{song}: in allow-list but not included in zpevnik.tex")

    for n in notes:
        print(f"note: {n}")
    for e in errors:
        print(f"ERROR: {e}")
    checked = len(songs)
    if checked == 0:
        print("ERROR: no \\include{pisnicky/...} found in zpevnik.tex")
        return 1
    print(f"checked {checked} songs, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
