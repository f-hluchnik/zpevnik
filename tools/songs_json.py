#!/usr/bin/env python3
"""Write songs.json: the songs of the full book for the website (J2, D-165).

The website shows the full book only. songs.json holds its songs in book order, each
read by the converter (tools/songbook/, export.py has the shape of one song) with its
page in the built full book; the letter contents and the artist index as the book lists
them, so the website never sorts; and the version of the build. Hidden songs are left
out with the function every book uses (songs.published, D-161).

Build the full book first (`make json` does both): the pages come from its .aux files,
and a build of other songs than these is an error.

Usage: python3 tools/songs_json.py [--output PATH] [repo-root]   (default: build/songs.json)
Python >= 3.11, standard library only.
"""
import argparse
import json
import sys
from collections.abc import Callable
from itertools import groupby
from operator import attrgetter
from pathlib import Path

import songs as metadata
from artist_toc import HEADING_BREAK, book_order, members, page_title
from build_version import build_patch
from check_pages import song_pages
from collation import section
from generate import InputError, ordered, read_inputs, version
from letter_toc import Entry, sorted_entries
from paths import DEFAULT_EDITION, SONGS_DIR, SONGS_JSON_FILE, add_root_argument, edition_output_dir
from registry import Artist, normalise
from songbook import Song, SongSyntaxError, read_song
from songbook.export import JsonObject, song_json

SCHEMA_VERSION = 1  # raise it with every change a reader of songs.json has to follow
WEBSITE_EDITION = DEFAULT_EDITION  # the full book: the website is built from no other edition
SongsById = dict[str, Song]
TitleOf = Callable[[Song], str]
CONTENTS_TITLE: TitleOf = attrgetter("contents_title")  # what the letter contents list
PAGE_TITLE: TitleOf = attrgetter("page_title")          # what the artist sections list


class SongsJsonError(Exception):
    """The full book is not built or was built from other songs, or the converter rejects a song."""


def book_pages(root: Path, song_ids: list[str]) -> dict[str, int]:
    """The first page of each song in the built full book; SongsJsonError unless the book holds
    exactly these songs in this order."""
    built, errors = song_pages(root / edition_output_dir(WEBSITE_EDITION))
    if errors:
        raise SongsJsonError("the full book is not built (make json builds it): " + "; ".join(errors))
    if [song_id for song_id, _, _ in built] != song_ids:
        raise SongsJsonError("the full book was built from other songs than these: build it again (make json)")
    return {song_id: first_page for song_id, first_page, _ in built}


def entry_json(entry: Entry, songs: SongsById, title_of: TitleOf) -> JsonObject:
    """An entry of the contents or of an artist: the song's title, or one of its other titles."""
    song = songs[entry.song_id]
    alternative = entry.alt_index is not None
    title = song.alt_titles[entry.alt_index] if alternative else title_of(song)
    return {"id": song.id, "title": title, "alternative": alternative}


def contents_json(book_songs: list[metadata.Song], songs: SongsById) -> list[JsonObject]:
    """The letter sections of the contents, each with its entries in book order."""
    entries = sorted_entries(book_songs)
    return [{"letter": letter, "entries": [entry_json(entry, songs, CONTENTS_TITLE) for entry in group]}
            for letter, group in groupby(entries, key=lambda entry: section(entry.sort_text))]


def artist_json(artist: Artist, book_songs: list[metadata.Song], songs: SongsById) -> JsonObject:
    entries = sorted_entries(members(artist, book_songs), page_title)
    return {"slug": artist["slug"], "name": artist["name"].replace(HEADING_BREAK, " "), "label": artist["label"],
            "linkLabel": artist["link_label"], "kind": artist["kind"], "section": artist["section"],
            "entries": [entry_json(entry, songs, PAGE_TITLE) for entry in entries]}


def artists_json(registry: list[dict], book_songs: list[metadata.Song], songs: SongsById) -> list[JsonObject]:
    """Every registry entry a song names, in the order of the artist index."""
    named = sorted((artist for artist in map(normalise, registry) if members(artist, book_songs)), key=book_order)
    return [artist_json(artist, book_songs, songs) for artist in named]


def read_converted(root: Path, song_ids: list[str]) -> SongsById:
    songs = {}
    for song_id in song_ids:
        path = SONGS_DIR / f"{song_id}.tex"
        try:
            songs[song_id] = read_song(root / path)
        except SongSyntaxError as error:
            raise SongsJsonError(f"{path}:{error.line}: {error.message}") from error
    return songs


def songs_document(root: Path) -> JsonObject:
    """songs.json; InputError or SongsJsonError if it cannot be made."""
    inputs = read_inputs(root, WEBSITE_EDITION)
    book_songs = ordered(inputs.songs)
    song_ids = [song.id for song in book_songs]
    pages = book_pages(root, song_ids)
    songs = read_converted(root, song_ids)
    linkable = set(song_ids)  # a \seealso to any other song is left out, as in the book
    return {
        "schemaVersion": SCHEMA_VERSION,
        "version": version(len(inputs.all_songs), build_patch(root)),
        "songs": [song_json(songs[song_id], pages[song_id], linkable) for song_id in song_ids],
        "contents": contents_json(book_songs, songs),
        "artists": artists_json(inputs.entries, book_songs, songs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--output", type=Path, help=f"where to write it (default: {SONGS_JSON_FILE})")
    add_root_argument(parser)
    args = parser.parse_args()
    try:
        document = songs_document(args.root)
    except (InputError, SongsJsonError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    output = args.output or args.root / SONGS_JSON_FILE
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{output}: {len(document['songs'])} songs, version {document['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
