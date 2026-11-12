"""Read a chord, `\\chord{F\\kk m\\7}` or one chord of `\\chords{...}`, into its parts.

The chord symbols of zpevnik.sty become the characters the PDF prints, each on the
base line, in superscript or in subscript; everything inside `\\bas{...}` is a
subscript (a sharp of a bass note too), everything inside `\\add` and `\\sus` a superscript.

Python >= 3.11, standard library only.
"""
from songbook import grammar
from songbook.errors import SongSyntaxError
from songbook.lexer import DEPTH_CHANGE, Kind, Token
from songbook.model import Chord, ChordPart, ChordPosition
from songbook.stream import TokenStream

ChordRow = list[list[Token]]
SHARP_SIGN = "#"  # \\#: a plain sign in text, never in a chord
MINOR = "m"  # what may follow a chord symbol after a space TeX drops: the chord name goes on (F\\kk m)


def parse_chord(tokens: list[Token], command: Token) -> Chord:
    parts: list[ChordPart] = []
    read_parts(tokens, None, parts)
    chord = Chord(tuple(merged(stripped(parts))))
    if not chord.parts:
        raise SongSyntaxError(command.line, "an empty chord")
    return chord


def chord_symbol_parts(stream: TokenStream, command: Token) -> list[ChordPart]:
    """The parts of one chord symbol named in running text (`C\\kk dur`), with its argument."""
    signature = grammar.CHORD_COMMANDS[command.text]
    tokens = [command] + [token for argument in stream.arguments(command, signature)
                          for token in braced(argument, command)]
    parts: list[ChordPart] = []
    read_parts(tokens, None, parts)
    return merged(parts)


def braced(argument: list[Token], command: Token) -> list[Token]:
    return [Token(Kind.BEGIN_GROUP, "{", command.line), *argument, Token(Kind.END_GROUP, "}", command.line)]


def read_parts(tokens: list[Token], forced: ChordPosition | None, parts: list[ChordPart]) -> None:
    """Append the parts of `tokens`; `forced` is the position everything inside \\bas, \\add or \\sus takes."""
    def add(text: str, position: ChordPosition) -> None:
        parts.append(ChordPart(text, forced or position))

    stream = TokenStream(tokens)
    while not stream.at_end():
        token = stream.next()
        check_dropped_space(token, stream.peek())
        if token.kind in (Kind.TEXT, Kind.SPACE):
            add(token.text, ChordPosition.BASE)
        elif token.kind is Kind.BEGIN_GROUP:  # \maj{}: a group only ends the command name
            read_parts(stream.rest_of_group(token), forced, parts)
        elif token.kind is Kind.COMMAND and token.text in grammar.CHORD_SYMBOLS:
            add(*grammar.CHORD_SYMBOLS[token.text])
        elif token.kind is Kind.COMMAND and token.text == "dots":
            add(grammar.TEXT_SYMBOLS["dots"], ChordPosition.BASE)
        elif token.kind is Kind.COMMAND and token.text == grammar.BASS:
            add(grammar.BASS_SEPARATOR, ChordPosition.BASE)
            read_parts(stream.group(token), forced or ChordPosition.SUBSCRIPT, parts)
        elif token.kind is Kind.COMMAND and token.text == grammar.ADDED:
            read_parts(stream.group(token), forced or ChordPosition.SUPERSCRIPT, parts)
        elif token.kind is Kind.COMMAND and token.text == grammar.SUSPENDED:
            add(grammar.SUSPENDED_PREFIX, ChordPosition.SUPERSCRIPT)
            read_parts(stream.group(token), forced or ChordPosition.SUPERSCRIPT, parts)
        elif token.kind is Kind.COMMAND and token.text == SHARP_SIGN:
            raise SongSyntaxError(token.line, "\\# is not allowed in a chord: a sharp is \\kk")
        else:
            shown = "\\" + token.text if token.kind is Kind.COMMAND else repr(token.text)
            raise SongSyntaxError(token.line, f"{shown} is not allowed in a chord")


def stripped(parts: list[ChordPart]) -> list[ChordPart]:
    """Without the spaces at the start and the end of the chord."""
    while parts and not parts[0].text.strip():
        parts.pop(0)
    while parts and not parts[-1].text.strip():
        parts.pop()
    if parts:
        parts[0] = ChordPart(parts[0].text.lstrip(), parts[0].position)
        parts[-1] = ChordPart(parts[-1].text.rstrip(), parts[-1].position)
    return parts


def merged(parts: list[ChordPart]) -> list[ChordPart]:
    """Neighbouring parts in the same position joined."""
    result: list[ChordPart] = []
    for part in parts:
        if result and result[-1].position is part.position:
            result[-1] = ChordPart(result[-1].text + part.text, part.position)
        else:
            result.append(part)
    return result


def check_dropped_space(token: Token, following: Token | None) -> None:
    """TeX drops the space after a chord symbol named with letters (`\\kk`, `\\maj`). That is
    right inside a chord name, before `m` or another symbol (`F\\kk m`); before anything else
    the space was meant to be printed (`\\bas{C\\kk F}`, `C\\kk dur`, `\\chords{Dm\\maj Dm}`)."""
    if (token.kind is Kind.COMMAND and token.text in grammar.CHORD_SYMBOLS and token.swallowed_space
            and following is not None and following.kind is Kind.TEXT and not following.text.startswith(MINOR)):
        raise SongSyntaxError(token.line, f"TeX drops the space after \\{token.text}: "
                              f"write \\{token.text}{{}} to keep it")


def split_chord_row(tokens: list[Token]) -> ChordRow:
    """The chords of `\\chords{A B C}`: TeX splits the row at the spaces outside braces
    (a space TeX dropped after a chord symbol splits nothing, see check_dropped_space)."""
    chords: ChordRow = [[]]
    depth = 0
    for token in tokens:
        if token.kind is Kind.SPACE and depth == 0:
            chords.append([])
            continue
        depth += DEPTH_CHANGE.get(token.kind, 0)
        chords[-1].append(token)
    return [chord for chord in chords if chord]
