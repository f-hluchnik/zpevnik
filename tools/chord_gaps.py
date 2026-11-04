"""Check that no two chords on the same line overlap (C1 prototype).

Build with the trace on, e.g. add \\zpchordtracetrue after \\usepackage{zpevnik}; \\chord then
writes "x y page width" (sp) for every chord to <job>.chords in document order. This prints
the number of overlapping pairs and the smallest gaps; exit code 1 if any pair overlaps.
Usage: python3 tools/chord_gaps.py [zpevnik.chords] [--list N]
"""
import sys
from pathlib import Path

SP = 65536


def main() -> int:
    args = sys.argv[1:]
    n = int(args[args.index('--list') + 1]) if '--list' in args else 10
    files = [a for a in args if a.endswith('.chords')]
    rows = [line.split() for line in Path(files[0] if files else 'zpevnik.chords').read_text().splitlines()]
    gaps = []
    for (x0, y0, p0, w0), (x, y, p, _) in zip(rows, rows[1:]):
        if (y, p) == (y0, p0):
            gaps.append(((int(x) - int(x0) - int(w0)) / SP, p))
    gaps.sort()
    over = sum(g < 0 for g, _ in gaps)
    print(f'{len(rows)} chords, {len(gaps)} pairs on the same line, {over} overlapping')
    for g, p in gaps[:n]:
        print(f'  {g:7.2f}pt  p. {p}')
    return 1 if over else 0


if __name__ == '__main__':
    sys.exit(main())
