"""The error of a song the converter cannot read.

Python >= 3.11, standard library only.
"""


class SongSyntaxError(ValueError):
    """Something in a song the converter does not accept; `line` is its line in the file."""

    def __init__(self, line: int, message: str):
        super().__init__(f"line {line}: {message}")
        self.line = line
        self.message = message
