# make          generate the derived .tex files, then compile zpevnik.pdf
# make generate only run the generator (tools/generate.py)
# make song SONG=<id>  build only that song into build/<id>.pdf (tools/build_song.py)
.PHONY: all generate pdf song

all: pdf

generate:
	python3 tools/generate.py

pdf: generate
	latexmk -pdf -interaction=nonstopmode -halt-on-error zpevnik.tex

song:
	python3 tools/build_song.py $(SONG)
