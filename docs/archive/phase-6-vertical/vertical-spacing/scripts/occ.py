"""List every occurrence of the vertical-spacing macros in the songs (V1 analysis)."""
import json, re, sys
from pathlib import Path
REPO = Path(sys.argv[1])
PAT = re.compile(r"\\(ns|cns|vnv|vinv|lsp)(?![A-Za-z])|\\vspace\s*\{([^}]*)\}")
out = []
for f in sorted((REPO / "pisnicky").glob("*.tex")):
    lines = f.read_text(encoding="utf-8").split("\n")
    for i, line in enumerate(lines):
        code = re.split(r"(?<!\\)%", line, 1)[0]
        for m in PAT.finditer(code):
            kind = m.group(1) or "vspace"
            out.append(dict(song=f.stem, line=i + 1, col=m.start(), kind=kind,
                            arg=m.group(2), text=line))
json.dump(out, open("occ.json", "w"), ensure_ascii=False, indent=0)
from collections import Counter
print(Counter(o["kind"] for o in out))
