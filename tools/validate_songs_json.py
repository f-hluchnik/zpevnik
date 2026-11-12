#!/usr/bin/env python3
"""Check songs.json against its schema, tools/songs.schema.json (J4, D-166).

The schema is the contract with the website (D-165), so the file a release publishes has to
satisfy it. The unit tests validate only some songs; this validates the whole file that
`make json` wrote, in about 5 s. CI runs it on every build, so a change that breaks the contract
fails its pull request, not the website's next build.

This is the one tool that needs a package, jsonschema (requirements-dev.txt, D-165): the tools
that build the book stay standard library.

Usage: python3 tools/validate_songs_json.py [--input PATH] [repo-root]   (default: build/songs.json)
Exit status 1 if the file is missing, is not JSON or breaks the schema.
"""
import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from paths import SONGS_JSON_FILE, SONGS_SCHEMA_FILE, add_root_argument

MAX_REPORTED = 20      # problems printed; a systematic mistake repeats in every song
MAX_MESSAGE_CHARS = 200  # jsonschema quotes the offending value, which can be a whole song
WHOLE_DOCUMENT = "(document)"  # the place of a problem that is not in any field


def read_schema(root: Path) -> dict:
    return json.loads((root / SONGS_SCHEMA_FILE).read_text(encoding="utf-8"))


def make_validator(schema: dict, definition: str | None = None) -> Draft202012Validator:
    """The validator of the whole document, or of one definition of $defs (a song, ...)."""
    if definition is None:
        return Draft202012Validator(schema)
    return Draft202012Validator({"$defs": schema["$defs"], "$ref": f"#/$defs/{definition}"})


def problems(validator: Draft202012Validator, value: object) -> list[str]:
    """What is wrong with the value: "path: message", the message shortened."""
    found = []
    for error in validator.iter_errors(value):
        message = error.message
        if len(message) > MAX_MESSAGE_CHARS:
            message = message[:MAX_MESSAGE_CHARS] + "..."
        place = "/".join(map(str, error.absolute_path)) or WHOLE_DOCUMENT
        found.append(f"{place}: {message}")
    return found


def file_problems(root: Path, path: Path) -> list[str]:
    """What is wrong with the songs.json at path; an empty list if it is valid."""
    if not path.is_file():
        return [f"{path} does not exist (make json builds it)"]
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"{path} is not JSON: {error}"]
    return problems(make_validator(read_schema(root)), document)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--input", type=Path, help=f"the file to check (default: {SONGS_JSON_FILE})")
    add_root_argument(parser)
    args = parser.parse_args()
    path = args.input or args.root / SONGS_JSON_FILE
    found = file_problems(args.root, path)
    if found:
        for problem in found[:MAX_REPORTED]:
            print(f"error: {problem}", file=sys.stderr)
        hidden = len(found) - MAX_REPORTED
        print(f"{path} breaks {SONGS_SCHEMA_FILE}; problems: {len(found)}"
              + (f" ({hidden} not shown)" if hidden > 0 else ""), file=sys.stderr)
        return 1
    print(f"{path}: valid against {SONGS_SCHEMA_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
