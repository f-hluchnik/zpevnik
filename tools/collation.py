"""Czech collation of song titles (DECISIONS D-107).

Implemented here, not with locale.strxfrm: locale collation depends on the
locales installed on the machine, so local runs and CI could disagree.

The key is compared in four passes, each only for entries equal so far:
 1. word by word (a space sorts before any letter), case and accents ignored
    except for c-caron, r-caron, s-caron, z-caron, which are letters of their
    own, and the digraph "ch" (a letter between h and i, in any title).
    Digits come after z-caron. Punctuation is ignored.
 2. the other accented letters (a-acute after a, e-acute and e-caron after e, ...).
 3. case: a lowercase letter before an uppercase one.
 4. punctuation, only to break a remaining tie.

Not covered by D-107 (decided here): letters that do not decompose into a
Latin letter and an accent are mapped by FOLD below (l-stroke sorts as l in
pass 1 and after l in pass 2); any other such letter raises an error, so a
new song cannot silently get a wrong position.

Python >= 3.11, standard library only.
"""
import unicodedata

# Pass 1 alphabet. "ch" is one letter; digits follow.
ALPHABET = ["a", "b", "c", "č", "d", "e", "f", "g", "h", "ch", "i", "j", "k", "l", "m",
            "n", "o", "p", "q", "r", "ř", "s", "š", "t", "u", "v", "w", "x", "y", "z", "ž"]
ALPHABET += list("0123456789")
WEIGHT = {letter: n for n, letter in enumerate(ALPHABET, start=1)}  # a space is 0

CARON = "̌"
FIRST_PASS_CARON = {"c", "r", "s", "z"}  # only these carons are first-pass letters

# Pass 2: rank of the accent on a letter. 0 = none. The Czech accents follow
# the alphabet order (a, á; e, é, ě; u, ú, ů); others come after, by mark.
ACCENT_ORDER = ["́", CARON, "̊"]  # acute, caron, ring
OTHER_ACCENT_BASE = 10

FOLD = {"ł": ("l", 1), "Ł": ("L", 1)}  # letter without decomposition: (base, accent rank)


def tokens(text: str) -> list[tuple[int, int, int]]:
    """(pass-1 weight, accent rank, upper) per letter, digit or space of the
    text: spaces collapsed, punctuation dropped, "ch" joined."""
    out: list[tuple[int, int, int]] = []
    pending_space = False
    for ch in text:
        if ch.isspace():
            pending_space = bool(out)  # no leading space
            continue
        base, rank = FOLD.get(ch, (None, 0))
        if base is None:
            d = unicodedata.normalize("NFD", ch)
            base, marks = d[0], d[1:]
            rank = 0
            if marks == CARON and base.lower() in FIRST_PASS_CARON:
                base = unicodedata.normalize("NFC", base + CARON)  # c-caron etc.
            elif marks:
                m = marks[0]
                rank = ACCENT_ORDER.index(m) + 1 if m in ACCENT_ORDER else OTHER_ACCENT_BASE + ord(m)
        if not base.isalnum():
            continue  # punctuation is ignored in the first three passes
        lower = base.lower()
        if lower not in WEIGHT:
            raise ValueError(f"cannot collate {ch!r}: add it to tools/collation.py")
        upper = int(base != lower)
        if pending_space:
            out.append((0, 0, 0))
            pending_space = False
        if lower == "h" and out and out[-1][0] == WEIGHT["c"] and out[-1][1] == 0:
            out[-1] = (WEIGHT["ch"], 0, out[-1][2])  # "ch": keep the case of the c
            continue
        out.append((WEIGHT[lower], rank, upper))
    return out


def sort_key(title: str) -> tuple:
    """Sort key of a plain-text title; sorted() gives the D-107 order."""
    t = tokens(title)
    return (tuple(x[0] for x in t),     # 1: letters
            tuple(x[1] for x in t),     # 2: accents
            tuple(x[2] for x in t),     # 3: case
            title)                      # 4: punctuation (the rest is equal)


def section(title: str) -> str:
    """First-pass letter of the title: the TOC letter section ("CH", no "Ď")."""
    first = tokens(title)[0][0]
    letter = ALPHABET[first - 1]
    if letter.isdigit():
        raise ValueError(f"title starts with a digit, no letter section: {title!r}")
    return letter.upper()
