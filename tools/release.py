#!/usr/bin/env python3
"""The release of a build: one PDF per edition, and the notes that list the editions.

Every edition (a folder of editions/, see edition.py), the full book included, is released
as `zpevnik-<edition>-<version>.pdf` (D-143). A new edition is released without a change
here or in the CI. The PDFs are built by `make` into build/editions/<name>/; this copies
them under their asset names into build/release/ and prints the editions part of the
release notes (Markdown, in Czech like the site).

Usage: python3 tools/release.py VERSION [repo-root]
Python >= 3.11, standard library only.
"""
import argparse
import shutil
import sys
from pathlib import Path

from edition import EditionError, edition_names, read_book, read_edition
from paths import BOOK_PDF_NAME, RELEASE_DIR, add_root_argument, edition_output_dir
from registry import read_entries
from songs import published, read_songs

FEW_SONGS_MAX = 4  # Czech: 1 píseň, 2-4 písně, 5 and more písní


def asset_name(edition: str, version: str) -> str:
    return f"zpevnik-{edition}-{version}.pdf"


def songs_phrase(count: int) -> str:
    """The song count with the Czech plural of "píseň"."""
    if count == 1:
        return "1 píseň"
    return f"{count} písně" if 2 <= count <= FEW_SONGS_MAX else f"{count} písní"


def edition_line(name: str, subtitle: str | None, song_count: int, asset: str) -> str:
    label = f"`{name}`" + (f" ({subtitle})" if subtitle else "")
    return f"- {label}: {songs_phrase(song_count)}, `{asset}`"


def stage_assets(root: Path, version: str) -> list[Path]:
    """Copy the PDF of every edition to RELEASE_DIR under its asset name; the copies' paths.
    FileNotFoundError, naming every edition that was not built, if any PDF is missing."""
    names = edition_names(root)
    pdfs = {name: root / edition_output_dir(name) / BOOK_PDF_NAME for name in names}
    missing = [name for name, pdf in pdfs.items() if not pdf.is_file()]
    if missing:
        raise FileNotFoundError(f"not built (make EDITION=<name>): {', '.join(missing)}")
    (root / RELEASE_DIR).mkdir(parents=True, exist_ok=True)
    staged = []
    for name, pdf in pdfs.items():
        target = root / RELEASE_DIR / asset_name(name, version)
        shutil.copyfile(pdf, target)
        staged.append(target)
    return staged


def edition_notes(root: Path, version: str) -> str:
    """The release notes' list of editions, with the song count of each."""
    entries = read_entries(root)
    all_songs = read_songs(root)
    songs = published(all_songs, root)
    book = read_book(root)
    slugs = {entry["slug"] for entry in entries}
    lines = []
    for name in edition_names(root):
        edition = read_edition(root, name, book, all_songs, slugs)
        lines.append(edition_line(name, edition.subtitle, len(edition.select(songs)),
                                  asset_name(name, version)))
    return "\n".join(["**Vydání**", *lines])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("version")
    add_root_argument(parser)
    args = parser.parse_args()
    try:
        stage_assets(args.root, args.version)
        print(edition_notes(args.root, args.version))
    except (FileNotFoundError, EditionError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
