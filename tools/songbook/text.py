"""The characters the PDF prints for a run of TeX text.

Python >= 3.11, standard library only.
"""
from songbook.grammar import LIGATURES


def printed_text(tex: str) -> str:
    """`tex` with TeX's ligatures replaced: `--` is an en dash, `'` a right quote, ..."""
    for ligature, character in LIGATURES:
        tex = tex.replace(ligature, character)
    return tex
