# Zpěvník modernisation plan

**Goal:** the songbook as a downloadable PDF *and* an online HTML songbook on the website, both built from the same LaTeX song files, with the technical debt (hand spacing, hand-written TOC and include list, duplicated metadata) paid off first ([DECISIONS.md](DECISIONS.md) D-100). Editions, the koledy songbook and the print layout are out of scope (D-102, D-109).

Companion files: [TICKETS.md](TICKETS.md) turns this plan into ordered, self-contained tickets; [INVENTORY.md](INVENTORY.md) lists every place that needs fixing (section IDs such as A1, B2, C1 are referenced below); [DECISIONS.md](DECISIONS.md) records agreed decisions and their rationale. All numbers are from `master` of `zpevnik` on 3 Nov 2026 (733 songs).

Tags: **[agent]** = mechanical, suitable for an AI agent when the baseline check (WP0) is in place. **[you]** = needs your decision or visual review.

## Principles

1. **One source of truth:** the song files plus one artists registry. The table of contents, the include list, the artist index, the web pages and `songs.json` are all generated from them.
2. **Song files say *what*, never *how far*:** a chord, a verse, an artist; never millimetres of space.
3. **One song per page in the PDF is enforced by CI**, not by eye.
4. **Generated `.tex` files are produced at build time** (`make`), never committed (D-104). Your Overleaf single-song workflow (README, "Doporučení pro psaní písniček") must keep working: one song compiles with just the style file, and an unknown artist slug degrades gracefully (no error, no output).
5. **Every refactor is checked against a baseline PDF**, built in the same CI job from the base commit with the same pinned TeX Live, and compared song by song (D-105, D-106).
6. **Songs are ordered by Czech collation of their title**, never by file name (D-107).

## Order of work

| WP | What | Changes the PDF? | Effort |
|---|---|---|---|
| 0 | Safety net (pinned TeX Live, baseline diff, one-page check) | only the fix for the one known spill | M |
| 1 | Artists registry, generated TOC and include list | typo fixes and a one-time reorder of ~20 songs | M–L |
| 4 | Source hygiene | no | S |
| 2 | Chord spacing | yes, many pages | M |
| 3 | Vertical spacing | yes, many pages | M |
| 5 | Converter and `songs.json` | no | M |
| 7 | Legal hygiene | no | S |
| 6 | Website | n/a | M |
| 8 | Editions (song subsets) | no | M |
| 9 | Print | no (separate build) | M |

Why this order (D-108): WP1 attacks the real bottleneck (adding a song currently means editing three places). WP4, WP2 and WP3 pay off the layout debt *before* the converter exists, so the converter is written once, against semantic macros only, and `songs.json` carries no layout. WP2 and WP3 touch all 733 pages and need visual review, which the WP0 diff makes reviewable. Legal hygiene (WP7) must be done before the lyrics go online (WP6).

---

## WP0 – Safety net

**Problem.** Nothing tells you whether a refactor changed any of the 733 pages, or whether a song spilled onto a second page. Worse, the layout depends on the TeX Live version: CI uses the latest one, and the published v8.33 PDF (757 pages) has "I'll Be There For You" spilling onto a second page, while TeX Live 2023 keeps every song on one page (756 pages).

**Steps**
1. [agent] Pin the TeX Live year in CI (D-105) and add PR builds (publishing steps stay main-only).
2. [agent] The one-page check reads the per-song `.aux` files that `\include` already writes (each records the page counter after the song); no new macro needed. CI fails if a song takes more than one page, except songs on an allow-list.
3. [you] Decide the existing spill under the pinned version: fix the song, or allow-list it.
4. [agent] Visual diff (D-106): compile the base commit and the PR head in the same job (≈8 s each), match pages by song id from the `.aux` records, and leave out the page-number footer and the colophon date. Report changed, added, removed and moved songs. It never fails on its own (some tickets expect differences); the PR description states the expected differences.

**Done when** CI turns red for a deliberately two-page test song, and a PR changing one chord reports exactly that song.

---

## WP1 – Artists registry, generated TOC and include list

**Problem**
- Adding a song is six manual steps today (README): new file, include line, TOC entries, version bump, compile. `zpevnik.tex` lists 733 includes by hand. `obsah.tex` has 1,461 hand-maintained entries: every song appears in its letter section and usually again in an artist section.
- That duplication has already drifted (INVENTORY C5, D): 35 songs are titled differently in the TOC than in the song (typos such as "Brigh Side", "přijížději"); `nadstademkoni` has no alphabetical entry; 6 artist-section mismatches; the `filmy` section is a collection, not an artist.
- Artist anchors are inconsistent: 12 are not the slug of the name, 7 anchors carry several display names (C1, C2).

**Target**
- `data/artists.toml`, the registry (TOML, because Python reads it without dependencies and it allows comments), one entry per index section: `slug`, `name`, `index_label` (surname as shown in the index), `sort`, `kind` (`artist` or `collection`, e.g. `filmy`), `section` (true/false). Seeded from the 49 existing sections. Entries with `section: false` are allowed, so `\artist{}` can be filled for every song over time.
- Uniform song header (sketch, not final):
  ```
  \song{Title}
  \artist{slug}              % may be empty; up to two
  \alttitle{Other title}     % optional, repeatable
  ```
  `\artist` prints the top-right link only when the registry says `section: true`. An optional per-song label override covers intentional cases (Greenhorns under Tučný).
- Generator `tools/generate.py` writes `generated/include.tex`, `generated/obsah.tex`, `generated/artists.tex` at build time (`generated/` is gitignored; `make` generates and compiles; D-104). Its input is an ordered list of songs, so editions could be added later without redesign (D-102).
- Order = standard Czech collation of the plain-text title (`\toctitle`, else `\song`), never the file name (D-107 has the exact rules): word by word, Č, CH, Ř, Š, Ž are letters of their own (Ď sorts with D, so the TOC's Ď section goes away), other diacritics and case only break ties. Implemented and unit-tested in the generator, not via the system locale. The current hand-made order ignores spaces and has ~20 further deviations (e.g. `bellaciao` before `bednaodwhisky`), so the switch reorders a number of songs once.
- Sections policy: the 49 existing sections stay (including the 7 below three songs, C4). A lint **warns** when an artist without a section reaches the threshold; the threshold is one config value (you wrote both "at least three" and "more than 3").

**Steps**
1. [you] Resolve the open items: renames in C1; slug rule for bands (default: drop a leading article, so `beatles`); canonical names in C2; split `trikyapovery` into *Triky a pověry* and *Ricchi e Poveri*; the Greenhorns override; the two two-artist songs (C3).
2. [agent] Create the registry from `obsah.tex`.
3. [agent] Rename anchors and fix names in the 550 songs that have `\interpret`; update the registry.
4. [agent] Add `\artist{}` to all 733 songs (from the old `\interpret` / `\interpretdva`, empty elsewhere); remove the old macros.
5. [you] Decide the 35 rows of D2; [agent] apply them, move the 28 italic titles (D1) into `\alttitle`, fix `nadstademkoni`; check the 6 titles with footnotes (C6).
6. [you] Review the list of songs the new order moves (D-107).
7. [agent] Write the generator, the lints and tests. Switch `zpevnik.tex` and `obsah.tex` to the generated files. Move all macro definitions out of `zpevnik.tex` (its first ~95 lines) into `zpevnik.sty`, so the Overleaf project becomes `zpevnik.sty` + one song instead of a hand-copied simplified `zpevnik.tex`.
8. [agent] Rewrite the README: adding a song = one new file (plus a registry entry for a new artist) and `make`. The colophon version is typed by hand while CI computes *song count + 100*; generate it once.

**Done when** the baseline diff shows only the typo fixes and the agreed reorder, and adding a test song touches exactly one file.

---

## WP4 – Source hygiene (no visual change)

**Status (4 Nov 2026):** the first four bullets are done (H1–H4, DECISIONS D-120); counts below are the original ones (accent macros: 59 `` \` `` and 4 `\^`). The last bullet (unused macros) was added to C4 (owner decision, 4 Nov 2026).

- Delete the redundant `\newpage` (708 songs): `\include` already starts a new page; the README claiming it is required is wrong.
- Stop repeating `\hyt{id}` in 733 files: the generated include list already knows each id and can set it before each `\include` (no `currfile` package needed; verify that it works with `\include`).
- Replace accent macros with UTF-8 letters (`` \` `` occurs 60 times, also in a title: `Felicit\`{a}`).
- Fix the source quirks that LaTeX tolerates silently but a strict parser rejects: `klada` (`\note(capo 2)`), `jaktosnamalaskobude` (`\emph(Cože)`), `neninutno` (`\vers{3} =…`), `noe` (`\refsm` without argument), `morituritesalutant` (`\bridge` without content).
- Delete what is unused: `\bc` (0 uses), the optional alignment argument of `\chord`, and check `\placepic` / `\placetextbox` (only `vosa.tex`).

---

## WP2 – Chord spacing

**Problem.** `\chord` is a zero-width `\makebox` containing a `tabular`. That is a legitimate technique, but it reserves no space, so authors compensate by hand: `\nc` 712×, `\mm` 319×, `\sm` 254× in 303 songs (A1). The values are points, not tied to anything, and wide chords still collide (324 lines where a chord is directly followed by another, A2).

**Verdict.** Not a hack. Keep the `\chord{X}text` syntax (733 songs and the converter depend on it) and add the missing piece: collision handling.

**Target rule** (D-123).
- A chord and its text occupy max(text width, chord width + `\chordsep` 0.5em). Chords with no text between them are `\chordrunsep` 1em apart. Consecutive chords never overlap.
- Pauses (a chord struck before the singing starts) are intentional and use `\gap{n}`, with *n* in characters (0.5em); there is no pause inside a word.
- Whole chord-only lines and chords written as `\textbf` become `\chords{…}` (inline, red).
- A pad that splits a word gets a hyphen.
- The website uses the same rule, so PDF and HTML agree.

**Steps**
1. [agent + you] Prototype, done (C1, session 9). A single-pass lookahead in `\chord`; gate passed and path A chosen (C2, D-123).
2. [agent] C3a: macros on master with the spacing off. C3b: migrate in batches of about 45 songs (≈ 460 songs: manual spacing, `\textbf` chords, and songs whose collisions get fixed), each reviewed with a real PDF. The `\sm` nudges inside chords (A3) just go.
3. [you] Review every page the baseline diff flags.
4. [agent] Delete the macros. Define the label width once (`\vers`, `\refrain`, … each use their own `\hspace` of 0.5–1.2 em today) and derive `\nv` from it; replace the 24 raw `\hspace` (A4).

**Done when** grep finds none of the old macros, the diff is reviewed and no song spills (WP0).

---

## WP3 – Vertical spacing

**Problem.** Spacing is tuned by hand per song: `\ns` 300×, `\vinv` 92×, `\lsp` 59×, `\vnv` 30×, `\cns` 4×, plus 133 raw `\vspace` (B1, B2). The macros also hide compensations: every block macro starts with `\vspace{20pt}`, `\ns` cancels it with −20pt, `\note` bakes in −20pt, `\sub` −10 mm, `\hyl` −15pt, and `\vinv` secretly contains a line break (`\vspace{-2mm}\\`). They cancel each other, so changing one breaks the others.

**Target.** Spacing is defined once and is semantic:
- one shrinkable length, `\blocksep`, used by all block macros, which absorbs what `\ns`, `\cns` and the negative `\vspace` did by hand (D-124: they existed to make songs fit and are deleted);
- the dashed lines stay as a separator that replaces the gap; the gaps inside verses become `\groupbreak`, reviewed per song;
- a raw `\vspace` survives only with a reason, or next to a score image.

**Steps**
1. [agent] Sample 20 contexts per macro and propose the semantic replacements; [you] approve.
2. [agent] Introduce `\blocksep`; remove the baked-in spacing from `\note`, `\sub`, `\hyl`.
3. [agent] Replace and delete the custom macros (B1).
4. [you] Go through the raw `\vspace` (B2), keep or delete each.
5. [agent] Run the WP0 checks; [you] review the diff.

**One page per song.** The WP0 check is the guarantee. Shrinkable `\blocksep` absorbs small overflows automatically; for a genuinely long song you choose: tighten, split, or put it on the allow-list. Automatic font scaling is deliberately *not* proposed (inconsistent type sizes).

---

## WP5 – Converter and `songs.json`

**State.** An earlier session reported a prototype (`tex2json.py`) that parsed 731 of 733 songs. It is **not in either repository** (checked 3 Nov 2026), so the converter is written from scratch. Because it comes after WP2–WP4, it only needs to understand the cleaned-up, semantic macros (D-108).

**Design.** `songs.json` is a derived export of the songbook: the LaTeX song files stay the only source (D-001), the converter parses them, and the website renders the JSON. Conditions:
1. Generated, never hand-edited.
2. Carries a `schemaVersion`; a JSON Schema is validated in the CI of both repos (this is the contract between them).
3. Semantic only, no layout.
4. Published as a **release asset** of `zpevnik`; the web build downloads the version pinned in its `version.txt` (which the songbook CI already writes) instead of committing generated data into the web repo (this also stops the 4 MB PDF commits from growing that repo).
5. One file for now (≈370 kB gzipped); split only if it passes a few MB.

**Contents.** `version`, `songs[]` (`id`, `title`, `altTitles`, `artists`, `subtitle`, `see`, `order`, `page`, `footnotes`, `images`, `columns`, `blocks[]` → lines → chord/text segments), `artists[]` (from the registry).

**Steps**
1. [agent] Write the converter in `tools/`, in strict mode (an unknown macro is an error), with tests (snapshot tests for ~10 songs plus a whole-book parse).
2. [agent] Read the registry and song metadata; add `page` from the WP0 records.
3. [agent] JSON Schema and validation.
4. [agent] CI job on every push; on release, attach `songs.json` and notify the web repo.
5. [agent] Export the score images from the `.mscz` files in CI with a pinned MuseScore, for both the PDF and the web (D-125). No manual conversion.

---

## WP7 – Legal hygiene (reasonable effort, not legal advice)

Lyrics and arrangements are copyrighted unless public domain; a free PDF and a website are the same kind of "making available".
1. [agent] `noindex` meta tag and `robots.txt` on the website; no sitemap.
2. [you] A short notice page on the site and in the PDF: non-commercial, contact address for removal requests.
3. [agent] A per-song `hidden` switch in the metadata, so any song can be removed from web and PDF within minutes.
4. (Backlog, with the print edition, D-109) If a printed edition is **sold**, that is a different situation from a free PDF; check licensing (e.g. with OSA) before printing.

---

## WP6 – Website (`zpevnik-web`)

The online songbook lives in this repo but is clearly separate from the download page (D-103): the download page stays at `/`; the songbook lives under `/zpevnik/` with its own templates and navigation, and the download page links to it. The web build gets `songs.json` and the PDF from the release assets pinned in `version.txt` instead of committed files (D-110).

1. [agent] `build.py` renders, under the songbook prefix, one page per song, an alphabetical index, artist pages and prev/next in book order (Jinja, no framework).
2. [agent] Chord CSS (inline-block, same rule as WP2), font-size control, existing dark mode.
3. [agent] Build-time search index over title, alternative titles, artist and lyrics (diacritics-insensitive), lazy-loaded.
4. [agent] Screen wake-lock toggle (this is the useful part of the "stage mode").
5. Later: transposition (with the Czech B/H convention), setlists, offline.
Dropped: chord toggle.


---

## WP8 – Editions (D-121)

A song subset (first use: `zpevnik-lite`, a manual selection) built from the same files: a filter on the song list in `tools/generate.py`, an edition file per edition, edition title and version parameters, no dangling links, CI and release asset. Tickets E1–E5 (TICKETS, phase 10). The full book must not change.

## WP9 – Print (D-122)

A print build with its own page geometry from the same files, a check that every song still fits on a page, a preflighted proof and the owner's licensing check. Tickets P1–P4 (TICKETS, phase 3). It needs only WP0–WP1 and can be repeated after WP2–WP3; it needs WP8 only if the book is a subset.
---

## Decisions

Agreed and proposed decisions, with rationale, are recorded in [DECISIONS.md](DECISIONS.md). Superseded here: generated files are no longer committed (D-104).

**Still open:** (1) threshold "≥3" or ">3"; (2) slug rule for bands (`beatles` vs `thebeatles`); (3) the `trikyapovery` split and the Greenhorns override (1–3 are ticket R1); (4) final form of the spacing macros, decided by the WP2 prototype gate; (5) the existing spill of `illbethereforyou` under the pinned TeX Live (ticket S2).
