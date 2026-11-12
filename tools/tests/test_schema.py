"""songs.json against its schema (tools/songs.schema.json, J3): the contract with the website.

Needs jsonschema (requirements-dev.txt, D-165); the tools themselves do not.
Run from the repository root: python3 -m unittest discover -s tools
"""
import copy
import json
import unittest

from jsonschema import Draft202012Validator

from paths import REPO_ROOT, SONGS_SCHEMA_FILE
from songbook import parse_song, read_song
from songbook.export import song_json
from songs_json import SCHEMA_VERSION, songs_document
from .test_songbook import SNAPSHOT_DIR
from .test_songs_json import SongsRepository

PAGE = 1


def schema() -> dict:
    return json.loads((REPO_ROOT / SONGS_SCHEMA_FILE).read_text(encoding="utf-8"))


def validator(definition: str | None = None) -> Draft202012Validator:
    """The validator of the whole document, or of one definition of $defs (a song, ...)."""
    whole = schema()
    if definition is None:
        return Draft202012Validator(whole)
    return Draft202012Validator({"$defs": whole["$defs"], "$ref": f"#/$defs/{definition}"})


def problems(checker: Draft202012Validator, value: object) -> list[str]:
    return [f"{'/'.join(map(str, error.absolute_path))}: {error.message}" for error in checker.iter_errors(value)]


def rest_of_the_kinds() -> dict:
    """A song with every kind of item the snapshot songs do not have."""
    source = ("\\song{T\\footnote{n}} \\artist{a}\n\\subtitle{S}\n\\toctitle{T (a)}\n\\alttitle{U}\n"
              "\\seealso{other}{O}\n\n\\prechorus{H\\textsubscript{2}O in C\\kk{} dur}\n\n\\partrule\n\n"
              "\\speaker{A}{la}\n")
    return song_json(parse_song("test", source), PAGE, frozenset({"other"}))


def used(songs: list[dict]) -> set[str]:
    """Every item type, block or rule kind and style the songs use."""
    found: set[str] = set()
    def walk(value: object) -> None:
        if isinstance(value, dict):
            found.update(value[key] for key in ("type", "kind") if isinstance(value.get(key), str))
            found.update(value.get("style", []))
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(songs)
    return found


def declared() -> set[str]:
    """Every item type, block or rule kind and style the schema names."""
    definitions = schema()["$defs"]
    types = {definition["properties"]["type"]["const"] for definition in definitions.values()
             if "type" in definition.get("properties", {})}
    return (types | set(definitions["block"]["properties"]["kind"]["enum"])
            | set(definitions["rule"]["properties"]["kind"]["enum"])
            | set(definitions["run"]["properties"]["style"]["items"]["enum"]))


class Schema(unittest.TestCase):
    def test_the_schema_is_a_valid_json_schema_2020_12(self):
        Draft202012Validator.check_schema(schema())

    def test_it_names_the_schema_version_of_songs_json_py(self):
        self.assertEqual(schema()["properties"]["schemaVersion"], {"const": SCHEMA_VERSION})


class Songs(unittest.TestCase):
    """The frozen songs of the snapshot tests, chosen to hold every kind of item. The whole book
    takes about 5 s with jsonschema: CI validates the real songs.json instead (J4)."""

    def test_every_snapshot_song_is_valid(self):
        song = validator("song")
        for path in sorted(SNAPSHOT_DIR.glob("*.tex")):
            with self.subTest(path.stem):
                self.assertEqual(problems(song, song_json(read_song(path), PAGE, frozenset())), [])

    def test_a_song_with_what_the_snapshot_songs_lack_is_valid(self):
        self.assertEqual(problems(validator("song"), rest_of_the_kinds()), [])

    def test_the_songs_use_every_kind_and_style_of_the_schema(self):
        songs = [song_json(read_song(path), PAGE, frozenset()) for path in SNAPSHOT_DIR.glob("*.tex")]
        self.assertEqual(used(songs + [rest_of_the_kinds()]), declared())


class Document(SongsRepository):
    """A whole songs.json, from the small repository of test_songs_json."""

    def document(self) -> dict:
        self.build("alfa", "gama")
        return songs_document(self.repo.root)

    def test_an_assembled_document_is_valid(self):
        self.assertEqual(problems(validator(), self.document()), [])

    def test_what_breaks_the_contract_is_found(self):
        valid = self.document()
        breakages = {
            "a missing field": lambda d: d["songs"][0].pop("page"),
            "an unknown field": lambda d: d["songs"][0].update(order=1),
            "a wrong type": lambda d: d["songs"][0].update(page="9"),
            "an unknown kind of item": lambda d: d["songs"][0]["body"][0].update(type="paragraph"),
            "text as a plain string": lambda d: d["songs"][0].update(title="Alfa"),
            "another schema version": lambda d: d.update(schemaVersion=SCHEMA_VERSION + 1),
            "an id unsafe in a URL": lambda d: d["songs"][0].update(id="a b"),
        }
        for name, breakage in breakages.items():
            with self.subTest(name):
                broken = copy.deepcopy(valid)
                breakage(broken)
                self.assertNotEqual(problems(validator(), broken), [])


if __name__ == "__main__":
    unittest.main()
