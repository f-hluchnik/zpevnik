# Zpěvník modernisation plan

**Goal:** the songbook as a downloadable PDF *and* an online HTML songbook on the website, both built from the same LaTeX song files, with the technical debt paid off first ([DECISIONS.md](DECISIONS.md) D-100). Editions (song subsets) and a print edition are in scope too (D-121, D-122); the koledy songbook is not.

Companion files: [TICKETS.md](TICKETS.md) (ordered, self-contained tickets and their status), [SESSIONS.md](SESSIONS.md) (tickets grouped into working sessions), [DECISIONS.md](DECISIONS.md) (agreed decisions and rationale), [HISTORY.md](HISTORY.md) (what was done, and notes for the article on the website). Helper files of finished phases and the original inventory are in [archive/](archive/); this plan as it was before the 6 Nov 2026 cleanup is in archive/snapshot-2026-11-06/.

Tags: **[agent]** = suitable for an AI agent. **[you]** = needs your decision or visual review.

## Principles

1. **One source of truth:** the song files plus one artists registry. The table of contents, the include list, the artist index, the web pages and `songs.json` are all generated from them.
2. **Song files say *what*, never *how far*:** a chord, a verse, an artist; never millimetres of space.
3. **One song per page in the PDF is enforced by CI**, not by eye.
4. **Generated files are produced at build time** (`make`), never committed (D-104). One song still compiles with just the style file (Overleaf, D-005).
5. **Every change is checked against a baseline PDF**, built in the same CI job from the base commit with the same pinned TeX Live, and compared song by song (D-105, D-106).
6. **Songs are ordered by Czech collation of their title**, never by file name (D-107).

## Order of work (D-108, D-132, D-147)

| WP | What | Status | Tickets |
|---|---|---|---|
| 0 | Safety net (pinned TeX Live, PDF diff, one-page check) | done | S1–S3 |
| 1 | Artists registry, generated TOC and include list | done | R1–R14 |
| 4 | Source hygiene | done | H1–H6 |
| 2 | Chord spacing | done | C1–C5 |
| 3 | Vertical spacing | done | V1–V9 |
| Q | Code quality and final command names | done | Q1–Q6 |
| 8 | Editions (song subsets), build version | done except E4 (after print) | E0–E4, E7, E8 |
| 6a | Delivery of the editions: CI release, download page | done | E5–E6 |
| 9 | Print | **next**; P4 after the owner's new songs | P0, P1, P3, P4 |
| A | Audits: README, unit tests, build speed | done | A1–A3 |
| 5 | Converter and `songs.json` | later | J1–J5 |
| 7 | Legal hygiene | done (`songs.json` part of L2 in J2) | L1–L2 |
| 6 | Website | later | W1–W7 |

WP0–WP4 are described in HISTORY.md (results) and in the archived plan (the original problem statements). The cleanup came before the converter so that the converter is written once, against semantic macros only, and `songs.json` carries no layout (D-108). Editions and print were pulled ahead of the converter in D-132; D-147 added the delivery of the editions and the audits before it, and moved `zpevnik-lite` behind the print edition.

---

## WP-Q – Code quality (D-131)

The refactoring is closed by a review of the code as a senior engineer would leave it:
- `zpevnik.sty` ordered by topic, English comments with the reason, internals under `\zp@`, named constants, idiomatic optional arguments (`\NewDocumentCommand`), no dead code (Q1);
- the Python tools: one registry module, one place for paths, one command-line style (Q2);
- CI runs the assertions of the test documents, not just their compilation (Q3);
- the song commands get their final names before the converter makes them its grammar: `\chorus`, `\coda`, `\subtitle`, `\speaker`, `\seealso`, optional numbers, one `\cue` for repeat marks (Q4), plus the last song-source leftovers and the decision on song footnotes (Q5).

## WP8 – Editions (D-121)

A song subset built from the same files, as a songbook of its own (D-139): `zpevnik-lite` (a manual selection, the main download on the website) and `lidovky` (until now a separate repository, now the songs of one registry entry). A folder per edition with its selection (song ids and/or artists) and an explicit page contract: each replaceable page is shared or its own, extra pages before the songs and after the contents (D-143); a filter on the song list in `tools/generate.py`, with the full book as the edition `full`; one `build/` root and `make` as the only entry point; the edition named by the build it comes from; no dangling links; one imprint core in every book, with the derivation sentence in every edition but the full book; CI, release asset and the download page (configured in `zpevnik-web`). Editions are independent of the print format. The full book must not change. The same filter later serves the hide switch (L2). First, E0 makes the version name one build (`8.33.N`, D-133), which the edition releases and the print proof rely on.

## WP9 – Print (D-122)

A print version of any edition: by default the screen PDF scaled to the print page size (A4 to A5 is exactly 1/√2), with the binding offset and the blank pages a printed book needs; a LaTeX page geometry only as a trial for a specific printed edition (D-142); and a preflighted proof. The print format combines with any edition (D-139); it needs WP8 only if the printed book is a subset. The book is never sold (D-140).

---

## WP5 – Converter and `songs.json`

**State.** J1 done (12 Nov 2026, D-164): the converter `tools/songbook/` reads every song into an in-memory model, strictly; `make check` and CI run it. J2 done (12 Nov 2026, D-165): `make json` writes `build/songs.json` from the full book. Next: its schema (J3), the release (J4).

**Design.** `songs.json` is a derived export: the LaTeX song files stay the only source (D-001), the converter parses them, the website renders the JSON. Conditions:
1. Generated, never hand-edited.
2. Carries a `schemaVersion`; a JSON Schema is validated in the CI of both repos (this is the contract between them).
3. Semantic only, no layout.
4. Published as a **release asset** of `zpevnik`; the web build downloads the version pinned in its `version.txt` instead of committing generated data into the web repo (D-110).
5. One file (4.9 MB, 455 kB gzipped, D-165); the website reads it at build time only, so its size reaches no reader.

**Contents.** `schemaVersion`, `version`, `songs[]` (body → lines → segments and marks), `contents` and `artists[]` in book order: the shape is D-165.

**Steps.** First the owner decides the remaining song quirks (score images get a `\score` command, echo lines, layout-only places; J0). Then the converter in `tools/`, strict (an unknown macro is an error), with snapshot tests and a whole-book parse (J1); `songs.json` with registry, metadata and `page` (J2); JSON Schema (J3); CI and release asset (J4); score images exported from the `.mscz` files with a pinned MuseScore, for the PDF and the web (J5, D-125; done with J0, D-136). Done so far: J0, J0a, J1, J1a, J2, J5.

## WP7 – Legal hygiene (reasonable effort, not legal advice)

Lyrics and arrangements are copyrighted unless public domain; a free PDF and a website are the same kind of "making available".
1. `noindex` meta tag and `robots.txt` on the website; no sitemap (D-006, W6).
2. A short notice in the PDF colophon and the web footer, in Czech and English: non-commercial, contact address for removal requests (L1, done: D-141); the Apache licence covers only the owner's own work, not the songs (D-141).
3. A per-song hide switch, so any song can be removed from web and PDF within minutes (L2, using the edition filter).

The book is never sold, printed or not (D-140), so there is no licensing check for selling.

## WP6 – Website (`zpevnik-web`)

The online songbook lives in the web repo but is clearly separate from the download page (D-103): the download page stays at `/`; the songbook lives under `/zpevnik/` with its own templates and navigation, and the download page links to it. The web build gets `songs.json` and the PDF from the release assets pinned in `version.txt` instead of committed files (D-110).
1. `build.py` renders one page per song, an alphabetical index, artist pages and prev/next in book order (Jinja, no framework).
2. Chord CSS (inline-block, the rule of D-123), font-size control, existing dark mode.
3. Build-time search index over title, alternative titles, artist and lyrics (diacritics-insensitive), lazy-loaded.
4. Screen wake-lock toggle.
5. Later: transposition (with the Czech B/H convention), setlists, offline.

## Open owner decisions

Listed with what they block in [SESSIONS.md](SESSIONS.md) (*Owner decisions that gate sessions*).
