"""Read the songs in pisnicky/*.tex (shared by the generators, D-107).

A song file has one `\\song{Title}`, optionally one `\\toctitle{TOC title}` and
any number of `\\alttitle{Other title}`, each at the start of a line.

Python >= 3.11, standard library only.
"""
import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from tex_text import brace_group, plain_text


@dataclass(frozen=True)
class Song:
    id: str                  # file name without .tex, as used in \include
    title: str               # \song, as written in TeX
    toctitle: str | None     # \toctitle, if the TOC and the order need another
    alttitles: tuple[str, ...] = ()  # \alttitle, other names the song is known by

    @cached_property
    def sort_title(self) -> str:
        """Plain text of the title that orders and lists the song (D-107)."""
        return plain_text(self.title if self.toctitle is None else self.toctitle)


def find_arguments(text: str, command: str) -> list[str]:
    """The arguments of every `\\command{...}` at the start of a line."""
    return [brace_group(text, m.end())[0]
            for m in re.finditer(r"^\\" + command + r"(?=\{)", text, re.M)]


def read_title(text: str, command: str, where: str) -> str | None:
    """The argument of the one `\\command{...}` at the start of a line, or None."""
    found = find_arguments(text, command)
    if len(found) > 1:
        raise ValueError(f"{where}: {len(found)} lines with \\{command}, expected at most 1")
    return found[0] if found else None


def read_songs(root: Path) -> list[Song]:
    """All songs in pisnicky/, in file-name order (not the songbook order)."""
    songs = []
    for path in sorted((root / "pisnicky").glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        title = read_title(text, "song", path.name)
        if title is None:
            raise ValueError(f"{path.name}: no \\song")
        songs.append(Song(path.stem, title, read_title(text, "toctitle", path.name),
                          tuple(find_arguments(text, "alttitle"))))
    return songs
