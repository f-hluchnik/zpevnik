# Zpěvník – tickets

Each ticket is one pull request. Background: [PLAN.md](PLAN.md). Agreed decisions: [DECISIONS.md](DECISIONS.md); a ticket never overrides an agreed decision. This file lists only what is left. What is done: [HISTORY.md](HISTORY.md), and the full text of every finished ticket in [archive/](archive/README.md). Tickets are grouped into sessions with ready-made prompts in [SESSIONS.md](SESSIONS.md).

Goal: the PDF and an online HTML songbook, both built from the same LaTeX files (D-100). The refactoring, the editions, the converter, the legal hygiene and the online songbook are done (HISTORY.md). What is left is the printed edition (P1, P4), the choice of songs for `zpevnik-lite` (E4), the chord wrapping on the web (W6a) and the finishing tickets (J6, H7, V10, Z2). Then the songbook is done: the features that are not planned, and why, are in D-175 (correct and simple, not every feature).

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
| P4 | todo | owner signs off the proof, on the final content (after the owner's new songs, and after J6, H7 and V10 if they are to be in the printed book; K1 is done) |
| W6a | in review | zpevnik-web PR #15; owner chose "head + tail" and the font size stays (13 Nov 2026, D-176) |
| W5a | in review | zpevnik-web PR #16; owner asked for it on 13 Nov 2026 (D-174) |
| J6 | in review | `zpevnik` part: PR in the ticket text (owner chose the places, D-177); the `zpevnik-web` part is left, after the release that carries `schemaVersion` 2 |
| H7 | todo | owner decides which songs are split and their names |
| V10 | todo | owner decides the form (pages of the candidates first); after H7 |
| Z2 | todo | agent; the owner writes the article himself (D-175) |

## Overview, in the order of work (D-132)

| Phase | Tickets | After it you have |
|---|---|---|
| 10 Editions | E4 | The songs of `zpevnik-lite`, a book of favourites, picked by the owner after the printed edition (D-147) |
| 3 Print | P1, P4 | The printer's requirements and the owner's decisions, then a checked proof on the final content (D-122, D-147) |
| 9 Website | W6a, W5a | Lines of the online songbook that wrap like the book's (D-123 on the web, D-176); the screen toggle as a small icon (D-174) |
| 13 Finishing | J6, H7, V10, Z2 | Remarks the website can tell from lyrics, bilingual songs as two songs, songs in parts set consistently, and an overview of the refactoring for the article (D-175) |

The owner's new songs (about ten) are content work that runs beside these; P4 comes after them (D-147). J6, H7 and V10 change the PDF: they go before P4 if the printed book is to have them; the owner decides by the print deadline (P1).

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

The songbook is online at `/zpivej/` (HISTORY.md, phase 9). Two tickets are left.

### W5a · Keep-the-screen-on as a small icon — [agent] · S · `zpevnik-web`
The button "Nezhasínat displej" (W5, D-174) becomes a small icon button beside A− and A+, as tall as they are; the words stay as its label and tooltip; `wake-lock.js` unchanged (owner, 13 Nov 2026).

### W6a · Segments wrap freely — [strong model] · M · needs W2 · **option chosen: head + tail (owner, 13 Nov 2026, D-176)**
**The problem.** On a narrow screen, or with a larger font, a line wraps strangely (the release check of W7 saw it at the default font size on a 390 px phone too): in `folsomprisonblues`, "I" stands alone and "hear the train a-coming, …" starts the next line. Cause, measured on 12 Nov 2026: a chord and all its text up to the next chord are one `inline-block` (the W2 form of the chord rule, D-123), and a browser moves such a box whole to the next line when it does not fit beside what is before it; TeX would break at any space. The PDF is not affected.
**Not the fix.** Letting only the first word be the chord's column and the text after it flow: it pads after a first word shorter than its chord, which the book does not (498 of 1,518 multi-word chord segments in 120 sampled songs).
**To decide first (a note in this ticket's PR, an owner decision if the options differ visibly), then implement.** CSS cannot say "pad only where the next chord would collide" without measuring, so every approach is a compromise. The candidates:
1. *A text clearly longer than its chord flows; a short one keeps today's unbreakable column.* The chord is zero-width over the first word, so the text is not padded; the collision guarantee stays for the short ones (11 of 1,518 sampled multi-word segments have a text narrower than the chord and its separator). A segment that ends inside a word (the hyphen) stays unbreakable. A threshold in one named constant.
2. *Measure in JavaScript* and pad where a chord would collide. The page must still read without JavaScript, so the unbreakable columns stay as the base: the wrap is not fixed without it.
3. *Leave it:* the book's rule is exact, and the reader can make the text smaller.
The first is the simplest that fixes the wrap without JavaScript; whether a threshold is acceptable is the question.
**Chosen (13 Nov 2026, D-176):** a fourth option found in the consultation, *head + tail*: the chord's column holds only the shortest run of whole words that is at least as long as the chord, the rest of the text flows; text without a chord flows; a line breaks inside a word only with a hyphen, as in the book. The default font size stays. The measurements and the reasons are in D-176. Check with screenshots of `folsomprisonblues` and a few dense songs at 390 px and with the font at the largest size, and that the number of songs where a chord is closer to the next than 0.5 em does not grow (measure it in the browser, as for the sample above).

---

# Phase 13 – Finishing (D-175)

Q7 (one reader of the songs) is done (archive/phase-13-finishing/). The last tickets before the songbook is done. What is not planned, and why: D-175. J6, H7 and V10 are ⚠ (song files): one at a time, each merged before the next.

### J6 · Remarks as their own command — [you] + [agent] · S · ⚠ · `zpevnik` and `zpevnik-web`
**The problem** (owner, 6 Nov 2026). `\note` belongs to the next block (D-128): right for "capo 3". A remark that stands alone is written as an unnumbered verse `\vers{\emph{…}}`: 6 places in 5 songs (`hledamdevcenanedeli` "rec. A nebudu.", `allyouneedislove` ×2 (the structure of the verse; "interludium (sloka)"), `bellaciao`, `cernymuz` "verze Waldemara Matušky", `ahorsewithnoname` (the tuning)). In `songs.json` they are italic lyrics, so the website shows and searches them as lyrics.
**Decided (owner, 13 Nov 2026, D-177):** `allyouneedislove` ×2, `ahorsewithnoname` and `bellaciao` are remarks; `hledamdevcenanedeli` "rec. A nebudu." is a speaker line (`\speaker{rec}{A nebudu.}`); `cernymuz` "verze Waldemara Matušky" is a second song and goes to H7.
**The change.** A command `\remark{…}` that prints as these places print today; the converter gives a body item `remark` (a change of `songs.json`: `schemaVersion` 2, D-165); the website sets it like a note and the search leaves it out (D-170).
**Expected differences:** none in the PDF except `hledamdevcenanedeli` ("rec:" in the label column, D-177).
**Part 1, `zpevnik`:** the command, the converter, the schema, the lint, the README, the tests and the five songs. In review (the PR number is in its description).
**Part 2, `zpevnik-web`, after the release that carries `schemaVersion` 2 (until then the website's build stops on it, D-177):** `SUPPORTED_SCHEMA_VERSION` to 2 in `build.py`; `_song.html` renders a `remark` as a block of italic lines like a note (`song-note`, one line per element of `lines`); a test that the search index holds no remark text (`allyouneedislove`: "interludium"); the test that rejects another version must use a version other than 2; check the four songs at 390 px and `python check_site.py`. Then this ticket leaves TICKETS.md in a docs PR in `zpevnik`.

### H7 · Bilingual songs as two songs — [you] + [agent] · S · ⚠
**The problem** (owner, `jednoubudemdal`). The Czech version and the English original ("We shall overcome") share one song, and the verse numbers start again; by the logic of the songbook they are two songs, each with its own title, its line in the contents and in the search, linked by `\seealso`.
**To decide first (owner):** which songs (look at the other songs whose numbering starts again, listed in V10) and the new ids and titles. **Already decided in J6 (owner, 13 Nov 2026, D-177):** `cernymuz` "verze Waldemara Matušky" is one of them: the second version becomes `cernymuzmatuska`, linked with `\seealso`, and its `\vers{\emph{verze …}}` line goes (the title says it).
**Expected differences:** the songs split, one more entry in the contents and the artist index per song; the pages after them shift.

### V10 · Songs in parts and tight verses — [you] + [agent] · M · ⚠ · `zpevnik` and `zpevnik-web` · after H7 · [strong model] for the design
**The problem** (owner). (a) `ejhorahora`: short one-line verses looked better tight; a group of verses could be tight inside, with the normal gap between groups. (b) A song in parts has no consistent separator: 8 songs start their verse numbers again (`cernymuz`, `ejhorahora` (3 parts), `idzepostaridze` (3), `jedesohajzvidna`, `jednoubudemdal`, `kolenasejchalupecky`, `rezrezrez`, `vodavodenka`); 4 of them separate the parts with `\partrule`, the others only with the normal block gap.
**What exists:** one shrinkable block gap `\blocksep` (D-124); `\groupbreak` (a smaller gap between groups of lines inside one verse); `\blockrule` (dashed); `\partrule` (solid).
**To decide first (owner, from pages of the candidates):** whether a song in parts always gets `\partrule` (or a larger gap instead), and whether tight verses are a new semantic form (a group of blocks) or stay one verse with `\groupbreak`. Whatever is chosen is semantic, so it reaches `songs.json` and the website (D-108). One song per page (CI) must still hold.
**Expected differences:** the songs decided, nothing else.

---

# Documentation

### Z1 · Project history and helper files — [agent] · S · at the end of every phase
Done for every finished phase (HISTORY.md, docs/archive/); phases 10 and 3 have a few tickets open, whose finished ones are archived already. At the end of each phase, in the PR of its last ticket: add the phase to HISTORY.md (what changed and why, numbers, PRs, decisions), move its finished ticket texts and status rows to `docs/archive/<phase>/TICKETS.md` and its text helper files next to them. Binary review files are not committed (attach them to the PRs). Exact duplicates may be deleted; everything else is moved.

### Z2 · An overview of the refactoring — [agent] · S · `zpevnik` (docs only)
For the owner, who writes the article on the website himself (D-175), and as a reference later: `docs/OVERVIEW.md`, facts only, readable in ten minutes. The starting point (v8.33) and the goal; for each area (safety net, registry and generated files, source hygiene, chord spacing, vertical spacing, code quality, editions, print, converter and `songs.json`, legal, website) the problem, what was done and how (the mechanism in a sentence or two), the numbers, and the decisions and PRs as links; the end state as one diagram (song files → `zpevnik.sty` → PDF; song files → converter → `songs.json` → website); what is not planned and why (D-175). It links to HISTORY.md, DECISIONS.md and WALKTHROUGH.md instead of repeating them. The *Notes for the website article* of HISTORY.md move into it, so the article has one place. A later phase adds its line in its last PR (Z1).
