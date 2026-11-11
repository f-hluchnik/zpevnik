# The build targets print the path of what they built; everything goes under build/.
# make [pdf] [EDITION=<name>] [FORMAT=<name>]  generate the edition's .tex files and the score images, then
#                              compile build/editions/<name>/zpevnik.pdf (default edition: full);
#                              FORMAT=print|print-black builds it for paper into build/editions/<name>/<format>/
#                              (tools/formats.py; default: screen)
# make generate [EDITION=<name>]  only run the generator (tools/generate.py)
# make scores   only export the score images from MuseScore into build/scores/
#               (tools/scores.py; skips scores that are up to date)
# make song SONG=<id>  build only that song into build/songs/<id>.pdf (tools/build_song.py)
# make check [EDITION=<name>] [FORMAT=<name>]  the unit tests and the lints, then build the edition (which
#               fails on a link to a missing target) and run the one-page and chord checks on it
# make clean    delete build/
# PYTHON=<command>  the Python the tools run with (default python3); it must be 3.11 or newer
EDITION ?= full
FORMAT ?= screen
PYTHON ?= python3
REQUIRED_PYTHON := 3.11

# make check prints a heading per step; make and make check end with the path of the PDF.
step = @printf '\n==> %s\n' '$(1)'
finish = @printf '\n==> %s\n    %s/%s\n\n' '$(1)' "$(CURDIR)" "$$($(PYTHON) tools/build_edition.py --edition $(EDITION) --format $(FORMAT) --path)"

.PHONY: all generate scores compile pdf song check check-python clean

all: pdf

check-python:
	@if ! $(PYTHON) -c 'import sys; sys.exit(sys.version_info[:2] < tuple(map(int, "$(REQUIRED_PYTHON)".split("."))))' 2>/dev/null; then \
		echo "error: the tools need Python $(REQUIRED_PYTHON) or newer, but '$(PYTHON)' is: $$($(PYTHON) --version 2>&1)" >&2; \
		echo "       Activate the virtual environment (source .venv/bin/activate) or run make PYTHON=python3.12" >&2; \
		echo "       (README, Nastavení lokální kopie)" >&2; \
		exit 1; \
	fi

generate: check-python
	@$(PYTHON) tools/generate.py --edition $(EDITION)

scores: check-python
	@$(PYTHON) tools/scores.py

compile: generate scores
	@$(PYTHON) tools/build_edition.py --edition $(EDITION) --format $(FORMAT) > /dev/null

pdf: compile
	$(call finish,The PDF is ready:)

song: scores
	@$(PYTHON) tools/build_song.py $(SONG)

check: check-python
	$(call step,Unit tests)
	@$(PYTHON) -m unittest discover -s tools -q
	$(call step,Lint)
	@$(PYTHON) tools/lint.py
	$(call step,Build of the $(EDITION) edition)
	@$(MAKE) --no-print-directory compile
	$(call step,Checks of the built edition)
	@$(PYTHON) tools/check_pages.py --edition $(EDITION) --format $(FORMAT)
	@$(PYTHON) tools/chord_gaps.py --edition $(EDITION) --format $(FORMAT)
	$(call finish,All checks passed. The PDF:)

clean:
	rm -rf build
