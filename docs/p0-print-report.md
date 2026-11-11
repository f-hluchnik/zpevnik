# P0 · Print feasibility report

Session 21c, 11 Nov 2026. A report, not a change of the book (D-147, D-148): it holds what was measured, the plan the owner agreed, and the checklist for the printer (section 4). The scaled print it led to is built (D-154, D-155, D-156); the geometry trial is not built and stays a one-off branch (section 3, item 4).

The print edition is `editions/skaut-kravare/` (152 songs, "Skautský zpěvník, oddíl Kravaře"), the only hand-made edition (D-148).

## 1. Scaled sample (done)

| | A4 (screen PDF) | A4 scaled to A5 (× 1/√2) |
|---|---|---|
| Pages | 164 | 164 |
| Page size | 595.3 × 841.9 pt | 419.5 × 595.3 pt |
| Body text | `\Large` of a 10 pt class = 14.4 pt | ≈ 10.2 pt |
| One-page rule | `make check`: 152 songs, 0 problems | holds by construction |

The full book at A4 is 764 pages today (D-148 had 763).

Scaling was done with `pdfpages` in a small wrapper document (`\includepdf` with `scale=0.70710678`, no new dependency); the A5 page size came out exactly as above. Sent to the owner in the session, not committed (binary files, TICKETS *Working environment*): the 10-page sample (cover, imprint, a score, a plain song, a `\large` song, a two-column song, a dense song, the contents), the whole scaled PDF, and the A4 PDF for printing "2 per sheet" (D-142).

## 2. Geometry trial: measured so far (indicative, scratch copy outside the repository)

A5 page, margins of the A4 book × 0.707 (top 1.06, bottom 1.41, left 1.41, right 0.71 cm), the print edition only, the real geometry reaching the document through a macro (section 3).

| Body size | Pages | Songs that spill to a second page (of 152) |
|---|---|---|
| `\Large` (today's) | 224 | 58 |
| `\large` | 173 | 7 |
| `\normalsize` | 169 | 3 |

So with today's body size and no per-song fixes, the A5 geometry is not an option for this edition: 38 % of the songs spill. The scaled print has none, by construction. The full list of spilling songs with a proposed fix per song, and the side-by-side pages, come after the owner's OK on section 3.

## 3. Plan agreed with the owner (11 Nov 2026, supersedes the earlier proposal)

The default is the scaled print. Hiding the links and black chords cannot be done on a finished PDF, so the scaled print needs a *print variant* of the A4 document; that variant is the build-time macro mechanism (D-154) that a geometry trial would reuse.

1. **Output formats `print` and `print-black`** (PR #114, D-154): the "→ obsah" label and the arrow before the artist are left out (the artist stays, grey); black chords as an option. Screen PDF unchanged.
2. **Page numbers** in the contents, the artist index and the `\seealso` lines of the print formats (PR #115, D-155; a printed contents without them cannot be used). One entry alignment for every format.
3. **Scaling step** to A5 with a symmetric spine shift and an even page count; the cover stays outside (PR #116, D-156: `make print`, `tools/print_pdf.py`).
4. **Geometry trial** (A5 typeset, `\large` first, bigger chord superscripts, songs spilling on purpose and starting on a left-hand page so the spread is read without a page turn) only on a one-off feature branch, and only if the scaled text (about 10.2 pt) is too small on paper, or the printer needs more margin than scaling can give (section 5).

Measured so far for the trial (scratch copy, indicative): A5 with the A4 margins × 0.707: `\Large` 224 pages / 58 of 152 songs spill, `\large` 173 / 7, `\normalsize` 169 / 3.

Smallest text after scaling: footnote text 8 pt → about 5.7 pt and its number 6 pt → about 4.2 pt (9 pages of the edition: 11, 17, 43, 55, 73, 80, 106, 111, 131); the imprint 7 pt → about 5 pt; chord superscripts about 10 pt → about 7 pt.

## 4. Printer checklist

### What is ready (the facts to give the printer)
- A5 portrait (148 × 210 mm), about 162 pages without the cover (164 with it); two-sided, so about 81 sheets. Ring binding, the cover a separate image.
- Vector PDF: all fonts embedded (`pdffonts`, 23 of 23 on the A5 file), no raster images in the book block except what the printer sees in the cover.
- Colour: the red chords and the grey labels in `print`; everything black and white except the grey in `print-black` (the grey stays). Both files come from the same sources.
- Nothing reaches the page edge: the page is white and the ink starts 7.1 mm inside every edge, so no bleed is built in.
- Page numbers are printed; the contents and the "see also" lines carry them; no links are shown.
- The smallest text after scaling: footnotes about 5.7 pt (9 pages), the imprint about 5 pt, chord superscripts about 7 pt; the body text about 10.2 pt.

### What only the printer can decide (ready to send, Czech)
1. **Kroužková vazba:** kolik mm od hřbetu musí zůstat volných pro děrování a kroužky, a na které straně se děruje? Kniha má nyní stejné okraje na všech stranách (text je 7,1 mm od okraje A5, tj. celkem 14,2 mm k rozdělení mezi hřbet a vnější okraj). Pokud vám to nestačí, pošleme jiný soubor.
2. **Nepotisknutelný okraj:** jak blízko k oříznutému okraji se při vašem stroji spolehlivě tiskne (tisk těsně u okraje, ořez)?
3. **Formát souboru:** stačí běžné PDF s vloženými písmy, nebo požadujete PDF/X (X-1a, X-4)? Jaký barevný prostor (RGB, nebo CMYK, kdo převádí)?
4. **Spadávka a ořezové značky:** jsou potřeba? (Na stránkách nic nesahá do kraje, spadávku nepotřebují.)
5. **Barva:** cena černobílého tisku, tisku s barevnými akordy (červená) a plnobarevného; má smysl rozlišovat?
6. **Papír:** gramáž a typ pro oboustranný tisk, tloušťka bloku asi 81 listů, největší blok, který kroužek unese (průměr kroužku).
7. **Obálka:** samostatný obrázek: rozměr a rozlišení, přední a zadní strana, potisk, průhledná fólie nebo lamino, kdo ji spojí s blokem.
8. **Nátisk:** lze vytisknout jeden zkušební výtisk a za kolik, jak dlouho trvá?
9. **Náklad, cena, termín** a způsob předání souborů.

### What the owner decides (P1, recorded as a DECISIONS entry)
- The **deadline** (17 Nov 2026 was a target for the review rounds, D-148).
- **Is the scaled text readable on paper?** Print the A4 PDF "2 per sheet" (D-142). No: the geometry trial, on a feature branch.
- **Colour or black** by the price: `make print FORMAT=print` or `FORMAT=print-black`.
- **The spine shift** (`--spine-shift-mm`), after the printer's answer to question 1; **the cover** (`--skip-first`, an even number); **the number of copies**.
- **The proof** (P4), on the final content (the owner's new songs), signed off by the owner.

## 5. If scaling needs more margin: scale further (theoretical)

Uniform scaling by 1/√2 gives the ink 7.1 mm at each edge; scaling the pages further, by a factor s below 1 around the page centre, would widen both margins and shrink the text by the same factor:

| s | Room for spine + outer edge | Body | Footnotes | Imprint | Chord superscripts |
|---|---|---|---|---|---|
| 1.00 (today) | 14.2 mm | 10.2 pt | 5.7 pt | 5.0 pt | 7.0 pt |
| 0.95 | 20.9 mm | 9.7 pt | 5.4 pt | 4.8 pt | 6.7 pt |
| 0.92 | 24.9 mm | 9.4 pt | 5.2 pt | 4.6 pt | 6.4 pt |
| 0.90 | 27.6 mm | 9.2 pt | 5.1 pt | 4.5 pt | 6.3 pt |

(Arithmetic from the measured widths: ink 134.3 mm wide on a 148.5 mm page; not built.) It would be a single option in `tools/print_pdf.py`, but it buys the margin with the very thing that is already too small, and the vertical margins grow for nothing. The typeset geometry (section 3, item 4) gives the room only where it is needed, at the spine, and keeps or enlarges the text; it costs spilling songs. So: scale further only if the paper test says the 10.2 pt text is comfortable and the printer needs a little more room.
