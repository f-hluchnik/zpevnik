"""Read the text of a part (or of a title, a note, a footnote) into lines.

A line is segments and marks. A segment is a chord and the text after it; it ends at
the next chord, at the end of the line, at a mark, or at the end of the TeX group the
chord stands in, as `\\chord` in zpevnik.sty measures it. Spaces are collapsed and trimmed
at both ends of a line, as TeX typesets them. What a context does not allow (a chord in
a footnote, a line break in a title) is an error.

Python >= 3.11, standard library only.
"""
from dataclasses import dataclass, field

from songbook import grammar
from songbook.chords import check_dropped_space, chord_symbol_parts, parse_chord, split_chord_row
from songbook.errors import SongSyntaxError
from songbook.lexer import Kind, Token
from songbook.model import (Chord, ChordPosition, Cue, FootnoteRef, Gap, Inline, Line, Mark, Note, RepeatEnd, RepeatStart, Run,
                            Score, Segment, Speaker, Style, Text)
from songbook.stream import TokenStream, group_number, group_text
from songbook.text import printed_text


@dataclass(frozen=True)
class Allowed:
    """What a piece of text may contain."""
    line_breaks: bool  # \\ (and \groupbreak with music)
    music: bool        # chords, cues, repeats, scores, notes, speakers
    footnotes: bool


IN_PART = Allowed(line_breaks=True, music=True, footnotes=True)
IN_FOOTNOTE = Allowed(line_breaks=True, music=False, footnotes=False)
IN_TITLE = Allowed(line_breaks=False, music=False, footnotes=True)
IN_LABEL = Allowed(line_breaks=False, music=False, footnotes=False)  # a note, a link text, a name

CHORD_SYMBOL_STYLES = {ChordPosition.BASE: Style.PLAIN, ChordPosition.SUPERSCRIPT: Style.SUPERSCRIPT,
                       ChordPosition.SUBSCRIPT: Style.SUBSCRIPT}


@dataclass
class SongState:
    """What the parts of one song share while it is read."""
    footnotes: list[tuple[Text, ...]] = field(default_factory=list)
    blocks: dict[str, int] = field(default_factory=dict)  # block key -> index in the body of its last block

    def add_footnote(self, lines: tuple[Text, ...]) -> int:
        self.footnotes.append(lines)
        return len(self.footnotes)

    def cue(self, label: str, line: int) -> Cue:
        if label not in self.blocks:
            raise SongSyntaxError(line, f"\\cue{{{label}}} refers to no part with that label written before it")
        return Cue(label, self.blocks[label])


@dataclass
class OpenSegment:
    chord: Chord | None
    text: list[Inline] = field(default_factory=list)


class InlineParser:
    def __init__(self, state: SongState, allowed: Allowed, continued: Line | None = None):
        self.state = state
        self.allowed = allowed
        self.lines: list[Line] = []
        self.items: list[Segment | Mark] = list(continued.items) if continued else []
        self.group_start = continued.group_start if continued else False
        self.segment: OpenSegment | None = None
        # A space is kept only after something else than a space; the start of a line counts as one.
        self.after_space = not self.items

    # --- reading -------------------------------------------------------------------------

    def read(self, tokens: list[Token], style: Style = Style.PLAIN) -> None:
        stream = TokenStream(tokens)
        while not stream.at_end():
            token = stream.next()
            if token.kind is Kind.TEXT:
                self.add_text(printed_text(token.text), style)
            elif token.kind is Kind.SPACE:
                self.add_text(" ", style)
            elif token.kind is Kind.TIE:
                self.add_text(grammar.TIE, style)
            elif token.kind is Kind.MATH:
                self.add_text(self.math(stream, token), style)
            elif token.kind is Kind.BEGIN_GROUP:
                self.read_group(stream.rest_of_group(token), style)
            elif token.kind is Kind.PAR:
                raise SongSyntaxError(token.line, "an empty line inside a part: a new line is \\\\")
            elif token.kind is Kind.COMMAND:
                self.command(stream, token, style)
            else:
                raise SongSyntaxError(token.line, f"unexpected {token.text!r}")

    def read_group(self, tokens: list[Token], style: Style) -> None:
        """A TeX group: a chord that starts inside it does not reach past its end."""
        before = self.segment
        self.read(tokens, style)
        if self.segment is not before and self.segment is not None and self.segment.chord is not None:
            self.close_segment()

    def math(self, stream: TokenStream, opening: Token) -> str:
        parts: list[str] = []
        while (token := stream.next()).kind is not Kind.MATH:
            if token.kind is Kind.COMMAND and token.text in grammar.MATH_SYMBOLS:
                parts.append(grammar.MATH_SYMBOLS[token.text])
            elif token.kind is not Kind.SPACE:
                raise SongSyntaxError(opening.line, "math may only hold " +
                                      ", ".join("\\" + name for name in grammar.MATH_SYMBOLS))
        return "".join(parts)

    def command(self, stream: TokenStream, token: Token, style: Style) -> None:
        name = token.text
        if name in grammar.TEXT_SYMBOLS:
            self.add_text(grammar.TEXT_SYMBOLS[name], style)
        elif name in grammar.STYLES:
            [content] = stream.arguments(token, grammar.TEXT_COMMANDS[name])
            self.read_group(content, style | grammar.STYLES[name])
        elif name in grammar.QUOTES:
            self.quote(stream, token, style)
        elif name == grammar.FOOTNOTE:
            self.footnote(stream, token)
        elif name == grammar.TIMES:
            [count] = stream.arguments(token, grammar.TEXT_COMMANDS[name])
            self.add_text(grammar.TIMES_SIGN + str(group_number(count, token)), style)
        elif name in grammar.LINE_BREAKS:
            self.line_break(token)
        elif name in grammar.PART_COMMANDS:
            self.require(self.allowed.music, token, "only in a part")
            self.music(stream, token, style)
        elif name in grammar.CHORD_COMMANDS:  # a chord named in the text, not played
            for part in chord_symbol_parts(stream, token):
                self.add_text(part.text, style | CHORD_SYMBOL_STYLES[part.position])
            check_dropped_space(token, stream.peek())
        else:
            raise SongSyntaxError(token.line, f"unknown command \\{name}")

    def quote(self, stream: TokenStream, token: Token, style: Style) -> None:
        [*star, content] = stream.arguments(token, grammar.TEXT_COMMANDS[token.text])
        opening, closing = grammar.INNER_QUOTES if any(star) else grammar.QUOTES[token.text]
        self.add_text(opening, style)
        self.read_group(content, style)
        self.add_text(closing, style)

    def footnote(self, stream: TokenStream, token: Token) -> None:
        self.require(self.allowed.footnotes, token, "not allowed here")
        [content] = stream.arguments(token, grammar.TEXT_COMMANDS[token.text])
        lines = read_lines(content, self.state, IN_FOOTNOTE, token)
        self.add_inline(FootnoteRef(self.state.add_footnote(tuple(line_text(line) for line in lines))))

    def line_break(self, token: Token) -> None:
        self.require(self.allowed.line_breaks, token, "not allowed here")
        if token.text == grammar.GROUP_BREAK:
            self.require(self.allowed.music, token, "only in a part")
        if not self.items and self.segment is None:
            raise SongSyntaxError(token.line, f"\\{token.text} after an empty line: nothing to end")
        self.end_line()
        self.group_start = token.text == grammar.GROUP_BREAK

    def music(self, stream: TokenStream, token: Token, style: Style) -> None:
        name = token.text
        arguments = stream.arguments(token, grammar.PART_COMMANDS[name])
        if name == grammar.CHORD:
            self.start_segment(parse_chord(arguments[0], token))
        elif name == grammar.CHORD_ROW:  # the optional width is layout
            for chord in split_chord_row(arguments[1]):
                self.start_segment(parse_chord(chord, token))
            self.close_segment()
        elif name == grammar.GAP:
            self.add_inline(Gap(group_number(arguments[0], token)))
        elif name == grammar.REPEAT:
            self.add_mark(RepeatStart())
            self.read_group(arguments[0], style)
            self.add_mark(RepeatEnd())
        elif name == grammar.RECITATIVE:
            self.add_text(grammar.RECITATIVE_LABEL, style | Style.ITALIC)
            self.add_text(grammar.RECITATIVE_DELIMITER, style)
            self.read_group(arguments[0], style)
            self.add_text(grammar.RECITATIVE_DELIMITER, style)
        elif name == grammar.SCORE:
            self.add_mark(Score(group_text(arguments[0], token)))
        elif name == grammar.CUE:
            self.add_mark(self.state.cue(group_text(arguments[0], token), token.line))
        elif name == grammar.NOTE:
            self.add_mark(Note(read_text(arguments[0], self.state, IN_LABEL, token)))
        elif name == grammar.SPEAKER:  # the text is not a group in zpevnik.sty: \emph{#1:}~#2
            self.add_mark(Speaker(group_text(arguments[0], token)))
            self.read(arguments[1], style)

    @staticmethod
    def require(condition: bool, token: Token, reason: str) -> None:
        if not condition:
            raise SongSyntaxError(token.line, f"\\{token.text} is {reason}")

    # --- building --------------------------------------------------------------------------

    def start_segment(self, chord: Chord) -> None:
        self.close_segment()
        self.segment = OpenSegment(chord)
        self.after_space = False

    def close_segment(self) -> None:
        if self.segment is not None:
            self.items.append(Segment(self.segment.chord, tuple(self.segment.text)))
            self.segment = None

    def add_mark(self, mark: Mark) -> None:
        self.close_segment()
        self.items.append(mark)
        self.after_space = False

    def add_inline(self, item: Inline) -> None:
        if self.segment is None:
            self.segment = OpenSegment(None)
        self.segment.text.append(item)
        self.after_space = False

    def add_text(self, text: str, style: Style) -> None:
        if text == " ":
            if self.after_space:
                return
            self.after_space = True
        else:
            self.after_space = text.endswith(" ")
        if self.segment is None:
            self.segment = OpenSegment(None)
        runs = self.segment.text
        if runs and isinstance(runs[-1], Run) and runs[-1].style == style:
            runs[-1] = Run(runs[-1].text + text, style)
        else:
            runs.append(Run(text, style))

    def end_line(self) -> None:
        self.close_segment()
        self.lines.append(Line(trimmed(tuple(self.items)), self.group_start))
        self.items = []
        self.group_start = False
        self.after_space = True

    def finish(self, command: Token) -> list[Line]:
        if not self.items and self.segment is None:
            if self.lines:
                raise SongSyntaxError(command.line, f"\\{command.text}{{...}} ends with a line break")
            raise SongSyntaxError(command.line, f"\\{command.text}{{...}} has no text")
        self.end_line()
        return self.lines


def trimmed(items: tuple[Segment | Mark, ...]) -> tuple[Segment | Mark, ...]:
    """The line without the space TeX drops before its end."""
    if not items or not isinstance(items[-1], Segment) or not items[-1].text:
        return items
    last = items[-1]
    *text, run = last.text
    if not isinstance(run, Run):
        return items
    stripped = run.text.rstrip(" ")
    kept = tuple(text) + ((Run(stripped, run.style),) if stripped else ())
    return items[:-1] + (Segment(last.chord, kept),)


def read_lines(tokens: list[Token], state: SongState, allowed: Allowed, command: Token,
               continued: Line | None = None) -> list[Line]:
    """The lines of the argument of `command`."""
    parser = InlineParser(state, allowed, continued)
    parser.read(tokens)
    return parser.finish(command)


def line_text(line: Line) -> Text:
    """The text of a line that holds no chords and no marks."""
    return tuple(inline for segment in line.items if isinstance(segment, Segment) for inline in segment.text)


def read_text(tokens: list[Token], state: SongState, allowed: Allowed, command: Token) -> Text:
    """One line of text without music, such as a title."""
    [line] = read_lines(tokens, state, allowed, command)
    return line_text(line)
