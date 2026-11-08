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
  - Run `apt-get update`, then `apt-get install -y texlive-lang-czechslovak texlive-latex-extra texlive-fonts-extra poppler-utils latexmk` in each new session (without the update the packages had no install candidate). The full book then compiles in ≈8 s with one `pdflatex` pass. Python there is 3.13.
  - That TeX Live is 2023 (pdfTeX 1.40.25) like CI, but a local build is only compared with another local build (base vs head). CI is the reference.
- **The owner's computer** (Linux VM shell, if a session is linked to it) has TeX Live 2022 *without* Czech babel and Python 3.10, so neither the book nor the tools run there. It is needed only for the owner's local files, e.g. uncommitted changes in `zpevnik-web`.
- **Cloud session tooling:** `gh pr create` does not work there (GraphQL is blocked); open PRs with `gh api repos/f-hluchnik/zpevnik/pulls -f title=… -f head=<branch> -f base=master -F body=@file`. The clone is shallow: after the first push set the upstream by hand (`git config branch.<b>.remote origin` and `branch.<b>.merge refs/heads/<b>`). CI job logs contain the PDF diff summary (`gh api repos/f-hluchnik/zpevnik/actions/jobs/<id>/logs`).
- **Repositories:** `f-hluchnik/zpevnik` (default branch `master`) and `f-hluchnik/zpevnik-web` (`main`). Both are public: anonymous clones work; pushing and PRs need the repo attached with push access.

## Status

`todo` · `in progress` · `in review` (PR open) · `done` · `blocked` (reason in notes).

**Done** (details in HISTORY.md and archive/): S1–S3, R1–R14, H1–H6, C1–C5, V1–V6, V8, V9 (V7 merged into V5), Q1–Q6 (with Q5a, Q5b), Z1 (phases up to 11).

| Ticket | Status | Notes / PR |
|---|---|---|
| K1 | todo | owner: chords for the 8 songs without them |
| E0 | todo | build version `8.33.N` (D-133); needs nothing, before E5 and P4 |
| E1 | todo | owner decisions |
| E2 | todo | |
| E3 | todo | |
| E4 | todo | owner picks the songs |
| E5 | todo | |
| P1 | todo | owner: print requirements and the deadline |
| P2 | todo | owner: licensing check before selling |
| P3 | todo | |
| P4 | todo | owner signs off the proof |
| J0 | in review | song quirks: PR #88 (D-135); scores: PR #89 (D-136) |
| J1 | todo | strong model (parser design) |
| J2 | todo | strong model (data model = contract between repos) |
| J3 | todo | strong model (schema = contract between repos) |
| J4 | todo | |
| J5 | in review | done with J0's scores (D-136): PR #89 |
| L1 | todo | owner: notice text |
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
| 10 Editions | E0–E5 | Song subsets such as `zpevnik-lite` built from the same files (D-121) |
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

Use cases: **`zpevnik-lite`**, a book of selected favourites (manual selection), exported now and then; possibly the printed book (P1). The generator already works from one song list, so an edition is a filter over it. Everything below keeps the full book byte-identical (zero diff).

### E0 · Build version `8.33.N` — [agent] · S · needs nothing
D-133. Today every push to master replaces the PDF of release `v8.33`, whose tag still points at the source of 21 Aug 2026, and commits another PDF to `zpevnik-web`; the version names a song count, not a build.
1. `tools/generate.py` computes `major.minor.patch`: `major.minor` = song count + 100 as today; `patch` = the number of first-parent commits on the current branch since the last commit that changed the song count (Git, standard library `subprocess`). Without Git history the patch is `?` (`8.33.?`), visibly incomplete like today's `?.??` placeholder. Unit tests with a temporary Git repository.
2. The colophon prints the full version; `--version` prints it; CI validates `^[0-9]+\.[0-9]{2}\.[0-9]+$`.
3. Release step: tag `v<version>`, name `Zpěvník v<version>`; fail if the tag already exists (never overwrite or move a tag). `version.txt` in `zpevnik-web` gets the full version. The old tag `v8.33` stays.
4. README (Czech): what the three numbers mean.
**Expected differences:** the colophon page only (version line).

### E1 · Decide the editions design — [you] · S
Answer the six questions; the agent's proposed defaults are marked with *.
1. How an edition is defined: `editions/<name>.toml` (title, optional subtitle, file name, list of song ids)*, or a tag in the song files. The order is always the D-107 collation, never the list order*.
   - I think that the edition should be defined as list of song ids plus it's optional own title page, dedication, colophon... basically everything in preamble. Example usecase: "Skautský zpěvník" - this is the printed edition we should prepare. It gets its own preable (titulní stránka, název, obálka, patitul, titulní list, úvod, dedikace, vydavatelský záznam). We can think of it as a new songbook derived from the current one, and it only gets the songs and table of contents from it. It can add as many pages it wants either before the songs or after the TOC. Therefore, an edition should be stored in it's own directory within our repo (I'm thinking `/editions/<concrete-edition>`) and should be compiled only on demand. An exception would be zpevnik-lite - this one should be regularly published to the website.
   - About the zpevnik-lite: I see the future like this:
      - on the website, the main button is to download zpevnik-lite
      - there is a secondary button for the full version, which is also downloaded under the static link `zpevnik_latest.pdf`, because I already have QR codes for that.
      - on the website, there is the online version of the zpevnik under `zpevnik.hluchnikovi.cz/zpevnik` (or something better if we can think of something that would make more sense)
      - on the website, there are ternary buttons (or maybe a section) for the carols songbook (this is, however, not derived from the base zpevnik) and for the "lidovky" zpevnik. AFAIK the zpevnik-lidovky now has it's own repo, but we should turn it into an edition as it's a perfect example of an edition
2. What happens to a `\seealso` link (and any other reference) to a song that is not in the edition: leave the link out*, or print the title without a link.
   - If the song that the `\seealso` points to is missing in the edition, don't include the link at all (that means, no link, nothing printed). Basically act as if the `\seealso` song never existed.
3. Artist sections and index: only artists with at least one song in the edition*; the threshold of 3 (D-119) does not apply*.
   - Yes, the threshold should not apply in an edition.
4. Name and version of an edition book, for example `zpevnik-lite` plus the book version*.
   - The filename doesn't matter much. The real name we should be able to choose (similarly as the title page and colophon, see bellow). The edition book should have it's own version and note saying which base zpevnik version it was derived from.
5. Where it is published: a release asset only*, or also the download page of `zpevnik-web`.
   - It depends on the edition. For example, zpevnik-lite should go to the zpevnik-web. But there can be some editions that are only meant for printing. These could be only published as a release asset. But wouldn't them be buried in the release assets then?
6. Title page and colophon text of each edition.
   - When creating an edition, we should be able to submit a custom title page and at least edit the colophon. I know it's tricky since we have that generated, but I still see the preamble directory in the repo. I'm thinking that we could allow a custom colophon when present and only check if it contains the mandatory parts (we should decide what is mandatory first).

### E2 · Generator: edition filter — [agent] · M · needs E1
`tools/generate.py --edition <name>` (default: the full book) reads `editions/<name>.toml`, filters the song list once and generates everything from it: include list, letter contents, artist index and sections. Edition title, subtitle and version go to a generated `edition.tex` that `patitul`, `titulnilist`, `uvod` and `vydavatelskyzaznam` use instead of the hard-coded title. An edition's generated files go to their own folder, so both builds can run in one checkout (the simplest way that leaves `make` unchanged). An unknown song id is an error. Unit tests. Design the filter so that L2's hidden songs are the same mechanism (an exclusion list applied before the edition filter). **Expected differences:** none for the full book; `generated/` byte-identical except the new `edition.tex`.

### E3 · Links to songs outside the edition — [agent] · S · needs E2
Implement the E1 rule for `\seealso` (84 uses in 76 songs on 6 Nov 2026); a generated list of the songs present (like the artist registry) lets `zpevnik.sty` decide without a second pass. Add a check that every contents link, `\seealso` and artist-section link of an edition points to an existing target, and fails otherwise; run the one-page check and the lints on the edition. **Expected differences:** none for the full book.

### E4 · Choose the songs for `zpevnik-lite` — [you] + [agent] · S · needs E2
The agent adds a small helper that lists song ids with title and artist (filter by artist) to pick from. The owner picks the songs; the agent writes `editions/lite.toml`; the lint checks that every id exists. **Expected differences:** none for the full book.

### E5 · CI and release — [agent] · M · needs E3, E4
CI builds every edition in `editions/` on pull requests (the build, the one-page check and the link check must pass) and, on pushes to master, attaches `zpevnik-<name>-<version>.pdf` to the same release as the full book. No change in `zpevnik-web` unless E1 says so. The PDF diff keeps comparing the full book only. Czech README section on editions: how to add a song to one.

---

# Phase 3 – Print (D-122)

The printed edition is important and has a deadline. The screen PDF must never change because of it (zero diff).

### P1 · Print requirements — [you] · S
Decide and write down (the agent records it as a DECISIONS entry): the **deadline**; page size and binding (A4, A5, …); margins including the gutter for two-sided printing; paper and colour (black and white or colour); the printer's technical requirements (PDF version or PDF/X, embedded fonts, bleed, crop marks); whether links stay visible; the number of copies; **full songbook or a subset** (a subset needs E1–E4 first).

### P2 · Licensing check — [you] · S
Before **selling** printed copies, check the licensing (e.g. with OSA and the rights holders of the lyrics and chords). A sold book is not the same as a free PDF. Record the result in DECISIONS. It blocks selling, not building.

### P3 · Print build — [agent] · M · needs P1 (and E4 for a subset)
A separate build target (`make print`) with the page geometry from P1, built from the same song files and generated files; no copy of song content. Every song must fit on one page, and a page smaller than A4 makes some spill: run the one-page check with the print geometry, report every song that takes more pages and propose a fix per song (a `\large` as D-129 allows, a two-page allow-list entry); do not change song content or fix silently. Also: even page count, blank pages where a spread needs them, the contents and the artist index still resolve, links printed without colour (or as P1 says). **Expected differences:** none for the screen PDF.

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
**Done together with J0 item 1 (D-136), 8 Nov 2026:** the export is `tools/scores.py` with a shared style, the PDF uses the converted SVG, and every score places itself with `\score{name}`. Left for J4: put the SVGs (`generated/scores/*.svg`) into the release and reference them from `songs.json`. The text below is the original plan.
The `.mscz` files are the source; CI exports the images, so the PDF and the web use the same export (D-125). A score is a single page by principle.
1. **Prototype first and report before building on it:** a pinned MuseScore 4 in CI with `-o file.svg -T 0` (trimmed SVG, documented for single-page scores only). pdfLaTeX cannot include SVG, so for the PDF either convert the SVG (e.g. `rsvg-convert`) or export a PDF and crop it with `pdfcrop`. Compare a few results with today's images.
2. One `.mscz` per image. Missing (5 Nov 2026): `tickettoride` uses `ticket_to_ride_intro.png`, which has no source. These `.mscz` produce more than one image today: `morseovka.mscz` (`morseovka_1.png`, `morseovka_2.png`), `pohadka.mscz` (`pohadka.pdf` and `pohadkaref.pdf`), `reddwarftheme.mscz` (intro and outro), `slunecnyhrob.mscz` (intro and solo). Unused: `morseovkasolo1–3.pdf`. The owner provides the missing files.
3. The exported images are build output (D-104), not committed; remove the committed PDFs and PNGs once the export works. The SVGs go into the release as one zip and are referenced from `songs.json`.
4. The `\vspace` and `\hspace` next to scores stay (D-124), but check them against the new crop.
**Expected differences:** small shifts of the score images; the owner reviews them.

---

# Phase 8 – Legal

### L1 · Notice text — [you] · S
A short text in Czech and English: non-commercial, contact address for removal requests. It goes into the website footer and the PDF colophon.

### L2 · Hide switch — [agent] · S · needs E2, J2, L1
`data/hidden.txt` with one song id per line. The generator leaves those songs out of every book, using E2's song filter (TOC, index and include list follow); the converter leaves them out of `songs.json`; a lint checks that each id exists. Put the L1 text into the colophon. (This hides songs from the outputs; only deleting the file removes it from the repository.)

---

# Phase 9 – Website (`zpevnik-web`)

### W1 · Load the data — [agent] · M · needs J4
`build.py` downloads `songs.json` from the release tagged `v<version.txt>` (the songbook CI already writes `version.txt` after creating the release) into an uncommitted folder, validates `schemaVersion`, and fails loudly if missing. Add a local option to point at a file.
The PDF comes the same way (D-110): the songbook CI stops committing `static/files/zpevnik_last.pdf` and only writes `version.txt` (a separate PR in `zpevnik`); the download page keeps its URL and `download` file name.

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
`robots.txt` disallowing everything, no sitemap, notice page and footer link. Hidden songs are absent because they are absent from the JSON.

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
