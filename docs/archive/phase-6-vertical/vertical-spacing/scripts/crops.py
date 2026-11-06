"""Render 'as is | without' crops around each sampled occurrence (V1 analysis)."""
import json, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
DPI = 100; S = DPI / 72
PAGE_H = 841.89
ABOVE, BELOW = 95, 125          # pt shown above / below the marker
X0, X1 = 18, 585                # pt, horizontal window (text block incl. hanging labels)
OUT = Path("/home/claude/crops")
occ = json.load(open("occ.json")); sample = json.load(open("sample.json"))
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
def marks(build):
    m = {}
    for line in open(f"{build}/zpevnik.marks"):
        i, x, y, p = line.split(); m[int(i)] = (int(x) / 65536, int(y) / 65536, int(p))
    return m
_cache = {}
def page(build, p):
    key = (build, p)
    if key not in _cache:
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(p), "-l", str(p), "-png", "-q",
                            f"{build}/zpevnik.pdf", f"{d}/p"], check=True)
            _cache[key] = Image.open(next(Path(d).glob("*.png"))).convert("RGB")
    return _cache[key]
def panel(build, mk, label):
    x, y, p = mk
    top = PAGE_H - y - ABOVE
    src = page(build, p)
    box = (int(X0 * S), int(top * S), int(X1 * S), int((top + ABOVE + BELOW) * S))
    im = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), "white")  # white beyond the page edge
    clip = (box[0], max(0, box[1]), box[2], min(src.height, box[3]))
    im.paste(src.crop(clip), (0, clip[1] - box[1]))
    d = ImageDraw.Draw(im)
    my = int(ABOVE * S); mx = max(0, int((x - X0) * S))
    d.polygon([(mx - 9, my - 6), (mx - 9, my + 6), (mx - 1, my)], fill=(0, 110, 255))  # marker: where the macro is
    d.line([(0, my), (8, my)], fill=(0, 110, 255), width=3)
    d.rectangle([0, 0, im.width - 1, im.height - 1], outline=(160, 160, 160))
    d.text((im.width - 10, 6), label, fill=(0, 110, 255), font=FONT, anchor="ra")
    return im
base = marks("/home/claude/instr")
for kind, ids in sample.items():
    var = marks(f"/home/claude/var_{kind}")
    for n, i in enumerate(ids, 1):
        o = occ[i]
        name = "\\" + kind
        a = panel("/home/claude/instr", base[i], "as is")
        b = panel(f"/home/claude/var_{kind}", var[i], f"without {name}")
        im = Image.new("RGB", (a.width * 2 + 12, a.height), "white")
        im.paste(a, (0, 0)); im.paste(b, (a.width + 12, 0))
        im = im.quantize(colors=64)
        fn = OUT / f"{kind}-{n:02d}-{o['song']}.png"
        im.save(fn, optimize=True)
        o["crop"] = fn.name; o["page"] = base[i][2]
json.dump(occ, open("occ_crops.json", "w"), ensure_ascii=False, indent=0)
