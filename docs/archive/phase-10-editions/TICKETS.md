# Phase 10 tickets: editions (done 9–11 Nov 2026, except E4)

The ticket texts and status rows as they were when the work ended: the generator and the build for editions, English names, integrity checks, `lidovky`, front matter in book order. **E4** (the songs of `zpevnik-lite`) is still open and stays in [TICKETS.md](../../TICKETS.md). Summary: [HISTORY.md](../../HISTORY.md).

| Ticket | Status | Notes / PR |
|---|---|---|
| E0 | done | build version `8.33.N` (D-133): PR #93, first release v8.33.68 |
| E1 | done | D-138, superseded by D-139 |
| R15 | done | English names (D-143): PR #95; the transitional old-folder handling is listed in R16 |
| E2 | done | editions in the generator and the build (D-144): PR #96 |
| E3 | done | `\seealso` per edition, link check, lints on every edition, `make check` (D-145): PR #97 |
| E7 | done | `editions/lidovky/` with its own cover (D-146): PR #103; `zpevnik-lidovky` is archived (owner, after E5) |
| E8 | done | front matter in book order (D-143), the songs from page 9: PR #98 |
| R16 | done | the old song folder and the layout before editions dropped from the tools and CI: PR #102 |
| S4 | done | the PDF diff ignores the imprint's version line: PR #99 |

### E0 · Build version `8.33.N` — [agent] · S · needs nothing
D-133. Today every push to master replaces the PDF of release `v8.33`, whose tag still points at the source of 21 Aug 2026, and commits another PDF to `zpevnik-web`; the version names a song count, not a build.
1. `tools/generate.py` computes `major.minor.patch`: `major.minor` = song count + 100 as today; `patch` = the number of first-parent commits on the current branch since the last commit that changed the song count (Git, standard library `subprocess`). Without Git history the patch is `?` (`8.33.?`), visibly incomplete like today's `?.??` placeholder. Unit tests with a temporary Git repository.
2. The colophon prints the full version; `--version` prints it; CI validates `^[0-9]+\.[0-9]{2}\.[0-9]+$`.
3. Release step: tag `v<version>`, name `Zpěvník v<version>`; fail if the tag already exists (never overwrite or move a tag). `version.txt` in `zpevnik-web` gets the full version. The old tag `v8.33` stays.
4. README (Czech): what the three numbers mean.
**Expected differences:** the colophon page only (version line).

### E1 · Decide the editions design — [you] · S — **done**
Decided by the owner on 9 Nov 2026: **D-138**, superseded by the review **D-139** the same day (selection by song id or artist, front matter per edition, one colophon core, no edition version, the download page configured in `zpevnik-web`, the rules for links and artist sections). The owner's original answers are in the snapshot of this file in the Git history (before the PR of D-138).

### R15 · English names — [agent] · S · ⚠ · needs E0
D-143. A mechanical rename with `git mv`, nothing else: `pisnicky/`→`songs/`, `obrazky/`→`images/`, `sablona.tex`→`song-template.tex`, `preamble/`→`shared-pages/` (`obalka`→`cover`, `patitul`→`halftitle`, `titulnilist`→`titlepage`, `vydavatelskyzaznam`→`imprint`, `upozorneni`→`notice`, `dedikace`→`dedication`, `uvod`→`introduction`), `obsah.tex`→`shared-pages/contents.tex`. Update every reference (`tools/paths.py`, `zpevnik.tex`, `zpevnik.sty`, the tests, CI, the Makefile, the README, `.gitignore`, the current text of the docs; not the archive and not past DECISIONS entries). `tools/build_version.py` counts both the old and the new song folder, with a test that a renamed folder keeps the patch counting. Output paths do not change yet (E2). The owner's branch `new_songs` stays; he re-adds its songs by hand after the merge.
**Expected differences:** none; `generate.py --version` on the rename gives the previous patch + 1, not 0.

### E2 · Generator and build: editions — [agent] · M · needs R15, E1
D-139 and D-143. Zero diff for the full book (the song-by-song diff and identical rendered front-matter pages, D-143 on `/ID`); its generated `.tex` files identical to today's at their new path, except new files.
1. `data/book.toml` and `editions/<name>/edition.toml` (keys and errors as in D-143), read and validated by a small module; a unit test for each error.
2. One `Edition` type for every book; the full book is `editions/full/`. `tools/generate.py --edition <name>` (default `full`) filters the song list once (after an exclusion list, empty until L2) and writes into `build/editions/<name>/generated/`: the include list, the letter contents, the artist index and sections (the full book's rules, restricted to the artists with a song in the edition), the registry, the version, the macros and the resolved page list. The version is the build's (the full song count, D-133), never the edition's song count.
3. Generated macros: the book's title, author, start year and source; the edition's title, subtitle, editors and song count; the version; the derivation sentence (empty for the base edition). The shared pages use them instead of hard-coded text.
4. The skeleton in `zpevnik.tex`, in today's order (E8 changes it): the pages resolved by the generator from `[pages]`, `before_songs` and `after_contents`; the imprint with its core and its slot. Move the full book's dedication, introduction and credits into `editions/full/`. Remove `\setcounter{page}{8}`.
5. Build: `make [pdf] [EDITION=<name>]` creates the output directory and the subfolders LaTeX writes the per-song `.aux` files into, runs latexmk with `-outdir` and the edition (`-usepretex`), and prints the PDF's path; `zpevnik.tex` stops with an error without an edition. `make song` writes `build/songs/<id>.pdf`, the score images go to `build/scores/`, `make clean` deletes `build/`. `check_pages.py` works on any edition's output; `chord_gaps.py` stays on the full book (chord spacing depends on the format, not on the selection). CI, the release and the website copy take the full book's PDF from its new path (the release asset keeps its name until E5); the CI PDF diff also handles a base with the old layout (needed in this PR only).
Test with a throwaway edition that is not committed: songs by id, one artist, an own title page, a `before_songs` page and an imprint fragment.
**Expected differences:** none for the full book.

### E3 · Edition integrity — [agent] · S · needs E2
1. `\seealso` to a song outside the edition prints nothing and takes no space (D-139); a generated list of the songs present lets `zpevnik.sty` decide without a second pass (84 uses in 76 songs on 6 Nov 2026).
2. A link to a missing target fails the edition build: pdfTeX's warning in the log (`… has been referenced but does not exist`). Verify with the throwaway edition that it catches the contents links, `\seealso` and the artist links.
3. Run the one-page check and the lints on the edition.
4. `make check [EDITION=<name>]` (D-143, D-144): the unit tests, the lints, the one-page check and the link check of the edition; the chord check on the edition too (D-145).
**Expected differences:** none for the full book.

### E7 · `lidovky` as an edition — [you] + [agent] · S · **done** (PR #103, D-146)
All songs of the `zpevnik-lidovky` repository are already in the full book (owner, 9 Nov 2026), and the 76 songs tagged `\artist{lidove}` match the 2020 book (D-139). The agent writes `editions/lidovky/edition.toml` with `artists = ["lidove"]`, compares the result with the song list of the old repository (by title, with E4's helper) and reports any difference, and, if the old book has its own title page or foreword, adds its front matter; the owner confirms the list and the front matter, and archives the old repository himself.

### E8 · Front matter in book order — [agent] · S · needs E3
D-143. The skeleton gets the Czech book order: cover, blank, halftitle, blank, title page (a right-hand page), the imprint on its back, then `before_songs`. The songs start on page 9 instead of 8. (The `\hspace{10mm}` before the first credit went in E2, D-144.)
**Expected differences:** the front-matter pages (order, one new blank page); every page number one higher (the contents print no page numbers, only links). The song-by-song diff reports every song: check that each differs only in its page number.

### R16 · Drop the old song folder from the version — [agent] · S · needs the first song-count change after R15
D-143, D-144. Once a commit after R15 has changed the song count (the version is 8.34.0 or later), `tools/build_version.py` stops counting `pisnicky/` and its rename tests go. The other traces of the old folder and of the layout before editions, all removed here: `LEGACY_SONGS_DIR` in `tools/paths.py`, the `pisnicky/` pathspec of the *List newly added songs* step in the CI workflow, `book_output_dir`'s fallback to the root in `tools/pdfdiff.py` (a base built before E2) and the `else latexmk` branch of the *Compile base* step. (E2 already removed `songs_dir()` and the fallback of `tools/check_pages.py`.) **Expected differences:** none.

### S4 · The PDF diff ignores the version line — [agent] · S · needs E0
D-133. Since E0 the imprint prints the build's version, which counts the commits, so every PR's diff reported the imprint page as changed (base `8.33.N`, head the merge commit `8.33.N+1`). `tools/pdfdiff.py` leaves the version out like the build date: a word shaped like a version (`8.33.71`, or `8.33.?` without Git history) on the front-matter pages is masked with its line. **Expected differences:** none in the book; from this PR on, the imprint page is no longer reported unless something else on it changes.
