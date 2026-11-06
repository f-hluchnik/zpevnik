#!/usr/bin/env bash
# Overleaf-style check: one song must compile with zpevnik.sty alone.
#
# Usage: bash tests/single-song.sh DIR [--build]
#
# Fills DIR with exactly what an Overleaf project has: zpevnik.sty,
# single-song.tex and the one song it includes, plus artist.tex (the edge
# cases of \artist), metadata.tex (\alttitle, \toctitle, \collection) and
# chords.tex (automatic chord spacing).
# With --build it also compiles them with pdflatex and checks them: the song
# takes one page, each page of artist.tex prints the artist links it should,
# metadata.tex prints none of its metadata, and chords.tex has no overlapping
# chords, and spacing.tex keeps its separators and unnumbered verses in line.
# CI runs this script with --build in the pinned TeX Live action; any failed check fails the job.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
dir=${1:?usage: single-song.sh DIR [--build]}
song=$(grep -oP '(?<=\\include\{pisnicky/)[^}]+' "$root/tests/single-song.tex")

rm -rf "$dir"
mkdir -p "$dir/pisnicky"
cp "$root/zpevnik.sty" "$root/tests/single-song.tex" "$root/tests/artist.tex" "$root/tests/metadata.tex" "$root/tests/chords.tex" "$root/tests/spacing.tex" "$dir/"
cp "$root/pisnicky/$song.tex" "$dir/pisnicky/"

[ "${2:-}" = "--build" ] || exit 0

cd "$dir"
pdflatex -interaction=nonstopmode -halt-on-error single-song.tex >/dev/null
pages=$(pdfinfo single-song.pdf | awk '/^Pages:/ {print $2}')
[ "$pages" = 1 ] || { echo "expected 1 page, got $pages" >&2; exit 1; }
echo "single-song OK ($song, 1 page)"

# \artist: an empty or unknown slug, or an artist without a section, prints
# nothing and is not an error; labels, two artists, a third ignored.
pdflatex -interaction=nonstopmode -halt-on-error artist.tex >/dev/null
[ "$(pdfinfo artist.pdf | awk '/^Pages:/ {print $2}')" = 9 ] || { echo "artist.tex: expected 9 pages" >&2; exit 1; }
page() { pdftotext -f "$1" -l "$1" artist.pdf -; }
# The page text goes through a variable: with pipefail, `grep -q` ending the pipe early can
# make pdftotext fail with SIGPIPE, so the pipeline reports "no match" for a match.
expect() { # page, "has"|"lacks", text
  local text; text=$(page "$1")
  if grep -qF -- "$3" <<<"$text"; then found=has; else found=lacks; fi
  [ "$found" = "$2" ] || { echo "artist.tex page $1 should $2 '$3'" >&2; exit 1; }
}
arrows() { # page, number of arrows: 1 for the "obsah" link in the title + 1 per artist
  n=$(page "$1" | grep -o "→" | wc -l)
  [ "$n" = "$2" ] || { echo "artist.tex page $1: expected $2 arrows, got $n" >&2; exit 1; }
}
arrows 1 1; arrows 2 1; arrows 7 1; arrows 8 1
arrows 3 2; expect 3 has "A. Test"
arrows 4 2; expect 4 has "Own label"; expect 4 lacks "A. Test"
arrows 5 3; expect 5 has "A. Test"; expect 5 has "B. Test"
arrows 6 3; expect 6 lacks "C. Test"
expect 8 lacks "Own label"
arrows 9 2; expect 9 has "D. L. Test"; expect 9 lacks "Dee Long"
echo "artist OK (9 pages)"

# \alttitle, \toctitle, \collection: no output, one page, the song is intact.
pdflatex -interaction=nonstopmode -halt-on-error metadata.tex >/dev/null
[ "$(pdfinfo metadata.pdf | awk '/^Pages:/ {print $2}')" = 1 ] || { echo "metadata.tex: expected 1 page" >&2; exit 1; }
text=$(pdftotext metadata.pdf -)
grep -qF "Lyrics stay" <<<"$text" || { echo "metadata.tex: lyrics missing" >&2; exit 1; }
for t in "other title" "Metadata test (TOC)" "filmy" "break"; do
  ! grep -qF -- "$t" <<<"$text" || { echo "metadata.tex: '$t' should not be printed" >&2; exit 1; }
done
echo "metadata OK"
# DELIBERATELY BROKEN ASSERTION (to be reverted)
grep -qF "this text is not on the page" <<<"$text" || { echo "deliberately broken assertion" >&2; exit 1; }

# Automatic chord spacing: no chords overlap on the page; \gap and \chords print their text.
pdflatex -interaction=nonstopmode -halt-on-error chords.tex >/dev/null
[ "$(pdfinfo chords.pdf | awk '/^Pages:/ {print $2}')" = 1 ] || { echo "chords.tex: expected 1 page" >&2; exit 1; }
python3 "$root/tools/chord_gaps.py" --trace chords.chords >/dev/null \
  || { echo "chords.tex: chords overlap" >&2; exit 1; }
text=$(pdftotext -f 1 -l 1 chords.pdf -)
grep -qF "Pause" <<<"$text" && grep -qF "here" <<<"$text" || { echo "chords.tex: lyrics missing" >&2; exit 1; }
grep -qF "G7" <<<"$text" || { echo "chords.tex: \\chords did not print its chords" >&2; exit 1; }
# \chords[sep]{...} changes the spacing of its row only: the narrow row ends left of the normal one.
ends=$(pdftotext -f 1 -l 1 -bbox chords.pdf - | awk -F'"' '/>Rc</ {print $6}')
[ "$(wc -l <<<"$ends")" = 2 ] && awk -v a="$(head -1 <<<"$ends")" -v b="$(tail -1 <<<"$ends")" 'BEGIN {exit !(b+0 < a-5)}' \
  || { echo "chords.tex: \\chords[0.2em] should be narrower than \\chords" >&2; exit 1; }
echo "chords OK"

# Vertical spacing: \vers{}{...} prints no label but the text starts where a labelled one does;
# a separator at the end of a song does not swallow the first gap of the next song (\song resets it).
pdflatex -interaction=nonstopmode -halt-on-error spacing.tex >/dev/null
[ "$(pdfinfo spacing.pdf | awk '/^Pages:/ {print $2}')" = 4 ] || { echo "spacing.tex: expected 4 pages" >&2; exit 1; }
word() { # page, word, bbox attribute (xMin or yMin)
  pdftotext -f "$1" -l "$1" -bbox spacing.pdf - | awk -F'"' -v w="$2" -v a="$3" '$0 ~ ">" w "<" {print (a == "x" ? $2 : $4); exit}'
}
[ -n "$(word 1 Beta x)" ] && [ "$(word 1 Alpha x)" = "$(word 1 Beta x)" ] \
  || { echo "spacing.tex: unnumbered verse is not aligned with a numbered one" >&2; exit 1; }
text=$(pdftotext -f 1 -l 1 spacing.pdf -)
! grep -qx '\.' <<<"$text" || { echo "spacing.tex: unnumbered verse prints a stray label" >&2; exit 1; }
[ -n "$(word 2 Verse y)" ] && [ "$(word 2 Verse y)" = "$(word 3 Verse y)" ] \
  || { echo "spacing.tex: a separator at the end of a song changed the next song" >&2; exit 1; }
echo "spacing OK"
