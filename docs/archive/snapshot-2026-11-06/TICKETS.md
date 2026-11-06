# Zpěvník – tickets

Work through the tickets **in this order**. Each is one pull request. Background and reasoning: [PLAN.md](PLAN.md). Exact places to fix: [INVENTORY.md](INVENTORY.md). Agreed decisions: [DECISIONS.md](DECISIONS.md); a ticket never overrides an agreed decision.

Goal: the PDF and an online HTML songbook, both built from the same LaTeX files, with the technical debt paid off before the converter and the website are built (D-100, D-108).

Tags: **[agent]** an AI agent can do it · **[you]** needs your decision or review · **⚠** touches many song files, so never run two ⚠ tickets in parallel and merge each before the next · **[strong model]** needs design judgement beyond following the steps: run it with the strongest available model, or have one review the result before merge · size S/M/L.

## Rules for every ticket

1. **Scope.** Change only what the ticket says. If counts, names or files do not match the description, stop and report; do not improvise.
2. **INVENTORY.md is a snapshot** (3 Nov 2026). After merges, counts and line numbers are stale: re-derive lists with grep or the tools, never trust line numbers.
3. **Verification.** From S1 on, every PR gets a song-by-song PDF diff against its base commit, built in the same job with the same pinned TeX Live (D-105, D-106). The PR description must contain *Expected differences* (default: none) and *Actual differences* (songs from the diff). A mismatch means the ticket is not done.
4. **Content is untouchable.** Lyrics, chords and Czech text stay as they are unless a ticket says otherwise.
5. **Tools** (`tools/`) use Python ≥ 3.11 and the standard library only.
6. Commit messages in English; PR description in English.
7. **Git.** One branch and one PR per ticket, in the repository the ticket names (`zpevnik` unless it says `zpevnik-web`). Commit, push the ticket branch and open the PR without asking; never merge, force-push or push to the default branch without the owner's explicit OK.
8. **Status.** When a ticket's state changes, update the *Status* table below in the same session (and DECISIONS.md if a decision was made).

**Prompt to give the agent:** *"You are implementing ticket `<ID>` from docs/TICKETS.md. Read CLAUDE.md, 'Rules for every ticket', 'Working environment', DECISIONS.md, PLAN.md and that ticket. Check the Git state of both repos. Do only that ticket. Finish with: what you changed, what you verified and how, expected vs actual PDF differences, anything that did not match the ticket, and the updated Status table."*

Tickets are grouped into sessions with ready-made prompts in [SESSIONS.md](SESSIONS.md).

## Working environment (verified 3 Nov 2026)

- **Planning docs** live in `songbook-project/docs/` on the owner's computer, outside both Git repositories (not versioned). A session must be linked to that computer to read and update them.
- **Building and testing:** use the cloud workspace, not the computer.
  - Its TeX Live (2023, pdfTeX 1.40.25) needs `apt-get install -y texlive-lang-czechslovak texlive-latex-extra texlive-fonts-extra poppler-utils latexmk` in each new session; run `apt-get update` first (without it the packages had no install candidate, session 8). After that, the full book compiles in ≈8 s with one `pdflatex` pass. Python there is 3.13.
  - This TeX Live is not the version pinned in CI (S1), so a local build is only comparable with another local build (base vs head). CI is the reference.
- **The owner's computer** (Linux VM shell) has TeX Live 2022 *without* Czech babel, so the book does not compile there, and Python 3.10 (no `tomllib`). Use it for reading and editing the repos only. Git commits in the connected folders need delete permission (Git removes its lock files).
- **Cloud session tooling** (session 8): run `apt-get update` before the `apt-get install` above, and add `latexmk` (`make` needs it). `gh pr create` does not work there (GraphQL is blocked); open PRs with `gh api repos/f-hluchnik/zpevnik/pulls -f title=… -f head=<branch> -f base=master -F body=@file`. The clone is shallow: after the first push set the upstream by hand (`git config branch.<b>.remote origin` and `branch.<b>.merge refs/heads/<b>`), otherwise the stop hook reports unpushed commits that are already on the remote. CI job logs contain the PDF diff summary (`gh api repos/f-hluchnik/zpevnik/actions/jobs/<id>/logs`).
- **Repositories:** `f-hluchnik/zpevnik` (default branch `master`) and `f-hluchnik/zpevnik-web` (`main`). Both are public: anonymous clones work in the cloud workspace; pushing and PRs need the repo attached with push access.

## Status

`todo` · `in progress` · `in review` (PR open) · `done` · `blocked` (reason in notes). S1–S3 and R3–R5 do not depend on the owner's decisions R1/R2, so they can start first.

| Ticket | Status | Notes / PR |
|---|---|---|
| S1 | done | PR #23 merged; first pinned the 2026 image by digest (CI verified: 757 pages, publishing skipped on PRs). Pin changed to TeX Live 2023 in S2's PR #24 (D-105 note) |
| S2 | done | PR #24 merged; CI verified: TeX Live 2023 (pdfTeX 1.40.25), 756 pages, 733 songs / 0 problems. Allow-list empty (pin switched to 2023, D-105 note) |
| S3 | done | PR #25 merged (3 Nov 2026); CI of the PR verified in session 8: success, 756 pages, 733 songs unchanged. Earlier note: PR #25 (zpevnik), branch `ci/s3-song-pdf-diff`. Check the PR's job summary: expect 733 unchanged songs, nothing else. Adding a song with a footnote renumbers later footnotes (reported as changed songs, correct) |
| R1 | done | answered in INVENTORY C1–C3 (3–4 Nov 2026); Greenhorns, Beatles and slugs for the split settled in session 3 (D-112) |
| R2 | done | answered in INVENTORY D2; three rows settled in session 5 (D-116) |
| R3 | done | PR #26 merged. Local diff: 733 songs unchanged; single-song test added (CI of the PR verified in session 8: success, 733 unchanged) |
| R4 | done | PR #27 merged. 49 entries; `lidove` classified as `collection`; validator wired into CI through `tools/lint.py` in R12. Owner wants some registry details changed: handled in R6 |
| R5 | done | PR #28 merged. `make` = generate + latexmk; `generated/` gitignored; lookups in `zpevnik.sty`. README rewritten in R12 |
| R6 | done | PR #30 merged. Locally: 5 changed songs (label typos) + TOC pages 749, 753–756, as expected. Labels "Michal Tučný"/"Greenhorns"/"J. S. Lenk" deliberately unchanged; the label overflow is fixed in R7 (D-113) |
| R7 | done | PR #31 merged (seen in the `zpevnik` master log, session 7). Earlier note: PR #31 (zpevnik), branch `refactor/r7-artist-macro`. Locally: 550 songs changed (label right-aligned, D-113; Tučný/Lenk label texts unified, D-114), 183 unchanged (`\artist{}`), TOC page 752 (Nohavica heading). Registry simplified (D-114). CI of the PR verified in session 8: success; 550 changed, 183 unchanged, as locally |
| R8 | done | PR #32 merged (seen in master 9ce185e, 4 Nov 2026). Earlier note: PR #32 (zpevnik), branch `refactor/r8-alt-titles`. Locally: 7 song titles changed as expected, 726 songs unchanged, TOC unchanged, 29 `\alttitle`, 15 `\toctitle`, 46 `\collection{filmy}` (D-116). CI of the PR verified in session 8: success; 7 changed, 726 unchanged, as locally |
| R9 | done | PR #33 merged (seen in the `zpevnik` master log, session 8). Earlier note: PR #33 (zpevnik), branch `refactor/r9-include-list`. Owner approved the 67 moves (docs/R9-moves.md); also drops `\sub` from 8 songs (D-117). Locally for the include list: 731 songs unchanged, 2 changed (footnote numbers only: ahorsewithnoname, acrosstheuniverse), 253 moved, TOC unchanged, 756 pages, check_pages 0 problems. CI of the PR verified in session 8: success; 723 unchanged, 253 moved, 10 changed (the 2 footnote-number songs plus the 8 `\sub` drops of D-117) |
| R10 | done | PR #34 merged (seen in the `zpevnik` master log, session 7). Earlier note: PR #34 (zpevnik), branch `refactor/r10-toc-letters`. Locally: 733 songs unchanged, only the 16 contents pages differ (typos fixed, D-107 order, Ď removed, `oldtimereligion` entry dropped, `mojiprvnimuze` alt entry added, 3 forced line breaks gone). `nadstademkoni` already had its entry. Artist index and sections untouched (R11). CI of the PR verified in session 8: success; 733 songs unchanged |
| R11 | done | PR #35 merged (4 Nov 2026, session 7); CI of the PR passed (3 runs, all green). Earlier note: PR #35 (zpevnik), branch `refactor/r11-artist-toc`. Locally: 727 songs unchanged, 6 changed (a second artist link added on purpose, owner decision), contents pages differ (749–757; 756 → 757 pages): two-column index "Surname, First" (D-118), sections generated from the tags, drift fixes (+2 entries; the 6 songs missing from their sections got `\artist` tags: bonsoirmademoiselleparis, hvezdanavrbe, dvebaby, huslicky, sbohemgalanecko, sirokyhluboky), D-107 order, titles as on the pages, alt-title entries in every section of their song (list in the PR). check_pages 0 problems, single-song OK. PDF diff summary read in session 8: 727 unchanged, 6 changed, 756 → 757 pages |
| R12 | done | PR #36 merged (seen in the `zpevnik` master log, session 8). Earlier note: PR #36 (zpevnik), branch `refactor/r12-lints-readme`. `tools/lint.py` (errors / warnings / info as in the ticket; threshold 3 or more) + CI step, Czech README rewritten. Locally zero diff (733 songs, 757 pages), 82 unit tests, lint 0 errors / 0 warnings. README tested end to end with a throwaway song on a scratch branch (never pushed): lint failed on the unknown slug, passed after the registry entry; `make` gave 758 pages, version 8.34, song in include list, letters, index and section. CI of the PR passed (3 min 10 s; lint step green; diff summary read in session 8: zero diff, 757 pages) |
| R13 | done | PR #29 merged (seen in the `zpevnik` master log). Locally zero diff (8.33). CI of PR #29 verified in session 8: success, 733 unchanged |
| R14 | done | Session 10a: PR #46 (zpevnik), branch `build/r14-make-song`. `make song SONG=<id>` builds one song; README section "Lokální sestavení". Verified on Linux only; the owner checks the macOS commands on his Mac. Mac check: use `make song SONG=<id>` (the owner's first try without `SONG=` printed the usage, as designed) |
| H1 | done | PR #38 merged (4 Nov 2026, session 8; the owner also edited `jaktosnamalaskobude` in the PR). Earlier note: PR #38 (zpevnik), branch `refactor/h1-source-quirks`. Owner confirmed each fix in session 8. Locally: 3 songs changed as expected (`klada` and `jaktosnamalaskobude`: whole note/aside italic; `morituritesalutant`: bare `\bridge` is now `\bridgesm{}`), 730 unchanged (`neninutno`, `noe` zero diff), 757 pages, check_pages 0 problems, lint clean, unit tests OK. CI of the PR verified in session 8: success; 3 changed, 730 unchanged |
| H2 | done | PR #39 merged (4 Nov 2026, session 8). Earlier note: PR #39 (zpevnik), branch `refactor/h2-remove-newpage`. Final `\newpage` removed from 708 songs (25 never had it), `sablona.tex` and the README (item 3 replaced by one sentence). Locally zero diff (733 songs unchanged, 757 pages, 72 and 150 dpi), check_pages 0 problems, lint clean, unit and single-song tests OK. CI of the PR verified in session 8: success; zero diff |
| H3 | done | PR #40 merged (4 Nov 2026, session 8). Earlier note: PR #40 (zpevnik), branch `refactor/h3-hyt-from-include`. `generated/include.tex` writes `\songinclude{id}`; `\song` makes the target from it (works with `\include`; no id → no target). `\hyt` removed from 733 songs, `sablona.tex`, README. `check_pages.py` reads both include forms (fallback for pdfdiff against older base builds; removable later). Locally zero diff (733 songs unchanged, 757 pages), all 2520 named destinations identical (pypdf), check_pages 0 problems, lint clean, 88 unit tests and single-song test OK. CI of the PR verified in session 8: success; zero diff |
| H4 | done | PR #41 merged (4 Nov 2026, session 8). Branch `refactor/h4-accents-utf8`. 59 `\`` and 4 `\^` accent macros (ticket said 60 + 5; the rest was a snapshot difference) in 12 songs replaced by UTF-8, incl. `Felicità` and the `\hyl` link texts; contents carry it via the generator, nothing else needed. Second commit removes the pre-H3 include fallback from `check_pages.py` (owner request). Locally zero diff (733 songs unchanged, 757 pages, contents pages unchanged), all 2520 named destinations identical, check_pages 0 problems, lint clean, unit tests OK. CI of the PR verified in session 8: success; zero diff. Open: the six songs with `\footnote{}` inside `\song{}` (TODO below H4) are untouched |
| H5 | done | Session 10a: PR #45 (zpevnik), branch `refactor/h5-review-fixes`. acrosstheuniverse footnote moved into `\song{}` (`\vspace{-7pt}` keeps one page), rosanakolejich chord added |
| H6 | done | PR #64 merged (seen in master `8a206b4`, session 14). Session 13 (5 Nov 2026): PR #64 (zpevnik), branch `refactor/h6-everypar`, base master `88b5205`. Hack removed: `\parindent` −10 mm + `indentfirst`, `\@nobreakfalse` in `\sub` (50 songs pixel-identical), `\placetextbox` without the `\hspace{22pt}` compensation (vosa x 0.5 → 0.40476). `center` now standard LaTeX (owner, D-127): idzepostaridze (2 `\ns` before the rules removed, blank line after `\end{center}`), jedesohajzvidna, kolenasejchalupecky, vosa (0.28 pt), front matter pp. 3, 5–7, contents 741–742, 749–757. Locally and in CI (run 42102337515, success) exactly these differences: 729 songs unchanged, 757 pages, check_pages 0, chord_gaps 0 overlapping, lint 0 errors / 3 warnings; single-song test and `make song` OK locally. |
| C1 | done | Session 9 (4 Nov 2026): draft PR #42, branch `proto/c1-chord-spacing`, never merged (close it after C3a). Second iteration after the owner's review: single-pass lookahead `\chord` (the `\pdfsavepos` version was dropped). Locally and in CI of the PR: 0 overlapping chord pairs (master 157), 757 pages, check_pages 0 problems, padding off = zero diff. Assessment and PDFs: docs/C1-chord-spacing.md; lists with the owner's answers: docs/C1-review-lists.md |
| C2 | done | Path A (owner, 4 Nov 2026): D-123 |
| C3a | done | Session 10a (4 Nov 2026): PR #43 merged, draft PR #42 closed. Zero diff on master (733 songs unchanged, 757 pages). Tool follow-up: PR #44 (chord lists with line breaks become `\chords` rows). See the D-123 note |
| C3b | done | Session 10a/10b (4–5 Nov 2026), run in parallel: 12 batches, 449 songs, PRs #47–#56 (batches 1–10), #57+#58 (batch 11: glued chords fixed, owner's answers for two pauses), #59+#61 (batch 12: `\chords[sep]`, option E; #60 was merged into the stacked branch by mistake, #61 put it on master). All merged and reviewed by the owner. Fixes found in review: `kralaklaun` (line breaks), `podzim` (coda row split). On master: 757 pages, 0 overlapping chords, `grep '\\(nc|mm|sm|bc)'` finds nothing, 449 songs with `\autochords`. The step 4 reports (uneven chord runs, lyrics moved) were dropped: the owner reviewed every song. See DECISIONS D-123 notes |
| C4 | done | PR #62 merged (seen in master `6f05e68`, session 12). Session 11 (5 Nov 2026): PR #62 (zpevnik), branch `refactor/c4-chord-cleanup`. Locally zero diff against master `ae6e531` (733 songs unchanged, 757 pages, 72 and 150 dpi), 0 overlapping chords, check_pages 0 problems, 103 unit tests, single-song test and `make song` OK. `\autochords` removed from 449 songs; `\nc \mm \sm \bc`, `\placepic`, the `\chord` alignment argument and the strip tool deleted (`\placetextbox` kept, `vosa.tex` uses it); `chord_gaps.py` fails on any overlap; lint: error on the old macros, warning without chords (3 songs: the score-only ones of K1, the other 5 got `\chords` in C3b); Czech README. Also deleted the helper modules only the strip tool used (see the D-123 note). CI of the PR verified in session 11: success; 733 songs unchanged, 0 changed, 757 pages, chord_gaps 0 overlapping, lint 0 errors / 3 warnings |
| K1 | todo | owner: chords for the 8 songs without them |
| C5 | done | PR #63 merged (seen in master `88b5205`, session 12). Session 11 (5 Nov 2026): PR #63 (zpevnik), branch `refactor/c5-label-width`. Owner decisions: label width 25 pt, score-image indents stay, other raw `\hspace` go. `\labelw` + `\lbl` for all label macros, `\nv`/`\hyl`/`\lsp` derived (`\nv` is `\hspace*`); hacks removed in `promeny`, `ringoffire`, `eldorado`, `herecomesthesun`, `zapomnetliva` (labels to `\lbl`); `velicenstvokat` keeps its negative `\hspace` (commented; the repeat sign wraps without it). Locally: 731 songs changed (all that use a label macro, `\nv` or `\hyl`), 2 unchanged, 757 pages, 0 overlapping chords, check_pages 0 problems, 103 unit tests, single-song test OK. Previews: docs/C5-previews.pdf. CI of the PR verified in session 11: success; 2 songs unchanged (731 changed, as locally), 757 pages, chord_gaps 0 overlapping, lint 0 errors / 3 warnings. Owner reviews the previews before merging |
| V1 | done | Session 12 (5 Nov 2026), base master `88b5205`: docs/vertical-spacing.md (one-page proposal, owner's feedback included; open: Q1 dashed lines, Q2 `\vinv`). Full analysis, crops, `occurrences.csv` and scripts in docs/vertical-spacing/. Exact replacements verified by scratch builds (zero diff at 150 dpi) |
| V2 | done | Owner, 5 Nov 2026: D-124 (dashed lines stay, `\vinv` → `\groupbreak` then per-song review, score spacing stays). Ticket plan rewritten the same day (V3 shrinkable, V5 one batch pass, V7 merged into V5) |
| V3 | done | PR #65 merged (seen in master `2b7c7d3`, session 14). Session 14 (5 Nov 2026): PR #65 (zpevnik), branch `refactor/v3-blocksep`, base master `8a206b4`. `\blocksep` = `20pt minus 20pt`, helper `\zp@blockgap` in the 11 block macros, flag `\ifzp@nogap` (reset by `\song`, set by nothing until V4). Locally and in CI (run 42104297467, success) exactly the 6 expected songs differ (`babickamary`, `illbethereforyou`, `milionar`, `promeny`, `tophatbarandgrill`, `vodavodenka`), 727 unchanged, 757 pages, check_pages 0, chord_gaps 0 overlapping, lint 0 errors / 3 warnings. Page crops of the 6 checked: no overlaps; in `babickamary` and `milionar` some blocks touch (gap 0), left to V8. |
| V4 | done | PR #66 merged (seen in master `82772ee`, session 14). Session 14 (5 Nov 2026): PR #66 (zpevnik), branch `refactor/v4-named-separators`, base master `2b7c7d3`. `\groupbreak` (91 places), `\blockrule` (59 `\lsp`), `\partrule` (2, without the leading −20 pt: H6 had removed the `\ns` before the rules; ends with `\par`), `\vers{}{…}` prints no label; `tests/spacing.tex` added (also in CI). Zero diff locally and in CI (run 42106016793, success): 733 songs unchanged, 757 pages, check_pages 0, chord_gaps 0 overlapping, lint 0 errors / 3 warnings. **Open:** the second `\vinv` in `vlese` (after verse 2) has no inner `\`, it is only a −2 mm tightening, so it stays as `\vinv`; needs the owner's decision before V8 (e.g. `\\[-2mm]` or delete). `\vinv` and `\lsp` stay defined until V8. |
| V5 | done | All merged 6 Nov 2026 (#68–#76); master `9aed4f1`: 733 songs, check_pages 0, chord_gaps 0, lint 0 errors. Follow-ups: the dashed-rule step 2 (backlog), `vlese` `\vinv` (owner), V8. Session 15 (5–6 Nov 2026), 8 PRs in zpevnik, all CI `build` green, no conflicts. Prerequisite **#74** (base master): `\note` attaches to the next block with the no-gap flag (`\noteshift` removed), fixed 20 pt gap inside `multicols`, `\songinclude` runs each song in a group. Batches on master `2162600`, alphabetical: **#68** acrosstheuniverse…dobrodruzstvisbohempanem, **#69** donebes…jestemichvilkuzpivej, **#70** jez…nadejeatouhy, **#71** nancymulligan…promeny, **#72** pterodaktylus…totenkratvctyricatompatom, **#73** totenkratvsedesatomosmom…zumzumII. **#75** (stacked on #74): babickamary, milionar, summernights (`\large`), nepijjanonepijvodu (explicit `\vspace{-35pt}` KEEP), herecomesthesun, vodavodenka (`\columnbreak`), pohadka, potopa. #74 and #68 merged (6 Nov); #75 retargeted to master; #76 (rule offsets, zero diff) is a prerequisite of the later dashed-rule step;  the batches are independent of each other. Verified on the merged combination: check_pages 733 songs 0 problems, chord_gaps 0, lint 0 errors. Before/after PDFs in `docs/V5-batches/`. Open: `vlese` (`\vinv` decision untouched), herecomesthesun gaps are tight (review), `\ns`/`\cns` now only in a comment in nepijjanonepijvodu (V8 deletes the macros) |
| V6 | in review | Session 14 (5 Nov 2026): PR #67 (zpevnik), branch `refactor/v6-named-lengths`, base master `82772ee`. `\noteshift` (−20 pt), `\subshift` (−10 mm), `\hylshift` (−15 pt), `\ruleshiftbefore` (−13 pt), `\ruleshiftafter` (−3 pt), each with a comment; `\hdashrule` dash parameters and `\groupbreak`'s −2 mm left as they are. Zero diff locally and in CI (run 42107227734, success): 733 songs unchanged, 757 pages, check_pages 0, chord_gaps 0 overlapping, lint 0 errors / 3 warnings. Waiting for the owner's merge |
| V7 | dropped | merged into V5 (D-124) |
| V8 | in review | Session 16 (6 Nov 2026), PR #77, base master `9aed4f1`: `\ns`, `\cns`, `\vnv`, `\vinv`, `\lsp` deleted, lint error for them, README section, the dashed-line step (D-128 amended) and `vlese` (owner's edit). 733 songs, pdfdiff vs master: exactly the 6 dashed-rule songs and vlese changed; check_pages 0, chord_gaps 0, lint 0 errors. Remaining `\vspace`: docs/vertical-spacing/remaining-vspace.md |
| V9 | in review | Session 16 (6 Nov 2026), PR #78 (base master): leftover non-score `\vspace` removed (see vertical-spacing/remaining-vspace.md), D-130. pdfdiff vs #77: 16 songs changed (motyl, the 9 edited, 8 others with notes; 17 vs the old baseline). check_pages 0, chord_gaps 0, lint 0 errors. `\spk` added for motyl (speaker marks backlog item done). Refactoring V1–V9 finished once #78 merges. |
| J1 | todo | strong model (parser design) |
| J2 | todo | strong model (data model = contract between repos) |
| J3 | todo | strong model (schema = contract between repos) |
| J4 | todo | |
| J5 | todo | |
| L1 | todo | |
| L2 | todo | |
| W1 | todo | |
| W2 | todo | |
| W3 | todo | |
| W4 | todo | |
| W5 | todo | |
| W6 | todo | |
| W7 | todo | |
| P1 | todo | owner: print requirements and the deadline |
| P2 | todo | owner: licensing check before selling |
| P3 | todo | |
| P4 | todo | owner signs off the proof |
| E1 | todo | owner decisions |
| E2 | todo | |
| E3 | todo | |
| E4 | todo | owner picks the songs |
| E5 | todo | |
| Z1 | todo | docs only, any time (session 26); then at the end of every phase |

## Overview

| Phase | Tickets | After it you have |
|---|---|---|
| 1 Safety net | S1–S3 | PRs build; every change is diffed; one-song-per-page is enforced |
| 2 Registry | R1–R14 | Adding a song = one file; TOC, includes, artist index, version generated |
| 3 Print | P1–P4 | Back in scope with a deadline (D-122): a print build and a checked proof |
| 4 Hygiene | H1–H6 | Cleaner song files, no visual change |
| 5 Chords | C1–C5, K1 | No manual chord spacing |
| 6 Vertical | V1–V8 | No hand-tuned vertical spacing |
| 7 Converter | J1–J5 | `songs.json` and score SVGs on every release |
| 8 Legal | L1–L2 | Notice, hide switch |
| 9 Website | W1–W7 | Online songbook |
| 10 Editions | E1–E5 | Song subsets such as `zpevnik-lite` built from the same files (D-121) |

The converter (phase 7) and the website (phase 9) start only after the cleanup phases 4–6 (D-108), so the converter is written once, against semantic macros only. Phase 8 (legal) must be done before the songs go online (W6). Phases 3 and 10 are independent of the others: phase 10 needs only phase 2 (done), and phase 3 needs phase 10 only if the printed book is a subset (P1). The print has a deadline, so phase 3 may be pulled forward; the sessions say what to repeat afterwards.

---

# Phase 1 – Safety net

### S1 · Pinned TeX Live and PR builds — [agent] · S
1. Pin the TeX Live year used by `xu-cheng/latex-action` (D-105) to the year that built the v8.33 release (its PDF says pdfTeX 1.40.29; confirm the year from that run's log), so the published layout does not change. The sibling `xu-cheng/texlive-action` documents a `texlive_version` input; verify that `latex-action` accepts the same, otherwise pin the Docker image. Confirm that the pinned build matches the v8.33 PDF (757 pages).
2. In `.github/workflows/build-and-publish.yml` add a `pull_request` trigger. Guard every publishing step (website checkout, version file, PDF copy, release, push) with `if: github.event_name == 'push'`. PRs only build.

**Done when:** a PR builds without publishing; master builds with the pinned version.

### S2 · One song per page check — [agent] · S · needs S1
1. `tools/check_pages.py` reads the per-song `pisnicky/<id>.aux` files (each `\include` already records the page counter after the song) in include order, and fails if a song takes more than one page. Songs listed in `tools/multipage-allowlist.txt` may take two. No change to the macros.
2. Run it in CI after the compile; a failure blocks the PR.

Known on 3 Nov 2026: `illbethereforyou` spills in the published v8.33 PDF (newer TeX Live) but not under TeX Live 2023. If it spills under the pinned version, do **not** change the song: allow-list it, list it in the PR, and I decide (fix or keep).
**Done when:** a deliberately two-page test song turns CI red; master is green.

### S3 · Song-by-song PDF diff — [agent] · M · needs S2
1. In PR builds, also compile the base commit (same job, same TeX Live; ≈8 s).
2. `tools/pdfdiff.py`: renders both PDFs with `pdftoppm` (low resolution, grayscale), maps pages to song ids using the `.aux` records from S2, and compares each song's page with the page-number footer excluded. Front matter and TOC pages are compared by position, with the colophon date excluded. Install poppler with `apt` in a normal runner step, not inside the LaTeX container.
3. Write to the job summary: changed, added, removed and moved songs, plus changed non-song pages. The diff only reports; it never fails the build, because some tickets expect differences.

**Done when:** a PR changing one chord reports exactly that song; a PR adding a song reports one added song and nothing else.

---

# Phase 2 – Registry and generated files

### R1 · Decide the artist questions — [you] · S
Edit INVENTORY.md in place, one answer per row: **C1** (accept each new slug or write another), **C2** (canonical name per anchor; mark intentional label differences such as Greenhorns), `trikyapovery` (split into *Triky a pověry* and *Ricchi e Poveri*; slugs?), **C3** (the two two-artist songs), the band slug rule (default: drop a leading article, so `beatles`), the section threshold (≥3 or >3), and how the 48 `filmy` songs join their collection (default: an invisible `\collection{filmy}` tag).
**Done when:** no row is unanswered.

### R2 · Decide the title mismatches — [you] · S
INVENTORY **D2**, row by row, write one of: `song` (the song's title is right, the TOC changes), `toc` (the TOC is right, the song title changes), `keep` (it is a disambiguation such as "Marie (Klus)"; it becomes an explicit TOC title, see R8).
### R3 · Move macros into `zpevnik.sty` — [agent] · M · needs S1
1. Move all package loading and macro definitions from the top of `zpevnik.tex` into `zpevnik.sty` (a proper `\ProvidesPackage`). `zpevnik.tex` keeps the document class, `\usepackage{zpevnik}`, metadata and body.
2. Add `tests/single-song.tex`, the Overleaf-style setup (class + style + one included song), and compile it in CI.

**Done when:** zero page diff; the single-song test compiles.

### R4 · Artists registry and validator — [agent] · M · needs S1
1. Create `data/artists.toml` (TOML: readable by Python's standard library, allows comments). One entry per section with `slug`, `name`, `index_label`, `sort`, `kind` (`artist` or `collection`), `section` (true/false).
2. Seed it from `obsah.tex` using **current** anchors: the index block after `\hyt{podleinterpreta}` gives slug and label, the `\subsection*{…}\hyt{slug}` headings give name and order. `filmy` is a collection. Renames happen in R6.
3. `tools/check_registry.py`: unique slugs, required fields, every `\interpret` slug exists, every `section = true` entry has ≥1 song (warning).

**Done when:** 49 entries, validator green, no `.tex` changes.

### R5 · Generator part 1: `generated/artists.tex` — [agent] · M · needs R3, R4
1. `tools/generate.py` reads the registry and writes `generated/artists.tex` (name, index label, section flag per slug, lookable by slug in TeX). Header: "GENERATED – do not edit".
2. Generated files are build outputs (D-104): `generated/` is gitignored. Add a `Makefile`: `make generate`, and `make` (= generate, then compile with `latexmk`).
3. CI runs the generator (Python step) before the LaTeX compile. `zpevnik.sty` loads `generated/artists.tex` if present; a missing file or unknown slug must **not** break compilation (Overleaf).

**Done when:** zero page diff; a fresh clone builds with `make`; nothing under `generated/` is tracked.

### R6 · ⚠ Normalise anchors and names — [agent] · M · needs R1, R4, S2
1. Apply the answers from R1 (rename table C1, split of `trikyapovery`) to the anchors in every `\interpret`/`\interpretdva` in `pisnicky/`, in `obsah.tex` (`\hylo`, `\hyt`) and in the registry.
2. Fix the name typos (C2): "Nohvica", "Marie Kubišová", and the rest decided in R1. Intentional differing labels stay for now (R7).
3. Run the validator.

**Expected differences:** only pages whose artist name was a typo or variant; list them.

### R7 · ⚠ `\artist{}` migration — [agent] · L · needs R5, R6
1. In `zpevnik.sty` define `\artist{slug}`, with an optional label override `\artist[Label]{slug}` and up to two artists per song. (What if we allowed n artists per song?) It prints the existing top-right link exactly as `\interpret` does (same position; second artist at the `\interpretdva` position), only when the registry says `section = true`. Name comes from the registry unless overridden. Empty or unknown slug: no output, no error.
2. In all 733 songs replace `\interpret`/`\interpretdva` with `\artist`; songs without artist get `\artist{}` on the line after `\song{}`. Use the override where R1 marked a label as intentional (e.g. Greenhorns).
3. Delete the old macros. Extend the validator: every song has exactly one `\artist` line.

**Expected differences:** none, except pages whose name now comes from the registry; list them.

**Changed in session 4 (owner decisions, D-113, D-114):** the link is right-aligned (1 cm from the page edge) instead of starting at 0.9 / 0.7 of the page width, so every label moves and long labels are no longer cut off; at most two artists per song, written `\artist{a}\artist{b}`; the registry has one `label` plus optional `link_label` (no `song_label`/`index_label`), and the 7 per-song overrides are gone, so Tučný songs read "Michal Tučný & Greenhorns" and Lenk songs "J. S. Lenk" (D-114).

### R8 · ⚠ Alternative titles, collections, title fixes — [agent] · M · needs R2, R3
1. In `zpevnik.sty` define three no-output macros: `\alttitle{…}` (repeatable), `\toctitle{…}` (TOC title if it differs from the song title), `\collection{slug}`.
2. Move the 28 italic alternative titles from `obsah.tex` (D1) into the songs as `\alttitle`.
3. Apply R2: fix typos on the chosen side; "keep" rows become `\toctitle`.
4. `nadstademkoni` (Buty) needs a normal alphabetical entry;
5. Add `\collection{filmy}` to the songs now listed in the `filmy` section of `obsah.tex`.
6. Note the 6 titles containing `\footnote` (C6); no change.

**Expected differences:** typo fixes in song titles only (the TOC is still hand-written).

### R9 · Generator: include list — [agent] · S · needs R8
1. Generator writes `generated/include.tex`: one `\include{pisnicky/<id>}` per song, with a letter comment (`%A`, `%B`, …) for each first-pass letter of D-107. There is no `%Ď` any more: Ď sorts with D.
2. Order = Czech collation of the plain-text TOC title (`\toctitle`, else `\song`), exactly as specified in DECISIONS.md D-107, never the file name. Implement the collation in the generator with unit tests (no `locale`). The plain-text title has its footnote removed and its accent macros and `\uv{}` resolved.
3. First generate and compare with the current order in `zpevnik.tex`; report every song that moves (the ~20 hand-placement deviations plus titles affected by word-by-word ordering) and wait for my OK before replacing anything.
4. Replace the hand-written include block with `\input{generated/include}`.

**Expected differences:** only the approved moves (S3 reports them as moved songs).

### R10 · Generator: TOC letter sections — [agent] · L · needs R8, R9
1. Generate the letter navigation row and the letter sections of `obsah.tex` (multicols, `\hylo` per song, `\alttitle` entries in italic, `\toctitle` honoured), reproducing the current layout exactly.
2. Replace the hand-written part; the generated file is `generated/obsah-letters.tex`.

**D-115 agreed (4 Nov 2026):** the artist index becomes a column list and the TOC order changes (letter row, link to the artist index, song list, artist index, songs by artist). At the start of R10 the agent presents which part each of R10 and R11 builds and the expected differences; the owner confirms before work starts.

**Expected differences:** the corrected typos, the order within letter sections (same order as R9), and the removed Ď section and its link in the navigation row ("Ďáblovy námluvy" is listed under D, D-107); nothing else.

### R11 · Generator: artist index and sections — [agent] · L · needs R7, R10
1. Generate the artist index as a column list with the full labels of the registry (D-115, D-114; agreed split in session 6: the TOC order stays, only the index changes form) and the per-artist sections from the songs' `\artist` / `\collection` tags and the registry (`section = true` only; order by `sort`; songs by title).
2. `obsah.tex` becomes a thin wrapper around the generated files.

**Expected differences:** the artist index (column list, full labels) and the drift fixes (6 mismatches listed in C5); list them. At the start the agent proposes the column layout (number of columns, spacing) and the owner confirms.

### R12 · Lints and README — [agent] · M · needs R11
1. Lints in `tools/`, run in CI. Fail: song without `\song`, unknown `\artist` slug, `section = true` with no songs. **Warn** (list): artist with `section = false` reaching the threshold from R1, duplicate titles without `\toctitle`. Info: count of songs with empty `\artist{}`.
2. Rewrite the README (Czech, same style): how to add a song now (one file, `\artist`, registry entry for a new artist, `make`), the Overleaf single-song workflow, the artist rules. Remove obsolete steps (hand-editing `zpevnik.tex` and `obsah.tex`, bumping the version, `pdflatex zpevnik.tex`).

**Done when:** following the README on a new test song works end to end.

### R13 · Single source for the version — [agent] · S · needs R5
CI computes the version as *song count + 100* (8.33 today), but the colophon (`preamble/vydavatelskyzaznam.tex`) has it typed in by hand. Make `generate.py` write `generated/version.tex` with that same formula, include it in the colophon, and let the CI version step read it from the generator. Remove the manual version step from the README.
**Done when:** the PDF shows the computed version; no manual edit needed.


### R14 · Local build, also of a single song — [agent] + [you] · S · needs nothing
- `make song SONG=<id>` builds only that song, in seconds and without Overleaf: a generated main file based on `tests/single-song.tex`, with the output in `build/<id>.pdf` (gitignored).
- README (Czech): how to install what the build needs on macOS (MacTeX, or BasicTeX plus the `tlmgr` packages the book uses, latexmk, Python ≥ 3.11) and on Linux. A local build with a newer TeX Live can differ slightly from CI, which stays the reference.
- The agent can't run macOS. The owner confirms on his Mac that `make` and `make song` work.

---

# Phase 3 – Print (back in scope, D-122)

The printed edition is important and has a deadline. The plan is to finish the refactoring first, but the owner may pivot, so P1, P3 and P4 are written to work on the current layout: they need only phases 1–2 (done) and can be repeated after phases 5–6 change the spacing. The screen PDF must never change because of them (S3 diff: none).

### P1 · Print requirements — [you] · S
Decide and write down (the agent records it as a DECISIONS entry): the **deadline**; page size and binding (A4, A5, …); margins including the gutter for two-sided printing; paper and colour (black and white or colour); the printer's technical requirements (PDF version or PDF/X, embedded fonts, bleed, crop marks); whether links stay visible; the number of copies; **full songbook or a subset** (a subset needs E1–E4 first); and which refactoring phases must be done before the print (or the cut-off at which you print the layout as it is).

### P2 · Licensing check — [you] · S
Before **selling** printed copies, check the licensing (e.g. with OSA and the rights holders of the lyrics and chords). A sold book is not the same as a free PDF. Record the result in DECISIONS. It blocks selling, not building.

### P3 · Print build — [agent] · M · needs P1 (soft: C5, V8)
A separate build target (`make print`) with the page geometry from P1, built from the same song files and generated files; no copy of song content. The screen PDF is unchanged (zero diff). Every song is meant to fit on one page, and a smaller page than A4 makes some spill: run the one-page check with the print geometry, report every song that takes more pages and propose a fix per song (smaller text, a tighter block gap, a two-page allow-list entry); do not change song content or fix silently. Also: even page count, blank pages where a spread needs them, the contents and the artist index still resolve, links printed without colour (or as P1 says).

### P4 · Print proof check — [agent] + [you] · S · needs P3
Preflight the PDF: fonts embedded (`pdffonts`), page size and page count, colour space against the printer's requirement (report, convert only if asked), crops of the first page, a middle page, a two-page song and the contents at 100%. The owner reads a proof and signs off. Record the commit and version that went to the printer in the Status table.

---

# Phase 4 – Hygiene (no visual change)

### H1 · Fix source quirks — [agent] + [you] · S
Five files rely on how LaTeX tolerates a missing argument. Fix each so the source says what was meant, show the page diff, and let me confirm:
`klada` (`\note(capo 2)` → braces around the whole note), `jaktosnamalaskobude` (`\emph(Cože)`), `neninutno` (`\vers{3} =…`: show the lines and ask), `noe` (`\refsm` without argument swallows the next command), `morituritesalutant` (`\bridge` without content swallows `\newpage`).
**Must come before H2.** `oneofus` (free text inside a chord) is valid; leave it.

### H2 · ⚠ Remove redundant `\newpage` — [agent] · S · needs H1
Remove the final `\newpage` from every song (`\include` already starts a new page), from `sablona.tex` and from the README. **Expected differences:** none. If any page changes, restore that song and report it.

### H3 · ⚠ Derive `\hyt` from the generated include list — [agent] · M · needs H2, R9
Have the generated include list set the song id before each `\include` (e.g. a `\songinclude{<id>}` macro), and have `\song` create the hypertarget from it; then delete `\hyt{…}` from all songs, `sablona.tex` and the README. In the Overleaf single-song test no id is set, and `\song` simply creates no target. If this does not work with `\include`, stop and report.
**Expected differences:** none.

### H4 · ⚠ Accents to UTF-8 — [agent] · S · needs H3
Replace accent macros (60 uses of `` \` ``, 5 others), including in titles (`Felicit\`{a}` → `Felicità`) and wherever the TOC copies them. **Expected differences:** none.

**TODO (owner, session 6): song footnotes in `\song{}`.** Six songs (`bellaciao`, `conselho`, `johnnybgoode`, `pasopanori`, `tasidele`, `thepassenger`) have a `\footnote{}` inside `\song{}`; the footnote is about the whole song, not the title. The owner wants to keep the `\footnote` syntax so that whoever writes the next song is not confused, so nothing changes now: the generators drop the footnote from the plain-text title (D-107), and the converter (WP5) must do the same. Decide the final place when H4 or the converter touches titles; options discussed: `\songnote{}` before `\song{}` (same page), after `\artist{}` anchored to the first verse, or a visible note line.


### H5 · Song fixes from the C1 review — [agent] · S · needs nothing
- `acrosstheuniverse`: its song-level footnote is written as `\note{\footnote{…}}`, so the footnote mark stands alone on the left under the title (owner: not a good place). Move the `\footnote{…}` into `\song{…}`, like the six songs in INVENTORY C6, so the mark follows the title. The plain-text title stays as it is (the generators drop footnotes, D-107).
- `rosanakolejich`: a chord is missing, `Je \chord{D}ráno` (owner, C1 review; the first "Je ráno" in the song).

**Expected differences:** those two songs only. Footnote numbering unchanged.

### H6 · ⚠ Replace the `\everypar` hack — [agent] · M · needs nothing
`zpevnik.sty` redefines the TeX primitive `\everypar` as a macro (`\def\everypar{\parindent=-10mm}`). TeX still uses the real token list at every paragraph start, so the macro runs only where LaTeX code calls `\everypar{…}` by name (after headings, in lists, after environments, in parboxes and minipages). There it sets the hanging indent and runs LaTeX's intended code immediately instead of at the next paragraph start. The layout depends on these side effects. Replace the hack with explicit settings: the −10 mm indent set once, plus whatever the side effects provide today. The primitive is restored.
Found in session 12 (scratch build, never pushed): the naive replacement (`\setlength{\parindent}{-10mm}` + `indentfirst`) changes 54 songs, pages 3, 5–7, 741–742 and the contents (749–757). 47 of the 49 changed songs without a footnote have a subtitle (`\sub`). Probable cause, not verified: LaTeX's "right after a heading" state is no longer cleared at the title, so the `\subsection*` inside `\sub` loses its space above.
**Expected differences:** none. If one cannot be avoided cleanly, list it; the owner decides.

---

# Phase 5 – Chord spacing

### C1 · Prototype automatic chord spacing — [agent] · **[strong model]** · L · needs H4 — done
Done in session 9: draft PR #42 (branch `proto/c1-chord-spacing`, never merged; close it after C3a is merged). Assessment, real PDFs and images: docs/C1-chord-spacing.md and docs/C1-chord-spacing/. Book-wide lists: docs/C1-review-lists.md (the owner's answers are in sections 1–2). Outcome: D-123.

### C2 · Gate — [you] · S — done
Path A (owner, 4 Nov 2026), with the details in D-123.

### C3a · Chord macros on master, switched off — [agent] · M · needs C2
One PR. **Expected differences: none.**
1. Port into `zpevnik.sty` from `proto/c1-chord-spacing`, simplified as D-123 says (no hyphen switch; `\gap{n}` is a plain `\hspace{n × 0.5em}`):
   - the lookahead `\chord`, with `\chordsep` 0.5em and `\chordrunsep` 1em;
   - the hyphen in a split word;
   - `\gap{n}`;
   - `\chords{…}` (red);
   - the chord-position trace.
2. Per-song switch: the automatic spacing is off by default and `\song` switches it off. A song opts in with `\autochords` written right after its `\song{…}` line (temporary, removed in C4).
3. `tools/strip_chord_spacing.py` (from the branch), updated per D-123:
   - spacing after a chord inside a word is removed, not turned into `\gap`;
   - the owner's answers (D-123) are encoded, so none of those places is reported as CHECK any more;
   - whole chord-only lines become `\chords{…}`, and so does `\textbf{…}` that holds only chord names;
   - the tool adds `\autochords`;
   - unit tests for every rule, with examples from D-123 and C1-review-lists.md.
4. `tools/chord_gaps.py`: the trace is on in every build (`zpevnik.chords`, gitignored). Map pages to songs (check_pages). CI fails on an overlap in a song with `\autochords` and only reports overlaps elsewhere.
5. **Batch plan.** Build master with the spacing on for every song and diff it against master. Write `docs/C3-batches.md` on the owner's computer. It lists every song C3 will change (manual spacing, `\textbf` chords, chord-only lines, or a page that changes with the spacing on), alphabetically, in batches of about 45 (expected ≈ 460 songs, ≈ 10 batches).

Verification: zero diff; single-song test with `\autochords`; the tool run on three songs in a scratch branch (never pushed) shows each rule.

### C3b · ⚠ Remove manual chord spacing, in batches — [agent] + [you] · L · needs C3a
One PR per batch of docs/C3-batches.md, in order.
1. Run `tools/strip_chord_spacing.py <the batch's ids>`. Put its log in the PR description: every `\gap`, kept word space, `\chords` conversion and CHECK place. The owner decides the CHECK places in the PR.
2. Build. check_pages 0 problems; chord_gaps 0 overlaps in the batch's songs. PDF diff: the batch's songs and nothing else.
3. Compile the batch's songs as a real PDF (`\includeonly`, as in C1), master and new pages alternating, to `docs/C3-batches/batch-NN.pdf` on the owner's computer.
4. Report:
   - chord runs whose uneven spacing may have been intentional (they are now even);
   - songs where lyrics moved by more than 2 characters;
   - songs whose height changed (chord-only lines turned into `\chords` take less space).

**Expected differences:** the batch's songs only.

### C4 · Chord cleanup — [agent] · S · needs all C3b batches
- Make the automatic spacing the default, and remove `\autochords` and the switch. **Zero diff**: every song that changes was migrated in C3b.
- Delete `\nc \mm \sm \bc` (grep must find none) and `tools/strip_chord_spacing.py`.
- chord_gaps fails CI on any overlap in the book.
- Lint: an error on `\nc \mm \sm \bc`; a warning for a song with no `\chord` or `\chords` (K1).
- Update the README (Czech): `\chord`, `\gap{n}` for pauses, `\chords{…}` for chord-only lines, no manual spacing.
- Also delete what is unused (owner, 4 Nov 2026; PLAN WP4 last bullet):
  - the optional alignment argument of `\chord` (0 uses of `\chord[`; the padding assumes left alignment);
  - `\placepic` (no use);
  - check `\placetextbox` (only `vosa.tex`) and keep it if it's still used.

### C5 · Label width — [agent] + [you] · M · needs C4
Today each block macro (`\vers`, `\refrain`, …) uses its own `\hspace` (0.5–1.2 em) after the label. Replace them by one fixed label width, derive `\nv` from it, and replace the 24 raw `\hspace` (A4).
**Expected differences:** text after labels shifts by tenths of a millimetre; you review.


### K1 · Songs without chords — [you] · S · needs nothing
Every song should have chords. 8 songs have no `\chord`:
- 5 have only a chord progression written as `\textbf{…}`, which becomes red `\chords{…}` in C3: gronskapisnicka, marieklus, noe, panubohudooken, vranabuty.
- 3 have only a score image: ladovskazima, scarboroughfaircarthy, triandele.

The owner decides per song whether to add chords over the lyrics (content work). From C4 on, the lint warns about a song without chords.

---

# Phase 6 – Vertical spacing

### V1 · Analysis, no code changes — [agent] · **[strong model]** · M · needs C5
For `\ns`, `\cns`, `\vnv`, `\vinv`, `\lsp` and the raw `\vspace`: take 20 random contexts each (all if fewer), show the source and the rendered page crop, classify what the author meant (e.g. "attach to previous block"), and propose one semantic replacement per class with the exact equivalent. Write `docs/vertical-spacing.md`.

### V2 · Approve — [you] · S
Mark each proposal `OK` or correct it. Tickets V5–V7 follow only what you approved. Done 5 Nov 2026: D-124 (the ticket plan V3–V8 below was rewritten after it).

### V3 · Shrinkable `\blocksep` — [agent] · S · needs V2, H6
One length `\blocksep` = 20 pt minus 20 pt (D-124), used by every block macro that starts with `\vspace{20pt}`, through one internal helper. The helper also supports "the next block has no gap" for V4's separators; `\song` resets that flag. `check_pages` stays at 0 problems.
**Expected differences:** 6 songs (session 12 scratch build): `babickamary`, `milionar`, `promeny`, `vodavodenka` (two-column: the balancing uses the shrink), `tophatbarandgrill` (lines up to 7.3 pt higher), `illbethereforyou` (3 pixels). The cause for the last two was not found. A gap next to a remaining `\ns` can shrink below zero, so check these 6 for overlaps; the owner reviews them.

### V4 · Named separators and group break — [agent] · S · needs V3
- `\\` + `\vinv` → `\groupbreak` (90 places; the 2 in `vlese` stand after a `}`: move the inner `\\` out).
- `\lsp{w}` → `\blockrule{w}`: the same dashed rule, but it replaces the next block gap instead of cancelling it (−3 pt after the rule instead of −23 pt).
- `idzepostaridze`: `\ns` + centered `\rule{18cm}{0.03cm}` + `\ns` → `\partrule`.
- `\vers{}{…}` with an empty number prints no label (no song uses that today).
The definitions gave zero diff in the session 12 scratch builds (docs/vertical-spacing/analysis.md, section 5). **Expected differences:** none.

### V5 · ⚠ Song-by-song cleanup, in batches — [agent] + [you] · L · needs V4
Alphabetical batches of about 30 of the 172 songs with vertical spacing, reviewed like C3b. Per song, in one go:
1. Delete every `\ns`, `\cns` and squeezing negative `\vspace`, all of them in the song at once (a remaining one next to a shrinking gap can go below zero).
2. Wrap blocks without a label (`\nv` paragraphs separated by `\vnv` or `\vspace`) in `\vers{}{…}`.
3. For each `\groupbreak` and each remaining `\vspace`, the agent proposes keep (a `\vspace` gets a `% reason`), replace or delete; the owner decides.
4. The `\vspace` and `\hspace` next to score images stay (D-124).
5. `check_pages` 0 problems; a song that spills is reported, not tuned by hand. (Owner, session 15: no song may spill; fix each one, see D-128.)
`docs/vertical-spacing/occurrences.csv` has a pre-class for every occurrence (snapshot; re-derive). Batch PDF in `docs/V5-batches/`.
**Expected differences:** the batch's songs; the owner reviews every one.

### V6 · Name the hidden spacing — [agent] · S · needs V3
Replace the literal numbers inside `\note` (−20 pt), `\sub` (−10 mm, unless H6 removed it), `\hyl` (−15 pt) and `\blockrule` by named lengths in `zpevnik.sty`, with a comment each. **Expected differences:** none.

### V7 · Merged into V5 (D-124)

### V8 · Final cleanup — [agent] · M · needs all V5 batches, V6
Delete `\ns`, `\cns`, `\vnv`, `\vinv` and `\lsp`; lint error on them (as C4 did for the chord macros); `check_pages` on everything; README. `babickamary` and `milionar` spill with the shrinking gap alone (session 12): report them with a proposal per song (tighten, split or allow-list); the owner decides. **Expected differences:** none beyond those two songs.

---

# Phase 7 – Converter and `songs.json`

### J1 · Converter package — [agent] · **[strong model]** · L · needs R12, H4, C5, V8
1. Write the converter in `tools/songbook/` as a package: parser, model, command line. The `tex2json.py` prototype mentioned earlier is not in either repository, so this starts from scratch. Strict: an unknown macro is an error. It only needs to understand the macros left after phases 4–6; legacy spacing macros are errors (D-108).
2. Support the new macros (`\artist`, `\alttitle`, `\toctitle`, `\collection`); keep the title and its footnote apart; render repeat marks as the PDF does.
3. Tests: snapshot tests for 10 songs plus a whole-book parse that must succeed for all 733 songs in under 5 s.

### J2 · Assemble `songs.json` — [agent] · **[strong model]** · M · needs J1, S2
Top level: `schemaVersion`, `version`, `songs[]` in book order (the generated include order), `artists[]` from the registry. Each song: `id`, `title`, `altTitles`, `artists`, `collections`, `subtitle`, `see`, `order`, `page` (from the S2 records), `footnotes`, `images`, `columns`, `blocks[]` (lines of chord/text segments).

### J3 · JSON Schema — [agent] · **[strong model]** · S · needs J2
`tools/songs.schema.json`; validate the output in tests and in CI.

### J4 · CI and release asset — [agent] · M · needs J3
After the compile, run the converter and the schema validation. On pushes to `main`/`master`, add `songs.json` to the `files:` of the release step. PRs only validate.

### J5 · Scores from MuseScore — [agent] + [you] · M · needs J4
The `.mscz` files are the source; CI exports the images, so the PDF and the web use the same export (D-125). A score is a single page by principle.
1. **Prototype first and report before building on it:** a pinned MuseScore 4 in CI with `-o file.svg -T 0` (trimmed SVG, documented for single-page scores only). pdfLaTeX cannot include SVG, so for the PDF either convert the SVG (e.g. `rsvg-convert`) or export a PDF and crop it with `pdfcrop`. Compare a few results with today's images.
2. One `.mscz` per image. Missing (session 12): `tickettoride` uses `ticket_to_ride_intro.png`, which has no source. These `.mscz` produce more than one image today: `morseovka.mscz` (`morseovka_1.png`, `morseovka_2.png`), `pohadka.mscz` (`pohadka.pdf` and `pohadkaref.pdf`), `reddwarftheme.mscz` (intro and outro), `slunecnyhrob.mscz` (intro and solo). Unused: `morseovkasolo1–3.pdf`. The owner provides the missing files.
3. The exported images are build output (D-104), not committed; remove the committed PDFs and PNGs once the export works. The SVGs go into the release as one zip and are referenced from `songs.json`.
4. The `\vspace` and `\hspace` next to scores stay (D-124), but check them against the new crop.
**Expected differences:** small shifts of the score images; the owner reviews them.

---

# Phase 8 – Legal

### L1 · Notice text — [you] · S
A short text in Czech and English: non-commercial, contact address for removal requests. It goes into the website footer and the PDF colophon.

### L2 · Hide switch — [agent] · S · needs R11, J2, L1
`data/hidden.txt` with one song id per line. The generator leaves those songs out of the include list, TOC and index; the converter leaves them out of `songs.json`; a lint checks that each id exists. Put the L1 text into the colophon. (This hides songs from the outputs; deleting the file is the only way to remove it from the repository.)

---

# Phase 9 – Website (`zpevnik-web`)

### W1 · Load the data — [agent] · M · needs J4
`build.py` downloads `songs.json` from the release tagged `v<version.txt>` (the songbook CI already writes `version.txt` after creating the release) into an uncommitted folder, validates `schemaVersion`, and fails loudly if missing. Add a local option to point at a file.
The PDF comes the same way (D-110): the songbook CI stops committing `static/files/zpevnik_last.pdf` and only writes `version.txt`; the download page keeps its URL and `download` file name.

### W2 · Song pages — [agent] · L · needs W1
The online songbook is separate from the download page (D-103): it lives under `/zpevnik/`, with its own templates and navigation; the download page at `/` stays as it is, plus one link to the songbook.
Jinja template, one page per song at `/zpevnik/<id>/`: chords above lyrics (each chord and its text in an inline-block that keeps spaces; chord width is respected, like in the PDF), labels, footnotes, score SVGs, the existing dark mode, a font-size control. It must read well without JavaScript. Every page carries `<meta name="robots" content="noindex">`.

### W3 · Index, artists, navigation — [agent] · M · needs W2
Alphabetical index (same order as the PDF), artist pages at `/zpevnik/interpret/<slug>/`, collection pages, alternative titles listed, previous/next links in book order, "open in PDF" using `page`.

### W4 · Search — [agent] · M · needs W2
Build-time index over title, alternative titles, artist and lyrics (about 270 kB gzipped), loaded on first use, diacritics-insensitive, no libraries unless tiny.

### W5 · Wake lock — [agent] · S · needs W2
A toggle on the song page using the Screen Wake Lock API; hidden where unsupported.

### W6 · Robots and notice — [agent] · S · needs W2, L1
`robots.txt` disallowing everything, no sitemap, notice page and footer link. Hidden songs are absent because they are absent from the JSON.

### W7 · Release check — [agent] · S · needs W3–W6
Build under 1 minute; 733 song pages (minus hidden); every internal link resolves; screenshots of 3 songs on a phone-sized viewport; update the web README.

---

# Phase 10 – Editions (song subsets, D-121)

Known use cases: **`zpevnik-lite`**, a book of selected favourites (manual selection), exported now and then; and possibly the printed book (P1). The generator already works from one song list, so an edition is a filter over it. Everything below keeps the full book byte-identical (zero diff).

### E1 · Decide the editions design — [you] · S
Answer the six questions; the agent proposes the defaults marked with *.
1. How an edition is defined: `editions/<name>.toml` (title, optional subtitle, file name, list of song ids)*, or a tag in the song files. The order is always the D-107 collation, never the list order*.
2. What happens to a `\hyl` link (and any other reference) to a song that is not in the edition: leave the link out*, or print the title without a link.
3. Artist sections and index: only artists with at least one song in the edition*; the threshold of 3 (D-119) does not apply*.
4. Name and version of an edition book, for example `zpevnik-lite` plus the book version*.
5. Where it is published: a release asset only*, or also the download page of `zpevnik-web`.
6. Title page and colophon text of each edition.

### E2 · Generator: edition filter — [agent] · M · needs E1
`tools/generate.py --edition <name>` (default: the full book) reads `editions/<name>.toml`, filters the song list once and generates everything from it: include list, letter contents, artist index and sections. Edition title, subtitle and version go to a generated `edition.tex` that `patitul`, `titulnilist`, `uvod` and `vydavatelskyzaznam` use instead of the hard-coded title. An edition's generated files go to their own folder, so both builds can run in one checkout (for example a path macro passed on the `pdflatex` command line; take the simplest way that leaves `make` unchanged). An unknown song id is an error. Unit tests. **Expected differences:** none for the full book.

### E3 · Links to songs outside the edition — [agent] · S · needs E2
Implement the E1 rule for `\hyl` (84 uses in 76 songs); a generated list of the songs present (like the artist registry) lets `zpevnik.sty` decide without a second pass. Add a check that every `\hylo`, `\hyl` and artist-section link of an edition points to an existing target, and fails otherwise; run the one-page check and the lints on the edition. **Expected differences:** none for the full book.

### E4 · Choose the songs for `zpevnik-lite` — [you] + [agent] · S · needs E2
The agent adds a small helper that lists song ids with title and artist (filter by artist) to pick from. The owner picks the songs; the agent writes `editions/lite.toml`; lint checks that every id exists. **Expected differences:** none for the full book.

### E5 · CI and release — [agent] · M · needs E3, E4
CI builds every edition in `editions/` on pull requests (the build, the one-page check and the link check must pass) and, on pushes to master, attaches `zpevnik-<name>-<version>.pdf` to the same release as the full book. No change in `zpevnik-web` unless E1 says so. The PDF diff keeps comparing the full book only. Czech README section on editions: how to add a song to one.

---

# Documentation

### Z1 · Project history and helper files — [agent] · S · needs nothing; repeat at the end of each phase
1. Start `docs/HISTORY.md`: one short section per finished phase, with what changed and why, the key numbers before and after, the PRs and the decisions. Facts only, taken from the Status table, DECISIONS.md and the helper files. It is the source for the later story on the website.
2. Move the finished phases' helper files into `docs/archive/<phase>/` (C1-*, C3-*, C5-previews.pdf, R9-moves.md, vertical-spacing/ after V8, …). Before moving a file, check that everything important in it is in HISTORY.md, DECISIONS.md or TICKETS.md. Update the links. Nothing is deleted. INVENTORY.md stays until all its sections are consumed.

---

## Backlog (not ticketed)

Transposition (Czech B/H convention), setlists, offline use, fit-to-screen, ChordPro export.

- **Body font size** (session 12): the class is 10 pt and the whole book is wrapped in `\begin{Large}` (14.4 pt on 18 pt), so absolute sizes stay tied to 10 pt: footnotes are about 8 pt, and `\dm`/`\bb` call `\Large` themselves. Set the body size once in `zpevnik.sty` with today's look, so footnotes scale and print can change it in one place. After V8; keeping it as it is is fine (owner, 5 Nov 2026). Before P3 if the print needs another size. **Decided 6 Nov 2026 (D-129):** the book stays in `\Large`, `\large` by hand per song when it is too long.
- **Rethink `\refsm` / `\refsme`** (owner, session 15, 6 Nov 2026): both print the small refrain mark "R."; `\refsm{}` is inline (end of a verse line), `\refsme{}` is a standalone line with a block gap before it (`\zp@blockgap`). Consider one command that behaves by position, or a name that says which one is which. Seen in `dobreminenarada` and `allyouneedislove` (706 uses of `\refsm` in the songs).
- **Capo note versus song remark** (owner, session 15, 6 Nov 2026): `\note` belongs to the next block (the no-gap flag, D-128), which is right for "capo 3" but wrong for a standalone remark (`allyouneedislove`: structure 4/4 | 3/4, `interludium (sloka)`), which needs a normal block gap and today gets a manual `\vspace{\blocksep}` with `% KEEP` or a `\vers{}{\emph{…}}`. Idea: a second command for remarks that behaves like a block, which would also give the web version a note type. Agent's view: decide after the V5 review, when it is clear how many songs have a remark (so far 1 in batch 1; 5 other songs checked there are capo-style).
- **Grouping verses, tight versus loose** (owner, session 15, 6 Nov 2026, seen in `ejhorahora`): short one-line verses looked better with the old tight spacing; one 20 pt gap between every verse is airy. Idea: a way to group verses so they sit tight inside the group and get the normal gap between groups. Not necessary.
- **Bigger gap between groups of verses, and bilingual songs** (owner, session 15, `jednoubudemdal`): a manual bigger gap between groups of verses would be useful. The Czech and the English version share one page there; by the logic of the songbook they should be two songs (which would remove the need). Not necessary.
- **Dashed rule and chords of the next block**: done in #76 and #77 (D-128 amended).
- **Standalone `\refsm` lines** (owner, session 15, 6 Nov 2026): eight songs have a `\refsm{…}` mark on its own paragraph, which sits tight under the block above while the next block gets a gap (as in master, where the `\ns` lines hid it): brnojezlatalod, buchetjespousta, haubilouplani, letitbe, rekalasky, ringoffire, soske, tasidele. Decide together with the `\refsm` / `\refsme` rethink whether such a mark should get a block gap (in morseovka and allyouneedislove it became `\refsme`).
- **DONE 6 Nov 2026 (`\spk`, PR #78): Speaker marks (`On:`/`Ona:`)** (session 15, `motyl`): the marks hang in the label column through the negative `\parindent`, not through a label; `\vers{}{…}` would inline them. A label type for speakers (together with the capo-note/remark types) would let them be blocks with the normal gaps. For now `motyl` keeps its paragraphs with `\vspace{\blocksep}` between the groups.
- **Refactoring story on the website** (owner, 5 Nov 2026): a short story of the whole refactoring, written from `docs/HISTORY.md` (Z1) when the website exists.

- **Print edition and song subsets** moved into phases 3 and 10 (D-121, D-122, 4 Nov 2026).
- **CI speed** (session 7, 4 Nov 2026): a PR check takes about 3.5 min; 132 s of that is the first `xu-cheng/latex-action` step downloading the TeX Live 2023 container, poppler adds 12–29 s, everything else is seconds. Tried: Ubuntu 24.04's own TeX Live 2023 via apt (PR #37, closed): its output is identical to the container's (757 pages, same renders and text), but the apt download was 1161 MB at 1.3 MB/s, so the install took about 15 min. Not adopted. Ideas not tried: skip the poppler install if the runner already has it (about 25 s); a smaller TeX image if one exists with the needed packages (fonts-extra only for one cursive font).
