# The cover of skaut-kravare for the printer

The printer binds the book with rings and prints the cover separately: one PDF of four A5 pages, with
bleed and crop marks (D-188, D-192, D-193). This folder holds its source; it is built by hand, not by
`make`.

| Page | What |
|---|---|
| 1 | the front: Klára Horká's drawing with its rough painted edges, on white, 6 mm from the trim top and bottom |
| 2 | the inside of the front: white |
| 3 | the inside of the back: white |
| 4 | the back: beige paper, the scout lily between two rules, "celý zpěvník *Ještě mi chvilku zpívej*", a QR code to <https://zpevnik.hluchnikovi.cz/> and the address |

The edition's own first page (`../cover.tex`) shows the same picture, so the screen PDF opens with it.

## Building

XeLaTeX, from this folder (the paths inside are relative to it), into `build/`:

```sh
cd editions/skaut-kravare/print-cover
mkdir -p ../../../build/print-cover
xelatex -output-directory=../../../build/print-cover preview.tex      # the cover as cut: front and back
xelatex -output-directory=../../../build/print-cover print-cover.tex  # for the printer
```

Run each twice the first time (TikZ places the pictures on the page from the first run).
The fonts come with TeX Live: Alegreya (package `alegreya`) and FreeSerif (`gnu-freefont`).

## Files

- `design.tex`: the front (`\front`), the back (`\back`), their type and colours; shared by both
  documents.
- `preview.tex`: the cover as the reader sees it: A5, cut, no marks.
- `print-cover.tex`: the four pages for the printer: trim 148 × 210 mm, 3 mm bleed, corner crop
  marks 10 mm outside the trim; the PDF names its trim box and bleed box.
- `scan.jpg`: the illustrator's scan of the drawing, the whole A5 sheet at 600 dpi (3527 × 5001 px),
  as she sent it: the source of the front.
- `make_assets.py` and `assets/`: the pictures, each the bleed box (154 × 216 mm) at 300 dpi, made
  from `scan.jpg`:
  - `front.jpg`: the painted area with its rough edges, scaled to leave 6 mm to the trim at the top and
    the bottom, centred on white. The script first white-balances the scan on its bare paper (which
    the scanner gave as 254, not 255), so the paper round the drawing is pure white and meets the
    white page without a faint printed edge. Nothing else of the drawing is changed.
  - `paper-beige.jpg`: the back's paper. Its tone is the drawing's own: the mean colour of the sky's
    light wash in the scan, the same hue, slightly more saturated and darker so that it reads as beige
    rather than off-white (#EDEAD8). The texture over it is generated, not scanned: soft broad clouds,
    fine mottling, grain and short fibres, each a few per cent of the brightness.

  The output is committed; rerun the script (it needs numpy and Pillow) only to change it:
  `python3 make_assets.py`. It gives the same files byte for byte.

## Before it goes to the printer

- The printer's answers: the bleed he wants (3 mm here); whether he wants the front and the back as
  one 4-page PDF or separately; how far from the edge the ring holes go (the drawing starts about
  6 mm from the bound edge, so the holes may go through its edge); and the colours: he asked for CMYK (D-188), and this PDF is RGB. Ask
  which profile to convert to, or whether he converts.
- A test print of the back, the QR code scanned with a few phones.
