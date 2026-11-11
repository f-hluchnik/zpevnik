"""The letter part of the table of contents.

`letters_tex` returns the letter row and the letter sections of shared-pages/contents.tex:
one `\\zpcontentsentry` (zpevnik.sty: a link on the screen, a dotted entry with the page on
paper) per song, in songbook order, and an italic entry for each alternative title, ordered by
that title under its own letter. The letter row and the link to the artist index only exist on the
screen: they jump somewhere.

Python >= 3.11, standard library only.
"""
import unicodedata
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from itertools import groupby

from collation import section, sort_key
from songs import Song
from tex_text import escape_tex, plain_text

ARTIST_INDEX_ANCHOR = "podleinterpreta"
ARTIST_INDEX_LINK = "řazení podle interpretů"


@dataclass(frozen=True)
class Entry:
    song_id: str
    text: str        # TeX, as printed in the contents
    sort_text: str   # plain text the entry is ordered by


TitleOf = Callable[[Song], str]


def contents_title(song: Song) -> str:
    """The title the letter sections list: the TOC title, if the song has one."""
    return song.sort_title


def entries(songs: list[Song], title_of: TitleOf = contents_title) -> Iterator[Entry]:
    """The entry of each song and one for each of its alternative titles."""
    for song in songs:
        title = title_of(song)
        yield Entry(song.id, escape_tex(title), title)
        for alttitle in map(plain_text, song.alttitles):
            yield Entry(song.id, f"\\emph{{{escape_tex(alttitle)}}} ({escape_tex(title)})", alttitle)


def anchor(letter: str) -> str:
    """Link target of a letter section: the letter, doubled for a letter with a
    caron (Č is Cc), so that it differs from the plain one."""
    if letter.isascii():
        return letter
    base = unicodedata.normalize("NFD", letter)[0]
    return base + base.lower()


def link_target(name: str) -> str:
    """A target of a link; on paper zpevnik.sty also labels it, so that its page can be printed."""
    return f"\\zptarget{{{name}}}"


def link(target: str, text: str) -> str:
    return f"\\hyperlink{{{target}}}{{{text}}}"


def entry_tex(target: str, text: str) -> str:
    """An entry of the contents: a link, with its page on paper."""
    return f"\\zpcontentsentry{{{target}}}{{{text}}}"


def sorted_entries(songs: list[Song], title_of: TitleOf = contents_title) -> list[Entry]:
    """The entries of the songs in songbook order (the song id breaks a tie)."""
    return sorted(entries(songs, title_of), key=lambda e: (sort_key(e.sort_text), e.song_id))


def letters_tex(songs: list[Song]) -> str:
    """The letter row, the link to the artist index and the letter sections."""
    ordered = sorted_entries(songs)
    sections = [(letter, list(group))
                for letter, group in groupby(ordered, key=lambda e: section(e.sort_text))]
    row = "\\hfill ".join(link(anchor(letter), letter) for letter, _ in sections)
    lines = [
        "\\begin{center}\n\\begin{Large}\n",
        f"\\zpscreenorprint{{{row}\n\\vspace{{5pt}}\n\n}}{{}}\n",
        f"\\zpscreenorprint{{{link(ARTIST_INDEX_ANCHOR, ARTIST_INDEX_LINK)}}}{{}}\n",
        "\\end{Large}\n\n\\zprule{10cm}\n\\end{center}\n\n\n",
        "\\begin{multicols}{2}\n",
    ]
    for letter, group in sections:
        lines.append(f"{link_target(anchor(letter))}\n\\subsection*{{{letter}}}\n")
        lines += [entry_tex(e.song_id, e.text) + "\n\n" for e in group]
    lines.append("\\end{multicols}\n")
    return "".join(lines)
