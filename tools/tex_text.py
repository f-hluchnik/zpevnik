"""Convert between TeX text, such as a song title, and plain Unicode text.

`plain_text`: footnotes are removed; `\\uv{}`, `\\textit{}` and accent macros are
resolved. A macro this module does not know is an error, not a guess.
`escape_tex`: plain text to TeX, escaping the special characters.

Python >= 3.11, standard library only.
"""
import re
import unicodedata

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


TEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\u00a0": "~",  # a non-breaking space in the registry is a tie in TeX
}


def escape_tex(text: str) -> str:
    """Plain text as TeX: every special character escaped."""
    return "".join(TEX_ESCAPES.get(ch, ch) for ch in text)
