# C3 · The two songs that take a second page

`jenamteplo` and `malujzaseobrazky` (batch 11 held them back). Images: `C3-overflow/` (left: now on master, 1 page; middle and right: with `\autochords` and the chord rows as `\chords`).

![jenamteplo](C3-overflow/jenamteplo-overflow.png)

![malujzaseobrazky](C3-overflow/malujzaseobrazky-overflow.png)

## What happens

- `jenamteplo` (p. 235): the last line (`nejde ti spať … R. ×3`) moves to a second page.
- `malujzaseobrazky` (p. 328): the song still fills page 1, but a blank second page follows (only the page number), because the page is full by a hair. The chord row of the first line `I:` also wraps (`F E Am` on its own line).
- Cause in both: the chord-only rows (`I:`, `S:`) were bold text, now they are `\chords` rows, which put 1 em (`\chordrunsep`) between chords, wider than the bold text had. The long rows wrap or grow, and the page overflows. All other 432 songs of the batches fit.

## Options

| | What | Checked |
|---|---|---|
| A | Add `\autochords` but keep the long chord rows as `\textbf{…}` (as on master) | Built: both songs one page, `check_pages` 0 problems, `chord_gaps` 0 errors. Nothing else in the songs changes. The rows convert later with a layout decision in C4. |
| B | `\chords` rows with a narrower `\chordrunsep` for the whole book (e.g. 0.7 em) | Not built. It changes every chord row of the book, so it is a C3a-level design decision, not a song fix. |
| C | Keep `\chords` and pull the song up with `\vspace{-Npt}` (as H5 did for acrosstheuniverse) | Not built. A per-song hack that has to be measured. |
| D | Cut the two rows in the middle (a shorter `\chords` row) | Changes the songbook's content, so it is your call. |

**Recommendation: A.** It is verified, the song text and spacing are the same as the migration would give, and only the two chord rows stay old-style. If you choose A, batch 12 (these two songs) is generated like the others; just answer `A`, `B`, `C` or `D`.
