"""Report the horizontal gap between consecutive chords on the same line (C1 prototype).

Reads the chord positions that \\chord writes to pisnicky/*.aux (after a full build) and
prints the number of overlapping pairs and the smallest gaps. Exit code 1 if any overlap.
Usage: python3 tools/chord_gaps.py [ROOT] [--list N]
"""
import re
import sys
from pathlib import Path

ENTRY = re.compile(r'\{zpc\}\{(\d+)\}\{\{(-?\d+)\}\{(-?\d+)\}\{([^}]*)\}\{(\d+)\}\{(\d+)\}\}')
SP = 65536


def main() -> int:
    args = sys.argv[1:]
    n = int(args[args.index('--list') + 1]) if '--list' in args else 10
    root = Path(next((a for a in args if not a.startswith('--') and not a.isdigit()), '.'))
    chords = {}
    for aux in (root / 'pisnicky').glob('*.aux'):
        for m in ENTRY.finditer(aux.read_text(encoding='utf-8', errors='replace')):
            i, x, y, page, pad, w = m.groups()
            chords[int(i)] = (aux.stem, int(x) + int(pad), int(y), page, int(w))
    gaps = []
    for i in sorted(chords):
        if i - 1 in chords:
            s, x, y, pg, _ = chords[i]
            s0, x0, y0, pg0, w0 = chords[i - 1]
            if (s, y, pg) == (s0, y0, pg0):
                gaps.append(((x - x0 - w0) / SP, s, pg))
    gaps.sort()
    over = [g for g in gaps if g[0] < 0]
    print(f'{len(chords)} chords, {len(gaps)} pairs on the same line, {len(over)} overlapping')
    for g, s, pg in gaps[:n]:
        print(f'  {g:7.2f}pt  {s} (p. {pg})')
    return 1 if over else 0


if __name__ == '__main__':
    sys.exit(main())
