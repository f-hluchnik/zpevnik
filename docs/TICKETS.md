# Zpěvník – tickets

Each ticket is one pull request. Background: [PLAN.md](PLAN.md). Agreed decisions: [DECISIONS.md](DECISIONS.md); a ticket never overrides an agreed decision. This file lists only what is left. What is done: [HISTORY.md](HISTORY.md), and the full text of every finished ticket in [archive/](archive/README.md). Tickets are grouped into sessions with ready-made prompts in [SESSIONS.md](SESSIONS.md).

Goal: the PDF and an online HTML songbook, both built from the same LaTeX files (D-100). The refactoring, the editions, the converter, the legal hygiene and the online songbook are done (HISTORY.md). What is left is the printed edition (P1, P4), the choice of songs for `zpevnik-lite` (E4) and, optionally, the chord wrapping on the web (W6a).

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

Everything not in the table is `done` or `cancelled` (HISTORY.md, archive/).

| Ticket | Status | Notes / PR |
|---|---|---|
| E4 | todo | owner picks the songs, after the printed edition (D-147) |
| P1 | in progress | owner and printer: what is left is listed in `docs/p0-print-report.md`, section 4 and D-157 (deadline, the printer's answers, colour, spine shift, copies); does not block the audits |
| P4 | todo | owner signs off the proof, on the final content (after the owner's new songs; K1 is done) |
| W6a | optional | segments of a line wrap freely (D-123 on the web); the owner decided on 12 Nov 2026 that the release does not wait for it |

## Overview, in the order of work (D-132)

| Phase | Tickets | After it you have |
|---|---|---|
| 10 Editions | E4 | The songs of `zpevnik-lite`, a book of favourites, picked by the owner after the printed edition (D-147) |
| 3 Print | P1, P4 | The printer's requirements and the owner's decisions, then a checked proof on the final content (D-122, D-147) |
| 9 Website | W6a (optional) | Lines of the online songbook that wrap like the book's (D-123 on the web) |

The owner's new songs (about ten) are content work that runs beside these; P4 comes after them (D-147).

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

# Phase 9 – the online songbook (`zpevnik-web`)

The songbook is online at `/zpivej/` (HISTORY.md, phase 9). One optional ticket is left.

### W6a · Segments wrap freely — [strong model] · M · needs W2 · optional (owner, 12 Nov 2026)
**The problem.** On a narrow screen, or with a larger font, a line wraps strangely (the release check of W7 saw it at the default font size on a 390 px phone too): in `folsomprisonblues`, "I" stands alone and "hear the train a-coming, …" starts the next line. Cause, measured on 12 Nov 2026: a chord and all its text up to the next chord are one `inline-block` (the W2 form of the chord rule, D-123), and a browser moves such a box whole to the next line when it does not fit beside what is before it; TeX would break at any space. The PDF is not affected.
**Not the fix.** Letting only the first word be the chord's column and the text after it flow: it pads after a first word shorter than its chord, which the book does not (498 of 1,518 multi-word chord segments in 120 sampled songs).
**To decide first (a note in this ticket's PR, an owner decision if the options differ visibly), then implement.** CSS cannot say "pad only where the next chord would collide" without measuring, so every approach is a compromise. The candidates:
1. *A text clearly longer than its chord flows; a short one keeps today's unbreakable column.* The chord is zero-width over the first word, so the text is not padded; the collision guarantee stays for the short ones (11 of 1,518 sampled multi-word segments have a text narrower than the chord and its separator). A segment that ends inside a word (the hyphen) stays unbreakable. A threshold in one named constant.
2. *Measure in JavaScript* and pad where a chord would collide. The page must still read without JavaScript, so the unbreakable columns stay as the base: the wrap is not fixed without it.
3. *Leave it:* the book's rule is exact, and the reader can make the text smaller.
The first is the simplest that fixes the wrap without JavaScript; whether a threshold is acceptable is the question. Check with screenshots of `folsomprisonblues` and a few dense songs at 390 px and with the font at the largest size, and that the number of songs where a chord is closer to the next than 0.5 em does not grow (measure it in the browser, as for the sample above).

---

# Documentation

### Z1 · Project history and helper files — [agent] · S · at the end of every phase
Done for every finished phase (HISTORY.md, docs/archive/); phases 10 and 3 have a few tickets open, whose finished ones are archived already. At the end of each phase, in the PR of its last ticket: add the phase to HISTORY.md (what changed and why, numbers, PRs, decisions), move its finished ticket texts and status rows to `docs/archive/<phase>/TICKETS.md` and its text helper files next to them. Binary review files are not committed (attach them to the PRs). Exact duplicates may be deleted; everything else is moved.

---

## Backlog (not ticketed)

- Transposition (Czech B/H convention), setlists, offline use, fit-to-screen, ChordPro export.
- **Capo note versus song remark** (owner, 6 Nov 2026): `\note` belongs to the next block (right for "capo 3"); a standalone remark is written as an unnumbered `\vers{\emph{…}}`. A separate remark command would give the web version a note type; decide if the website needs it.
- **Grouping verses, tight versus loose** (owner, `ejhorahora`): short one-line verses looked better tight; a way to group verses (tight inside, normal gap between groups). Not necessary.
- **Bigger gap between groups of verses, and bilingual songs** (owner, `jednoubudemdal`): the Czech and the English version share one page; by the logic of the songbook they should be two songs. Not necessary.
- **One reader of the songs** (D-164): now that J2 is done, the generator can take the song metadata from the converter, and the regexes of `songs.py` (and `tex_text.plain_text` for titles) go.
- **Refactoring story on the website** (owner, 5 Nov 2026): notes are in HISTORY.md (*Notes for the website article*); the online songbook now exists, so the article can be written.
