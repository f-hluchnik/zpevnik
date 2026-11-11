# Zpěvník – tickets

Each ticket is one pull request. Background: [PLAN.md](PLAN.md). Agreed decisions: [DECISIONS.md](DECISIONS.md); a ticket never overrides an agreed decision. What is already done: [HISTORY.md](HISTORY.md). The full text of the finished tickets, as they were on 6 Nov 2026: [archive/snapshot-2026-11-06/TICKETS.md](archive/snapshot-2026-11-06/TICKETS.md). Tickets are grouped into sessions with ready-made prompts in [SESSIONS.md](SESSIONS.md).

Goal: the PDF and an online HTML songbook, both built from the same LaTeX files (D-100). The refactoring is done (HISTORY.md); what is left is editions and print, then the converter, legal and the website (D-132).

Tags: **[agent]** an AI agent can do it · **[you]** needs your decision or review · **⚠** touches many song files, so never run two ⚠ tickets in parallel and merge each before the next · **[strong model]** needs design judgement beyond following the steps: run it with the strongest available model, or have one review the result before merge · size S/M/L.

## Rules for every ticket

1. **Scope.** Change only what the ticket says. If counts, names or files do not match the description, stop and report; do not improvise. Counts in tickets are snapshots: re-derive them with grep or the tools.
2. **Verification.** Every PR gets the song-by-song PDF diff against its base commit (CI, D-105, D-106). The PR description contains *Expected differences* (default: none) and *Actual differences*. A mismatch means the ticket is not done.
3. **Content is untouchable.** Lyrics, chords and Czech text stay as they are unless a ticket says otherwise.
4. **Tools** (`tools/`) use Python ≥ 3.11 and the standard library only.
5. Commit messages, PR descriptions and code comments in English (D-131); the README is Czech.
6. **Git.** One branch and one PR per ticket, in the repository the ticket names (`zpevnik` unless it says `zpevnik-web`). Commit, push the ticket branch and open the PR without asking; never merge, force-push or push to the default branch without the owner's explicit OK.
7. **Status and docs.** The ticket's PR also updates the docs: its row in the *Status* table goes to `done` (the merge makes it true), HISTORY.md at the end of a phase, DECISIONS.md if a decision was made. A change of plan without a ticket gets its own docs-only PR.

## Working environment (verified 3–6 Nov 2026)

- **Planning docs** live in `docs/` of the `zpevnik` repository (D-134), so a session needs only the repository: no link to the owner's computer. They change through pull requests like the code. Large binary files (review PDFs, page images) are not committed: attach them to the PR, or the owner keeps them locally (the older ones are in `songbook-project/docs/archive/` on his computer, see archive/README.md).
- **Building and testing:** use the cloud workspace.
  - Run `apt-get update`, then `apt-get install -y texlive-lang-czechslovak texlive-latex-extra texlive-fonts-extra texlive-music poppler-utils latexmk` in each new session (without the update the packages had no install candidate). The full book then compiles in ≈8 s with one `pdflatex` pass. Python there is 3.13.
  - That TeX Live is 2023 (pdfTeX 1.40.25) like CI, but a local build is only compared with another local build (base vs head). CI is the reference.
- **The owner's computer** (Linux VM shell, if a session is linked to it) has TeX Live 2022 *without* Czech babel and Python 3.10, so neither the book nor the tools run there. It is needed only for the owner's local files, e.g. uncommitted changes in `zpevnik-web`.
- **Cloud session tooling:** `gh pr create` does not work there (GraphQL is blocked); open PRs with `gh api repos/f-hluchnik/zpevnik/pulls -f title=… -f head=<branch> -f base=master -F body=@file`. The clone is shallow: after the first push set the upstream by hand (`git config branch.<b>.remote origin` and `branch.<b>.merge refs/heads/<b>`). CI job logs contain the PDF diff summary (`gh api repos/f-hluchnik/zpevnik/actions/jobs/<id>/logs`).
- **Repositories:** `f-hluchnik/zpevnik` (default branch `master`) and `f-hluchnik/zpevnik-web` (`main`). Both are public: anonymous clones work; pushing and PRs need the repo attached with push access.

## Status

`todo` · `in progress` · `in review` (PR open) · `done` · `blocked` (reason in notes) · `cancelled` (reason in notes).

**Done** (details in HISTORY.md and archive/): S1–S3, R1–R14, H1–H6, C1–C5, V1–V6, V8, V9 (V7 merged into V5), Q1–Q6 (with Q5a, Q5b), Z1 (phases up to 11).

| Ticket | Status | Notes / PR |
|---|---|---|
| K1 | todo | owner: chords for the 8 songs without them |
| E0 | done | build version `8.33.N` (D-133): PR #93, first release v8.33.68 |
| R15 | done | English names (D-143): PR #95; the transitional old-folder handling is listed in R16 |
| E1 | done | D-138, superseded by D-139 |
| E2 | done | editions in the generator and the build (D-144): PR #96 |
| E3 | done | `\seealso` per edition, link check, lints on every edition, `make check` (D-145): PR #97 |
| E4 | todo | owner picks the songs |
| E5 | todo | |
| E6 | todo | `zpevnik-web`; takes over the PDF half of W1 |
| E7 | todo | owner confirms the `lidovky` song list |
| E8 | done | front matter in book order (D-143), the songs from page 9: PR #98 |
| R16 | todo | needs the first song-count change after R15 (8.34.0) |
| P1 | todo | owner: print requirements and the deadline |
| P2 | cancelled | the book is never sold (D-140) |
| P3 | todo | |
| P4 | todo | owner signs off the proof |
| J0 | done | song quirks: PR #88 (D-135); scores: PR #89 (D-136) |
| J1 | todo | strong model (parser design) |
| J2 | todo | strong model (data model = contract between repos) |
| J3 | todo | strong model (schema = contract between repos) |
| J4 | todo | |
| J5 | done | done with J0's scores (D-136): PR #89 |
| L1 | done | D-141 (notice in the PDF colophon and the web footer, licence scope) |
| L2 | todo | |
| W1 | todo | |
| W2 | todo | |
| W3 | todo | |
| W4 | todo | |
| W5 | todo | |
| W6 | todo | |
| W7 | todo | |

## Overview, in the order of work (D-132)

| Phase | Tickets | After it you have |
|---|---|---|
| 1, 2, 4, 5, 6, 11 | done | Safety net, generated lists, clean sources, automatic chord and vertical spacing, code quality and the final command names (HISTORY.md) |
| 10 Editions | E0–E8, R15, R16 | Song subsets such as `zpevnik-lite` and `lidovky` built from the same files, with their own pages; the full book is one of them (D-121, D-139, D-143) |
| 3 Print | P1–P4 | A print build and a checked proof (D-122) |
| 7 Converter | J0–J5 | `songs.json` and score SVGs on every release |
| 8 Legal | L1–L2 | Notice, hide switch |
| 9 Website | W1–W7 | Online songbook |

The converter is written once, against the final command names of phase 11 (D-108, D-131). Phase 8 must be done before the songs go online (W6). Print needs phase 10 only if the printed book is a subset (P1).

---

# Content

### K1 · Songs without chords — [you] · S · needs nothing
8 songs have no chords over the lyrics: 5 have only a `\chords` row (gronskapisnicka, marieklus, noe, panubohudooken, vranabuty), 3 only a score image (ladovskazima, scarboroughfaircarthy, triandele). The owner decides per song whether to add chords (content work). The lint warns about songs without `\chord`. - ladovskazima, scarboroughfaircarthy, triandele are correct without chords. I wonder what would adding an empty `\chord` command with a comment saying it's for linters do? The other songs should be adjusted (read, chords should be added properly, not as list, at least where possible).

---

# Phase 10 – Editions (song subsets, D-121)

Use cases: **`zpevnik-lite`**, a book of selected favourites (manual selection), the main download on the website; **`lidovky`**; possibly the printed book (P1). The generator already works from one song list, so an edition is a filter over it, with its own front matter (D-138). Everything below keeps the full book byte-identical (zero diff).

### E0 · Build version `8.33.N` — [agent] · S · needs nothing
D-133. Today every push to master replaces the PDF of release `v8.33`, whose tag still points at the source of 21 Aug 2026, and commits another PDF to `zpevnik-web`; the version names a song count, not a build.
1. `tools/generate.py` computes `major.minor.patch`: `major.minor` = song count + 100 as today; `patch` = the number of first-parent commits on the current branch since the last commit that changed the song count (Git, standard library `subprocess`). Without Git history the patch is `?` (`8.33.?`), visibly incomplete like today's `?.??` placeholder. Unit tests with a temporary Git repository.
2. The colophon prints the full version; `--version` prints it; CI validates `^[0-9]+\.[0-9]{2}\.[0-9]+$`.
3. Release step: tag `v<version>`, name `Zpěvník v<version>`; fail if the tag already exists (never overwrite or move a tag). `version.txt` in `zpevnik-web` gets the full version. The old tag `v8.33` stays.
4. README (Czech): what the three numbers mean.
**Expected differences:** the colophon page only (version line).

### E1 · Decide the editions design — [you] · S — **done**
Decided by the owner on 9 Nov 2026: **D-138**, superseded by the review **D-139** the same day (selection by song id or artist, front matter per edition, one colophon core, no edition version, the download page configured in `zpevnik-web`, the rules for links and artist sections). The owner's original answers are in the snapshot of this file in the Git history (before the PR of D-138).

### R15 · English names — [agent] · S · ⚠ · needs E0
D-143. A mechanical rename with `git mv`, nothing else: `pisnicky/`→`songs/`, `obrazky/`→`images/`, `sablona.tex`→`song-template.tex`, `preamble/`→`shared-pages/` (`obalka`→`cover`, `patitul`→`halftitle`, `titulnilist`→`titlepage`, `vydavatelskyzaznam`→`imprint`, `upozorneni`→`notice`, `dedikace`→`dedication`, `uvod`→`introduction`), `obsah.tex`→`shared-pages/contents.tex`. Update every reference (`tools/paths.py`, `zpevnik.tex`, `zpevnik.sty`, the tests, CI, the Makefile, the README, `.gitignore`, the current text of the docs; not the archive and not past DECISIONS entries). `tools/build_version.py` counts both the old and the new song folder, with a test that a renamed folder keeps the patch counting. Output paths do not change yet (E2). The owner's branch `new_songs` stays; he re-adds its songs by hand after the merge.
**Expected differences:** none; `generate.py --version` on the rename gives the previous patch + 1, not 0.

### E2 · Generator and build: editions — [agent] · M · needs R15, E1
D-139 and D-143. Zero diff for the full book (the song-by-song diff and identical rendered front-matter pages, D-143 on `/ID`); its generated `.tex` files identical to today's at their new path, except new files.
1. `data/book.toml` and `editions/<name>/edition.toml` (keys and errors as in D-143), read and validated by a small module; a unit test for each error.
2. One `Edition` type for every book; the full book is `editions/full/`. `tools/generate.py --edition <name>` (default `full`) filters the song list once (after an exclusion list, empty until L2) and writes into `build/editions/<name>/generated/`: the include list, the letter contents, the artist index and sections (the full book's rules, restricted to the artists with a song in the edition), the registry, the version, the macros and the resolved page list. The version is the build's (the full song count, D-133), never the edition's song count.
3. Generated macros: the book's title, author, start year and source; the edition's title, subtitle, editors and song count; the version; the derivation sentence (empty for the base edition). The shared pages use them instead of hard-coded text.
4. The skeleton in `zpevnik.tex`, in today's order (E8 changes it): the pages resolved by the generator from `[pages]`, `before_songs` and `after_contents`; the imprint with its core and its slot. Move the full book's dedication, introduction and credits into `editions/full/`. Remove `\setcounter{page}{8}`.
5. Build: `make [pdf] [EDITION=<name>]` creates the output directory and the subfolders LaTeX writes the per-song `.aux` files into, runs latexmk with `-outdir` and the edition (`-usepretex`), and prints the PDF's path; `zpevnik.tex` stops with an error without an edition. `make song` writes `build/songs/<id>.pdf`, the score images go to `build/scores/`, `make clean` deletes `build/`. `check_pages.py` works on any edition's output; `chord_gaps.py` stays on the full book (chord spacing depends on the format, not on the selection). CI, the release and the website copy take the full book's PDF from its new path (the release asset keeps its name until E5); the CI PDF diff also handles a base with the old layout (needed in this PR only).
Test with a throwaway edition that is not committed: songs by id, one artist, an own title page, a `before_songs` page and an imprint fragment.
**Expected differences:** none for the full book.

### E3 · Edition integrity — [agent] · S · needs E2
1. `\seealso` to a song outside the edition prints nothing and takes no space (D-139); a generated list of the songs present lets `zpevnik.sty` decide without a second pass (84 uses in 76 songs on 6 Nov 2026).
2. A link to a missing target fails the edition build: pdfTeX's warning in the log (`… has been referenced but does not exist`). Verify with the throwaway edition that it catches the contents links, `\seealso` and the artist links.
3. Run the one-page check and the lints on the edition.
4. `make check [EDITION=<name>]` (D-143, D-144): the unit tests, the lints, the one-page check and the link check of the edition; the chord check on the edition too (D-145).
**Expected differences:** none for the full book.

### E4 · Choose the songs for `zpevnik-lite` — [you] + [agent] · S · needs E2
The agent adds a small helper that lists song ids with title and artist (filter by artist) to pick from. The owner picks the songs; the agent writes `editions/lite/edition.toml`. **Expected differences:** none for the full book.

### E5 · CI and release — [agent] · M · needs E3, E4
CI builds every edition in `editions/` on pull requests (the build, the one-page check and the link check must pass) and, on pushes to master, attaches `zpevnik-<edition>-<version>.pdf` of each edition (the build version, D-143) to the release of the full book; the release notes list the editions. The PDF diff keeps comparing the full book only. Czech README section on editions: how to make one (by song ids or by artist), how to add a song to one, and that an uncommitted edition folder is a private edition built only locally.

### E6 · Download page with editions — [agent] · M · needs E5 · `zpevnik-web` (and a small PR in `zpevnik`)
D-139, D-110. The website gets the PDFs from the release (this takes over the PDF half of W1): `build.py` downloads the PDFs of the release tagged `v<version.txt>`; the songbook CI stops committing the PDF into `zpevnik-web` and only writes `version.txt`. Which editions the download page shows, and how, is configured in `zpevnik-web` (the songbook has no `publish` flag): `zpevnik-lite` as the main button, the full book as the second one, also served at its fixed URL `zpevnik_last.pdf` (printed QR codes point to it); further editions such as `lidovky` and the separate koledy songbook in their own section. Only `zpevnik_last.pdf` needs a fixed URL; the others may link to the release assets. The owner had an uncommitted change in `templates/base.html` (6 Nov 2026): ask before touching it.

### E7 · `lidovky` as an edition — [you] + [agent] · S · needs E4
All songs of the `zpevnik-lidovky` repository are already in the full book (owner, 9 Nov 2026), and the 76 songs tagged `\artist{lidove}` match the 2020 book (D-139). The agent writes `editions/lidovky/edition.toml` with `artists = ["lidove"]`, compares the result with the song list of the old repository (by title, with E4's helper) and reports any difference, and, if the old book has its own title page or foreword, adds its front matter; the owner confirms the list and the front matter, and archives the old repository himself.

### E8 · Front matter in book order — [agent] · S · needs E3
D-143. The skeleton gets the Czech book order: cover, blank, halftitle, blank, title page (a right-hand page), the imprint on its back, then `before_songs`. The songs start on page 9 instead of 8. (The `\hspace{10mm}` before the first credit went in E2, D-144.)
**Expected differences:** the front-matter pages (order, one new blank page); every page number one higher (the contents print no page numbers, only links). The song-by-song diff reports every song: check that each differs only in its page number.

### R16 · Drop the old song folder from the version — [agent] · S · needs the first song-count change after R15
D-143, D-144. Once a commit after R15 has changed the song count (the version is 8.34.0 or later), `tools/build_version.py` stops counting `pisnicky/` and its rename tests go. The other traces of the old folder and of the layout before editions, all removed here: `LEGACY_SONGS_DIR` in `tools/paths.py`, the `pisnicky/` pathspec of the *List newly added songs* step in the CI workflow, `book_output_dir`'s fallback to the root in `tools/pdfdiff.py` (a base built before E2) and the `else latexmk` branch of the *Compile base* step. (E2 already removed `songs_dir()` and the fallback of `tools/check_pages.py`.) **Expected differences:** none.

---

# Phase 3 – Print (D-122)

The printed edition is important and has a deadline. The screen PDF must never change because of it (zero diff).

### P1 · Print requirements — [you] · S
Decide and write down (the agent records it as a DECISIONS entry): the **deadline**; page size and binding (A4, A5, …; ring binding needs no gutter); whether the scaled screen PDF reads well on paper (D-142: print A4 pages "2 per sheet" to see A5 size); the binding offset for two-sided printing; paper and colour (black and white or colour); the printer's technical requirements (PDF version or PDF/X, embedded fonts, bleed, crop marks); whether links stay visible; the number of copies; **full songbook or a subset** (a subset needs E1–E4 first).

### P2 · Licensing check — [you] · S — **cancelled**
Was: check the licensing before selling printed copies. The book is never sold (D-140).

### P3 · Print build — [agent] · M · needs P1 (and E4 for a subset)
D-142. The print format is a step after the build, separate from the edition (D-139): it combines with the full book or any edition and writes into an output directory of its own; no copy of song content.
1. **Scaled print (the default):** scale the edition's screen PDF to the print page size from P1 (A4 to A5 is exactly 1/√2), with the offset of odd and even pages for the binding if P1 asks for it, blank pages where a spread needs them (songs starting on a right-hand page, an even page count), and the cover outside the numbered book block if P1 says so. Use what the pinned TeX Live has (`pdfpages` in a small wrapper document, or `pdfjam`); no new dependency. Check page size and page count; the contents links still work.
2. **Geometry trial:** for the specific printed edition, build it once with a LaTeX page geometry for the print size (E2's parameters, no copy of `zpevnik.tex`), run the one-page check, report every song that spills, and attach a few pages of both versions for comparison; propose a fix per song (a `\large` as D-129 allows, a two-page allow-list entry), never fix silently. The owner chooses; the trial is not merged unless he picks it.
**Expected differences:** none for the screen PDF.

### P4 · Print proof check — [agent] + [you] · S · needs P3
Preflight the PDF: fonts embedded (`pdffonts`), page size and page count, colour space against the printer's requirement (report, convert only if asked), crops of the first page, a middle page, a two-column song and the contents at 100%. The owner reads a proof and signs off. Record the commit and version that went to the printer in the Status table.

---

# Phase 7 – Converter and `songs.json`

### J0 · Song quirks before the converter — [you] + [agent] · M · needs nothing
The converter is strict (an unknown macro is an error), so every remaining special case in the songs needs a decision first: give it a semantic command, let the converter ignore it as PDF-only layout, or keep it and say how the converter treats it. The agent re-derives the list with grep at the start and the owner decides each item; then the agent implements the agreed commands (zero diff where possible).
1. **Score images** (owner: agreed): 15 songs place a score by hand (`\vspace{-25…-58pt}`, `\hspace{20pt}`, `21pt` or `9mm`, `\includegraphics[width=…]`); only 2 have a `% KEEP` comment. A `\score[offset]{file}` command: the indent is one constant inside it, the per-song vertical offset an explicit optional argument (until J5's trimmed export makes it one constant), the converter reads one command. Zero diff.
2. **Echo and backing vocals** as `\textsuperscript{\Large\emph{…}}` (`kratkypopisleta`) or `\textsuperscript{\emph{…}}` (`dvakrat`): a command such as `\echo{…}`, or leave them as formatting.
3. Layout in a few songs: `multicols` and `\columnbreak` (cernymuz, lojzaaliza, milionar, promeny, zkratky), `\placetextbox` (vosa), the negative `\hspace` inside `\rep` (velicenstvokat), `center` (jedesohajzvidna, kolenasejchalupecky), `\note{\small …}` (jednourano): PDF-only layout the converter skips, or a semantic form (e.g. `columns` in `songs.json`).
4. `zapomnetliva`: the repeat mark stands before the speaker name (nitpick left from Q5).
5. Anything else the strict parser of J1 would reject; footnotes in `\song{}` stay (Q5).
**Decided (owner, 8 Nov 2026):** items 2–5 and the rest of the list in D-135; item 1 together with J5 (a standard MuseScore export that places itself, no per-song offsets).

### J1 · Converter package — [agent] · **[strong model]** · L · needs Q4, Q5, J0
1. Write the converter in `tools/songbook/` as a package: parser, model, command line. It starts from scratch (the earlier `tex2json.py` prototype is in neither repository). Strict: an unknown macro is an error; it understands only the command set after Q4 (D-108, D-131).
2. Song metadata (`\artist`, `\alttitle`, `\toctitle`, `\collection`); the title and its footnote apart (Q5 item 4); `\cue` as a reference to another block; repeat marks rendered as the PDF does.
3. Tests: snapshot tests for 10 songs plus a whole-book parse that must succeed for all songs in under 5 s.

### J2 · Assemble `songs.json` — [agent] · **[strong model]** · M · needs J1
Top level: `schemaVersion`, `version`, `songs[]` in book order (the generated include order), `artists[]` from the registry. Each song: `id`, `title`, `altTitles`, `artists`, `collections`, `subtitle`, `see` (from `\seealso`), `order`, `page` (from the page checkpoints), `footnotes`, `images`, `columns`, `blocks[]` (lines of chord/text segments).

### J3 · JSON Schema — [agent] · **[strong model]** · S · needs J2
`tools/songs.schema.json`; validate the output in tests and in CI.

### J4 · CI and release asset — [agent] · M · needs J3
After the compile, run the converter and the schema validation. On pushes to master, add `songs.json` to the `files:` of the release step. PRs only validate.

### J5 · Scores from MuseScore — [agent] + [you] · M · needs J4
**Done together with J0 item 1 (D-136), 8 Nov 2026:** the export is `tools/scores.py` with a shared style, the PDF uses the converted SVG, and every score places itself with `\score{name}`. Left for J4: put the SVGs (`build/scores/*.svg` since E2, D-143) into the release and reference them from `songs.json`. The text below is the original plan.
The `.mscz` files are the source; CI exports the images, so the PDF and the web use the same export (D-125). A score is a single page by principle.
1. **Prototype first and report before building on it:** a pinned MuseScore 4 in CI with `-o file.svg -T 0` (trimmed SVG, documented for single-page scores only). pdfLaTeX cannot include SVG, so for the PDF either convert the SVG (e.g. `rsvg-convert`) or export a PDF and crop it with `pdfcrop`. Compare a few results with today's images.
2. One `.mscz` per image. Missing (5 Nov 2026): `tickettoride` uses `ticket_to_ride_intro.png`, which has no source. These `.mscz` produce more than one image today: `morseovka.mscz` (`morseovka_1.png`, `morseovka_2.png`), `pohadka.mscz` (`pohadka.pdf` and `pohadkaref.pdf`), `reddwarftheme.mscz` (intro and outro), `slunecnyhrob.mscz` (intro and solo). Unused: `morseovkasolo1–3.pdf`. The owner provides the missing files.
3. The exported images are build output (D-104), not committed; remove the committed PDFs and PNGs once the export works. The SVGs go into the release as one zip and are referenced from `songs.json`.
4. The `\vspace` and `\hspace` next to scores stay (D-124), but check them against the new crop.
**Expected differences:** small shifts of the score images; the owner reviews them.

---

# Phase 8 – Legal

### L1 · Notice text — [you] · S — **done**
A short text in Czech and English: non-commercial, contact address for removal requests. It goes into the website footer and the PDF colophon. Done on 9 Nov 2026 (D-141): `shared-pages/notice.tex` (then `preamble/upozorneni.tex`) in the colophon, the footer in `zpevnik-web/templates/base.html`, and the scope of the Apache licence in `LICENSE` and the README.

### L2 · Hide switch — [agent] · S · needs E2, J2, L1
`data/hidden.txt` with one song id per line. The generator leaves those songs out of every book, using E2's song filter (TOC, index and include list follow); the converter leaves them out of `songs.json`; a lint checks that each id exists. (This hides songs from the outputs; only deleting the file removes it from the repository.)

---

# Phase 9 – Website (`zpevnik-web`)

### W1 · Load the data — [agent] · M · needs J4
`build.py` downloads `songs.json` from the release tagged `v<version.txt>` (the songbook CI already writes `version.txt` after creating the release) into an uncommitted folder, validates `schemaVersion`, and fails loudly if missing. Add a local option to point at a file.
The PDFs already come from the release since E6 (D-110, D-138); W1 adds `songs.json` the same way.

### W2 · Song pages — [agent] · L · needs W1
The online songbook is separate from the download page (D-103): it lives under `/zpevnik/`, with its own templates and navigation; the download page at `/` stays as it is, plus one link to the songbook.
Jinja template, one page per song at `/zpevnik/<id>/`: chords above lyrics (each chord and its text in an inline-block that keeps spaces; chord width is respected, the rule of D-123), labels, footnotes, score SVGs, the existing dark mode, a font-size control. It must read well without JavaScript. Every page carries `<meta name="robots" content="noindex">`.

### W3 · Index, artists, navigation — [agent] · M · needs W2
Alphabetical index (same order as the PDF, taken from `songs.json`, never re-sorted), artist pages at `/zpevnik/interpret/<slug>/`, collection pages, alternative titles listed, previous/next links in book order, "open in PDF" using `page`.

### W4 · Search — [agent] · M · needs W2
Build-time index over title, alternative titles, artist and lyrics (about 270 kB gzipped), loaded on first use, diacritics-insensitive, no libraries unless tiny.

### W5 · Wake lock — [agent] · S · needs W2
A toggle on the song page using the Screen Wake Lock API; hidden where unsupported.

### W6 · Robots and notice — [agent] · S · needs W2, L1
`robots.txt` disallowing everything, no sitemap. The notice is already in the footer of every page (L1, D-141); no separate notice page. Hidden songs are absent because they are absent from the JSON.

### W7 · Release check — [agent] · S · needs W3–W6
Build under 1 minute; every song page present (minus hidden); every internal link resolves; screenshots of 3 songs on a phone-sized viewport; update the web README.

---

# Documentation

### Z1 · Project history and helper files — [agent] · S · at the end of every phase
Done for every phase up to 11 (HISTORY.md, docs/archive/). At the end of each phase, in the PR of its last ticket: add the phase to HISTORY.md (what changed and why, numbers, PRs, decisions), move its finished ticket texts and status rows to `docs/archive/<phase>/TICKETS.md` and its text helper files next to them. Binary review files are not committed (attach them to the PRs). Exact duplicates may be deleted; everything else is moved.

---

## Backlog (not ticketed)

- Transposition (Czech B/H convention), setlists, offline use, fit-to-screen, ChordPro export.
- **Capo note versus song remark** (owner, 6 Nov 2026): `\note` belongs to the next block (right for "capo 3"); a standalone remark is written as an unnumbered `\vers{\emph{…}}`. A separate remark command would give the web version a note type; decide in J1 if the converter needs it.
- **Grouping verses, tight versus loose** (owner, `ejhorahora`): short one-line verses looked better tight; a way to group verses (tight inside, normal gap between groups). Not necessary.
- **Bigger gap between groups of verses, and bilingual songs** (owner, `jednoubudemdal`): the Czech and the English version share one page; by the logic of the songbook they should be two songs. Not necessary.
- **Refactoring story on the website** (owner, 5 Nov 2026): notes are in HISTORY.md; write the article when the online songbook exists.
- **CI speed** (4 Nov 2026): a PR check takes about 3.5 min; 132 s is the first `xu-cheng/latex-action` step downloading the TeX Live 2023 container, poppler adds 12–29 s. Tried and not adopted: Ubuntu's own TeX Live 2023 via apt (identical output, but a 15 min install; PR #37, closed). Not tried: skip the poppler install if the runner has it; a smaller TeX image with the needed packages. Q3 may change the picture.
