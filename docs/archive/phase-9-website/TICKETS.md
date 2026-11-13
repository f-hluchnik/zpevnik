# Phase 9 tickets: the online songbook (done 13 Nov 2026)

The ticket texts and status rows as they were when the work ended: the data from the release, song pages, index, artists, navigation, search, wake lock, robots.txt and the release check, in `zpevnik-web`. W5a (the wake-lock button as an icon) and W6a (chord wrapping, head + tail) were added on 13 Nov 2026 and are done. Summary: [HISTORY.md](../../HISTORY.md).

| Ticket | Status | Notes / PR |
|---|---|---|
| W1 | done | `build.py` of `zpevnik-web` downloads `songs.json` from the release into `build/` and checks `schemaVersion` (`--songs-json FILE` for a local one): zpevnik-web PR #4 |
| W2 | done | one page per song at `/zpivej/<id>/` from `songs.json` and `scores.zip`, the chord rule of D-123 in CSS, noindex, font-size control, 404 for unknown songs (D-167); the hyphen inside a split word is shown only where the gap is wide enough (README of `zpevnik-web`): zpevnik-web PR #5 |
| W3 | done | the index at `/zpivej/` (the contents of `songs.json`, never re-sorted), the artists and collections at `/zpivej/interpret/`, the navigation, links between songs and artists, previous/next in book order, "open in PDF" at the song's page, the link from the download page and from `404.html` (D-168): zpevnik-web PR #6 |
| W3a | done | two levels of navigation: the tabs "Stáhnout" and "Zobrazit online" on every page, the songbook's own row under `/zpivej/` (D-169), smaller font buttons: zpevnik-web PR #7 |
| W3b | done | a muted link up above the title of a song and an artist; those pages mark no item of the songbook's row (D-172): zpevnik-web PR #10 |
| W4 | done | `/zpivej/hledat/` and `static/search-index.json` (title, other titles, artists, lyrics; 262 kB gzipped), loaded when the field is first used, case and diacritics ignored, all words must occur, ranked title / artist / lyrics, the query in `?q=` (D-170): zpevnik-web PR #8 |
| W4a | done | search matches from the start of words; style sheets, scripts and the search index get a content hash in their URL, so a browser never combines new pages with an old style sheet (D-171): zpevnik-web PR #9 |
| W4b | done | search results in two groups (title or artist, lyrics), the matched words bold, the lyrics group cut to 10 with a button for all (D-173): zpevnik-web PR #11 |
| W5 | done | the button "Nezhasínat displej" on a song, Screen Wake Lock API, hidden where unsupported, asked for again when the page is shown, the choice kept for the tab (D-174): zpevnik-web PR #12 |
| W6 | done | `robots.txt` that disallows everything, no sitemap, tested with the standard robots parser: zpevnik-web PR #13 |
| W7 | done | the release check: `check_site.py` (every song has a page, every link and anchor of the built site resolves) run in CI; the build takes 3 s, the whole workflow 18 s: zpevnik-web PR #14 |
| W5a | done | the wake-lock button is a small coffee-cup icon beside A− and A+, the words are its label and tooltip (D-174): zpevnik-web PR #16 |
| W6a | done | chord segments wrap like the book's: the chord's column holds the head (the shortest run of whole words as long as the chord), the rest flows; option chosen by the owner on 13 Nov 2026 (D-176): zpevnik-web PR #15 |

### W1 · Load the data — [agent] · M · needs J4
`build.py` downloads `songs.json` from the release tagged `v<version.txt>` (the songbook CI already writes `version.txt` after creating the release) into an uncommitted folder, validates `schemaVersion`, and fails loudly if missing. Add a local option to point at a file.
The PDFs already come from the release since E6 (D-110, D-138); W1 adds `songs.json` the same way.

### W2 · Song pages — [agent] · L · needs W1
The online songbook is separate from the download page (D-103): it lives under `/zpivej/` (D-167), with its own templates and navigation; the download page at `/` stays as it is (the link to the songbook comes with the index, W3). An unknown song gets `404.html` (D-167).
Jinja template, one page per song at `/zpivej/<id>/`: chords above lyrics (each chord and its text in an inline-block that keeps spaces; chord width is respected, the rule of D-123), labels, footnotes, score SVGs, the existing dark mode, a font-size control. It must read well without JavaScript. Every page carries `<meta name="robots" content="noindex">`.

### W3 · Index, artists, navigation — [agent] · M · needs W2
Alphabetical index (same order as the PDF, taken from `songs.json`, never re-sorted), artist pages at `/zpivej/interpret/<slug>/`, collection pages, alternative titles listed, previous/next links in book order, "open in PDF" using `page`. The download page gets its link to the songbook here (D-167).

### W3a · Two levels of navigation — [agent] · S · needs W3 · added after W3 (owner, 12 Nov 2026)
The owner looked at the live W3 pages: the link to the songbook was a download-style button, and "Ke stažení" stood in the songbook's row as if it were one of its pages. Now: the tabs **Stáhnout** and **Zobrazit online** (the owner's labels) under the header of every page (`_site-nav.html`), the songbook's own row (Písničky · Interpreti, from W4 also the search) only under `/zpivej/`, and the download page without its extra button. The font size buttons get smaller. See D-169.

### W3b · A way up from a song or an artist — [agent] · S · needs W3a · added after W4a (owner, 12 Nov 2026)
The owner found it unclear that the way back to the index is the item "Písničky": on a song page it was marked as the current one, which reads as "you are here" and not as a link. Now a muted link above the title ("← Všechny písničky", on an artist "← Všichni interpreti") and no marked item in the row on the page of one song or artist. See D-172.

### W4 · Search — [agent] · M · needs W2
Build-time index over title, alternative titles, artist and lyrics (about 270 kB gzipped), loaded on first use, diacritics-insensitive, no libraries unless tiny.

### W4a · Search from the start of words, versioned URLs — [agent] · S · needs W4 · added after W4 (owner, 12 Nov 2026)
The owner tried the live search. (1) A word of the query must begin a word of the text (`jede` no longer finds `pojedeme`). (2) On his desktop the search page looked unstyled (a tiny box, a numbered list) while his phone showed it right: the browser had `songbook.css` from before W4 cached (GitHub Pages: ten minutes), so the new page met the old style sheet. Style sheets, scripts and the search index are now asked for as `<path>?v=<hash of the content>`. See D-171.

### W4b · Search results in groups — [agent] · S · needs W4a · added after W3b (owner, 12 Nov 2026)
The owner found it odd that songs matching only in some line of the lyrics stand among those matching in the title. The results are now in two headed groups, **V názvu nebo u interpreta (N)** and **V textu (N)**; a song is in its best group only; the matched words of the lyrics line are bold; the group of the lyrics shows 10 songs and a button **Zobrazit všech N**. The cut at 60 results is gone. See D-173.

### W5 · Wake lock — [agent] · S · needs W2
A toggle on the song page using the Screen Wake Lock API; hidden where unsupported. Done as the button "Nezhasínat displej" (`static/wake-lock.js`); see D-174. The lock itself could not be tried on a real phone, so the owner should try it once on his.

### W6 · Robots and notice — [agent] · S · needs W2, L1
`robots.txt` disallowing everything, no sitemap. The notice is already in the footer of every page (L1, D-141); no separate notice page. Hidden songs are absent because they are absent from the JSON.

### W7 · Release check — [agent] · S · needs W3–W6
Build under 1 minute; every song page present (minus hidden); every internal link resolves; screenshots of 3 songs on a phone-sized viewport; update the web README.

### W5a · Keep-the-screen-on as a small icon — [agent] · S · `zpevnik-web`
The button "Nezhasínat displej" (W5, D-174) becomes a small icon button beside A− and A+, as tall as they are; the words stay as its label and tooltip; `wake-lock.js` unchanged (owner, 13 Nov 2026).

### W6a · Segments wrap freely — [strong model] · M · needs W2 · **option chosen: head + tail (owner, 13 Nov 2026, D-176)**
**The problem.** On a narrow screen, or with a larger font, a line wraps strangely (the release check of W7 saw it at the default font size on a 390 px phone too): in `folsomprisonblues`, "I" stands alone and "hear the train a-coming, …" starts the next line. Cause, measured on 12 Nov 2026: a chord and all its text up to the next chord are one `inline-block` (the W2 form of the chord rule, D-123), and a browser moves such a box whole to the next line when it does not fit beside what is before it; TeX would break at any space. The PDF is not affected.
**Not the fix.** Letting only the first word be the chord's column and the text after it flow: it pads after a first word shorter than its chord, which the book does not (498 of 1,518 multi-word chord segments in 120 sampled songs).
**To decide first (a note in this ticket's PR, an owner decision if the options differ visibly), then implement.** CSS cannot say "pad only where the next chord would collide" without measuring, so every approach is a compromise. The candidates:
1. *A text clearly longer than its chord flows; a short one keeps today's unbreakable column.* The chord is zero-width over the first word, so the text is not padded; the collision guarantee stays for the short ones (11 of 1,518 sampled multi-word segments have a text narrower than the chord and its separator). A segment that ends inside a word (the hyphen) stays unbreakable. A threshold in one named constant.
2. *Measure in JavaScript* and pad where a chord would collide. The page must still read without JavaScript, so the unbreakable columns stay as the base: the wrap is not fixed without it.
3. *Leave it:* the book's rule is exact, and the reader can make the text smaller.
The first is the simplest that fixes the wrap without JavaScript; whether a threshold is acceptable is the question.
**Chosen (13 Nov 2026, D-176):** a fourth option found in the consultation, *head + tail*: the chord's column holds only the shortest run of whole words that is at least as long as the chord, the rest of the text flows; text without a chord flows; a line breaks inside a word only with a hyphen, as in the book. The default font size stays. The measurements and the reasons are in D-176. Check with screenshots of `folsomprisonblues` and a few dense songs at 390 px and with the font at the largest size, and that the number of songs where a chord is closer to the next than 0.5 em does not grow (measure it in the browser, as for the sample above).
