# Implementation sessions

How the remaining tickets in [TICKETS.md](TICKETS.md) are grouped into working sessions, and the prompt for each. Sessions 1–19 are done (HISTORY.md; their blocks are in archive/snapshot-2026-11-06/SESSIONS.md and archive/phase-11-code-quality/SESSIONS.md). Numbering continues from 20, in the order of work of D-132.

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

### Session 20 · E0, E2, E3 · Sonnet · `zpevnik`
- **Needs:** nothing for E0; E1 (owner decisions recorded in DECISIONS) for E2, E3.
- **Read:** DECISIONS D-102, D-107, D-119, D-121, D-132, D-133 · PLAN WP8 · `tools/generate.py`, `tools/artist_toc.py` · for E0 the CI workflow.
- **Notes:** Zero diff for the full book (S3 diff) and a byte-identical `generated/` except the new `edition.tex`. Test with a throwaway edition file that is not committed. E3: the rule for `\seealso` is the one chosen in E1. E0 first (its own PR); its only visible difference is the colophon; read the first release run on master before claiming it works (the owner merges, then checks the tag).

### Session 21 · E4, E5 · Sonnet · `zpevnik`
- **Needs:** E3 and the owner's song list for `zpevnik-lite` (E4).
- **Read:** DECISIONS D-110, D-121 · TICKETS E4, E5 · the CI workflow.
- **Notes:** Release assets only on pushes to master; do not touch `zpevnik-web` unless E1 says so. Read the first real CI run before claiming anything about it.

### Session 22 · P3, P4 · Sonnet · `zpevnik`
- **Needs:** P1 answered by the owner (page size, binding, deadline, full book or subset); E4 if a subset.
- **Read:** DECISIONS D-122, D-129 and the P1 entry · PLAN WP9 · README (one page per song).
- **Notes:** The screen PDF must not change (zero diff). Report every song that spills over a page with the print geometry and propose a fix per song; do not fix silently. P4 ends with the owner's sign-off, not with the agent's.

### Session 23 · J0, J1 · **strong model** · `zpevnik`
- **Needs:** Q4, Q5; for J0 the owner's answers per quirk (ask at the start).
- **Read:** DECISIONS D-001, D-007, D-108, D-131 · PLAN WP5.
- **Notes:** J0 first, its own PR (the `\score` command must give zero diff). J1: there is no prototype; this starts from scratch. Before coding, propose the parser structure and the in-memory model and wait for the owner's OK: J2/J3 turn that model into the contract with the website.

### Session 24 · J2, J3 · **strong model** · `zpevnik`
- **Needs:** J1.
- **Read:** DECISIONS D-001, D-110 · PLAN WP5 (Design, Contents).
- **Notes:** Propose the JSON shape for two representative songs (one with chord-only rows and `\cue`, one with footnotes and scores) and get the owner's OK before writing the schema.

### Session 25 · J4, J5, L1, L2 · Sonnet · `zpevnik`
- **Needs:** J3, E2; for J5 the missing `.mscz` files from the owner. L1 is the owner's text: draft it in Czech and English for approval.
- **Read:** DECISIONS D-006, D-008, D-110, D-125 · PLAN WP5 (Steps), WP7.
- **Notes:** J4 attaches `songs.json` (and keeps the PDF) as release assets on pushes to master only. J5: prototype the MuseScore export first and report before building on it. L2 reuses E2's song filter.

### Session 26 · W1, W2 · Sonnet · `zpevnik-web` (W1 also touches `zpevnik` CI)
- **Needs:** J4 released at least once.
- **Read:** DECISIONS D-103, D-110, D-123 · PLAN WP6 · zpevnik-web README.
- **Notes:** W1 also changes the songbook CI so it stops committing the PDF into `zpevnik-web` (D-110): a separate PR in `zpevnik`. The download page at `/` must look and work as before. The songbook lives under `/zpevnik/`. W2 implements the chord rule in CSS and must read well without JavaScript. The owner had an uncommitted change in `zpevnik-web/templates/base.html` (6 Nov 2026): ask before touching that file.

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
| Q5 items 2–4 (zapomnetliva dialogue, ahorsewithnoname note, song footnotes) | TICKETS Q5 | session 19 |
| E1 editions design | TICKETS E1 | session 20 (E2, E3) |
| J0 song quirks | TICKETS J0 | session 23 |
| E4 songs for `zpevnik-lite` | TICKETS E4 | session 21 |
| P1 print requirements and deadline | TICKETS P1 | session 22 |
| P2 licensing check before selling | TICKETS P2 | selling the print (not the build) |
| Missing `.mscz` files | TICKETS J5 | session 25 (J5) |
| L1 notice text | TICKETS L1 | sessions 25, 27 |
| K1 chords for the 8 songs without them | TICKETS K1 | nothing (content) |
