#!/usr/bin/env python3
"""Song-by-song PDF diff between two builds of the songbook.

Usage: python3 tools/pdfdiff.py --base BASE_DIR --head HEAD_DIR [--dpi 72]

Both directories hold a compiled checkout (zpevnik.pdf and the per-song
pisnicky/*.aux files). Pages are mapped to song ids with the page checkpoints
that check_pages.py reads, so a song is compared with itself wherever it sits
in the book. The page-number footer is left out of every comparison. Front
matter and the pages after the last song (the table of contents) are compared
by position, with the colophon date line left out.

Writes a Markdown report to stdout. Differences never change the exit code
(some tickets expect them); it exits 1 only when it cannot do its job.
Needs pdftoppm and pdftotext (poppler). Python >= 3.11, standard library only.
"""
import argparse
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from check_pages import song_pages
from paths import BOOK_PDF

FOOTER_TOP_PT = 805.0  # the page number sits at y = 808-817 pt on an A4 page
MONTHS = {
    "ledna", "února", "března", "dubna", "května", "června",
    "července", "srpna", "září", "října", "listopadu", "prosince",
}
MAX_LISTED = 60


class Build:
    def __init__(self, root: Path, dpi: int, tmp: Path, label: str):
        self.root = root
        self.dpi = dpi
        self.pdf = root / BOOK_PDF
        if not self.pdf.exists():
            raise SystemExit(f"ERROR: {self.pdf} not found")
        ranges, errors = song_pages(root)
        if errors:
            raise SystemExit(f"ERROR ({label}): " + "; ".join(errors[:5]))
        self.songs = {sid: (start, n) for sid, start, n in ranges}
        self.order = [sid for sid, _s, _n in ranges]
        self.first = ranges[0][1]
        self.last_end = ranges[-1][1] + ranges[-1][2]  # first page after the songs
        out = tmp / label
        out.mkdir()
        run(["pdftoppm", "-r", str(dpi), "-gray", str(self.pdf), str(out / "p")])
        self.files = {
            int(re.search(r"-(\d+)\.pgm$", f.name).group(1)): f
            for f in out.glob("p-*.pgm")
        }
        self.pages = len(self.files)
        self.date_bands = self._date_bands()

    def _date_bands(self) -> dict[int, list[tuple[int, int]]]:
        """Pixel rows of lines with a Czech month name on the front pages."""
        bands: dict[int, list[tuple[int, int]]] = {}
        if self.first <= 1:
            return bands
        text = run(["pdftotext", "-bbox", "-f", "1", "-l", str(self.first - 1),
                    str(self.pdf), "-"])
        page = 0
        for line in text.splitlines():
            if "<page " in line:
                page += 1
                continue
            m = re.search(r'yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)">(.*?)</word>', line)
            if m and html.unescape(m.group(3)).lower() in MONTHS:
                bands.setdefault(page, []).append((self._row(float(m.group(1))) - 1,
                                                   self._row(float(m.group(2))) + 2))
        return bands

    def _row(self, y_pt: float) -> int:
        return int(y_pt / 72 * self.dpi)

    def page_pixels(self, page: int, extra_masks: list[tuple[int, int]]) -> bytes:
        """Pixels of a page without the footer and the masked rows."""
        w, h, pix = read_pgm(self.files[page])
        keep_to = min(h, self._row(FOOTER_TOP_PT))
        masked = set()
        for lo, hi in extra_masks:
            masked.update(range(lo, hi))
        return b"".join(pix[r * w:(r + 1) * w] for r in range(keep_to) if r not in masked)


def run(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        raise SystemExit(f"ERROR: {cmd[0]} not found (install poppler-utils)")
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"ERROR: {' '.join(cmd[:2])} failed: {e.stderr[:300]}")
    return r.stdout


def read_pgm(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    pos, tokens = 0, []
    while len(tokens) < 4:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b"#":
            pos = data.index(b"\n", pos)
            continue
        end = pos
        while not data[end:end + 1].isspace():
            end += 1
        tokens.append(data[pos:end])
        pos = end
    if tokens[0] != b"P5" or tokens[3] != b"255":
        raise SystemExit(f"ERROR: unexpected image format in {path}")
    w, h = int(tokens[1]), int(tokens[2])
    pix = data[pos + 1:pos + 1 + w * h]
    return w, h, pix


def pages_equal(base: Build, bp: int, head: Build, hp: int, masks_base=(), masks_head=()) -> bool:
    masks = list(masks_base) + list(masks_head)
    return base.page_pixels(bp, masks) == head.page_pixels(hp, masks)


def fmt_pages(pages: list[int]) -> str:
    out, i = [], 0
    while i < len(pages):
        j = i
        while j + 1 < len(pages) and pages[j + 1] == pages[j] + 1:
            j += 1
        out.append(str(pages[i]) if i == j else f"{pages[i]}–{pages[j]}")
        i = j + 1
    return ", ".join(out)


def listing(title: str, items: list[str]) -> list[str]:
    lines = [f"**{title} ({len(items)})**"]
    if not items:
        return lines + ["", "none", ""]
    shown = items[:MAX_LISTED]
    body = ", ".join(f"`{x}`" for x in shown)
    if len(items) > MAX_LISTED:
        body += f", … and {len(items) - MAX_LISTED} more"
    return lines + ["", body, ""]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--head", required=True, type=Path)
    ap.add_argument("--dpi", type=int, default=72)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        base = Build(args.base.resolve(), args.dpi, tmp, "base")
        head = Build(args.head.resolve(), args.dpi, tmp, "head")

        added = [s for s in head.order if s not in base.songs]
        removed = [s for s in base.order if s not in head.songs]
        common = [s for s in head.order if s in base.songs]

        changed, moved = [], []
        for sid in common:
            (bs, bn), (hs, hn) = base.songs[sid], head.songs[sid]
            if bn != hn or not all(
                pages_equal(base, bs + k, head, hs + k) for k in range(hn)
            ):
                changed.append(f"{sid} (p. {hs}" + (f", {bn}→{hn} pages)" if bn != hn else ")"))
            if bs != hs:
                moved.append((sid, hs - bs))

        # moved songs, grouped into runs of the same page offset (head order)
        runs: list[tuple[int, list[str]]] = []
        for sid, delta in moved:
            if runs and runs[-1][0] == delta and head.order.index(runs[-1][1][-1]) + 1 == head.order.index(sid):
                runs[-1][1].append(sid)
            else:
                runs.append((delta, [sid]))

        # front matter and back matter, compared by position
        diff_pages: list[int] = []
        for p in range(1, min(base.first, head.first)):
            masks = base.date_bands.get(p, []) + head.date_bands.get(p, [])
            if not pages_equal(base, p, head, p, masks):
                diff_pages.append(p)
        base_back = list(range(base.last_end, base.pages + 1))
        head_back = list(range(head.last_end, head.pages + 1))
        for bp, hp in zip(base_back, head_back):
            if not pages_equal(base, bp, head, hp):
                diff_pages.append(hp)
        front_note = ""
        if base.first != head.first:
            front_note = f" Front matter length differs: {base.first - 1} → {head.first - 1} pages."
        back_note = ""
        if len(base_back) != len(head_back):
            back_note = f" Pages after the songs: {len(base_back)} → {len(head_back)}."

    out = ["## Song-by-song PDF diff", ""]
    out.append(f"Base: {base.pages} pages, {len(base.songs)} songs · "
               f"Head: {head.pages} pages, {len(head.songs)} songs · "
               f"unchanged songs: {len(common) - len(changed)}")
    out.append("")
    out += listing("Changed songs", changed)
    out += listing("Added songs", added)
    out += listing("Removed songs", removed)
    out.append(f"**Moved songs ({len(moved)})**")
    out.append("")
    if runs:
        for delta, sids in runs[:MAX_LISTED]:
            span = f"`{sids[0]}`" if len(sids) == 1 else f"`{sids[0]}` … `{sids[-1]}`"
            out.append(f"- {len(sids)} song(s) moved by {delta:+d} page(s): {span}")
        if len(runs) > MAX_LISTED:
            out.append(f"- … and {len(runs) - MAX_LISTED} more runs")
    else:
        out.append("none")
    out.append("")
    out.append("**Changed pages outside the songs** (front matter and table of contents, PDF page numbers of the head)")
    out.append("")
    out.append((fmt_pages(diff_pages) if diff_pages else "none") + front_note + back_note)
    out.append("")
    out.append("_Compared as grayscale renders at "
               f"{args.dpi} dpi; page-number footers and the colophon date are ignored. "
               "Footnote numbers run through the whole book, so adding or removing a song "
               "with a footnote changes every later song that has one._")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
