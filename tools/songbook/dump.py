"""The model as plain JSON values, for reading it and for the snapshot tests.

Not songs.json: that is the contract with the website and has its own shape (J2).
Every object carries its class name in "type"; enums are their values, styles a list of names.

Python >= 3.11, standard library only.
"""
from dataclasses import fields, is_dataclass
from enum import Enum

from songbook.model import Style

JsonValue = None | bool | int | str | list["JsonValue"] | dict[str, "JsonValue"]


def to_json(value: object) -> JsonValue:
    if isinstance(value, Style):
        return [style.name for style in Style if style and style in value]
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {"type": type(value).__name__} | {field.name: to_json(getattr(value, field.name))
                                                 for field in fields(value)}
    if isinstance(value, tuple | list):
        return [to_json(item) for item in value]
    return value
