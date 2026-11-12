# Phase 7 tickets: converter and `songs.json` (done 8–12 Nov 2026)

The ticket texts and status rows as they were when the work ended: the song quirks and structure, the converter, `songs.json`, its schema, the release assets and the scores. Summary: [HISTORY.md](../../HISTORY.md).

| Ticket | Status | Notes / PR |
|---|---|---|
| J0 | done | song quirks: PR #88 (D-135); scores: PR #89 (D-136) |
| J0a | done | structure the converter's grammar needs: cues, scores in a part, no `\\` at the end of a part and no empty line in one: PR #123 (D-163) |
| J1 | done | the converter `tools/songbook/` and `tools/convert.py`, a `make check` and CI step; 20 songs fixed for it: PR #124 (D-164) |
| J1a | done | bass notes written as plain text (`C/G`, 14 chords of `pianoman`) are `\bas{}`, and the converter rejects them (D-164): PR #126 |
| J2 | done | `tools/songs_json.py` and `songbook/export.py` write `build/songs.json` (`make json`), shape agreed with the owner (D-165): PR #127 |
| J3 | done | `tools/songs.schema.json` (JSON Schema 2020-12) and its tests with `jsonschema` pinned in `requirements-dev.txt`; CI installs it: PR #128 (D-165) |
| J4 | done | CI builds `songs.json` and validates the whole file against the schema on every run; a push to `master` releases `songs.json` and `scores.zip` (the score SVGs) with the PDFs (D-166): PR #129 |
| J5 | done | done with J0's scores (D-136): PR #89 |

### J0 · Song quirks before the converter — [you] + [agent] · M · needs nothing
The converter is strict (an unknown macro is an error), so every remaining special case in the songs needs a decision first: give it a semantic command, let the converter ignore it as PDF-only layout, or keep it and say how the converter treats it. The agent re-derives the list with grep at the start and the owner decides each item; then the agent implements the agreed commands (zero diff where possible).
1. **Score images** (owner: agreed): 15 songs place a score by hand (`\vspace{-25…-58pt}`, `\hspace{20pt}`, `21pt` or `9mm`, `\includegraphics[width=…]`); only 2 have a `% KEEP` comment. A `\score[offset]{file}` command: the indent is one constant inside it, the per-song vertical offset an explicit optional argument (until J5's trimmed export makes it one constant), the converter reads one command. Zero diff.
2. **Echo and backing vocals** as `\textsuperscript{\Large\emph{…}}` (`kratkypopisleta`) or `\textsuperscript{\emph{…}}` (`dvakrat`): a command such as `\echo{…}`, or leave them as formatting.
3. Layout in a few songs: `multicols` and `\columnbreak` (cernymuz, lojzaaliza, milionar, promeny, zkratky), `\placetextbox` (vosa), the negative `\hspace` inside `\rep` (velicenstvokat), `center` (jedesohajzvidna, kolenasejchalupecky), `\note{\small …}` (jednourano): PDF-only layout the converter skips, or a semantic form (e.g. `columns` in `songs.json`).
4. `zapomnetliva`: the repeat mark stands before the speaker name (nitpick left from Q5).
5. Anything else the strict parser of J1 would reject; footnotes in `\song{}` stay (Q5).
**Decided (owner, 8 Nov 2026):** items 2–5 and the rest of the list in D-135; item 1 together with J5 (a standard MuseScore export that places itself, no per-song offsets).

### J0a · Song structure before the converter — [agent] + [you] · S · needs J0
Found while designing J1 (session 23): J0 listed the macros, environments and math in the songs, but not their structure, which TeX accepts silently and only a parser sees. The owner decided each fix and reviewed the before/after pages; the rules are in D-163.
1. A brace closing a part in the wrong place (`idzepostaridze`: verse 2 contained the next part); a pause inside a chord (`pepita`).
2. A cue that refers to no part written before it with that label (13 cues in 11 songs).
3. A score outside a part (`batalion`, `scarboroughfaircarthy`, `svazceskychbohemu`).
4. `\\` at the end of a part (11 parts in 5 songs) and an empty line inside a part (`pohadka`, `waterlooabba`).
**Expected differences:** the songs with a changed cue, score or line break; the markup-only fixes none.

### J1 · Converter package — [agent] · **[strong model]** · L · needs Q4, Q5, J0, J0a
1. Write the converter in `tools/songbook/` as a package: parser, model, command line. It starts from scratch (the earlier `tex2json.py` prototype is in neither repository). Strict: an unknown macro is an error; it understands only the command set after Q4 (D-108, D-131).
2. Song metadata (`\artist`, `\alttitle`, `\toctitle`, `\collection`); the title and its footnote apart (Q5 item 4); `\cue` as a reference to another block; repeat marks rendered as the PDF does.
   The structure rules of D-163 are errors of the converter, and the whole-book parse is a `make check` step.
3. Tests: snapshot tests for 10 songs plus a whole-book parse that must succeed for all songs in under 5 s.

### J1a · Bass notes as `\bas` — [agent] · S · needs J1
Found in session 24: `pianoman` wrote 14 bass notes as plain text (`C/G`), printed on the base line unlike every `\bas{G}`; the JSON would have two forms of one thing. The songs use `\bas{}`, and a slash right before a note name on a chord's base line is a converter error (`\add{6/9}` and `1. E\7 / 2. C` stay text).

### J2 · Assemble `songs.json` — [agent] · **[strong model]** · M · needs J1
Top level: `schemaVersion`, `version`, `songs[]` in book order (the generated include order), `artists[]` from the registry. Each song: `id`, `title`, `altTitles`, `artists`, `collections`, `subtitle`, `see` (from `\seealso`), `order`, `page` (from the page checkpoints), `footnotes`, `images`, `columns`, `blocks[]` (lines of chord/text segments). This list predates the converter: the shape comes from its model (D-164), whose body also has cue blocks, notes, rules and speaker blocks, and whose scores are marks in the lines. **Done:** the agreed shape is D-165. **Hidden songs (L2, D-161):** select the songs with `songs.published()`, like the generator, so a hidden song is not in `songs.json`.

### J3 · JSON Schema — [agent] · **[strong model]** · S · needs J2
`tools/songs.schema.json` (JSON Schema 2020-12) for the shape of D-165; validate the output in tests and in CI with `jsonschema`, pinned in `requirements-dev.txt` (D-165: an exception to rule 4 for tests and CI only; the README's setup installs it, `make check` stops with a clear message without it).

### J4 · CI and release asset — [agent] · M · needs J3
The converter already runs in CI (J1). J4 builds `songs.json` after the compile (`tools/songs_json.py`) and validates the whole file against `tools/songs.schema.json` with `jsonschema` (about 5 s; the unit tests validate only the snapshot songs, D-165); on pushes to master it adds `songs.json` and the score SVGs (`build/scores/*.svg`, one zip, D-136) to the `files:` of the release step. PRs only validate.

### J5 · Scores from MuseScore — [agent] + [you] · M · needs J4
**Done together with J0 item 1 (D-136), 8 Nov 2026:** the export is `tools/scores.py` with a shared style, the PDF uses the converted SVG, and every score places itself with `\score{name}`. J4 put the SVGs (`build/scores/*.svg` since E2, D-143) into the release as `scores.zip` (D-166); `songs.json` names each by its `score` items. The text below is the original plan.
The `.mscz` files are the source; CI exports the images, so the PDF and the web use the same export (D-125). A score is a single page by principle.
1. **Prototype first and report before building on it:** a pinned MuseScore 4 in CI with `-o file.svg -T 0` (trimmed SVG, documented for single-page scores only). pdfLaTeX cannot include SVG, so for the PDF either convert the SVG (e.g. `rsvg-convert`) or export a PDF and crop it with `pdfcrop`. Compare a few results with today's images.
2. One `.mscz` per image. Missing (5 Nov 2026): `tickettoride` uses `ticket_to_ride_intro.png`, which has no source. These `.mscz` produce more than one image today: `morseovka.mscz` (`morseovka_1.png`, `morseovka_2.png`), `pohadka.mscz` (`pohadka.pdf` and `pohadkaref.pdf`), `reddwarftheme.mscz` (intro and outro), `slunecnyhrob.mscz` (intro and solo). Unused: `morseovkasolo1–3.pdf`. The owner provides the missing files.
3. The exported images are build output (D-104), not committed; remove the committed PDFs and PNGs once the export works. The SVGs go into the release as one zip and are referenced from `songs.json`.
4. The `\vspace` and `\hspace` next to scores stay (D-124), but check them against the new crop.
**Expected differences:** small shifts of the score images; the owner reviews them.
