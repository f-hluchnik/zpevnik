"""The book facts (data/book.toml) and the editions (editions/<name>/edition.toml).

Every songbook is an edition, the full book too (`editions/full/`). An edition selects
songs and says which front-matter pages it shares (`shared-pages/<page>.tex`) and which
are its own (`editions/<name>/<page>.tex`); it can add an imprint fragment and pages
before the songs and after the contents. `read_book` and `read_edition` validate the
files and report every problem at once in an `EditionError`.

Files an edition lists are written relative to its folder; another edition's file is
named by path ("../full/introduction.tex"), so sharing is visible. A `.tex` file in the
folder that nothing references is an error, so a misspelt name never goes unnoticed.

Python >= 3.11, standard library only.
"""
import posixpath
import re
import tomllib
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from paths import BOOK_FILE, EDITION_FILE_NAME, EDITIONS_DIR, SHARED_PAGES_DIR
from songs import Song

SHARED, OWN = "shared", "own"
COVER, HALFTITLE, TITLEPAGE = "cover", "halftitle", "titlepage"
PAGES = (COVER, HALFTITLE, TITLEPAGE)  # the replaceable pages, each shared or own
TEX_SUFFIX = ".tex"
ALL, SONGS, ARTISTS = "all", "songs", "artists"  # the selection keys of edition.toml
EDITION_NAME = re.compile(r"[a-z0-9][a-z0-9-]*")  # used in paths and in file names
EDITION_FILE_DEPTH = len(("editions", "<name>", "<file>.tex"))  # no subfolders: see build_edition.py


@dataclass(frozen=True)
class Kind:
    """What a TOML value must be, for the error message and the check."""
    description: str
    accepts: Callable[[object], bool]


def is_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


TEXT = Kind("a non-empty string", is_text)
YEAR = Kind("an integer", lambda v: isinstance(v, int) and not isinstance(v, bool))
TRUE = Kind("true", lambda v: v is True)
TEXTS = Kind("a list of non-empty strings", lambda v: isinstance(v, list) and all(map(is_text, v)))
TABLE = Kind("a table", lambda v: isinstance(v, dict))
PAGE_CHOICE = Kind(f'"{SHARED}" or "{OWN}"', lambda v: v in (SHARED, OWN))

BOOK_KEYS = {"title": TEXT, "author": TEXT, "start_year": YEAR, "source": TEXT, "base_edition": TEXT}
EDITION_REQUIRED = {"before_songs": TEXTS, "after_contents": TEXTS, "pages": TABLE}
EDITION_OPTIONAL = {"title": TEXT, "subtitle": TEXT, "editors": TEXTS, "cover_image": TEXT,
                    "imprint": TEXT, ALL: TRUE, SONGS: TEXTS, ARTISTS: TEXTS}
PAGE_KEYS = {page: PAGE_CHOICE for page in PAGES}


class EditionError(Exception):
    """Every problem of a book or edition file, one message each."""

    def __init__(self, where: Path, errors: list[str]):
        super().__init__(f"{where} is invalid:\n  " + "\n  ".join(errors))
        self.where = where
        self.errors = errors


@dataclass(frozen=True)
class Book:
    """The facts every edition shares; no edition changes them."""
    title: str
    author: str
    start_year: int
    source: str        # a plain URL
    base_edition: str  # the edition that is the book itself (no derivation sentence)


@dataclass(frozen=True)
class Selection:
    """Every song, or the songs named by id and the songs of the named registry slugs."""
    every_song: bool
    song_ids: frozenset[str]
    slugs: frozenset[str]

    def selects(self, song: Song) -> bool:
        return self.every_song or song.id in self.song_ids or not self.slugs.isdisjoint(song.groups)


@dataclass(frozen=True)
class Edition:
    """An edition with its files resolved: TeX paths relative to the repository root,
    without the .tex suffix, as \\include and \\input take them."""
    name: str
    title: str
    subtitle: str | None
    editors: tuple[str, ...]
    pages: dict[str, str]           # page -> TeX path, for every page in PAGES
    cover_image: str | None         # with a shared cover only
    imprint: str | None             # TeX fragment above the imprint core
    before_songs: tuple[str, ...]
    after_contents: tuple[str, ...]
    selection: Selection

    def select(self, songs: Iterable[Song]) -> list[Song]:
        """The edition's songs, in the order given."""
        return [song for song in songs if self.selection.selects(song)]


def read_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def key_errors(table: dict, required: dict[str, Kind], optional: dict[str, Kind]) -> list[str]:
    """A missing or unknown key, and a value of the wrong kind."""
    errors = [f"missing key '{key}'" for key in required if key not in table]
    errors += [f"unknown key '{key}'" for key in sorted(table.keys() - required.keys() - optional.keys())]
    errors += [f"'{key}' must be {kind.description}"
               for key, kind in {**required, **optional}.items()
               if key in table and not kind.accepts(table[key])]
    return errors


def edition_folder(name: str) -> Path:
    return EDITIONS_DIR / name


def read_book(root: Path) -> Book:
    """data/book.toml, validated; its base edition must exist."""
    table = read_toml(root / BOOK_FILE)
    errors = key_errors(table, BOOK_KEYS, {})
    if not errors and not (root / edition_folder(table["base_edition"]) / EDITION_FILE_NAME).is_file():
        errors.append(f"base_edition '{table['base_edition']}' has no {EDITIONS_DIR}/<name>/{EDITION_FILE_NAME}")
    if errors:
        raise EditionError(BOOK_FILE, errors)
    return Book(**table)


def repo_path(folder: Path, reference: str) -> PurePosixPath:
    """A path written relative to `folder`, as a normalised path relative to the root."""
    return PurePosixPath(posixpath.normpath(posixpath.join(folder.as_posix(), reference)))


def tex_path(path: PurePosixPath) -> str:
    return str(path.with_suffix(""))


class EditionReader:
    """Validates one edition file against the repository, collecting every error."""

    def __init__(self, root: Path, name: str, table: dict):
        self.root = root
        self.folder = edition_folder(name)
        self.table = table
        self.errors: list[str] = []
        self.referenced: set[PurePosixPath] = set()

    def listed_file(self, reference: str, key: str) -> str:
        """A .tex file the edition lists, directly in an edition folder and existing; its TeX path."""
        path = repo_path(self.folder, reference)
        if (path.suffix != TEX_SUFFIX or path.parts[0] != EDITIONS_DIR.name
                or len(path.parts) != EDITION_FILE_DEPTH):
            self.errors.append(f"'{key}': {reference} must be a .tex file in an edition folder")
        elif not (self.root / path).is_file():
            self.errors.append(f"'{key}': {reference} does not exist")
        self.referenced.add(path)
        return tex_path(path)

    def listed_files(self, key: str) -> tuple[str, ...]:
        return tuple(self.listed_file(reference, key) for reference in self.table[key])

    def page(self, page: str, choice: str) -> str:
        if choice == SHARED:
            return tex_path(PurePosixPath(SHARED_PAGES_DIR.as_posix(), page + TEX_SUFFIX))
        return self.listed_file(page + TEX_SUFFIX, f"pages.{page}")

    def cover_image(self, cover: str) -> str | None:
        reference = self.table.get("cover_image")
        if cover == OWN:
            if reference is not None:
                self.errors.append("'cover_image' goes with a shared cover only")
            return None
        if reference is None:
            self.errors.append("a shared cover needs 'cover_image'")
            return None
        path = repo_path(self.folder, reference)
        if path.parts[:1] == ("..",) or not (self.root / path).is_file():
            self.errors.append(f"'cover_image': {reference} is not a file of the repository")
        return str(path)

    def selection(self, song_ids: set[str], slugs: set[str]) -> Selection:
        table = self.table
        every_song = table.get(ALL, False)
        chosen = {key for key in (SONGS, ARTISTS) if key in table}
        if every_song and chosen:
            self.errors.append(f"'{ALL}' goes without '{SONGS}' and '{ARTISTS}'")
        elif not every_song and not chosen:
            self.errors.append(f"no selection: give '{ALL} = true', or '{SONGS}' and/or '{ARTISTS}'")
        listed_ids, listed_slugs = table.get(SONGS, []), table.get(ARTISTS, [])
        self.errors += [f"'{SONGS}': unknown song id '{s}'" for s in listed_ids if s not in song_ids]
        self.errors += [f"'{ARTISTS}': unknown registry slug '{s}'" for s in listed_slugs if s not in slugs]
        return Selection(every_song, frozenset(listed_ids), frozenset(listed_slugs))

    def unreferenced(self) -> list[str]:
        own = (PurePosixPath(p.relative_to(self.root).as_posix())
               for p in (self.root / self.folder).glob("*" + TEX_SUFFIX))
        return [f"{path.name} is not referenced by {EDITION_FILE_NAME}"
                for path in sorted(own) if path not in self.referenced]


def read_edition(root: Path, name: str, book: Book, songs: list[Song], slugs: set[str]) -> Edition:
    """editions/<name>/edition.toml, validated against the songs and the registry slugs."""
    where = edition_folder(name) / EDITION_FILE_NAME
    if not EDITION_NAME.fullmatch(name):
        raise EditionError(where, [f"the edition name '{name}' must match {EDITION_NAME.pattern}"])
    if not (root / where).is_file():
        raise EditionError(where, ["no such file"])
    table = read_toml(root / where)
    errors = key_errors(table, EDITION_REQUIRED, EDITION_OPTIONAL)
    if "pages" in table and TABLE.accepts(table["pages"]):
        errors += [f"pages: {e}" for e in key_errors(table["pages"], PAGE_KEYS, {})]
    if errors:
        raise EditionError(where, errors)

    reader = EditionReader(root, name, table)
    edition = Edition(
        name=name,
        title=table.get("title", book.title),
        subtitle=table.get("subtitle"),
        editors=tuple(table.get("editors", [])),
        pages={page: reader.page(page, table["pages"][page]) for page in PAGES},
        cover_image=reader.cover_image(table["pages"][COVER]),
        imprint=reader.listed_file(table["imprint"], "imprint") if "imprint" in table else None,
        before_songs=reader.listed_files("before_songs"),
        after_contents=reader.listed_files("after_contents"),
        selection=reader.selection({song.id for song in songs}, slugs),
    )
    reader.errors += reader.unreferenced()
    if not reader.errors and not edition.select(songs):
        reader.errors.append("the selection has no songs")
    if reader.errors:
        raise EditionError(where, reader.errors)
    return edition


def edition_names(root: Path) -> list[str]:
    """Every edition folder of the repository."""
    return sorted(path.name for path in (root / EDITIONS_DIR).iterdir() if path.is_dir())


def edition_problems(root: Path, songs: list[Song], slugs: set[str]) -> list[str]:
    """Every problem of the book file and of every edition, one line each (for the lints)."""
    try:
        book = read_book(root)
    except EditionError as error:
        return [f"{error.where}: {message}" for message in error.errors]
    problems = []
    for name in edition_names(root):
        try:
            read_edition(root, name, book, songs, slugs)
        except EditionError as error:
            problems += [f"{error.where}: {message}" for message in error.errors]
    return problems
