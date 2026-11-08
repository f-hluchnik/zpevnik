# make          generate the derived .tex files and the score images, then compile zpevnik.pdf
# make generate only run the generator (tools/generate.py)
# make scores   only export the score images from MuseScore (tools/scores.py; skips
#               scores that are up to date)
# make song SONG=<id>  build only that song into build/<id>.pdf (tools/build_song.py)
.PHONY: all generate scores pdf song

all: pdf

generate:
	python3 tools/generate.py

scores:
	python3 tools/scores.py

pdf: generate scores
	latexmk -pdf -interaction=nonstopmode -halt-on-error zpevnik.tex

song: scores
	python3 tools/build_song.py $(SONG)
