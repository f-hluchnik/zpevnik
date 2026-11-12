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
MINOR = "m"  # may follow a chord symbol after a space TeX drops: the chord name goes on (F\\kk m)
# The position everything inside these commands takes.
ARGUMENT_POSITIONS = {grammar.BASS: ChordPosition.SUBSCRIPT, grammar.ADDED: ChordPosition.SUPERSCRIPT,
                      grammar.SUSPENDED: ChordPosition.SUPERSCRIPT}


def parse_chord(tokens: list[Token], command: Token) -> Chord:
    parts: list[ChordPart] = []
    read_all(tokens, None, parts)
    chord = Chord(tuple(merged(stripped(parts))))
    if not chord.parts:
        raise SongSyntaxError(command.line, "an empty chord")
    return chord


def chord_symbol_parts(stream: TokenStream, command: Token) -> list[ChordPart]:
    """The parts of a chord symbol named in running text (`C\\kk{} dur`), with its argument."""
    parts: list[ChordPart] = []
    read_command(stream, command, None, parts)
    check_dropped_space(command, stream.peek())
    return merged(parts)


def read_token(stream: TokenStream, forced: ChordPosition | None, parts: list[ChordPart]) -> None:
    """Append the parts of the next token (with its argument); `forced` is the position
    everything inside \\bas, \\add or \\sus takes."""
    token = stream.next()
    check_dropped_space(token, stream.peek())
    if token.kind in (Kind.TEXT, Kind.SPACE):
        parts.append(ChordPart(token.text, forced or ChordPosition.BASE))
    elif token.kind is Kind.BEGIN_GROUP:  # \maj{}: a group only ends the command name
        read_all(stream.rest_of_group(token), forced, parts)
    elif token.kind is Kind.COMMAND:
        read_command(stream, token, forced, parts)
    else:
        raise SongSyntaxError(token.line, f"{token.text!r} is not allowed in a chord")


def read_all(tokens: list[Token], forced: ChordPosition | None, parts: list[ChordPart]) -> None:
    stream = TokenStream(tokens)
    while not stream.at_end():
        read_token(stream, forced, parts)


def read_command(stream: TokenStream, token: Token, forced: ChordPosition | None, parts: list[ChordPart]) -> None:
    name = token.text
    if name in grammar.CHORD_SYMBOLS:
        text, position = grammar.CHORD_SYMBOLS[name]
        parts.append(ChordPart(text, forced or position))
    elif name == grammar.DOTS:
        parts.append(ChordPart(grammar.TEXT_SYMBOLS[name], forced or ChordPosition.BASE))
    elif name in ARGUMENT_POSITIONS:
        if name == grammar.BASS:
            parts.append(ChordPart(grammar.BASS_SEPARATOR, forced or ChordPosition.BASE))
        elif name == grammar.SUSPENDED:
            parts.append(ChordPart(grammar.SUSPENDED_PREFIX, forced or ChordPosition.SUPERSCRIPT))
        read_all(stream.group(token), forced or ARGUMENT_POSITIONS[name], parts)
    elif name == grammar.SHARP_SIGN:
        raise SongSyntaxError(token.line, "\\# is not allowed in a chord: a sharp is \\kk")
    else:
        raise SongSyntaxError(token.line, f"\\{name} is not allowed in a chord")


def check_dropped_space(token: Token, following: Token | None) -> None:
    """TeX drops the space after a chord symbol named with letters (`\\kk`, `\\maj`). That is
    right inside a chord name, before `m` or another symbol (`F\\kk m`); before anything else
    the space was meant to be printed (`\\bas{C\\kk F}`, `C\\kk dur`, `\\chords{Dm\\maj Dm}`)."""
    if (token.kind is Kind.COMMAND and token.text in grammar.CHORD_SYMBOLS and token.swallowed_space
            and following is not None and following.kind is Kind.TEXT and not following.text.startswith(MINOR)):
        raise SongSyntaxError(token.line, f"TeX drops the space after \\{token.text}: "
                              f"write \\{token.text}{{}} to keep it")


def stripped(parts: list[ChordPart]) -> list[ChordPart]:
    """Without the spaces at the start and the end of the chord."""
    first = next((index for index, part in enumerate(parts) if part.text.strip()), len(parts))
    last = max((index for index, part in enumerate(parts) if part.text.strip()), default=-1)
    kept = parts[first:last + 1]
    if kept:
        kept[0] = ChordPart(kept[0].text.lstrip(), kept[0].position)
        kept[-1] = ChordPart(kept[-1].text.rstrip(), kept[-1].position)
    return kept


def merged(parts: list[ChordPart]) -> list[ChordPart]:
    """Neighbouring parts in the same position joined."""
    result: list[ChordPart] = []
    for part in parts:
        if result and result[-1].position is part.position:
            result[-1] = ChordPart(result[-1].text + part.text, part.position)
        else:
            result.append(part)
    return result


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
