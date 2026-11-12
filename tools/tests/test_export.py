"""Unit tests of songs.json's shape of a song (tools/songbook/export.py).

Run from the repository root: python3 -m unittest discover -s tools
"""
import json
import re
import unittest

from paths import REPO_ROOT
from songbook import parse_song, read_song
from songbook.export import song_json
from songbook.grammar import GAP_UNIT_EM
from songs import song_paths

PAGE = 7
GAPUNIT = re.compile(r"\\newcommand\*\{\\gapunit\}\{([\d.]+)em\}")
LAYOUT = re.compile(r"[\\{}]")  # TeX markup must never reach songs.json


def exported(body: str, header: str = "", known: frozenset[str] = frozenset({"other"})) -> dict:
    return song_json(parse_song("test", f"\\song{{Title}} \\artist{{abba}}\n{header}\n{body}\n"), PAGE, known)


def first_line_items(body: str) -> list[dict]:
    return exported(body)["body"][0]["lines"][0]["items"]


def strings(value: object):
    """Every string in a JSON value, keys included."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)


class SongFields(unittest.TestCase):
    def test_every_field_is_present_even_when_empty(self):
        song = exported("\\vers{a}")
        self.assertEqual(list(song), ["id", "title", "tocTitle", "altTitles", "subtitle", "artists", "collections",
                                      "see", "page", "columns", "footnotes", "body"])
        self.assertEqual((song["subtitle"], song["altTitles"], song["footnotes"], song["page"]), (None, [], [], PAGE))
        self.assertEqual(song["artists"], [{"slug": "abba", "label": None}])

    def test_the_toc_title_is_the_title_without_a_toctitle(self):
        self.assertEqual(exported("\\vers{a}")["tocTitle"], "Title")
        self.assertEqual(exported("\\vers{a}", "\\toctitle{Title (abba)}")["tocTitle"], "Title (abba)")

    def test_a_see_also_to_a_song_not_in_songs_json_is_left_out(self):
        song = exported("\\vers{a}", "\\seealso{other}{Other}\n\\seealso{hidden}{Hidden}")
        self.assertEqual(song["see"], [{"id": "other", "title": [{"type": "run", "text": "Other", "style": []}]}])


class Body(unittest.TestCase):
    def test_a_part_has_its_kind_number_and_printed_label(self):
        block = exported("\\vers[2]{a}\n\n\\chorus{b}")["body"]
        self.assertEqual([(b["kind"], b["number"], b["label"]) for b in block], [("verse", "2", "2."), ("chorus", None, "R.")])

    def test_a_cue_prints_its_label_and_names_no_position(self):
        body = exported("\\chorus{a} \\cue{R}\n\n\\cue{R} \\ntimes{2}")["body"]
        self.assertEqual(body[0]["lines"][0]["items"][-1], {"type": "cue", "label": "R."})
        self.assertEqual(body[1]["type"], "cueBlock")
        self.assertEqual((body[1]["label"], body[1]["line"]["items"][0]["lyrics"][0]["text"]), ("R.", "×2"))

    def test_notes_speakers_rules_and_scores(self):
        body = exported("\\note{capo 2}\n\n\\speaker{A}{la}\n\n\\partrule\n\n\\vers{\\score{s}}")["body"]
        self.assertEqual(body[0], {"type": "note", "content": [{"type": "run", "text": "capo 2", "style": []}]})
        self.assertEqual((body[1]["type"], body[1]["name"]), ("speakerBlock", "A"))
        self.assertEqual(body[2], {"type": "rule", "kind": "solid"})
        self.assertEqual(body[3]["lines"][0]["items"], [{"type": "score", "name": "s"}])


class Lines(unittest.TestCase):
    def test_a_segment_is_a_chord_and_its_lyrics(self):
        [segment] = first_line_items("\\vers{\\chord{F\\kk m}la}")
        self.assertEqual(segment, {"type": "segment", "chord": [{"text": "F", "position": "base"},
                                                                {"text": "♯", "position": "superscript"},
                                                                {"text": "m", "position": "base"}],
                                   "lyrics": [{"type": "run", "text": "la", "style": []}], "endsInWord": False})

    def test_ends_in_word_marks_the_segment_before_a_chord_inside_a_word(self):
        items = first_line_items("\\vers{slip a\\chord{A}way \\chord{B}home}")
        self.assertEqual([item["endsInWord"] for item in items], [True, False, False])

    def test_a_gap_is_its_length_in_em(self):
        [segment] = first_line_items("\\vers{a\\gap{3}b}")
        self.assertEqual(segment["lyrics"][1], {"type": "gap", "em": 1.5})

    def test_the_gap_unit_is_zpevnik_sty_s(self):
        sty = (REPO_ROOT / "zpevnik.sty").read_text(encoding="utf-8")
        self.assertEqual(float(GAPUNIT.search(sty).group(1)), GAP_UNIT_EM)

    def test_marks_styles_and_footnotes(self):
        items = first_line_items("\\vers{\\rep{\\echo{a\\footnote{n}}} \\speaker{B}{b}}")
        self.assertEqual([item["type"] for item in items], ["repeatStart", "segment", "repeatEnd", "segment", "speaker",
                                                            "segment"])
        self.assertEqual(items[1]["lyrics"], [{"type": "run", "text": "a", "style": ["echo"]},
                                              {"type": "footnote", "number": 1}])


class WholeBook(unittest.TestCase):
    def test_no_tex_markup_reaches_songs_json(self):
        for path in song_paths(REPO_ROOT):
            song = song_json(read_song(path), PAGE, frozenset())
            with self.subTest(path.stem):
                self.assertEqual([text for text in strings(song) if LAYOUT.search(text)], [])
                json.dumps(song)  # every value is JSON


if __name__ == "__main__":
    unittest.main()
