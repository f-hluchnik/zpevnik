# How it works: one song, from file to screen

A map of the whole system for its owner, and a trace of one real song through it: `songs/folsomprisonblues.tex`. Read this first; the other docs say *what was decided and when* ([DECISIONS.md](DECISIONS.md), [HISTORY.md](HISTORY.md)), this one says *how the parts fit together*. The module-by-module list is [tools/README.md](../tools/README.md); the website's own model is in the `zpevnik-web` README (*The mental model*).

Written on 12 Nov 2026 from `zpevnik` master `9ac19fc` and the release `v8.38.38`; numbers such as page 146 move as songs are added.

## The map

Three kinds of thing, and the whole design is keeping them apart:

| Kind | Where | Rule |
|---|---|---|
| **Source** | `songs/*.tex`, `data/` (artists registry, book facts, hidden songs), `editions/<name>/`, `zpevnik.sty`, `zpevnik.tex` | The only things a person edits. Song files say *what* (a chord, a verse, an artist), never *how far apart*. |
| **Build output** | `build/` (and `generated/` inside it) | Made by `make`, never committed, safe to delete (`make clean`). |
| **Release** | GitHub release `v<version>` of `zpevnik` | What the other repository consumes: one PDF per edition, `songs.json`, `scores.zip`. |

```
songs/*.tex ──┬─ tools/generate.py ─► build/…/generated/*.tex ─┐
data/*.toml   │   (contents, song list, version, front matter)  ├─ latexmk ─► zpevnik.pdf ─┐
editions/     │                                  zpevnik.tex    ┘  (TeX Live 2023)         │
zpevnik.sty ──┘                                  + zpevnik.sty                             ├─► release v8.38.38
              │                                                                            │   (PDFs, songs.json,
              └─ tools/songbook/ (converter) ─► songs.json ◄── page numbers from the PDF's ┘    scores.zip)
                                                                                              │
                          zpevnik-web: version.txt names the release ─► build.py downloads it ┘
                                                  ─► dist/ (HTML) ─► GitHub Pages
```

Two repositories, one contract. `zpevnik` knows nothing about HTML; `zpevnik-web` knows nothing about LaTeX. Between them is `songs.json`, described by `tools/songs.schema.json` and validated in `zpevnik`'s CI, so a change that breaks the website fails the songbook's pull request, not the website's next build.

## The trace

### 0. The song file

```tex
\song{Folsom Prison Blues} \artist{johnnycash}      title, and a slug into data/artists.toml
\seealso{bluesfolsomskeveznice}{Blues folsomské věznice}   a link to another song
\note{capo 1}                                       belongs to the block that follows

\vers[1]{                                           a numbered verse: label "1."
I \chord{E}hear the train a-coming, it's rolling round the bend\\
and I ain't seen the sunshine since \chord{E\7}I don't know when.\\
…
}
```

The file name (`folsomprisonblues`) is the song's id everywhere: in the include list, in `\seealso`, in `songs.json`, in the URL `/zpivej/folsomprisonblues/`.

### 1. `tools/generate.py`: from files to lists

`make` first runs the generator (`python3 tools/generate.py --edition full`). It reads every song's header (`songs.py`, a few regexes), the registry (`registry.py`) and the edition (`edition.py`), drops songs listed in `data/hidden.txt` (`songs.published()`), and writes TeX into `build/editions/full/generated/`:

- `include.tex`: one `\songinclude{id}` per song, in **Czech collation order** (`collation.py`: CH after H, a space before any letter). Our song lands in section F. The order is never typed by hand.
- `song-list.tex`: the songs of the edition, so a `\seealso` to a song *outside* an edition prints nothing instead of a dead link.
- `artists.tex`, the letter contents, the artist index, `version.tex`, the front matter.

The version is `major.minor.patch`: song count + 100 gives 738 + 100 → `8.38`; the patch counts commits since the song count last changed (`build_version.py`).

An **edition** is just a filter over the song list plus its own front matter (`editions/full/`, `lidovky`, `skaut-kravare`). The full book is one of them.

### 2. TeX: `zpevnik.tex` and `zpevnik.sty`

`zpevnik.tex` is short: cover, title pages, then `\input{generated/include}` which `\include`s every song, then the contents. All the typography is in `zpevnik.sty`.

- `\vers[1]{…}` becomes a block: a bold label in a fixed-width column (`\labelw`), the lines beside it. `\\` ends a line.
- `\chord{E}` has zero width and sits above the text that follows it. The macro reads the text up to the next chord, measures it and widens the gap **only where two chords would collide**: a chord and its text take `max(text width, chord width + 0.5em)` (D-123). This is why no song contains hand-made spacing.
- CI fails if a song takes more than one page (`check_pages.py`) or two chords overlap (`chord_gaps.py`).

### 3. The converter: `tools/songbook/`

The converter reads the **same `.tex` file** and builds an in-memory model of it, strictly: an unknown macro or a structure it does not understand is an error with file and line, never a guess. Stages: `lexer` (tokens) → `stream` → `parser` (the song level: blocks, notes, rules) → `inline` (lines, chords, text) → `model` → `export` (the shape of `songs.json`). `python3 tools/convert.py --song folsomprisonblues` prints the model.

For our first line, `I \chord{E}hear the train…` becomes two **segments**: one with no chord and the text `I `, and one with chord `E` and the text `hear the train a-coming, it’s rolling round the bend`. Along the way `'` becomes `’`, and `E\7` becomes the parts `E` (base) and `7` (superscript). A segment is exactly what `\chord` measures: a chord and the text up to the next chord.

### 4. `tools/songs_json.py`: the contract

`make json` writes `build/songs.json` from the built full book. The page numbers come from the book's `.aux` files, so the book must be built from exactly the same songs (otherwise it stops with an error). The file holds `schemaVersion`, `version`, `songs[]` (738), `contents[]` and `artists[]` in book order, so the website never sorts. Our song in `v8.38.38`:

```json
{"id": "folsomprisonblues", "page": 146, "artists": [{"slug": "johnnycash", "label": null}],
 "see": [{"id": "bluesfolsomskeveznice", …}],
 "body": [{"type": "note", …},
          {"type": "block", "kind": "verse", "label": "1.", "lines": [
            {"items": [
              {"type": "segment", "chord": null, "lyrics": [{"type": "run", "text": "I "}], "endsInWord": false},
              {"type": "segment", "chord": [{"text": "E", "position": "base"}],
               "lyrics": [{"type": "run", "text": "hear the train a-coming, it’s rolling round the bend"}], …}]}, …]}, …]}
```

It carries meaning and no layout: no millimetres, no pixel widths.

### 5. CI releases it

`.github/workflows/build-and-publish.yml` runs on every pull request and on every push to `master`. In order: list editions, generate, unit tests (309), lint, converter on every song, export the scores with MuseScore, compile every edition (TeX Live 2023), one-page and chord-overlap checks, build and validate `songs.json`, the test documents, and on pull requests the **song-by-song PDF diff** against the base commit. Only on a push to `master`: compute the version, create the release `v8.38.38` with the PDFs, `songs.json` and `scores.zip`, and then write the version into `version.txt` of `zpevnik-web` and push it. The order matters: the web never points at a release that does not exist yet.

### 6. `zpevnik-web`: from JSON to HTML

That push to `zpevnik-web` starts its workflow (`deploy.yml`). `build.py` reads `version.txt`, downloads `songs.json`, `scores.zip` and the PDFs of that release, checks `schemaVersion`, and renders Jinja templates into `dist/`: one page per song, the index, artists, the search index. Our segment becomes (`templates/_song.html`):

```html
<span class="segment"><span class="lyrics">I </span></span><span class="segment"><span class="chord">E</span><span class="lyrics">hear the train a-coming, it’s rolling round the bend</span></span>
```

`static/songbook.css` implements the **same chord rule** as TeX: `.segment` is an `inline-block`, `.chord` has `padding-right: 0.5em`, so the column is as wide as the wider of text and chord + separator. No JavaScript is involved. After the build, `check_site.py` fails if a song has no page or a link leads nowhere; `main` is then deployed to GitHub Pages.

## Where the weak points are

Already tracked:

- **The converter is a second reader of the song files**: `songs.py` still reads the same files with regexes (TICKETS.md, backlog *One reader of the songs*, D-164).
- **Not verified on real devices**: the wake lock, the search keyboard, `#page=N` in a phone's PDF viewer (HISTORY.md, phase 9).
- **Chords wrap oddly on a narrow screen**: the chord rule is implemented twice, in TeX (`zpevnik.sty`) and in CSS, by design (D-123 on the web). A browser moves a chord-and-text `inline-block` to the next line whole, where TeX breaks at any space. This is W6a, optional (TICKETS.md).

Not tracked anywhere: **nothing automated compares the web layout with the PDF.** The PDF is protected by the PDF diff and the overlap check; `check_site.py` checks that pages exist and links resolve, not how a line looks. W6a's own verification is by hand (screenshots, measuring in a browser), so a change to `songbook.css` or `_song.html` could break the rule on the web unnoticed. Whether that is worth a ticket is the owner's call.

## Where to look when…

| Problem | Start here |
|---|---|
| A chord is misplaced or overlaps in the PDF | `\chord` in `zpevnik.sty`, `tests/chords.tex`, `tools/chord_gaps.py` |
| A song is in the wrong place in the contents | `tools/collation.py`, `data/artists.toml` |
| A new song fails `make check` | the message names file and line: `tools/lint.py`, `tools/convert.py`, the grammar in `tools/songbook/grammar.py` |
| A song is missing from the website | `data/hidden.txt`, `tools/songs_json.py`, `check_site.py` in `zpevnik-web` |
| The web looks different from the PDF | `static/songbook.css`, `templates/_song.html` |
| The wrong version is published | `tools/build_version.py`, the release steps of the workflow, `version.txt` |

## Try it yourself

These run without TeX (Python 3.11 or newer; the tests also need `jsonschema`, see the README):

1. `python3 tools/convert.py --song folsomprisonblues` and compare the output with the song file, line by line.
2. Add a made-up macro to a copy of the song (`\foo{x}`) and run the converter again: the error names the line.
3. `python3 -m unittest discover -s tools`: the 309 tests of the tools.
4. Website: download `songs.json` and `scores.zip` of the latest release, then in `zpevnik-web` run `python build.py --songs-json songs.json --scores-zip scores.zip` and `python check_site.py --songs-json songs.json`, and open `dist/zpivej/folsomprisonblues/index.html`.

With TeX installed (README, *Nastavení lokální kopie*): `make song SONG=folsomprisonblues` builds that one song into `build/songs/`.
