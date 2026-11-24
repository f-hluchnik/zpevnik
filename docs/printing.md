# Printing an edition

Any edition can go to a printer. What the printer needs is written in the edition's
`edition.toml`; one command makes the files:

```
make print EDITION=skaut-kravare
```

They go to `build/print/<edition>/`, named with the edition and the version:

| File | What |
|---|---|
| `zpevnik-<edition>-<version>-blok.pdf` | the book block: every page of the book between the covers |
| `zpevnik-<edition>-<version>-obalka.pdf` | the cover, printed separately (with a `[print.cover]` table) |
| `zpevnik-<edition>-<version>-nahled.pdf` | the book as the reader will see it: the cover round the block, every page cut, no marks; for looking at, not for the printer |

Each `make print` empties the folder first, so it holds exactly what the printer gets. Without the
full Git history the build number is unknown and the names have `x` in its place (`8.49.x`).

## What `make print` does

1. Reads the edition's `[print]` table and chooses the format the book is typeset in
   (below: *Ink and colour*).
2. Builds the book in that format on A4, with the same checks as `make check`: every song on one
   page, no overlapping chords, no wrapped lines.
3. Places the pages on the printer's paper: it measures how far the ink reaches on every page and
   works out one scale and one shift away from the spine that keep the margins on every page. The
   book is only ever made smaller, so every song still fits its page.
4. Checks the finished block and stops with the page numbers if anything is wrong (below:
   *Checks*). It prints how close the ink comes to the spine and to the outer edge, measured on
   the finished file, e.g. `the ink is at least 12.53 mm from the spine and 4.58 mm from the
   outer edge`.
5. With a `[print.cover]` table, makes the cover from the edition's design, checks it, and makes
   the preview.

## The block

Every key is optional; without the table an edition is printed on A4, in colour, with its cover,
as it is on the screen. `skaut-kravare` has:

```toml
[print.block]
paper = "A5"
ink = "black"
crop_marks = true
spine_margin_mm = 12.5
outer_margin_mm = 4.5
```

| Key | Default | Meaning |
|---|---|---|
| `paper` | `"A4"` | The trimmed page: `"A4"` or `"A5"`. On A5 the A4 pages are scaled down to about 70 %. |
| `spine_margin_mm` | `0` | No ink closer than this to the bound edge (left on odd pages, right on even ones). |
| `outer_margin_mm` | `0` | No ink closer than this to the outer edge. |
| `ink` | `"colour"` | `"black"`: everything in black ink alone, for a one-colour press. |
| `colour` | `"rgb"` | With colour ink: `"rgb"` or `"cmyk"` (below). |
| `profile` | `"FOGRA39"` | With `colour = "cmyk"`: the colour profile of the printer's press and paper; `"FOGRA39"` or a `.icc` file the printer gives, its path relative to the edition's folder. |
| `cover` | `true`, `false` with a `[print.cover]` table | Whether the book's own cover and its blank back start the block. Without them the pages count from the half-title, as in a printed book. |
| `crop_marks` | `false` | Crop marks in the corners, on a PDF page 15 mm larger on every side than the trimmed page. |
| `bleed_mm` | `0` | How far beyond the trimmed page the printing may reach. Only a page printed to its edge needs it; with crop marks at most 15. |

The PDF names the trimmed page (its *trim box*) and the bleed (its *bleed box*), so the printer's
software knows where to cut. Leave a margin's worth to spare: the cut is never exact. A printer who
asks for 12 mm gets `12.5`.

## The cover

A cover printed separately is four pages: the front, the inside of the front, the inside of the
back and the back. It is drawn from the edition's own design:

```toml
[print.cover]
design = "print-cover/design.tex"
paper = "A5"
colour = "cmyk"
crop_marks = true
bleed_mm = 3
```

`design` (required) is a `.tex` file in the edition's folder, its path relative to that folder.
The other keys are the block's and mean the same: `paper`, `colour`, `profile`, `crop_marks`,
`bleed_mm`.

The design is read into a pdfLaTeX document with TikZ, graphicx and xcolor loaded, and loads
anything else it needs. It defines a command for each page:

| Command | Page |
|---|---|
| `\zpcoverfront` | the front (required) |
| `\zpcoverinsidefront` | the inside of the front (white if not defined) |
| `\zpcoverinsideback` | the inside of the back (white if not defined) |
| `\zpcoverback` | the back (required) |

Each draws its page inside a TikZ picture over the whole page, where `(zpcovertrim)` is the lower
left corner of the trimmed page and `\zpcovertrimwidth`, `\zpcovertrimheight` and `\zpcoverbleed`
are lengths. A picture printed to the edge covers the bleed too. `editions/skaut-kravare/print-cover/`
is an example.

**Pictures** are the design's ingredients, committed next to it and found by name
(`\includegraphics{front.jpg}`). Give them as RGB JPEGs: for a cover in CMYK, `make print`
converts every JPEG of the design's folder to the printer's CMYK with the profile. A picture made
from something else (a scan, a script) keeps its source and the script in a subfolder, which
`make print` does not read. Vector art can be a PDF. Text, rules and QR codes are best in black ink
alone, `\definecolor{...}{cmyk}{0,0,0,1}`: a dark colour mixed from four inks is never as sharp.

## Ink and colour

- **Black ink** (`ink = "black"`): the chords are black, and so are the chords inside the scores
  (each score image has a black-ink version, made by `make`). The grey artist names stay grey:
  grey is printed with the same black ink, only lighter.
- **RGB colour** (the default): the PDF as it is on the screen, red chords included. Fine for a
  home or office printer; most print shops want no RGB.
- **CMYK colour** (`colour = "cmyk"`): the red of the chords is converted to the printer's CMYK
  with the profile, and the scores use their black-ink images, so their notes are printed in black
  ink alone rather than in a mix of four inks. A cover's pictures are converted the same way. The
  conversion needs Pillow (`requirements-dev.txt`).

A CMYK file still looks right on a screen: it stores how much of each ink to print, and the viewer
works out the screen colour from it. The colours on the screen are a viewer's guess; only a proof
from the printer shows the real ones.

A colour photo or drawing cannot go into a black-ink or CMYK block: the check refuses an RGB image.
Such an edition prints its cover separately (`[print.cover]`), which leaves the book's own cover out
of the block.

## Checks

The block and the cover must have:

- the trimmed page of the paper asked for, the bleed box and the room for the crop marks the table
  asks for;
- every font embedded;
- in black ink or CMYK, no image in RGB.

The block must also have:

- an even page count (a blank page is added at the end when the book has an odd one);
- no ink closer to the spine or the outer edge than the margins. Every page is rendered at 300 dpi
  inside its trimmed page, and any pixel that is not pure white is ink: letters, scores, lines,
  QR codes. The measure is good to about a pixel (0.085 mm), so the pages are placed with a pixel
  to spare;
- with black ink, black ink alone on every page (Ghostscript's ink coverage).

The cover must have four pages. Its margins are not checked: a design may print to the edge.

## Checking the PDF yourself

- **With a ruler:** print an odd and an even page of the block at actual size ("Actual size" or
  "100 %" in the print dialogue, not "Fit") and measure from the crop mark to the nearest letter.
- **With the printer:** ask for a preflight before printing; it confirms the margins and the inks.
  In Adobe Acrobat Pro, *Output Preview* shows the separations: a black-ink block has ink on
  *Black* only.
- **With a proof:** one test print shows everything at once, the real cut included.

## Asking a new printer

What to ask, and the key each answer goes to:

| Question | Key |
|---|---|
| What size is the trimmed page? | `paper` |
| How close to the spine and to the edge may text be? | `spine_margin_mm`, `outer_margin_mm` |
| One colour (black) or full colour? In CMYK? With which profile? | `ink`, `colour`, `profile` |
| Do you print the cover separately? | `[print.cover]` |
| Crop marks? Bleed, and how much? | `crop_marks`, `bleed_mm` |
