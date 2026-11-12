#!/usr/bin/env python3
"""Read every song with the converter (tools/songbook/) and report what it does not accept.

The converter is strict: an unknown command, a cue without a target, a line break at
the end of a part (D-163) is an error with its file and line. `make check` and CI run
this. `--song ID` prints the model of one song as JSON instead (for reading; songs.json
is J2).

Usage: python3 tools/convert.py [--song ID] [repo-root]
Exits 1 on errors. Python >= 3.11, standard library only.
"""
import argparse
import json
import sys
from pathlib import Path

from paths import SONGS_DIR, add_root_argument
from songbook import SongSyntaxError, read_song
from songbook.dump import to_json
from songs import song_paths

JSON_INDENT = 1


def check_all(root: Path) -> int:
    paths = song_paths(root)
    errors = []
    for path in paths:
        try:
            read_song(path)
        except SongSyntaxError as error:
            errors.append(f"{SONGS_DIR / path.name}:{error.line}: {error.message}")
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Converter: {len(paths)} songs, {len(errors)} error(s)")
    return 1 if errors else 0


def print_song(root: Path, song_id: str) -> int:
    path = root / SONGS_DIR / f"{song_id}.tex"
    if not path.is_file():
        print(f"error: no song {song_id} ({SONGS_DIR / path.name})", file=sys.stderr)
        return 1
    try:
        song = read_song(path)
    except SongSyntaxError as error:
        print(f"{SONGS_DIR / path.name}:{error.line}: {error.message}", file=sys.stderr)
        return 1
    print(json.dumps(to_json(song), ensure_ascii=False, indent=JSON_INDENT))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--song", metavar="ID", help="print the model of this song as JSON")
    add_root_argument(parser)
    args = parser.parse_args()
    return print_song(args.root, args.song) if args.song else check_all(args.root)


if __name__ == "__main__":
    sys.exit(main())
