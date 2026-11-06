r"""Copy the repo and insert a position marker before selected occurrences (V1 analysis only).

usage: instrument.py SRC DST [--drop KIND:IDX,...]
Every occurrence gets \zpmark{IDX}; occurrences listed in --drop are also removed
(the macro and its argument), to render the page "without" them.
"""
import json, re, shutil, sys
from pathlib import Path
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
drop = set()
if len(sys.argv) > 3:
    drop = {int(x) for x in sys.argv[4].split(",") if x}
occ = json.load(open(Path(__file__).parent / "occ.json"))
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", "zpevnik.pdf", "*.aux", "*.log", "*.fls", "*.fdb_latexmk"))
sty = dst / "zpevnik.sty"
MARK = r"""\pdfminorversion=7
\newwrite\zpmarks\AtBeginDocument{\immediate\openout\zpmarks=\jobname.marks\relax}
\newcommand{\zpmark}[1]{\pdfsavepos\write\zpmarks{#1 \the\pdflastxpos\space\the\pdflastypos\space\thepage}}"""
sty.write_text(sty.read_text().replace(r"\pdfminorversion=7", MARK, 1))
by_file = {}
for i, o in enumerate(occ):
    by_file.setdefault(o["song"], []).append((i, o))
def arg_end(text, p):
    """index after the {...} argument starting at or after p"""
    q = text.index("{", p); lvl = 0
    while True:
        c = text[q]
        if c == "{": lvl += 1
        elif c == "}":
            lvl -= 1
            if lvl == 0: return q + 1
        q += 1
for song, items in by_file.items():
    f = dst / "pisnicky" / f"{song}.tex"
    text = f.read_text(encoding="utf-8")
    starts = [0] + [k + 1 for k, c in enumerate(text) if c == "\n"]
    for i, o in sorted(items, key=lambda t: -(starts[t[1]["line"] - 1] + t[1]["col"])):
        p = starts[o["line"] - 1] + o["col"]
        if i in drop:
            name = "\\" + o["kind"]
            end = arg_end(text, p) if o["kind"] in ("vspace", "lsp") else p + len(name)
            text = text[:p] + f"\\zpmark{{{i}}}" + text[end:]
        else:
            text = text[:p] + f"\\zpmark{{{i}}}" + text[p:]
    f.write_text(text, encoding="utf-8")
