"""Replace the manual chord spacing (\\nc \\mm \\sm \\bc) in songs (C1 prototype).

Usage: python3 tools/strip_chord_spacing.py [--dry-run] SONG_ID ...   (edits pisnicky/<id>.tex)

Each run of spacing macros is classified by where it stands:
- right after a chord and before lyrics: a pause (the chord is struck, then the
  singing starts) -> \\gap{n};
- inside lyrics, or at the start of a line, without a chord: a deliberate gap -> \\gap{n};
- between two chords, or after the last chord of a line: removed (\\chordrunsep spaces runs);
- after lyrics and before a chord: removed (collision avoidance, now automatic). TeX
  swallows the space after a control word, so `je\\nc \\chord{Am}hojnost` had the macro
  as its only word gap: one space is kept when the author typed a space after the macro
  or the character before it is not a letter. With a letter right before it and no
  typed space it is either inside a word (`invisi\\sm\\chord{F}ble`) or the only word
  gap (`já\\sm\\chord{C}panenku`); the songbook itself decides: if the joined form is a
  word elsewhere in the book (or no letter follows), it is inside a word and removed;
  otherwise a space is kept (never join words on a guess) and listed as CHECK.
n is in characters of 0.5em: \\sm = 1, \\mm = 2, \\nc = 4, \\bc = 8, summed over the run.
Prints a summary and every \\gap, kept space and in-word removal, for review.
"""
import re
import sys
from collections import Counter
from pathlib import Path

RUN = re.compile(r'(?:\\(?:nc|mm|sm|bc)(?![A-Za-z])[ \t]*)+')
UNITS = {'sm': 1, 'mm': 2, 'nc': 4, 'bc': 8}
CHORD_END = re.compile(r'\\chord(?:\[[a-z]\])?\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}[ \t]*$')
CHORD_START = re.compile(r'\\chords?[\[{]')


CHORD_ANY = re.compile(r'\\chord(?:\[[a-z]\])?\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}')
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")


def corpus(paths) -> set[str]:
    """Words of all songs, with chords removed and words touching manual spacing skipped."""
    words: set[str] = set()
    for path in paths:
        text = re.sub(r'(?<!\\)%.*', '', path.read_text(encoding='utf-8'))
        text = CHORD_ANY.sub('', text)
        text = RUN.sub('\x00', text)
        text = re.sub(r'\\[A-Za-z]+|\\.|[{}]', ' ', text)
        for token in text.split():
            if '\x00' not in token:
                words.update(w.lower() for w in WORD.findall(token))
    return words


def fragment(text: str, left: bool) -> str:
    """Letters next to a gap: the end of `text` (left) or its start; chords inside the
    word are skipped, other manual spacing counts as a word boundary."""
    text = RUN.sub('\x01', text[-200:] if left else text[:200])
    text = CHORD_ANY.sub('', text)
    text = re.sub(r'\\[A-Za-z]+|[{}]', '\x01', text)
    m = re.search(r"[^\W\d_]+$", text) if left else re.match(r"[^\W\d_]+", text)
    return m.group().lower() if m else ''


def classify(src: str, m: re.Match) -> str:
    before, after = src[:m.start()], src[m.end():]
    line_before = before.rsplit('\n', 1)[-1].strip()
    nxt = after.lstrip(' \t')
    at_end = nxt.startswith('\\\\') or nxt[:1] in ('\n', '}', '')
    if CHORD_END.search(before):
        if CHORD_START.match(nxt) or at_end:
            return 'run'
        return 'pause'
    if CHORD_START.match(nxt):
        return 'before-chord'
    if not line_before or line_before.endswith('{'):
        return 'line-start'
    return 'in-lyrics'


def convert(src: str, name: str, log: list[str], stats: Counter, words: set[str]) -> str:
    out, pos = [], 0
    for m in RUN.finditer(src):
        kind = classify(src, m)
        prev, rest = src[m.start() - 1:m.start()], src[m.end():]
        line = src.count('\n', 0, m.start()) + 1
        ctx = (src[max(0, m.start() - 22):m.start()] + '[' + m.group().strip() + ']' + rest[:22]).replace('\n', '⏎')
        if kind in ('pause', 'in-lyrics', 'line-start'):
            n = sum(UNITS[u] for u in re.findall(r'\\(nc|mm|sm|bc)', m.group()))
            repl = f'\\gap{{{n}}}'
            log.append(f'{name}:{line}: {kind} -> {repl}  {ctx}')
        elif kind == 'run':
            repl = ''
            log.append(f'{name}:{line}: run of chords, removed  {ctx}')
        else:  # before-chord
            typed_space = bool(re.search(r'[ \t]', m.group()))
            if prev in ' \t\n{' or rest[:1] in ('\n', '}', ''):
                repl = ''
            elif typed_space or not prev.isalpha():
                repl = ' '
                log.append(f'{name}:{line}: kept a word space  {ctx}')
            else:
                left, right = fragment(src[:m.start()], True), fragment(rest, False)
                if not right or left + right in words:
                    repl = ''
                    log.append(f'{name}:{line}: removed inside a word ({left}|{right})  {ctx}')
                else:
                    repl = ' '
                    log.append(f'{name}:{line}: CHECK, kept a space ({left}|{right})  {ctx}')
        stats[kind] += 1
        out += [src[pos:m.start()], repl]
        pos = m.end()
    out.append(src[pos:])
    return ''.join(out)


def main() -> int:
    args = [a for a in sys.argv[1:] if a != '--dry-run']
    log: list[str] = []
    stats: Counter = Counter()
    words = corpus(Path('pisnicky').glob('*.tex'))
    for song in args:
        path = Path('pisnicky') / f'{song}.tex'
        new = convert(path.read_text(encoding='utf-8'), song, log, stats, words)
        if '--dry-run' not in sys.argv:
            path.write_text(new, encoding='utf-8')
    print('\n'.join(log))
    print(', '.join(f'{k}: {v}' for k, v in stats.most_common()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
