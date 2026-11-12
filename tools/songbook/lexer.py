"""Split the TeX source of a song into tokens, the way TeX reads it.

Only what the songs need: commands (control words and control symbols), braces,
brackets, math shifts, ties, text, spaces and paragraph breaks. TeX's rules for
white space are kept, because the songs rely on them (`F\\kk m` is one chord):
- after a control word (and after `\\ `), spaces and one end of line are skipped;
- a run of spaces with at most one end of line is one space;
- an empty line is a paragraph break, also right after a command or a comment;
- a comment drops the rest of its line, the end of line and the next line's indent.

Python >= 3.11, standard library only.
"""
from dataclasses import dataclass
from enum import Enum, auto

from songbook.errors import SongSyntaxError


class Kind(Enum):
    COMMAND = auto()      # text: the name without the backslash ("chord", "\\", "&")
    BEGIN_GROUP = auto()  # {
    END_GROUP = auto()    # }
    MATH = auto()         # $
    TIE = auto()          # ~
    TEXT = auto()         # ordinary characters; [ and ] are tokens of their own
    SPACE = auto()
    PAR = auto()          # an empty line


@dataclass(frozen=True)
class Token:
    kind: Kind
    text: str
    line: int
    swallowed_space: bool = False  # a control word followed by white space that TeX skipped


SINGLE_CHARACTERS = {"{": Kind.BEGIN_GROUP, "}": Kind.END_GROUP, "$": Kind.MATH, "~": Kind.TIE}
BRACKETS = "[]"
DEPTH_CHANGE = {Kind.BEGIN_GROUP: 1, Kind.END_GROUP: -1}  # how a token changes the brace depth
SPECIAL = set("\\%") | set(SINGLE_CHARACTERS) | set(BRACKETS)
BLANKS = " \t"
WHITE = BLANKS + "\n"
CONTROL_SPACE = " "
NEWLINES_OF_EMPTY_LINE = 2  # the end of a line, then an empty line


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens: list[Token] = []

    def run(self) -> list[Token]:
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char == "\\":
                self.command()
            elif char == "%":
                self.comment()
            elif char in WHITE:
                self.white_space()
            elif char in SINGLE_CHARACTERS:
                self.emit(SINGLE_CHARACTERS[char], char)
                self.pos += 1
            elif char in BRACKETS:
                self.emit(Kind.TEXT, char)
                self.pos += 1
            else:
                self.text()
        return self.tokens

    def emit(self, kind: Kind, text: str, swallowed_space: bool = False) -> None:
        self.tokens.append(Token(kind, text, self.line, swallowed_space))

    def command(self) -> None:
        start = self.pos + 1
        if start >= len(self.source):
            raise SongSyntaxError(self.line, "a backslash at the end of the file")
        end = start
        while end < len(self.source) and self.source[end].isascii() and self.source[end].isalpha():
            end += 1
        is_word = end > start
        name = self.source[start:end] if is_word else self.source[start]
        if name == "\n":
            raise SongSyntaxError(self.line, "a backslash at the end of a line")
        self.pos = end if is_word else start + 1
        skips_white = is_word or name == CONTROL_SPACE
        swallowed = skips_white and self.pos < len(self.source) and self.source[self.pos] in WHITE
        self.emit(Kind.COMMAND, name, swallowed)
        if skips_white:
            self.skip_white()

    def comment(self) -> None:
        end = self.source.find("\n", self.pos)
        if end == -1:
            self.pos = len(self.source)
            return
        self.pos = end  # the end of line belongs to the white space after the comment
        self.skip_white()

    def white_space(self) -> None:
        if not self.skip_white():
            self.emit(Kind.SPACE, " ")

    def skip_white(self) -> bool:
        """Skip white space and emit a paragraph break if it holds an empty line;
        True if it did."""
        line = self.line
        newlines = 0
        while self.pos < len(self.source) and self.source[self.pos] in WHITE:
            if self.source[self.pos] == "\n":
                newlines += 1
                self.line += 1
            self.pos += 1
        if newlines >= NEWLINES_OF_EMPTY_LINE:
            self.tokens.append(Token(Kind.PAR, "", line))
            return True
        return False

    def text(self) -> None:
        end = self.pos
        while end < len(self.source) and self.source[end] not in SPECIAL and self.source[end] not in WHITE:
            end += 1
        self.emit(Kind.TEXT, self.source[self.pos:end])
        self.pos = end


def tokenize(source: str) -> list[Token]:
    return Lexer(source).run()
