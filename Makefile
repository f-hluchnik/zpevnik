# The build targets print the path of what they built; everything goes under build/.
# make [pdf] [EDITION=<name>]  generate the edition's .tex files and the score images, then
#                              compile build/editions/<name>/zpevnik.pdf (default edition: full)
# make generate [EDITION=<name>]  only run the generator (tools/generate.py)
# make scores   only export the score images from MuseScore into build/scores/
#               (tools/scores.py; skips scores that are up to date)
# make song SONG=<id>  build only that song into build/songs/<id>.pdf (tools/build_song.py)
# make check [EDITION=<name>]  the unit tests and the lints, then build the edition (which
#               fails on a link to a missing target) and run the one-page and chord checks on it
# make clean    delete build/
EDITION ?= full

.PHONY: all generate scores pdf song check clean

all: pdf

generate:
	python3 tools/generate.py --edition $(EDITION)

scores:
	python3 tools/scores.py

pdf: generate scores
	python3 tools/build_edition.py --edition $(EDITION)

song: scores
	python3 tools/build_song.py $(SONG)

check:
	python3 -m unittest discover -s tools
	python3 tools/lint.py
	$(MAKE) pdf EDITION=$(EDITION)
	python3 tools/check_pages.py --edition $(EDITION)
	python3 tools/chord_gaps.py --edition $(EDITION)

clean:
	rm -rf build
