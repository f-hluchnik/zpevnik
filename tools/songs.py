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
from pathlib import Path

# TeX accent -> Unicode combining character.
SYMBOL_ACCENTS = {
    "'": "́", "`": "̀", '"': "̈", "^": "̂",
    "~": "̃", "=": "̄", ".": "̇",
}
WORD_ACCENTS = {
    "v": "̌", "c": "̧", "u": "̆", "H": "̋",
    "r": "̊", "k": "̨",
}
UNWRAP = {"uv", "textit", "textbf", "emph", "textsc", "textrm"}  # keep the argument
DROP = {"footnote"}                                              # drop the argument
ESCAPES = set("&%$#_{}")


@dataclass(frozen=True)
class Song:
    id: str            # file name without .tex, as used in \include
    title: str         # \song, as written in TeX
    toctitle: str | None

    @property
    def sort_title(self) -> str:
        """Plain text of the title that orders and lists the song (D-107)."""
        return plain_text(self.toctitle if self.toctitle is not None else self.title)


def group(text: str, i: int) -> tuple[str, int]:
    """The brace group starting at text[i] == '{': (content, index after it)."""
    depth = 0
    j = i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced braces: " + text[i:i + 40])


def argument(text: str, i: int) -> tuple[str, int]:
    """The argument of an accent macro at text[i]: {x}, or one character."""
    if i < len(text) and text[i] == "{":
        return group(text, i)
    if i < len(text) and text[i] == "\\":
        m = re.match(r"\\([A-Za-z]+|.)", text[i:])
        return m.group(0), i + len(m.group(0))
    if i < len(text):
        return text[i], i + 1
    raise ValueError("accent without a letter: " + text)


def plain_text(tex: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(tex):
        c = tex[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", tex[i:])
            if m:
                name = m.group(1)
                i += len(m.group(0))
                if name in DROP or name in UNWRAP:
                    while i < len(tex) and tex[i] == " ":
                        i += 1
                    content, i = group(tex, i)
                    if name in UNWRAP:
                        out.append(plain_text(content))
                elif name in WORD_ACCENTS:
                    while i < len(tex) and tex[i] == " ":
                        i += 1
                    arg, i = argument(tex, i)
                    out.append(unicodedata.normalize("NFC", plain_text(arg) + WORD_ACCENTS[name]))
                else:
                    raise ValueError(f"unknown macro \\{name} in title: {tex}")
                continue
            sym = tex[i + 1:i + 2]
            i += 2
            if sym in SYMBOL_ACCENTS:
                arg, i = argument(tex, i)
                out.append(unicodedata.normalize("NFC", plain_text(arg) + SYMBOL_ACCENTS[sym]))
            elif sym in ESCAPES:
                out.append(sym)
            elif sym in (" ", "\\"):
                out.append(" ")
            else:
                raise ValueError(f"unknown macro \\{sym} in title: {tex}")
        elif c == "~":
            out.append(" ")
            i += 1
        elif c in "{}":
            i += 1
        else:
            out.append(c)
            i += 1
    return unicodedata.normalize("NFC", "".join(out))


def read_title(text: str, command: str, where: str) -> str | None:
    found = [m.end() for m in re.finditer(r"^\\" + command + r"(?=\{)", text, re.M)]
    if len(found) > 1:
        raise ValueError(f"{where}: {len(found)} lines with \\{command}, expected at most 1")
    return group(text, found[0])[0] if found else None


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
