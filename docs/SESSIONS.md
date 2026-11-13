# Implementation sessions

How the remaining tickets in [TICKETS.md](TICKETS.md) are grouped into working sessions, and the prompt for each. This file lists only the sessions still to run. Sessions 1–27 and 29 are done (HISTORY.md; their blocks are in archive/snapshot-2026-11-06/SESSIONS.md, archive/phase-11-code-quality/SESSIONS.md and archive/sessions-20-27/SESSIONS.md, which also holds session 29). The next free number is 32; a letter after a number means "in this slot, after it".

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

### Any session · P4 · Sonnet · `zpevnik`
- **Needs:** P3, and the final content: the owner's new songs (D-147; K1 is done).
- **Read:** TICKETS P4 · the P1 entry.
- **Notes:** P4 ends with the owner's sign-off, not with the agent's.

### Session 28 · W6a · strongest model · `zpevnik-web` (+ a docs PR in `zpevnik`)
- **Needs:** nothing; the option is chosen (D-176). Running on 13 Nov 2026 in the session that made the choice.
- **Read:** TICKETS W6a · D-123 (the chord rule) · D-176 · zpevnik-web README (*The check of the built site*).
- **Notes:** screenshots at 390 px and with the largest font; measure again what D-176 lists; run `python check_site.py` and compare with the base build. The ticket leaves TICKETS.md in a docs PR in `zpevnik` after the web PR is merged.

### Session 30 · J6 · Sonnet · `zpevnik`, then `zpevnik-web`
- **Needs:** the owner's answer on the 6 places (TICKETS J6); show him the 6 places first if he has not answered.
- **Read:** TICKETS J6 · D-128, D-165 (the schema rules), D-170 (the search).
- **Notes:** two PRs: `zpevnik` (command, converter, schema, release) first; `zpevnik-web` after a release carries it.

### Session 31 · H7, then V10 · strongest model · `zpevnik`, then `zpevnik-web` for V10
- **Needs:** the owner's answers for H7, then for V10 (TICKETS); start by showing him pages of the candidate songs.
- **Read:** TICKETS H7, V10 · D-108, D-124, D-128.
- **Notes:** ⚠ both: H7 merged before V10 starts.

### Any session · Z2 · Sonnet · `zpevnik`
- **Needs:** nothing; best after the other phase-13 tickets, so the overview is complete (otherwise the later PRs add their lines).
- **Read:** TICKETS Z2 · HISTORY.md · DECISIONS.md headings · WALKTHROUGH.md.
- **Notes:** docs only, no diff of the book.

---

## Owner decisions that gate sessions

| Decision | Where | Blocks |
|---|---|---|
| E4 songs for `zpevnik-lite` | TICKETS E4 | after the printed edition (D-147): nothing now |
| J6 which of the 6 places are remarks | TICKETS J6 | J6 |
| H7 which songs are split, their ids and titles | TICKETS H7 | H7 |
| V10 the form of songs in parts and of tight verses | TICKETS V10 | V10 |
| J6, H7, V10 in the printed book or after it | TICKETS overview | the order of J6, H7, V10 and P4 |
| P1 print requirements and deadline (the printer's answers, D-157) | TICKETS P1 | P4 |
| The owner's new songs (about ten), content work | D-147 | P4 |
