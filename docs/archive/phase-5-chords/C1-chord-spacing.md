# C1 · Automatic chord spacing: prototype and assessment

**Decided:** path A, with the details in DECISIONS D-123 (owner, 4 Nov 2026). Since then: in-word pauses are removed, not `\gap`; `\chords` (red) is used only for whole chord-only lines and `\textbf` chords; the hyphen switch and the `\gap` hyphen logic are dropped.

Session 9, 4 Nov 2026 (second iteration, after the owner's review). Branch `proto/c1-chord-spacing`, draft PR #42 (do not merge). Input for the owner's gate **C2**.

**Files in [C1-chord-spacing/](C1-chord-spacing/):**
- `C1-13-songs-master.pdf` and `C1-13-songs-prototype.pdf`: the 13 songs as real compiled PDFs, from master and from the prototype, with page numbers as in the full book.
- `C1-13-songs-master-vs-prototype.pdf`: the same pages interleaved (master, prototype, master, …).
- `C1-full-book-prototype.pdf`: the whole book with the prototype `\chord`. Only the 13 songs had their manual spacing removed.
- `<song>-before-after.png`: quick previews.

The book-wide lists (every place C3 would change, the cases to check, chords written without `\chord`) are in [C1-review-lists.md](C1-review-lists.md).

## The 13 test songs

The top 10 by `\nc+\mm+\sm`: otazky, lonelystranger, soske, ringoffire, rekalasky, letniukolebavka, jednourano, chcibytpritom, cervenareka, bratrickuzavirejvratka. Plus nejlipjimbylo, zafukane and goodriddance (chord-only lines). The A1 totals still match: 712/319/254 in 303 songs.

## How it works

`\chord{X}text` keeps its syntax and its zero-width chord box. The changes:
1. **Lookahead, single pass.** After placing the chord, `\chord` reads the tokens up to the next `\chord` (or `\chords`, `\\`, `}`, `\par`, `\end`, `\begin`). It measures them in a box, with footnotes switched off so counters don't move, and puts them back **unchanged**. Line breaking, hyphenation and footnotes work as before.
2. **Pad only where needed.** If the next chord would start closer than this chord's width + `\chordsep` (0.5em), a pad goes in right before it. When there is no text between the two chords (chord-only lines, runs), the gap is `\chordrunsep` (1em). This is PLAN WP2's rule: a chord and its text occupy max(text width, chord width + `\chordsep`). Text does not move where nothing would collide.
3. **Hyphen in a split word.** A pad between two letters gets a centred hyphen, and is widened to fit it if needed (a bare gap inside a word reads as a word break). It works for Czech letters too. `\zpchordhyphenfalse` turns it off.
4. **`\gap{n}`** for deliberate gaps (pauses), n in characters of 0.5em. Right after a chord inside a word it also gets the hyphen ("setmě - lo").
5. **`\chords{E F\kk m\7 Am\6\bas{E} E}`** sets chords inline on one line, in chord style, spaced by `\chordrunsep`. It's for the places that today use plain `\textbf{…}`. It's tried in the prototype on lonelystranger's intro and cervenareka's two line ends, in red. Whether these should be red or black is still open.
6. `\zpchordspacingfalse` restores the old behaviour (no pads). It is the natural per-song switch for C3 path A. `\zpchordtracetrue` writes chord positions to a separate file for `tools/chord_gaps.py`; it's off by default and nothing reads it back.

About 110 lines in `zpevnik.sty`, no new packages, no .aux state, no extra passes.

### Why not `\pdfsavepos` (the first iteration)

The first prototype recorded each chord's position in the .aux and padded on the next pass. It was dropped, for three reasons:
- **It needed more passes:** 4 from clean instead of 2.
- **It didn't converge.** On the fully stripped book, latexmk gave up after 5 passes (paradaII needed a 6th). Lines TeX justifies make positions depend on the pads, so convergence can't be guaranteed.
- **Its premise was wrong.** I had assumed a lookahead can't see through `\rep{…}` and similar groups. Measured: only **25 of 12,676** same-line chord pairs have a brace boundary between them, and with all manual spacing removed only **1 of 1,674** needed pads does (tasidele). The lookahead gets the same result in one pass.

### Honest assessment of the lookahead

- **Strengths.** Single pass, deterministic, local to `\chord`. The text is re-read, never re-typed, which is proven book-wide: with padding off, all 17,154 chords go through the scanner and the PDF is **identical to master** (733 songs unchanged).
- **Limitation 1.** It can't measure across a brace boundary. When the text after a chord ends at a `}` that is not a line end (e.g. the end of `\rep{…}`) and another chord follows on the same line, it doesn't pad. That is 25 places today; none collides now, and 1 (tasidele) would after C3. It's easy to lint, or to fix in the source.
- **Limitation 2.** Measurement uses natural word spacing. On lines TeX justifies (lines too long, which wrap), shrinking can bring chords slightly closer than 0.5em; the smallest gap in the book is 4.2 pt (zkratky). They never overlap.
- **Cost.** Every chord's text is set twice, once to measure and once for real. A clean build of the full book takes 15.3 s instead of 13.6 s locally (+12 %), with 2 passes as on master.

## Results against the pass criteria

| Criterion | Result |
|---|---|
| No overlapping chords | **Pass.** 0 overlapping pairs in the whole book (17,154 chords, 12,676 same-line pairs). Master has 157 overlapping pairs in 102 songs. |
| No song spills (S2) | **Pass.** check_pages 0 problems, 757 → 757 pages, every song on its own page, 0 overfull boxes. |
| Text within about 2 characters (1 ch = 0.5em = 7.2 pt) | **1,641 of 1,668 lyric fragments (98 %)**; 9 of the 13 songs have none beyond. |

The 27 fragments beyond 2 ch: chcibytpritom 13 and jednourano 11, plus 2 in lonelystranger and 1 in letniukolebavka. All are lyrics after a **run of chords** that master had squeezed together or overlapping ("A A⁴A", "AmDm⁷F"), now evenly spaced at 1em. Pauses are kept (`\gap`), so goodriddance and rekalasky are now 0.

Full book with the prototype `\chord` (only the 13 songs stripped): 356 songs differ from master, 377 are unchanged (CI of the PR reports the same). 8 songs have no chords, and in the others no two chords on a line come closer than chord width + 0.5em, so nothing moves.

## Owner feedback from the first iteration, and what changed

- **Pauses are intentional** (a chord struck, then a pause before the lyrics): kept as `\gap{n}`. Book-wide: 157 after a chord, 69 inside lyrics, 1 at a line start.
- **Words must not be joined.** TeX swallows the space after a control word, so `já\sm\chord{C}panenku` used the macro as the only word gap. A gap between two letters is now removed only when the joined form is a word elsewhere in the songbook (or no letter follows). Otherwise a space is kept and the place is listed. Book-wide: 30 removed inside a word, 130 keep a word space, **23 to check** (list in C1-review-lists.md).
- **Hyphens in split words:** kept, and now always visible.
- **Chord-only lines:** evenly spaced, at 1em now (it was 1.5em). Every run (681 places) is listed so intentional unevenness can be spotted.
- **Chords written without `\chord`:** about 96 places in 58 songs (`\textbf{…}`), listed. `\chords{…}` is proposed and tried in 3 places.

## Recommendation for C2

**Path A.** It removes every overlap, keeps pauses explicit and semantic (`\gap`), and it's a single-pass extension of the existing macro with no new state, so it's durable. It also maps directly to the web (W2): put each chord and its text in an inline-block column with `padding-right` = sep on the chord, and the box is then max(text, chord + sep) wide, without JavaScript.

## Owner decisions for C2

1. Path A or B.
2. Values: `\chordsep` 0.5em, `\chordrunsep` 1em.
3. `\chords{…}` for chords written without `\chord`: yes/no. Red like other chords, or black as today? Do it within C3, or as a separate ticket?
4. The 23 CHECK places (word gap or inside a word). They can wait until their C3 batch.

## Notes for C3 (if path A)

- Batch flow: `tools/strip_chord_spacing.py <ids>`, then review its log (`\gap` places, kept spaces, CHECK), build, and run the PDF diff. The tool takes the songbook-wide word list into account, so run it from the repository root.
- `\zpchordspacingtrue/false` is a global switch: `\song` must reset it per song during the migration.
- After C4: wire `tools/chord_gaps.py` into CI (build with `\zpchordtracetrue`; exit 1 on overlap), and lint the 25 brace-boundary pairs.
- `\gap` with a non-integer n is not supported (`\dimexpr` multiplies by an integer); every case in the book is an integer.

## Verified

Locally (TeX Live 2023):
- build OK: 1 pass incremental, latexmk default otherwise; 757 pages
- check_pages 0 problems, 0 overfull boxes, lint 0/0, unit tests OK, single-song/artist/metadata tests OK
- chord_gaps 0 overlapping
- padding off: zero diff against master
- content of the 13 songs equal to master apart from the spacing macros, `\gap` and `\chords`

CI of the PR (run 41906882487, pinned TeX Live 2023): success in 3 min 13 s; latexmk 2 passes; 757 pages; check_pages 0 problems; PDF diff 356 changed, 377 unchanged, identical to the local clean build.

## Not verified

- Overleaf (not tested).
- A local build on the owner's Mac (instructions in the reply; this session can only reach a Linux VM on that computer).
