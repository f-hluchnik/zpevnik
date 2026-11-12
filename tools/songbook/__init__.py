"""The converter: reads the LaTeX songs (songs/<id>.tex) into an in-memory model (D-164).

Strict: a command, an environment or a structure it does not know is an error with its
line (D-135, D-163), never a guess. `parse_song` reads one song from its source, `read_song`
one song file.

Python >= 3.11, standard library only.
"""
from pathlib import Path

from songbook.errors import SongSyntaxError
from songbook.model import Song
from songbook.parser import parse_song

__all__ = ["SongSyntaxError", "Song", "parse_song", "read_song"]


def read_song(path: Path) -> Song:
    """The song of a file `songs/<id>.tex`; SongSyntaxError for anything it does not accept."""
    return parse_song(path.stem, path.read_text(encoding="utf-8"))
