# The cover of skaut-kravare for the printer

The printer binds the book with rings and prints the cover separately: four A5 pages in CMYK, with
a 3 mm bleed and crop marks. `make print EDITION=skaut-kravare` makes it from this folder, as the
`[print.cover]` table of `../edition.toml` asks ([docs/printing.md](../../../docs/printing.md)).

| Page | What |
|---|---|
| 1 | the front: Klára Horká's drawing with its rough painted edges, on white, 6 mm from the trim top and bottom |
| 2, 3 | the insides: white |
| 4 | the back: beige paper, the scout lily between two rules, "celý zpěvník *Ještě mi chvilku zpívej*", a QR code to <https://zpevnik.hluchnikovi.cz/> and the address, in black ink alone |

## Files

- `design.tex`: the design, read by `make print`.
- `front.jpg` (600 ppi), `paper.jpg` (300 ppi): the pictures of the bleed box, in sRGB; `make print`
  converts them to the printer's CMYK (FOGRA39).
- `lily.pdf`: the scout lily, the glyph ⚜ of FreeSerif as vector art.
- `source/`: what the ingredients are made from, run by hand, never by the build.
  - `scan.jpg`: the illustrator's scan, the whole A5 sheet at 1200 dpi (7089 × 10044 px), as she
    sent it.
  - `make_ingredients.py`: `front.jpg`, `paper.jpg` and the screen PDF's first page
    (`../cover.jpg`) from the scan. The front is the painted area with its rough edges, scaled to
    leave 6 mm to the trim at the top and the bottom, centred on white; the scan is first
    white-balanced on its bare paper, so the paper round the drawing is pure white and meets the
    white page without a faint printed edge. The beige is the mean colour of the sky's light wash
    in the scan, a little more saturated and darker so that it reads as beige; the texture over it
    is generated: soft clouds, mottling, grain and short fibres, each a few per cent of the
    brightness. Needs numpy and Pillow.
  - `lily.tex`: `lily.pdf`, with XeLaTeX (`xelatex -output-directory=.. lily.tex` from `source/`).

## Changing the beige

Two numbers in `source/make_ingredients.py`: `BEIGE_SATURATION` (above 1: more colour, more yellow;
below 1: greyer, nearer white) and `BEIGE_VALUE` (below 1: darker). Change them, run
`python3 make_ingredients.py` from `source/` (it prints the new colour as a hex code), then
`make print EDITION=skaut-kravare`. Small steps are enough: 0.1 in saturation or 0.01 in value is
visible.
