# How the songbook works

How the system is built today, and why. Each choice says what was decided and the reason,
not when or by whom.

**Keep it true.** A change of behaviour edits this file in its pull request: new text replaces
the old, and git keeps the history. The record of the 2026 refactoring (its decision log,
plans, tickets and phases) is frozen in [archive/](archive/README.md), for reference only.

Related: [README.md](../README.md) (in Czech: setup, writing songs, commands),
[printing.md](printing.md) (printing an edition), [tools/README.md](../tools/README.md) (every
tool), and the `zpevnik-web` README (the website).

## The parts

Three kinds of thing, kept apart:

| Kind | Where | Rule |
|---|---|---|
| **Source** | `songs/`, `data/`, `editions/`, `scores/`, `shared-pages/`, `zpevnik.tex`, `zpevnik.sty` | The only things a person edits. |
| **Build output** | `build/` | Made by `make`, never committed, safe to delete (`make clean`). What a printer gets is in `build/print/`. |
| **Release** | GitHub release `v<version>` | What the website uses: one PDF per edition, `songs.json`, `scores.zip`. |

```
songs/*.tex ──┬─ tools/generate.py ─► build/editions/<e>/generated/ ─┐
data/         │   (song list, contents, artist index, version)        ├─ latexmk ─► zpevnik.pdf ─┐
editions/<e>/ │                        zpevnik.tex + zpevnik.sty ─────┘                          │
scores/*.mscz ┼─ tools/scores.py (MuseScore) ─► build/scores/ (PDF for TeX, SVG for the web) ─┤
              │                                                                               ├─► release
              └─ tools/songbook/ (converter) ─► songs.json ◄── page numbers from the PDF ─────┘
                                                                                                  │
            zpevnik-web: version.txt names the release ─► build.py ─► HTML ─► GitHub Pages ◄──────┘
```

## Songs

- **One file per song** in `songs/`, LaTeX with the commands of `zpevnik.sty`. A song says
  *what* (a chord, a verse, a pause, an artist), never *how far apart*. That keeps the layout
  consistent and lets the converter read meaning instead of millimetres.
- **A song compiles alone** with the style file (`song-template.tex`), as on Overleaf. An
  unknown artist then simply prints nothing.
- **Artists** are named by slug (`\artist{slug}`); `data/artists.toml` holds their names, sort
  keys and whether they have a section. An artist with a section needs at least one song.
- **Hidden songs** (`data/hidden.txt`, with the reason for each) are left out of every book and of
  `songs.json`, by one function (`songs.published`).
- **Order** is the Czech collation of the title (ČSN 97 6030, implemented in
  `tools/collation.py`), never the file name. It does not depend on the machine's locales.
- **One song, one page; one source line, one printed line.** A line slightly too long is
  squeezed by its spaces; one that cannot be squeezed fails the build, so whoever writes the song
  splits it where it makes sense. Letters are never narrowed: pdfTeX's font expansion (the
  `microtype` package, at most 2 %, only in song paragraphs) was tried and works, but the simpler
  book was chosen; it is the way to go if many lines ever need it. Songs that may take two
  pages, or have no chords, are listed in `data/multipage-allowlist.txt` and
  `data/no-chords-allowlist.txt`.

## The book

- `zpevnik.tex` is the book's frame; `zpevnik.sty` holds every command, ordered by topic, with
  the reason in each comment and internals under `\zp@`.
- **Generated files are made at build time** (`tools/generate.py` into
  `build/editions/<edition>/generated/`): the song list, the include list, the contents by letter
  and by artist, the version, the front matter's facts. They are never committed, so they cannot
  go stale.
- **TeX Live is pinned to 2023** in CI. The layout changes between TeX Live years (a song spilled
  onto a second page once), so every comparison is made with the same year.
- **Formats** are TeX macros the build defines before the document (`tools/formats.py`):
  `screen` (links, red chords), `print` (no links; page numbers instead), `print-black` (the
  same in black ink only: black chords and black-ink score images). A format never changes the
  songs, the front matter or the page size.

## Scores

`scores/*.mscz` are exported by MuseScore (`tools/scores.py`, the version pinned in CI) with one
shared style (`scores/zpevnik.mss`) and the songbook's chord list, so that B-flat prints as B.
Each score gives a PDF for TeX and an SVG for the website: the same image in both. For black ink,
Ghostscript makes a grey copy of each PDF.

## Editions

Every book is an edition: `editions/<name>/edition.toml`, the full book too (`editions/full/`).

- **Selection:** `all = true`, or `songs` (ids) and/or `artists` (slugs).
- **Front matter:** each of the cover, half-title and title page is `shared` (`shared-pages/`) or
  the edition's own file. An edition can add an `imprint` fragment, pages `before_songs` and
  pages `after_contents`. Every `.tex` file in the folder must be referenced, so a misspelt name
  fails.
- **Book facts** every edition shares (title, author, years, source) are in `data/book.toml`.
- The imprint of an edition other than the full book says it is a selection; it does not count
  its songs.
- CI builds, checks and releases every edition; a new folder needs no change anywhere else.

## Print

`make print EDITION=<e>` makes the book block for the edition's printer, as the `[print.block]`
table of its `edition.toml` asks ([printing.md](printing.md) lists the keys).
Every key has a default, so every edition can be printed. The block goes to
`build/print/<e>/zpevnik-<e>-<version>-blok.pdf`; the printer gets nothing from anywhere else.

- **One build, a few switches.** The book is typeset on A4 in a format (`tools/formats.py`)
  that follows from the table: `print-black` (black ink), `print` (colour, RGB) or `print-cmyk`.
  It is checked like `make check` checks the screen PDF, then placed on the paper by a small
  pdfpages document (`tools/print_pdf.py`). The page size never changes in TeX, so a song fits
  its page in every format.
- **Margins on the ink:** every page is rendered at 300 dpi and its ink measured; the largest
  scale and the shift away from the spine that keep both margins on every page are computed
  (`tools/print_layout.py`), never above the paper's own (1 for A4, 1/√2 for A5). The finished
  PDF is measured again, against its exact trim box.
- **The page:** crop marks (the `crop` package) on a page with 15 mm round the trim, or the
  bleed alone; the PDF names the trim box and the bleed box.
- **CMYK without converting the PDF.** Only the chords have a colour. Their red is converted
  once with the edition's profile (FOGRA39 from TeX Live by default) by littleCMS through Pillow
  (`tools/colours.py`) and typeset as a CMYK colour; the scores use their black-ink images.
  Converting the finished PDF with Ghostscript was rejected: its PDF writer ignores the profile it
  is given and uses its own.
- **Black ink** is checked with Ghostscript's ink coverage on every page; a black-ink or CMYK
  block may hold no RGB image, and every font must be embedded.
- **The cover:** `cover = false` leaves the book's cover and its back out of the block at TeX
  level (`\zpprintwithoutcover`), so the pages count from the half-title as in a printed book.
  The cover of `skaut-kravare` is built by hand from `editions/skaut-kravare/print-cover/` (its
  README). It is being moved into `make print`, configured by a `[print.cover]` table like the
  block.

## Version and release

- **The version names a build:** `major.minor` is the song count + 100 (738 songs: 8.38),
  `patch` the number of first-parent commits since the song count last changed
  (`tools/build_version.py`). It comes from git, so CI and a local build agree.
- **Every push to `master` is a release** `v<version>`: one PDF per edition
  (`zpevnik-<edition>-<version>.pdf`), `songs.json` and `scores.zip`. A tag is never overwritten;
  CI fails before publishing if it exists.
- **The website is told by two files** CI pushes to `zpevnik-web`: `version.txt` (the release to
  build from) and `previous-version.txt` (the release before the song count last changed, for
  the website's "Jaké písničky přibyly?" comparison). The website commits no PDFs; it downloads
  them from the release.

## The website contract

- **`songs.json`** holds the full book's published songs in book order, with their pages in the
  screen PDF, the contents and the artists. It is written by `tools/songs_json.py` from the
  converter's model (`tools/songbook/`, the one reader of the song files) and checked against
  `tools/songs.schema.json` in every CI run, so a change that would break the website fails its
  own pull request.
- **Any change of the shape** raises `schemaVersion` and changes the schema in the same pull
  request; the website reads only the version it knows.
- **The online songbook** lives at `/zpivej/` on the website. It never sorts: the order of the
  songs, the contents and the artists comes from `songs.json`, written by the same functions as
  the book's contents.

## Checks

`make check` runs what CI runs on a build, and CI adds the comparison with the base:

| Check | Catches |
|---|---|
| unit tests (`tools/tests/`) | a broken rule of the tools |
| `tools/lint.py` | a bad song, registry entry or edition definition |
| `tools/convert.py` | a song the converter cannot read, with file and line |
| link check in `tools/build_edition.py` | a link or page reference that points nowhere |
| `check_pages.py`, `chord_gaps.py`, `song_lines.py` | a song on two pages, overlapping chords, a wrapped line |
| `validate_songs_json.py` | `songs.json` breaking the contract |
| song-by-song PDF diff (`tools/pdfdiff.py`, CI) | every visible change of every edition, against the base commit |

**A unit test earns its place** when it protects a rule or a failure that no other check catches,
and asserts behaviour (an order, a choice, an error), not an exact TeX string or an internal name,
unless that string is a contract.

## Conventions

- **Tools:** Python 3.11+, standard library only. The tests and the check of `songs.json` also
  use `jsonschema`, and a CMYK print Pillow (`requirements-dev.txt`).
- **Language:** code, comments, commits and these docs in English; the README in Czech.
- **Changes** reach `master` only through a pull request. Its description states the *expected*
  differences of the PDFs and the *actual* ones the CI diff shows.

## Deliberately not done

The songbook aims to be correct and simple, not to have every feature:

- **Setlists:** not needed.
- **Offline use:** the PDF is the offline songbook.
- **Fit to screen:** the A− and A+ buttons cover it.
- **Smaller default font on phones:** the text becomes too small to sing from.
- **Transposition:** it would contradict the score images, capo notes and chords named in remarks.
- **ChordPro export:** a second writer of the song model, worth it only if someone uses such an app.
