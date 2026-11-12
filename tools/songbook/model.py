"""The in-memory model of a song, as the converter reads it from songs/<id>.tex.

Semantic, not layout: what the PDF prints, without how it is placed. Text is kept as
the PDF prints it (quote marks, dashes, "×2"); spacing, sizes and column breaks are
not kept. Every class is immutable.

Python >= 3.11, standard library only.
"""
from dataclasses import dataclass
from enum import Enum, Flag, auto


class Style(Flag):
    """How a run of text is set; runs inside each other combine (bold inside echo)."""
    PLAIN = 0
    ITALIC = auto()     # \emph, \rec's label, notes
    BOLD = auto()       # \textbf
    ECHO = auto()       # \echo: echo or backing vocals, raised and in italics
    SUBSCRIPT = auto()  # \textsubscript; a bass note of a chord named in the text
    SUPERSCRIPT = auto()  # a chord symbol named in the text ("C\kk dur": C♯)


@dataclass(frozen=True)
class Run:
    """Text in one style."""
    text: str
    style: Style = Style.PLAIN


@dataclass(frozen=True)
class Gap:
    """An intentional pause, `\\gap{n}`: n units of half an em."""
    units: int


@dataclass(frozen=True)
class FootnoteRef:
    """Where a footnote stands; `number` counts the footnotes of the song from 1."""
    number: int


Inline = Run | Gap | FootnoteRef
Text = tuple[Inline, ...]


class ChordPosition(Enum):
    BASE = "base"
    SUPERSCRIPT = "superscript"  # the chord's quality: ⁷, ♯, sus4 ...
    SUBSCRIPT = "subscript"      # a bass note after the slash


@dataclass(frozen=True)
class ChordPart:
    text: str
    position: ChordPosition = ChordPosition.BASE


@dataclass(frozen=True)
class Chord:
    parts: tuple[ChordPart, ...]


@dataclass(frozen=True)
class Segment:
    """A chord and the text under it: the text runs up to the next chord, the end of
    the line or the end of the TeX group the chord stands in (the rule of \\chord).
    A segment without a chord is text before the first chord of a line.
    `in_word`: the chord stands inside a word, with a character of the text right before it
    and a letter right after it (the test of \\chord); where the PDF widens the gap before
    such a chord, it prints a hyphen in the gap."""
    chord: Chord | None
    text: Text = ()
    in_word: bool = False


@dataclass(frozen=True)
class RepeatStart:
    """`\\rep{`: the PDF prints \\: (a repeat may span lines)."""


@dataclass(frozen=True)
class RepeatEnd:
    """The end of `\\rep{...}`: the PDF prints :\\."""


LABEL_END = "."  # what the PDF prints after the label of a part and of a cue: "R2."


@dataclass(frozen=True)
class Cue:
    """`\\cue{label}`: the place where a part written out before is sung again.
    `target` is the index in Song.body of the last block with that label before the
    cue; a cue without one is an error."""
    label: str
    target: int

    @property
    def printed_label(self) -> str:
        """The label the PDF prints, "R2." (zpevnik.sty's \\cue)."""
        return self.label + LABEL_END


@dataclass(frozen=True)
class Note:
    """`\\note{...}`: a short remark (capo, tempo), printed in italics."""
    text: Text


@dataclass(frozen=True)
class Speaker:
    """`\\speaker{name}{...}` inside a part: the name before the line."""
    name: str


@dataclass(frozen=True)
class Score:
    """`\\score{name}`: the image of scores/<name>.mscz."""
    name: str


Mark = RepeatStart | RepeatEnd | Cue | Note | Speaker | Score


@dataclass(frozen=True)
class Line:
    items: tuple[Segment | Mark, ...]
    group_start: bool = False  # a \groupbreak stands before it


class BlockKind(Enum):
    """The kinds of part; the value is the letter of its label (a verse has only its number)."""
    VERSE = ""
    CHORUS = "R"
    PRECHORUS = "P"
    BRIDGE = "B"
    SOLO = "S"
    INTRO = "I"
    CODA = "C"


@dataclass(frozen=True)
class Block:
    kind: BlockKind
    number: str | None  # "2", "a", "4*"; None: no number (an unnumbered verse has no label)
    lines: tuple[Line, ...]

    @property
    def key(self) -> str:
        """What a cue names to refer to this block: "R2", "R", "3"."""
        return self.kind.value + (self.number or "")

    @property
    def label(self) -> str:
        """The label the PDF prints, "R2."; empty for an unnumbered verse."""
        return self.key + LABEL_END if self.key else ""


@dataclass(frozen=True)
class SpeakerBlock:
    """`\\speaker{name}{...}` after an empty line: the name stands in the label column."""
    name: str
    lines: tuple[Line, ...]


@dataclass(frozen=True)
class CueBlock:
    """A cue after an empty line, a block of its own; `line` holds what follows it
    on its line (e.g. "×2"), often nothing."""
    cue: Cue
    line: Line


class RuleKind(Enum):
    DASHED = "dashed"  # \blockrule: between tight verses
    SOLID = "solid"    # \partrule: between parts of a song


@dataclass(frozen=True)
class Rule:
    kind: RuleKind


BodyItem = Block | SpeakerBlock | CueBlock | Note | Rule


@dataclass(frozen=True)
class ArtistRef:
    slug: str
    label: str | None = None  # \artist[label]{slug}: a label instead of the registry's


@dataclass(frozen=True)
class SeeAlso:
    """`\\seealso{id}{text}`: a link to another song."""
    song_id: str
    text: Text


@dataclass(frozen=True)
class Song:
    id: str
    title: Text
    toc_title: str | None = None
    alt_titles: tuple[str, ...] = ()
    subtitle: Text | None = None
    artists: tuple[ArtistRef, ...] = ()
    collections: tuple[str, ...] = ()
    see: tuple[SeeAlso, ...] = ()
    columns: int = 1
    footnotes: tuple[tuple[Text, ...], ...] = ()  # each footnote is lines of text
    body: tuple[BodyItem, ...] = ()

    @property
    def contents_title(self) -> str:
        """The title the contents list: the TOC title, if the song has one."""
        return self.toc_title if self.toc_title is not None else plain(self.title)

    @property
    def page_title(self) -> str:
        """The title printed on the song's page, as plain text (the artist sections list it)."""
        return plain(self.title)


def plain(text: Text) -> str:
    """The characters of a text, without styles, gaps and footnote references."""
    return "".join(item.text for item in text if isinstance(item, Run))
