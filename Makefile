# make          generate the derived .tex files, then compile zpevnik.pdf
# make generate only run the generator (tools/generate.py, D-104)
.PHONY: all generate pdf

all: pdf

generate:
	python3 tools/generate.py

pdf: generate
	latexmk -pdf -interaction=nonstopmode -halt-on-error zpevnik.tex
