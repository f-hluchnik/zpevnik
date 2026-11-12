# Phase 8 tickets (done 12 Nov 2026)

The ticket texts and status rows of the legal phase as they were when it ended. Summary: [HISTORY.md](../../HISTORY.md), phase 8. What is left of it lives in other tickets: `songs.json` leaves out the hidden songs in J2, `noindex` and `robots.txt` are W6.

| Ticket | Status | Notes / PR |
|---|---|---|
| L1 | done | D-141 (notice in the PDF colophon and the web footer, licence scope) |
| L2 | done | `data/hidden.txt`, applied by `songs.published()` to every book; the `songs.json` part is in J2 (D-161): PR #121 |

### L1 · Notice text — [you] · S — **done**
A short text in Czech and English: non-commercial, contact address for removal requests. It goes into the website footer and the PDF colophon. Done on 9 Nov 2026 (D-141): `shared-pages/notice.tex` (then `preamble/upozorneni.tex`) in the colophon, the footer in `zpevnik-web/templates/base.html`, and the scope of the Apache licence in `LICENSE` and the README.

### L2 · Hide switch — [agent] · S · needs E2, L1 (the `songs.json` part moved to J2, D-161)
`data/hidden.txt` with one song id per line. The generator leaves those songs out of every book, using E2's song filter (TOC, index and include list follow); the converter leaves them out of `songs.json`; a lint checks that each id exists. (This hides songs from the outputs; only deleting the file removes it from the repository.)
