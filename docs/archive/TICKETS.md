# Zpěvník – tickets

Each ticket is one pull request. Background: [PLAN.md](PLAN.md). Agreed decisions: [DECISIONS.md](DECISIONS.md); a ticket never overrides an agreed decision. This file lists only what is left. What is done: [HISTORY.md](HISTORY.md), and the full text of every finished ticket in [archive/](README.md). Tickets are grouped into sessions with ready-made prompts in [SESSIONS.md](SESSIONS.md).

Goal: the PDF and an online HTML songbook, both built from the same LaTeX files (D-100). The refactoring, the editions, the converter, the legal hygiene, the online songbook and the overview for the article are done (HISTORY.md, OVERVIEW.md). **What is left is mostly the owner's own work** (new songs, the printer); the agent's part is the print proof (P4) and small helpers on request. E4 and H7 were dropped (D-189). Then the songbook is done: the features that are not planned, and why, are in D-175 (correct and simple, not every feature).

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
- **The owner's computer** (Linux VM shell, if a session is linked to it) has TeX Live 2022 *without* Czech babel and Python 3.10, so neither the book nor the tools run there as they are. It is needed for the owner's local files, e.g. uncommitted changes in `zpevnik-web`. Verified on 19 Nov 2026 (D-188): with the owner's grant of his Mac's `/usr/local/texlive/2026`, that shell builds the book with the Mac's TeX Live tree and its own pdfTeX (a `pdflatex.fmt` made with `pdftex -ini` and `TEXMFDIST`, `TEXMFSYSVAR`, `TEXMFSYSCONFIG` pointing into the tree, `TEXFORMATS` at the format), Python 3.12 from `uv python install 3.12`, and the score images copied from the owner's `build/scores/` (no MuseScore there). It has Ghostscript and poppler; `rsvg-convert` and `git` over SSH it does not have, so push from a cloud clone.
- **Cloud session tooling:** `gh pr create` does not work there (GraphQL is blocked); open PRs with `gh api repos/f-hluchnik/zpevnik/pulls -f title=… -f head=<branch> -f base=master -F body=@file`. The clone is shallow: after the first push set the upstream by hand (`git config branch.<b>.remote origin` and `branch.<b>.merge refs/heads/<b>`). CI job logs contain the PDF diff summary (`gh api repos/f-hluchnik/zpevnik/actions/jobs/<id>/logs`).
- **Repositories:** `f-hluchnik/zpevnik` (default branch `master`) and `f-hluchnik/zpevnik-web` (`main`). Both are public: anonymous clones work; pushing and PRs need the repo attached with push access.

## Status

`todo` · `in progress` · `in review` (PR open) · `done` · `blocked` (reason in notes) · `cancelled` (reason in notes) · `optional` (the owner decided it need not be done).

Everything not in the table is `done` or `cancelled` (HISTORY.md, archive/). **The table is the whole list of what is left, in the order of work (D-132, D-147).**

| Step | Ticket | Who acts | Status | Waiting for, and what comes next |
|---|---|---|---|---|
| 1 | The owner's new songs (about ten) | owner | in progress | content work, not a ticket (D-147); everything after it works on the final content |
| 2 | P5 | owner, printer | in progress | the cover is ready (D-192, D-193): CMYK, 3 mm bleed, the book's crop marks; the owner sends the book and the cover to the printer; then a test print checks the colours and the QR code |
| 3 | P4 | agent, then the owner signs off | todo | step 1 (the owner adds two more songs); the PDF is `make EDITION=skaut-kravare FORMAT=print CHORDS=black SIZE=A5` (D-188); the owner reads a proof; the commit and version that went to the printer are recorded here. Still the owner's: the deadline, the paper, the number of copies |
| 4 | F1 | agent, if the owner wants it | optional | Chrome and Gmail show only "Skaut" of the cursive title (diagnosed, see F1); the owner decided to leave it for now (19 Nov 2026) |

---

# Phase 3 – Print (D-122)

The printed edition is important and has a deadline. The screen PDF must never change because of it (zero diff). The report, the cancelled licensing check, the print build and the printer's requirements (P1, D-188) are done (HISTORY.md, archive/phase-3-print/).

### P5 · The cover of skaut-kravare — [you] + [agent] · S · needs the printer's check
Done: the source (D-192), the back, the front from the 1200 dpi scan, CMYK, the book's crop marks on a 15 mm room, no subtitle, a page for notes (D-193, `editions/skaut-kravare/print-cover/README.md`). Left: the printer checks the book and the cover; a test print, its colours and the QR code scanned on phones.

### P4 · Print proof check — [agent] + [you] · S · needs P3 and the final content
Done on the final content, after the owner's new songs (D-147; K1 is done); until then P3's output is a draft. Build `make EDITION=skaut-kravare FORMAT=print CHORDS=black SIZE=A5` on the owner's Mac (it checks the trim box, the margins and the one ink itself, D-188). Preflight the PDF: fonts embedded (`pdffonts`), page size and page count, crops of the first page, a middle page, a score, a two-column song and the contents at 100%. Tell the printer the final page count. The owner reads a proof and signs off. Record the commit and version that went to the printer in the Status table. Phase 3 ends with P4: its PR adds the phase to HISTORY.md and finishes its line in OVERVIEW.md (Z1).

### F1 · The width table of the cursive title font — [you] + [agent] · S
The title page sets its title in the French Cursive font (`\fontfamily{frc}`, `shared-pages/titlepage.tex`, and the cover of `lidovky`). The font joins letters with small connecting glyphs; two of them, codes 10 and 11 of `frcr14`, have a negative width (−0.025 em). **Diagnosed 19 Nov 2026:** PDFium (the PDF engine of Chrome, Gmail's preview and other Google viewers) stops drawing a text run at a glyph with a negative width, so the title shows as "Skaut" (the first such glyph follows the *t*) and the rest of the line is missing; reproduced with `pypdfium2` on the release PDF. In copies of the PDF where the two widths are 0, or where the glyph is left out, PDFium draws the whole title. pdfTeX also writes the two widths as `-25.-2`, not a valid PDF number, but that is a separate pdfTeX bug and not the cause (repairing the number alone changes nothing). The proposed fix: a corrected copy of the font's metrics in the repository, made by a documented script from the TeX Live font, with the two glyphs at width 0 and the −0.025 em moved into the kerning, so TeX places every glyph where it does today; and reports to the frcursive maintainer and to PDFium. Alternatives: another title font; or leave it. **The owner's call** (19 Nov 2026: leave it, thinking it only affects Gmail; it affects Chrome's PDF viewer too). Do not patch PDFs after the build. **Expected differences:** none in the rendered pages.

---

# Documentation

### Z1 · Project history and helper files — [agent] · S · at the end of every phase
Done for every finished phase (HISTORY.md, docs/archive/); phase 3 has a ticket open (P4), whose finished ones are archived already. At the end of each phase, in the PR of its last ticket: add the phase to HISTORY.md (what changed and why, numbers, PRs, decisions) and its line to OVERVIEW.md, move its finished ticket texts and status rows to `docs/archive/<phase>/TICKETS.md` and its text helper files next to them. Binary review files are not committed (attach them to the PRs). Exact duplicates may be deleted; everything else is moved.
