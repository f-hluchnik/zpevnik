"""The letter part of the table of contents (ticket R10, DECISIONS D-107, D-116).

`letters_tex` returns the letter row and the letter sections of obsah.tex:
one `\\hylo` per song, in the order of D-107, and an italic entry for each
alternative title, ordered by that title under its own letter.

Python >= 3.11, standard library only.
"""
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import groupby

from collation import section, sort_key
from songs import Song
from tex_text import plain_text, tex

ARTIST_INDEX_ANCHOR = "podleinterpreta"
ARTIST_INDEX_LINK = "řazení podle interpretů"


@dataclass(frozen=True)
class Entry:
    song_id: str
    text: str        # TeX, as printed in the contents
    sort_text: str   # plain text the entry is ordered by


def entries(songs: list[Song]) -> Iterator[Entry]:
    """The entry of each song and one for each of its alternative titles."""
    for song in songs:
        title = song.sort_title
        yield Entry(song.id, tex(title), title)
        for alttitle in map(plain_text, song.alttitles):
            yield Entry(song.id, f"\\emph{{{tex(alttitle)}}} ({tex(title)})", alttitle)


def anchor(letter: str) -> str:
    """Link target of a letter section: the letter, doubled for a letter with a
    caron (Č is Cc), so that it differs from the plain one."""
    if letter.isascii():
        return letter
    base = unicodedata.normalize("NFD", letter)[0]
    return base + base.lower()


def link(target: str, text: str) -> str:
    return f"\\hylo{{{target}}}{{{text}}}"


def letters_tex(songs: list[Song]) -> str:
    """The letter row, the link to the artist index and the letter sections."""
    ordered = sorted(entries(songs), key=lambda e: (sort_key(e.sort_text), e.song_id))
    sections = [(letter, list(group))
                for letter, group in groupby(ordered, key=lambda e: section(e.sort_text))]
    row = "\\hfill ".join(link(anchor(letter), letter) for letter, _ in sections)
    lines = [
        "\\begin{center}\n\\begin{Large}\n",
        row + "\n",
        "\\vspace{5pt}\n\n",
        link(ARTIST_INDEX_ANCHOR, ARTIST_INDEX_LINK) + "\n",
        "\\end{Large}\n\n\\rule{10cm}{0.03cm}\n\\end{center}\n\n\n",
        "\\begin{multicols}{2}\n",
    ]
    for letter, group in sections:
        lines.append(f"\\hyt{{{anchor(letter)}}}\n\\subsection*{{{letter}}}\n")
        lines += [link(e.song_id, e.text) + "\n\n" for e in group]
    lines.append("\\end{multicols}\n")
    return "".join(lines)
