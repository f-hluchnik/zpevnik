"""Every command and environment a song may use, and what it takes.

This is the command set of zpevnik.sty after the renames (D-131) and the song quirks
(D-135, D-136, D-163). A command that is not listed here is an error; one that is listed
is an error where it does not belong (a part inside a part, a chord in a title).

An argument signature is a string of letters, as in xparse: `m` a mandatory `{...}`
argument, `o` an optional `[...]` argument, `s` an optional star.

Python >= 3.11, standard library only.
"""
from songbook.model import BlockKind, ChordPosition, RuleKind, Style

# The parts of a song; `\intro` and `\coda` take no number.
BLOCKS: dict[str, BlockKind] = {
    "vers": BlockKind.VERSE, "chorus": BlockKind.CHORUS, "prechorus": BlockKind.PRECHORUS,
    "bridge": BlockKind.BRIDGE, "solo": BlockKind.SOLO, "intro": BlockKind.INTRO, "coda": BlockKind.CODA,
}
UNNUMBERED_BLOCKS = {"intro", "coda"}
BLOCK_SIGNATURE = "om"            # \vers[2]{...}
UNNUMBERED_BLOCK_SIGNATURE = "m"  # \intro{...}

# Song level, outside the parts.
METADATA = {"song": "m", "subtitle": "m", "artist": "om", "alttitle": "m", "toctitle": "m",
            "collection": "m", "seealso": "mm"}
RULES: dict[str, tuple[str, RuleKind]] = {"blockrule": ("m", RuleKind.DASHED), "partrule": ("", RuleKind.SOLID)}
ENVIRONMENT_COMMANDS = {"begin": "m", "end": "m"}
COLUMNS_ENVIRONMENT = "multicols"  # \begin{multicols}{n}: the song has n columns (D-135)
LAYOUT_ENVIRONMENTS = {"small"}     # PDF-only: a smaller font
ENVIRONMENT_ARGUMENTS = {COLUMNS_ENVIRONMENT: "m"} | {name: "" for name in LAYOUT_ENVIRONMENTS}
# PDF-only layout, read and dropped: a font size, a column break, the gap between columns.
LAYOUT_COMMANDS = {"large": "", "columnbreak": "", "setlength": "mm"}

# Both levels: alone after an empty line, otherwise appended to the line (zpevnik.sty).
CUE = "cue"
NOTE = "note"
SPEAKER = "speaker"
MODE_DEPENDENT = {CUE: "m", NOTE: "m", SPEAKER: "mm"}

# Inside a part.
LINE_BREAK = "\\"
GROUP_BREAK = "groupbreak"
CHORD = "chord"
CHORD_ROW = "chords"  # \chords[width]{A B C}: chords without text; the width is layout
GAP = "gap"
REPEAT = "rep"
RECITATIVE = "rec"
TIMES = "ntimes"
SCORE = "score"
FOOTNOTE = "footnote"
# The commands of music in a part, with their arguments (line breaks are handled apart).
PART_COMMANDS = {CHORD: "m", CHORD_ROW: "om", GAP: "m", REPEAT: "m", RECITATIVE: "m",
                 SCORE: "m"} | MODE_DEPENDENT
LINE_BREAKS = {LINE_BREAK, GROUP_BREAK}

# Text, wherever text is allowed (lines, titles, notes, footnotes).
STYLES: dict[str, Style] = {"emph": Style.ITALIC, "textbf": Style.BOLD, "echo": Style.ECHO,
                            "textsubscript": Style.SUBSCRIPT}
CZECH_QUOTES = "uv"
ENGLISH_QUOTES = "enquote"  # \enquote{} and the inner quotes \enquote*{}
QUOTES = {CZECH_QUOTES: ("„", "“"), ENGLISH_QUOTES: ("‘", "’")}
INNER_QUOTES = ("“", "”")  # \enquote*: what the British style of csquotes prints
TEXT_COMMANDS = {CZECH_QUOTES: "m", ENGLISH_QUOTES: "sm", FOOTNOTE: "m", TIMES: "m"} | {name: "m" for name in STYLES}
DOTS = "dots"
SHARP_SIGN = "#"  # \#: a plain sign in text (note names in lowercase letters); in a chord a sharp is \kk
TEXT_SYMBOLS = {DOTS: "…", "&": "&", "ss": "ß", " ": " ", "textdagger": "†", "textasteriskcentered": "∗",
                SHARP_SIGN: "#"}
# Math is allowed for these symbols only (D-135).
MATH_SYMBOLS = {"times": "×", "rightarrow": "→"}
TIE = " "  # ~
TIMES_SIGN = MATH_SYMBOLS["times"]
RECITATIVE_LABEL = "rec: "  # \rec{x} prints "rec: " in italics, then /x/
RECITATIVE_DELIMITER = "/"
# TeX's ligatures of the T1 font, longest first: what the PDF prints for them.
LIGATURES = (("---", "—"), ("--", "–"), ("``", "“"), ("''", "”"), ("`", "‘"), ("'", "’"))

# Inside a chord (\chord{...}, one chord of \chords{...}): the chord symbols of zpevnik.sty,
# as the PDF prints them.
SUPERSCRIPT = ChordPosition.SUPERSCRIPT
CHORD_SYMBOLS: dict[str, tuple[str, ChordPosition]] = {
    "kk": ("♯", SUPERSCRIPT), "bb": ("♭", SUPERSCRIPT), "maj": ("△", SUPERSCRIPT),
    "dm": ("∘", SUPERSCRIPT), "hdm": ("∅", SUPERSCRIPT), "+": ("+", SUPERSCRIPT),
} | {digit: (digit, SUPERSCRIPT) for digit in "245679"}
BASS = "bas"          # \bas{X}: "/" and X as a subscript
BASS_SEPARATOR = "/"
ADDED = "add"         # \add{x}: x as a superscript
SUSPENDED = "sus"     # \sus{x}: "sus" and x as a superscript
SUSPENDED_PREFIX = "sus"
CHORD_COMMANDS = {BASS: "m", ADDED: "m", SUSPENDED: "m", DOTS: ""} | {name: "" for name in CHORD_SYMBOLS}
