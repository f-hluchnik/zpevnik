# Implementation sessions

How the remaining tickets in [TICKETS.md](TICKETS.md) are grouped into working sessions, and the prompt for each. This file lists only the sessions still to run. Sessions 1–31 are done (HISTORY.md; their blocks are in archive/snapshot-2026-11-06/SESSIONS.md, archive/phase-11-code-quality/SESSIONS.md and archive/sessions-20-27/SESSIONS.md, which also holds sessions 28 to 31). The next free number is 33; a letter after a number means "in this slot, after it".

**To start a session**, open a Claude Code session with the `f-hluchnik/zpevnik` repository (from any device; the desktop app with the `songbook-project` folder linked works too, but is needed only for the owner's local files), choose the model listed for it, and paste the one-line prompt, e.g. `Run session 20 from docs/SESSIONS.md.`

**Why groups, not one session per ticket:** every new session pays a fixed cost (reading CLAUDE.md and the docs, installing TeX, cloning), while a long session re-sends its whole history on every turn. A group of related tickets that share context, ending at a merge, is the cheapest unit. Don't continue into the next group in the same session.

---

## Common rules (every session)

1. **Read only:** `CLAUDE.md`; this file's *Common rules* and your session's block; in `TICKETS.md` the sections *Rules for every ticket*, *Working environment*, *Status* and your session's tickets; and the DECISIONS / PLAN sections your block lists. Don't read whole files you don't need.
2. **Check prerequisites:** every ticket your block lists under *Needs* must be done: the Status table lists only what is left, so a ticket that is in neither the table nor TICKETS.md is done (its text is in archive/). If one isn't, or an owner decision it needs is missing, stop and say so.
3. **Setup:** work in the cloud workspace: attach the repo(s) in scope with push access (always `zpevnik`, which holds these docs), clone them, check out the latest default branch, read the docs from there, and install the TeX packages listed under *Working environment*. Confirm that the base builds before changing anything. If the session is linked to the owner's computer, check the Git state of its working copies too, read-only.
4. **Per ticket:** give a plan of at most 5 lines plus anything in the ticket that doesn't match reality. Wait only if something doesn't match or a decision is needed. One branch and one PR per ticket; don't stack branches.
5. **Git:** when a ticket is ready, review your own diff (CLAUDE.md, *After implementation*), commit it on its own branch, push the branch and open the PR without asking (the owner reviews in the PR). Never merge, force-push, or push to the default branch. After opening a PR, stop until the owner has merged it, then continue with the next ticket of the session.
6. **Verification:** verify locally what you can, then in the PR's CI run. Put the diff report in the PR description as *Expected differences* / *Actual differences*. Never claim CI behaviour you haven't seen in an actual run.
7. **Token hygiene:** keep command output small (`grep -c`, `head`, summaries); don't re-read files you already have; don't paste whole diffs of song files into the conversation.
8. **End of each ticket:** in the ticket's PR (or the docs PR that goes with it), move the ticket out of TICKETS.md: its row and text go to archive/<phase>/TICKETS.md, marked `done`; record any new decision in DECISIONS.md (TICKETS rule 7); and report: what changed, what was verified and how, expected vs actual differences, anything that didn't match the ticket. End of session: list what is left and the next session to run.
9. **End of a phase:** in the PR of its last ticket, add the phase to docs/HISTORY.md and move its ticket texts and text helper files to docs/archive/<phase>/ (TICKETS Z1).

---

## Sessions

**What is left, in the order of work** (the same order as the Status table in TICKETS.md; the agent's sessions are only 2 and 4):

| Step | What | Who | Session |
|---|---|---|---|
| 1 | About ten new songs | owner | none: content work (D-147) |
| 2 | H7: split the bilingual songs (and `cernymuz` → `cernymuzmatuska`) | owner writes, the agent checks on request | Session 32 |
| 3 | The printer: deadline, colour, spine shift, copies, PDF requirements (P1) | owner | none; the owner brings the answers, the agent records them in a decision |
| 4 | P4: proof check of the print PDF, then the owner signs off | agent, then owner | P4 session |
| 5 | E4: the songs of `zpevnik-lite` | owner picks, the agent writes the edition | E4 session, after the print (D-147) |

When the owner says "the songs are written" (steps 1 and 2) and "the printer answered" (step 3), the agent runs the P4 session; it records P1 as a decision first. After P4 and E4 the songbook is done: what is not planned is in D-175.

### Session 32 · H7 · `zpevnik` · when the owner has chosen the songs
- **Needs:** the owner's choice of the songs to split and their ids and titles (TICKETS H7); `cernymuz` is decided (D-177). Run it when the owner has the songs ready, or let the owner write them and ask the agent only to check.
- **Read:** TICKETS H7 · D-108, D-124, D-128, D-177, D-178.
- **Notes:** ⚠ one song at a time. `cernymuz` and `jednoubudemdal` are the songs in parts that V10 left to H7 (D-178); afterwards a lint that every restart of the verse numbers has a `\partrule` is a small addition, if the owner wants it. H7 closes phase 13: its PR adds the phase to HISTORY.md and its line to OVERVIEW.md (Z1). H7 changes the PDF, so do it before P4 if the printed book is to have it.

### P4 session · Sonnet · `zpevnik` · after steps 1 to 3
- **Needs:** P3 (done), the owner's new songs (D-147), H7 if it is to be in the printed book, and the printer's answers (P1) recorded as a decision.
- **Read:** TICKETS P4 · TICKETS P1 · D-157 · `docs/p0-print-report.md`.
- **Notes:** P4 ends with the owner's sign-off, not with the agent's. It is the last ticket of phase 3: its PR adds the phase to HISTORY.md and its line to OVERVIEW.md (Z1).

### E4 session · Sonnet · `zpevnik` · after the printed edition
- **Needs:** the owner's list of the songs for `zpevnik-lite`.
- **Read:** TICKETS E4.
- **Notes:** nothing waits for it; the full book does not change. It is the last ticket of phase 10: its PR adds the phase to HISTORY.md and its line to OVERVIEW.md (Z1).

---

## Owner decisions that gate sessions

| Decision | Where | Blocks |
|---|---|---|
| The owner's new songs (about ten), content work | D-147 | P4 |
| H7: which songs are split, their ids and titles; and whether H7 is in the printed book or after it | TICKETS H7 | H7; the order of H7 and P4 |
| P1: the printer's answers and the deadline (D-157) | TICKETS P1 | P4 |
| E4: the songs for `zpevnik-lite` | TICKETS E4 | E4 (after the print) |
