"""Plain text as TeX: `escape_tex` escapes the special characters.

Python >= 3.11, standard library only.
"""
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
    " ": "~",  # a non-breaking space in the registry is a tie in TeX
}


def escape_tex(text: str) -> str:
    """Plain text as TeX: every special character escaped."""
    return "".join(TEX_ESCAPES.get(ch, ch) for ch in text)
