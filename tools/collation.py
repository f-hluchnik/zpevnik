"""Czech collation of song titles.

Implemented here, not with locale.strxfrm: locale collation depends on the
locales installed on the machine, so local runs and CI could disagree.

A title is compared in four passes, each only for titles equal so far:
 1. word by word (a space sorts before any letter), ignoring case, accents and
    punctuation, except that č, ř, š, ž are letters of their own and "ch" is
    one letter between h and i, in any title. Digits come after ž.
 2. the other accents (á after a; é, ě after e; ů after ú; ...).
 3. case: a lowercase letter before an uppercase one.
 4. punctuation, only to break a remaining tie.

Beyond the Czech rules, decided here: ł sorts as l in pass 1 and after l in
pass 2; any other accent sorts after the Czech ones, by code point; a letter
that is neither Latin nor in LETTER_WITHOUT_DECOMPOSITION raises an error,
so a new song cannot silently get a wrong position.

Python >= 3.11, standard library only.
"""
import unicodedata
from typing import NamedTuple

CARON = "̌"

# Pass 1 alphabet, in order. "ch" is one letter; digits follow.
ALPHABET = ("a b c č d e f g h ch i j k l m n o p q r ř s š t u v w x y z ž "
            "0 1 2 3 4 5 6 7 8 9").split()
SPACE_WEIGHT = 0
WEIGHT = {letter: n for n, letter in enumerate(ALPHABET, start=1)}

# Letters whose caron makes them a letter of their own (pass 1).
CARON_LETTERS = {"c", "r", "s", "z"}

# Pass 2: rank of an accent; 0 = none. Acute, caron, ring follow the Czech
# alphabet (a á; e é ě; u ú ů); any other accent comes after, by code point.
ACCENT_RANK = {"́": 1, CARON: 2, "̊": 3}
OTHER_ACCENT_RANK = 10

# Letters that do not decompose into a letter and an accent: (letter, accent rank).
LETTER_WITHOUT_DECOMPOSITION = {"ł": ("l", 1), "Ł": ("L", 1)}


class Token(NamedTuple):
    """One space, letter or digit of a title, as the passes compare it."""
    weight: int   # pass 1
    accent: int   # pass 2
    upper: bool   # pass 3


SPACE = Token(SPACE_WEIGHT, 0, False)


def split_accent(char: str) -> tuple[str, int]:
    """(letter, accent rank) of a character; a caron on c, r, s, z is kept in
    the letter, because those are letters of their own."""
    if char in LETTER_WITHOUT_DECOMPOSITION:
        return LETTER_WITHOUT_DECOMPOSITION[char]
    letter, *marks = unicodedata.normalize("NFD", char)
    if not marks:
        return letter, 0
    if marks == [CARON] and letter.lower() in CARON_LETTERS:
        return unicodedata.normalize("NFC", letter + CARON), 0
    mark = marks[0]
    return letter, ACCENT_RANK.get(mark, OTHER_ACCENT_RANK + ord(mark))


def tokens(text: str) -> list[Token]:
    """The text as tokens: spaces collapsed, punctuation dropped, "ch" joined."""
    result: list[Token] = []
    space_before = False
    for char in text:
        if char.isspace():
            space_before = bool(result)  # no space at the start
            continue
        letter, accent = split_accent(char)
        if not letter.isalnum():
            continue  # punctuation: only pass 4 sees it
        weight = WEIGHT.get(letter.lower())
        if weight is None:
            raise ValueError(f"cannot collate {char!r}: add it to tools/collation.py")
        token = Token(weight, accent, letter != letter.lower())
        if space_before:
            result.append(SPACE)
            space_before = False
        elif token.weight == WEIGHT["h"] and result and result[-1][:2] == (WEIGHT["c"], 0):
            result[-1] = result[-1]._replace(weight=WEIGHT["ch"])  # "c" + "h"
            continue
        result.append(token)
    return result


def sort_key(title: str) -> tuple:
    """Sort key of a plain-text title; sorted() gives the songbook order."""
    parts = tokens(title)
    return (tuple(t.weight for t in parts),   # pass 1
            tuple(t.accent for t in parts),   # pass 2
            tuple(t.upper for t in parts),    # pass 3
            title)                            # pass 4: the rest is equal, so punctuation


def section(title: str) -> str:
    """First-pass letter of the title, the TOC letter section: "CH" for "ch",
    never "Ď" (Ď sorts with D)."""
    letter = ALPHABET[tokens(title)[0].weight - 1]
    if letter.isdigit():
        raise ValueError(f"title starts with a digit, no letter section: {title!r}")
    return letter.upper()
