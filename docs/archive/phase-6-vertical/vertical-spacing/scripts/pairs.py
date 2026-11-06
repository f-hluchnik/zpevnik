"""For each occurrence: the block macro before and after it (V1)."""
import json, re
from pathlib import Path
from collections import Counter, defaultdict
r=json.load(open("ctx.json"))
BLK=r"\\(vers|refrain|refrainn|intro|bridge|bridgesm|prechorus|solo|solon|solosm|cod|refsme|refsm|song|sub|note|lsp|nv|rec|begin\{[a-z]+\}|includegraphics|hyl|chords)\b"
def blocks(song):
    t=Path(f"/home/claude/zpevnik/pisnicky/{song}.tex").read_text()
    starts=[0]+[i+1 for i,c in enumerate(t) if c=="\n"]
    return t,starts
for o in r:
    t,st=blocks(o["song"]); p=st[o["line"]-1]+o["col"]
    before=[m.group(1) for m in re.finditer(BLK,t[:p])]
    after=[m.group(1) for m in re.finditer(BLK,t[p:])]
    # top-level block before: last block macro that starts a line
    tb=[m.group(1) for m in re.finditer(r"(?m)^\s*\\(vers|refrainn?|intro|bridge|prechorus|solon?|solosm|cod|refsme|song|lsp|nv|note|rec)\b",t[:p])]
    ta=[m.group(1) for m in re.finditer(r"(?m)^\s*\\(vers|refrainn?|intro|bridge|prechorus|solon?|solosm|cod|refsme|lsp|nv|note|rec|begin|hyl)\b",t[p+3:])]
    o["blk_before"]=tb[-1] if tb else None
    o["blk_after"]=ta[0] if ta else None
json.dump(r,open("ctx.json","w"),ensure_ascii=False,indent=0)
for kind in ["ns","cns","vnv","lsp"]:
    c=Counter((o["blk_before"],o["blk_after"]) for o in r if o["kind"]==kind)
    print("==",kind, c.most_common(20))
# per-song density of ns
d=defaultdict(int)
for o in r:
    if o["kind"]=="ns": d[o["song"]]+=1
print("songs with ns:",len(d), Counter(d.values()))
