# Phase 13 tickets (finishing)

The ticket texts and status rows of the finishing phase that are done, as they were when each ended. The phase is not finished: J6, H7, V10 and Z2 are in [TICKETS.md](../../TICKETS.md). Summary when the phase ends: [HISTORY.md](../../HISTORY.md).

| Ticket | Status | Notes / PR |
|---|---|---|
| Q7 | done | the converter is the one reader of the songs; `songs.py` has no regexes (D-164): PR #142 |

### Q7 · One reader of the songs — [agent] · M · `zpevnik`
**The problem.** Two programs read the song files: the converter (`tools/songbook/`, strict, D-164) and the regexes of `tools/songs.py` (title, toc title, alternative titles, artists, collections, `\score`), with `tex_text.plain_text` for the titles. A test (J1) keeps them in agreement. Two readers of one grammar is the duplication D-164 left as a follow-up.
**The change.** The generator and every other user of `songs.py` take the song metadata from the converter's model; the regexes of `songs.py` go, and `tex_text.plain_text` if nothing else needs it; the agreement test goes with them. First list what `songs.py` gives that the model does not (the file path, hidden songs, D-161) and keep that in one place. Watch the titles: `songs.py` keeps them as TeX for the generated contents and sorts by their plain text, while the model holds printed text; the generated TeX must not change. The generator runs on every `make`: measure that the build is not noticeably slower (the whole-book parse is under 5 s, D-164).
**Expected differences:** none: the PDF and `songs.json` of every edition byte-identical.
