# P0 · Print feasibility report (draft)

Session 21c, 11 Nov 2026. A report, not a change of the book: nothing here is merged unless the owner picks it (D-147, D-148). This first version holds what was measured so far and the proposal for the geometry trial, which waits for the owner's OK before any code is written.

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

1. **Output formats `print` and `print-black`** (PR #114): the "→ obsah" label and the arrow before the artist are left out (the artist stays, grey); black chords as an option. Screen PDF unchanged.
2. **Page numbers** in the contents, the artist index and the `\seealso` lines of the print formats (a printed contents without them cannot be used; today the contents is hyperlinks only).
3. **Scaling step** to A5 with the binding offset (opposite directions on odd and even pages, the printer names the clear margin the rings need) and an even page count; the cover stays outside.
4. **Geometry trial** (A5 typeset, `\large` first, bigger chord superscripts, songs spilling on purpose and starting on a left-hand page so the spread is read without a page turn) only on a one-off feature branch, and only if the scaled text (about 10.2 pt) is too small on paper.

Measured so far for the trial (scratch copy, indicative): A5 with the A4 margins × 0.707: `\Large` 224 pages / 58 of 152 songs spill, `\large` 173 / 7, `\normalsize` 169 / 3.

Smallest text after scaling: footnote text 8 pt → about 5.7 pt and its number 6 pt → about 4.2 pt (9 pages of the edition: 11, 17, 43, 55, 73, 80, 106, 111, 131); the imprint 7 pt → about 5 pt; chord superscripts about 10 pt → about 7 pt.

## 4. Printer checklist

To be written after the trial; it needs the page count of the chosen variant.
