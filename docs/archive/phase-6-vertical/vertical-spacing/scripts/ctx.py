"""Structural context of each occurrence: mode, brace depth, what precedes and follows."""
import json, re, sys
from pathlib import Path
from collections import Counter
REPO = Path(sys.argv[1])
occ = json.load(open("occ.json"))
TOK = re.compile(r"\\[A-Za-z@]+\*?|\\.|[{}]|\n[ \t]*\n|%[^\n]*|\s+|[^\\{}%\s]+")
BLOCKS = {"vers","refrain","refrainn","intro","bridge","prechorus","solo","solon","solosm","cod","refsme"}
def tokens(text):
    return [m for m in TOK.finditer(text)]
cache = {}
def analyse(song):
    if song in cache: return cache[song]
    text = (REPO/"pisnicky"/f"{song}.tex").read_text(encoding="utf-8")
    toks = tokens(text)
    # line starts
    starts = [0]+[i+1 for i,c in enumerate(text) if c=="\n"]
    cache[song] = (text, toks, starts)
    return cache[song]
def describe(t):
    s = t.group(0)
    if s.startswith("%"): return None
    if re.fullmatch(r"\n[ \t]*\n", s): return "PAR"
    if s.isspace(): return None
    if s.startswith("\\"): return s
    if s in "{}": return s
    return "TEXT"
res = []
for o in occ:
    text, toks, starts = analyse(o["song"])
    pos = starts[o["line"]-1] + o["col"]
    idx = next(i for i,t in enumerate(toks) if t.start()==pos)
    # brace depth & enclosing macro
    depth = 0; stack=[]; lastcs=None
    for t in toks[:idx]:
        s=t.group(0)
        if s.startswith("%"): continue
        if s=="{": stack.append(lastcs); lastcs=None
        elif s=="}": stack and stack.pop(); lastcs=None
        elif s.startswith("\\"): lastcs=s
        elif not s.isspace(): lastcs=None
    encl = [c for c in stack if c]  # macros whose argument we are in
    # previous meaningful items
    prev=[]; j=idx-1
    while j>=0 and len(prev)<3:
        d=describe(toks[j]);
        if d: prev.append(d)
        j-=1
    # skip own argument for vspace/lsp
    k=idx+1
    if o["kind"] in ("vspace","lsp"):
        while toks[k].group(0)!="{": k+=1
        lvl=0
        while True:
            s=toks[k].group(0)
            if s=="{": lvl+=1
            elif s=="}":
                lvl-=1
                if lvl==0: break
            k+=1
        k+=1
    nxt=[]
    while k<len(toks) and len(nxt)<3:
        d=describe(toks[k]);
        if d: nxt.append(d)
        k+=1
    o.update(encl=[e.lstrip("\\") for e in encl], prev=prev, next=nxt)
    res.append(o)
json.dump(res, open("ctx.json","w"), ensure_ascii=False, indent=0)
