# Content tickets K1 and K2 (done 11 Nov 2026)

The ticket texts and status rows as they were when the work ended: the owner's songs without chords, and the allow-list for songs that are right without them. The owner's new songs before the print are content work, not a ticket (D-147).

| Ticket | Status | Notes / PR |
|---|---|---|
| K1 | done | the five songs with only a `\chords` row got chords over the lyrics: PR #109; the three scores need none (K2). The owner's new songs (about ten) before the print are content work, not a ticket (D-147) |
| K2 | done | `tools/no-chords-allowlist.txt` (since D-162 `data/no-chords-allowlist.txt`) read by the lint (answers K1's question): PR #111 |

### K1 · Songs without chords — [you] · S · needs nothing
8 songs have no chords over the lyrics: 5 have only a `\chords` row (gronskapisnicka, marieklus, noe, panubohudooken, vranabuty), 3 only a score image (ladovskazima, scarboroughfaircarthy, triandele). The owner decides per song whether to add chords (content work). The lint warns about songs without `\chord`. - ladovskazima, scarboroughfaircarthy, triandele are correct without chords. I wonder what would adding an empty `\chord` command with a comment saying it's for linters do? The other songs should be adjusted (read, chords should be added properly, not as list, at least where possible). The question about an empty `\chord` for the linters is answered by K2. About ten new songs before the print are content work too (owner, 11 Nov 2026): not a ticket, every new song passes `make check`.

### K2 · Songs that are right without chords — [agent] · S · needs nothing
D-147. The lint warns about a song that has no `\chord` or `\chords` (`tools/lint.py`): today `ladovskazima`, `scarboroughfaircarthy` and `triandele`, which are a score and are correct (K1). An empty `\chord` in the song just to silence the warning would put a marker inside the content that the converter (J1) would have to know and `songs.json` would carry; the repository already has the other answer, an allow-list read by a tool (`tools/multipage-allowlist.txt`). So: `tools/no-chords-allowlist.txt`, one song id per line with a `#` comment saying why, read by the lint like the multipage allow-list; the warning stays for every other song; a unit test that an allow-listed song passes, an unlisted one warns, and an id that is not a song fails. **Expected differences:** none (no song and no PDF changes).
