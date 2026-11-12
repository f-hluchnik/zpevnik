#!/usr/bin/env python3
"""The release of a build: one PDF per edition, what the website needs, and the release notes.

Every edition (a folder of editions/, see edition.py), the full book included, is released
as `zpevnik-<edition>-<version>.pdf` (D-143). A new edition is released without a change
here or in the CI. The PDFs are built by `make` into build/editions/<name>/; this copies
them under their asset names into build/release/ and prints the editions part of the
release notes (Markdown, in Czech like the site).

The website's build reads the release named in its version.txt (D-110), so the release also
holds `songs.json` and `scores.zip`, the score images (build/scores/*.svg) of the songs
(J4, D-166). Their names carry no version: the release's tag already does.

Usage: python3 tools/release.py VERSION [repo-root]
Python >= 3.11, standard library only.
"""
import argparse
import shutil
import sys
import zipfile
from pathlib import Path

from edition import EditionError, edition_names, read_book, read_edition
from paths import (BOOK_PDF_NAME, RELEASE_DIR, SCORE_OUTPUT_DIR, SONGS_JSON_FILE, add_root_argument,
                   edition_output_dir)
from registry import read_entries
from songs import published, read_songs

FEW_SONGS_MAX = 4  # Czech: 1 píseň, 2-4 písně, 5 and more písní
SONGS_JSON_ASSET = SONGS_JSON_FILE.name
SCORES_ASSET = "scores.zip"
SCORE_IMAGE_GLOB = "*.svg"  # the images for the web; the PDFs and .tex files beside them are for TeX
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)  # the earliest a zip can hold: the same scores give the same bytes


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


def zip_scores(root: Path, target: Path) -> None:
    """Write the score images (SVG, by name) into a zip with a fixed timestamp.
    FileNotFoundError if there are none: the scores were not exported (make scores)."""
    images = sorted((root / SCORE_OUTPUT_DIR).glob(SCORE_IMAGE_GLOB))
    if not images:
        raise FileNotFoundError(f"no score images in {SCORE_OUTPUT_DIR} (make scores)")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for image in images:
            info = zipfile.ZipInfo(image.name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, image.read_bytes())


def stage_web_assets(root: Path) -> list[Path]:
    """Copy songs.json and zip the score images into RELEASE_DIR; the paths of both.
    FileNotFoundError if either is not built (make json)."""
    songs_json = root / SONGS_JSON_FILE
    if not songs_json.is_file():
        raise FileNotFoundError(f"not built: {SONGS_JSON_FILE} (make json)")
    release_dir = root / RELEASE_DIR
    release_dir.mkdir(parents=True, exist_ok=True)
    staged_json = release_dir / SONGS_JSON_ASSET
    shutil.copyfile(songs_json, staged_json)
    staged_scores = release_dir / SCORES_ASSET
    zip_scores(root, staged_scores)
    return [staged_json, staged_scores]


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
        stage_web_assets(args.root)
        print(edition_notes(args.root, args.version))
    except (FileNotFoundError, EditionError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
