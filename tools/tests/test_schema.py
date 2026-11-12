"""songs.json against its schema (tools/songs.schema.json, J3): the contract with the website.

Needs jsonschema (requirements-dev.txt, D-165); the tools themselves do not.
Run from the repository root: python3 -m unittest discover -s tools
"""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from paths import REPO_ROOT
from songbook import parse_song, read_song
from songbook.export import song_json
from songs_json import SCHEMA_VERSION, songs_document
from validate_songs_json import MAX_MESSAGE_CHARS, file_problems, make_validator, problems, read_schema
from .test_songbook import SNAPSHOT_DIR
from .test_songs_json import SongsRepository

PAGE = 1


def schema() -> dict:
    return read_schema(REPO_ROOT)


def validator(definition: str | None = None) -> Draft202012Validator:
    return make_validator(schema(), definition)


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


class ValidatedFile(SongsRepository):
    """The tool CI runs on the real build/songs.json (J4)."""

    def setUp(self):
        super().setUp()
        self.build("alfa", "gama")
        self.path = Path(self.tmp.name) / "songs.json"

    def write(self, document: dict):
        self.path.write_text(json.dumps(document), encoding="utf-8")

    def test_a_valid_file_has_no_problems(self):
        self.write(songs_document(self.repo.root))
        self.assertEqual(file_problems(REPO_ROOT, self.path), [])

    def test_a_file_that_breaks_the_contract_is_reported_with_its_place(self):
        document = songs_document(self.repo.root)
        document["songs"][0]["page"] = "9"
        self.write(document)
        (problem,) = file_problems(REPO_ROOT, self.path)
        self.assertTrue(problem.startswith("songs/0/page: "), problem)

    def test_a_long_message_is_shortened(self):
        document = songs_document(self.repo.root)
        document["songs"][0]["body"][0]["type"] = "x" * 1000
        self.write(document)
        for problem in file_problems(REPO_ROOT, self.path):
            self.assertLessEqual(len(problem.split(": ", 1)[1]), MAX_MESSAGE_CHARS + len("..."))

    def test_a_missing_file_and_a_file_that_is_not_json_are_reported(self):
        self.assertIn("does not exist", file_problems(REPO_ROOT, self.path)[0])
        self.path.write_text("{", encoding="utf-8")
        self.assertIn("is not JSON", file_problems(REPO_ROOT, self.path)[0])


if __name__ == "__main__":
    unittest.main()
