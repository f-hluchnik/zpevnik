#!/usr/bin/env python3
"""Lints for the songs and the artists registry.

Errors fail the build:
  - a registry entry is invalid (see registry.py);
  - a song has no `\\song`, or not exactly one line with `\\artist`, or more than
    two artists, or still uses `\\interpret`;
  - a song still uses the manual chord spacing `\\nc \\mm \\sm \\bc` (pauses are
    `\\gap{n}`, chord-only lines `\\chords{...}`);
  - a song still uses the old spacing `\\ns \\cns \\vnv \\vinv \\lsp` (the gap between blocks
    is automatic, see the README);
  - a song places or spaces something by hand (`\\includegraphics`, `\\vspace`, `\\hspace`) or
    writes an echo or repeat signs by hand (see HAND_WRITTEN_FORMS);
  - a song has text, `\\rec` or `\\chords` outside a block (a paragraph must start with a block or a separator);
  - a song has a block without text (`\\bridge{}`, `\\vers[3]{}`); a label alone is `\\cue{...}`;
  - a song still uses a renamed command (`\\refrain`, `\\sub`, `\\refsm`, ... see
    RENAMED_COMMANDS) or the old two-brace `\\vers{n}{...}`;
  - a song refers (`\\artist`, `\\collection`) to a slug that is not in the registry;
  - an entry with `section = true` has no songs;
  - a song sets `\\score{name}` and there is no `scores/<name>.mscz`.
Warnings are listed and do not fail:
  - a song has no `\\chord` or `\\chords`;
  - an artist without a section has MIN_SONGS_FOR_SECTION songs or more;
  - several songs have the same title in the contents and none tells them apart
    with a `\\toctitle`;
  - a `scores/<name>.mscz` is used by no song.
Info: how many songs have an empty `\\artist{}`.

Usage: python3 tools/lint.py [repo-root]
Exits 1 on errors. Python >= 3.11, standard library only.
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from paths import SCORES_DIR, add_root_argument
from registry import Artist, check_entries, normalise, read_entries
from songs import ARTIST, Song, parse_song, song_paths

MIN_SONGS_FOR_SECTION = 3  # an artist with this many songs or more gets a section
MAX_ARTISTS = 2            # per song, see \artist in zpevnik.sty
ARTIST_LINE = re.compile(r"\\artist\b")
OLD_MACRO = re.compile(r"\\interpret(?:dva)?\b")
MANUAL_SPACING = re.compile(r"\\(?:nc|mm|sm|bc)(?![A-Za-z])")  # replaced by \gap and \chords
OLD_SPACING = re.compile(r"\\(?:ns|cns|vnv|vinv|lsp)(?![A-Za-z])")  # the gap between blocks is automatic
# Commands that were renamed or replaced; the value is what to write instead.
RENAMED_COMMANDS = {
    "refrain": "\\chorus", "refrainn": "\\chorus[n]", "solon": "\\solo[n]", "cod": "\\coda",
    "sub": "\\subtitle", "spk": "\\speaker", "hyl": "\\seealso",
    "refsm": "\\cue{R}", "refsme": "\\cue{R}", "bridgesm": "\\cue{B}", "solosm": "\\cue{S}",
    "hyt": "\\hypertarget", "hylo": "\\hyperlink",
    "nv": "\\vers{...} (a block without a label)", "lbl": "\\speaker{A}{...} or \\cue{...}",
}
# LaTeX commands that do by hand what a song command or the style does; the value is the advice.
HAND_WRITTEN_FORMS = {
    "textsuperscript": "write \\echo{...} for an echo or backing vocals",
    "backslash": "write \\rep{...}", "textbackslash": "write \\rep{...}",
    "includegraphics": "write \\score{name} for scores/<name>.mscz",
    "vspace": "the gaps between blocks are automatic and scores place themselves",
    "hspace": "chord spacing is automatic (a pause is \\gap{n}) and scores place themselves",
}


def command_pattern(names: dict[str, str]) -> re.Pattern[str]:
    """Matches \\name for any of the names, not after a line break (\\\\name) and not as a prefix."""
    return re.compile(r"(?<!\\)\\(" + "|".join(names) + r")(?![A-Za-z])")


RENAMED_COMMAND = command_pattern(RENAMED_COMMANDS)
HAND_WRITTEN_FORM = command_pattern(HAND_WRITTEN_FORMS)
# A block without text only prints its label, which is what \cue is for. A second group after the
# empty one is text that was written next to the block instead of in it.
EMPTY_BLOCK = re.compile(r"\\(?:vers|chorus|bridge|prechorus|solo|intro|coda)(?:\[[^\]]*\])?\{\s*\}")
OLD_VERS = re.compile(r"\\vers\{[^{}]*\}\s*\{")  # \vers{n}{text}: the number is now \vers[n]{text}
COMMENT = re.compile(r"(?<!\\)%.*")
# What a paragraph outside braces may start with: the header, the blocks, the separators, column
# layout and scores. Anything else (text, \\rec, \\chords) belongs in a block, also inside an
# environment such as multicols.
PARAGRAPH_START = re.compile(r"\\([A-Za-z@]+)|[^\\\s]")
ALLOWED_PARAGRAPH_STARTS = frozenset(
    "song artist alttitle subtitle toctitle collection note cue speaker vers chorus prechorus bridge solo "
    "intro coda blockrule partrule groupbreak seealso large begin end columnbreak score "
    "hypertarget".split())
PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n")
ESCAPED_BRACE = re.compile(r"\\[{}]")
CHORD_USE = re.compile(r"\\chords?\b")


def text_outside_blocks(code: str) -> list[str]:
    """The first line of each paragraph outside braces that does not start with a block or a separator."""
    stray, braces = [], 0
    for paragraph in PARAGRAPH_BREAK.split(code):
        start = PARAGRAPH_START.match(paragraph.strip())
        if start and braces == 0 and start.group(1) not in ALLOWED_PARAGRAPH_STARTS:
            stray.append(paragraph.strip().splitlines()[0][:40])
        unescaped = ESCAPED_BRACE.sub("", paragraph)
        braces += unescaped.count("{") - unescaped.count("}")
    return stray


def text_problems(song_id: str, text: str) -> list[str]:
    """Problems of a song file that its parsed form does not show."""
    problems = []
    artist_lines = sum(1 for line in text.splitlines() if ARTIST_LINE.search(line))
    if artist_lines != 1:
        problems.append(f"{song_id}: {artist_lines} lines with \\artist, expected exactly 1")
    if OLD_MACRO.search(text):
        problems.append(f"{song_id}: still uses \\interpret / \\interpretdva")
    artists = len(ARTIST.findall(text))
    if artists > MAX_ARTISTS:
        problems.append(f"{song_id}: {artists} artists, at most {MAX_ARTISTS} are printed")
    spacing = len(MANUAL_SPACING.findall(text))
    if spacing:
        problems.append(f"{song_id}: {spacing} manual chord spacings (\\nc \\mm \\sm \\bc); "
                        "use \\gap{n} for a pause, \\chords{...} for a line of chords")
    old_spacing = len(OLD_SPACING.findall(COMMENT.sub("", text)))
    if old_spacing:
        problems.append(f"{song_id}: {old_spacing} uses of the removed spacing macros "
                        "(\\ns \\cns \\vnv \\vinv \\lsp); the gap between blocks is automatic")
    code = COMMENT.sub("", text)
    for name, count in Counter(RENAMED_COMMAND.findall(code)).items():
        problems.append(f"{song_id}: {count} uses of the removed \\{name}; write {RENAMED_COMMANDS[name]}")
    for name, count in Counter(HAND_WRITTEN_FORM.findall(code)).items():
        problems.append(f"{song_id}: {count} uses of \\{name}; {HAND_WRITTEN_FORMS[name]}")
    old_vers = len(OLD_VERS.findall(code))
    if old_vers:
        problems.append(f"{song_id}: {old_vers} uses of the old \\vers{{n}}{{text}}; write \\vers[n]{{text}}")
    empty_blocks = len(EMPTY_BLOCK.findall(code))
    if empty_blocks:
        problems.append(f"{song_id}: {empty_blocks} blocks without text; a label alone is \\cue{{...}}")
    for line in text_outside_blocks(code):
        problems.append(f"{song_id}: text outside a block ({line!r}); put it in \\vers{{...}}")
    return problems


def chord_warnings(song_id: str, text: str) -> list[str]:
    return [] if CHORD_USE.search(text) else [f"{song_id}: no \\chord or \\chords"]


def songs_by_group(songs: list[Song]) -> dict[str, list[Song]]:
    """The songs of each registry slug they are tagged with (`\\artist`, `\\collection`)."""
    groups: dict[str, list[Song]] = defaultdict(list)
    for song in songs:
        for slug in song.groups:
            groups[slug].append(song)
    return groups


def unknown_slugs(songs: list[Song], registry: list[Artist]) -> list[str]:
    known = {artist["slug"] for artist in registry}
    return [f"unknown slug '{slug}' used by {len(users)} song(s), e.g. {users[0].id}"
            for slug, users in sorted(songs_by_group(songs).items()) if slug not in known]


def empty_sections(songs: list[Song], registry: list[Artist]) -> list[str]:
    groups = songs_by_group(songs)
    return [f"entry '{a['slug']}' has a section (section = true) but no songs"
            for a in registry if a["section"] and a["slug"] not in groups]


def artists_ready_for_section(songs: list[Song], registry: list[Artist],
                              minimum: int = MIN_SONGS_FOR_SECTION) -> list[str]:
    groups = songs_by_group(songs)
    return [f"entry '{a['slug']}' has no section but {len(groups[a['slug']])} songs "
            f"(a section from {minimum})"
            for a in registry if not a["section"] and len(groups.get(a["slug"], [])) >= minimum]


def duplicate_titles(songs: list[Song]) -> list[str]:
    by_title: dict[str, list[Song]] = defaultdict(list)
    for song in songs:
        by_title[song.sort_title.casefold()].append(song)
    return [f"{len(same)} songs are listed as '{same[0].sort_title}' ({', '.join(s.id for s in same)}): "
            "tell them apart with \\toctitle"
            for same in by_title.values() if len(same) > 1]


def score_names(root: Path) -> set[str]:
    return {path.stem for path in (root / SCORES_DIR).glob("*.mscz")}


def unknown_scores(songs: list[Song], available: set[str]) -> list[str]:
    return [f"{song.id}: \\score{{{name}}} has no {SCORES_DIR}/{name}.mscz"
            for song in songs for name in song.scores if name not in available]


def unused_scores(songs: list[Song], available: set[str]) -> list[str]:
    used = {name for song in songs for name in song.scores}
    return [f"{SCORES_DIR}/{name}.mscz is used by no song" for name in sorted(available - used)]


def empty_artist_info(songs: list[Song]) -> str:
    without = [song for song in songs if not song.artists]
    in_collection = sum(1 for song in without if song.collections)
    return f"{len(without)} songs have an empty \\artist{{}} ({in_collection} of them are in a collection)"


def load_songs(root: Path) -> tuple[list[Song], list[str], list[str]]:
    """Every readable song, and the problems and warnings of all song files."""
    songs, problems, warnings = [], [], []
    for path in song_paths(root):
        text = path.read_text(encoding="utf-8")
        problems += text_problems(path.stem, text)
        warnings += chord_warnings(path.stem, text)
        try:
            songs.append(parse_song(path.stem, text))
        except ValueError as error:
            problems.append(str(error))
    return songs, problems, warnings


@dataclass
class Findings:
    errors: list[str]
    warnings: list[str]
    info: str


def lint(root: Path) -> Findings:
    entries = read_entries(root)
    errors = check_entries(entries)
    songs, problems, warnings = load_songs(root)
    errors += problems
    if not errors:  # the lints below need valid entries and readable songs
        registry = [normalise(entry) for entry in entries]
        errors += unknown_slugs(songs, registry) + empty_sections(songs, registry)
        warnings += artists_ready_for_section(songs, registry) + duplicate_titles(songs)
    available_scores = score_names(root)
    errors += unknown_scores(songs, available_scores)
    warnings += unused_scores(songs, available_scores)
    return Findings(errors, warnings, empty_artist_info(songs))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_root_argument(parser)
    findings = lint(parser.parse_args().root)
    for line in findings.warnings:
        print(f"warning: {line}")
    for line in findings.errors:
        print(f"error: {line}")
    print(f"info: {findings.info}")
    print(f"{len(findings.errors)} error(s), {len(findings.warnings)} warning(s)")
    return 1 if findings.errors else 0


if __name__ == "__main__":
    sys.exit(main())
