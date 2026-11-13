# Tools

The Python tools that generate, build and check the songbook: Python 3.11 or newer, standard library only; the tests and `validate_songs_json.py` also need `jsonschema` from `requirements-dev.txt` (setup in the main README, *Nastavení lokální kopie*). They run from the repository root. This page says what each module is for and who runs it; how it works is in the module's docstring, and every command prints its options with `--help`.

## Commands, run through `make`

You normally run these through `make` (the main README, *Příkazy*); each also runs alone as `python3 tools/<module>.py`.

| Module | Run by | What it does |
|---|---|---|
| `generate.py` | `make`, `make generate` | Writes the generated TeX of an edition (song list, contents, artist index, version, front matter) into `build/editions/<edition>/generated/`. `--version` prints the songbook version. |
| `scores.py` | `make`, `make scores` | Exports the MuseScore scores (`scores/*.mscz`) as images into `build/scores/`, skipping those that are up to date. |
| `build_edition.py` | `make` | Compiles an edition with latexmk and prints the path of its PDF. CI also uses `--list` to find the editions. |
| `build_song.py` | `make song SONG=<id>` | Compiles one song alone into `build/songs/<id>.pdf`, the way Overleaf would. |
| `print_pdf.py` | `make print` | Scales an edition's print format to A5 for a printer. |
| `lint.py` | `make check` | Checks the songs, the artists registry, the edition definitions and the lists in `data/`. Errors fail, warnings are only listed. |
| `convert.py` | `make check` | Reads every song with the converter (`songbook/`) and fails on anything it does not accept, with the file and line. `--song <id>` prints the model of one song as JSON. |
| `songs_json.py` | `make json` | Writes `build/songs.json` for the website (D-165): the full book's published songs in book order with their pages, the contents and the artists. Needs the built full book, which `make json` builds first. |
| `validate_songs_json.py` | `make json`, CI | Checks the whole `build/songs.json` against `songs.schema.json` and prints where it breaks the contract (D-166). The only tool that needs `jsonschema`. |
| `songs.schema.json` | the tests, `validate_songs_json.py` | The JSON Schema of `songs.json`, the contract with the website (D-165). A change of the shape changes it and `SCHEMA_VERSION` in `songs_json.py` in the same PR. |
| `check_pages.py` | `make check`, after the build | Fails if a song takes more than one page, unless `data/multipage-allowlist.txt` lists it. |
| `chord_gaps.py` | `make check`, after the build | Fails if two chords on the same line overlap. |

## Commands, run by CI

These are run by `.github/workflows/build-and-publish.yml`. You run them yourself only to debug CI.

| Module | Run by | What it does |
|---|---|---|
| `pdfdiff.py` | CI, pull requests | Compares the PDF of every edition with the PDF before the change, song by song and page by page; the result goes to the run summary. Locally it needs two built checkouts (`--base`, `--head`). |
| `release.py` | CI, every build; the release only on push to `master` | Copies each edition's PDF under its release asset name into `build/release/`, adds `songs.json` and `scores.zip` (the score SVGs) for the website (D-166), and prints the editions part of the release notes. |

## Library modules, never run directly

| Module | What it holds |
|---|---|
| `paths.py` | Where things live in the repository, and the `--edition` and `repo-root` arguments the commands share. |
| `songs.py` | Reading `songs/*.tex` with the converter (`songbook/`, the one reader of the songs, D-164); `published()` leaves the hidden songs out. |
| `registry.py` | The artists registry (`data/artists.toml`): loading, defaults and validation. |
| `edition.py` | The book facts (`data/book.toml`) and the editions (`editions/<name>/edition.toml`): reading, validation and the song selection. |
| `edition_tex.py` | The generated TeX of an edition's front matter. |
| `formats.py` | The output formats (`screen`, `print`, `print-black`) and the `--format` argument. |
| `letter_toc.py` | The letter part of the contents. |
| `artist_toc.py` | The artist part of the contents. |
| `collation.py` | The Czech collation of song titles. |
| `tex_text.py` | Escaping plain text as TeX. |
| `songbook/` | The converter (D-164): reads a song into an in-memory model, strictly. A package: `lexer`, `stream`, `grammar` (every command a song may use), `parser` (the song level), `inline` (lines, chords, text), `chords`, `model`, `dump` (the model as JSON for reading and snapshots), `export` (a song in the shape of songs.json), `errors`. |
| `allowlist.py` | Reading a list of song ids (`data/hidden.txt`, `data/multipage-allowlist.txt`, `data/no-chords-allowlist.txt`). |
| `build_version.py` | The patch number of the version, counted from the Git history. |

The data the tools read (the registry, the book facts, the hidden songs and the two allow-lists) lives in `data/`, not here.

## Unit tests

`tests/` holds the unit tests, one `test_<module>.py` per module that has them. `make check` and CI run them all:

```
python3 -m unittest discover -s tools                     # all of them
python3 -m unittest discover -s tools -p test_lint.py     # one file
```

What deserves a test is decided in `docs/DECISIONS.md` (D-159). `tests/test_readme.py` checks that this page lists every module and package of `tools/`, so a new one needs a row here. `tests/songbook_snapshots/` holds the songs the converter's snapshot tests read, frozen, with the expected model.

The LaTeX tests of `zpevnik.sty` are a different thing: they live in the top-level `tests/` and CI runs them through `tests/single-song.sh`.
