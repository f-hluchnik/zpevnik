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
| 2 | P4: proof check of the print PDF, then the owner signs off (the printer's requirements are built in, D-188) | agent, then owner | P4 session |
| 3 | F1: the cursive title in Chrome and Gmail (optional: the owner left it for now) | agent, if the owner asks | F1 session |

When the owner says "the songs are written" (step 1), the agent runs the P4 session. After P4 the songbook is done: what is not planned is in D-175; E4 and H7 were dropped (D-189).

### P4 session · Sonnet · `zpevnik` · after steps 1 to 3
- **Needs:** P3 and P1 (done, D-188), the owner's new songs (D-147).
- **Read:** TICKETS P4 · D-188 · README *Tisk*.
- **Notes:** the PDF is built on the owner's Mac (`make EDITION=skaut-kravare FORMAT=print CHORDS=black SIZE=A5`), which also makes the black-ink scores with the real `rsvg-convert` for the first time. P4 ends with the owner's sign-off, not with the agent's.

### F1 session · `zpevnik` · when the owner has said what Gmail shows
- **Needs:** the owner's go-ahead (he left it for now, 19 Nov 2026). The cause is known (TICKETS F1).
- **Read:** TICKETS F1 · D-188 (*Known and left as it is*). It is the last ticket of phase 3: its PR adds the phase to HISTORY.md and its line to OVERVIEW.md (Z1).

---

## Owner decisions that gate sessions

| Decision | Where | Blocks |
|---|---|---|
| The owner's new songs (about ten), content work | D-147 | P4 |
| The print deadline, the paper and the number of copies (D-188) | the owner and the printer | sending the PDF |
