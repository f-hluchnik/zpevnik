"""Read one song file into a Song (model.py).

The song level follows TeX's modes as zpevnik.sty uses them: after an empty line
(vertical mode) a `\\cue`, `\\note` or `\\speaker` is a block of its own; after a part in
the same paragraph, whatever follows (a cue, "×2", a note) is appended to the part's
last line. Two parts in one paragraph are two blocks (D-163).

Python >= 3.11, standard library only.
"""
from dataclasses import dataclass, field, replace

from songbook import grammar
from songbook.errors import SongSyntaxError
from songbook.inline import IN_LABEL, IN_PART, IN_TITLE, SongState, read_lines, read_text
from songbook.lexer import DEPTH_CHANGE, Kind, Token, tokenize
from songbook.model import (ArtistRef, Block, BodyItem, CueBlock, Line, Note, Rule, RuleKind, SeeAlso, Song,
                            SpeakerBlock, Text, plain)
from songbook.stream import TokenStream, group_number, group_text

LINE_CARRIERS = (Block, SpeakerBlock)  # body items whose last line takes what follows in the paragraph


@dataclass
class SongBuilder:
    song_id: str
    state: SongState = field(default_factory=SongState)
    title: Text | None = None
    toc_title: str | None = None
    alt_titles: list[str] = field(default_factory=list)
    subtitle: Text | None = None
    artists: list[ArtistRef] = field(default_factory=list)
    collections: list[str] = field(default_factory=list)
    see: list[SeeAlso] = field(default_factory=list)
    columns: int = 1
    body: list[BodyItem] = field(default_factory=list)

    def song(self) -> Song:
        return Song(self.song_id, self.title, self.toc_title, tuple(self.alt_titles), self.subtitle,
                    tuple(self.artists), tuple(self.collections), tuple(self.see), self.columns,
                    tuple(self.state.footnotes), tuple(self.body))


class SongParser:
    def __init__(self, song_id: str, source: str):
        self.stream = TokenStream(tokenize(source))
        self.song = SongBuilder(song_id)
        self.vertical = True          # at the start of a paragraph
        self.carrier: int | None = None  # the body item the rest of the paragraph is appended to
        self.environments: list[tuple[str, int]] = []  # name and line of each \begin not closed yet

    def parse(self) -> Song:
        while not self.stream.at_end():
            token = self.stream.peek()
            if token.kind is Kind.PAR:
                self.stream.next()
                self.new_paragraph()
            elif token.kind is Kind.SPACE:
                self.stream.next()
            elif token.kind is Kind.COMMAND and token.text in SONG_LEVEL:
                self.stream.next()
                SONG_LEVEL[token.text](self, token)
            else:
                self.paragraph_text(self.take_paragraph_text())
        if self.environments:
            name, line = self.environments[-1]
            raise SongSyntaxError(line, f"\\begin{{{name}}} without \\end")
        if self.song.title is None:
            raise SongSyntaxError(1, "no \\song{...}")
        return self.song.song()

    def new_paragraph(self) -> None:
        self.vertical = True
        self.carrier = None

    def arguments(self, token: Token) -> list:
        return self.stream.arguments(token, SIGNATURES[token.text])

    # --- metadata ------------------------------------------------------------------------

    def title(self, token: Token) -> None:
        if self.song.title is not None:
            raise SongSyntaxError(token.line, "a second \\song")
        [content] = self.arguments(token)
        self.song.title = read_text(content, self.song.state, IN_TITLE, token)
        self.new_paragraph()  # a heading

    def subtitle(self, token: Token) -> None:
        [content] = self.arguments(token)
        self.song.subtitle = read_text(content, self.song.state, IN_TITLE, token)
        self.new_paragraph()

    def artist(self, token: Token) -> None:
        label, slug = self.arguments(token)
        slug = group_text(slug, token)
        if slug:  # \artist{}: no known artist
            self.song.artists.append(ArtistRef(slug, label))

    def alt_title(self, token: Token) -> None:
        [content] = self.arguments(token)
        self.song.alt_titles.append(plain(read_text(content, self.song.state, IN_LABEL, token)))

    def toc_title(self, token: Token) -> None:
        [content] = self.arguments(token)
        self.song.toc_title = plain(read_text(content, self.song.state, IN_LABEL, token))

    def collection(self, token: Token) -> None:
        [slug] = self.arguments(token)
        self.song.collections.append(group_text(slug, token))

    def see_also(self, token: Token) -> None:
        song_id, text = self.arguments(token)
        self.song.see.append(SeeAlso(group_text(song_id, token),
                                     read_text(text, self.song.state, IN_LABEL, token)))

    # --- the body ------------------------------------------------------------------------

    def block(self, token: Token) -> None:
        kind = grammar.BLOCKS[token.text]
        if token.text in grammar.UNNUMBERED_BLOCKS:
            number, (content,) = None, self.stream.arguments(token, grammar.UNNUMBERED_BLOCK_SIGNATURE)
        else:
            number, content = self.stream.arguments(token, grammar.BLOCK_SIGNATURE)
        lines = read_lines(content, self.song.state, IN_PART, token)
        block = Block(kind, number or None, tuple(lines))
        self.song.state.blocks[block.key] = len(self.song.body)
        self.add(block, carries_line=True)

    def rule(self, token: Token) -> None:
        signature, kind = grammar.RULES[token.text]
        self.stream.arguments(token, signature)  # the length of a dashed rule is layout
        self.add(Rule(kind), carries_line=False)
        if kind is RuleKind.SOLID:  # \partrule ends its paragraph
            self.new_paragraph()

    def add(self, item: BodyItem, carries_line: bool) -> None:
        self.song.body.append(item)
        self.carrier = len(self.song.body) - 1 if carries_line else None
        self.vertical = False

    def environment(self, token: Token) -> None:
        [name] = self.arguments(token)
        name = group_text(name, token)
        if token.text == "begin":
            self.begin(token, name)
        elif not self.environments or self.environments[-1][0] != name:
            raise SongSyntaxError(token.line, f"\\end{{{name}}} does not close the last \\begin")
        else:
            self.environments.pop()
        self.new_paragraph()

    def begin(self, token: Token, name: str) -> None:
        if name not in grammar.ENVIRONMENT_ARGUMENTS:
            raise SongSyntaxError(token.line, f"unknown environment {name}")
        arguments = self.stream.arguments(token, grammar.ENVIRONMENT_ARGUMENTS[name])
        if name == grammar.COLUMNS_ENVIRONMENT:
            self.song.columns = group_number(arguments[0], token)
        self.environments.append((name, token.line))

    def layout(self, token: Token) -> None:
        self.arguments(token)  # read and dropped: PDF-only

    # --- text in a paragraph, outside the parts --------------------------------------------

    def take_paragraph_text(self) -> list[Token]:
        """The tokens up to the end of the paragraph or the next song-level command."""
        start = self.stream.pos
        depth = 0
        while (token := self.stream.peek()) is not None:
            if depth == 0 and (token.kind is Kind.PAR or (token.kind is Kind.COMMAND and token.text in SONG_LEVEL)):
                break
            depth += DEPTH_CHANGE.get(token.kind, 0)
            self.stream.next()
        return self.stream.tokens[start:self.stream.pos]

    def paragraph_text(self, tokens: list[Token]) -> None:
        if self.vertical:
            self.standalone(tokens)
        elif self.carrier is None:
            raise SongSyntaxError(tokens[0].line, "text that follows no part in its paragraph: start a new paragraph")
        else:
            self.append_to_carrier(tokens, tokens[0])

    def standalone(self, tokens: list[Token]) -> None:
        """A paragraph that is not a part: a cue, a note or a speaker block."""
        stream = TokenStream(tokens)
        first = stream.next()
        if first.kind is not Kind.COMMAND or first.text not in grammar.MODE_DEPENDENT:
            raise SongSyntaxError(first.line, "text outside a part")
        arguments = stream.arguments(first, grammar.MODE_DEPENDENT[first.text])
        rest = tokens[stream.pos:]
        state = self.song.state
        if first.text == grammar.CUE:
            cue = state.cue(group_text(arguments[0], first), first.line)
            line = Line(()) if is_blank(rest) else self.one_line(rest, first)
            self.add(CueBlock(cue, line), carries_line=False)
        elif first.text == grammar.NOTE:
            if not is_blank(rest):
                raise SongSyntaxError(first.line, "text after a \\note: start a new paragraph")
            self.add(Note(read_text(arguments[0], state, IN_LABEL, first)), carries_line=False)
        else:
            name, content = arguments
            lines = read_lines(content, state, IN_PART, first)
            self.add(SpeakerBlock(group_text(name, first), tuple(lines)), carries_line=True)
            if not is_blank(rest):
                self.append_to_carrier(rest, first)

    def one_line(self, tokens: list[Token], command: Token) -> Line:
        lines = read_lines(tokens, self.song.state, IN_PART, command)
        if len(lines) != 1:
            raise SongSyntaxError(command.line, f"a line break after \\{command.text}: start a new paragraph")
        return lines[0]

    def append_to_carrier(self, tokens: list[Token], command: Token) -> None:
        """What follows a part in its paragraph goes on the part's last line."""
        if is_blank(tokens):
            return
        carrier = self.song.body[self.carrier]
        *kept, last = carrier.lines
        lines = read_lines(tokens, self.song.state, IN_PART, command, continued=last)
        self.song.body[self.carrier] = replace(carrier, lines=tuple(kept + lines))


def is_blank(tokens: list[Token]) -> bool:
    return all(token.kind is Kind.SPACE for token in tokens)


SONG_LEVEL = {
    "song": SongParser.title, "subtitle": SongParser.subtitle, "artist": SongParser.artist,
    "alttitle": SongParser.alt_title, "toctitle": SongParser.toc_title,
    "collection": SongParser.collection, "seealso": SongParser.see_also,
    **{name: SongParser.block for name in grammar.BLOCKS},
    **{name: SongParser.rule for name in grammar.RULES},
    **{name: SongParser.environment for name in grammar.ENVIRONMENT_COMMANDS},
    **{name: SongParser.layout for name in grammar.LAYOUT_COMMANDS},
}
SIGNATURES = grammar.METADATA | grammar.ENVIRONMENT_COMMANDS | grammar.LAYOUT_COMMANDS


def parse_song(song_id: str, source: str) -> Song:
    """The song of one file; SongSyntaxError for anything the converter does not accept."""
    return SongParser(song_id, source).parse()
