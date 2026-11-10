"""The generated TeX of an edition's front matter: its macros and its pages.

`macros_tex` defines the facts the shared pages print: the book's title, author, start
year and source, the edition's title, subtitle, editors and song count, the cover image,
and whether the edition is derived from the book (then the imprint prints the
derivation sentence instead of the plain version line). `pages_tex` defines the
pages zpevnik.tex puts into its fixed skeleton, resolved from edition.toml.
The macros are defined with \\newcommand* so that an empty one compares equal to \\empty.

Python >= 3.11, standard library only.
"""
from edition import COVER, HALFTITLE, TITLEPAGE, Book, Edition
from tex_text import escape_tex

URL_SCHEMES = ("https://", "http://")
EDITOR_SEPARATOR = ", "


def define(name: str, body: str) -> str:
    return f"\\newcommand*{{\\{name}}}{{{body}}}\n"


def source_text(url: str) -> str:
    """The source link as printed: without its scheme."""
    for scheme in URL_SCHEMES:
        url = url.removeprefix(scheme)
    return url


def macros_tex(book: Book, edition: Edition, song_count: int) -> str:
    derived = edition.name != book.base_edition
    return "".join([
        define("zpbooktitle", escape_tex(book.title)),
        define("zpbookauthor", escape_tex(book.author)),
        define("zpbookstartyear", str(book.start_year)),
        define("zpbooksource", book.source),
        define("zpbooksourcetext", escape_tex(source_text(book.source))),
        define("zpeditiontitle", escape_tex(edition.title)),
        define("zpeditionsubtitle", escape_tex(edition.subtitle or "")),
        define("zpeditioneditors", escape_tex(EDITOR_SEPARATOR.join(edition.editors))),
        define("zpeditionsongcount", str(song_count)),
        define("zpcoverimage", edition.cover_image or ""),
        "\\newif\\ifzpderived\n",
        "\\zpderivedtrue\n" if derived else "",
    ])


def includes(paths: tuple[str, ...]) -> str:
    return "".join(f"\\include{{{path}}}" for path in paths)


def pages_tex(edition: Edition) -> str:
    imprint = f"\\input{{{edition.imprint}}}" if edition.imprint else ""
    return "".join([
        define("zpcoverpage", includes((edition.pages[COVER],))),
        define("zphalftitlepage", includes((edition.pages[HALFTITLE],))),
        define("zptitlepage", includes((edition.pages[TITLEPAGE],))),
        define("zpimprintslot", imprint),
        define("zpbeforesongs", includes(edition.before_songs)),
        define("zpaftercontents", includes(edition.after_contents)),
    ])
