# Sessions 17–19 (phase 11, done 6 Nov 2026)

### Session 17 · Q1, Q2, Q3 · Sonnet · `zpevnik`
- **Needs:** nothing.
- **Read:** DECISIONS D-131 · PLAN WP-Q · TICKETS Q1–Q3.
- **Notes:** All three are zero diff; Q2 also needs `generated/` byte-identical to master. Three PRs, independent of each other. In Q1 keep `\sc`'s `\normalfont` effect where it matters. In Q3, read the first real CI run (and the deliberately red one) before claiming anything.

### Session 18 · Q4 · Sonnet · `zpevnik` · ⚠
- **Needs:** Q1.
- **Read:** DECISIONS D-128, D-130, D-131 · TICKETS Q4 · the README section "Přepisování písniček".
- **Notes:** Write the migration script and its tests first; show the counts per rename before running it on all songs. The only expected visible differences are the 8 standalone repeat marks. Every old name becomes a lint error. The README command reference is rewritten from the style file, in Czech.

### Session 19 · Q5 · Sonnet · `zpevnik`
- **Needs:** Q4; the owner's answers to items 2–4 (ask at the start).
- **Read:** TICKETS Q5 · DECISIONS D-124, D-131.
- **Notes:** Show each song's page diff and get the owner's confirmation. Item 5 only where it gives zero diff. End of phase 11: rule 9.

