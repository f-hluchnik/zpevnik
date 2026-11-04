"""Read song titles from pisnicky/*.tex (shared by the generators, D-107).

A song file has one `\\song{Title}` and optionally `\\toctitle{TOC title}` at
the start of a line. `plain_text` turns a title into plain Unicode text: the
footnote is removed, accent macros and `\\uv{}` are resolved. Macros it does
not know are an error, not a guess.

Python >= 3.11, standard library only.
"""
import re
import unicodedata
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

# TeX accent macros -> Unicode combining characters.
SYMBOL_ACCENTS = {  # \'a  \`a  \"a  \^a  \~a  \=a  \.a
    "'": "́", "`": "̀", '"': "̈", "^": "̂",
    "~": "̃", "=": "̄", ".": "̇",
}
WORD_ACCENTS = {  # \v c  \c c  \u a  \H o  \r u  \k a
    "v": "̌", "c": "̧", "u": "̆", "H": "̋",
    "r": "̊", "k": "̨",
}
KEEP_ARGUMENT = {"uv", "textit", "textbf", "emph", "textsc", "textrm"}
DROP_ARGUMENT = {"footnote"}
ESCAPED_CHARS = set("&%$#_{}")

CONTROL_WORD = re.compile(r"\\([A-Za-z]+)")
CONTROL = re.compile(r"\\([A-Za-z]+|.)")


@dataclass(frozen=True)
class Song:
    id: str                  # file name without .tex, as used in \include
    title: str               # \song, as written in TeX
    toctitle: str | None     # \toctitle, if the TOC and the order need another

    @cached_property
    def sort_title(self) -> str:
        """Plain text of the title that orders and lists the song (D-107)."""
        return plain_text(self.title if self.toctitle is None else self.toctitle)


def brace_group(text: str, start: int) -> tuple[str, int]:
    """The `{...}` group at text[start]: (its content, the index after it)."""
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "\\":
            i += 2  # an escaped brace does not count
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    raise ValueError("unbalanced braces: " + text[start:start + 40])


def skip_spaces(text: str, i: int) -> int:
    while i < len(text) and text[i] == " ":
        i += 1
    return i


def accent_argument(text: str, i: int) -> tuple[str, int]:
    """What an accent macro applies to: a `{...}` group, a macro, or one character."""
    if text.startswith("{", i):
        return brace_group(text, i)
    if text.startswith("\\", i):
        macro = CONTROL.match(text, i)
        return macro.group(0), macro.end()
    if i < len(text):
        return text[i], i + 1
    raise ValueError("accent without a letter: " + text)


def accented(text: str, i: int, accent: str) -> tuple[str, int]:
    letter, end = accent_argument(text, i)
    return unicodedata.normalize("NFC", plain_text(letter) + accent), end


def plain_text(tex: str) -> str:
    """The title as plain text: footnotes dropped, `\\uv{}` and accents resolved."""
    out: list[str] = []
    i = 0
    while i < len(tex):
        char = tex[i]
        if char == "~":
            out.append(" ")
            i += 1
        elif char in "{}":
            i += 1
        elif char != "\\":
            out.append(char)
            i += 1
        elif word := CONTROL_WORD.match(tex, i):
            name, i = word.group(1), word.end()
            if name in KEEP_ARGUMENT | DROP_ARGUMENT:
                content, i = brace_group(tex, skip_spaces(tex, i))
                if name in KEEP_ARGUMENT:
                    out.append(plain_text(content))
            elif name in WORD_ACCENTS:
                text, i = accented(tex, skip_spaces(tex, i), WORD_ACCENTS[name])
                out.append(text)
            else:
                raise ValueError(f"unknown macro \\{name} in title: {tex}")
        else:
            symbol, i = tex[i + 1:i + 2], i + 2
            if symbol in SYMBOL_ACCENTS:
                text, i = accented(tex, i, SYMBOL_ACCENTS[symbol])
                out.append(text)
            elif symbol in ESCAPED_CHARS:
                out.append(symbol)
            elif symbol in (" ", "\\"):
                out.append(" ")
            else:
                raise ValueError(f"unknown macro \\{symbol} in title: {tex}")
    return unicodedata.normalize("NFC", "".join(out))


def read_title(text: str, command: str, where: str) -> str | None:
    """The argument of `\\command{...}` at the start of a line, or None."""
    found = [m.end() for m in re.finditer(r"^\\" + command + r"(?=\{)", text, re.M)]
    if len(found) > 1:
        raise ValueError(f"{where}: {len(found)} lines with \\{command}, expected at most 1")
    return brace_group(text, found[0])[0] if found else None


def read_songs(root: Path) -> list[Song]:
    """All songs in pisnicky/, in file-name order (not the songbook order)."""
    songs = []
    for path in sorted((root / "pisnicky").glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        title = read_title(text, "song", path.name)
        if title is None:
            raise ValueError(f"{path.name}: no \\song")
        songs.append(Song(path.stem, title, read_title(text, "toctitle", path.name)))
    return songs
