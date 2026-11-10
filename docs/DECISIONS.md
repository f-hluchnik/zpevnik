# Architectural decisions

Agreed decisions and their rationale. Once a decision is **Agreed**, it changes only through a new entry that supersedes it (mark the old one *Superseded by D-xxx*), never by silent editing. **Proposed** entries may still be edited until they are agreed.

Status values: **Agreed** · **Proposed** (raised, awaiting agreement) · **Deferred** (not part of this refactor) · **Superseded**.

---

## Goal of the refactor

### D-100 · Goal: PDF and an online HTML songbook, both built from the same LaTeX files — Agreed (3 Nov 2026)
The goal is to extend the website so the songbook can be read online, while the downloadable PDF stays. Both come from the same song files (D-001). The technical debt (hand spacing, hand-written TOC and include list, duplicated metadata) is paid off *before* the HTML is built, so nothing gets implemented only to be refactored later (D-108).
Out of scope: the koledy songbook (a separate project). Editions (D-102) and the print layout (D-109) were out of scope at first and came back in D-121 and D-122; the order of the remaining work is D-132.

---

## Inherited from PLAN.md ("Made / confirmed", before the 3 Nov 2026 review)

### D-001 · LaTeX song files stay the source of song content — Agreed
The 733 `pisnicky/*.tex` files are the only place where song content is authored. Everything else (TOC, include list, artist index, `songs.json`, HTML) is derived from them plus the artists registry.
*Verified 3 Nov 2026:* the website currently holds no song content (it only serves PDFs), so there is no second representation to reconcile. `songs.json` is a derived export parsed from LaTeX, not an independent source.

### D-002 · Artists registry — Agreed
One registry file lists artists and collections (slug, display name, index label, sort key, kind, whether a section exists). Song files reference artists by slug only. Format: TOML (see D-101 for a tooling caveat).

### D-003 · `\artist{}` on every song, empty allowed — Agreed
An empty or unknown slug produces no output and no error.

### D-004 · All 49 existing artist sections stay, including the 7 small ones — Agreed
New sections are created only for artists with enough songs (threshold: 3 or more, decided in session 7, D-119).

### D-005 · The Overleaf single-song workflow must keep working — Agreed
One song must compile with the style file alone. With build-time generation (D-104) an unknown artist slug simply prints nothing there.
Since H3 (D-120) the song's hypertarget comes from the generated include list, so a song compiled alone has no target (nothing links to it there anyway).

### D-006 · Website: `noindex`, no sitemap — Agreed

### D-007 · The converter lives in `zpevnik` — Agreed

### D-008 · Score PDFs are converted to SVG in CI, never by hand — Agreed; amended by D-136 (MuseScore exports SVG, CI converts it to PDF)

---

## From the 3 Nov 2026 architectural review

### D-101 · Tool runtime — Proposed
`tools/` target Python ≥ 3.11 and the standard library only (`tomllib` needs 3.11+). The CI runners have it. The Linux VM used for local verification has 3.10, so local runs there need a newer Python.

### D-102 · Editions (song subsets) — Deferred (3 Nov 2026); superseded by D-121 (4 Nov 2026)
Not a goal of this refactor. The only constraint: the generator takes an ordered list of songs as its input (today, all of them), so editions can be added later without redesign. No edition configuration is built now.
*Context:* the lidovky PDF (2020) equals today's 76 songs tagged `lidove`, so a later edition could be a tag filter.

### D-103 · The online songbook lives in `zpevnik-web`, separate from the download page — Agreed (3 Nov 2026)
One repo, one build, one GitHub Pages site and domain. The download page stays as it is at `/`; the online songbook lives under `/zpevnik/` (song pages `/zpevnik/<id>/`, artist pages `/zpevnik/interpret/<slug>/`) with its own templates and navigation. The download page links to it.

### D-104 · Generated `.tex` files are produced at build time, not committed — Agreed (3 Nov 2026)
`generated/` is gitignored. `make` runs the generator and then compiles; CI does the same. This supersedes PLAN principle 4 ("generated files are committed, CI checks they are up to date").
Consequences: the local build command changes from `pdflatex zpevnik.tex` to `make` (README); the Overleaf single-song setup needs only the style file (D-005).

### D-105 · Pin the TeX Live version — Agreed (3 Nov 2026)
Layout depends on the TeX Live release. On master `a7345a2`, TeX Live 2023 (pdfTeX 1.40.25) gives 756 pages with every song on one page; the published v8.33 PDF (CI, pdfTeX 1.40.29) has 757 pages because "I'll Be There For You" spills onto a second page. CI must use a pinned TeX Live year, and the diff baseline must be built with the same one.

*Implementation note (S1/S2, 3 Nov 2026):* S1 first pinned the 2026 image that built the published v8.33 by digest (`xu-cheng/latex-action@v3` only maps `texlive_version` 2020–2025, and `2025` = moving `latest`). A page-by-page comparison of the 2023 build with the 2026 build of the same master (S2, PR #24) found the books identical apart from `illbethereforyou` (spills only under 2026), sub-point chord/footnote shifts on a few pages, the colophon block and anti-aliasing noise. **CI is therefore pinned to TeX Live 2023** (`texlive_version: 2023`): frozen, same as the dev workspace, and every song fits on one page (756 pages), so the one-page allow-list is empty. Moving to another year later changes the layout and should be reviewed with the S3 diff.

### D-106 · Visual diff compares songs, not page positions — Agreed (3 Nov 2026)
Base and head are both compiled in the same CI job (≈8 s each) and pages are matched by song id (from the per-song `.aux` page checkpoints), with the page-number footer and the colophon date excluded. Comparing by page position is useless as soon as a song is added, removed or reordered.

### D-107 · Song order: standard Czech collation of the title — Agreed (3 Nov 2026)
Songs (include list, TOC letter sections, artist sections, web index) are ordered by the **title**, never by the file name: file names have no diacritics, and diacritics affect the order. Moving songs is acceptable if the result is more correct.
- Sort key: the plain-text title (`\toctitle` if set, else `\song`), with footnotes removed and accent macros and `\uv{}` resolved. Titles are sorted as written, with no article stripping ("The Passenger" stays under T, as today).
- The rules follow the Czech standard for alphabetical ordering (ČSN 01 0181, superseded by ČSN 97 6030), as described by Petr Olšák, *Zpravodaj CSTUG* 4/1994:
  1. **First pass.** Compare word by word: a space sorts before any letter, so "A Horse With No Name" comes before "Abych tu žil" (a change from today, where spaces are ignored). Only plain letters plus **č, ř, š, ž** and the digraph **ch** (one letter between h and i, also in non-Czech titles: "Change the World" stays under CH) are distinguished here. Digits come after ž. Punctuation is ignored.
  2. **Second pass**, only for entries equal so far: the other accented letters are distinguished (á after a, é and ě after e, …).
  3. **Third pass:** case; a lowercase letter sorts before an uppercase one.
  4. **Last:** punctuation, only to break a remaining tie.
- Implemented in the generator itself (stdlib, with unit tests built from the examples above), not with `locale.strxfrm`. Locale collation depends on which locales the machine has installed (the cloud container has no `cs_CZ`), so local runs and CI could disagree.
- TOC letter sections follow the first-pass letters, so the current **Ď section is removed** and "Ďáblovy námluvy" is listed under D (owner decision, 3 Nov 2026, after briefly keeping Ď as an exception).
- Expected one-time effect: the ~20 hand-placement deviations move, plus every title whose position depends on spaces (many in A). Page numbers after them shift. The generator lists all moves for review before the switch (TICKETS R9).

### D-108 · Clean up spacing before building the converter and the HTML — Agreed (3 Nov 2026)
Order: safety net → registry and generators → source hygiene → chord spacing → vertical spacing → converter → legal → website.
Rationale: the converter is then written once, against semantic macros only (the requirement to understand the legacy spacing macros is dropped); `songs.json` stays free of layout; the web uses the same chord-spacing rule as the PDF.
*The order after the cleanup is amended by D-132.*

### D-109 · Print layout is out of scope — Agreed (3 Nov 2026); superseded by D-122 (4 Nov 2026)
The printed edition is a one-time, separate effort (backlog). The PDF built here is the screen/download PDF. The licensing note for a *sold* printed book stays in the backlog.

### D-110 · The website gets the songbook outputs from release assets — Agreed (3 Nov 2026)
The web build downloads `songs.json` (and the PDF) from the `zpevnik` release pinned in `version.txt` instead of having them committed. The songbook CI already commits a 4 MB PDF per release; `zpevnik-web/.git` is 29 MB after 6 updates. Existing history is not rewritten. The static lidovky and koledy PDFs stay in the repo.

### D-111 · Registry and generator conventions — Implemented in R4, R5, R13 (3 Nov 2026), merged by the owner; details may change in R6
- `data/artists.toml` stores plain text, no TeX markup; the generator escapes it (`&` → `\&`) and turns U+00A0 into `~`. Entries are `[[entry]]` tables; fields since R7: see D-114 (earlier: `slug`, `name`, `index_label`, `sort`, `kind`, `section`).
- `name` is the section heading ("Surname, First" for people), so `sort` equals `name` for artists; collections have explicit sort keys and come after all artists. Whether `name` becomes the natural form is open (R6).
- `filmy` and `lidove` are `kind = "collection"`. The forced line break in the `filmy` heading is not stored; R11 must reproduce it.
- TeX side: `generated/artists.tex` calls `\zpregisterartist`; `zpevnik.sty` offers `\artistname`, `\artistlabel`, `\artistlinklabel` (R7, D-114), `\ifartistsection`; `\zpregisterartist` takes 5 arguments since R7. A missing file or unknown slug prints nothing (D-003, D-005).
- Version (*amended by D-133: a third number counts the builds*): `tools/generate.py` computes *song files + 100* (733 → 8.33); the colophon uses `\zpversion` (shown as `?.??.?` without the generated file); CI reads it with `generate.py --version`.

### D-112 · Artist anchors and names after R6 — Implemented in R6 (4 Nov 2026), PR #30
- Anchors are the lowercase ASCII name without spaces or a leading article (INVENTORY C1 renames applied). `trikyapovery` is split: `trikyapovery` = "Triky a pověry", `ricchiepoveri` = "Ricchi e Poveri" with its own section (between Redl and Rottrová) and index entry.
- Registry names: "The Beatles"; "Tučný, Michal & Greenhorns" (name and sort key; "Fešáci" dropped). Headings of people stay "Surname, First"; whether `name` becomes the natural form is still open.
- Owner decided: the song labels of `michaltucny` (21× "Michal Tučný", 5× "Greenhorns") and the 2× "J. S. Lenk" stay for now. The decided labels "Michal Tučný & Greenhorns" / "Jaroslav Samson Lenk" are too wide for the `\interpret` position (starts at x≈451 pt of 595 pt) and would be cut off; master already cuts "Jaroslav Samson Lenk" on 9 pages. R7 (`\artist`, same position) must resolve this; the owner decides how. **Superseded in R7 by D-114:** the overrides are gone.
- Label typos fixed in 5 songs (Beatles, Marie Kubišová, Nohvica, Nohavica, Plíhal).

### D-113 · `\artist{}` — Implemented in R7 (4 Nov 2026), PR #31
- Syntax: `\artist[label]{slug}` on the line of `\song`, exactly one such line per song. Two artists: `\artist{a}\artist{b}` (first = rightmost); a third is ignored (owner: max 2, no layout exists for more). Songs without an artist have `\artist{}`. Empty or unknown slug, or an artist without a section, prints nothing and is no error (D-003, D-005); the validator reports unknown slugs.
- The link text comes from the registry (D-114), not from `name`, which is the section heading. `\artist[label]{slug}` can still override it per song, but no song does.
- Layout (owner decision, replaces "same position as `\interpret`" in the R7 ticket and the session notes): links are right-aligned with the right edge 1 cm from the page edge; the vertical position is unchanged. This fixes the overflow described in D-112: no label is cut off any more (it also changed "Len" to "Lenk" on 9 pages).
- Implementation detail worth knowing: the list of links is built when `\artist` is called and typeset at shipout, in the font active then (`\Large` in the book); `\song` starts a new list, so `\artist` belongs after `\song`.

### D-114 · Registry fields: one label, defaults — Implemented in R7 (4 Nov 2026), PR #31
Owner request: fewer, easier-to-remember properties and less repetition in `data/artists.toml`. An entry needs only `slug` and `name`; the rest is optional and written only when the default is wrong:
- `name`: the section heading, people as "Surname, First". `sort` defaults to `name` (explicit only for Beatles, `filmy`, `lidove`).
- `label`: how the artist is named in the index and, by default, in the link on the artist's songs. Default: "First Surname" for a name of the form "Surname, First", otherwise the name itself (so "Hapka & Horáček" and "The Beatles" need nothing). Explicit for `michaltucny` ("Michal Tučný & Greenhorns") and `filmy` ("filmová hudba", as in today's index).
- `link_label`: shorter text for the song link, default `label`. Used only for `jaroslavsamsonlenk`: heading "Lenk, Jaroslav Samson", index "Jaroslav Samson Lenk", song link "J. S. Lenk".
- `kind` defaults to `"artist"`, `section` to `true`.
- The old `song_label` and `index_label` are gone. The index used the surname only ("Plíhal"); with one `label` it will show the full name when R11 generates it (the hand-written index in `obsah.tex` is unchanged for now).
- Owner decisions in this change: Nohavica is "Jaromír" everywhere (heading in the registry and `obsah.tex`); all songs of Michal Tučný & Greenhorns say "Michal Tučný & Greenhorns" (5 songs said "Greenhorns", 21 "Michal Tučný"); all Lenk songs say "J. S. Lenk"; no per-song overrides remain.
- The TeX side: `\zpregisterartist{slug}{name}{label}{link label}{section}`; `\artistlabel`, `\artistlinklabel`.

### D-115 · Artist index as a column list — Agreed (4 Nov 2026, session 6)
Because the index would now show full labels, the owner proposes turning the one-row index block into a proper alphabetical list of artists in columns. The TOC would read: letter row, link to the artist index, alphabetical list of songs, alphabetical artist index, songs listed by artist. This changes the layout that R10 must "reproduce exactly" and the index R11 generates; agreed by the owner in session 6. R10/R11 are adjusted at the start of R10: the agent presents which part of the new TOC layout each ticket builds, and the owner confirms.

### D-116 · Alternative titles, TOC titles, collections — Implemented in R8 (4 Nov 2026), PR #32
- `\alttitle{}`, `\toctitle{}` and `\collection{}` are no-output macros in `zpevnik.sty`, written on the lines after `\song{}`/`\artist{}`. An alternative title is stored as plain text, without the italics or the forced line break of the old TOC entry (those are layout for R10/R11).
- 29 alternative titles, not the 28 of INVENTORY D1: `mojiprvnimuze` "Smutno je mi" appears only in the artist index, and the owner chose to keep it.
- R2 rows settled in session 5: `whenthesaintsgomarchingin` (written `= toc`) is `toc`; `escesomsaneozenil` stays `song` ("Eščě" was a TOC typo, the lyrics say "Eště"); the plain TOC entry "Gimme Dat Ol' Time Religion" (`oldtimereligion`) is dropped, not an `\alttitle`.
- The 11 `song` rows leave the hand-written TOC wrong until R10 generates it. TOC-only inconsistencies not listed in D2 (`pianoman`, `ringoffire`, `tickettoride`, `jednoumifotrpovida` "Jednohou", `hittheroadjack`) go away the same way.
- `\collection{filmy}` is set on the 46 songs of the `filmy` section; `lidove` stays an `\artist{}` (76 songs). `tools/check_registry.py` does not know `\collection` yet (R12).

### D-117 · Drop `\sub` where it only repeats the artist — Agreed (4 Nov 2026), done in the R9 PR #33
`\artist{}` now prints the artist on the page, so a `\sub{Spirituál kvintet}` under the title says the same twice. Candidates found by comparing `\sub` with the registry (session 6): `digadigadospiritual`, `podzimnispiritual`, `slapejdalspiritual`, `slapejdaltucny`, `vranabuty`, `podzimniplihal`, `vranaplihal`, `cervenarekatucny` (this one also has a `\note` on the `\sub` line, which stays). Not candidates: `digadigadoplihal` ("Karel Plíhal, text Josef Kainar" has more than the artist) and `scarboroughfaircarthy` (no `\artist`). The TOC disambiguation is `\toctitle` and is not affected. Removing a `\sub` changes the song page (the `\vspace{-10mm}` goes with it), The owner agreed and asked for it in the R9 PR: the eight songs above changed (subtitle gone, text one subtitle height higher), nothing else.

### D-118 · Artist index and sections generated (R11) — Implemented in R11 (4 Nov 2026, session 7), PR #35
- **Index** (amends D-114/D-115): two columns, `\Large`, ragged right. It shows `name` (the section heading, "Surname, First", so it can be searched by surname) for artists and the short `label` for collections ("filmová hudba"). `label` now serves only the links on the songs' pages. Owner's decision in session 7; no registry change.
- **Sections** come from the songs' `\artist` / `\collection` tags and the registry (`section = true`, ordered by `sort`, collections last, songs by D-107). A song is listed under each of its tags; this removed the C5 drift. For the six songs that the hand-written contents listed under an artist their file did not name, the owner chose to add the `\artist` tag to the song (bonsoirmademoiselleparis, hvezdanavrbe: olympic; dvebaby: spiritualkvintet; huslicky, sbohemgalanecko: vlastaredl; sirokyhluboky: spiritualkvintet; the existing artist stays first, i.e. rightmost) rather than dropping them from the sections. Entries use the title printed on the song's page, not the `\toctitle` (which is only a disambiguation for the letter sections), and every `\alttitle` has an italic entry in each section of its song.
- A line break (`\n`) in a registry `name` is a forced break in the section heading (only `filmy` has one).
- `generated/obsah-artists.tex` holds the index, the rule and the sections; `obsah.tex` only wraps it and `generated/obsah-letters.tex`. `Song.groups` (tags) is what R12's lints should use: `check_registry.py` still counts only `\artist`, so it warns that `filmy` has no songs.

### D-119 · Lints and the section threshold — Implemented in R12 (4 Nov 2026, session 7), PR #36
- `tools/lint.py` (CI step) fails on: invalid registry entry, song without `\song`, not exactly one `\artist` line, more than two artists, `\interpret` left over, unknown slug in `\artist` / `\collection`, `section = true` without songs. It warns (never fails) when an artist with `section = false` has **3 or more** songs and when several songs share a contents title without a `\toctitle`; it prints the number of songs with an empty `\artist{}` as info.
- Owner's decision (session 7): the section threshold of D-004 is "3 or more"; it is the constant `MIN_SONGS_FOR_SECTION` in `tools/lint.py`. The seven existing sections below three songs stay as agreed.
- `check_registry.py` only validates the registry entries now; the song checks moved to `lint.py` and use the tags read by `songs.py` (`Song.groups`).

### D-120 · Source hygiene H1–H4 — Implemented in session 8 (4 Nov 2026), PRs #38–#41
- **H1 (owner confirmed each fix):** `klada` `\note{(capo 2)}` and `jaktosnamalaskobude` `\emph{(Cože)}` plus the sentence after it in italics (visible changes); `neninutno` `\vers{3}{=\mm \textbf{1.}}`, `noe` `\refsm{}`, `morituritesalutant` `\bridgesm{}` (a short bridge repeat, "B."; the bare `\bridge` had printed a "B:" label). `oneofus` left alone.
- **H2:** no song ends in `\newpage` (708 removed, 25 never had it); `\include` starts the page. The README says so.
- **H3:** `generated/include.tex` writes `\songinclude{<id>}`; the macro (`zpevnik.sty`) stores the id in `\zpsongid` and calls `\include{pisnicky/<id>}`; `\song` calls `\zpsongtarget`, which makes the hypertarget once per include and clears the id. Without an id there is no target (D-005). A song file no longer carries its id: **the file name is the id** (the converter, WP5, takes it from there). The `\hyt` macro stays because the generated contents use it for letter and artist anchors. `check_pages.py` reads `\songinclude`; its pre-H3 fallback was removed in the H4 PR.
- **H4:** accent macros in 12 songs replaced by UTF-8 (59 `` \` `` and 4 `\^{o}`; the ticket's 60 and 5 were a snapshot count). `tools/tex_text.py` still resolves accent macros, so a future title written with one still works for the order and the contents.
- The six songs with `\footnote{}` inside `\song{}` are unchanged; the final place of that footnote is still open (TICKETS, TODO under H4).

### D-121 · Editions are in scope — Agreed (owner, 4 Nov 2026), tickets E1–E7; design decided in D-138, revised in D-139
Two use cases: `zpevnik-lite` (a manual selection of favourites, exported now and then, not on a schedule) and possibly the printed book (D-122). The constraint of D-102 stays: the generator works from one ordered song list, so an edition is a filter over it and the full book stays byte-identical. Design questions (definition by file or tag, links to songs outside the edition, artist sections, naming, publishing) are the owner's decision E1; the agent's proposed defaults are in TICKETS. Checked in session 8: the include list, the letter contents and the artist sections already follow the song list; the artist index and sections still loop over the whole registry; the title and the version (song files + 100) are not parametrised; 84 `\hyl` links in 76 songs would dangle.

### D-122 · The print edition is in scope with a deadline — Agreed (owner, 4 Nov 2026), tickets P1–P4; amended by D-140, D-142
Supersedes D-109 (which had put the print layout out of scope). The print is important and has a deadline (the date is asked in P1). The plan is to finish the refactoring first, but the owner may pivot, so the print build needs only phases 1–2 (done) and works on the current layout; it is repeated after phases 5–6. If the book is a subset it needs E1–E4 first (P1 asks). Licensing for a sold book is the separate owner task P2.


### D-123 · Automatic chord spacing, gate C2: path A — Agreed (owner, 4 Nov 2026, session 9)
Prototype and evidence: docs/archive/phase-5-chords/C1-chord-spacing.md, docs/archive/phase-5-chords/C1-review-lists.md (with the owner's answers), draft PR #42 (`proto/c1-chord-spacing`, never merged).
- **Rule.** A chord and its text occupy max(text width, chord width + `\chordsep`), `\chordsep` = 0.5em. Between two chords with no text between them: chord width + `\chordrunsep`, `\chordrunsep` = 1em. Text moves only where a chord would collide.
- **Technique: a single-pass lookahead in `\chord`.** `\chord` reads the tokens up to the next `\chord`, `\chords`, `\\`, `}`, `\par`, `\end` or `\begin`. It measures them in a box (with `\footnote` neutralised) and puts them back unchanged, so line breaking, hyphenation and footnotes are untouched. Then it pads before the next chord if that chord would collide. Syntax unchanged; the chord box keeps zero width.
  - Rejected: positions via `\pdfsavepos` and the .aux. It needed 4 passes instead of 2, and on the fully stripped book it didn't converge in latexmk's 5 passes.
  - Known limits:
    - The lookahead can't measure across a brace boundary: 25 same-line pairs, of which only tasidele would need a pad after C3; the overlap check catches it.
    - On justified (wrapped) lines a gap can shrink below 0.5em (minimum 4.2 pt) but never overlaps.
- **Pauses are intentional everywhere** (a chord struck, then a pause before the lyrics). They are written `\gap{n}`, n in characters of 0.5em: `\sm` 1, `\mm` 2, `\nc` 4, `\bc` 8, summed. A deliberate gap inside lyrics without a chord also becomes `\gap{n}`.
- **No pause inside a word.** Spacing after a chord inside a word is removed: "tomu", not "to - mu" (letadozravani, batalion, bratrickuzavirejvratka, …).
- **A pad that splits a word gets a centred hyphen**, and the pad is widened to fit it ("invisi - ble"). There is no switch for this.
- **`\chords{…}`** sets chords inline in the lyric line: red, `\chordrunsep` apart. It is used for whole chord-only lines (also inside `\intro{}`, `\solo{}`, …) and for chords written as plain `\textbf{…}` (≈ 96 places in 58 songs). Runs after the last lyric of a line, between lyrics or before them stay `\chord` above the text.
- **Words are never joined.** A gap between two letters is removed only if the joined form is a word elsewhere in the songbook, or if the owner said so (C1-review-lists.md sections 1–2):
  - Joined: pohání, Goliáš (go|li, li|áš), zavanou (za|va), ořecha, končívaj, wasting, emotion, invisible, medecína, naráží, suchá, tomu.
  - Kept apart: sněhy|za, fare|and, ledový|přinesl, listopadový|písni, stíráš|rosu, já|panenku, jen|pouhý, je|soudný, vandrovali|po.
- **Migration (C3).**
  - C3a puts the macros on master with the spacing off (zero diff).
  - C3b then migrates songs in batches of about 45 (alphabetical, ≈ 460 songs in ≈ 10 batches). Each song opts in with a temporary `\autochords` and is reviewed once, with a real PDF of the batch.
  - C4 makes the spacing the default and removes the switch (zero diff).
- **Simplicity review** (owner asked whether it is overengineered).
  - What stays:
    - the scanner, measuring and padding (the rule itself);
    - the two separators;
    - the in-word hyphen (owner's wish);
    - `\gap` (semantic pauses) and `\chords` (semantic chord lines);
    - the per-song switch (temporary, for reviewable batches);
    - a chord-position trace for the overlap check in CI.
  - Dropped from the prototype: the hyphen on/off switch, and the hyphen logic in `\gap` (no in-word pauses).
  - About 85 lines in `zpevnik.sty`, no new package, single pass, build +12 %. With the spacing off, the whole book is identical to master, which shows the lookahead puts the text back unchanged.
- **Web (W2)** uses the same rule in CSS. Each chord and its text form an inline-block column, with the chord's `padding-right` = sep. `\gap` is a fixed spacer, and `\chords` is an inline run of chords.
Rationale: the target rule of WP2 with no manual spacing left. Pauses stay explicit and semantic, which the converter and the website need (D-108).

- **Implementation note (session 10a, C3a; not a change of the decision).** How the tool decides "inside a word" for a pause after a chord: the same judgement as for a gap before a chord, in this order: the owner's answer (the pairs of D-123, plus the pauses of letadozravani, batalion and bratrickuzavirejvratka), the joined form is a word elsewhere in the book (removed), both parts are words elsewhere (two words, the pause stays a `\gap`), otherwise the pause stays a `\gap` and is listed as CHECK. A control word before the chord (`\dots`) is not a letter. So a pause is never removed on a guess, but a one-syllable part that is also a word (cervenareka `jezdí|vá`) keeps its `\gap`; the batch review shows it. Chord-only `\textbf` lists with a line break (blackbird, kluziste, prosimteholka) stay `\textbf`. 15 places print glued chords on master today (a control word swallows the space, `Dm Dm\maj Dm\7` prints `Dm△Dm7`): the tool keeps the source and lists them; fixing them is the owner's decision in C3b.
- **Implementation note (session 10a, parallel batches; not a change of the decision).** Chord lists with a line break become one `\chords` row per line (owner's request; PR #44), so blackbird, kluziste and prosimteholka are no longer exceptions. C3b batches are generated in parallel, one branch and PR per batch from master (#47–#56), nothing merged; the songs that need the owner's decision form batch 11 and are not generated: unclear pauses (conselho, jasetesimdonebe), glued chords (12 songs), the two songs that take a second page with `\autochords` (jenamteplo, malujzaseobrazky) and rosanakolejich (H5 edits the same line). A batch PR contains song files only; the tool lives in the C3a/#44 code.
- **Implementation note (session 10a, batches 11–12; not a change of the decision).** Owner's answers: glued chords are all fixed (`{}` after the control word, so the printed chords change; tool PR #57), conselho entregar|a two words, jasetesimdonebe le|luja one word. `jenamteplo` and `malujzaseobrazky` took a second page with the 1 em `\chordrunsep` (chord-only rows were bold text before and are wider as `\chords`). Tried: `\vspace` (works for jenamteplo, not for malujzaseobrazky: needs 18 pt and then collides with the title) and a narrower book-wide `\chordrunsep` (malujzaseobrazky needs 0.55 em). Owner's choice, option E: `\chords[sep]{...}` overrides the spacing of one row (PR #59); `malujzaseobrazky` uses 0.55em on its first row, `jenamteplo` 0.9em on the `S:` row (PR #60). `\chordrunsep` stays 1 em. Chord rows are never kept as `\textbf` (unified approach).
- **Implementation note (session 11, C4; not a change of the decision).** The spacing is now the default and the switch is gone (`\autochords` removed from the 449 songs, `\song` no longer resets it), with zero diff. Deleted with `tools/strip_chord_spacing.py` because nothing else used them: `chord_lists.py`, `word_decisions.py`, `migration_report.py`, `chord_syntax.py` (the word judgements of this decision stay in the Git history and in this text). `chord_gaps.py` fails on any overlap in the book and lost its `--list` option. Lint: error on `\nc \mm \sm \bc`, warning for a song without `\chord`/`\chords`.
- **Implementation note (session 11, C5; not a change of the decision).** Label width (owner, 5 Nov 2026): one fixed `\labelw` = 25 pt for all labelled blocks (the widest label, "R1:", is 24.1 pt; before, text started at 21.1–24.1 pt, after `\solo` at 29.6 pt); `\nv`, `\hyl` and `\lsp` are derived from it. Score-image `\hspace` indents stay as placed by hand (owner). A `\hspace` that only compensates a label or a line fit is removed, except `velicenstvokat` (negative `\hspace`, line fit; kept and commented).

### D-124 · Vertical spacing: one shrinkable block gap — Agreed (owner, 5 Nov 2026, session 12, V1/V2)
- The vertical spacing in the songs was added ad hoc; its purpose is to fit one song on one page. Target: one block gap `\blocksep` (20 pt) in `zpevnik.sty`, shrinkable (to zero) when a song would not fit, and no vertical spacing in song files apart from the exceptions below.
- `\ns`, `\cns` and the negative `\vspace` between blocks are deleted, not replaced (evidence: without them 74 of 88 songs spill; with a shrinking gap 2, `babickamary` and `milionar`). A semantic replacement would carry a print-only fix into `songs.json` (D-108).
- Dashed lines (`\lsp`) stay: they separate tightly packed verses, which helps while playing. They become a separator that replaces the next block gap instead of cancelling it (verified zero diff).
- `\vinv` first becomes one named macro `\groupbreak` (zero diff); whether each one stays is decided per song in the batch review, as for the horizontal spacing (C3b).
- Blocks without a label become unnumbered verses `\vers{}{…}` with the normal gap. The solid rule in `idzepostaridze` becomes `\partrule`.
- The `\vspace` and `\hspace` next to score images stay.
- Analysis and evidence: docs/archive/phase-6-vertical/vertical-spacing.md and docs/archive/phase-6-vertical/vertical-spacing/analysis.md.
- Ticket plan (owner, 5 Nov 2026): the gap is shrinkable from V3 on; V4 introduces the named macros with zero diff; V5 is one batched pass per song (deletions, unnumbered verses, the decision on each `\groupbreak` and remaining `\vspace`), reviewed like C3b; V7 is merged into V5; V8 deletes the old macros. Before all of it, H6 replaces the `\everypar` hack (owner: as soon as possible). The body font size (`\Large`) waits until after V8 and may stay as it is (backlog).

### D-125 · Score images are exported from MuseScore in CI — Direction agreed (owner, 5 Nov 2026), confirmed by J5's prototype; implemented in D-136
- The `.mscz` files are the source of the score images. CI exports them with a pinned MuseScore, so the PDF and the web use the same export, and the exported images are build output (D-104), not committed.
- A score is a single page by principle; that is what makes MuseScore's trimmed SVG export (`-T`) usable. pdfLaTeX cannot include SVG, so the PDF needs a converted SVG or a cropped PDF export; J5's prototype decides.
- One `.mscz` per image; the owner provides the missing ones (list in TICKETS J5). Replaces J5's earlier plan (`pdftocairo` from the committed PDFs).

### D-126 · Project history and helper files — Agreed (owner, 5 Nov 2026), ticket Z1
- `docs/HISTORY.md` records each finished phase (what changed and why, numbers, PRs, decisions), so that the refactoring can be told as a short story on the website later.
- Helper files of finished phases move to `docs/archive/<phase>/` once their important content is in HISTORY.md, DECISIONS.md or TICKETS.md. Nothing is deleted.
- *First run (6 Nov 2026):* HISTORY.md started (with notes for the article); INVENTORY.md (fully consumed) and the helper files of phases 2, 5 and 6 moved to `docs/archive/`; snapshots of PLAN, TICKETS and SESSIONS before their cleanup in `docs/archive/snapshot-2026-11-06/`. Owner's instruction the same day: remove what is not needed, keep what is important; so exact duplicates may be deleted (six V5 review PDFs in `Claude outputs/` were byte-identical to the archived ones), everything else is moved.

### D-127 · `\everypar` hack replaced; `center` behaves as standard LaTeX — Agreed (owner, 5 Nov 2026, session 13, H6)
- Cause (verified with a logging build): in LaTeX 2023-11, `\everypar` is a `\newtoks` register that the paragraph hook reads by number, so `\def\everypar{…}` only hid the name. Every `\everypar{X}` in LaTeX code set `\parindent` to −10 mm and ran X immediately: 865 × after headings, 3092 resets, 554 × parbox/minipage, 11 × `\item`, 11 × end of a list.
- Replaced by explicit settings: `\parindent` −10 mm with `indentfirst`. `\sub` clears LaTeX's after-heading flag (`\@nobreakfalse`), so the subtitle keeps its space above (50 songs pixel-identical; local in `\sub` rather than a global patch of `\@afterheading`, which gives the same output). `\placetextbox` no longer compensates the hidden indents; vosa's x is adjusted to keep the note in place.
- `center` (rules in 3 songs, front matter, contents) is not reproduced: the hack gave each one an extra empty line and a 5 mm off-centre first line. The owner accepted standard LaTeX there. In idzepostaridze, the two `\ns` that compensated the empty line are deleted (V5 deletes all `\ns` anyway).
- Side effect, kept on purpose: the first paragraph after a heading now gets LaTeX's club penalty (no page break after its first line); this made no difference in the current book.

### D-128 · V5 details: `\note` flag, fixed gap in multicols, `\large` policy — Agreed (owner, 5 Nov 2026, session 15), PRs #74, #75
- `\note` no longer shifts up by a hidden −20 pt; like a rule it makes the next block gap disappear (the same global flag as `\blockrule`), so a note sits against its block and cannot collide on a tight page. `\noteshift` is removed.
- Inside `multicols` the block gap is fixed at 20 pt (`env/multicols/begin` hook), because multicols balances columns by shrinking glue, which squeezed the gaps to zero (vodavodenka, `\columnbreak` instead of `\vspace{175pt}`).
- A song that does not fit one page at `\Large` once the gaps cannot go negative gets `\large` after its header (precedent: mikymauz; babickamary, milionar, summernights, acrosstheuniverse). Not for songs with dashed rules: their offsets are tuned for the `\Large` line pitch (nepijjanonepijvodu keeps an explicit `\vspace{-35pt}` with a `% KEEP` reason). `\songinclude` runs each song in a group so a per-song font size cannot leak into later songs.
- Owner's rule for V5: no song may spill; each spilling song is fixed with the simplest local change instead of only reported (this replaces ticket V5 step 5).
- Remaining `\vspace` in songs carry a `% KEEP: reason` (score alignment, before a note or an attribution). `vlese` keeps its `\vinv` until the owner decides.

**Amended (owner, 6 Nov 2026, session 15, PRs #76, #77):**
- The dashed lines are treated differently from D-124 (zero-diff separator): the offsets of `\blockrule` are fractions of the line height (`\ruleshiftbefore` −13/18, `\ruleshiftafter` +4/18 line, `\dimexpr` on `\baselineskip`), so a dashed-rule song can use `\large`. The old −3 pt after the rule let the chords of the next block touch it; +4/18 line gives them room, and all six dashed-rule songs (jenamteplo, kometa, mamdomakocku, nepijjanonepijvodu, tesar, zpatkydotrenek) take `\large` because they spill at `\Large` with that room. nepijjanonepijvodu's `\vspace{-35pt}` is gone.
- V8 (#77): `\ns`, `\cns`, `\vnv`, `\vinv`, `\lsp` are deleted and `tools/lint.py` reports them as errors.
- The list of the remaining manual `\vspace` is `docs/archive/phase-6-vertical/vertical-spacing/remaining-vspace.md`.

### D-129 · Body font stays `\Large`; `\large` per song when a song is too long — Agreed (owner, 6 Nov 2026, session 15)
- The whole book stays in `\Large`. A song that does not fit one page even with every block gap shrunk to zero gets `\large` after its header, with a comment saying why (today: acrosstheuniverse, babickamary, mikymauz, milionar, summernights and the six dashed-rule songs).
- No automatic step-down and no other per-song sizes. `\songinclude` runs each song in a group, so the size does not leak into the next song.
- Closes the "Body font size" backlog question for now; absolute sizes of footnotes, `\dm`, `\bb` stay tied to 10 pt.
- The README documents it for the person writing a song (section "Svislé mezery a velikost písma").

### D-130 · `\note` has the block gap above, not below — Implemented (agent, 6 Nov 2026, session 16), PR #78 merged by the owner
- A note (capo, "pomalu") is attached to the next block (no gap below, D-128) but has the normal shrinkable gap above itself, except at the start of a song, after `\sub` and after a `\hyl` link line (flag `\ifzp@top`, raised by `\song`, dropped by blocks, notes and `\hyl`).
- Consequence: the manual `\vspace` before notes and after link lines are gone; eight songs with mid-song notes got a gap above them.
- Remark blocks without label are `\vers{}{\emph{…}}`. Speaker changes: `\spk{On}{text}` (block gap + italic name inline); motyl was the only user (renamed `\speaker` in D-131). No manual non-score `\vspace` is left.

### D-131 · Code-quality pass and the final command names — Agreed (owner, 6 Nov 2026), tickets Q1–Q5
- Before the features, the style file, the tools and the CI get a clean-code pass with zero diff (Q1–Q3), then the song commands get their final names (Q4), before the converter makes them its grammar (D-108).
- Names (checked against the book's packages and Czech babel: none collides): `\chorus` (was `\refrain`; the modern term for the repeated section, consistent with `\prechorus`; the label stays "R:"), `\coda` (`\cod`), `\subtitle` (`\sub`), `\speaker` (`\spk`), `\seealso` (`\hyl`). `\vers` stays, because `\verse` is LaTeX's `verse` environment.
- Numbers are an optional argument: `\vers[n]`, `\chorus[n]`, `\prechorus[n]`, `\bridge[n]`, `\solo[n]`; `\refrainn` and `\solon` go, and `\vers{…}` is an unnumbered verse.
- One `\cue{label}` for every repeat mark (`\refsm`, `\refsme`, `\bridgesm`, `\solosm` and hand-written `\textbf{1.}`): after an empty line it is a block of its own with the block gap, otherwise it is appended to the line, like `\note`. The 8 standalone `\refsm` lines get a gap (owner accepted).
- The chord symbols (`\kk \bb \dm \7 …`) stay: short, documented, and the obvious names collide (`\sharp`, `\flat`, `\dim` are math commands); `#` cannot be written in a macro argument, so plain-text chords are not possible.
- No aliases for old names; the lint reports them.
- Code comments in English; they give the reason, not ticket or decision IDs, because the docs are not in the repository.

**Implementation notes (agent, 6 Nov 2026, session 18, Q4, PR #82; owner accepted the differences):**
- The block macros are `\NewDocumentCommand{…}{o +m}`: `+m` keeps empty lines allowed inside the text, as they were with `\newcommand`. `\intro` and `\coda` take no number; `\nv` and `\lbl` stay until Q5.
- `\hyt` and `\hylo` are removed; the generated contents and `obsah.tex` use `\hypertarget` and `\hyperlink`.
- The PDF diff shows 15 changed songs, not the 8 of the ticket: ringoffire does not change (`\refsme` already had the gap); 6 more songs have a standalone mark after an empty line (hledamdevcenanedeli, jezisek, nejlipjimbylo, ourlastsummer, tata, morituritesalutant); slunecnyhrob and zafukane had a mark appended to a block's last line, where the old `\solosm` added a second gap before the next block.
- The migration script and its tests are not in the repository.
- After the owner's review (same PR): every block label ends with a dot (`R. I. P. B. S. C.`, `1.`, `Rn.`), none with a colon; this amends "the label stays R:" above. The `\speaker` name keeps its colon. Labels are right-aligned (dots line up) and followed by a fixed gap, so block text always starts at the left margin; block text ignores leading spaces. The `A:`/`B:` dialogue of haubilouplani is `\speaker`. Every label-only mark in the songs is `\cue` (also the empty `\bridge{}` and `\vers[n]{}` hacks); `tools/lint.py` reports a block without text. Inside `multicols` widows and orphans are forbidden.
- `\speaker` names and standalone `\cue` marks are right-aligned in the label column like labels (a wider name sticks out to the left); this replaces the "name inline in the text" of D-128. The gap between a label and a following `\chords` row was judged fine by the owner after the right alignment.
- Review before merge (6 Nov 2026): `\nv` indented by `\labelw` (25 pt) while the text after a label starts at the 10 mm hang, so `\nv` lines, `\seealso` and `\blockrule` sat 3.4 pt left of the text; `\nv` now indents by the hang (92 songs differ by that shift: those using `\nv`, `\seealso`, `\blockrule`), checked in `tests/spacing.tex`. `\nv` and `\lbl` are still used by 15 and 1 songs (`zapomnetliva`: `\lbl{A:}` keeps its colon until Q5 converts it to `\speaker`, owner's decision in Q5); Q5 removes the author uses, then `\nv` becomes an internal `\zp@` macro and lint reports any author use.
- Open for Q5: about 50 paragraphs in the songs do not start with a block macro (9 with `\nv`; `\rec{…}`, `\emph{rec.}`, chord rows, score images, the `zkratky` list); text ones start in the label column instead of the text column, like the old `rec:` of slunecnyhrob did.

- Q5 (owner, 6 Nov 2026, session 19, PR #83; 15 songs differ, owner reviewed each page): `\speaker{A}{text}` is mode-aware like `\cue`: inside a block (e.g. a numbered verse) it prints the italic name before the line, so dialogues keep their verse numbers. Song footnotes stay in `\song{}`. A long tuning note is an unnumbered `\vers{\emph{…}}` (`\note` is for short notes). `\nv` and `\lbl` are lint errors in songs. The tuning note of `ahorsewithnoname` is long, so `\note` (negative paragraph indent, expects a label) spilled its first line left. In `zapomnetliva` the repeat mark precedes the speaker name because `\rep` cannot span `\speaker` blocks (owner: leave). Not done: `\nv`/`\lbl` are still public names in `zpevnik.sty` (used by `\cue`, `\seealso`, `\blockrule`, `\zp@block`); done afterwards in PR #84 (`\zp@boldlabel`, `\zp@labelindent`). The "about 50 paragraphs without a block macro" note above was really 7 songs (PR #85: `\rec`, chord rows and `\emph{rec.}` are in `\vers{…}`; `lint.py` rejects text outside a block). Exempt on purpose: the `zkratky` glossary (a `multicols` appendix) and the `\placetextbox` of `vosa`. Also in #85: `=\gap{2}\cue{n}` is `= \cue{n}` (14 songs), so the space after `=` matches the label gap.

### D-132 · Order after the refactoring: editions and print before the converter and the website — Agreed (owner, 6 Nov 2026)
The refactoring took longer than expected, so after phase 11 the work goes: editions (E1–E5), print (P1–P4), then the converter (J1–J5), legal (L1–L2) and the website (W1–W7). Amends the order of D-108 after the cleanup; its rule that the converter comes after the cleanup still holds (it now also comes after Q4). L2's hide switch uses the edition filter of E2.

### D-133 · The version identifies a build: `8.33.N` — Agreed (owner, 6 Nov 2026; details proposed by the agent, confirmed in E0's PR), ticket E0
- Found in the review after phase 11: the tag `v8.33` points at the source of 21 Aug 2026, while every push to master replaced the PDF of that release and committed another 4 MB PDF to `zpevnik-web` (10 on 6 Nov alone). The version is the song count, so a refactoring never changed it, and W1 (download by tag), E5 (edition PDFs in "the same release") and P4 (which build went to the printer) need a version that names one build.
- Owner's scheme: `major.minor` stays the song count + 100 (D-111), the third number counts the builds with that song count: 8.33.0, 8.33.1, … Every other change is a patch from the point of view of the PDF.
- `patch` comes from Git, not from GitHub: the number of first-parent commits since the last commit that changed the song count. Deterministic (CI and a local build with history agree), nothing stored. The first release after the switch therefore continues from the existing history (around 8.33.6x), not from 1; the old tag `v8.33` stays.
- A tag is never overwritten or moved: CI fails if it exists (possible only if songs are removed and the count returns to an earlier value).
- The colophon, the release, `version.txt` and the edition file names use the full version; without Git history the colophon shows `8.33.?`.
- Details confirmed in E0: the song count "changed" in a commit when it adds more song files than it deletes, or the reverse (swapping one song for another does not restart the patch). A shallow clone, no Git or no repository gives `?`, never a wrong number. The tag check is its own CI step before anything is published. The first release after the switch is 8.33.67 (computed from the history of 10 Nov 2026).
- Not adopted: counting releases through the GitHub API (not reproducible locally), Conventional-Commits semantic versioning (the version describes the PDF, not the code).

### D-134 · The planning docs live in the `zpevnik` repository — Agreed (owner, 6 Nov 2026)
- `docs/` (PLAN, TICKETS, SESSIONS, DECISIONS, HISTORY, archive/) and the project's `CLAUDE.md` moved from `songbook-project/` on the owner's computer into this repository, so a session needs only the repository and can run from any device. Supersedes the "docs are outside both repositories" setup (TICKETS *Working environment* before 6 Nov 2026).
- The docs change through pull requests: a ticket's PR also sets its status to `done` and records its decisions and, at the end of a phase, its HISTORY entry; a change of plan without a ticket is a docs-only PR. Docs live in `zpevnik` because the songbook is the centre of both repositories; `zpevnik-web` tickets update them with a small PR here.
- Only text is committed: the binary review files of the finished phases (≈150 PDFs and page images, 58 MB) stay on the owner's computer (`docs/archive/README.md` says where); new ones are attached to their PRs. The CI clones the full history (`fetch-depth: 0`), so 58 MB would slow every run.
- Code comments still give the reason, not decision IDs (D-131): a comment must be readable without the docs.

### D-135 · Song quirks before the converter (J0) — Agreed (owner, 8 Nov 2026, session 23)
The converter is strict (an unknown macro is an error), so every special case in the songs got a semantic command, a standard form, or an explicit rule for the converter. Re-derived from every macro, environment and `$` in the 733 songs.
- **Echo and backing vocals** are `\echo{…}`: italic, raised like a superscript, at the size of the text around it (the look of `kratkypopisleta`, which is unchanged; `dvakrat`'s smaller superscripts grow). The lint reports `\textsuperscript` in songs.
- **Repeat counts** are `\ntimes{N}`, printed `×N`. 75 counts in 60 songs were written six ways (`$\times 2$`, `$\times$ 2`, `2×`, `(4×)`, …); each is now `×N` after the mark (`\cue{R} \ntimes{2}`), so 14 songs change slightly. `9$\times$19 mm` in a footnote of `lasko` is a size, not a count, and stays.
- **Repeat signs are only `\rep{…}`**: the hand-written `\: … :\` of `dvahavrani`, `milionar` and `saraperchetiamo` became `\rep`; the lint reports `\backslash` and `\textbackslash` in songs. In `dvahavrani` the quotation of a whole verse ends after the repeat sign (`\uv{… \rep{…}}`), because the quote and the repeat must nest.
- **Math stays** where it is the correct LaTeX (owner): `$\rightarrow$` in `panubohudooken`, `9$\times$19` in `lasko`; `\ntimes` uses `$\times$` inside. The converter accepts this short list of symbols in math and nothing else.
- **Hand-drawn rules** (`center` + `\rule{18cm}`) in `jedesohajzvidna` and `kolenasejchalupecky` are `\partrule`, which also drops the block gap after the rule, as in the other two songs.
- **No layout squeezing in song text:** `velicenstvokat` puts each `\rep{…}` on its own line instead of pulling the line in with negative `\hspace` (owner's edit).
- **Content fixes by the owner:** `oneofus` (the chord with a remark inside `\chord` is gone; the closing chorus is written out), `jednourano` (chords fixed, `\note{\small …}` gone), `kdonaplninebe` (plain slashes in the lick), `rosanakolejich` (`\artist{wabidanek}`). The title page says `2019--\the\year` (the songbook was started in 2019).
- **`vosa`:** the poem placed with `\placetextbox` at fixed page coordinates is removed, and so is the command (owner: short poems may come back later as a feature; fixed page coordinates would break in the print geometry).
- **Text inside an environment must be in a block too:** the glossary of `zkratky` is one unnumbered `\vers{…}` inside `small` and `multicols` (it still fits one page; at normal size it does not). Its `\setstretch{1.0}` was the only use of `setspace`, which is no longer loaded (the whole book renders identically without it). The lint no longer exempts environments; `\columnbreak` and `\end` may start a paragraph.
- **Kept, and how the converter treats it:** `multicols` is a song-level fact (`columns` in `songs.json`); `\columnbreak`, `small` and `\large` are PDF-only layout. `\textbf` stays as bold, like `\emph` (only in the footnote of `polesbavlnou`: **Tex**as, **Ark**ansas, L**ana**). `\uv`, `\enquote` and `\enquote*` stay, each with its own quote marks. Line breaks inside a word in `noe` are the lyric. `zapomnetliva` stays as decided in Q5.
- **Scores** (item 1 of J0) are decided separately, together with J5: see the next entry.

### D-136 · Scores place themselves: shared MuseScore style, trimmed SVG, `\score{name}` — Agreed (owner, 8 Nov 2026, session 23), J0 item 1 together with J5
- **Problem:** 22 score images in 18 songs were placed by hand (`\vspace{-25…-58pt}`, `\hspace{20pt}`, `21pt` or `9mm`, widths from `0.7\linewidth` to `515pt`), cropped by hand in macOS Preview, at different scales, two of them 10 mm into the left margin. An indent "as one constant" with zero diff was impossible: the indents differed.
- **Source:** one `scores/<name>.mscz` per image (owner split `morseovka`, `pohadka`, `reddwarftheme`, `slunecnyhrob` and added `tickettoride`); the committed PDFs and PNGs are gone (build output, D-104). A score is a single page.
- **Shared style `scores/zpevnik.mss`**, applied on every export with MuseScore's `-S` (it overrides the style saved in the file; verified): the owner's house style (staff space 1.764 mm, printable width 190 mm, no indent of the first system) with CMU Serif (Computer Modern, the book's font) for all text, bold chord names in German spelling (H/B, as in the songbook), no measure numbers, systems 0–7 sp apart. With it 21 of 22 scores keep their own line breaks; `variacenarenesancnitema` wrapped its last measure (bold chord names are wider) and got a layout stretch of 0.95 on its measures, which keeps it on one system. Editing a score means loading this style in MuseScore first, so what the owner sees is what the build makes.
- **Export (`tools/scores.py`, `make scores`):** MuseScore 4.6.5 (pinned in CI, AppImage) writes a trimmed SVG (`-T 0`): its left edge is the left end of the staff. The tool reads the first staff from the lines MuseScore marks `class="StaffLines"`, removes the white page background (for a dark web page), paints the chord names (`class="Harmony"`) in `chordred` read from `zpevnik.sty`, converts the SVG to a PDF of the same size with `rsvg-convert` (pdfLaTeX cannot include SVG), and writes `<name>.tex` with the left end and the middle of the first staff. Text in the SVG is outlines, so the result does not depend on fonts at build time beyond the export.
- **Placement (`\score{name}` in `zpevnik.sty`):** one scale for all scores, a full system (the style's printable width) fills the line from the text column to the right margin (0.894 on A4; a print page size scales the same way). The staff starts at the text column; the middle of its first staff is level with the middle of a label, so at the start of a block the label stands beside the staff. No offsets in songs: the aligning `\vspace` lines (`% KEEP`) of `pohadka` and `variacenarenesancnitema` are gone, and no song has a manual `\vspace` left. A song compiled alone (Overleaf, D-005) shows a framed name instead of the image.
- **Lint:** `\score{name}` without `scores/<name>.mscz` is an error, an unused `.mscz` a warning.
- **Reproducible:** the PDF conversion runs with `SOURCE_DATE_EPOCH=0`, so an export gives the same bytes every time; MuseScore may write the lyric dashes of `scarboroughfaircarthy` in another order between runs, but the image is identical (checked on five exports).
- **Web:** the same SVGs, transparent, chord names in the songbook's red; J2/J4 put them into `songs.json` and the release.
- Amends D-008 (the conversion goes SVG → PDF, not PDF → SVG) and confirms D-125 (J5's prototype is this). Not adopted: per-song offset arguments (they encoded the hand-cropping), cropping PDF exports with `pdfcrop` (MuseScore trims only PNG and SVG; the SVG also gives the staff position).

### D-137 · Chord sharps and flats are engraved music signs — Agreed (owner, 9 Nov 2026, session 23)
- The chord sharp `\kk` was the number sign `#` and the flat `\bb` the thin maths sign ♭, next to bold chord letters. Noticed next to the scores, whose chord names use engraved signs. Compared (owner chose E): `#`; the maths ♯/♭ (too thin); bold maths signs; the MusiXTeX music font at two sizes.
- `\kk` and `\bb` now print the sharp and flat of the MusiXTeX font (`musix20`, characters 92 and 90), raised like the other chord superscripts, scaled to twice the superscript size and lifted by their own depth so they stand on the baseline. Embedded as a Type 1 font. Needs `musixtex-fonts` (in the CI's TeX Live and on Overleaf; locally `texlive-music` or `tlmgr install musixtex-fonts`, README).
- 196 songs change (every song with a sharp or a flat), nothing else; every song still fits one page and no chords overlap.
- With it: `vimvim` wrote its bass sharps by hand (`A\#`, `D\#`), now `\kk`, and the lint reports `\#` in songs. Two chord typos fixed: `andelska` `E\bb m \7` (printed "E♭m 7") and `changetheworld` `C m\7` (printed "C m7"). A sharp in a bass note (`\bas{F\kk}`) keeps the proportion of the chord's own sharp (measured 1.07 against 1.05 of the letter height), so it needs no change.
- The converter and the web print `\kk` as ♯ (U+266F), `\bb` as ♭ (U+266D).

### D-138 · Editions: a folder per edition, its own front matter, its own version — Agreed (owner, 9 Nov 2026, session 23; E1); superseded by D-139 (9 Nov 2026)
An edition is a new songbook derived from the full one: it takes the songs it lists and the contents built from them, and has its own front matter. Use cases: `zpevnik-lite` (favourites, the main download on the website), `lidovky` (all its songs are already in the full book; the separate repository becomes an edition), a printed book such as a scout songbook (P1).
- **Definition:** `editions/<name>/edition.toml` with `title`, optional `subtitle`, `file` (PDF name), `publish` and `songs` (ids). The order of the list does not matter: songs are always in the D-107 collation. An unknown id is an error. Editions are built on demand (`make edition EDITION=<name>`) and in CI (E5); the full book is still `make`.
- **Front matter:** a file in `editions/<name>/` named like one in `preamble/` (`obalka`, `patitul`, `vydavatelskyzaznam`, `titulnilist`, `dedikace`, `uvod`) replaces it; every other one comes from `preamble/`. Extra pages: `editions/<name>/pred-pisnickami.tex` (before the songs) and `po-obsahu.tex` (after the contents). The base front matter takes the book's title, subtitle and versions from generated macros, so an edition without its own files is still correct, and the full book stays byte-identical.
- **Colophon:** an edition may bring its own `vydavatelskyzaznam.tex`; a check fails the build unless it prints the mandatory parts through the generated macros: the edition's name and version, the version of the full book it was built from, the build date and the link to the source (and the L1 notice once it exists).
- **Version:** the scheme of D-133 applied to the edition: `major.minor` = the edition's song count + 100, `patch` = first-parent commits since the last commit that changed the edition's song count. The colophon also names the full book's version it was built from.
- **Links and artists:** a `\seealso` to a song outside the edition is left out completely (no title, no link). Artist sections and the artist index list only artists with a song in the edition; the section threshold (D-119) does not apply.
- **Publishing:** `publish = "web"` puts the edition on the download page of `zpevnik-web` (`zpevnik-lite` as the main button, the full book as the second one at its current URL `zpevnik_last.pdf`, which printed QR codes point to; `lidovky` at its current URL); `publish = "release"` attaches it to the release only (print editions are for the owner and the printer). Every edition is attached to the release of its build, and the release notes list them all.
- **Hidden songs (L2)** are an exclusion list applied before the edition filter, so they are gone from every book.
- Replaces the defaults of E1 (one TOML file per edition, title and version only). The koledy songbook stays separate (not derived from the full book).

### D-139 · Editions, revised before E2: selection by song or artist, one colophon core, the build version — Agreed (owner, 9 Nov 2026); supersedes D-138; superseded in part by D-143 (front matter, page names, PDF name, output paths)
The design of editions after an architectural review of D-138, before its implementation. This entry is the complete design; the reasons for each change follow it.
An edition is a new songbook derived from the full one: it takes the songs it selects and the contents built from them, and may have its own front matter. Use cases: `zpevnik-lite` (favourites, the main download on the website), `lidovky` (all its songs are already in the full book; the separate repository becomes an edition), a songbook of one artist, a book for a group such as scouts (printed or not: the print format is a separate choice, see below).
- **The full book is an edition too:** the one without a filter. The generator, the build and the checks have one code path for every book; the full book only keeps its current output paths (`generated/`, `zpevnik.pdf`) and stays byte-identical.
- **Definition:** `editions/<name>/edition.toml` with `title`, optional `subtitle`, `file` (PDF name) and the selection: `songs` (song ids) and/or `artists` (registry slugs, artists or collections); the edition takes every song selected by either. The order does not matter: songs are always in the D-107 collation. An unknown key, song id or slug, or an empty selection is an error. Editions are built on demand (`make edition EDITION=<name>`) and in CI (E5); the full book is still `make`. An edition folder that is never committed is a private edition: it is built locally and published nowhere.
- **Front matter:** a file in `editions/<name>/` named like one in `preamble/` (`obalka`, `patitul`, `titulnilist`, `dedikace`, `uvod`) replaces it; every other one comes from `preamble/`. Extra pages: `pred-pisnickami.tex` (before the songs) and `po-obsahu.tex` (after the contents). The generator resolves this (in Python, not by TeX file lookup) and writes the edition's list of front-matter files; any other `.tex` file in the folder is an error, so a misspelt name never silently falls back to the base page. The base front matter takes the title, subtitle and version from generated macros, so an edition without its own files is still correct, and the full book stays byte-identical.
- **Colophon:** a generated core that no book replaces: the version (the build, D-133) and the build date, as in the full book today; in an edition also that it is a selection of N songs from the full book, and the link to the source; later the L1 notice in every book. Besides the core come additions: the full book's credits (today the cover and the proofreading) in `preamble/vydavatelskyzaznam.tex`, which an edition replaces with its own `vydavatelskyzaznam.tex`. An edition cannot remove the core, so there is nothing to check. Where the core and the additions sit on the page is E2's choice, as long as the full book stays byte-identical.
- **Version:** an edition has no version of its own. It is named by the build it comes from (D-133): `<file>-<version>.pdf`, and its colophon gives that version.
- **Page numbering:** as in the full book today (the usual book convention): the front-matter pages are counted but carry no number, numbers are printed from the first song on. The page counter is not set by hand, so an edition with more or fewer front-matter pages is numbered correctly. Rules of a printed book (the cover outside the book block, the songs starting on a right-hand page) belong to the print format (P3).
- **Links and artists:** a `\seealso` to a song outside the edition is left out completely (no title, no link, no space). The artist index and sections follow the same rules as in the full book (the registry's `section` flag, D-119), restricted to the artists with a song in the edition: no edition-specific rule, so editions never drift from the full book.
- **Checks:** every edition passes the one-page check and the lints; a link to a missing target fails the build (pdfTeX reports it in the log).
- **Format is not part of an edition:** an edition chooses songs and front matter, never page geometry. The print format (P3) combines with any edition, including the full book; every combination of edition and format has its own output directory.
- **Publishing:** every edition in the repository is attached to the release of its build, and the release notes list them all. What the download page offers (which editions, `zpevnik-lite` as the main button, the full book also at its fixed URL `zpevnik_last.pdf`, which printed QR codes point to) is configured in `zpevnik-web` (E6). No other PDF needs a fixed URL; the page may link to the release assets.
- **Hidden songs (L2)** are an exclusion list applied before the edition filter, so they are gone from every book.

Changes from D-138 and why:
- **Selection by artist as well as by id.** `lidovky` is exactly the 76 songs tagged `\artist{lidove}` (checked 9 Nov 2026), which match the 2020 lidovky book. An id list would copy what the songs already say (PLAN principle 1): every new folk song would have to be added in two places. It also makes a songbook of one artist a two-line file.
- **One colophon core, additions only** instead of an edition's own colophon plus a check that it still prints the mandatory parts: a colophon without them cannot be written, so the check is not needed (E3 lost that item).
- **No edition version.** The edition's own `major.minor.patch` would have needed the edition's song count at every past commit (a second version scheme with its own code), and its numbers would tell the reader nothing the build version does not. The edition is identified by its name and the build it comes from.
- **`publish` dropped.** The download page needs its own configuration anyway (the main button, the fixed URL), so a `publish` flag would have kept half of it in this repository. The songbook releases every edition; `zpevnik-web` decides what it shows. A private edition is one that is never committed. Only `zpevnik_last.pdf` needs a fixed URL (owner); `zpevnik_lidovky.pdf` does not.
- **Artist sections as in the full book** (owner: unification, so editions do not drift), instead of "no section threshold in an edition".
- **The full book is an edition without a filter**, so there are no edition special cases scattered through the generator, the Makefile, CI and the checks.
- **Format separate from edition:** a printed songbook may be a subset (P1); geometry in `edition.toml` would have tied the two together.
- **Front matter resolved in Python:** testable, and a misspelt replacement file is an error.
- **Page counter:** `zpevnik.tex` sets `\setcounter{page}{8}`, which assumes the full book's seven front-matter pages. LaTeX counts those pages by itself, so the line is probably redundant (not verified: the cover changes the page geometry); E2 removes it if the full book stays byte-identical, and otherwise derives the number.
- **Links checked from the log** instead of a separate link checker: pdfTeX already warns about a link to a missing target; E3 verifies that this catches the contents, `\seealso` and the artist links.

### D-140 · The songbook is never sold — Agreed (owner, 9 Nov 2026)
The songbook is and stays free: a free PDF and later a free website. Printed copies are not sold. P2 (licensing check before selling) is cancelled, and D-122's note on a sold book and PLAN WP7 item 4 no longer apply. A free PDF and a website are still a kind of "making available", so L1 (notice) and L2 (hide switch) stay, before WP6 goes online.

### D-141 · Legal notice and the scope of the licence — Agreed (owner, 9 Nov 2026), ticket L1
Reasonable effort, not legal advice (WP7).
- **Notice**, in Czech and English, in the colophon of every book (`preamble/upozorneni.tex`, part of the colophon core of D-139) and in the footer of every page of the website: the songbook is non-commercial and free; the copyright in the lyrics and music belongs to the authors; rights holders who do not want their song in it write to frantahluchnik@gmail.com and the song is removed. The two copies (PDF and web) are kept in step by hand: a short text in two repositories does not justify a shared data file; each copy says where the other is.
- **Licence scope:** the Apache License 2.0 in `LICENSE` had covered the whole repository, songs included, which the owner cannot license. A scope statement now precedes the unchanged licence text: it covers only the owner's own work (tools, tests, CI, Makefile, `zpevnik.sty`, the document structure, the artists registry, the docs). The songs (`pisnicky/`), the scores (`scores/`), the PDFs built from them, the front matter (`preamble/`, whose foreword quotes lyrics by Vlasta Redl) and the cover (`obrazky/`, by Ivana Vlčková) are not licensed. The README says the same in Czech. GitHub may stop showing "Apache-2.0" for the repository, which is correct for a repository with mixed content.
- Links to the web in the PDF are grey like the internal ones (`urlcolor`; the mail address is the first web link in the book).
- Still open in WP7: the hide switch (L2) and `noindex`/`robots.txt` for the online songbook (W6).

### D-142 · Print: the screen PDF scaled down; an own page geometry only as a trial — Agreed (owner, 9 Nov 2026), amends P1/P3
A5 is A4 scaled by 1/√2 (ISO 216), so the A4 PDF scales to A5 without any change of layout: no song spills, the one-page rule holds, and the screen PDF stays the only typeset source. The cost: the body text becomes ≈ 10 pt (from 14.4 pt) and the margins shrink to 70.7 % (2 cm left, 1 cm right become 14 mm and 7 mm), the same on every page, so a two-sided bound book needs an offset of odd and even pages towards the outer edge (or ring binding). The owner checks legibility on paper by printing A4 pages "2 per sheet".
- **The print format is a step after the build**: it takes the PDF of any edition (D-139) and scales it to the print page size, with the binding offset and the blank pages a printed book needs (songs starting on a right-hand page if P1 asks). No new LaTeX geometry, no fixes per song.
- **Trial in P3:** a LaTeX page geometry for the specific printed edition (P1), which may not contain the longest songs: report which songs spill and compare a few pages with the scaled version. The owner chooses; the scaled version is the default.
- Amends D-122 and the print notes of D-139 (the format is a scaling step, not a geometry, unless the trial wins).

### D-143 · Editions: the full book is one of them, an explicit page contract, English names, one build root — Agreed (owner, 10 Nov 2026, session 20); supersedes D-139 on front matter, page names, the PDF name and output paths
Agreed while planning E2. This entry is the complete design of what it changes; the rest of D-139 (selection, collation, links, artists, checks, publishing, hidden songs) stays.
- **English names** (rename R15, before E2, zero diff): `pisnicky/`→`songs/`, `obrazky/`→`images/`, `sablona.tex`→`song-template.tex`, `preamble/`→`shared-pages/` with `obalka`→`cover`, `patitul`→`halftitle`, `titulnilist`→`titlepage`, `vydavatelskyzaznam`→`imprint`, `upozorneni`→`notice`, `dedikace`→`dedication`, `uvod`→`introduction`, and `obsah.tex`→`shared-pages/contents.tex`. E2 then moves the full book's own pages (dedication, introduction, the credits) to `editions/full/`. Song ids, the name `zpevnik`, all Czech text and the README stay Czech.
- **Base book facts** live once, in `data/book.toml`: title (*Ještě mi chvilku zpívej*), author, start year, source link (`https://github.com/f-hluchnik/zpevnik`) and `base_edition = "full"`. The generator turns them into macros; no edition changes them. An edition only adds: its `title` (default: the book's), `subtitle`, `editors`.
- **The full book is the edition `full`** (`editions/full/`): its definition and its own pages. There is no base book that editions inherit from; an edition that reuses a page of another names it by path (`"../full/introduction.tex"`), so the sharing is visible.
- **Fixed skeleton:** cover, blank, halftitle, blank, title page, imprint (on the back of the title page), `before_songs`, songs, contents, `after_contents`. The title page is a right-hand page (Czech book practice). This order moves every song one page later, so it is its own ticket E8 after E2; until then E2 builds today's order (zero diff).
- **Pages:** cover, halftitle and title page are each declared in `[pages]` as `"shared"` (`shared-pages/<page>.tex`) or `"own"` (`editions/<name>/<page>.tex`). Every key is required, so a new replaceable page forces each edition to decide. The imprint and the contents are never replaced. Shared pages take their text from `book.toml` and `edition.toml`; the shared title page always prints the book's author, then the editors. An own title page may leave the author out: the imprint guarantees the attribution.
- **Imprint:** one page at the front, against the Czech convention of a copyright page plus a tiráž at the end (owner: at the end nobody would find it). A fixed core in every book: place and date, the version line, "vysázeno jazykem LaTeX", the legal notice (`shared-pages/notice.tex`, D-141). In every edition except the base one, the version line becomes the derivation sentence: *Výběr N písní ze zpěvníku Ještě mi chvilku zpívej (František Hluchník), verze 8.33.68, github.com/f-hluchnik/zpevnik.* One slot above the core: the edition's TeX fragment (`imprint = "<file>"`); the full book's credits are such a fragment. The stray `\hspace{10mm}` before the first credit is a bug; it goes in E8.
- **`edition.toml`:** `title`?, `subtitle`?, `editors`?, `cover_image` (with a shared cover only), `imprint`?, `before_songs`, `after_contents` (lists of the edition's files or another edition's by path), `[pages]`, and the selection: `all = true`, or `songs` and/or `artists` (D-139). Errors: an unknown or missing key, `all` together with a selection, `cover_image` with an own cover, a listed file that does not exist, a `.tex` file in the folder that nothing references. No `file` key: an edition's PDF in the release is `zpevnik-<edition>-<version>.pdf` (E5).
- **One derived root, `build/`** (gitignored): `build/scores/` (score images, shared), `build/songs/<id>.pdf` (`make song`), `build/editions/<name>/` (its generated `.tex` files in `generated/`, the PDF, LaTeX's auxiliary files). The root `generated/` and `zpevnik.pdf` are gone. Each edition has its own directory because LaTeX reads its auxiliary files back on the next run. The print format (D-142) is a step after the build that writes an output of its own, so the build path has no format level.
- **`make` is the only entry point.** The target says what, a variable says which: `make [pdf] [EDITION=<name>]` (default `full`), `make song SONG=<id>`, `make generate|scores|check|clean`. Each prints the path of what it built. `zpevnik.tex` stops with an error when compiled without an edition. The edition reaches the document as one definition on the latexmk command line (`-usepretex`); verified with TeX Live 2023 in session 20, together with the `.aux` subfolders the build must create in the output directory. Overleaf keeps working for a single song (`zpevnik.sty` alone).
- **Page counter:** `\setcounter{page}{8}` goes (verified in session 20: the full book is byte-identical without it).
- **Version across the rename:** `tools/build_version.py` counts song files under both `pisnicky/` and `songs/`, so the rename commit nets to zero and the patch keeps counting. After the first change of the song count after R15 (8.34.0) the old path is dropped (R16).
- **Zero diff after moving the output:** pdfTeX derives the PDF's `/ID` from the output file name, so a moved but otherwise identical PDF differs in its bytes. From E2 on, zero diff means the song-by-song diff plus identical rendered front-matter pages, not `cmp`.
- **Why:** D-139's base-plus-override model made `preamble/` both the full book's content and every edition's default, so a change to the full book silently changed other editions; `pred-pisnickami` and `po-obsahu` existed only to add pages to a model that could only replace them; and the full book kept output paths of its own. English names now, because E2 creates the first public names of editions and a later rename costs more. Not adopted: splitting the imprint into a copyright page and a tiráž at the end (nobody would see it); TeX in TOML strings for the credits (the slot is a file: one mechanism); a format level in the build path (print does not change the page numbers, D-142).
