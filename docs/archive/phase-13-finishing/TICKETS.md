# Phase 13 tickets (finishing)

The ticket texts and status rows of the finishing phase that are done, as they were when each ended. The phase is not finished: H7, V10 and Z2 are in [TICKETS.md](../../TICKETS.md). Summary when the phase ends: [HISTORY.md](../../HISTORY.md).

| Ticket | Status | Notes / PR |
|---|---|---|
| Q7 | done | the converter is the one reader of the songs; `songs.py` has no regexes (D-164): PR #142 |
| J6 | done | `\remark` for text that is not sung, a body item `remark` in `songs.json`, `schemaVersion` 2 (D-177): PR #143 and zpevnik-web PR #17; the owner chose the places (one became a `\speaker`, one went to H7) |

### Q7 · One reader of the songs — [agent] · M · `zpevnik`
**The problem.** Two programs read the song files: the converter (`tools/songbook/`, strict, D-164) and the regexes of `tools/songs.py` (title, toc title, alternative titles, artists, collections, `\score`), with `tex_text.plain_text` for the titles. A test (J1) keeps them in agreement. Two readers of one grammar is the duplication D-164 left as a follow-up.
**The change.** The generator and every other user of `songs.py` take the song metadata from the converter's model; the regexes of `songs.py` go, and `tex_text.plain_text` if nothing else needs it; the agreement test goes with them. First list what `songs.py` gives that the model does not (the file path, hidden songs, D-161) and keep that in one place. Watch the titles: `songs.py` keeps them as TeX for the generated contents and sorts by their plain text, while the model holds printed text; the generated TeX must not change. The generator runs on every `make`: measure that the build is not noticeably slower (the whole-book parse is under 5 s, D-164).
**Expected differences:** none: the PDF and `songs.json` of every edition byte-identical.

### J6 · Remarks as their own command — [you] + [agent] · S · ⚠ · `zpevnik` and `zpevnik-web`
**The problem** (owner, 6 Nov 2026). `\note` belongs to the next block (D-128): right for "capo 3". A remark that stands alone is written as an unnumbered verse `\vers{\emph{…}}`: 6 places in 5 songs (`hledamdevcenanedeli` "rec. A nebudu.", `allyouneedislove` ×2 (the structure of the verse; "interludium (sloka)"), `bellaciao`, `cernymuz` "verze Waldemara Matušky", `ahorsewithnoname` (the tuning)). In `songs.json` they are italic lyrics, so the website shows and searches them as lyrics.
**Decided (owner, 13 Nov 2026, D-177):** `allyouneedislove` ×2, `ahorsewithnoname` and `bellaciao` are remarks; `hledamdevcenanedeli` "rec. A nebudu." is a speaker line (`\speaker{rec}{A nebudu.}`); `cernymuz` "verze Waldemara Matušky" is a second song and goes to H7.
**The change.** A command `\remark{…}` that prints as these places print today; the converter gives a body item `remark` (a change of `songs.json`: `schemaVersion` 2, D-165); the website sets it like a note and the search leaves it out (D-170).
**Expected differences:** none in the PDF except `hledamdevcenanedeli` ("rec:" in the label column, D-177).
**Part 1, `zpevnik`:** the command, the converter, the schema, the lint, the README, the tests and the five songs. Merged: PR #143 (13 Nov 2026).
**Part 2, `zpevnik-web`, after the release that carries `schemaVersion` 2 (until then the website's build stops on it, D-177):** `SUPPORTED_SCHEMA_VERSION` to 2 in `build.py`; `_song.html` renders a `remark` as a block of italic lines like a note (`song-note`, one line per element of `lines`); a test that the search index holds no remark text (`allyouneedislove`: "interludium"); the test that rejects another version must use a version other than 2; check the four songs at 390 px and `python check_site.py`. Then this ticket leaves TICKETS.md in a docs PR in `zpevnik`.
