"""A cursor over the tokens of a song, and reading a command's arguments by its signature.

Python >= 3.11, standard library only.
"""
from songbook.errors import SongSyntaxError
from songbook.lexer import DEPTH_CHANGE, Kind, Token

MANDATORY = "m"
OPTIONAL = "o"
STAR = "s"

Argument = list[Token] | str | bool | None  # m: tokens, o: text or None, s: present or not


class TokenStream:
    def __init__(self, tokens: list[Token], line: int = 1):
        self.tokens = tokens
        self.pos = 0
        self.last_line = tokens[-1].line if tokens else line

    def at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    def peek(self) -> Token | None:
        return None if self.at_end() else self.tokens[self.pos]

    def next(self) -> Token:
        token = self.peek()
        if token is None:
            raise SongSyntaxError(self.last_line, "unexpected end of the text")
        self.pos += 1
        return token

    def skip_spaces(self) -> None:
        while (token := self.peek()) is not None and token.kind is Kind.SPACE:
            self.pos += 1

    def arguments(self, command: Token, signature: str) -> list[Argument]:
        """The arguments of `command`; TeX skips spaces before each of them."""
        readers = {MANDATORY: self.group, OPTIONAL: self.optional, STAR: self.star}
        return [readers[letter](command) for letter in signature]

    def group(self, command: Token) -> list[Token]:
        """The tokens inside the `{...}` that comes next (without the braces)."""
        self.skip_spaces()
        token = self.peek()
        if token is None or token.kind is not Kind.BEGIN_GROUP:
            raise SongSyntaxError(command.line, f"\\{command.text} needs an argument in {{...}}")
        self.pos += 1
        return self.rest_of_group(token)

    def rest_of_group(self, opening: Token) -> list[Token]:
        """The tokens up to the `}` that closes `opening`, a `{` already read."""
        start = self.pos
        depth = 1
        while (token := self.peek()) is not None:
            self.pos += 1
            depth += DEPTH_CHANGE.get(token.kind, 0)
            if depth == 0:
                return self.tokens[start:self.pos - 1]
        raise SongSyntaxError(opening.line, "a { that is not closed")

    def optional(self, command: Token) -> str | None:
        """The text of a `[...]` argument, or None if there is none."""
        token = self.peek()
        if token is None or token.kind is not Kind.TEXT or token.text != "[":
            return None
        self.pos += 1
        parts: list[str] = []
        while (token := self.next()).text != "]":
            if token.kind not in (Kind.TEXT, Kind.SPACE):
                raise SongSyntaxError(token.line, f"the [...] argument of \\{command.text} must be plain text")
            parts.append(token.text)
        return "".join(parts).strip()

    def star(self, command: Token) -> bool:
        token = self.peek()
        if token is not None and token.kind is Kind.TEXT and token.text == "*":
            self.pos += 1
            return True
        return False


def group_text(tokens: list[Token], command: Token) -> str:
    """A `{...}` argument that must be plain text, such as a slug or a score name."""
    if any(token.kind not in (Kind.TEXT, Kind.SPACE) for token in tokens):
        raise SongSyntaxError(command.line, f"the argument of \\{command.text} must be plain text")
    return "".join(token.text for token in tokens).strip()


def group_number(tokens: list[Token], command: Token) -> int:
    """A `{...}` argument that must be a whole number, such as a repeat count."""
    text = group_text(tokens, command)
    if not text.isdigit():
        raise SongSyntaxError(command.line, f"\\{command.text} needs a whole number, not {text!r}")
    return int(text)

