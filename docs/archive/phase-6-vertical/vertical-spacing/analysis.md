# Vertical spacing: analysis (V1)

Ticket V1 (session 12, 5 Nov 2026). No code changes. The owner approves or corrects each proposal in V2 (section 6). V3–V8 follow only what is approved.

**Base:** `zpevnik` master `88b5205` (C5 merged), 733 songs, 757 pages, built in the cloud workspace (TeX Live 2023, pdfTeX 1.40.25). Counts are re-derived and match INVENTORY B1/B2: `\ns` 300, `\cns` 4, `\vnv` 30, `\vinv` 92, `\lsp` 59, raw `\vspace` 133 (in 65 songs). None of them is commented out.

**Files next to this document** (`docs/vertical-spacing/`):
- `*.png`: one crop per sampled context, **as is | without the macro** (the macro and its argument removed only at the sampled places). The blue arrow marks where the macro is in the source.
- `occurrences.csv`: all 618 occurrences with their class (section 3) and whether the song still fits on one page without that macro.
- `scripts/`: the analysis scripts (occurrence list, instrumented build for the crop positions, crops, classes, this report). Only for reproducing the analysis; they are not project tools.

## 1. Summary

1. **The dominant intent is "make the song fit on one page".** If every `\ns` and `\cns` is disabled, 74 of the 88 songs that use them spill onto a second page. The same is true for 18 songs when the negative raw `\vspace` are removed and for all 6 songs with `\lsp`. `\vnv`, `\vinv` and the positive raw `\vspace` are never needed for fit.
2. **A shrinkable block gap does that job automatically.** With all `\ns`/`\cns` deleted and the block gap allowed to shrink to zero, only 2 songs still spill (both two-column). With V8's planned 20 pt minus 8 pt, 24 still spill (table in section 4).
3. So **`\ns`/`\cns` should not get a semantic replacement** (which would carry a print-only hack into the converter and the web as fake structure, against D-108). They should be deleted per song together with the shrinkable gap (V8). The remaining macros have real structural meanings, and each has a replacement that I verified to be pixel-identical (section 5).
4. Three verified exact mechanisms: `\groupbreak` for `\\`+`\vinv`, a "this separator replaces the next block gap" flag for `\lsp` (→ `\blockrule`) and the rule in `idzepostaridze` (→ `\partrule`), and the ticket's own V4 step `\vinv` → `\\[-2mm]`.
5. This changes the scope of V3–V8 (section 6, item 10). Nothing is changed until you approve it.

## 2. How the spacing works today

- Every block macro (`\vers`, `\refrain`, `\refrainn`, `\intro`, `\bridge`, `\prechorus`, `\solo`, `\solon`, `\solosm`, `\cod`, `\refsme`) starts with `\vspace{20pt}`. `\refsm` and `\bridgesm` do not. The song body is `\Large`, so the line distance is 18 pt.
- **Mode matters.** `\vspace` in a paragraph (horizontal mode) becomes a `\vadjust` and acts *after the line that contains it*. After a blank line (vertical mode) it acts right there. Most `\ns` stand after a block's closing `}` without a blank line, so they act after the block's last line.
- `\ns` = −20 pt: cancels the *next* block's 20 pt, so the next block follows like the next line. `\cns` = −35 pt: the same plus 15 pt more.
- `\vinv` = `\vspace{-2mm}\\`. It always follows a `\\`, so `…\\ \vinv` is an **empty line** minus 2 mm: a gap of about two-thirds of a line inside a block.
- `\vnv` = +25 pt after the current line: the gap before an unlabelled (`\nv`) block, 5 pt larger than the labelled block gap.
- `\lsp{w}` = −13 pt, a dashed rule `w` cm long, −23 pt. Followed by the next block's +20 pt, the blocks end up about as close as two lines, with the rule between them. It is therefore also a space saver.
- `\note` has a built-in −20 pt after the note line, so a note on its own line attaches to the following block (80 of the 99 `\note` uses are a line at the top of a song, typically the capo). Several raw `\vspace` exist only to undo or extend that (classes R4, R5).

## 3. Classes, intent and proposals

Classes are defined by their source context so that V5/V7 can find them mechanically. Every occurrence's class is in `occurrences.csv`. "Exact" means pixel-identical in the song-by-song diff at 150 dpi (section 5).

### `\ns` (300) and `\cns` (4)

| Class | Context | Count | Intent | Proposal | Exact equivalent |
|---|---|---|---|---|---|
| **N1** squeeze | after a block, or right after the title (65), also stacked with `\vspace`, around `multicols`, after a capo `\note` | 296 + 4 `\cns`, 87 songs | **Fit:** 74 of these songs spill without them. In the other 13 songs it is a habit or style (list below), mostly right under the title. | **Delete in V8**, song by song, together with the shrinkable gap; `check_pages` guards fit. No new macro. | If you want to keep a specific attachment: `\attach` (the next block skips its gap). Exact in 720 of 733 songs; see section 5. |
| **N2** part rule | `\ns` + `\begin{center}\rule{18cm}{0.03cm}\end{center}` + `\ns` | 4 (2 rules), `idzepostaridze` | Separate the language versions of the song | `\partrule` (full-width rule that replaces the next block gap) | **Exact** (Z5) |

Songs where `\ns`/`\cns` are *not* needed for fit (deleting them only adds space): barbarskepobrezi, cernymuz, cervenarekatucny, idzepostaridze (that is N2), koberecek, nadejeatouhy, nemusibejt, pianoman, povestehovejs, scarboroughfaircarthy, tesar, thetimestheyareachangin, tresnicky, walkingbacktohappiness.

![N1 between blocks: alisongross](ns-02-alisongross.png)
![N1 under the title: mladickabasnirka](ns-10-mladickabasnirka.png)

### `\vinv` (92)

| Class | Context | Count | Intent | Proposal | Exact equivalent |
|---|---|---|---|---|---|
| **I1** line-group break | `…\\` then `\vinv` inside a block | 90 | Split a long block into groups of lines (half-verses, couplets) | `\groupbreak` replaces `\\`+`\vinv`: one macro, defined once in `zpevnik.sty` | **Exact** (Z4). V4 as written (`\vinv` → `\\[-2mm]`) is exact too (Z3) but leaves `\\ \\[-2mm]` in the song: an empty line minus 2 mm, i.e. the hidden mechanism moved into the song. |
| **I2** after a closing brace | `…\\` `}` `\vinv` `\nv …`, only `vlese` (2) | 2 | An unlabelled continuation directly after a verse | Same `\groupbreak` after the `}`, with the inner trailing `\\` removed | Not built; V4 verifies |

![I1: jez](vinv-04-jez.png)

### `\vnv` (30, 16 songs)

| Class | Context | Count | Intent | Proposal | Exact equivalent |
|---|---|---|---|---|---|
| **U1** unlabelled block gap | between `\nv` paragraphs in songs without verse numbers; also before a `\rec` or `\note` block | 30 | Block gap for blocks without a label | **Unnumbered verse `\vers{}{…}`**: `\vers` with an empty number prints no label (today it would print "."), and the empty label box has the same width as `\nv`. Each unlabelled block is wrapped, the first one too. No new macro; the converter sees a verse without a number. | Not exact: the gap becomes the block gap (20 pt, today 25 pt), and the first block gets the 20 pt under the title that labelled songs already have. Not built. |

The same proposal covers raw-`\vspace` class R3 (35 more gaps between unlabelled blocks, mostly `\vspace{5mm}`, used instead of `\vnv`).

### `\lsp` (59, 6 songs)

| Class | Context | Count | Intent | Proposal | Exact equivalent |
|---|---|---|---|---|---|
| **L1** dashed rule | between two blocks, always on its own paragraph; one width per song (10, 12 or 17 cm) | 59 | Separate verses by a dashed rule *instead of* a blank gap, which also saves space (all 6 songs spill without it) | `\blockrule{w}`: same drawing, but it **replaces** the next block's gap instead of cancelling it with −23 pt (which would go wrong once the gap shrinks) | **Exact** (Z5) |

In 4 of the 6 songs every gap is a rule. A per-song switch ("this song separates blocks with rules") would be simpler to write, but it is not exact for `jenamteplo` and `zpatkydotrenek`. I don't propose it now.

![L1: nepijjanonepijvodu](lsp-08-nepijjanonepijvodu.png)

### Raw `\vspace` (133, 65 songs)

These are pre-classes by context. V7 confirms each one.

| Class | Context | Count | Intent | Proposal |
|---|---|---|---|---|
| **R1** squeeze | negative, between blocks (34) or under the title (6), often stacked with `\ns` | 40 | Fit (removing all negative `\vspace` spills 18 songs) | Delete in V8 with N1 |
| **R2** score alignment | negative, before `\hspace` + `\includegraphics` in an `\intro`/`\solo`/`\refrain` (mostly −20 … −58 pt) | 20 | Put the score image level with its label | A `\score[width]{file}` macro that aligns the image with the label automatically; not exact (each value was tuned by eye); prototype in V7. J5 (scores to SVG) touches the same places. |
| **R3** unlabelled block gap | positive, between `\nv` blocks | 35 | Same as `\vnv` | `\vers{}{…}` (U1) |
| **R4** before a note / recitation | positive, before a `\note` or `\rec` on its own paragraph (9–20 pt; one 100 pt) | 18 | Separate a trailing or mid-song note/recitation like a block | Block gap (via U1 or a block-level note); small differences |
| **R5** after a top note | positive, after a capo `\note`, before the first block | 6 | Undo `\note`'s built-in −20 pt | Depends on decision 9 (`\note`) |
| **R6** column break | ≥ 50 pt in a two-column song (`promeny`, `vodavodenka`) | 2 | Force a column break | `\columnbreak` (multicol); not exact (column balancing) |
| **R7** other gaps | positive, elsewhere (dialogue turns `On:`/`Ona:` in `motyl`, `P. S.` in `barborapiseztabora`, gaps next to `\lsp`, before a closing `\rec`…) | 12 | Various | Case by case in V7 (keep with `% reason`, or one of the above) |

![R1: pianoman](vspace-13-pianoman.png)
![R2: deepriverblues](vspace-06-deepriverblues.png)

## 4. Fit experiments

Each row is one full build of master with a change applied to all songs. "Spill" = more than one page (`check_pages`).

| Variant | Songs that spill |
|---|---|
| All `\ns` and `\cns` removed, gap fixed at 20 pt | **74** (of the 88 songs using them) |
| … and block gap 20 pt minus 8 pt (V8's starting value) | 24 |
| … minus 10 pt | 20 |
| … minus 12 pt | 16 |
| … minus 14 pt | 10 |
| … minus 16 pt | 7: babickamary, dontstopmenow, malujzaseobrazky, milionar, noe, summernights, zumzumII |
| … minus 20 pt (gap may shrink to zero) | **2**: babickamary, milionar (both two-column) |
| … minus 8 pt and no gap before the first block of a song | 20 |
| All `\lsp` removed | 6 (every `\lsp` song) |
| All negative raw `\vspace` removed | 18 |
| All positive raw `\vspace`, all `\vnv` or all `\vinv` removed | 0 |

TeX shrinks all gaps on a page by the same amount, and normally only on a page that would otherwise spill (but see the caveat below). A song that needs the full 20 pt therefore looks as it does today with `\ns` everywhere, while a song that is a few points too long loses a fraction of a point per gap. Removing the "first block" gap helps only 4 songs, so I don't propose it.

**Caveat:** a shrinkable gap is *not* zero-diff on today's master. With 20 pt minus 8 pt (or minus 20 pt) and nothing else changed, 727 songs are unchanged and 6 change: the two-column songs `babickamary`, `milionar`, `promeny` and `vodavodenka` (multicol uses the shrink when it balances columns) plus `illbethereforyou` (a 3-pixel change) and `tophatbarandgrill` (all lines up to 7.3 pt higher). Those two fit today. I could not determine why TeX shrinks them; V8 should review them.

## 5. Verification of the exact equivalents

Scratch builds of master `88b5205` (never pushed), compared with `tools/pdfdiff.py` at 150 dpi, plus `check_pages`:

| Build | Change | Result |
|---|---|---|
| Z3 | V4 as written: every `\vinv` → `\\[-2mm]` | 733 unchanged |
| Z4 | 90 × `\\`+`\vinv` → `\groupbreak` (`\newcommand{\groupbreak}{\\\vspace{-2mm}\\}`); the 2 I2 left as they are | 733 unchanged |
| Z5 | Block gap through a flag (`\ifzp@nogap` skips the next `\vspace{20pt}`, `\song` resets it); 59 × `\lsp` → `\blockrule{w}` = `\vspace{-13pt}\nv\hdashrule{#1cm}{1pt}{3pt}\vspace{-3pt}` + flag; the 2 rules in `idzepostaridze` → `\partrule` = `\vspace{-20pt}\begin{center}\rule{\textwidth}{0.03cm}\end{center}` + flag | 733 unchanged |
| Z6 | Z5 plus 283 × `\ns` (title and between-block ones) → `\attach` (flag only) | 720 unchanged, 13 changed. 8 of them have a `\ns` followed by a capo `\note` or a `\vspace` instead of a block, so the skipped gap is a different one (expected): aztosemnusekne, malujzaseobrazky, melanaocichbryle, nemusibejt, nowhereman, obladioblada, potopa, sprostyadmindusan. The other 5 (dance, ejhorahora, illbethereforyou, ourlastsummer, zapomenutytrumf) change although every `\ns` there is followed by a block. Measured in `zapomenutytrumf`: the gap after verse 1 is 16.75 pt smaller, the other gaps are the same. Cause not determined (removing the space after the `}` is not it). |
| Z1, Z2 | Block gap 20 pt minus 8 pt / minus 20 pt, nothing else | 727 unchanged, 6 changed (section 4, caveat) |

The crops come from an instrumented build that writes the page position of every occurrence. Its PDF is identical to master except `morseovka`, where a marker next to a `\vspace` shifts one space; its crop positions are still right.

## 6. For V2: your decisions

Mark each item **OK** or write the correction. Items 1, 2 and 10 are the ones that matter most.

1. **N1/R1 are fit hacks.** `\ns`, `\cns` (296 + 4) and the negative squeeze `\vspace` (40) get no semantic replacement; they are deleted song by song in V8, together with the shrinkable gap, and every song with any of them changes its spacing. In one song, delete them all at once: a kept `\ns` next to a shrinkable gap could shrink below zero. Keep `\attach` (exact) only for attachments you want to keep on purpose. — **…**
2. **Shrink amount for V8:** "minus 20 pt" (gap may shrink to zero where needed; 2 songs left, both two-column) or a visible minimum (e.g. minus 12 pt: 16 songs left for a per-song decision: tighten, split or allow-list, PLAN WP3). I recommend minus 20 pt, with V8's visual review of every changed song. — **…**
3. **`\groupbreak`** for `\\`+`\vinv` instead of `\\[-2mm]` in V4 (both exact). — **…**
4. **Unnumbered verse `\vers{}{…}`** for unlabelled blocks (U1, R3), first block included; gaps become the block gap. — **…**
5. **`\blockrule{w}`** for `\lsp` (exact); or keep the name `\lsp` with the new definition. — **…**
6. **`\partrule`** for the two rules in `idzepostaridze` (exact). — **…**
7. **Score images (R2):** prototype a `\score` macro in V7, or keep the raw `\vspace` with a `% reason` until J5. — **…**
8. **Column breaks (R6):** `\columnbreak` in `promeny` and `vodavodenka`. — **…**
9. **`\note`:** its built-in −20 pt only makes sense for a note at the top (80 of 99 uses). Keep it and just name it in V6 (as ticketed), or split into a top note (attaches to the first block) and a note without spacing, which would remove classes R4/R5. — **…**
10. **Ticket scope**, if 1–9 are approved:
    - V3: `\blocksep` *and* the next-gap flag (zero diff).
    - V4: `\groupbreak` (90 + the 2 I2).
    - V5: N2, L1, U1 + R3 (no longer `\ns`/`\cns`). Expected differences: none for N2/L1, about 5 pt per gap in the 16 `\vnv` songs, and the R3 gaps.
    - V6: as ticketed, plus decision 9.
    - V7: R2, R4–R7 (58). R1 moves to V8.
    - V8: shrinkable gap; delete N1 and R1 per song; review the 6 songs from the caveat; report what still spills.

    — **…**

## 7. Other findings (out of scope, not analysed)

- `zpevnik.sty` redefines the TeX primitive `\everypar` as a macro (`\def\everypar{\parindent=-10mm}`), so LaTeX internals that call `\everypar{…}` run differently than intended. It works today; it is a risk for any future change around paragraphs (the converter is unaffected).
- `zpevnik.log` reports one overfull line (20.9 pt too wide) in `pohoda`.

## Appendix: sampled contexts

20 random contexts per macro (all 4 for `\cns`), chosen with Python `random.Random(12)`. Each shows the source (the marked line is the macro) and the crop **as is | without it**. Class and fit status as in section 3.

### `\ns`: 20 sampled contexts
<details><summary>Show the samples</summary>

**1. `acrosstheuniverse` line 9**, page 12 · class **N1** · song spills without
```tex
  \includegraphics[width=515pt]{scores/acrosstheuniverse.pdf}
  }
> \ns
  \vspace{-10pt}
  
```
![acrosstheuniverse line 9](ns-01-acrosstheuniverse.png)

**2. `alisongross` line 33**, page 16 · class **N1** · song spills without
```tex
  \uv{Kdybys jen chtěl se mým milencem stát, tak dostal bys vše, co bys jenom chtěl.}
  }
> \ns
  
  \vers{5}{
```
![alisongross line 33](ns-02-alisongross.png)

**3. `dvakrat` line 9**, page 123 · class **N1** · song spills without
```tex
  \includegraphics[width=515pt]{scores/dvakrat.pdf}
  }
> \ns
  
  \vers{1}{
```
![dvakrat line 9](ns-03-dvakrat.png)

**4. `dvakrat` line 17**, page 123 · class **N1** · song spills without
```tex
  skupina spustila \uv{Andulko Šafářova}
  }
> \ns
  
  \vers{2}{
```
![dvakrat line 17](ns-04-dvakrat.png)

**5. `ejhorahora` line 40**, page 127 · class **N1** · song spills without
```tex
  Tady nám nedali, tady nám dajú, komára zabili, slaninu majú.
  }
> \ns
  
  \vers{3}{
```
![ejhorahora line 40](ns-05-ejhorahora.png)

**6. `feleenazelpasa` line 35**, page 139 · class **N1** · song spills without
```tex
  Pak přišlo to štěstí, vstoupil jí do cesty muž, kterej jinej než ty, co dřív znala se zdál.\\
  }\refsm{}
> \ns
  
  \vers{5}{
```
![feleenazelpasa line 35](ns-06-feleenazelpasa.png)

**7. `hladiny` line 30**, page 171 · class **N1** · song spills without
```tex
  rezaví sejf a houstne med, čeří se, čeří, hladiny.
  }
> \ns
  
  \bridge{
```
![hladiny line 30](ns-07-hladiny.png)

**8. `koberecek` line 2**, page 275 · class **N1** · song fits without
```tex
  \song{Kobereček} \artist{pokac}
> \ns
  
  \refrainn{1}{
```
![koberecek line 2](ns-08-koberecek.png)

**9. `letosmonikou` line 4**, page 309 · class **N1** · song spills without
```tex
  \artist{}
  \hyl{inthesummertime}{In the Summertime}
> \ns
  
  \vers{1}{
```
![letosmonikou line 4](ns-09-letosmonikou.png)

**10. `mladickabasnirka` line 4**, page 354 · class **N1** · song spills without
```tex
  \artist{jaromirnohavica}
  
> \ns
  \vers{1}{
  \chord{G}Mladičká básnířka \chord{Hm}s korálky nad kotní\chord{Em}ky, \chord{D}\\
```
![mladickabasnirka line 4](ns-10-mladickabasnirka.png)

**11. `nadejeatouhy` line 26**, page 385 · class **N1** · song fits without
```tex
  }
  
> \ns
  \bridge{
  Pak \chord{Hm\7}víčka sevřená a \chord{Bm\7}jen se nedívat,\\
```
![nadejeatouhy line 26](ns-11-nadejeatouhy.png)

**12. `nemusibejt` line 2**, page 403 · class **N1** · song fits without
```tex
  \song{Nemusí bejt} \artist{michalhorak}
> \ns
  
  \note{capo 4}
```
![nemusibejt line 2](ns-12-nemusibejt.png)

**13. `noe` line 19**, page 415 · class **N1** · song spills without
```tex
  kde by mohla jeho archa stát.
  }
> \ns
  
  \vers{2}{
```
![noe line 19](ns-13-noe.png)

**14. `noe` line 51**, page 415 · class **N1** · song spills without
```tex
  a v těle zahříval ho rum.
  }
> \ns
  
  \vers{6}{
```
![noe line 51](ns-14-noe.png)

**15. `prazce` line 65**, page 486 · class **N1** · song spills without
```tex
  pak praštili mě pražcem a já jsem tvrdě spal.
  }
> \ns
  
  \refrainn{3}{
```
![prazce line 65](ns-15-prazce.png)

**16. `skupinovefoto` line 35**, page 551 · class **N1** · song spills without
```tex
  motorista za tu dobu nězarobi na blatnik a mala ručička něoběhne cifernik.
  }
> \ns
  
  \vers{5}{
```
![skupinovefoto line 35](ns-16-skupinovefoto.png)

**17. `sprostyadmindusan` line 2**, page 562 · class **N1** · song spills without
```tex
  \song{Sprostý admin Dušan} \artist{pokac}
> \ns 
  \note{(capo 3)}
  
```
![sprostyadmindusan line 2](ns-17-sprostyadmindusan.png)

**18. `summernights` line 30**, page 572 · class **N1** · song spills without
```tex
  I saved her life, she nearly drowned. He showed off, splashing around.
  }
> \ns
  
  \prechorus{
```
![summernights line 30](ns-18-summernights.png)

**19. `tophatbarandgrill` line 44**, page 624 · class **N1** · song spills without
```tex
  at the Top Hat Bar and Grille.
  }
> \ns
  
  \refrainn{3}{
```
![tophatbarandgrill line 44](ns-19-tophatbarandgrill.png)

**20. `zapomenutytrumf` line 31**, page 713 · class **N1** · song spills without
```tex
  přeci přidej, gizde, zaber, bo sme posledni!
  }
> \ns
  
  \vers{4}{
```
![zapomenutytrumf line 31](ns-20-zapomenutytrumf.png)

</details>

### `\cns`: 4 sampled contexts
<details><summary>Show the samples</summary>

**1. `nepijjanonepijvodu` line 2**, page 407 · class **N1** · song spills without
```tex
  \song{Nepij, Jano, nepij vodu} \artist{lidove}
> \cns
  
  \vers{1}{
```
![nepijjanonepijvodu line 2](cns-01-nepijjanonepijvodu.png)

**2. `summernights` line 3**, page 572 · class **N1** · song spills without
```tex
  \song{Summer Nights}
  \artist{}
> \cns
  
  \intro{\bas{D DG GA AG A G}}
```
![summernights line 3](cns-02-summernights.png)

**3. `summernights` line 35**, page 572 · class **N1** · song spills without
```tex
  Summer sun, something's begun, but uh-oh those summer nights. Oh ela ela ela ooh.
  }
> \cns
  
  \refrainn{2}{
```
![summernights line 35](cns-03-summernights.png)

**4. `summernights` line 41**, page 572 · class **N1** · song spills without
```tex
  Tell me more, tell me more, did she put up a fight? \rep{Aha-tu-dub} tu-dub-dub-dub.
  }
> \cns
  
  \bridge{
```
![summernights line 41](cns-04-summernights.png)

</details>

### `\vinv`: 20 sampled contexts
<details><summary>Show the samples</summary>

**1. `bratrickuzavirejvratka` line 5**, page 54 · class **I1**
```tex
  \chord{Em}Bratříčku, nevzlykej, to nejsou \chord{G}bubáci,\\
  \chord{D}vždyť už jsi velikej, to jsou jen \chord{H\7}vojáci,\\
> \vinv
  \chord{C}přijeli v hranatých železných maringot\chord{H\7}kách.\\
  Se slzou na víčku hledíme na sebe,\\
```
![bratrickuzavirejvratka line 5](vinv-01-bratrickuzavirejvratka.png)

**2. `coztebebude` line 28**, page 71 · class **I1**
```tex
  Možná by ale někdy stálo za to říct,\\
  že život je i něco víc.\\
> \vinv
  Víc než do kanclu z kanclu splácet hypotéku\\
  a ke kafi si ráno dát tři cukry a hrst léků.\\
```
![coztebebude line 28](vinv-02-coztebebude.png)

**3. `hajnyjelesapan` line 15**, page 159 · class **I1**
```tex
  \chord{D}Že by pytlák, lesní pych?\\
  Já tu meškám v pantoflích.}\\
> \vinv
  \chord{B}Klidně si zůstaňte v domácí obuvi,\\
  \chord{G}klukům to nevadí, \chord{A}dívky vás omluví.
```
![hajnyjelesapan line 15](vinv-03-hajnyjelesapan.png)

**4. `jez` line 9**, page 243 · class **I1**
```tex
  \chord{Em}Jenda \chord{A\7}Benda \chord{D}nemožný je \chord{H\7}zadák,\\
  \chord{E\7}nemá vlohy a je \chord{A\7}laj, laj, lajdák.\\
> \vinv
  On \chord{D}ví, že šumí les, že \chord{H\7}vysouší se mez,\\
  že v \chord{E\7}dáli hárá pes, že \chord{A\7}kvete bílý bez\\
```
![jez line 9](vinv-04-jez.png)

**5. `jez` line 21**, page 243 · class **I1**
```tex
  Jenda Benda sjel na vodu mělkou,\\
  spáchal v lodi díru vel, vel, velkou.\\
> \vinv
  Já měl náladu zlou, on zničil keňu mou,\\
  už nikdy, houpy hou, s ní nepopluji mhou.\\
```
![jez line 21](vinv-05-jez.png)

**6. `jinetonebude` line 27**, page 245 · class **I1**
```tex
  Za obzorem v dálce jedou kombajny, postavme se kamarádi do lajny.\\
  Jeden rok a nebo už jen den, na koho to slovo padne, půjde ven.\\
> \vinv
  S počasím a pitomcema nervu se, to jsou ta moje dlouhá léta v cirkuse.\\
  Ať už horor nebo pohádku, čtu to všechno pěkně řádek po řádku.
```
![jinetonebude line 27](vinv-06-jinetonebude.png)

**7. `pohadka` line 26**, page 470 · class **I1**
```tex
  A stíny ořechů orvaných dohola pletou se letícím kočárům pod kola.\\
  Šmudla si přivezl v odřeným Wartburgu kámošku z dětství, prej nějakou Sněhurku.\\
> \vinv
  Vrátný se zohýbá pro tučné spropitné, a kdo mu proklouzne, tak toho nechytne.\\
  Kouzelník za dvacku vykouzlí pět bonů a vítr na věži opřel se do zvonů.\\
```
![pohadka line 26](vinv-07-pohadka.png)

**8. `pohadka` line 32**, page 470 · class **I1**
```tex
  Honzové, princové, víly i sudičky chopí se poháru, nože i vidličky.\\
  \uv{Na zdraví nevěsty, na zdraví ženicha!}, dvě sousta do kapsy a jedno do břicha.\\
> \vinv
  Náhle se za oknem objevil skřítek, rozhrnul oponu z máminých kytek,\\
  pěkně se usmál a pěkně se podíval, a pak mi potichu do ucha zazpíval.
```
![pohadka line 32](vinv-08-pohadka.png)

**9. `pohoda` line 6**, page 471 · class **I1**
```tex
  Když jsem \chord{Dm}se ho ptal, jakpak \chord{G\7}dneska je, říkával: \chord{C}pohoda. \chord{Dm\7}\\
  \chord{G\7}Měl \chord{C}malej byt, ženu a \chord{Em}dvě děti, v pět vstával \chord{Am}do práce\\
> \vinv
  domů šel \chord{C}v půl třetí, noviny \chord{Dm\7}pod paží, cukroví \chord{G\7}pro děti, zkrátka \chord{C}poho
  \chord{Dm\7}Po domě se \chord{G\7}povídalo: \chord{C}ten má asi \chord{Am}příjem,\\
```
![pohoda line 6](vinv-09-pohoda.png)

**10. `skrhola` line 14**, page 584 · class **I1**
```tex
  \vinv
  \chord{G}Zbývá jen abychom \chord{D}k tomu dodali, že \chord{A\7}v tu ránu \chord{Hm}je po vo\chord{E\7}se a p
> \vinv
  Chtěl bych radit, nijak vás však nenutím:\\
  Malé věci řešte ruky mávnutím.\\
```
![skrhola line 14](vinv-10-skrhola.png)

**11. `swingmodrezdi` line 6**, page 579 · class **I1**
```tex
  \chord{Dm\6}Povím vám \chord{Am\6}příběh, \chord{Dm\6}jenž se věru \chord{Am\6}stal,\\
  když \chord{Dm\6}osamělý \chord{Am\6}chlapec \chord{E\9}smutný status \chord{Am\6}psal.\\
> \vinv
  Cítí se opuštěně, žádná nejde svést,\\
  když náhle v pravém horním rohu zářil friend request.
```
![swingmodrezdi line 6](vinv-11-swingmodrezdi.png)

**12. `swingmodrezdi` line 30**, page 579 · class **I1**
```tex
  \uv{Čauky, mňauky, prosím tebe, odkud ty mě znáš?\\
  Tebe bych si nepřidala, rychle si mě smaž!}\\
> \vinv
  A tak chlapec dopsal status: \uv{\dots v tomhle světě nezůstanu ani za litr,\\
  nevymlouvejte mi to, jdu balit na Twitter!}
```
![swingmodrezdi line 30](vinv-12-swingmodrezdi.png)

**13. `tramvajacka` line 20**, page 626 · class **I1**
```tex
  My jsme tramvajáci, kluci z Motola, Prahu obrážíme kolem dokola.\\
  Harfa Bubny, Klárov, Sparta, Prašný most, někdy toho máme opravdu už dost.\\
> \vinv
  Na svou šedou uniformu tramvaják je hrdý,\\
  na toho, kdo škubne dveřma, na toho je tvrdý.\\
```
![tramvajacka line 20](vinv-13-tramvajacka.png)

**14. `trpaslicisvatba` line 5**, page 630 · class **I1**
```tex
  \vers{1}{
  \chord{G}V lese, jó v lese \chord{C}na jehli\chord{G}čí, koná se svatba \chord{A}trpasli\chord{D\7}čí,\\
> \vinv
  \chord{G}žádná divná \chord{C}věc to ne\chord{H\7}ní, \chord{C}Šmudla \chord{C\kk\dm}už má \chord{G}po voj\cho
  Malou má ženu, malinkatou, s malým věnem, malou chatou.\\
```
![trpaslicisvatba line 5](vinv-14-trpaslicisvatba.png)

**15. `velrybarskavyprava` line 35**, page 671 · class **I1**
```tex
  Když jsme domů připluli, už psal se příští rok,\\
  starej rejdař povídá, že nedá ani flok.\\
> \vinv
  \uv{Místo velryb v grónským moři zajímal vás grog,\\
  tuhle práci zaplatil by asi jenom cvok.}
```
![velrybarskavyprava line 35](vinv-15-velrybarskavyprava.png)

**16. `velrybarskavyprava` line 43**, page 671 · class **I1**
```tex
  Tohleto nám neměl říkat, teď to dobře ví,\\
  stáhli jsme mu kůži z těla, tomu hadovi.\\
> \vinv
  Z paluby pak slanej vítr jeho tělo smet,\\
  máme velryb plný zuby, na to vezmi jed!
```
![velrybarskavyprava line 43](vinv-16-velrybarskavyprava.png)

**17. `vjednymdumku` line 18**, page 653 · class **I1**
```tex
  taky to był dobrotisko,\\
  ale robka teho chłopka rada nimjała.\\
> \vinv
  Štvero novych šatu, štvero střevice,\\
  do kosteła nešła enem k muzice,\\
```
![vjednymdumku line 18](vinv-17-vjednymdumku.png)

**18. `vlese` line 18**, page 654 · class **I2**
```tex
  však na cestu mi daj raw gulaš a z flanelu košili.\\
  }
> \vinv
  \nv
  A tak \chord{F}šel jsem tam, však byl jsem zpátky hned,\\
```
![vlese line 18](vinv-18-vlese.png)

**19. `vodauzjesvarena` line 12**, page 687 · class **I1**
```tex
  \chord{Am}Ještě toho večera \chord{G}říkal táta \chord{C}Mařeně:\\
  \uv{\chord{D}Ještě taháš kačera, \chord{E}tak se chovej zodpovědně.}\\
> \vinv
  Řekla na to Mařena: \uv{Neboj, já pít nebudu,\\
  neudělám ostudu, jako, že jsem Mařena.}
```
![vodauzjesvarena line 12](vinv-19-vodauzjesvarena.png)

**20. `zlatestrevicky` line 5**, page 726 · class **I1**
```tex
  \vers{1}{
  Moje \chord{D}střevíčky jsou jako ze zlata, když je mám, připadám si hrozně \chord{A\7}bohatá.\\
> \vinv
  Ty si vezmu jen v onen slavný den,
  až si sednem do kočáru ty a \chord{D}já.\\
```
![zlatestrevicky line 5](vinv-20-zlatestrevicky.png)

</details>

### `\vnv`: 20 sampled contexts
<details><summary>Show the samples</summary>

**1. `botyprotilasce` line 30**, page 52 · class **U1**
```tex
  prý v těchto botách jdu, a tak si šlapu po štěstí.
  }
> \vnv
  
  \nv\emph{rec:} Pozor, boty! Pochodem v chod!
```
![botyprotilasce line 30](vnv-01-botyprotilasce.png)

**2. `dobreminenarada` line 15**, page 113 · class **U1**
```tex
  Běž domů, Ivane, a už se nevra\chord{A}cej.
  }
> \vnv
  
  \rec{Ivan byl původně moc hodnej hoch.\\
```
![dobreminenarada line 15](vnv-02-dobreminenarada.png)

**3. `dobreminenarada` line 23**, page 113 · class **U1**
```tex
  
  \refsme{}
> \vnv
  
  \rec{No tak, Ivane, co je s tebou?\\
```
![dobreminenarada line 23](vnv-03-dobreminenarada.png)

**4. `idzepostaridze` line 5**, page 206 · class **U1**
```tex
  \sub{O poštaris avel}
  
> \vnv
  \nv\rep{\chord{Dm}O poštaris \chord{E}avel, \chord{A\7}telegramos \chord{Dm}anel. \chord{D\sus{2}} \chord{Dm}}
  
```
![idzepostaridze line 5](vnv-04-idzepostaridze.png)

**5. `jinetonebude` line 37**, page 245 · class **U1**
```tex
  }
  
> \vnv
  
  \nv Jiný \chord{Em}to, nebude, děku\chord{Am}ju ti osu\chord{H\7}de. (4$\times$)\\
```
![jinetonebude line 37](vnv-05-jinetonebude.png)

**6. `kloboukvekrovi` line 5**, page 272 · class **U1**
```tex
  \nv\chord{C}Vítr \chord{B\9}vane \chord{C}pouští,\chord{G\add{7/5+}}\chord{C}po písku \chord{B\9}žene klo\chor
  \chord{Fm}zahnal \chord{G\7}ho do \chord{C}houští,\chord{Am}\chord{Fm}starý a \chord{G\7}černý klo\chord{C}bou
> \vnv
  
  \nv\chord{C}Kdepak \chord{B\9}je ta \chord{C}hlava,\chord{G\add{7/5+}}\chord{C}která klo\chord{B\9}bouk nosi\c
```
![kloboukvekrovi line 5](vnv-06-kloboukvekrovi.png)

**7. `kloboukvekrovi` line 9**, page 272 · class **U1**
```tex
  \nv\chord{C}Kdepak \chord{B\9}je ta \chord{C}hlava,\chord{G\add{7/5+}}\chord{C}která klo\chord{B\9}bouk nosi\c
  \chord{Fm}Byla čer\chord{G\7}ná či \chord{C}plavá?\chord{Am}\chord{Fm}Komu a\chord{G\7}si patři\chord{C}la?\\
> \vnv
  
  \nv\chord{Em}Kdo to v poušti \chord{F}zmizel? \chord{Em}Odkud šel a \chord{A\7}kam?\\
```
![kloboukvekrovi line 9](vnv-07-kloboukvekrovi.png)

**8. `kloboukvekrovi` line 13**, page 272 · class **U1**
```tex
  \nv\chord{Em}Kdo to v poušti \chord{F}zmizel? \chord{Em}Odkud šel a \chord{A\7}kam?\\
  \chord{G}Jakou to měl \chord{D\7}svízel, \chord{G}že byl v \chord{F\7}pou\chord{F\kk\7}šti \chord{G\7}sám? \ch
> \vnv
  
  \nv\chord{C}Jen za\chord{A\bb}váté \chord{C}stopy.\chord{G\add{7/5+}}\chord{C}Starý klo\chord{B\9}bouk ve křo\
```
![kloboukvekrovi line 13](vnv-08-kloboukvekrovi.png)

**9. `nebenazemi` line 10**, page 396 · class **U1**
```tex
  \chord{D}Nestojím o \chord{D\bas{C\kk}}nekonečno \chord{Hm}s hvězdami vše\chord{E\7}mi,\\
  \chord{F\kk}stačí mi pár \chord{C\kk\7}krásných let \chord{F\kk}někde na ze\chord{A\+}mi.
> \vnv
  
  \nv Když já \chord{D}vám povídám, že je nebe na zemi, pravdu \chord{E\7}mám, věřte mi!\\
```
![nebenazemi line 10](vnv-09-nebenazemi.png)

**10. `prejelijsmeslepici` line 6**, page 497 · class **U1**
```tex
  To jistě as cos dobrého věstí, srazil jsem slípku, vběhla mi do cesty.\\
  \chord{G}Já zato nemohl, ona taky \chord{A}ne, \chord{G}dotlouklo srdce, srdce nevin\chord{A}né.
> \vnv
  
  \nv Brzdím a kvílí guma o vozovku, kráčím k té slepici, v ruce pětistovku.\\
```
![prejelijsmeslepici line 6](vnv-10-prejelijsmeslepici.png)

**11. `prejelijsmeslepici` line 11**, page 497 · class **U1**
```tex
  Pantáta přibíhá, hrozí mi pěstí, jednička, dvojka, vskutku jsem měl štěstí.\\
  Pro pána Jána, jak teď z toho ven? Pro pána Jána, jak teď z toho ven?
> \vnv
  
  \nv A stodeset,\chord{B}\gap{1}stodvacet,\chord{H}\chord{C}stotřicetpětkou jedu po okresce,\\
```
![prejelijsmeslepici line 11](vnv-11-prejelijsmeslepici.png)

**12. `prejelijsmeslepici` line 23**, page 497 · class **U1**
```tex
  \nv\chord{A}Vyhlížím značky, teď už turistické, však mládí má zelenou a mýlit se je lidské.\\
  Ale na gesto chlapské ešče v srdci schrastím, zadarmo povozím babičku s chrastím.
> \vnv
  
  \nv Ale že nám ten týden začíná hezky! Sluníčko, kroupy, mlha, hromy, blesky.\\
```
![prejelijsmeslepici line 23](vnv-12-prejelijsmeslepici.png)

**13. `satydelajcloveka` line 4**, page 580 · class **U1**
```tex
  \nv\chord{C}Je \chord{D\7}to \chord{G\7}tak, třeba \chord{C}je to \chord{D\7}k neví\chord{G\7}ře, \chord{C}že 
  \chord{Em}Je \chord{E\dm}to\chord{A\dm}tak, \chord{H\7}třeba \chord{Em}je to \chord{E\dm}k neví\chord{A\dm}ře,
> \vnv\\
  \nv\chord{C}Je to pravda \chord{Dm\7}odvě\chord{G\7}ká, \chord{C\7}šaty dělaj \chord{F}člově\chord{Fm}ka,\\
  \chord{C}kdo je \chord{A\7}nemá, \chord{Dm}ať od \chord{D\dm}lidí \chord{C}pranic \chord{A\7}neče\chord{D\7}ká
```
![satydelajcloveka line 4](vnv-13-satydelajcloveka.png)

**14. `slunicko` line 5**, page 554 · class **U1**
```tex
  \nv\chord{D}Sluníčko, \chord{A\7}sluníčko, \chord{D}popojdi \chord{A\7}maličko,\\
  \chord{D}sedíš tu u \chord{Em}cesty, \chord{A\7}stane se ne\chord{D}štěstí, \chord{G}něco tě \chord{A\7}zaje\c
> \vnv
  
  \nv\chord{A\7}Elce pelce strejček Nimra \chord{D}koupil šimla v Kadani,\\
```
![slunicko line 5](vnv-14-slunicko.png)

**15. `spimvobili` line 18**, page 559 · class **U1**
```tex
  
  \refsme{1} $\times 2$
> \vnv
  
  \note{pomalu}
```
![spimvobili line 18](vnv-15-spimvobili.png)

**16. `vadinevadi` line 9**, page 657 · class **U1**
```tex
  \chord{G\7}nemít žádné kamarády, tomu já říkám neštěs\chord{C}tí.\\
  Nemít \chord{Am}prachy, \chord{C}nevadí, nemít \chord{Am}srdce, \chord{C}vadí,\\
> \vnv
  zažít \chord{Am}krachy, \chord{C}nevadí, zažít \chord{Am}nudu, \chord{F}jó, to \chord{G}vadí, to vadí.\chord{(
  \rep{Není nutno, není nutno, aby bylo přímo veselo,\\
```
![vadinevadi line 9](vnv-16-vadinevadi.png)

**17. `zivotjejennahoda` line 10**, page 738 · class **U1**
```tex
  \chord{Hm}Zdání \chord{F\kk}klame, mimoto \chord{Hm}každý \chord{E\7}sen,\\
  který v no\chord{D}ci \chord{G\kk\dm}mí\chord{A\7}váme, zažene \chord{D}pří\chord{C}ští \chord{D\7}den. \chord
> \vnv\\
  \chord{G}Život je jen \chord{C\7}náhoda, \chord{G}jednou jsi dole jednou \chord{G\7}nahoře,\\
  \chord{C}život plyne \chord{Cm}jak voda a \chord{G}smrt je \chord{D\7}jako mo\chord{G}ře. \chord{D\7}\\
```
![zivotjejennahoda line 10](vnv-17-zivotjejennahoda.png)

**18. `zivotjejennahoda` line 15**, page 738 · class **U1**
```tex
  \chord{G}Každý k moři \chord{C\7}dopluje, \chord{G}někdo dříve a někdo \chord{G\7}později,\\
  \chord{C}kdo v životě \chord{Cm}miluje, ať \chord{G}neztrá\chord{D\7}cí nadě\chord{G}ji. \chord{G\7}
> \vnv\\
  \chord{C}Až uvidí v životě \chord{G}zázraky, \chord{C}které jenom láska u\chord{G}mí,\\
  \chord{A\7}zlaté ryby vyletí nad mraky, \chord{D}pak porozu\chord{D\7}mí:
```
![zivotjejennahoda line 15](vnv-18-zivotjejennahoda.png)

**19. `zivotjejennahoda` line 18**, page 738 · class **U1**
```tex
  \chord{C}Až uvidí v životě \chord{G}zázraky, \chord{C}které jenom láska u\chord{G}mí,\\
  \chord{A\7}zlaté ryby vyletí nad mraky, \chord{D}pak porozu\chord{D\7}mí:
> \vnv\\
  \chord{G}Že je život \chord{C\7}jak voda, \chord{G}kterou láska ve víno \chord{G\7}promění,\\
  \chord{C}láska, že je \chord{Cm}náhoda a \chord{G}bez ní \chord{D\7}štěstí ne\chord{G}ní.
```
![zivotjejennahoda line 18](vnv-19-zivotjejennahoda.png)

**20. `zizniva` line 27**, page 740 · class **U1**
```tex
  která chápe, jak to píše v břiše z půllitrové číše.
  }\refsm{}
> \vnv
  
  \emph{rec:} Tak teda Kofolu.
```
![zizniva line 27](vnv-20-zizniva.png)

</details>

### `\lsp`: 20 sampled contexts
<details><summary>Show the samples</summary>

**1. `jenamteplo` line 26**, page 235 · class **L1**
```tex
  }
  
> \lsp{10}
  
  \bridge{
```
![jenamteplo line 26](lsp-01-jenamteplo.png)

**2. `kometa` line 11**, page 280 · class **L1**
```tex
  }
  
> \lsp{10}
  
  \vers{2}{
```
![kometa line 11](lsp-02-kometa.png)

**3. `kometa` line 47**, page 280 · class **L1**
```tex
  } \refsm{} Na na na\dots
  
> \lsp{10}
  
  \vers{5}{
```
![kometa line 47](lsp-03-kometa.png)

**4. `mamdomakocku` line 20**, page 328 · class **L1**
```tex
  }
  
> \lsp{12}
  \vspace{5pt}
  
```
![mamdomakocku line 20](lsp-04-mamdomakocku.png)

**5. `mamdomakocku` line 30**, page 328 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{3}{
```
![mamdomakocku line 30](lsp-05-mamdomakocku.png)

**6. `mamdomakocku` line 57**, page 328 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{6}{
```
![mamdomakocku line 57](lsp-06-mamdomakocku.png)

**7. `nepijjanonepijvodu` line 9**, page 407 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{2}{
```
![nepijjanonepijvodu line 9](lsp-07-nepijjanonepijvodu.png)

**8. `nepijjanonepijvodu` line 16**, page 407 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{3}{
```
![nepijjanonepijvodu line 16](lsp-08-nepijjanonepijvodu.png)

**9. `nepijjanonepijvodu` line 23**, page 407 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{4}{
```
![nepijjanonepijvodu line 23](lsp-09-nepijjanonepijvodu.png)

**10. `nepijjanonepijvodu` line 30**, page 407 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{5}{
```
![nepijjanonepijvodu line 30](lsp-10-nepijjanonepijvodu.png)

**11. `nepijjanonepijvodu` line 86**, page 407 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{13}{
```
![nepijjanonepijvodu line 86](lsp-11-nepijjanonepijvodu.png)

**12. `nepijjanonepijvodu` line 114**, page 407 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{17}{
```
![nepijjanonepijvodu line 114](lsp-12-nepijjanonepijvodu.png)

**13. `tesar` line 37**, page 607 · class **L1**
```tex
  }
  
> \lsp{17}
  
  \vers{6}{
```
![tesar line 37](lsp-13-tesar.png)

**14. `tesar` line 44**, page 607 · class **L1**
```tex
  }
  
> \lsp{17}
  
  \vers{7}{
```
![tesar line 44](lsp-14-tesar.png)

**15. `tesar` line 51**, page 607 · class **L1**
```tex
  }
  
> \lsp{17}
  
  \vers{8}{
```
![tesar line 51](lsp-15-tesar.png)

**16. `tesar` line 58**, page 607 · class **L1**
```tex
  }
  
> \lsp{17}
  
  \vers{9}{
```
![tesar line 58](lsp-16-tesar.png)

**17. `tesar` line 89**, page 607 · class **L1**
```tex
  }
  
> \lsp{17}
  
  \vers{14}{Už běsnící bouře lodí kymácí, rve vítr cáry plachet bělostných\\
```
![tesar line 89](lsp-17-tesar.png)

**18. `tesar` line 95**, page 607 · class **L1**
```tex
  }
  
> \lsp{17}
  
  \vers{15}{Pak poslední vlna loď na bok pokládá a stěžeň jako stéblo ohýbá\\
```
![tesar line 95](lsp-18-tesar.png)

**19. `zpatkydotrenek` line 16**, page 727 · class **L1**
```tex
  }
  
> \lsp{12}
  
  \vers{2}{
```
![zpatkydotrenek line 16](lsp-19-zpatkydotrenek.png)

**20. `zpatkydotrenek` line 34**, page 727 · class **L1**
```tex
  } \refsm{1}
  
> \lsp{12}
  
  \vers{3}{
```
![zpatkydotrenek line 34](lsp-20-zpatkydotrenek.png)

</details>

### raw `\vspace`: 20 sampled contexts
<details><summary>Show the samples</summary>

**1. `aztosemnusekne` line 4**, page 31 · class **R1** · song fits without
```tex
  \ns
  \note{capo 3}
> \vspace{-3mm}
  
  \vers{1}{
```
![aztosemnusekne line 4](vspace-01-aztosemnusekne.png)

**2. `babickamary` line 3**, page 33 · class **R1** · song spills without
```tex
  \song{Babička Mary}
  \artist{}
> \vspace{-9mm}
  
  \vers{1}{
```
![babickamary line 3](vspace-02-babickamary.png)

**3. `barbarskepobrezi` line 3**, page 35 · class **R1** · song fits without
```tex
  \song{Barbarské pobřeží} \artist{asonance}
  \ns
> \vspace{-10pt}
  
  \vers{1}{
```
![barbarskepobrezi line 3](vspace-03-barbarskepobrezi.png)

**4. `barborapiseztabora` line 43**, page 36 · class **R1** · song fits without
```tex
  
  P. S.
> \vspace{-10pt}
  
  \vers{7}{
```
![barborapiseztabora line 43](vspace-04-barborapiseztabora.png)

**5. `carodejnicezamesbury` line 9**, page 73 · class **R1** · song spills without
```tex
  }
  \ns
> \vspace{-10pt}
  
  \vers{2}{
```
![carodejnicezamesbury line 9](vspace-05-carodejnicezamesbury.png)

**6. `deepriverblues` line 6**, page 98 · class **R2** · song spills without
```tex
  \intro{
  	
> \vspace{-55pt}
  \hspace{20pt}	
  \includegraphics[width=515pt]{scores/deepriverblues.pdf}
```
![deepriverblues line 6](vspace-06-deepriverblues.png)

**7. `eldorado` line 23**, page 131 · class **R4**
```tex
  } \refsm{}
  
> \vspace{10pt}
  \rec{\emph{(akordy jako ve sloce)}\\
  Protože my už dávno víme, že nad zlato a bohatství je moudrost a uvážlivý čin, že Eldorádo není kdesi v dálce,
```
![eldorado line 23](vspace-07-eldorado.png)

**8. `hodiljsemflintudozita` line 27**, page 179 · class **R4**
```tex
  }
  
> \vspace{10pt}
  \note{Od začátku a do ztracena.}
  
```
![hodiljsemflintudozita line 27](vspace-08-hodiljsemflintudozita.png)

**9. `jaktosnamalaskobude` line 5**, page 225 · class **R5**
```tex
  \note{originál v F dur, capo 3}
  
> \vspace{5mm}
  \refrain{
  \chord{D\6}Jak to s náma \chord{F\kk m\7}lásko bude \chord{Hm\7}za pár \chord{D\7}let, až si \chord{B\7}přesta
```
![jaktosnamalaskobude line 5](vspace-09-jaktosnamalaskobude.png)

**10. `ladovskazima` line 3**, page 293 · class **R2**
```tex
  \song{Ladovská zima} \artist{jaromirnohavica}
  \note{capo 5}
> \vspace{15pt}
  
  \includegraphics[width=\linewidth]{scores/ladovskazima.pdf}
```
![ladovskazima line 3](vspace-10-ladovskazima.png)

**11. `malujzaseobrazky` line 4**, page 327 · class **R1** · song spills without
```tex
  \artist{}
  \ns
> \vspace{-5pt}
  
  \intro{
```
![malujzaseobrazky line 4](vspace-11-malujzaseobrazky.png)

**12. `morseovka` line 12**, page 362 · class **R2** · song spills without
```tex
  \solon{1}{
  	
> \vspace{-30pt}
  \hspace{21pt}
  \includegraphics[width=\linewidth]{scores/morseovka_1.png}
```
![morseovka line 12](vspace-12-morseovka.png)

**13. `pianoman` line 4**, page 454 · class **R1** · song spills without
```tex
  
  \ns
> \intro{\chords{Dm\7 D\dm}, akordy jako ve sloce} \solon{1}{\chords{C F G F} $\times$ 2}\vspace{-30pt}
  
  \vers{1}{
```
![pianoman line 4](vspace-13-pianoman.png)

**14. `podzimniplihal` line 34**, page 468 · class **R4**
```tex
  }
  
> \vspace{20pt}
  
  \note{Celé znovu, a pak první sloka dvakrát.}
```
![podzimniplihal line 34](vspace-14-podzimniplihal.png)

**15. `pterodaktylus` line 20**, page 501 · class **R4**
```tex
  Jak slepice i opice, tak psy a párek hus, jen ať tam nechybí pterodaktylus!
  }
> \vspace{15pt}
  
  \rec{Tak Noe se zved' a šel domů pro kleště, sám archu postavil, než se dalo do deště.\\
```
![pterodaktylus line 20](vspace-15-pterodaktylus.png)

**16. `pterodaktylus` line 29**, page 501 · class **R4**
```tex
  Jak slepice i opice, tak psi a párek hus, ale kdepak, k sakru, je pterodaktylus?
  }
> \vspace{15pt}
  
  \rec{Když se Noe rozhlíd' deštěm z toho kopce do strání, byli pterodaktylové ještě kdesi schovaní.\\
```
![pterodaktylus line 29](vspace-16-pterodaktylus.png)

**17. `slunecnyhrob` line 6**, page 553 · class **R2** · song spills without
```tex
  \intro{
  	
> \vspace{-30pt}
  \hspace{21pt}
  \includegraphics[width=0.7\linewidth]{scores/slunecnyhrob_intro.pdf}
```
![slunecnyhrob line 6](vspace-17-slunecnyhrob.png)

**18. `triandele` line 5**, page 634 · class **R2** · song fits without
```tex
  \vers{1}{
  
> \vspace{-53pt}
  \hspace{20pt}
  \includegraphics[width=\linewidth]{scores/triandele.pdf}
```
![triandele line 5](vspace-18-triandele.png)

**19. `vodavodenka` line 37**, page 688 · class **R6**
```tex
  }
  
> \vspace{175pt}
  
  \vers{1}{
```
![vodavodenka line 37](vspace-19-vodavodenka.png)

**20. `vosa` line 33**, page 690 · class **R4**
```tex
  koho už vosy bodnuly, stále a znova a od nuly.
  }
> \vspace{20pt}
  
  \note{Celé znovu a od 5. sloky fade out.}
```
![vosa line 33](vspace-20-vosa.png)

</details>

### Extra (not random): the two raw `\vspace` classes the sample missed
<details><summary>Show the extra contexts</summary>

**E1. `idzepostaridze` line 11**, page 206 · class **R3**
```tex
  	
  \nv Dža, more, \chord{G\dm}dža, more, dža, mo\chord{A\7}re, na kamav \chord{Dm}tut! \chord{D\sus{2}} \chord{Dm
> \vspace{5mm}
  
  \nv\rep{Idze poštár, idze, telegram mi nese.}\\
```
![idzepostaridze line 11](vspace-extra-1-idzepostaridze.png)

**E2. `prejelijsmeslepici` line 16**, page 497 · class **R3**
```tex
  přemýšlím, za co mě Pán Bůh asi tresce? \chord{D}\chord{G}\\
  \chord{C}Ujíždím v prostoru, ujíždím v čase, ech, tfuj, už v tom lítám zase.
> \vspace{5mm}
  
  \nv\chords{D} \emph{(mezihra)}
```
![prejelijsmeslepici line 16](vspace-extra-2-prejelijsmeslepici.png)

**E3. `motyl` line 14**, page 365 · class **R7**
```tex
  a proto rozhodl se hned pro nejkrásnější květ\\
  a jenom pro něj hodlá žít.
> \vspace{5mm}
  
  \emph{On:} Snad řek jsem \chord{D\7}víc, \chord{G\kk\dm}než chtěl jsem \chord{D\7}říct,
```
![motyl line 14](vspace-extra-3-motyl.png)

**E4. `slunecnyhrob` line 55**, page 553 · class **R7**
```tex
  =\gap{2}\textbf{3.}
  }\refsm{}
> \vspace{2mm}
  
  
```
![slunecnyhrob line 55](vspace-extra-4-slunecnyhrob.png)

</details>
