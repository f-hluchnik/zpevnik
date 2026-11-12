# Sessions 20–27 (done 10–12 Nov 2026)

The blocks of the sessions of phases 10, 3, 12, 8, 7 and 9, with what each did, as they stood when the work ended (session 27, the online songbook, also covered W7). Summary: [HISTORY.md](../../HISTORY.md). Earlier sessions: [snapshot-2026-11-06/SESSIONS.md](../snapshot-2026-11-06/SESSIONS.md) and [phase-11-code-quality/SESSIONS.md](../phase-11-code-quality/SESSIONS.md).

### Session 20 · E0 and the editions review — done (10 Nov 2026)
E0 merged (PR #93; first release `v8.33.68`). Planning E2 led to D-143 (English names, the full book as the edition `full`, an explicit page contract, one `build/` root, `make` as the only entry point), recorded in a docs-only PR. Verified in this session with TeX Live 2023: the edition passed by `-usepretex`, the `.aux` subfolders the build must create in the output directory, and the full book byte-identical without `\setcounter{page}{8}`.

### Session 20a · R15 — done (10 Nov 2026)
R15 merged (PR #95): English names for the folders and front-matter files (D-143).

### Session 20b · E2, E3, E8 — done (11 Nov 2026)
E2 (PR #96, D-144): every book is an edition (`data/book.toml`, `editions/<name>/edition.toml`), generated into and built under `build/editions/<name>/` by `make [EDITION=<name>]`; the page check reads the main `.aux`; CI builds base and head in the same TeX Live action. E3 (PR #97, D-145): `\seealso` to a song outside the edition is left out, a link to a missing target fails the build, the lints validate every edition, `make check [EDITION=<name>]`. E8 (PR #98): front matter in Czech book order, the songs from page 9. All three verified with a throwaway edition (not committed); the full book unchanged by E2 and E3, every song exactly one page later after E8.

### Any session · R16 — done in session 21 (11 Nov 2026)
The song count changed after R15 (version 8.38); the traces of the old folder and of the layout before editions are gone.

### Session 21 · E7, R16 — done (11 Nov 2026)
R16 merged (PR #102). E7 merged (PR #103, D-146): `editions/lidovky/` with its own cover (the photo and the caption "lidové písničky" as in the old book) and the subtitle "lidové písničky". The planning of the rest of the session led to D-147 (the order below).

### Session 21a · E5 — done (11 Nov 2026)
E5 merged (PR #106, D-149): the CI finds, builds, checks and releases every edition by `edition_names()`; first release with it `v8.38.5`.

### Session 21b · E6 — done (11 Nov 2026)
E6 (PRs f-hluchnik/zpevnik-web#3, merged first, and f-hluchnik/zpevnik#107, D-150): the website downloads the PDFs from the release `v<version.txt>`, the buttons come from `EDITION_DOWNLOADS` in its `build.py`, the songbook CI writes only `version.txt`. The owner archives `zpevnik-lidovky` himself once the page is live.

### Session 21c · P0 — done (11 Nov 2026)
P0 merged (PR #113): the print feasibility report with the printer checklist (`docs/p0-print-report.md`); the geometry trial stays a one-off branch (D-154).

### Session 22 · P3 — done (11–12 Nov 2026)
P3 merged (PRs #114–#116, D-154–D-157): the print formats `print` and `print-black`, page numbers on paper, the A5 PDF with the spine shift (`make print`). P1 (the printer's and the owner's answers) and P4 (the proof, on the final content) are open.

### Session 22a · A1 — done (12 Nov 2026)
A1 merged (PR #117, D-158): the README follows the owner's work; changes reach `master` only through a pull request.

### Session 22b · A2 — done (12 Nov 2026)
A2 merged (PR #118, D-159): 8 tests dropped (252 → 244), the rest kept on the evidence of a mutation run.

### Session 22c · A3 — done (12 Nov 2026)
A3 (PRs #119 and #120, D-160): the apt step hardened, the PDF diff compares every edition; the other speed-ups were measured and not adopted. Phase 12 closed (HISTORY.md, archive/phase-12-audits/).

### L2 — done early (12 Nov 2026)
L2 (PR #121, D-161): `data/hidden.txt` and `songs.published()`; every book leaves hidden songs out. J2 selects the songs of `songs.json` with the same function.

### Session 23 · J0a, J1 — done (12 Nov 2026)
J0a (PR #123, D-163): the song structure the converter reads, fixed in 22 songs. J1 (PR #124, D-164): the converter `tools/songbook/` with `tools/convert.py`, a `make check` and CI step; 20 more songs fixed for it. Next: session 24 (J2, J3).

### Session 24 · J1a, J2, J3 — done (12 Nov 2026)
The owner reviewed the shape of `songs.json` on two songs next to their PDF pages and the awkward cases (D-165). J1a (PR #126): `pianoman`'s bass notes as `\bas`, plain ones are a converter error. J2 (PR #127): `make json` writes `build/songs.json` from the full book; `endsInWord` verified against TeX on every chord. J3 (PR #128): `tools/songs.schema.json`, tested with `jsonschema` pinned in `requirements-dev.txt` (an exception to TICKETS rule 4 for tests and CI). Next: session 25 (J4).

### Session 25 · J4 — done (12 Nov 2026)
J4 (PR #129, D-166): CI builds `songs.json` after the compile and validates the whole file with `tools/validate_songs_json.py` (`make json` does too); `release.py` stages `songs.json` and `scores.zip` (the 22 score SVGs) beside the PDFs and the release takes `build/release/*`. Pull requests build and validate; only a push to `master` releases. Next: session 26 (W1, W2), once the merge of this PR has made the first release with the new assets.

### Session 26 · W1, W2 · Sonnet · `zpevnik-web`
- **Needs:** J4 released at least once: the release after the merge of PR #129 holds `songs.json` and `scores.zip`; check the release page before starting.
- **Read:** DECISIONS D-103, D-110, D-123, D-165 (the shape of `songs.json`; `tools/songs.schema.json` is the contract) · PLAN WP6 · zpevnik-web README.
- **Notes:** The PDFs already come from the release (E6); W1 adds `songs.json`. The download page at `/` must look and work as before. The songbook lives under `/zpivej/` (D-167). W2 implements the chord rule in CSS and must read well without JavaScript.

### Session 27 · W3–W7 · Sonnet · `zpevnik-web`
- **Needs:** W2, L1.
- **Read:** DECISIONS D-006, D-103, D-107 · PLAN WP6.
- **Notes:** The index order must match the PDF exactly (it comes from `songs.json`, never re-sorted in the web build). The search index needs no library unless it is tiny.
- **Progress:** W3 is done (zpevnik-web PR #6, D-168). W3a (two levels of navigation, D-169, zpevnik-web PR #7) came after it at the owner's request and is done. W4 (search, D-170, zpevnik-web PR #8) is done, and W4a (the search from the start of words, versioned URLs, D-171, zpevnik-web PR #9, done) W3b (a way up from a song, D-172, zpevnik-web PR #10, done) and W4b (search results in groups, D-173, zpevnik-web PR #11, done) followed it at the owner's request. W5 (the wake lock, D-174, zpevnik-web PR #12), W6 (`robots.txt`, PR #13) and W7 (the release check `check_site.py`, PR #14) are done, each its own PR, after the one before was merged. W6a (the chord wrapping) was left optional by the owner.
