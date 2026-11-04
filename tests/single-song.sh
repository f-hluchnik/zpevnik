#!/usr/bin/env bash
# Overleaf-style check (D-005): one song must compile with zpevnik.sty alone.
#
# Usage: bash tests/single-song.sh DIR [--build]
#
# Fills DIR with exactly what an Overleaf project has: zpevnik.sty,
# single-song.tex and the one song it includes, plus artist.tex (the edge
# cases of \artist). With --build it also compiles both with pdflatex and
# checks them: the song takes one page, and each page of artist.tex prints
# the artist links it should. CI only prepares DIR and compiles it with the
# pinned TeX Live action.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
dir=${1:?usage: single-song.sh DIR [--build]}
song=$(grep -oP '(?<=\\include\{pisnicky/)[^}]+' "$root/tests/single-song.tex")

rm -rf "$dir"
mkdir -p "$dir/pisnicky"
cp "$root/zpevnik.sty" "$root/tests/single-song.tex" "$root/tests/artist.tex" "$dir/"
cp "$root/pisnicky/$song.tex" "$dir/pisnicky/"

[ "${2:-}" = "--build" ] || exit 0

cd "$dir"
pdflatex -interaction=nonstopmode -halt-on-error single-song.tex >/dev/null
pages=$(pdfinfo single-song.pdf | awk '/^Pages:/ {print $2}')
[ "$pages" = 1 ] || { echo "expected 1 page, got $pages" >&2; exit 1; }
echo "single-song OK ($song, 1 page)"

# \artist: an empty or unknown slug, or an artist without a section, prints
# nothing and is not an error (D-003); labels, two artists, a third ignored.
pdflatex -interaction=nonstopmode -halt-on-error artist.tex >/dev/null
[ "$(pdfinfo artist.pdf | awk '/^Pages:/ {print $2}')" = 9 ] || { echo "artist.tex: expected 9 pages" >&2; exit 1; }
page() { pdftotext -f "$1" -l "$1" artist.pdf -; }
expect() { # page, "has"|"lacks", text
  if page "$1" | grep -qF -- "$3"; then found=has; else found=lacks; fi
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
