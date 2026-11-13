"""The artist part of the table of contents.

`artist_part_tex` returns the artist index, a column list of every artist that has a
section and a song in the edition, and the sections themselves: the songs of each artist in the order of
songbook order under the title of their page (the `\\toctitle` only tells songs of the same name
apart in the letter sections), with the alternative titles.
Which songs belong to an artist comes from the `\\artist` and `\\collection` tags
of the song files, not from a second list.

Python >= 3.11, standard library only.
"""
from collation import sort_key
from letter_toc import ARTIST_INDEX_ANCHOR, entry_tex, link_target, sorted_entries
from registry import Artist
from songbook import Song
from tex_text import escape_tex

COLLECTION = "collection"
COLUMNS = 2  # the index and the sections are both set in two columns
HEADING_BREAK = "\n"  # in a registry name: a forced line break in the section heading
INDEX_TO_SECTIONS_RULE = "\\begin{center}\\zprule{\\textwidth}\\end{center}\n"


def page_title(song: Song) -> str:
    """The title the artist sections list: the one printed on the song's page."""
    return song.page_title


def heading_tex(artist: Artist) -> str:
    return "\\\\".join(escape_tex(line) for line in artist["name"].split(HEADING_BREAK))


def members(artist: Artist, songs: list[Song]) -> list[Song]:
    return [song for song in songs if artist["slug"] in song.groups]


def book_order(artist: Artist) -> tuple:
    """Sort key of the artist index: by sort key, collections last."""
    return artist["kind"] == COLLECTION, sort_key(artist["sort"])


def ordered_artists(registry: list[Artist], songs: list[Song]) -> list[Artist]:
    """Artists with a section and a song among `songs`, in the order of the book (book_order).
    The full book's rules, so an edition never differs from it."""
    listed = (artist for artist in registry if artist["section"] and members(artist, songs))
    return sorted(listed, key=book_order)


def index_text(artist: Artist) -> str:
    """How the index names the artist: as the section heading ("Surname, First", so
    that it can be searched by surname); a collection uses its short label."""
    return artist["label"] if artist["kind"] == COLLECTION else artist["name"]


def index_tex(artists: list[Artist]) -> str:
    """The artist index: the link target of the letter part and one line per artist."""
    lines = [link_target(ARTIST_INDEX_ANCHOR) + "\n",
             "\\begin{Large}\n",
             f"\\begin{{multicols}}{{{COLUMNS}}}\\raggedright\n"]
    lines += [entry_tex(a["slug"], escape_tex(index_text(a))) + "\\par\n" for a in artists]
    lines.append("\\end{multicols}\n\\end{Large}\n")
    return "".join(lines)


def sections_tex(artists: list[Artist], songs: list[Song]) -> str:
    """One section per artist: heading, link target and a link for each entry."""
    # \raggedcolumns: a column that ends a page early keeps its natural spacing instead of
    # stretching the few gaps it has (an artist with one song) down to the bottom of the page.
    lines = [f"\\begin{{multicols}}{{{COLUMNS}}}\\raggedcolumns\n"]
    for artist in artists:
        lines.append(f"\\subsection*{{{heading_tex(artist)}}}\n{link_target(artist['slug'])}\n")
        lines += [entry_tex(e.song_id, e.text) + "\n\n" for e in sorted_entries(members(artist, songs), page_title)]
    lines.append("\\end{multicols}\n")
    return "".join(lines)


def artist_part_tex(registry: list[Artist], songs: list[Song]) -> str:
    """The index, a full-width rule and the sections. The contents start the index on a new page."""
    artists = ordered_artists(registry, songs)
    return index_tex(artists) + INDEX_TO_SECTIONS_RULE + sections_tex(artists, songs)
