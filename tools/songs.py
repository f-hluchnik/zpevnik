"""The songs in songs/*.tex, read by the converter (tools/songbook/, D-164).

The converter is the one reader of the song files: every tool that needs a song's
title, artists, collections or scores takes them from its model (`songbook.Song`).
This module adds what the model does not know: where the song files are, and which
songs are published.

A song listed in data/hidden.txt (L2) stays in the repository but is left out of
everything that is published: `published()` is the one place that applies the list.

Python >= 3.11, standard library only.
"""
from collections.abc import Iterable
from pathlib import Path

from allowlist import read_allowlist
from paths import HIDDEN_SONGS, SONGS_DIR
from songbook import Song, SongSyntaxError, read_song


class SongReadError(Exception):
    """A song file the converter does not accept; the message is `songs/<id>.tex:<line>: <what>`."""


def song_paths(root: Path) -> list[Path]:
    """The song files of songs/, in file-name order (not the songbook order)."""
    return sorted((root / SONGS_DIR).glob("*.tex"))


def read_song_file(path: Path) -> Song:
    """The song of one file; SongReadError if the converter rejects it."""
    try:
        return read_song(path)
    except SongSyntaxError as error:
        raise SongReadError(f"{SONGS_DIR / path.name}:{error.line}: {error.message}") from error


def read_songs(root: Path) -> list[Song]:
    """All songs in songs/, in file-name order (not the songbook order); SongReadError at the first
    file the converter rejects."""
    return [read_song_file(path) for path in song_paths(root)]


def published(songs: Iterable[Song], root: Path) -> list[Song]:
    """The songs that are not hidden (data/hidden.txt): every book and songs.json select from these."""
    hidden = read_allowlist(root / HIDDEN_SONGS)
    return [song for song in songs if song.id not in hidden]
