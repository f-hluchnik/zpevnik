# Vertical spacing: proposal (V1)

Base: master `88b5205`. Decided in V2 (5 Nov 2026), recorded as D-124. The full analysis (crops, experiments, exactness checks) is in [vertical-spacing/analysis.md](vertical-spacing/analysis.md), for reference only.

**Agreed with the owner (5 Nov 2026):** the spacing in the songs was added ad hoc. Its purpose is to fit one song on one page. The dashed lines separate verses packed tightly to fit, which helps while playing, so they stay; the solid rules in `idzepostaridze` only separate. The gaps inside verses (`\vinv`) are mostly meaningful (like stanza breaks in a poem); each is reviewed per song. The `\vspace` and `\hspace` around score images stay.

## Target

- Blocks are separated by one gap, `\blocksep` (20 pt), defined once in `zpevnik.sty`. **When a song would not fit on its page, TeX shrinks the gaps automatically** (to zero at most).
- Song files contain no vertical spacing, except next to score images.

## What happens to each macro

| Today | Count | Becomes |
|---|---|---|
| `\ns`, `\cns`, negative `\vspace` between blocks | 304 + 40 | deleted (the gap shrinks instead) |
| `\lsp` (dashed line) | 59 | kept, as a separator that replaces the next gap (`\blockrule`, identical output) |
| `\vinv` (gap inside a verse) | 92 | `\groupbreak` (identical output); each one kept or removed in the batch review |
| `\vnv`, `\vspace` between blocks without a label | 30 + 35 | unnumbered verse `\vers{}{…}`, normal gap |
| solid rule in `idzepostaridze` | 2 | `\partrule` |
| `\vspace` next to a score image | 20 | kept |
| other `\vspace` (before a note or recitation, column breaks, a few others) | 38 | deleted; a note or recitation on its own paragraph gets the normal gap; the 2 column breaks become `\columnbreak` |

## Evidence

- Without `\ns`/`\cns`, 74 of the 88 songs using them spill onto a second page.
- With a shrinking gap, only 2 songs spill (`babickamary`, `milionar`, both two-column), even with all `\lsp` deleted too. They get a per-song decision in V8.
- If the gap must stay at least 6 pt, 16 songs spill, including all 6 dashed-line songs.

## Ticket plan (D-124; tickets in TICKETS.md, H6 comes first)

One pass over the songs instead of three (old V5, V7 and the deletions of V8), reviewed in batches like C3b:

- **V3** `\blocksep`, shrinkable from the start. Changes 6 songs slightly (4 two-column, `tophatbarandgrill`, `illbethereforyou`); you review them.
- **V4** Named macros with identical output: `\groupbreak` (for `\\`+`\vinv`), `\blockrule` (for `\lsp`), `\partrule`.
- **V5** Song batches, alphabetical: per song, delete `\ns`/`\cns`/the squeezing `\vspace`, turn unlabelled blocks into `\vers{}{…}`, decide each `\groupbreak` and each remaining `\vspace` (except next to scores). You review every batch.
- **V6** Name the remaining hidden lengths (`\note`, `\sub`, `\hyl`).
- **V7** dropped (merged into V5).
- **V8** Delete the old macros, lint against them, README; decide `babickamary` and `milionar`.
