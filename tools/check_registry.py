#!/usr/bin/env python3
"""Validate the artists registry (D-002, ticket R4).

Checks data/artists.toml:
  errors   - a field is missing or has the wrong type or value, a slug is
             used twice, or a song refers (\\interpret / \\interpretdva) to a
             slug that is not in the registry;
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
    "index_label": str,
    "sort": str,
    "kind": str,
    "section": bool,
}
KINDS = {"artist", "collection"}
INTERPRET = re.compile(r"\\interpret(?:dva)?\{([^}]*)\}")


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


def song_slugs(root: Path) -> dict[str, list[str]]:
    """slug -> song files that refer to it."""
    used: dict[str, list[str]] = {}
    for path in sorted((root / "pisnicky").glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        for slug in INTERPRET.findall(text):
            used.setdefault(slug, []).append(path.stem)
    return used


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    with open(root / "data" / "artists.toml", "rb") as f:
        entries = tomllib.load(f).get("entry", [])

    errors, slugs = check_entries(entries)
    used = song_slugs(root)
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
