# Overview of the refactoring

Facts only, for the owner who writes the article on the website himself ([D-175](DECISIONS.md#d-175--the-finished-songbook-what-is-planned-and-what-is-not--agreed-owner-13-nov-2026)), and as a reference later. Readable in ten minutes. It does not repeat [HISTORY.md](HISTORY.md) (what each phase changed, PR by PR), [DECISIONS.md](DECISIONS.md) (what was agreed and why) or [WALKTHROUGH.md](WALKTHROUGH.md) (how one song travels from file to screen); it points to them. State of 13 Nov 2026: 738 songs, release `v8.38.42` at the time of writing, 300 unit tests. PRs without a prefix are in `zpevnik`, those marked *web* in `zpevnik-web`.

## Starting point and goal

**v8.33 (August 2026):** 733 songs in LaTeX, one PDF, and a website that only offered the PDF for download. Adding a song took six manual steps in three places. The layout was tuned by hand, and nothing checked it.

**Goal ([D-100](DECISIONS.md#d-100--goal-pdf-and-an-online-html-songbook-both-built-from-the-same-latex-files--agreed-3-nov-2026)):** the songbook as a PDF *and* as an online HTML songbook, both built from the same LaTeX song files. The technical debt was paid off first, so that the converter reads meaning ("a chorus", "a pause here") and never millimetres.

## The end state

```
songs/*.tex ─┬─ tools/generate.py ─► generated *.tex ─┐
data/ (artists, book facts, hidden songs)            ├─ latexmk ─► PDF per edition ─┐
editions/<name>/                  zpevnik.tex+.sty ──┘  (TeX Live 2023)              │
zpevnik.sty ─┤                                                                      ├─► GitHub release v<version>
             └─ tools/songbook/ (converter) ─► songs.json ◄─ page numbers of the PDF │   (PDFs, songs.json, scores.zip)
scores/*.mscz ─► MuseScore ─► SVG (the same image in the PDF and on the web)          │
                                                                                      ▼
zpevnik-web: version.txt names the release ─► build.py ─► HTML ─► GitHub Pages (/zpivej/, search, PDF links)
```

Three kinds of thing are kept apart: *source* (song files, `data/`, `editions/`, `zpevnik.sty`), *build output* (`build/`, never committed) and the *release* (what the website downloads). The two repositories share one contract, `songs.json` with its JSON Schema, validated in the CI of `zpevnik`, so a change that would break the website fails the songbook's pull request first ([D-165](DECISIONS.md#d-165--songsjson-the-shape-of-the-contract-with-the-website--agreed-owner-12-nov-2026-session-24-ticket-j2-implemented-in-pr-127), [D-166](DECISIONS.md#d-166--the-release-carries-the-websites-data-songsjson-and-scoreszip-validated-in-ci--implemented-agent-12-nov-2026-session-25-ticket-j4-pr-129), [D-110](DECISIONS.md#d-110--the-website-gets-the-songbook-outputs-from-release-assets--agreed-3-nov-2026)).

## By area

### Safety net (phase 1) · [#23](https://github.com/f-hluchnik/zpevnik/pull/23)–[#25](https://github.com/f-hluchnik/zpevnik/pull/25)
- **Problem:** the published v8.33 had a song on two pages because CI had silently moved to a newer TeX Live. Nothing checked pages.
- **Done:** TeX Live is pinned (2023). CI builds the base and the head in the same job and compares them song by song; one song must fit one page; later chord overlaps fail CI too.
- **How:** `tools/pdfdiff.py` maps pages to song ids with the page checkpoints of the `.aux` files and ignores the footer and the build date; `tools/check_pages.py` reads the same checkpoints ([D-105](DECISIONS.md#d-105--pin-the-tex-live-version--agreed-3-nov-2026), [D-106](DECISIONS.md#d-106--visual-diff-compares-songs-not-page-positions--agreed-3-nov-2026)).
- **Numbers:** 756 pages then, 764 now; the first 61 pull requests (#23–#86, four days) were each built twice and compared song by song.

### Registry and generated files (phase 2) · [#26](https://github.com/f-hluchnik/zpevnik/pull/26)–[#36](https://github.com/f-hluchnik/zpevnik/pull/36), [#46](https://github.com/f-hluchnik/zpevnik/pull/46)
- **Problem:** six steps to add a song; 35 songs had another title in the contents than on their page; artists were spelled several ways.
- **Done:** one file per song. The 908-line main file is 26 lines, the 2,962-line contents is 16 lines (generated). `data/artists.toml` (50 entries) is the one list of artists; the generator writes the include list in Czech collation, the letter contents and the artist index.
- **How:** `tools/generate.py` reads the songs and the registry; `build/` is output, never committed ([D-104](DECISIONS.md#d-104--generated-tex-files-are-produced-at-build-time-not-committed--agreed-3-nov-2026), [D-107](DECISIONS.md#d-107--song-order-standard-czech-collation-of-the-title--agreed-3-nov-2026), [D-111](DECISIONS.md#d-111--registry-and-generator-conventions--implemented-in-r4-r5-r13-3-nov-2026-merged-by-the-owner-details-may-change-in-r6), [D-115](DECISIONS.md#d-115--artist-index-as-a-column-list--agreed-4-nov-2026-session-6), [D-118](DECISIONS.md#d-118--artist-index-and-sections-generated-r11--implemented-in-r11-4-nov-2026-session-7-pr-35)). CH sorts after H, a space before any letter; 67 songs moved to their right place once.
- **Numbers:** `\artist{slug}` replaced `\interpret` in 550 songs; the main file 908 → 26 lines.

### Source hygiene (phase 4) · [#38](https://github.com/f-hluchnik/zpevnik/pull/38)–[#41](https://github.com/f-hluchnik/zpevnik/pull/41), [#45](https://github.com/f-hluchnik/zpevnik/pull/45), [#64](https://github.com/f-hluchnik/zpevnik/pull/64)
- **Problem:** leftovers in the song files and a TeX hack (`\everypar`) that the layout depended on in over 4,000 places.
- **Done:** 708 redundant `\newpage` and `\hyt{id}` in 733 songs removed; accent macros became UTF-8; the hack was replaced by two explicit settings with pixel-identical output ([D-120](DECISIONS.md#d-120--source-hygiene-h1h4--implemented-in-session-8-4-nov-2026-prs-3841), [D-127](DECISIONS.md#d-127--everypar-hack-replaced-center-behaves-as-standard-latex--agreed-owner-5-nov-2026-session-13-h6)).

### Chord spacing (phase 5) · [#43](https://github.com/f-hluchnik/zpevnik/pull/43), [#44](https://github.com/f-hluchnik/zpevnik/pull/44), [#47](https://github.com/f-hluchnik/zpevnik/pull/47)–[#63](https://github.com/f-hluchnik/zpevnik/pull/63)
- **Problem:** 1,285 hand-made nudges between chords; chords still overlapped in 157 places.
- **Done:** a chord and its text take max(text, chord + 0.5 em); chords without text stand 1 em apart; a pause is `\gap{n}`; a pad that splits a word gets a hyphen ([D-123](DECISIONS.md#d-123--automatic-chord-spacing-gate-c2-path-a--agreed-owner-4-nov-2026-session-9)).
- **How:** the `\chord` macro looks ahead at the text up to the next chord, measures it and pads only where two chords would collide, in one TeX pass (about 85 lines, no package). A first prototype that measured over several runs never converged and was dropped.
- **Numbers:** 449 songs migrated in 12 batches, each reviewed as a PDF by the owner; 17,180 chords, 0 overlapping, checked on every pull request.

### Vertical spacing (phase 6) · [#65](https://github.com/f-hluchnik/zpevnik/pull/65)–[#78](https://github.com/f-hluchnik/zpevnik/pull/78)
- **Problem:** 618 hand-made vertical nudges (`\ns`, `\vinv`, `\lsp`, `\vspace`).
- **Done:** one gap between blocks, `\blocksep` (20 pt), that TeX may shrink to zero when a page is full; named separators `\groupbreak`, `\blockrule`, `\partrule`; `\note` belongs to the next block ([D-124](DECISIONS.md#d-124--vertical-spacing-one-shrinkable-block-gap--agreed-owner-5-nov-2026-session-12-v1v2), [D-128](DECISIONS.md#d-128--v5-details-note-flag-fixed-gap-in-multicols-large-policy--agreed-owner-5-nov-2026-session-15-prs-74-75), [D-130](DECISIONS.md#d-130--note-has-the-block-gap-above-not-below--implemented-agent-6-nov-2026-session-16-pr-78-merged-by-the-owner)).
- **Consequences:** 11 songs that would not fit one page use `\large` after the header, each with a comment ([D-129](DECISIONS.md#d-129--body-font-stays-large-large-per-song-when-a-song-is-too-long--agreed-owner-6-nov-2026-session-15)); 21 `\vspace` remained, all beside score images or commented.

### Code quality (phase 11, audits, Q7) · [#79](https://github.com/f-hluchnik/zpevnik/pull/79)–[#86](https://github.com/f-hluchnik/zpevnik/pull/86), [#117](https://github.com/f-hluchnik/zpevnik/pull/117)–[#120](https://github.com/f-hluchnik/zpevnik/pull/120), [#142](https://github.com/f-hluchnik/zpevnik/pull/142)
- **Done:** `zpevnik.sty` ordered by topic with the reason in each comment and internals under `\zp@`; final command names (`\chorus`, `\coda`, `\subtitle`, `\speaker`, `\seealso`, one `\cue`, numbers as `\vers[n]`; old names are lint errors) ([D-131](DECISIONS.md#d-131--code-quality-pass-and-the-final-command-names--agreed-owner-6-nov-2026-tickets-q1q5)); one registry module and one place for paths in the Python tools; the README rewritten after the owner's way of working ([D-158](DECISIONS.md#d-158--changes-reach-master-only-through-a-pull-request-the-readme-follows-the-owners-workflow--agreed-owner-12-nov-2026-session-22a-ticket-a1)).
- **Audits:** a throwaway mutation run (1,771 small code changes) showed that the tests catch 96 % of them, so the suite stayed ([D-159](DECISIONS.md#d-159--the-unit-tests-stay-except-eight-that-another-check-already-covers--agreed-owner-12-nov-2026-session-22b-ticket-a2)); most of a CI run (about 80 s of 170–210 s) is pulling the TeX Live image, and no way around it was worth its risk ([D-160](DECISIONS.md#d-160--build-and-ci-speed-the-time-is-the-tex-live-image-harden-apt-compare-every-edition--agreed-owner-12-nov-2026-session-22c-ticket-a3-implemented-in-prs-119-and-120)).
- **Q7:** the converter became the one reader of the song files; the regexes of `songs.py` went ([D-164](DECISIONS.md#d-164--converter-design-a-strict-parser-and-an-in-memory-model--agreed-owner-12-nov-2026-session-23-ticket-j1-implemented-in-pr-124)).

### Editions (phases 8, 9a, 10) · [#93](https://github.com/f-hluchnik/zpevnik/pull/93)–[#99](https://github.com/f-hluchnik/zpevnik/pull/99), [#102](https://github.com/f-hluchnik/zpevnik/pull/102), [#103](https://github.com/f-hluchnik/zpevnik/pull/103), [#106](https://github.com/f-hluchnik/zpevnik/pull/106), [#107](https://github.com/f-hluchnik/zpevnik/pull/107), *web* [#3](https://github.com/f-hluchnik/zpevnik-web/pull/3)
- **Problem:** one book only; the folk songs of `lidovky` lived in a separate repository, and no subset of the songs could be built.
- **Done:** an edition is a filter over the song list (song ids and artists) with its own front matter; the full book is one of them ([D-138](DECISIONS.md#d-138--editions-a-folder-per-edition-its-own-front-matter-its-own-version--agreed-owner-9-nov-2026-session-23-e1-superseded-by-d-139-9-nov-2026), [D-139](DECISIONS.md#d-139--editions-revised-before-e2-selection-by-song-or-artist-one-colophon-core-the-build-version--agreed-owner-9-nov-2026-supersedes-d-138-superseded-in-part-by-d-143-front-matter-page-names-pdf-name-output-paths), [D-144](DECISIONS.md#d-144--editions-the-details-settled-in-e2--agreed-owner-10-nov-2026-session-20b-ticket-e2)). A `\seealso` to a song outside an edition prints nothing ([D-145](DECISIONS.md#d-145--edition-integrity-how-the-checks-reach-every-edition--agreed-owner-11-nov-2026-session-20b-ticket-e3)). Adding an edition is adding a folder: CI finds it, builds and checks it and attaches its PDF to the release ([D-149](DECISIONS.md#d-149--release-of-every-edition-how-the-ci-finds-builds-and-releases-them--implemented-agent-11-nov-2026-session-21-ticket-e5-the-design-agreed-with-the-owner-d-139-d-143-d-147)). `lidovky` replaced the repository `zpevnik-lidovky` ([D-146](DECISIONS.md#d-146--the-lidovky-edition--agreed-owner-11-nov-2026-session-21-ticket-e7)).
- **Version:** `major.minor` is the song count + 100 (738 songs → 8.38), the patch counts commits, so a release is a build ([D-133](DECISIONS.md#d-133--the-version-identifies-a-build-833n--agreed-owner-6-nov-2026-details-proposed-by-the-agent-confirmed-in-e0s-pr-ticket-e0)).
- **Open:** the songs of `zpevnik-lite` are for the owner to pick after the printed edition (E4, [D-147](DECISIONS.md#d-147--order-after-session-21-delivery-print-audits-then-the-converter-and-the-website--agreed-owner-11-nov-2026-session-21-amends-d-132)).

### Print (phase 3) · [#113](https://github.com/f-hluchnik/zpevnik/pull/113)–[#116](https://github.com/f-hluchnik/zpevnik/pull/116)
- **Done:** a feasibility report with the printer's checklist (`docs/p0-print-report.md`); the print formats `print` and `print-black`; the screen PDF scaled to A5 with a spine shift, `make print` ([D-154](DECISIONS.md#d-154--print-the-owners-answers-and-output-formats-as-build-time-macros--implemented-in-part-agent-11-nov-2026-session-21c-first-pr-of-p3-agreed-with-the-owner-d-139-d-142-d-148)–[D-157](DECISIONS.md#d-157--print-preparation-is-done-what-is-left-belongs-to-the-printer-and-the-owner--recorded-agent-11-nov-2026-session-21c-closes-p0-and-p3-leaves-p1-open)). The screen PDF never changes because of print (zero diff).
- **Cancelled:** a licensing check for selling, because the book is never sold ([D-140](DECISIONS.md#d-140--the-songbook-is-never-sold--agreed-owner-9-nov-2026)).
- **Open:** the printer's answers (P1) and the checked proof on the final content (P4).

### Converter and `songs.json` (phase 7, J6) · [#88](https://github.com/f-hluchnik/zpevnik/pull/88), [#89](https://github.com/f-hluchnik/zpevnik/pull/89), [#123](https://github.com/f-hluchnik/zpevnik/pull/123), [#124](https://github.com/f-hluchnik/zpevnik/pull/124), [#126](https://github.com/f-hluchnik/zpevnik/pull/126)–[#129](https://github.com/f-hluchnik/zpevnik/pull/129), [#143](https://github.com/f-hluchnik/zpevnik/pull/143)
- **Problem:** the website needs the songs as data, and the song files had quirks that no strict reader would accept.
- **Done:** the owner decided each quirk and 42 songs were fixed (22 in J0a, 20 more in J1) ([D-135](DECISIONS.md#d-135--song-quirks-before-the-converter-j0--agreed-owner-8-nov-2026-session-23), [D-163](DECISIONS.md#d-163--the-structure-of-a-song-as-the-converter-will-read-it--agreed-owner-12-nov-2026-session-23-ticket-j0a)); scores became `\score{name}` and MuseScore exports one SVG used by the PDF and the web ([D-136](DECISIONS.md#d-136--scores-place-themselves-shared-musescore-style-trimmed-svg-scorename--agreed-owner-8-nov-2026-session-23-j0-item-1-together-with-j5)); the strict converter `tools/songbook/` is part of `make check` ([D-164](DECISIONS.md#d-164--converter-design-a-strict-parser-and-an-in-memory-model--agreed-owner-12-nov-2026-session-23-ticket-j1-implemented-in-pr-124)); `songs.json` has a JSON Schema (2020-12) that CI validates before every release ([D-165](DECISIONS.md#d-165--songsjson-the-shape-of-the-contract-with-the-website--agreed-owner-12-nov-2026-session-24-ticket-j2-implemented-in-pr-127), [D-166](DECISIONS.md#d-166--the-release-carries-the-websites-data-songsjson-and-scoreszip-validated-in-ci--implemented-agent-12-nov-2026-session-25-ticket-j4-pr-129)).
- **J6:** `\remark{…}` for text that is not sung (a tuning, the structure of a verse) became a body item `remark` in `songs.json` (`schemaVersion` 2); the website sets it like a note and the search leaves it out ([D-177](DECISIONS.md#d-177--remarks-remark-and-songsjson-with-schemaversion-2--agreed-owner-13-nov-2026-session-30-ticket-j6-implemented-in-zpevnik-pr-143-and-zpevnik-web-pr-17)).
- **V10:** a song in parts always has `\partrule` between its parts ([D-178](DECISIONS.md#d-178--a-song-in-parts-always-has-partrule-between-the-parts-no-new-form-for-tight-verses--agreed-owner-13-nov-2026-session-31-ticket-v10-zpevnik-pr-146), [#146](https://github.com/f-hluchnik/zpevnik/pull/146)).
- **Numbers:** `songs.json` is 4.9 MB, 455 kB gzipped, read at build time only.

### Legal (phase 8) · [#121](https://github.com/f-hluchnik/zpevnik/pull/121)
- **Done:** a notice in the colophon of every book and in the web footer: non-commercial, rights holders write and the song goes; the Apache licence covers only the owner's own work, not the songs ([D-141](DECISIONS.md#d-141--legal-notice-and-the-scope-of-the-licence--agreed-owner-9-nov-2026-ticket-l1)). `data/hidden.txt` removes a song from every book within one pull request without deleting it ([D-161](DECISIONS.md#d-161--hidden-songs-one-list-applied-in-one-function--implemented-agent-12-nov-2026-owner-asked-for-it-before-the-converter-ticket-l2)). The website has `noindex` and a `robots.txt` that disallows everything. This is reasonable effort, not legal advice.

### Website (phase 9) · *web* [#4](https://github.com/f-hluchnik/zpevnik-web/pull/4)–[#17](https://github.com/f-hluchnik/zpevnik-web/pull/17)
- **Done:** the online songbook at `/zpivej/`, separate from the download page ([D-167](DECISIONS.md#d-167--the-online-songbook-lives-under-zpivej-unknown-songs-get-the-sites-404--agreed-owner-12-nov-2026-session-26-ticket-w2)): 738 song pages built in about 3 s, the index in the book's order, artists and collections, previous and next song, "open in PDF" at the song's page ([D-168](DECISIONS.md#d-168--index-artists-and-the-pdf-link-of-the-online-songbook--implemented-in-w3-session-27-zpevnik-web-pr-6-the-owner-reviews-it-in-the-pr), [D-169](DECISIONS.md#d-169--two-levels-of-navigation--agreed-owner-12-nov-2026-after-w3-ticket-w3a)). Search over titles, artists and lyrics, matching from the start of words, results in two groups, a 262 kB gzipped index loaded on first use, no library ([D-170](DECISIONS.md#d-170--the-search-of-the-online-songbook--implemented-in-w4-session-27-zpevnik-web-pr-8-the-owner-reviews-it-in-the-pr), [D-171](DECISIONS.md#d-171--the-search-matches-from-the-start-of-words-versioned-urls-of-styles-and-scripts--agreed-owner-12-nov-2026-after-w4-ticket-w4a), [D-173](DECISIONS.md#d-173--search-results-in-groups--agreed-owner-12-nov-2026-after-w3b-ticket-w4b)). A font size control, a keep-the-screen-on button ([D-174](DECISIONS.md#d-174--keeping-the-screen-on--implemented-in-w5-session-27-zpevnik-web-pr-12-the-owner-reviews-it-in-the-pr)).
- **How:** `build.py` downloads `songs.json` and `scores.zip` of the release named in `version.txt`; the chord rule of the book is in CSS, and the page reads without JavaScript. `check_site.py` fails the build when a song has no page or a link leads nowhere.
- **Chord wrapping (W6a):** a browser moved a chord-and-text box whole to the next line (40 % of the 4,536 lines with chords wrapped on a 390 px phone). Now the column holds the shortest run of whole words as long as the chord and the rest flows; no chord closer than 0.5 em to the next, no break inside a word without a hyphen ([D-176](DECISIONS.md#d-176--chord-wrapping-on-the-web-head--tail--agreed-owner-13-nov-2026-ticket-w6a)).
- **Not verified on any real phone:** the screen staying on, the keyboard of the search, `#page=N` in a phone's PDF viewer.

## Not planned, and why ([D-175](DECISIONS.md#d-175--the-finished-songbook-what-is-planned-and-what-is-not--agreed-owner-13-nov-2026))
The principle is a songbook that is correct and simple, not one with every feature. Setlists (not needed), offline use (the PDF is the offline songbook), a fit-to-screen button (A− and A+ do it), a smaller default font on phones (the text gets too small to sing from first), transposition (it would need the chords as data and could not reach scores, capo notes or chords named in remarks, so a transposed page would contradict itself), a ChordPro export (a second writer of the song model, worth it only if someone uses such an app).

## What is open
- **H7:** two versions of one song become two songs (`cernymuz` → `cernymuzmatuska`, `jednoubudemdal`); the owner writes them.
- **The owner's new songs** (about ten), then **P1** (the printer's answers) and **P4** (the proof), then **E4** (`zpevnik-lite`).
- Each of these adds its line here in its last pull request.

---

## Notes for the website article

The notes below were collected on 6 Nov 2026 (the first part of the refactoring) and are kept as they were, with a later paragraph on the website. Later numbers are above.

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
4. *Chords that make room for themselves.* The chord macro now looks ahead at the text up to the next chord, measures it and adds space only where two chords would collide. The first prototype (measuring positions over several compile runs) never converged and was dropped for this one-pass version. Result: zero overlapping chords, checked in CI; intentional pauses are written as `\gap{n}`. The rule "never join two words on a guess" meant every unclear case went to the owner; 449 songs were migrated in batches, each reviewed as a PDF.
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

**What came next.** The editions, the converter (`songs.json`) and the online songbook at `/zpivej/`. Still to come: the printed edition and a "lite" songbook of favourites.

**The online songbook, for the article.** The owner looked at each step on the live site and sent back what felt wrong; four of the eleven website pull requests (W3a, W4a, W3b, W4b) are his observations: a download-style button for the songbook, a search box that looked unstyled on his desktop only (a cached style sheet, now fixed with content-hashed URLs), no obvious way back to the index, and lyrics matches mixed in with title matches. A good story for people who like small web details.
