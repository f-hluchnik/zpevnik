"""Remove the manual chord spacing (\\nc \\mm \\sm \\bc) from songs (C1 prototype).

Usage: python3 tools/strip_chord_spacing.py SONG_ID ...   (edits pisnicky/<id>.tex)

TeX swallows spaces after a control word, so authors often wrote `je\\nc \\chord{X}hojnost`
and the macro was the only word gap. A run of spacing macros therefore becomes one space
when it does not follow a chord and either the author typed a space after it or the
character before it is not a letter (e.g. `here,\\mm\\chord{A}well`). Otherwise it is
removed (a nudge after a chord, or a gap inside a word such as `invisi\\sm\\chord{F}ble`).
Prints every place where a space is kept, for review.
"""
import re
import sys
from pathlib import Path

RUN = re.compile(r'(?:\\(?:nc|mm|sm|bc)(?![A-Za-z])[ \t]*)+')
CHORD_END = re.compile(r'\\chord\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}$')


def strip(src: str, name: str, log: list[str]) -> str:
    out, pos = [], 0
    for m in RUN.finditer(src):
        before = src[:m.start()]
        prev = before[-1:]
        rest = src[m.end():]
        keep = (not CHORD_END.search(before)
                and prev not in ' \t\n{'
                and (re.search(r'[ \t]', m.group()) or not prev.isalpha())
                and rest[:1] not in ('\n', '}', '')
                and not rest.startswith('\\\\'))
        out += [src[pos:m.start()], ' ' if keep else '']
        pos = m.end()
        if keep:
            line = src.count('\n', 0, m.start()) + 1
            ctx = (src[max(0, m.start() - 20):m.start()] + '[' + m.group().strip() + ']' + rest[:20]).replace('\n', ' ')
            log.append(f'{name}:{line}: {ctx}')
    out.append(src[pos:])
    return ''.join(out)


def main() -> int:
    log: list[str] = []
    for song in sys.argv[1:]:
        path = Path('pisnicky') / f'{song}.tex'
        path.write_text(strip(path.read_text(encoding='utf-8'), song, log), encoding='utf-8')
    print('\n'.join(log))
    print(f'{len(log)} place(s) kept a space')
    return 0


if __name__ == '__main__':
    sys.exit(main())
