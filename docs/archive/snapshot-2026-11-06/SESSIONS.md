# Implementation sessions

How the tickets in [TICKETS.md](TICKETS.md) are grouped into working sessions, and the prompt for each.

**To start a session**, open a new session from the Claude desktop app with the `songbook-project` folder linked, choose the model listed for it, and paste the one-line prompt (e.g. `Run session 2 from docs/SESSIONS.md.`). For a repeatable session, add the batch: `Run session 10b from docs/SESSIONS.md, batch 2.`

**Why groups, not one session per ticket:** every new session pays a fixed cost (reading CLAUDE.md and the docs, installing TeX, cloning), while a long session re-sends its whole history on every turn. A group of related tickets that share context, ending at a merge, is the cheapest unit. Don't continue into the next group in the same session.

---

## Common rules (every session)

1. **Read only:** `CLAUDE.md`; this file's *Common rules* and your session's block; in `TICKETS.md` the sections *Rules for every ticket*, *Working environment*, *Status* and your session's tickets; and the DECISIONS / PLAN / INVENTORY sections your block lists. Don't read whole files you don't need. INVENTORY.md is long: read only the listed sections, and re-derive current counts with grep (INVENTORY is a snapshot).
2. **Check prerequisites:** every ticket your block lists under *Needs* must be `done` in the Status table. If one isn't, or an owner decision it needs is missing, stop and say so.
3. **Setup:** check the Git state of both repos in the linked folder (read-only; never modify those working copies). Work in the cloud workspace: attach the repo(s) in scope with push access, clone them, check out the latest default branch, and install the TeX packages listed under *Working environment*. Confirm that the base builds before changing anything.
4. **Per ticket:** give a plan of at most 5 lines plus anything in the ticket that doesn't match reality. Wait only if something doesn't match or a decision is needed. One branch and one PR per ticket; don't stack branches.
5. **Git:** when a ticket is ready, commit it on its own branch, push the branch and open the PR without asking (the owner reviews in the PR). Never merge, force-push, or push to the default branch. After opening a PR, stop until the owner has merged it, then continue with the next ticket of the session.
6. **Verification:** verify locally what you can, then in the PR's CI run. From S3 on, put the diff report in the PR description as *Expected differences* / *Actual differences*. Never claim CI behaviour you haven't seen in an actual run.
7. **Token hygiene:** keep command output small (`grep -c`, `head`, summaries); don't re-read files you already have; don't paste whole diffs of song files into the conversation.
8. **End of each ticket:** update its row in the Status table (docs/TICKETS.md on the owner's computer), record any new decision in DECISIONS.md, and report: what changed, what was verified and how, expected vs actual differences, anything that didn't match the ticket. End of session: list what is left and the next session to run.
9. **End of a phase:** add the phase to docs/HISTORY.md and move its helper files to docs/archive/<phase>/ (TICKETS Z1). Never delete.

---

## Sessions

### Session 1 · S1, S2, S3 · Sonnet · `zpevnik`
- **Needs:** nothing.
- **Read:** DECISIONS D-100, D-104, D-105, D-106 · PLAN WP0. No INVENTORY.
- **Notes:** Expect 756 pages from the local TeX Live 2023 build of master. The published v8.33 PDF (757 pages, pdfTeX 1.40.29) has `illbethereforyou` on two pages; TeX Live 2023 doesn't. Per S2, allow-list it and report; don't edit the song. It is not verified that `xu-cheng/latex-action` accepts `texlive_version` (the sibling `texlive-action` does): check the `action.yml` of the version the workflow uses.

### Session 2 · R3, R4, R5, R13 · Sonnet · `zpevnik`
- **Needs:** S1 (S3 for the diff).
- **Read:** DECISIONS D-001–D-005, D-101, D-104 · PLAN WP1 (Target) · INVENTORY C4, C5.
- **Notes:** R3 must give zero diff and a compiling single-song test. The `\begin{Large}` around the songs stays in `zpevnik.tex`. R4 seeds the registry with the *current* anchors, so renames wait for R6. `filmy` is a collection; `lidove` (76 songs) is used like an artist anchor: report how you classified it. R5: nothing under `generated/` is tracked. R13: the version formula must stay *song count + 100*.

### Session 3 · R6 · Sonnet · `zpevnik` · ⚠
- **Needs:** R1 answered in INVENTORY.md, R4, S2, S3.
- **Read:** DECISIONS D-002 · INVENTORY C1, C2 (with the owner's answers).
- **Notes:** Apply only what R1 decided. The expected differences are the pages whose artist name was a typo or variant: list them before pushing.

### Session 4 · R7 · Sonnet · `zpevnik` · ⚠
- **Needs:** R5, R6.
- **Read:** DECISIONS D-002, D-003, D-005 · INVENTORY C2, C3 (answers).
- **Notes:** `\artist` must print exactly where `\interpret` / `\interpretdva` print today (`\AddToShipoutPictureFG` at 0.9 / 0.7 `\paperwidth`). Test an empty slug and an unknown slug in the single-song setup.

### Session 5 · R8 · Sonnet · `zpevnik` · ⚠
- **Needs:** R2 answered in INVENTORY.md, R3.
- **Read:** INVENTORY C6, D1, D2 (with the answers).
- **Notes:** Six song titles contain a `\footnote`; their titles must not change. The TOC is still hand-written in this ticket, so only song titles change on the pages.

### Session 6 · R9, R10 · Sonnet · `zpevnik`
- **Needs:** R8.
- **Read:** DECISIONS D-104, D-107 (all of it) · PLAN WP1.
- **Notes:** Implement D-107 exactly, with unit tests from its examples ("A Horse With No Name" before "Abych tu žil"; CH after H, also in "Change the World"; Ď sorts with D, so there is no Ď section). In R9, stop after printing the list of moved songs and wait for the owner's OK before switching the include list. R10 must reproduce the current TOC layout; the only expected differences are listed in the ticket.

### Session 7 · R11, R12 · Sonnet · `zpevnik`
- **Needs:** R7, R10.
- **Read:** DECISIONS D-002, D-004, D-104 · INVENTORY C5.
- **Notes:** R11's expected differences are the drift fixes from C5: list them. The R12 README is in Czech, in the existing style. Test it end to end by adding a throwaway song in a scratch branch (never pushed).

### Session 8 · H1, H2, H3, H4 · Sonnet · `zpevnik` · ⚠
- **Needs:** R9 (for H3). H1 can start any time.
- **Read:** PLAN WP4.
- **Notes:** H1: show each of the five fixes with its page diff and get the owner's confirmation per file. H2 must give zero diff; restore and report any song that changes. H3 uses the generated include list (no `currfile`). H4 also covers titles and anything the TOC copies.

### Session 9 · C1 · **strong model** · `zpevnik` (branch only, never merged)
- **Needs:** H4.
- **Read:** DECISIONS D-108 · PLAN WP2 · INVENTORY A1, A2, A3 (re-derive the top 10).
- **Notes:** Study how the CTAN `songs` package spaces chords (documentation via the web; it is not installed locally); don't copy its code. Deliver before/after images of the 13 songs and an honest assessment against the pass criteria. The owner then decides gate C2 (path A or B) and records it in DECISIONS.md.

### Session 10a · C3a, H5, R14 · Sonnet · `zpevnik`
- **Needs:** C2 decided (D-123). H5 and R14 need nothing.
- **Read:**
  - DECISIONS D-123 · PLAN WP2 · TICKETS C3a, H5, R14
  - docs/C1-chord-spacing.md ("How it works" only)
  - on the branch `proto/c1-chord-spacing`: `zpevnik.sty` (the chord block), `tools/strip_chord_spacing.py`, `tools/chord_gaps.py`
  - docs/C1-review-lists.md, sections 1–2 only (the owner's answers)
- **Notes:**
  - C3a must give zero diff, because every song keeps the spacing off. Show the tool's rules on three songs in a scratch branch that is never pushed, and write docs/C3-batches.md.
  - After C3a is merged, close draft PR #42 (close, never merge).
  - R14: the owner checks it on his Mac before merging.
  - Three PRs, one per ticket.

### Session 10b · C3b, one batch per session · Sonnet · `zpevnik` · ⚠ · repeatable
- **Needs:** C3a merged; the previous batch merged.
- **Read:** DECISIONS D-123 · TICKETS C3b · docs/C3-batches.md (the batch's line) · docs/C1-review-lists.md (only lines of the batch's songs).
- **Notes:**
  - Put the tool's log and the CHECK places in the PR, and the batch PDF in docs/C3-batches/.
  - The owner decides the CHECK places; never join words on a guess.
  - Note the batch number in the Status table.

### Session 11 · C4, C5 · Sonnet · `zpevnik`
- **Needs:** all C3b batches.
- **Read:** DECISIONS D-123 · PLAN WP2 · INVENTORY A4.
- **Notes:** C4: flipping the default must give zero diff; grep must find no `\nc \mm \sm \bc \autochords`; chord_gaps then fails CI on any overlap. C5 shifts text after labels by tenths of a millimetre; the owner reviews.

### Session 12 · V1 · **strong model** · `zpevnik` (no code changes)
- **Needs:** C5.
- **Read:** DECISIONS D-108 · PLAN WP3 · INVENTORY B1, B2.
- **Notes:** Write `docs/vertical-spacing.md` in the docs folder on the owner's computer. Page crops go next to it in `docs/vertical-spacing/`. The owner approves it in V2.

### Session 13 · H6 · **strong model** · `zpevnik` · ⚠
- **Needs:** nothing (C5 done).
- **Read:** TICKETS H6 · DECISIONS D-124.
- **Notes:** Target zero diff. Before replacing the hack, explain each of its side effects; if one cannot be reproduced cleanly, show the differences and wait for the owner.

### Session 14 · V3, V4, V6 · Sonnet · `zpevnik`
- **Needs:** V2 done (D-124), H6.
- **Read:** DECISIONS D-124 · TICKETS V3, V4, V6 · docs/vertical-spacing.md · docs/vertical-spacing/analysis.md section 5 (the verified definitions).
- **Notes:** V3 may change only the 6 songs listed in the ticket; the owner reviews them. V4 and V6 must give zero diff.

### Session 15 · V5, one batch per session · Sonnet · `zpevnik` · ⚠ · repeatable
- **Needs:** V4; the previous batch merged.
- **Read:** DECISIONS D-124 · TICKETS V5 · docs/vertical-spacing/occurrences.csv (only the batch's songs).
- **Notes:**
  - Alphabetical batches of about 30 songs (172 in total).
  - For each `\groupbreak` and each remaining `\vspace`, propose keep, replace or delete with the page crop, and get the owner's decision before applying.
  - Batch PDF in docs/V5-batches/; note the batch in the Status table.

### Session 16 · V8 · Sonnet · `zpevnik`
- **Needs:** all V5 batches, V6.
- **Read:** TICKETS V8 · PLAN WP3 (One page per song).
- **Notes:** Report `babickamary`, `milionar` and any other song that spills, with a proposal per song; don't tune them by hand.

### Session 17 · J1 · **strong model** · `zpevnik`
- **Needs:** R12, H4, C5, V8.
- **Read:** DECISIONS D-001, D-007, D-108 · PLAN WP5.
- **Notes:** There is no prototype; this starts from scratch. Before coding, propose the parser structure and the in-memory model and wait for the owner's OK: J2/J3 turn that model into the contract with the website.

### Session 18 · J2, J3 · **strong model** · `zpevnik`
- **Needs:** J1, S2.
- **Read:** DECISIONS D-001, D-110 · PLAN WP5 (Design, Contents).
- **Notes:** Propose the JSON shape for two representative songs (one with chords-only lines, one with footnotes and scores) and get the owner's OK before writing the schema.

### Session 19 · J4, J5, L1, L2 · Sonnet · `zpevnik`
- **Needs:** J3, R11; for J5 the missing `.mscz` files from the owner. L1 is the owner's text: draft it in Czech and English for approval.
- **Read:** DECISIONS D-006, D-008, D-110 · PLAN WP5 (Steps), WP7.
- **Notes:** J4 attaches `songs.json` (and keeps the PDF) as release assets on pushes to master only. J5: prototype the MuseScore export first and report before building on it (D-125).

### Session 20 · W1, W2 · Sonnet · `zpevnik-web` (W1 also touches `zpevnik` CI)
- **Needs:** J4 released at least once.
- **Read:** DECISIONS D-103, D-110 · PLAN WP6 · zpevnik-web README.
- **Notes:** W1 also changes the songbook CI so it stops committing the PDF into `zpevnik-web` (D-110): that is a separate PR in `zpevnik`. The download page at `/` must look and work as before. The songbook lives under `/zpevnik/`. W2 implements the chord rule from WP2 in CSS and must read well without JavaScript.

### Session 21 · W3, W4, W5, W6 · Sonnet · `zpevnik-web`
- **Needs:** W2, L1.
- **Read:** DECISIONS D-006, D-103, D-107 · PLAN WP6.
- **Notes:** The index order must match the PDF exactly (it comes from `songs.json`, never re-sorted in the web build). The search index needs no library unless it is tiny.

### Session 22 · W7 · Sonnet · `zpevnik-web`
- **Needs:** W3–W6.
- **Read:** TICKETS W7 · zpevnik-web README.
- **Notes:** Screenshots at phone size; check that every internal link resolves; update the README.

### Session 23 · E2, E3 · Sonnet · `zpevnik`
- **Needs:** E1 (owner decisions in DECISIONS). Independent of sessions 9–22; can run any time.
- **Read:** DECISIONS D-102, D-107, D-119, D-121 · PLAN WP8 · `tools/generate.py`, `tools/artist_toc.py`.
- **Notes:** Zero diff for the full book (S3 diff) and a byte-identical `generated/` except the new `edition.tex`. Test with a throwaway edition file that is not committed. E3: the rule for `\hyl` is the one chosen in E1.

### Session 24 · E4, E5 · Sonnet · `zpevnik`
- **Needs:** E3 and the owner's song list for `zpevnik-lite` (E4).
- **Read:** DECISIONS D-110, D-121 · TICKETS E4, E5 · the CI workflow.
- **Notes:** Release assets only on pushes to master; do not touch `zpevnik-web` unless E1 says so. Read the first real CI run before claiming anything about it.

### Session 25 · P3, P4 · Sonnet · `zpevnik` · print, may be pulled forward
- **Needs:** P1 answered by the owner (page size, binding, deadline, full book or subset). Soft: C5, V8; if the deadline comes first, build on the current layout and repeat after C and V.
- **Read:** DECISIONS D-122 and the P1 entry · PLAN WP9 · README (one page per song).
- **Notes:** The screen PDF must not change (zero diff). Report every song that spills over a page with the print geometry and propose a fix per song; do not fix silently. P4 ends with the owner's sign-off, not with the agent's.

### Session 26 · Z1 · Sonnet · docs only · any time, independent
- **Needs:** nothing.
- **Read:** TICKETS Z1 and the Status table · DECISIONS (headings, then the entries you need) · the helper files of the finished phases.
- **Notes:** Docs on the owner's computer only, no repository. Show the list of moves and the HISTORY.md outline before moving anything; move, never delete.

---

## Owner decisions that gate sessions

| Decision | Where | Blocks |
|---|---|---|
| R1 artist questions | INVENTORY C1–C3 | sessions 3, 4 |
| R2 title mismatches | INVENTORY D2 | session 5 |
| C2 chord-spacing gate | DECISIONS D-123 (decided 4 Nov 2026) | sessions 10a, 10b |
| V2 vertical-spacing approvals | DECISIONS D-124 (decided 5 Nov 2026) | sessions 14–16 |
| Missing `.mscz` files | TICKETS J5 | session 19 (J5) |
| K1 chords for the 8 songs without them | TICKETS K1 | nothing (content; lint warns from C4) |
| L1 notice text | TICKETS L1 | sessions 19, 21 |
| E1 editions design | TICKETS E1 | session 23 |
| E4 songs for `zpevnik-lite` | TICKETS E4 | session 24 |
| P1 print requirements and deadline | TICKETS P1 | session 25 |
| P2 licensing check before selling | TICKETS P2 | selling the print (not the build) |
