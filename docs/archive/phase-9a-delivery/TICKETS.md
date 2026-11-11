# Phase 9a tickets (done 11 Nov 2026)

The ticket texts and status rows of the delivery phase as they were when it ended. Summary: [HISTORY.md](../../HISTORY.md), phase 9a.

| Ticket | Status | Notes / PR |
|---|---|---|
| E5 | done | CI and release for every edition, found not listed (D-149): PR #106; the release step is first seen on the merge |
| E6 | done | the download page shows the editions from the release; the songbook CI no longer commits the PDF (D-150): PRs f-hluchnik/zpevnik-web#3 and f-hluchnik/zpevnik#107; `zpevnik-lidovky` can be archived by the owner |

### E5 · CI and release for every edition — [agent] · M · needs E3, E7
D-139, D-143, D-147. The editions are found, not listed: `edition_names()` in `tools/edition.py` is the one place that says what an edition is (a folder in `editions/`), so adding an edition is adding a folder, with no change to the CI (owner, 11 Nov 2026).
1. `tools/build_edition.py --list` prints the edition names, one per line (from `edition_names()`; no second rule in YAML).
2. CI builds every edition on pull requests, in one run of the TeX Live step (a loop, not a container per edition), and runs the one-page, chord and link checks on each; the build, the one-page check and the link check must pass.
3. On pushes to master the release gets `zpevnik-<edition>-<version>.pdf` of each edition, the full book included (`zpevnik-full-<version>.pdf` replaces `zpevnik.pdf`; nothing reads the old name until E6), with the build version (D-143); the release notes list the editions with their song counts.
4. The PDF diff keeps comparing the full book only.
5. Czech README section on editions: how to make one (by song ids or by artist), how to add a song to one, and that an uncommitted edition folder is a private edition built only locally.
**Verification:** the PR run shows the loop and the checks for `full` and `lidovky`. The release step runs only on a push to master, so its first real run is the merge: read that run before claiming anything about it, and say so in the PR. **Expected differences:** none in the book.

### E6 · Download page with editions — [agent] · M · needs E5 released once · `zpevnik-web` (and a small PR in `zpevnik`)
D-139, D-110, D-147. The website gets the PDFs from the release (this takes over the PDF half of W1): `build.py` downloads the PDFs of the release tagged `v<version.txt>`; the songbook CI stops committing the PDF into `zpevnik-web` and only writes `version.txt`. Which editions the page shows, and how, is configured in `zpevnik-web` (the songbook has no `publish` flag).
- The full book is the main button and is also served at its fixed URL `zpevnik_last.pdf` (printed QR codes point to it); only that URL must stay fixed.
- `lidovky` is the edition from the release; it replaces the committed `static/files/zpevnik_lidovky.pdf` (the 2020 book, 2.2 MB). That is the website's only tie to the old repository `zpevnik-lidovky`, so after this the owner can archive it (he does it himself, once the page is live and the button works).
- The koledy songbook stays a static file in its own section.
- `zpevnik-lite` takes over the main button when it exists (E4, after the print edition); then adding it is one line of configuration.
- The committed `zpevnik_last.pdf` and `zpevnik_lidovky.pdf` leave the repository (not its history); the `zpevnik-web` README ("Updating the PDFs") is rewritten.
- Two PRs (`zpevnik-web` and the small one in `zpevnik`); the merge order matters, say it in both.
Earlier notes said the owner had an uncommitted change in `templates/base.html` (6 Nov 2026). His working copy was clean on 11 Nov 2026 (and five releases behind `origin`), so ask only if `git status` shows one again.
