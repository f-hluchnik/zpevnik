"""Songs for the tests, built by hand: the model of the converter with only what a test needs."""
from songbook.model import ArtistRef, Block, BlockKind, Line, Run, Score, Song


def make_song(song_id: str, title: str = "T", toc_title: str | None = None, *, alt_titles: tuple[str, ...] = (),
              artists: tuple[str, ...] = (), collections: tuple[str, ...] = (),
              scores: tuple[str, ...] = ()) -> Song:
    """A song with a plain title; its scores stand in one verse, one line each."""
    lines = tuple(Line((Score(name),)) for name in scores)
    return Song(song_id, (Run(title),), toc_title, alt_titles, artists=tuple(ArtistRef(slug) for slug in artists),
                collections=collections, body=(Block(BlockKind.VERSE, None, lines),) if lines else ())
