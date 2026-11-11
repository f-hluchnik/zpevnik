# Implementation sessions

How the remaining tickets in [TICKETS.md](TICKETS.md) are grouped into working sessions, and the prompt for each. Sessions 1–20 are done (HISTORY.md; their blocks are in archive/snapshot-2026-11-06/SESSIONS.md and archive/phase-11-code-quality/SESSIONS.md). Numbering continues from 20, in the order of work of D-132 as amended by D-147; a letter after a number means "in this slot, after it".

**To start a session**, open a Claude Code session with the `f-hluchnik/zpevnik` repository (from any device; the desktop app with the `songbook-project` folder linked works too, but is needed only for the owner's local files), choose the model listed for it, and paste the one-line prompt, e.g. `Run session 20 from docs/SESSIONS.md.`

**Why groups, not one session per ticket:** every new session pays a fixed cost (reading CLAUDE.md and the docs, installing TeX, cloning), while a long session re-sends its whole history on every turn. A group of related tickets that share context, ending at a merge, is the cheapest unit. Don't continue into the next group in the same session.

---

## Common rules (every session)

1. **Read only:** `CLAUDE.md`; this file's *Common rules* and your session's block; in `TICKETS.md` the sections *Rules for every ticket*, *Working environment*, *Status* and your session's tickets; and the DECISIONS / PLAN sections your block lists. Don't read whole files you don't need.
2. **Check prerequisites:** every ticket your block lists under *Needs* must be `done` in the Status table. If one isn't, or an owner decision it needs is missing, stop and say so.
3. **Setup:** work in the cloud workspace: attach the repo(s) in scope with push access (always `zpevnik`, which holds these docs), clone them, check out the latest default branch, read the docs from there, and install the TeX packages listed under *Working environment*. Confirm that the base builds before changing anything. If the session is linked to the owner's computer, check the Git state of its working copies too, read-only.
4. **Per ticket:** give a plan of at most 5 lines plus anything in the ticket that doesn't match reality. Wait only if something doesn't match or a decision is needed. One branch and one PR per ticket; don't stack branches.
5. **Git:** when a ticket is ready, review your own diff (CLAUDE.md, *After implementation*), commit it on its own branch, push the branch and open the PR without asking (the owner reviews in the PR). Never merge, force-push, or push to the default branch. After opening a PR, stop until the owner has merged it, then continue with the next ticket of the session.
6. **Verification:** verify locally what you can, then in the PR's CI run. Put the diff report in the PR description as *Expected differences* / *Actual differences*. Never claim CI behaviour you haven't seen in an actual run.
7. **Token hygiene:** keep command output small (`grep -c`, `head`, summaries); don't re-read files you already have; don't paste whole diffs of song files into the conversation.
8. **End of each ticket:** in the ticket's PR, set its row in the Status table to `done` and record any new decision in DECISIONS.md (TICKETS rule 7); and report: what changed, what was verified and how, expected vs actual differences, anything that didn't match the ticket. End of session: list what is left and the next session to run.
9. **End of a phase:** in the PR of its last ticket, add the phase to docs/HISTORY.md and move its ticket texts and text helper files to docs/archive/<phase>/ (TICKETS Z1).

---

## Sessions

### Session 20 · E0 and the editions review — done (10 Nov 2026)
E0 merged (PR #93; first release `v8.33.68`). Planning E2 led to D-143 (English names, the full book as the edition `full`, an explicit page contract, one `build/` root, `make` as the only entry point), recorded in a docs-only PR. Verified in this session with TeX Live 2023: the edition passed by `-usepretex`, the `.aux` subfolders the build must create in the output directory, and the full book byte-identical without `\setcounter{page}{8}`.

### Session 20a · R15 — done (10 Nov 2026)
R15 merged (PR #95): English names for the folders and front-matter files (D-143).

### Session 20b · E2, E3, E8 — done (11 Nov 2026)
E2 (PR #96, D-144): every book is an edition (`data/book.toml`, `editions/<name>/edition.toml`), generated into and built under `build/editions/<name>/` by `make [EDITION=<name>]`; the page check reads the main `.aux`; CI builds base and head in the same TeX Live action. E3 (PR #97, D-145): `\seealso` to a song outside the edition is left out, a link to a missing target fails the build, the lints validate every edition, `make check [EDITION=<name>]`. E8 (PR #98): front matter in Czech book order, the songs from page 9. All three verified with a throwaway edition (not committed); the full book unchanged by E2 and E3, every song exactly one page later after E8.

### Any session · R16 — done in session 21 (11 Nov 2026)
The song count changed after R15 (version 8.38); the traces of the old folder and of the layout before editions are gone.

### Session 21 · E7, R16 — done (11 Nov 2026)
R16 merged (PR #102). E7 merged (PR #103, D-146): `editions/lidovky/` with its own cover (the photo and the caption "lidové písničky" as in the old book) and the subtitle "lidové písničky". The planning of the rest of the session led to D-147 (the order below).

### Session 21a · E5 — done (11 Nov 2026)
E5 merged (PR #106, D-149): the CI finds, builds, checks and releases every edition by `edition_names()`; first release with it `v8.38.5`.

### Session 21b · E6 — done (11 Nov 2026)
E6 (PRs f-hluchnik/zpevnik-web#3, merged first, and f-hluchnik/zpevnik#PRNUM, D-150): the website downloads the PDFs from the release `v<version.txt>`, the buttons come from `EDITION_DOWNLOADS` in its `build.py`, the songbook CI writes only `version.txt`. The owner archives `zpevnik-lidovky` himself once the page is live.

### Session 21c · P0 · Sonnet · `zpevnik`
- **Needs:** the print edition (`editions/<name>/edition.toml`, prepared by the owner by hand, D-148); E5 and E6 first (owner, 11 Nov 2026).
- **Read:** DECISIONS D-122, D-129, D-139, D-142, D-143, D-147 · PLAN WP9 · TICKETS P0, P1.
- **Notes:** A report, not a change of the book: zero diff for the screen PDF, nothing merged except what the owner picks. Propose how the A5 geometry reaches the document (a parameter, no copy of `zpevnik.tex`) in the PR before coding. The owner answers P1 after reading the report.

### Session 22 · P3 · Sonnet · `zpevnik`
- **Needs:** P0, and P1 answered by the owner (page size, binding, deadline, full book or subset, the scaled PDF checked on paper); E4 only if a subset.
- **Read:** DECISIONS D-122, D-129, D-139, D-142, D-143 (format, page numbering) and the P1 entry · PLAN WP9 · README (one page per song).
- **Notes:** The screen PDF must not change (zero diff). The scaled print is the default; the geometry trial was P0's report and is merged only if the owner picks it. P4 is not here: it needs the final content.

### Session 22a · A1 · Sonnet · `zpevnik`
- **Needs:** P3 (the README then covers editions and print).
- **Read:** the README and `docs/` as the reader sees them · TICKETS A1.
- **Notes:** Report first, change after the owner's OK. Run every command the README gives.

### Session 22b · A2 · Sonnet · `zpevnik`
- **Needs:** nothing, but after P3 so that the tests it adds are included.
- **Read:** TICKETS A2 · `tools/test_*.py` · DECISIONS for the decisions the tests protect.
- **Notes:** Report first (a table, module by module, with evidence), removals only after the owner's OK. `coverage` may be installed for the audit, not added to the repository.

### Session 22c · A3 · Sonnet · `zpevnik`
- **Needs:** E5 (every edition builds in CI) and P3.
- **Read:** TICKETS A3 · the CI workflow · the backlog item *CI speed*.
- **Notes:** Measure before proposing; the PDF diff must stay at zero for every accepted change; one PR per accepted proposal.

### Any session · K2 · Sonnet · `zpevnik`
- **Needs:** nothing. Small; do it when convenient (it removes three warnings, no more).

### Any session · P4 · Sonnet · `zpevnik`
- **Needs:** P3, and the final content: the owner's new songs and K1 (D-147).
- **Read:** TICKETS P4 · the P1 entry.
- **Notes:** P4 ends with the owner's sign-off, not with the agent's.

### Session 23 · J1 · **strong model** · `zpevnik`
- **Needs:** Q4, Q5, J0 (done, D-135, D-136).
- **Read:** DECISIONS D-001, D-007, D-108, D-131, D-135, D-136 · PLAN WP5.
- **Notes:** J1: there is no prototype; this starts from scratch. Before coding, propose the parser structure and the in-memory model and wait for the owner's OK: J2/J3 turn that model into the contract with the website. D-135 lists how the converter treats every special case (math symbols, `multicols`, `\echo`, `\ntimes`, ...); D-136 the scores (`\score{name}`, SVGs in `generated/scores/`).

### Session 24 · J2, J3 · **strong model** · `zpevnik`
- **Needs:** J1.
- **Read:** DECISIONS D-001, D-110 · PLAN WP5 (Design, Contents).
- **Notes:** Propose the JSON shape for two representative songs (one with chord-only rows and `\cue`, one with footnotes and scores) and get the owner's OK before writing the schema.

### Session 25 · J4, L2 · Sonnet · `zpevnik`
- **Needs:** J3, E2 (L1 is done, D-141).
- **Read:** DECISIONS D-006, D-008, D-110, D-125, D-136 · PLAN WP5 (Steps), WP7.
- **Notes:** J4 attaches `songs.json` (and keeps the PDF) as release assets on pushes to master only. J4 also attaches the score SVGs (`build/scores/*.svg`, one zip; J5 was done with J0, D-136). L2 reuses E2's song filter.

### Session 26 · W1, W2 · Sonnet · `zpevnik-web`
- **Needs:** J4 released at least once.
- **Read:** DECISIONS D-103, D-110, D-123 · PLAN WP6 · zpevnik-web README.
- **Notes:** The PDFs already come from the release (E6); W1 adds `songs.json`. The download page at `/` must look and work as before. The songbook lives under `/zpevnik/`. W2 implements the chord rule in CSS and must read well without JavaScript. The owner had an uncommitted change in `zpevnik-web/templates/base.html` (6 Nov 2026): ask before touching that file.

### Session 27 · W3, W4, W5, W6 · Sonnet · `zpevnik-web`
- **Needs:** W2, L1.
- **Read:** DECISIONS D-006, D-103, D-107 · PLAN WP6.
- **Notes:** The index order must match the PDF exactly (it comes from `songs.json`, never re-sorted in the web build). The search index needs no library unless it is tiny.

### Session 28 · W7 · Sonnet · `zpevnik-web`
- **Needs:** W3–W6.
- **Read:** TICKETS W7 · zpevnik-web README.
- **Notes:** Screenshots at phone size; check that every internal link resolves; update the README. Then the refactoring story for the website (HISTORY.md, *Notes for the website article*), if the owner wants it now.

---

## Owner decisions that gate sessions

| Decision | Where | Blocks |
|---|---|---|
| E4 songs for `zpevnik-lite` | TICKETS E4 | after the printed edition (D-147): nothing now |
| P1 print requirements and deadline, after P0's report | TICKETS P1 | session 22 |
| The owner's new songs (about ten) and K1 chords | TICKETS K1 | P4 |
