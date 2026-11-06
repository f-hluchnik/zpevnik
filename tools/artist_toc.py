"""The artist part of the table of contents.

`artist_part_tex` returns the artist index, a column list of every artist that has a
section, and the sections themselves: the songs of each artist in the order of
songbook order under the title of their page (the `\\toctitle` only tells songs of the same name
apart in the letter sections), with the alternative titles.
Which songs belong to an artist comes from the `\\artist` and `\\collection` tags
of the song files, not from a second list.

Python >= 3.11, standard library only.
"""
from collation import sort_key
from letter_toc import ARTIST_INDEX_ANCHOR, link, sorted_entries
from registry import Artist
from songs import Song
from tex_text import escape_tex

COLLECTION = "collection"
COLUMNS = 2  # the index and the sections are both set in two columns
HEADING_BREAK = "\n"  # in a registry name: a forced line break in the section heading
INDEX_TO_SECTIONS_RULE = "\\begin{center}\\zprule{10cm}\\end{center}\n"


def page_title(song: Song) -> str:
    """The title the artist sections list: the one printed on the song's page."""
    return song.plain_title


def heading_tex(artist: Artist) -> str:
    return "\\\\".join(escape_tex(line) for line in artist["name"].split(HEADING_BREAK))


def ordered_artists(registry: list[Artist]) -> list[Artist]:
    """Artists with a section in the order of the book: by sort key, collections last."""
    with_section = (artist for artist in registry if artist["section"])
    return sorted(with_section, key=lambda a: (a["kind"] == COLLECTION, sort_key(a["sort"])))


def index_text(artist: Artist) -> str:
    """How the index names the artist: as the section heading ("Surname, First", so
    that it can be searched by surname); a collection uses its short label."""
    return artist["label"] if artist["kind"] == COLLECTION else artist["name"]


def index_tex(artists: list[Artist]) -> str:
    """The artist index: the link target of the letter part and one line per artist."""
    lines = [f"\\hyt{{{ARTIST_INDEX_ANCHOR}}}\n",
             "\\begin{Large}\n",
             f"\\begin{{multicols}}{{{COLUMNS}}}\\raggedright\n"]
    lines += [link(a["slug"], escape_tex(index_text(a))) + "\\par\n" for a in artists]
    lines.append("\\end{multicols}\n\\end{Large}\n")
    return "".join(lines)


def sections_tex(artists: list[Artist], songs: list[Song]) -> str:
    """One section per artist: heading, link target and a link for each entry."""
    lines = [f"\\begin{{multicols}}{{{COLUMNS}}}\n"]
    for artist in artists:
        members = [song for song in songs if artist["slug"] in song.groups]
        lines.append(f"\\subsection*{{{heading_tex(artist)}}}\n\\hyt{{{artist['slug']}}}\n")
        lines += [link(e.song_id, e.text) + "\n\n" for e in sorted_entries(members, page_title)]
    lines.append("\\end{multicols}\n")
    return "".join(lines)


def artist_part_tex(registry: list[Artist], songs: list[Song]) -> str:
    """The index, a rule and the sections."""
    artists = ordered_artists(registry)
    return index_tex(artists) + INDEX_TO_SECTIONS_RULE + sections_tex(artists, songs)
