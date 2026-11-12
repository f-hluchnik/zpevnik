"""Read the songs in songs/*.tex (shared by the generators).

A song file has one `\\song{Title}`, optionally one `\\toctitle{TOC title}` and
any number of `\\alttitle{Other title}`, each at the start of a line. The song
line carries its `\\artist{slug}` tags (up to two); `\\collection{slug}` is on
a line of its own. `\\score{name}` sets the image of `scores/<name>.mscz`.

A song listed in data/hidden.txt (L2) stays in the repository but is left out of
everything that is published: `published()` is the one place that applies the list.

Python >= 3.11, standard library only.
"""
import re
from dataclasses import dataclass
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path

from allowlist import read_allowlist
from paths import HIDDEN_SONGS, SONGS_DIR
from tex_text import brace_group, plain_text


ARTIST = re.compile(r"\\artist(?:\[[^\]]*\])?\{([^}]*)\}")  # \artist[label]{slug}
SCORE = re.compile(r"\\score\{([^}]*)\}")  # \score{name}: the image of scores/<name>.mscz


@dataclass(frozen=True)
class Song:
    id: str                  # file name without .tex, as used in \include
    title: str               # \song, as written in TeX
    toctitle: str | None     # \toctitle, if the TOC and the order need another
    alttitles: tuple[str, ...] = ()  # \alttitle, other names the song is known by
    artists: tuple[str, ...] = ()    # \artist slugs, empty ones left out
    collections: tuple[str, ...] = ()  # \collection slugs
    scores: tuple[str, ...] = ()       # \score names, in the order of the song

    @property
    def groups(self) -> tuple[str, ...]:
        """Registry slugs of the artist sections the song is listed under."""
        return tuple(dict.fromkeys(self.artists + self.collections))

    @cached_property
    def plain_title(self) -> str:
        """Plain text of the title printed on the song's page."""
        return plain_text(self.title)

    @cached_property
    def sort_title(self) -> str:
        """Plain text of the title that orders and lists the song."""
        return self.plain_title if self.toctitle is None else plain_text(self.toctitle)


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


def song_paths(root: Path) -> list[Path]:
    """The song files of songs/, in file-name order (not the songbook order)."""
    return sorted((root / SONGS_DIR).glob("*.tex"))


def parse_song(song_id: str, text: str) -> Song:
    """The song of one file; ValueError if it has no `\\song` or a metadata line is repeated."""
    where = song_id + ".tex"
    title = read_title(text, "song", where)
    if title is None:
        raise ValueError(f"{where}: no \\song")
    return Song(song_id, title, read_title(text, "toctitle", where),
                tuple(find_arguments(text, "alttitle")),
                tuple(slug for slug in ARTIST.findall(text) if slug),
                tuple(find_arguments(text, "collection")),
                tuple(SCORE.findall(text)))


def read_songs(root: Path) -> list[Song]:
    """All songs in songs/, in file-name order (not the songbook order)."""
    return [parse_song(path.stem, path.read_text(encoding="utf-8")) for path in song_paths(root)]


def published(songs: Iterable[Song], root: Path) -> list[Song]:
    """The songs that are not hidden (data/hidden.txt): every book and songs.json select from these."""
    hidden = read_allowlist(root / HIDDEN_SONGS)
    return [song for song in songs if song.id not in hidden]
