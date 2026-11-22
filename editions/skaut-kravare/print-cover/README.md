# The cover of skaut-kravare for the printer

The printer binds the book with rings and prints the cover separately: one PDF of four A5 pages, with
bleed and crop marks (D-188, D-192). This folder holds its source; it is built by hand, not by `make`.

| Page | What |
|---|---|
| 1 | the front: the illustrator's drawing, `../cover.jpg` (a grey placeholder until the scan is there) |
| 2 | the inside of the front: white |
| 3 | the inside of the back: white |
| 4 | the back: the design `\chosenback` in `print-cover.tex`, one of the six in `back.tex` |

The back carries the way to the online songbook: "celý zpěvník *Ještě mi chvilku zpívej*", a QR code
to <https://zpevnik.hluchnikovi.cz/> and the address. It replaces the book's last page (D-180).
The six designs are made in TeX and generated pictures only, nothing taken from the drawing, so they
are a fallback in case the illustrator does not draw the back herself.

## Building

XeLaTeX, from this folder (the paths inside are relative to it), into `build/`:

```sh
cd editions/skaut-kravare/print-cover
mkdir -p ../../../build/print-cover
xelatex -output-directory=../../../build/print-cover proposals.tex    # the six backs, A5 as cut
xelatex -output-directory=../../../build/print-cover print-cover.tex  # for the printer
```

Run each twice the first time (TikZ places the pictures on the page from the first run).
The fonts come with TeX Live: Alegreya (package `alegreya`) and FreeSerif (`gnu-freefont`).

## Files

- `back.tex`: the type, the colours, the QR code and the six back designs (`forest`, `row`, `lily`,
  `moss`, `paper`, `frame`), shared by both documents.
- `proposals.tex`: the six designs, one A5 page each, for choosing.
- `print-cover.tex`: the four pages for the printer: trim 148 × 210 mm, 3 mm bleed, corner crop
  marks 10 mm outside the trim; the PDF names its trim box and bleed box.
- `make_assets.py` and `assets/`: the paper textures (300 dpi over the bleed box) and the spruce
  rows. The output is committed; rerun the script (it needs numpy and Pillow) only to change them.

## Before it goes to the printer

- The scan of the drawing at 300 dpi or more, cropped to the bleed box (154 × 216 mm) with the
  paper's edges cut off, saved as `editions/skaut-kravare/cover.jpg`. A taller scan loses as much at
  the top as at the bottom; a wider one would leave a gap, so crop it.
- The owner's choice of the back (`\chosenback`), or the illustrator's own back instead.
- The printer's answers: the bleed he wants (3 mm here) and the colours: he asked for CMYK
  (D-188), and this PDF is RGB. Ask which profile to convert to, or whether he converts.
- A test print of the back, the QR code scanned with a few phones.
