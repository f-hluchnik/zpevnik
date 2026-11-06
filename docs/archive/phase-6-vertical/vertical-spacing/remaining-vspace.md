# Remaining manual `\vspace` in the songs (not counting scores)

State: PR #78 (V9, stacked on #77), 6 Nov 2026. Everything that was not about a score image is gone. Score-alignment `\vspace` (negative offsets, `% KEEP` gaps next to `\includegraphics`) are deliberately not listed; D-124 keeps them and the README says so.

## Removed in #78
- Gap between cross-reference links and the capo note (digadigadoplihal, dobrodruzstvisbohempanem, greensleeves, romance16leta): deleted. `\hyl` clears the song-top flag so the note after the link line gets the block gap.
- Gap before a mid-song note (azvzletnouptaci, 3mm) and `\nv` before it: `\note` now has the normal block gap above itself (not at the top of a song, after `\sub`, after `\hyl`); gap below still suppressed. Eight other songs with mid-song notes got that gap too (folsomprisonblues, chirpychirpycheepcheep, neopatrnykrecek, spimvobili, summernights, tvojesnidane, zpivatatajan, vlese).
- Attribution / remark blocks: cernymuz ("verze Waldemara Matušky"), allyouneedislove (structure remark) and svazceskychbohemu (caption "základní riff") are `\vers{}{\emph{…}}` now. cernymuz changed from centred to indented.
- herecomesthesun: spacer verses `\vers{a}{\vspace{5mm}}` are `\vers{a}{}`.

## Speaker changes (motyl)
`\spk{On}{text}`: block gap + italic name inline (the name is wider than the 25pt `\labelw`, so `\vers{On}{…}` overlaps). motyl's two `\vspace{\blocksep}` are gone.

## Still there
Nothing outside score alignment.
