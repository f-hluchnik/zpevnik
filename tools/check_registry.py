#!/usr/bin/env python3
"""Validate the artists registry (D-002, ticket R4).

Checks data/artists.toml:
  errors   - a field is missing or has the wrong type or value, a slug is
             used twice, a song refers (\\artist) to a slug that is not in the
             registry, or a song does not have exactly one \\artist line;
  warnings - an entry with section = true that no song refers to.

Usage: python3 tools/check_registry.py [repo-root]
Exits 1 on errors (warnings do not fail). Python >= 3.11, standard library only.
"""
import re
import sys
import tomllib
from pathlib import Path

FIELDS = {
    "slug": str,
    "name": str,
    "song_label": str,
    "index_label": str,
    "sort": str,
    "kind": str,
    "section": bool,
}
KINDS = {"artist", "collection"}
ARTIST = re.compile(r"\\artist(?:\[[^\]]*\])?\{([^}]*)\}")
ARTIST_LINE = re.compile(r"\\artist\b")
OLD_MACRO = re.compile(r"\\interpret(?:dva)?\b")
MAX_ARTISTS = 2  # per song, see \artist in zpevnik.sty


def check_entries(entries: list) -> tuple[list[str], set[str]]:
    errors = []
    seen = set()
    for n, entry in enumerate(entries, 1):
        where = f"entry {n} ({entry.get('slug', '?')})"
        for field, typ in FIELDS.items():
            if field not in entry:
                errors.append(f"{where}: missing '{field}'")
            elif not isinstance(entry[field], typ):
                errors.append(f"{where}: '{field}' must be {typ.__name__}")
            elif typ is str and not entry[field].strip():
                errors.append(f"{where}: '{field}' is empty")
        for field in entry.keys() - FIELDS.keys():
            errors.append(f"{where}: unknown field '{field}'")
        if entry.get("kind") not in KINDS:
            errors.append(f"{where}: 'kind' must be one of {sorted(KINDS)}")
        slug = entry.get("slug")
        if slug in seen:
            errors.append(f"{where}: duplicate slug")
        seen.add(slug)
    return errors, seen


def song_slugs(root: Path) -> tuple[dict[str, list[str]], list[str]]:
    """(slug -> song files that refer to it, problems with the \\artist lines).

    Every song has exactly one line with \\artist (it holds one or two
    \\artist commands); an empty slug is allowed and is not counted as used.
    """
    used: dict[str, list[str]] = {}
    problems: list[str] = []
    for path in sorted((root / "pisnicky").glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        lines = [ln for ln in text.splitlines() if ARTIST_LINE.search(ln)]
        if len(lines) != 1:
            problems.append(f"{path.stem}: {len(lines)} lines with \\artist, expected exactly 1")
        if OLD_MACRO.search(text):
            problems.append(f"{path.stem}: still uses \\interpret / \\interpretdva")
        slugs = ARTIST.findall(text)
        if len(slugs) > MAX_ARTISTS:
            problems.append(f"{path.stem}: {len(slugs)} artists, at most {MAX_ARTISTS} are printed")
        for slug in slugs:
            if slug:
                used.setdefault(slug, []).append(path.stem)
    return used, problems


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    with open(root / "data" / "artists.toml", "rb") as f:
        entries = tomllib.load(f).get("entry", [])

    errors, slugs = check_entries(entries)
    used, problems = song_slugs(root)
    errors.extend(problems)
    for slug, songs in sorted(used.items()):
        if slug not in slugs:
            errors.append(f"unknown slug '{slug}' used by {len(songs)} song(s), e.g. {songs[0]}")
    warnings = [
        f"entry '{e['slug']}' has a section but no song refers to it"
        for e in entries
        if e.get("section") is True and e.get("slug") not in used
    ]

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"checked {len(entries)} entries, {len(used)} slugs used by songs: "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
