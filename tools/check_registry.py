"""Validate the entries of the artists registry (D-002, ticket R4).

`check_entries` reports a field that is missing or has the wrong type or value,
an unknown field and a slug used twice. The lints that compare the registry with
the songs are in lint.py (R12).

Python >= 3.11, standard library only.
"""
import re
from typing import TypedDict

REQUIRED = {"slug": str, "name": str}
OPTIONAL = {"label": str, "link_label": str, "sort": str, "kind": str, "section": bool}
KINDS = {"artist", "collection"}
PERSON = re.compile(r"([^,&]+), ([^,&]+)")


def derive_label(name: str) -> str:
    """"Plíhal, Karel" gives "Karel Plíhal"; any other name is its own label."""
    m = PERSON.fullmatch(name)
    return f"{m.group(2)} {m.group(1)}" if m else name


class Artist(TypedDict):
    """A registry entry with every default filled in."""
    slug: str
    name: str
    label: str
    link_label: str
    sort: str
    kind: str
    section: bool


def normalise(entry: dict) -> Artist:
    """The entry with every default filled in (see the header of artists.toml)."""
    label = entry.get("label", derive_label(entry["name"]))
    return {
        "slug": entry["slug"],
        "name": entry["name"],
        "label": label,
        "link_label": entry.get("link_label", label),
        "sort": entry.get("sort", entry["name"]),
        "kind": entry.get("kind", "artist"),
        "section": entry.get("section", True),
    }


def check_entries(entries: list) -> tuple[list[str], set[str]]:
    errors = []
    seen = set()
    for n, entry in enumerate(entries, 1):
        where = f"entry {n} ({entry.get('slug', '?')})"
        for field, typ in REQUIRED.items():
            if field not in entry:
                errors.append(f"{where}: missing '{field}'")
        for field, typ in {**REQUIRED, **OPTIONAL}.items():
            if field not in entry:
                continue
            if not isinstance(entry[field], typ):
                errors.append(f"{where}: '{field}' must be {typ.__name__}")
            elif typ is str and not entry[field].strip():
                errors.append(f"{where}: '{field}' is empty")
        for field in entry.keys() - REQUIRED.keys() - OPTIONAL.keys():
            errors.append(f"{where}: unknown field '{field}'")
        if entry.get("kind", "artist") not in KINDS:
            errors.append(f"{where}: 'kind' must be one of {sorted(KINDS)}")
        slug = entry.get("slug")
        if slug in seen:
            errors.append(f"{where}: duplicate slug")
        seen.add(slug)
    return errors, seen
