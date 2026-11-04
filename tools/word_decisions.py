"""One word or two? Decisions about letters on both sides of a gap or a chord (D-123).

The owner's answers first, then the songbook itself; never a guess. Used by
strip_chord_spacing.py. Python >= 3.11, standard library only.
"""
from enum import Enum

# Gaps between two letters that the owner decided (D-123, docs/C1-review-lists.md): pairs
# of (letters left of the gap, letters right of it) as `fragment` reads them.
JOINED_BY_OWNER = frozenset({
    ("há", "ní"),  # pohání
    ("go", "li"), ("li", "áš"),  # Goliáš
    ("za", "va"),  # zavanou
    ("oře", "cha"),  # ořecha
    ("končí", "vaj"),  # končívaj
    ("wa", "sting"),  # wasting
    ("e", "motion"),  # emotion
    ("invisi", "ble"),  # invisible
    ("medecí", "na"),  # medecína
    ("dra", "ží"),  # naráží
    ("su", "chá"),  # suchá
    # pauses inside a word, in the songs D-123 names (a chord on a syllable, then a pause)
    ("to", "mu"),  # tomu (letadozravani)
    ("po", "há"), ("za", "mí"),  # pohání, zamíří (batalion)
    ("setmě", "lo"), ("nebu", "de"), ("krát", "ká"), ("berán", "ka"),  # bratrickuzavirejvratka
})
KEPT_APART_BY_OWNER = frozenset({
    ("sněhy", "za"), ("fare", "and"), ("ledový", "přinesl"), ("listopadový", "písni"),
    ("ráš", "rosu"), ("já", "panenku"), ("jen", "pouhý"), ("je", "soudný"),
    ("vadrovali", "po"),
})


class Verdict(Enum):
    """Do the letters on both sides of a gap belong to one word?"""
    JOINED = "joined"
    SEPARATE = "separate"
    UNKNOWN = "unknown"


def judge_pair(left: str, right: str, words: set[str]) -> tuple[Verdict, str]:
    """The owner's answers first, then the songbook itself; never a guess (D-123)."""
    if (left, right) in JOINED_BY_OWNER:
        return Verdict.JOINED, "owner's answer"
    if (left, right) in KEPT_APART_BY_OWNER:
        return Verdict.SEPARATE, "owner's answer"
    if left + right in words:
        return Verdict.JOINED, "the joined form is a word elsewhere"
    if left in words and right in words:
        return Verdict.SEPARATE, "both are words elsewhere"
    return Verdict.UNKNOWN, ""
