# Phase 12 tickets (done 12 Nov 2026)

The ticket texts and status rows of the audits as they were when the phase ended. Summary: [HISTORY.md](../../HISTORY.md), phase 12.

| Ticket | Status | Notes / PR |
|---|---|---|
| A1 | done | README rewritten in the order of the owner's work; no direct push to `master` (D-158): PR #117 |
| A2 | done | 8 tests dropped (252 → 244), the rest kept on evidence (D-159): PR #118 |
| A3 | done | apt hardened (PR #119) and the PDF diff compares every edition (PR #120), D-160 |

The owner wants these before the converter and the website start. Each audit reports first and changes only what the owner agrees to; each change is its own PR with zero diff for the book.

### A1 · README audit — [agent] · M · after P3 (the README then covers editions and print)
The README (Czech, about 190 lines) against reality: run every command and check every path and claim; what is stale (editions, print, `make`), duplicated in `docs/`, or in the wrong place for its reader; whether the order of sections fits how the owner works (write a song, build, publish). Report: a list of findings and the proposed structure. After the owner's OK: the rewritten README, a list of what moved or was dropped. The README stays Czech (D-131).

### A2 · Unit-test audit — [agent] · M · after P3
203 tests in 17 modules on 11 Nov 2026 (`test_lint` 38, `test_scores` 22, `test_edition` 21, `test_artist_toc` 17, `test_collation` 14, `test_songs` 13, …). The owner wants only the meaningful ones. Criteria: a test stays if it protects a decision or a failure that no other check catches (the song-by-song diff, the lints, the one-page, chord and link checks); it goes or merges if it duplicates another, pins an implementation detail (an exact TeX string, an internal name) or can't fail in practice. Evidence per module, not opinion: what it protects, which CI check also covers it, and whether the test fails when the code it targets is broken (done by hand or with `coverage` installed for the audit only, not added to the repository). Report: a table module by module (keep, merge, drop, reason). After the owner's OK: one PR with the removals, the test count before and after, and `make check` green.

### A3 · Build and CI speed audit — [agent] · M · after P3
"What takes so long, and could we optimise it?" Baseline measured on 11 Nov 2026: locally, the full book from scratch takes ≈18 s for the score export and ≈20 s for LaTeX (both ≈0.1–0.3 s when up to date); the unit tests 2 s; the lints and checks under 1 s; the PDF diff renders each book (≈7 s) and compares. In CI a pull-request run takes ≈170 s: the first TeX Live container step 96 s, of which ≈80 s is pulling the image (the same step for the base takes 15 s), then the PDF diff 13 s, installing the score tools 13 s, the score export 8 s and 7 s, the base compile 15 s. These are measurements, not conclusions. Questions to answer with measurements: how much of the 20 s of LaTeX is the 1.8 MB cover photo, TikZ, the contents and the passes; what is the cost of each edition once E5 builds all of them on every PR; what `ci/native-texlive` (an old branch) and the other attempts in the backlog (*CI speed*) taught; whether docs-only changes could skip the build; whether parallel jobs per edition pay off. Report: ranked proposals with the expected saving and the risk to identical output. After the owner's OK: each accepted proposal is its own PR, and the PDF diff must stay at zero.

**Notes from 11 Nov 2026 (a slow run; ideas to measure, not conclusions).** Run 43035250631 (PR #108, `chore/local-setup-and-quiet-build`) spent 924 s in *Install the score export tools* and then failed: `apt-get` could not resolve the Ubuntu mirrors (`Temporary failure resolving 'azure.archive.ubuntu.com'`), a DNS failure of that runner, not of the repository. The step normally takes ≈13 s; it has no time limit, and every later step was skipped. Re-running the job is the cure for that one run. Ideas, in the order I would measure them:
1. **Fail fast and retry on apt:** `timeout-minutes` on the step and `-o Acquire::Retries=3` on `apt-get`, so a mirror outage costs a minute, not 15. Cheap, changes no output.
2. **Do not depend on a live apt install on every run:** cache the packages of the score tools, or put them (and MuseScore) in a prebuilt image. Compare with option 1 before adding moving parts.
3. **The TeX Live image is pulled once per job** (the first container step 96 s, ≈80 s of it the pull; the later container steps of the same job take 15 s), so merging the three `texlive-action` steps into one saves container start-up only, probably seconds. Measure before restructuring. The pull itself is the cost: the options are in the backlog item *CI speed* and `ci/native-texlive` (pinning TeX Live 2023 is what keeps the PDF diff at zero).
4. **Cache `build/scores`** keyed on `scores/**`, `tools/scores.py` and the shared style: saves the score export (8 s, and 7 s again for the base on a PR). Small; only if the measurements say so.
