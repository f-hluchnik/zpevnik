# Phase 11 tickets (done 6 Nov 2026)

The ticket texts and status rows of phase 11 as they were when the phase ended. Summary: [HISTORY.md](../../HISTORY.md), phase 11.

| Ticket | Status | Notes / PR |
|---|---|---|
| Q1 | done | zero diff; PR f-hluchnik/zpevnik#79. Found: tests/single-song.sh --build fails on master at spacing.tex (4 pages, expects 3), see Q3 |
| Q2 | done | zero diff, byte-identical `generated/`; PR f-hluchnik/zpevnik#80 |
| Q3 | done | PR f-hluchnik/zpevnik#81; CI runs tests/single-song.sh --build in texlive-action (TL 2023) |
| Q4 | done | PR f-hluchnik/zpevnik#82 (merged). 15 songs differ (ticket expected 8; owner accepted, see D-131 notes); `\nv` and `\lbl` kept for Q5 |
| Q5 | done | PR f-hluchnik/zpevnik#83 (merged). 15 songs differ (items 1–3 + idzepostaridze), reviewed by the owner; \textit→\emph zero diff; `\nv`/`\lbl` are lint errors now. Nitpick left: in zapomnetliva the repeat mark precedes the speaker name |
| Q5a | done | PR f-hluchnik/zpevnik#84 (merged): `\nv` → `\zp@labelindent`, `\lbl` → `\zp@boldlabel`; zero diff |
| Q5b | done | PR f-hluchnik/zpevnik#85 (merged): 7 stray paragraphs in `\vers`, lint for text outside blocks, 14 `= \cue{n}` lines without `\gap`; 20 songs differ, owner reviewed |
| Q6 | done | PR f-hluchnik/zpevnik#86 (merged): dead `\artistname`/`\artistlabel`, comments on the TeX tricks, hyphen test before an accented letter, IDs out of comments, `\zprule{\textwidth}`, `\large` reasons; only `mikymauz` differs (its trailing `\Large` set the coda's line spacing). Phase 11 is done when it merges |

# Phase 11 – Code quality (D-131)

The last part of the refactoring: the code as a senior engineer would leave it, without changing the book (except where Q4 and Q5 say so).

### Q1 · `zpevnik.sty` internals — [agent] · M · needs nothing
1. Order the file in sections, each with a one-line header: packages and PDF settings; page layout and named lengths; song header (`\song`, `\sub`, song id and target, artist links); blocks and labels; separators and vertical spacing; chords; chord symbols; song metadata; registry lookups; version. `\note` moves to the blocks, `\pdfminorversion` to the packages.
2. Comments in English, each saying *why* in a line or two, without ticket or decision IDs (they point to docs outside the repo).
3. Remove the `\makeatletter` / `\makeatother` pair inside the package: `@` is already a letter in a `.sty`, and after the `\makeatother` any later `@` macro would break. Remove dead code: the commented-out alternative `\chord`, the unused colour `chordblack`.
4. Internal macros use the `\zp@` prefix (`\zpsongid`, `\zpsongtarget`, `\zpartistreset` become `\zp@…`). The interface used by generated files (`\songinclude`, `\zpregisterartist`, `\zpversion`) stays public and gets a comment saying so.
5. Named constants for the remaining literal values: the 20 pt block gap (defined once, used by `\blocksep` and the `multicols` hook), the −10 mm paragraph indent, the artist-link position (0.98 `\paperheight`, 1 cm from the page edge, 1.5 em between two links), the −2 mm of `\groupbreak`, the dash pattern of `\blockrule`, the 2 mm in `\song`, and the 0.03 cm rule (also in `obsah.tex` and `tools/toc.py`: one macro used by all three).
6. Font commands: `\sc` becomes `\scshape` (note that `\sc` also does `\normalfont`; keep the output identical); size switches are used as switches (`\Large{$\circ$}` in `\dm`, `\large{…}` in `\hdm`, `\bb`); drop the useless `\expandafter` in `\sub`.
7. `\artist` with `\NewDocumentCommand{\artist}{o m}` (in the LaTeX kernel, TeX Live 2023) and one helper that builds a link, instead of the two copied branches and the sentinel default label. `\chords[sep]` likewise.

**Expected differences:** none, for the book and for `tests/*.tex`.

### Q2 · Python tools — [agent] · M · needs nothing
1. `tools/registry.py`: loading `data/artists.toml`, `Artist`, `normalise`, `derive_label` and the entry validation (today in `check_registry.py`, which `generate.py` imports for its model). `generate.py` and `lint.py` stop loading the TOML themselves. Drop the unused second return value of `check_entries` and the unused loop variable.
2. Repository paths (`pisnicky/`, `data/artists.toml`, `generated/`, `zpevnik.tex`, the trace file) as named constants in one place; no module hard-codes them.
3. One command-line style: `argparse` in every script, default root = the repository root (from `__file__`). Today `check_pages.py` and `chord_gaps.py` default to the current directory, `lint.py` reads `sys.argv`, `generate.py` uses argparse.
4. `generate.py`: one list of outputs and one write helper instead of five near-identical writes; the version counts the same song list as everything else; f-strings throughout.
5. Names: `tex()` → `escape_tex()`, `toc.py` → `letter_toc.py` (its partner is `artist_toc.py`), inline regexes in `check_pages.py` as named constants.
6. Ticket and decision IDs out of docstrings and comments; the reason stays.

**Expected differences:** none. `generated/` byte-identical to master (`diff -r`), lint output identical, unit tests green.

### Q3 · CI runs the test assertions — [agent] · S · needs nothing
`tests/single-song.sh --build` holds the real checks (artist links per page, metadata prints nothing, no chord overlap, spacing alignment), but CI only prepares the folder and compiles the five test files, so none of the checks run. Run the script with `--build` inside the pinned TeX Live 2023 and replace the five compile steps by that one step. `xu-cheng/texlive-action` documents `texlive_version`; verify it accepts 2023 and that its image has `pdfinfo` / `pdftotext` (else install poppler in that step). Show that a deliberately broken assertion turns CI red (a commit on the branch, reverted before review). Update the script's header, which says CI only compiles.

**Expected differences:** none in the book.

### Q4 · ⚠ Song command names — [agent] · L · needs Q1
Agreed in D-131. One PR. A one-off migration script with unit tests (nested braces!), deleted in the same PR or kept out of the repository. Counts from 6 Nov 2026; re-derive them.

| Today | Becomes |
|---|---|
| `\vers{n}{…}`, `\vers{}{…}` (unnumbered) | `\vers[n]{…}`, `\vers{…}` (`\verse` is LaTeX's `verse` environment) |
| `\refrain{…}`, `\refrainn{n}{…}` | `\chorus{…}`, `\chorus[n]{…}`; the label stays "R:" |
| `\solo`, `\solon{n}{…}` | `\solo{…}`, `\solo[n]{…}` |
| `\bridge`, `\prechorus` | also get `[n]` |
| `\cod` (101) | `\coda` |
| `\sub` (52) | `\subtitle` |
| `\spk` (10) | `\speaker` |
| `\hyl` (84) | `\seealso` |
| `\refsm{n}`, `\refsme{n}`, `\bridgesm{}`, `\solosm{n}`, hand-written repeat marks (`\textbf{1.}`, `\textbf{I.}`, `\textbf{S1.}`, `\textbf{6. 7. 8. R.}`, `= \gap{2}\textbf{1.}`) | `\cue{Rn}`, `\cue{B}`, `\cue{Sn}`, `\cue{1}`, `\cue{I}` … (prints the label and a dot, bold) |

- `\cue` decides by position, like `\note`: after an empty line (vertical mode) it is a block of its own with the block gap; written after a block or inside one, it is appended to the line.
- The block macros use `\NewDocumentCommand` (`o m`); an empty optional number means no number.
- No aliases for the old names (one way to write each thing); `tools/lint.py` reports each old name as an error, as C4 and V8 did.
- Out of the author's command set: `\hyt` and `\hylo` (only the generated contents use them: write `\hypertarget` / `\hyperlink` or an internal macro), `\nv` and `\lbl` (internal; the songs that still use them are Q5).
- Unchanged: the chord symbols (`\kk \bb \dm \hdm \maj \+ \2`–`\9 \add \sus \bas`), `\chord`, `\chords`, `\gap`, `\note`, `\rep`, `\rec`, `\groupbreak`, `\blockrule`, `\partrule`.
- `sablona.tex`, `tests/*.tex` and the README follow. The README's command reference (Czech) is rewritten from the style file: every author command with a one-line example. It fixes the known errors: `\solsm` (does not exist), "R s tečkou" (prints "R:"), `+` for `\+`, the missing `\refsme`, `\prechorus`, `\note`, `\hyl`, `\groupbreak`, and the link to `docs/…` outside the repository.

**Expected differences:** the 8 songs whose standalone repeat mark gets a block gap (brnojezlatalod, buchetjespousta, haubilouplani, letitbe, rekalasky, ringoffire, soske, tasidele); nothing else. Check that `\solosm` → `\cue` gives zero diff (it printed a label box).

### Q5 · Song source leftovers — [agent] + [you] · S · needs Q4
1. Blocks that start with `\nv` instead of an unnumbered `\vers{…}` (15 files on 6 Nov 2026, e.g. davidagolias, dezo, linda, skrhola; some are continuation lines inside a block and stay). - we should prefer `\vers{}` as we are moving away from the old commands adn `\nv` basicaly means "non-verse". Try to render all with `\vers` and export the differences. Owner checks them and approves/suggest changes.
2. `zapomnetliva`: the dialogue is written with `\lbl{A:}` / `\lbl{B:}` and `\nv{}`, while `motyl` uses `\speaker`. Owner decides: `\speaker{A}{…}`, or a speaker label in the label column. - use `\speaker`
3. `ahorsewithnoname`: the hand-made note `\nv\textit{\normalsize{…}}` becomes a `\note` or an unnumbered `\vers{\emph{…}}`. - the hand-made note becomes a `\note`.
4. **Song footnotes in `\song{}`** (`bellaciao`, `conselho`, `johnnybgoode`, `pasopanori`, `tasidele`, `thepassenger`, `acrosstheuniverse`): the footnote is about the whole song, not the title. Owner decides the final form before the converter (J1): keep `\footnote` in `\song{}` (the generators already drop it from the plain title), a `\songnote{}` after the header, or a visible note line. - As we can safely stript the `\footnote` from the title, keep it as is and strip it where needed.
5. Optional: `\emph` (87) and `\textit` (128) are used for the same thing. Unify to `\emph` only where it gives zero diff (`\emph` inside italics turns upright). - Perfect, prefer `\emph` everywhere.

**Expected differences:** the songs of items 1–3; the owner reviews each.

### Q6 · Last leftovers from the review — [agent] · S · needs Q5
From the review after Q1–Q5 (6 Nov 2026): remove `\artistname` and `\artistlabel` (never used; `\zpregisterartist` takes only slug, link label and section flag); comment the TeX tricks as intentional, each with what happens if it breaks (the UTF-8 letter test relies on a LaTeX internal, the lookahead stops at a closing brace, the two-row tabular of a chord, `\groupbreak` as a shortened empty line, the `\fi` jump in `\chords`); test the hyphen in a split word, also before an accented letter; ticket and decision IDs out of the last comments; `\zprule{\textwidth}` in `obsah.tex`; the reason comment for `\large` in `acrosstheuniverse` and `mikymauz`, and `mikymauz`'s trailing `\Large` removed. **Expected differences:** none (in fact `mikymauz`: the trailing `\Large` set the coda's line spacing).
