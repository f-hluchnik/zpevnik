# The cover of skaut-kravare for the printer

The printer binds the book with rings and prints the cover separately: one PDF of four A5 pages
(D-188, D-192, D-193). This folder holds its source; it is built by hand, not by `make`.

| Page | What |
|---|---|
| 1 | the front: Klára Horká's drawing with its rough painted edges, on white, 6 mm from the trim top and bottom |
| 2 | the inside of the front: white |
| 3 | the inside of the back: white |
| 4 | the back: beige paper, the scout lily between two rules, "celý zpěvník *Ještě mi chvilku zpívej*", a QR code to <https://zpevnik.hluchnikovi.cz/> and the address |

The PDF is what the printer asked for (D-188): CMYK, no RGB; 3 mm bleed; the book's crop marks.
The edition's own first page (`../cover.tex`) shows the same drawing, so the screen PDF opens with it.

## Building

From this folder (the paths inside are relative to it), into `build/print-cover/`:

```sh
cd editions/skaut-kravare/print-cover
python3 make_assets.py                                                # the pictures, from scan.jpg
xelatex -output-directory=../../../build/print-cover preview.tex      # the cover as cut: front and back
xelatex -output-directory=../../../build/print-cover print-cover.tex  # for the printer
```

Run each `xelatex` twice the first time (TikZ places the pictures on the page from the first run).
`make_assets.py` needs numpy and Pillow (`python3 -m pip install numpy pillow`); the fonts and the
colour profile come with TeX Live: Alegreya (`alegreya`), FreeSerif (`gnu-freefont`), FOGRA39
(`colorprofiles`).

## Files

- `scan.jpg`: the illustrator's scan, the whole A5 sheet at 1200 dpi (7089 × 10044 px), as she sent
  it. The source of the front and of the beige.
- `make_assets.py`: everything taken from the scan.
  - The front: the painted area with its rough edges, scaled to leave 6 mm to the trim at the top
    and the bottom, centred on white. The scan is first white-balanced on its bare paper, so the
    paper round the drawing is pure white and meets the white page without a faint printed edge;
    nothing else of the drawing is changed. For the printer at 600 ppi in CMYK
    (`build/print-cover/assets/front-print.jpg`), for the screen PDF at 300 ppi in RGB
    (`assets/front-screen.jpg`, committed: `make` needs it).
  - The back's paper (`build/print-cover/assets/paper-beige.jpg`, CMYK): the beige is the mean colour
    of the sky's light wash in the scan, the same hue, a little more saturated and darker so that it
    reads as beige rather than off-white. The texture over it is generated: soft broad clouds, fine
    mottling, grain and short fibres, each a few per cent of the brightness.
  - The ink of the text and the QR code in CMYK (`assets/colours.tex`, committed).
  - CMYK is FOGRA39, the European standard for coated paper, converted with littleCMS (relative
    colorimetric, black point compensation: the usual prepress setting).
- `design.tex`: the front (`\front`), the back (`\back`), their type and colours; shared by both
  documents.
- `preview.tex`: the cover as the reader sees it: A5, cut, no marks.
- `print-cover.tex`: the four pages for the printer: trim 148 × 210 mm, 3 mm bleed, the book's crop
  marks (the `crop` package's `cam` marks, as in `tools/print_pdf.py`) on a 178 × 240 mm page; the
  PDF names its trim box and bleed box. The marks start 5 pt from the trim; the pictures are drawn
  over them, so inside the bleed they are covered.

## Changing the beige

Two numbers in `make_assets.py`: `BEIGE_SATURATION` (above 1: more colour, more yellow; below 1:
greyer, nearer white) and `BEIGE_VALUE` (below 1: darker). Change them, run `python3 make_assets.py`
(it prints the new colour as a hex code), then build the cover again. Small steps are enough: 0.1 in
saturation or 0.01 in value is visible.
