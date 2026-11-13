# Zpěvník – tickets

Each ticket is one pull request. Background: [PLAN.md](PLAN.md). Agreed decisions: [DECISIONS.md](DECISIONS.md); a ticket never overrides an agreed decision. This file lists only what is left. What is done: [HISTORY.md](HISTORY.md), and the full text of every finished ticket in [archive/](archive/README.md). Tickets are grouped into sessions with ready-made prompts in [SESSIONS.md](SESSIONS.md).

Goal: the PDF and an online HTML songbook, both built from the same LaTeX files (D-100). The refactoring, the editions, the converter, the legal hygiene, the online songbook and the overview for the article are done (HISTORY.md, OVERVIEW.md). **What is left is mostly the owner's own work** (new songs, splitting two songs, the printer, the choice of favourites); the agent's part is the print proof (P4) and small helpers on request. Then the songbook is done: the features that are not planned, and why, are in D-175 (correct and simple, not every feature).

Tags: **[agent]** an AI agent can do it · **[you]** needs your decision or review · **⚠** touches many song files, so never run two ⚠ tickets in parallel and merge each before the next · **[strong model]** needs design judgement beyond following the steps: run it with the strongest available model, or have one review the result before merge · size S/M/L.

## Rules for every ticket

1. **Scope.** Change only what the ticket says. If counts, names or files do not match the description, stop and report; do not improvise. Counts in tickets are snapshots: re-derive them with grep or the tools.
2. **Verification.** Every PR gets the song-by-song PDF diff against its base commit (CI, D-105, D-106). The PR description contains *Expected differences* (default: none) and *Actual differences*. A mismatch means the ticket is not done.
3. **Content is untouchable.** Lyrics, chords and Czech text stay as they are unless a ticket says otherwise.
4. **Tools** (`tools/`) use Python ≥ 3.11 and the standard library only. The tests and `tools/validate_songs_json.py` (the check of the whole `songs.json`, D-166) may also use the pinned packages of `requirements-dev.txt` (only `jsonschema`, D-165).
5. Commit messages, PR descriptions and code comments in English (D-131); the README is Czech.
6. **Git.** One branch and one PR per ticket, in the repository the ticket names (`zpevnik` unless it says `zpevnik-web`). Commit, push the ticket branch and open the PR without asking; never merge, force-push or push to the default branch without the owner's explicit OK.
7. **Status and docs.** The ticket's PR also updates the docs: the ticket leaves this file when it is done: its row and text go to `archive/<phase>/TICKETS.md`, marked `done` (the merge makes it true), HISTORY.md at the end of a phase, DECISIONS.md if a decision was made. A change of plan without a ticket gets its own docs-only PR.

## Working environment (verified 3–6 Nov 2026)

- **Planning docs** live in `docs/` of the `zpevnik` repository (D-134), so a session needs only the repository: no link to the owner's computer. They change through pull requests like the code. Large binary files (review PDFs, page images) are not committed: attach them to the PR, or the owner keeps them locally (the older ones are in `songbook-project/docs/archive/` on his computer, see archive/README.md).
- **Building and testing:** use the cloud workspace.
  - Run `apt-get update`, then `apt-get install -y texlive-lang-czechslovak texlive-latex-extra texlive-fonts-extra texlive-music poppler-utils latexmk` in each new session (without the update the packages had no install candidate). Python there is 3.13. The score export (D-136) needs more, verified on 11 Nov 2026: `apt-get install -y librsvg2-bin fonts-cmu xvfb`, and MuseScore as the AppImage named by `MUSESCORE_URL` in the CI workflow (download, `--appimage-extract`, `MSCORE=<dir>/squashfs-root/AppRun`); then `xvfb-run -a make …`. From scratch the full book takes ≈18 s for the scores and ≈20 s for LaTeX; both are skipped when up to date.
  - That TeX Live is 2023 (pdfTeX 1.40.25) like CI, but a local build is only compared with another local build (base vs head). CI is the reference.
- **The owner's computer** (Linux VM shell, if a session is linked to it) has TeX Live 2022 *without* Czech babel and Python 3.10, so neither the book nor the tools run there. It is needed only for the owner's local files, e.g. uncommitted changes in `zpevnik-web`.
- **Cloud session tooling:** `gh pr create` does not work there (GraphQL is blocked); open PRs with `gh api repos/f-hluchnik/zpevnik/pulls -f title=… -f head=<branch> -f base=master -F body=@file`. The clone is shallow: after the first push set the upstream by hand (`git config branch.<b>.remote origin` and `branch.<b>.merge refs/heads/<b>`). CI job logs contain the PDF diff summary (`gh api repos/f-hluchnik/zpevnik/actions/jobs/<id>/logs`).
- **Repositories:** `f-hluchnik/zpevnik` (default branch `master`) and `f-hluchnik/zpevnik-web` (`main`). Both are public: anonymous clones work; pushing and PRs need the repo attached with push access.

## Status

`todo` · `in progress` · `in review` (PR open) · `done` · `blocked` (reason in notes) · `cancelled` (reason in notes) · `optional` (the owner decided it need not be done).

Everything not in the table is `done` or `cancelled` (HISTORY.md, archive/). **The table is the whole list of what is left, in the order of work (D-132, D-147).**

| Step | Ticket | Who acts | Status | Waiting for, and what comes next |
|---|---|---|---|---|
| 1 | The owner's new songs (about ten) | owner | in progress | content work, not a ticket (D-147); everything after it works on the final content |
| 2 | H7 | owner writes; the agent checks on request | todo | the owner chooses the songs to split and their ids and titles; `cernymuz` is decided (D-177). It closes phase 13 (Z1) |
| 3 | P1 | owner and the printer | in progress | the printer's answers: deadline, colour, spine shift, copies, PDF requirements (`docs/p0-print-report.md`, section 4, D-157); the agent then records them as a decision |
| 4 | P4 | agent, then the owner signs off | todo | steps 1 to 3 (and H7 if it is to be in the printed book); the owner reads a proof; the commit and version that went to the printer are recorded here |
| 5 | E4 | owner picks, agent writes `edition.toml` | todo | after the printed edition (D-147); nothing waits for it |

H7 changes the PDF, so it goes before P4 if the printed book is to have it; the owner decides by the print deadline (P1). Optional, after H7, if the owner wants it enforced: a lint that a song whose verse numbers start again has a `\partrule` there (D-178).

---

# Phase 10 – Editions (song subsets, D-121)

The editions are built and released (HISTORY.md); one ticket is left.

### E4 · Choose the songs for `zpevnik-lite` — [you] + [agent] · S · needs E2 · **after the printed edition (D-147)**
The agent adds a small helper that lists song ids with title and artist (filter by artist) to pick from. The owner picks the songs; the agent writes `editions/lite/edition.toml`. **Expected differences:** none for the full book. Owner, 11 Nov 2026: later, after the print edition is done; nothing waits for it (E5 finds editions by itself, E6 shows what exists).

---

# Phase 3 – Print (D-122)

The printed edition is important and has a deadline. The screen PDF must never change because of it (zero diff). The report, the cancelled licensing check and the print build are done (HISTORY.md, archive/phase-3-print/).

### P1 · Print requirements — [you] · S
Decide and write down (the agent records it as a DECISIONS entry): the **deadline**; page size and binding (A4, A5, …; ring binding needs no gutter); whether the scaled screen PDF reads well on paper (D-142: print A4 pages "2 per sheet" to see A5 size); the binding offset for two-sided printing; paper and colour (black and white or colour); the printer's technical requirements (PDF version or PDF/X, embedded fonts, bleed, crop marks); whether links stay visible; the number of copies; **full songbook or a subset** (answered in D-148: the print book is its own edition, selected by hand by the owner; the rest of P1 is open). Answered after reading P0's report. The owner's new songs do not block P1 or P3: content changes need only a rebuild. Status of the answers: D-157.

### P4 · Print proof check — [agent] + [you] · S · needs P3 and the final content
Done on the final content, after the owner's new songs (D-147; K1 is done); until then P3's output is a draft. Preflight the PDF: fonts embedded (`pdffonts`), page size and page count, colour space against the printer's requirement (report, convert only if asked), crops of the first page, a middle page, a two-column song and the contents at 100%. The owner reads a proof and signs off. Record the commit and version that went to the printer in the Status table.

---

# Phase 13 – Finishing (D-175)

Q7 (one reader of the songs), J6 (remarks, D-177), V10 (parts, D-178) and Z2 (the overview, `docs/OVERVIEW.md`) are done (archive/phase-13-finishing/). H7 is the last ticket before the songbook is done. What is not planned, and why: D-175. H7 is ⚠ (song files).

### H7 · Bilingual songs as two songs — [you] + [agent] · S · ⚠
**The problem** (owner, `jednoubudemdal`). The Czech version and the English original ("We shall overcome") share one song, and the verse numbers start again; by the logic of the songbook they are two songs, each with its own title, its line in the contents and in the search, linked by `\seealso`.
**To decide first (owner):** which songs are really two versions of one song, and the new ids and titles. The candidates are the songs whose verse numbers start again: `cernymuz`, `ejhorahora`, `idzepostaridze`, `jedesohajzvidna`, `jednoubudemdal`, `kolenasejchalupecky`, `rezrezrez` and `vodavodenka`. A song that stays one song has `\partrule` between its parts (D-178; `cernymuz` and `jednoubudemdal` are the two without one). **Already decided (owner, 13 Nov 2026, D-177):** `cernymuz` "verze Waldemara Matušky" is a second song: it becomes `cernymuzmatuska`, linked with `\seealso`, and its `\vers{\emph{verze …}}` line goes (the title says it).
**Expected differences:** the songs split, one more entry in the contents and the artist index per split; the pages after them shift. **Last ticket of the phase:** its PR adds phase 13 to HISTORY.md and its line to OVERVIEW.md, and moves the rest of the phase's ticket texts to the archive (Z1).

---

# Documentation

### Z1 · Project history and helper files — [agent] · S · at the end of every phase
Done for every finished phase (HISTORY.md, docs/archive/); phases 10, 3 and 13 have tickets open, whose finished ones are archived already. At the end of each phase, in the PR of its last ticket: add the phase to HISTORY.md (what changed and why, numbers, PRs, decisions) and its line to OVERVIEW.md, move its finished ticket texts and status rows to `docs/archive/<phase>/TICKETS.md` and its text helper files next to them. Binary review files are not committed (attach them to the PRs). Exact duplicates may be deleted; everything else is moved.
