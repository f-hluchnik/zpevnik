"""Write the V1 appendix (sampled contexts with crops) and the occurrence CSV."""
import csv, json, re
from pathlib import Path
REPO = Path("/home/claude/zpevnik/pisnicky")
OUT = Path("/mnt/user-data/outputs")
occ = json.load(open("occ_crops.json")); ctx = json.load(open("ctx.json"))
sample = json.load(open("sample.json"))
ns_cls = json.load(open("classes_ns.json")); vs_cls = json.load(open("classes_vspace.json"))
spill_ns = set(open("/home/claude/over_X1.txt").read().split())
spill_vneg = {"acrosstheuniverse","babickamary","carodejnicezamesbury","dance","darmodej","deepriverblues","dvakrat","herecomesthesun","illbethereforyou","jdoupomnejdou","malujzaseobrazky","mikymauz","milionar","morseovka","pianoman","pohadka","slunecnyhrob","tearsinheaven"}
VS = {"squeeze": "R1", "squeeze-title": "R1", "score": "R2", "unlabelled-gap": "R3",
      "before-note-rec": "R4", "after-note": "R5", "column": "R6", "gap-other": "R7"}
def klass(i):
    o = occ[i]; k = o["kind"]
    if k in ("ns", "cns"):
        return "N2" if ns_cls[str(i)] == "rule" else "N1"
    if k == "vinv":
        return "I2" if ctx[i]["prev"][0] == "}" else "I1"
    if k == "vnv": return "U1"
    if k == "lsp": return "L1"
    return VS[vs_cls[str(i)][0]]
def fit(i):
    o = occ[i]
    if o["kind"] in ("ns", "cns"): return "spills without" if o["song"] in spill_ns else "fits without"
    if o["kind"] == "vspace" and o["arg"].strip().startswith("-"):
        return "spills without" if o["song"] in spill_vneg else "fits without"
    return ""
with open(OUT / "vertical-spacing" / "occurrences.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["song", "line", "macro", "argument", "class", "song without all of this macro", "source line"])
    for i, o in enumerate(occ):
        w.writerow([o["song"], o["line"], "\\" + o["kind"], o["arg"] or "", klass(i), fit(i), o["text"].strip()[:160]])
TITLES = {"ns": "`\\ns`", "cns": "`\\cns`", "vnv": "`\\vnv`", "vinv": "`\\vinv`", "lsp": "`\\lsp`", "vspace": "raw `\\vspace`"}
md = []
for kind in ["ns", "cns", "vinv", "vnv", "lsp", "vspace"]:
    ids = sample[kind]
    md.append(f"\n### {TITLES[kind]}: {len(ids)} sampled contexts\n")
    md.append("<details><summary>Show the samples</summary>\n")
    for n, i in enumerate(ids, 1):
        o = occ[i]; L = (REPO / f"{o['song']}.tex").read_text().split("\n")
        a, b = max(0, o["line"] - 3), min(len(L), o["line"] + 2)
        src = "\n".join(("> " if j == o["line"] - 1 else "  ") + L[j][:110] for j in range(a, b))
        md.append(f"\n**{n}. `{o['song']}` line {o['line']}**, page {o['page']} · class **{klass(i)}**" + (f" · song {fit(i)}" if fit(i) else "") + "\n")
        md.append("```tex\n" + src + "\n```\n")
        md.append(f"![{o['song']} line {o['line']}](vertical-spacing/{o['crop']})\n")
    md.append("\n</details>\n")
extra = json.load(open("extra.json"))
md.append("\n### Extra (not random): the two raw `\\vspace` classes the sample missed\n")
md.append("<details><summary>Show the extra contexts</summary>\n")
for n, i in enumerate([i for v in extra.values() for i in v], 1):
    o = occ[i]; L = (REPO / f"{o['song']}.tex").read_text().split("\n")
    a, b = max(0, o["line"] - 3), min(len(L), o["line"] + 2)
    src = "\n".join(("> " if j == o["line"] - 1 else "  ") + L[j][:110] for j in range(a, b))
    md.append(f"\n**E{n}. `{o['song']}` line {o['line']}**, page {o['page']} · class **{klass(i)}**\n")
    md.append("```tex\n" + src + "\n```\n")
    md.append(f"![{o['song']} line {o['line']}](vertical-spacing/{o['crop']})\n")
md.append("\n</details>\n")
(Path("/home/claude") / "appendix.md").write_text("".join(md), encoding="utf-8")
from collections import Counter
print(Counter((occ[i]["kind"], klass(i)) for i in range(len(occ))))
print("sample classes:", {k: Counter(klass(i) for i in v) for k, v in sample.items()})
