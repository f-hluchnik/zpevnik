# Phase 3 tickets: print (done 11–12 Nov 2026, except P1 and P4)

The ticket texts and status rows as they were when the work ended: the feasibility report, the cancelled licensing check, and the print build. **P1** (the owner's and the printer's answers) and **P4** (the proof on the final content) are still open and stay in [TICKETS.md](../../TICKETS.md). Summary: [HISTORY.md](../../HISTORY.md).

| Ticket | Status | Notes / PR |
|---|---|---|
| P0 | done | print feasibility report with the printer checklist: `docs/p0-print-report.md` (PR #113); the geometry trial stays a one-off branch (D-154) |
| P2 | cancelled | the book is never sold (D-140) |
| P3 | done | the scaled print: output formats `print`, `print-black` (D-154, PR #114), page numbers in the contents and `\seealso` (D-155, PR #115), the A5 PDF with the spine shift and `make print` (D-156, PR #116); the geometry trial stays a one-off branch, only if the scaled text is too small on paper. P4 comes on the final content |

### P0 · Print feasibility report — [agent] · M · needs the print edition (the owner prepares it by hand, D-148)
D-147, D-142. The owner expects the facts for P1 to come out of this: does the book work at A5, and what has to be asked of the printer. Nothing is decided and nothing is merged; the output is a report with attachments.
1. **Scaled sample:** the print edition's screen PDF scaled to A5 (1/√2), about ten pages (a dense song, a two-column song, a score, the contents), and the page counts at A4 and A5; the owner prints the A4 PDF "2 per sheet" to see the size on paper (D-142).
2. **Geometry trial:** the print edition built once with an A5 page geometry (a first run on the full book gave the numbers in D-148; the trial needs only the songs of the print edition, which may not contain the problematic ones). No copy of `zpevnik.tex`: the geometry is a parameter like the edition, and how it reaches the document is proposed in the PR before coding. The one-page check on it; every song that spills listed with a proposed fix per song (a `\large` as D-129 allows, a two-page allow-list entry), never fixed silently; a few pages of both versions side by side.
3. **Printer checklist**, ready to send as it is: page count and binding limits (the book is about 760 pages at A4), ring or glued binding and the gutter, paper weight and the thickness of that many pages, PDF version or PDF/X, fonts, colour or black and white, bleed and crop marks, cover in the file or separate, a proof copy, number of copies and price.
**Expected differences:** none for the screen PDF. The report is cheap to repeat: run it again after the owner's new songs.

### P2 · Licensing check — [you] · S — **cancelled**
Was: check the licensing before selling printed copies. The book is never sold (D-140).

### P3 · Print build — [agent] · M · needs P0, P1 (and E4 for a subset)
D-142. The print format is a step after the build, separate from the edition (D-139): it combines with the full book or any edition and writes into an output directory of its own; no copy of song content.
1. **Scaled print (the default):** scale the edition's screen PDF to the print page size from P1 (A4 to A5 is exactly 1/√2), with the offset of odd and even pages for the binding if P1 asks for it, blank pages where a spread needs them (songs starting on a right-hand page, an even page count), and the cover outside the numbered book block if P1 says so. Use what the pinned TeX Live has (`pdfpages` in a small wrapper document, or `pdfjam`); no new dependency. Check page size and page count; the contents links still work.
2. **Geometry trial:** done in P0. If the owner picks it, P3 makes it an option of the print format (merged only if he picks it); the scaled print stays the default.
**Expected differences:** none for the screen PDF.
