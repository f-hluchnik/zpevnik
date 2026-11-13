"""A song of the converter's model as songs.json carries it (D-164, D-165, J2).

songs.json is the contract with the website (tools/songs.schema.json, J3): semantic,
never layout, and fixed in shape. Every object in a list of mixed kinds has a "type";
every field is always present, null or empty when the song has nothing for it, so a
reader never needs a default. Text is what the PDF prints.

Python >= 3.11, standard library only.
"""
from collections.abc import Set

from songbook.grammar import GAP_UNIT_EM
from songbook.model import (Block, BodyItem, Chord, Cue, CueBlock, FootnoteRef, Gap, Line, Mark, Note, Remark,
                            RepeatEnd, RepeatStart, Rule, Run, Score, Segment, Song, Speaker, SpeakerBlock, Style,
                            Text)

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject = dict[str, JsonValue]
LineItem = Segment | Mark


def song_json(song: Song, page: int, song_ids: Set[str]) -> JsonObject:
    """The song as songs.json carries it; `page` is its page in the full book, `song_ids`
    the songs in songs.json (a \\seealso to any other song is left out, as in the books)."""
    return {
        "id": song.id,
        "title": text_json(song.title),
        "tocTitle": song.contents_title,
        "altTitles": list(song.alt_titles),
        "subtitle": text_json(song.subtitle) if song.subtitle is not None else None,
        "artists": [{"slug": artist.slug, "label": artist.label} for artist in song.artists],
        "collections": list(song.collections),
        "see": [{"id": see.song_id, "title": text_json(see.text)} for see in song.see if see.song_id in song_ids],
        "page": page,
        "columns": song.columns,
        "footnotes": [[text_json(line) for line in footnote] for footnote in song.footnotes],
        "body": [body_item_json(item) for item in song.body],
    }


def text_json(text: Text) -> list[JsonValue]:
    return [inline_json(item) for item in text]


def inline_json(item: Run | Gap | FootnoteRef) -> JsonObject:
    match item:
        case Run(text, style):
            return {"type": "run", "text": text, "style": style_names(style)}
        case Gap(units):
            return {"type": "gap", "em": units * GAP_UNIT_EM}
        case FootnoteRef(number):
            return {"type": "footnote", "number": number}
    raise TypeError(item)


def style_names(style: Style) -> list[JsonValue]:
    return [flag.name.lower() for flag in Style if flag and flag in style]


def chord_json(chord: Chord | None) -> JsonValue:
    if chord is None:
        return None
    return [{"text": part.text, "position": part.position.value} for part in chord.parts]


def body_item_json(item: BodyItem) -> JsonObject:
    match item:
        case Block(kind, number, lines):
            return {"type": "block", "kind": kind.name.lower(), "number": number, "label": item.label,
                    "lines": [line_json(line) for line in lines]}
        case SpeakerBlock(name, lines):
            return {"type": "speakerBlock", "name": name, "lines": [line_json(line) for line in lines]}
        case CueBlock(cue, line):
            return {"type": "cueBlock", "label": cue.printed_label, "line": line_json(line)}
        case Note(text):
            return note_json(text)
        case Remark(lines):
            return {"type": "remark", "lines": [text_json(text) for text in lines]}
        case Rule(kind):
            return {"type": "rule", "kind": kind.value}
    raise TypeError(item)


def note_json(text: Text) -> JsonObject:
    return {"type": "note", "content": text_json(text)}


def line_json(line: Line) -> JsonObject:
    items = line.items
    following = [*items[1:], None]
    return {"groupStart": line.group_start,
            "items": [line_item_json(item, after) for item, after in zip(items, following)]}


def line_item_json(item: LineItem, following: LineItem | None) -> JsonObject:
    match item:
        case Segment(chord, text):
            return {"type": "segment", "chord": chord_json(chord), "lyrics": text_json(text),
                    "endsInWord": isinstance(following, Segment) and following.in_word}
        case RepeatStart():
            return {"type": "repeatStart"}
        case RepeatEnd():
            return {"type": "repeatEnd"}
        case Cue():
            return {"type": "cue", "label": item.printed_label}
        case Note(text):
            return note_json(text)
        case Speaker(name):
            return {"type": "speaker", "name": name}
        case Score(name):
            return {"type": "score", "name": name}
    raise TypeError(item)
