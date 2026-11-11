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

## 3. Proposal: how the A5 geometry reaches the document (needs the owner's OK)

**Mechanism.** Next to `\zpgenerated`, the build defines two more macros with `-usepretex`:

- `\zpgeometry`, the option list of the `geometry` package, including the paper (`a5paper, top=…, left=…`);
- `\zpbodysize`, the name of the size declaration that wraps the songs.

`zpevnik.sty` and `zpevnik.tex` give both a default with `\providecommand` (today's margins, `Large`), so a build without them stays as it is today. No copy of `zpevnik.tex`. Checked in the scratch copy: the paper option of `geometry` overrides the `a4paper` of `\documentclass`, and the output is 419.5 × 595.3 pt.

**Build side.** A *format* (D-139: never part of an edition) is a named set of those two values, kept as constants in one small module of `tools/`; `tools/build_edition.py` and the checks get `--format <name>`; every combination has its own output directory (D-139). This is the concept P3 needs anyway (the scaled print would be another format), so the trial does not build a throwaway.

**Alternatives rejected.** A copy of `zpevnik.tex` (forbidden by the ticket). Geometry in `edition.toml` (D-139: an edition never chooses geometry). An environment variable (hidden state, not visible in the latexmk command, and TeX would need an extra package to read it).

**Variants to run on the print edition** (each with the one-page check, the spill list, the page count): body `\Large` and `\large`; margins × 0.707 and 15 mm / 10 mm (left / right; the book is one-sided, the binding offset is P1's). Per-song `\large` as D-129 allows, or a two-page allow-list entry, only proposed in the report, never applied.

**If the owner does not pick the geometry**, the branch of the trial is simply not merged; only this report (or nothing) stays.

**Not verified yet:** that a build without the two macros is byte-identical to today's (to be checked with the PDF diff before the trial is committed); that `check_pages.py` and `chord_gaps.py` work with a format's output directory.

## 4. Printer checklist

To be written after the trial; it needs the page count of the chosen variant.
