#!/usr/bin/env bash
# Overleaf-style check (D-005): one song must compile with zpevnik.sty alone.
#
# Usage: bash tests/single-song.sh DIR [--build]
#
# Fills DIR with exactly what an Overleaf project has: zpevnik.sty,
# single-song.tex and the one song it includes. With --build it also compiles
# the project with pdflatex and checks that the song takes one page. CI only
# prepares DIR and compiles it with the pinned TeX Live action.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
dir=${1:?usage: single-song.sh DIR [--build]}
song=$(grep -oP '(?<=\\include\{pisnicky/)[^}]+' "$root/tests/single-song.tex")

rm -rf "$dir"
mkdir -p "$dir/pisnicky"
cp "$root/zpevnik.sty" "$root/tests/single-song.tex" "$dir/"
cp "$root/pisnicky/$song.tex" "$dir/pisnicky/"

[ "${2:-}" = "--build" ] || exit 0

cd "$dir"
pdflatex -interaction=nonstopmode -halt-on-error single-song.tex >/dev/null
pages=$(pdfinfo single-song.pdf | awk '/^Pages:/ {print $2}')
[ "$pages" = 1 ] || { echo "expected 1 page, got $pages" >&2; exit 1; }
echo "single-song OK ($song, 1 page)"
