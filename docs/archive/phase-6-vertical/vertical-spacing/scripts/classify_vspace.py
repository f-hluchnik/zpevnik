"""Mechanical pre-classes for the raw \\vspace (V1); V7 confirms each one."""
import json, re
from pathlib import Path
from collections import Counter, defaultdict
c = json.load(open("ctx.json"))
REPO = Path("/home/claude/zpevnik/pisnicky")
def parse_len(a):
    m = re.fullmatch(r"\s*(-?)\s*([\d.]+)\s*(pt|mm|cm)\s*", a)
    v = float(m.group(2)) * {"pt": 1, "mm": 2.845, "cm": 28.45}[m.group(3)]
    return -v if m.group(1) else v
def cls(o):
    t = (REPO / f"{o['song']}.tex").read_text()
    st = [0] + [i + 1 for i, ch in enumerate(t) if ch == "\n"]
    p = st[o["line"] - 1] + o["col"]
    pre, post = t[max(0, p - 200):p], t[p:p + 200]
    post = post[post.index("}") + 1:]
    v = parse_len(o["arg"])
    nxt = post.lstrip()
    head = t[:p]
    after_title = not re.search(r"\\(vers|refrainn?|intro|bridge|prechorus|solon?|solosm|cod|refsme)\{|\\nv", head.split("\\song", 1)[-1])
    if re.match(r"(\\hspace\*?\{[^}]*\}\s*)?\\includegraphics", nxt) or re.search(r"\\includegraphics(\[[^]]*\])?\{[^}]*\}\s*$", pre):
        return "score", v
    if "multicols" in t and v >= 50:
        return "column", v
    if re.match(r"\\(note|rec)\b", nxt):
        return "before-note-rec", v
    if v < 0:
        return ("squeeze-title" if after_title else "squeeze"), v
    return "gap", v
res = {}
for i, o in enumerate(c):
    if o["kind"] == "vspace":
        res[i] = cls(o)
json.dump(res, open("classes_vspace.json", "w"))
cnt = Counter(k for k, v in res.values()); print(cnt)
songs = defaultdict(set)
for i, (k, v) in res.items(): songs[k].add(c[i]["song"])
for k in cnt: print(k, len(songs[k]), "values:", sorted(Counter(round(v) for kk, v in res.values() if kk == k).items()))
