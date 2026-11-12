# Project history

What changed in the songbook refactoring and why, phase by phase (DECISIONS D-126). Facts only; the reasoning behind each choice is in [DECISIONS.md](DECISIONS.md), the helper files of finished phases are in [archive/](archive/). The first part collects notes for the short story of the refactoring on the website.

---

## Notes for the website article

**Working title ideas:** "733 písniček, nula ručních mezer" · "Jak jsem uklidil zpěvník" · "Zpěvník pod kapotou". Write it in Czech, short (one screen or two), for people who use the songbook, not for TeX experts. One or two before/after images of a song page (archive/phase-5-chords/C1-chord-spacing/ has ready ones, e.g. `ringoffire-before-after.png`).

**Starting point (v8.33, August 2026).**
- 733 songs in LaTeX, one PDF, a website that only offered the PDF for download.
- Adding a song meant six manual steps in three places: the song file, a hand-written `\include` line in the 908-line main file, one or two entries in the 2,962-line hand-written contents, and a version bump.
- The copies had drifted: 35 songs had a different title in the contents than on their page ("Brigh Side"), artists were spelled several ways.
- The layout was tuned by hand: 1,285 horizontal nudges between chords (`\nc`, `\mm`, `\sm`) and 618 vertical ones (`\ns`, `\vinv`, `\lsp`, `\vnv`, `\cns`, `\vspace`). Chords still overlapped in 157 places.

**The goal.** The songbook should also be readable online, as web pages built from the same song files as the PDF. Before writing the converter, the debt was paid off, so that the converter reads clean, meaningful markup ("this is a chorus", "a pause here") and never millimetres.

**How.** Four days (3–6 November 2026), 61 merged pull requests, done in working sessions with an AI coding agent; the owner decided every content question and reviewed every changed page. Every pull request was built twice in CI (before and after) and compared song by song, so a change to 733 pages became reviewable.

**Stories worth telling (pick two or three).**
1. *The safety net found a bug first.* The published PDF had one song spilling onto a second page, only because CI had silently moved to a newer TeX Live. Pinning the TeX Live version made the build reproducible; a song-by-song image diff and a "one song, one page" check came next. Nothing else was touched before that.
2. *One file per song.* A registry of 50 artists and a generator replaced the hand-written lists: the main file went from 908 to 26 lines, the contents from 2,962 to 16. Adding a song is now one new file (plus a registry line for a new artist) and `make`.
3. *Czech alphabetical order is not trivial.* The contents follow the Czech standard: CH is a letter after H (also in "Change the World"), a space sorts before any letter ("A Horse With No Name" before "Abych tu žil"), Ď sorts with D. Implemented and unit-tested in the generator; 67 songs moved to their correct place once.
4. *Chords that make room for themselves.* The chord macro now looks ahead at the text up to the next chord, measures it and adds space only where two chords would collide. The first prototype (measuring positions over several compile runs) never converged and was dropped for this one-pass version. Result: zero overlapping chords, checked in CI; intentional pauses are written as `\gap{n}`. The rule "never join two words on a guess" meant every unclear case went to the owner; 449 songs were migrated in 12 batches, each reviewed as a real PDF.
5. *An old hack with side effects.* The style redefined a TeX primitive (`\everypar`) to get the hanging labels. It only worked by accident, and the layout depended on its side effects in over 4,000 places. It was replaced by two explicit settings with pixel-identical output.
6. *One gap instead of 618 nudges.* Without the hand-made squeezing, 74 of 88 songs would no longer fit on one page. One gap between blocks that TeX may shrink when a page is full brought that down to 2; those (and the few dashed-line songs) use a slightly smaller font, by an explicit, commented choice. Dashed lines between tight verses stayed: they help while playing.

**Before / after.**

| | v8.33 (Aug 2026) | 6 Nov 2026 |
|---|---|---|
| Places to edit when adding a song | 3 files, 6 steps | 1 file |
| Main file / contents | 908 / 2,962 lines, by hand | 26 / 16 lines, generated |
| Manual chord spacing | 1,285 | 0 (automatic, 0 overlaps) |
| Manual vertical spacing | 618 | 21 `\vspace`, all next to score images or commented |
| Contents ↔ song title mismatches | 35 | 0 (one source) |
| Automated checks | none | pinned TeX Live, song-by-song PDF diff, one page per song, chord overlaps, lint, 103 unit tests |

**Lessons (one paragraph at most).** Build the safety net before touching anything. Make the diff cheap, then large changes become safe. Write what a song *means*, never how far apart things are. Write decisions down; the agent never guesses about content. Delete what nobody uses.

**What comes next.** Editions (a "lite" songbook of favourites), the printed edition, then the converter (`songs.json`) and the online songbook.

---

## Phase 1 · Safety net (S1–S3) · 3 Nov 2026 · PRs #23–#25

- CI builds every pull request; publishing only on master. TeX Live pinned to 2023 (D-105): the published v8.33 (newer TeX Live) had `illbethereforyou` on two pages, 2023 keeps every song on one page (756 pages then).
- `tools/check_pages.py`: fails when a song takes more than one page (reads the per-song `.aux` checkpoints; allow-list empty).
- `tools/pdfdiff.py`: base and head compiled in the same job, pages matched by song id, footer and colophon date excluded; reports changed, added, removed and moved songs (D-106).

## Phase 2 · Registry and generated files (R1–R14) · 3–4 Nov 2026 · PRs #26–#36, #46

- Macros moved from `zpevnik.tex` into `zpevnik.sty`; one song compiles with the style alone (Overleaf, D-005); CI tests it (R3).
- `data/artists.toml` (49 entries, 50 after splitting Triky a pověry / Ricchi e Poveri), validator, generator; `generated/` is build output, `make` = generate + compile (D-104, D-111).
- Anchors normalised, name typos fixed (D-112). `\artist{slug}` on every song replaced `\interpret`/`\interpretdva` (550 songs); links right-aligned, none cut off (D-113); registry needs only `slug` and `name` (D-114).
- `\alttitle`, `\toctitle`, `\collection` (D-116); 8 subtitles that only repeated the artist dropped (D-117).
- Generated include list in Czech collation (D-107; 67 moves approved, docs in archive/phase-2-registry/), letter contents (Ď section gone), two-column artist index and artist sections from the song tags (D-115, D-118).
- Lints (`tools/lint.py`, threshold for a new section: 3 songs, D-119), Czech README, version computed as song count + 100 (R13), `make song SONG=<id>` (R14).

## Phase 4 · Source hygiene (H1–H6) · 4–5 Nov 2026 · PRs #38–#41, #45, #64

- Five source quirks fixed (H1); 708 redundant `\newpage` removed (H2); `\hyt{id}` removed from 733 songs, the target comes from the include list and the file name is the id (H3); accent macros replaced by UTF-8 (H4); two review fixes (H5) (D-120).
- The `\everypar` hack replaced by `\parindent` −10 mm with `indentfirst`; `center` now standard LaTeX (D-127).

## Phase 5 · Chord spacing (C1–C5) · 4–5 Nov 2026 · PRs #42 (prototype, closed), #43, #44, #47–#59, #61, #62, #63

- Rule (D-123): a chord and its text take max(text, chord + 0.5em); chords without text 1em apart; pauses are `\gap{n}`; chord-only lines are `\chords{…}`; a pad that splits a word gets a hyphen. Single-pass lookahead in `\chord`, about 85 lines, no new package, build +12 %.
- Migration in 12 batches (449 songs), each reviewed as a PDF; glued chords fixed; `\chords[sep]` for two over-long rows (C3b). Then the switch and `\nc \mm \sm \bc` deleted, any overlap fails CI (C4). One label width `\labelw` = 25 pt for all blocks (C5).
- Helper files: archive/phase-5-chords/.

## Phase 6 · Vertical spacing (V1–V9) · 5–6 Nov 2026 · PRs #65–#78

- Analysis and owner's approval (V1/V2, D-124): one block gap `\blocksep` = 20 pt, shrinkable to zero; `\ns`, `\cns` and negative `\vspace` deleted, not replaced; dashed lines kept as separators; `\vinv` → `\groupbreak`, reviewed per song.
- V3 shrinkable gap, V4 named separators (`\groupbreak`, `\blockrule`, `\partrule`), V6 named shifts, #74 `\note` attaches to the next block and songs run in a group (D-128), V5 six alphabetical batches plus follow-up (#68–#73, #75, #76), V8 old macros deleted and linted (#77), V9 the last non-score `\vspace` removed, `\note` gets the gap above, `\spk` for speaker changes (#78, D-130).
- Songs too long for one page at `\Large` use `\large` after the header, with a comment (11 songs, D-129).
- Helper files: archive/phase-6-vertical/ (the list of the remaining `\vspace` is `vertical-spacing/remaining-vspace.md` there).

## Phase 11 · Code quality (Q1–Q6) · 6 Nov 2026 · PRs #79–#86

- Q1 `zpevnik.sty` ordered by topic, English comments with the reason, internals under `\zp@`, named constants (#79, zero diff). Q2 Python tools: one registry module, one place for paths, one command-line style (#80, zero diff, `generated/` byte-identical). Q3 CI runs the assertions of the test documents, not only their compilation (#81).
- Q4 final command names (D-131): `\chorus`, `\coda`, `\subtitle`, `\speaker`, `\seealso`, one `\cue` for every repeat mark, numbers as optional arguments (`\vers[n]`); old names are lint errors (#82; 15 songs differ, the ticket expected 8; every block label ends with a dot).
- Q5 leftovers (#83, 15 songs differ, each page reviewed by the owner): labelless blocks are `\vers{…}` instead of `\nv` (12 songs), the `zapomnetliva` dialogue uses `\speaker` inside numbered blocks (`\speaker` is mode-aware like `\cue`), the tuning note of `ahorsewithnoname` is an unnumbered `\vers{\emph{…}}`, `\textit` became `\emph` (zero diff), song footnotes stay in `\song{}`; `\nv` and `\lbl` are lint errors in songs.
- Follow-ups the same day: `\nv` and `\lbl` became internal macros (#84, zero diff); text outside blocks in 7 songs went into `\vers{…}` and the lint rejects it, `= \cue{n}` lines lost their `\gap{2}` (#85, 20 songs differ). Exempt: the `zkratky` glossary and `vosa`'s `\placetextbox`.
- Q6, the last leftovers of the final review (#86): dead lookups removed, the TeX tricks commented as intentional (with what happens if they break), a test for the hyphen before an accented letter, the last IDs out of comments.
- Found in that review and ticketed for later: the version names a song count, not a build (D-133, E0); score images are placed by hand, and a few song quirks need a decision before the converter (J0).
- Helper files: none (the Q4 migration script was never committed).

## Phase 9a · Delivery of the editions (E5, E6) · 11 Nov 2026 · PRs #106, 107, zpevnik-web#3

- E5 (#106, D-149): the CI finds the editions by `edition_names()`, builds and checks every one in a single TeX Live step, and attaches `zpevnik-<edition>-<version>.pdf` of each to the release, with the song counts in the release notes; adding an edition is adding a folder. First release with it `v8.38.5` (`full` and `lidovky`).
- E6 (zpevnik-web#3 and #107, D-150): the website holds no songbook PDF; its build downloads the PDFs of the release named in `version.txt`, and the songbook CI only writes that file after creating the release. The download buttons are a list in the web's `build.py`; the full book keeps the fixed URL `zpevnik_last.pdf` (printed QR codes), `lidovky` is the edition from the release instead of the 2020 book, so the repository `zpevnik-lidovky` can be archived.
- Helper files: archive/phase-9a-delivery/ (the two ticket texts).

## Phase 12 · Audits (A1–A3) · 12 Nov 2026 · PRs #117–#120

The owner wanted the README, the tests and the build reviewed before the converter (D-147); each audit reported first and changed only what he agreed to.
- A1 (#117, D-158): every command of the README run and every path checked: nothing was wrong, but the song procedure was written twice, `make check` three times, and the two-page allow-list not at all. The README now follows the owner's work (setup, a new song, the writing reference, editions and print, publishing, one list of commands). Changes reach `master` only through a pull request.
- A2 (#118, D-159): 252 tests checked with coverage per test and a throwaway mutation run (1,771 small code changes): they catch 96 % of the logic changes, so the suite stays; 8 tests that another check covers were dropped (244 left).
- A3 (#119, #120, D-160): most of a CI run (about 80 s of 170–210 s) is pulling the TeX Live image, and none of the ways around it was worth its risk. The apt step got retries and time limits after a mirror outage held a run for 15 minutes; the PDF diff compares every edition, so an edition's own pages (cover, title page, imprint, contents) are reviewed too, for about 12 s per pull request.
- Helper files: archive/phase-12-audits/ (the three ticket texts). The audit scripts (coverage, mutation) were throwaway and not committed.

## Closing the refactoring · 6 Nov 2026

With Q6 (#86) the refactoring is finished: phases 1, 2, 4, 5, 6 and 11, 61 merged pull requests (#23–#86) in four days. The planning docs moved from the owner's computer into `docs/` of this repository (D-134), so work can continue from any device.

## Not done as part of the refactoring

- Phase 3 (print) and phase 10 (editions) came back into scope during the work (D-121, D-122) and are next (D-132).
- K1 (chords for 8 songs) is content work for the owner.
- Found in the final review and ticketed: the build version (E0, D-133), the song quirks and the `\score` command before the converter (J0).
