#!/usr/bin/env python3
"""Migrate songs to the automatic chord spacing (ticket C3, D-123).

Usage: python3 tools/strip_chord_spacing.py [--dry-run] [--list] (--all | SONG_ID ...)

Run from the repository root. Edits pisnicky/<id>.tex in place; --dry-run only prints,
--list prints just the ids of the songs whose chords or spacing would change (it implies
--dry-run). Four steps per song:

1. A plain \\textbf{...} that holds only chord names becomes \\chords{...}.
2. A whole chord-only line (also inside \\intro{}, \\solo{}, ...) becomes \\chords{...}.
3. Each run of manual spacing (\\nc \\mm \\sm \\bc) is classified by where it stands:
   - after a chord, before lyrics: a pause (the chord is struck, then the singing starts)
     -> \\gap{n}; inside a word it is removed (no pause inside a word);
   - inside lyrics, at a line start or before \\chords, without a chord: a deliberate gap
     -> \\gap{n};
   - between chords or after the last chord of a line: removed (\\chordrunsep spaces them);
   - after lyrics, before a chord: removed (collision avoidance is automatic now).
     TeX swallows the space after a control word, so `je\\nc \\chord{Am}hojnost` had the
     macro as its only word gap. A space is kept when the author typed one after the macro
     or the character before is not a letter. Between two letters the owner's answers
     decide (JOINED_BY_OWNER, KEPT_APART_BY_OWNER), then the songbook itself: the gap is
     removed if the joined form is a word elsewhere in the book. Anything else keeps a
     space and is listed as CHECK: words are never joined on a guess.
   n is in characters of 0.5 em: \\sm = 1, \\mm = 2, \\nc = 4, \\bc = 8, summed over the run.
4. `\\autochords` is added right after the \\song{...} line.

Prints a summary and every \\gap, kept space, removal and conversion for review.
Python >= 3.11, standard library only.
"""
import re
import sys
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from chord_lists import chordify_lines, chordify_textbf
from chord_syntax import (
    AUTOCHORDS,
    CHORD,
    CHORD_AT_END,
    CHORD_START,
    ENDS_WITH_CONTROL_WORD,
    GAP_MACRO,
    INLINE_CHORDS_START,
    SPACING_RUN,
    SPACING_UNITS,
    ends_with_chord,
    has_autochords,
)
from migration_report import Report, clean, line_of
from word_decisions import Verdict, judge_pair

SONGS_DIR = Path("pisnicky")
CONTEXT_CHARS = 22  # source characters shown on each side of a change in the log
FRAGMENT_WINDOW = 200  # characters scanned for the letters next to a gap
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")
LETTERS_BEFORE_END = re.compile(r"[^\W\d_]+$")
LETTERS_AT_START = re.compile(r"[^\W\d_]+")

SONG_COMMAND = "\\song{"


class Kind(Enum):
    """Where a run of manual spacing stands."""
    CHORD_RUN = "run of chords"  # between chords or after the last chord of a line
    PAUSE = "pause"  # right after a chord, before lyrics
    BEFORE_CHORD = "before-chord"  # lyrics, then spacing, then a chord
    IN_LYRICS = "in-lyrics"  # no chord next to it, or before \chords
    LINE_START = "line-start"


# --- step 3: manual spacing ----------------------------------------------------------


def corpus(paths) -> set[str]:
    """Words of all songs, with chords removed and words touching spacing skipped."""
    words: set[str] = set()
    for path in paths:
        text = re.sub(r"(?<!\\)%.*", "", path.read_text(encoding="utf-8"))
        text = CHORD.sub("", text)
        text = GAP_MACRO.sub("\x00", SPACING_RUN.sub("\x00", text))
        text = re.sub(r"\\[A-Za-z]+|\\.|[{}]", " ", text)
        for token in text.split():
            if "\x00" not in token:
                words.update(w.lower() for w in WORD.findall(token))
    return words


def fragment(text: str, left: bool) -> str:
    """Letters next to a gap: the end of `text` (left) or its start. Chords inside the
    word are skipped, other manual spacing counts as a word boundary."""
    text = SPACING_RUN.sub("\x01", text[-FRAGMENT_WINDOW:] if left else text[:FRAGMENT_WINDOW])
    text = CHORD.sub("", text)
    text = re.sub(r"\\[A-Za-z]+|[{}]", "\x01", text)
    m = LETTERS_BEFORE_END.search(text) if left else LETTERS_AT_START.match(text)
    return m.group().lower() if m else ""


def classify(before: str, after: str) -> Kind:
    line_before = before.rsplit("\n", 1)[-1].strip()
    following = after.lstrip(" \t")
    at_line_end = following.startswith("\\\\") or following[:1] in ("\n", "}", "")
    if ends_with_chord(before):
        if CHORD_START.match(following) or at_line_end:
            return Kind.CHORD_RUN
        return Kind.PAUSE
    if CHORD_START.match(following) and not INLINE_CHORDS_START.match(following):
        return Kind.BEFORE_CHORD
    if not line_before or line_before.endswith("{"):
        return Kind.LINE_START
    return Kind.IN_LYRICS


def chord_inside_word(converted_before: str, after: str) -> bool:
    """Does the chord that ends `converted_before` stand between two letters? A control
    word such as \\dots before the chord is not a letter."""
    chords = CHORD_AT_END.search(converted_before)
    if not chords:
        return False
    stem = converted_before[:chords.start()]
    return stem[-1:].isalpha() and not ENDS_WITH_CONTROL_WORD.search(stem) and after[:1].isalpha()


def gap_width(run: str) -> int:
    return sum(SPACING_UNITS[unit] for unit in re.findall(r"\\(nc|mm|sm|bc)", run))


class Resolution(NamedTuple):
    """What replaces a run of manual spacing."""
    text: str
    label: str  # log label and statistics key
    detail: str = ""
    logged: bool = True


def gap(run: str, label: str, detail: str = "") -> Resolution:
    return Resolution(f"\\gap{{{gap_width(run)}}}", label, detail)


def resolve_pause(run: str, converted_before: str, after: str, words: set[str]) -> Resolution:
    """Spacing right after a chord, before lyrics: a pause (\\gap) unless the chord stands on
    a syllable, where no pause is wanted (D-123)."""
    if not chord_inside_word(converted_before, after):
        return gap(run, Kind.PAUSE.value)
    left, right = fragment(converted_before, True), fragment(after, False)
    pair = f"({left}|{right})"
    verdict, why = judge_pair(left, right, words)
    if verdict is Verdict.JOINED:
        return Resolution("", "pause inside a word", f"removed {pair}, {why}")
    if verdict is Verdict.UNKNOWN:
        return gap(run, "CHECK, pause between letters", f"kept as a \\gap, one word or two? {pair}")
    return gap(run, Kind.PAUSE.value)


def resolve_before_chord(run: str, prev: str, after: str, left: str, right: str, words: set[str]) -> Resolution:
    """Spacing between lyrics and a chord: collision avoidance, now automatic. A word gap
    that only the macro provided is kept as a space."""
    if prev in " \t\n{" or after[:1] in ("\n", "}", ""):
        return Resolution("", Kind.BEFORE_CHORD.value, logged=False)
    if re.search(r"[ \t]", run) or not prev.isalpha():
        return Resolution(" ", "kept a word space")
    pair = f"({left}|{right})"
    if not right:
        return Resolution("", "removed inside a word", f"{pair}, no letter follows")
    verdict, why = judge_pair(left, right, words)
    if verdict is Verdict.JOINED:
        return Resolution("", "removed inside a word", f"{pair}, {why}")
    if verdict is Verdict.SEPARATE:
        return Resolution(" ", "kept apart", f"{pair}, {why}")
    return Resolution(" ", "CHECK, kept a space", f"one word or two? {pair}")


def resolve(kind: Kind, run: str, before: str, after: str, converted_before: str, words: set[str]) -> Resolution:
    if kind is Kind.PAUSE:
        return resolve_pause(run, converted_before, after, words)
    if kind in (Kind.IN_LYRICS, Kind.LINE_START):
        return gap(run, kind.value)
    if kind is Kind.CHORD_RUN:
        return Resolution("", kind.value)
    return resolve_before_chord(run, before[-1:], after, fragment(before, True), fragment(after, False), words)


def strip_spacing(src: str, song: str, report: Report, words: set[str]) -> str:
    result, pos = "", 0
    for m in SPACING_RUN.finditer(src):
        before, after = src[:m.start()], src[m.end():]
        resolution = resolve(classify(before, after), m.group(), before, after, result + src[pos:m.start()], words)
        if resolution.logged:
            context = clean(src[max(0, m.start() - CONTEXT_CHARS):m.start()] + "[" + m.group().strip() + "]"
                            + after[:CONTEXT_CHARS])
            message = " ".join(part for part in (resolution.label, resolution.detail) if part)
            report.note(resolution.label, song, line_of(src, m.start()),
                        f"{message} -> {resolution.text}" if resolution.text.startswith("\\gap") else message,
                        context)
        else:
            report.stats[resolution.label] += 1
        result += src[pos:m.start()] + resolution.text
        pos = m.end()
    return result + src[pos:]


# --- step 4: the per-song switch ------------------------------------------------------


def closing_brace(text: str, opening: int) -> int:
    """Index of the brace that closes the one at `opening` (the end of the text if none)."""
    depth = 0
    for index in range(opening, len(text)):
        depth += {"{": 1, "}": -1}.get(text[index], 0)
        if depth == 0:
            return index
    return len(text)


def add_autochords(src: str) -> str:
    """Put \\autochords on its own line right after the line that closes \\song{...}."""
    start = src.find(SONG_COMMAND)
    if has_autochords(src) or start < 0:
        return src
    end = src.find("\n", closing_brace(src, start + len(SONG_COMMAND) - 1))
    end = len(src) if end < 0 else end
    return f"{src[:end]}\n{AUTOCHORDS}{src[end:]}"


# --- driver -------------------------------------------------------------------------


def convert(src: str, song: str, report: Report, words: set[str]) -> str:
    """The song with the chord spacing migrated, without the \\autochords line."""
    src = chordify_textbf(src, song, report)
    src = chordify_lines(src, song, report)
    return strip_spacing(src, song, report, words)


def main() -> int:
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith("--")}
    unknown = flags - {"--dry-run", "--list", "--all"}
    ids = [a for a in args if not a.startswith("--")]
    if "--all" in flags:
        ids = sorted(p.stem for p in SONGS_DIR.glob("*.tex"))
    if unknown or not ids:
        print(__doc__, file=sys.stderr)
        return 2

    report = Report()
    words = corpus(SONGS_DIR.glob("*.tex"))
    changed = []
    for song in ids:
        path = SONGS_DIR / f"{song}.tex"
        src = path.read_text(encoding="utf-8")
        converted = convert(src, song, report, words)
        if converted != src:
            changed.append(song)
        if not flags & {"--dry-run", "--list"}:
            path.write_text(add_autochords(converted), encoding="utf-8")
    if "--list" in flags:
        print("\n".join(changed))
        return 0
    print("\n".join(report.lines))
    print(", ".join(f"{k}: {v}" for k, v in report.stats.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
