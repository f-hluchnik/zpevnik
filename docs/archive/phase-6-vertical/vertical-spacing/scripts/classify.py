"""Mechanical context classes for every occurrence (V1). Writes classes.json."""
import json, re
from pathlib import Path
from collections import Counter, defaultdict
c = json.load(open("ctx.json"))
REPO = Path("/home/claude/zpevnik/pisnicky")
def window(o, before=160, after=160):
    t = (REPO / f"{o['song']}.tex").read_text()
    st = [0] + [i + 1 for i, ch in enumerate(t) if ch == "\n"]
    p = st[o["line"] - 1] + o["col"]
    return t[max(0, p - before):p], t[p:p + after]
BLOCK = r"\\(vers|refrainn?|intro|bridge|prechorus|solon?|solosm|cod|refsme)\b"
def ns_class(o):
    pre, post = window(o)
    post1 = post[3:] if o["kind"] == "ns" else post[4:]
    nxt = post1.lstrip()
    if re.search(r"\\begin\{center\}\\rule", nxt[:40]) or re.search(r"\\rule\{[^}]*\}\{[^}]*\}\\end\{center\}\s*$", pre):
        return "rule"
    if re.match(r"\\(begin|end)\{multicols", nxt) or re.search(r"\\(begin|end)\{multicols\}(\{\d\})?\s*$", pre):
        return "multicols"
    if o["blk_before"] in ("song",) and not re.search(BLOCK, pre.split("\\song")[-1] if "\\song" in pre else pre):
        return "title"
    if re.match(r"\\note", nxt) or re.search(r"\\note\{[^}]*\}\s*$", pre):
        return "note"
    if re.match(r"\\(ns|cns|vspace)", nxt) or re.search(r"\\(ns|cns|vspace\{[^}]*\})\s*$", pre):
        return "stacked"
    return "between"
cls = {}
for i, o in enumerate(c):
    if o["kind"] in ("ns", "cns"):
        cls[i] = ns_class(o)
json.dump(cls, open("classes_ns.json", "w"))
cnt = Counter(cls.values()); print(cnt)
by = defaultdict(set)
for i, k in cls.items(): by[k].add(c[i]["song"])
for k, v in by.items(): print(k, len(v), sorted(v)[:12])
