# The build targets print the path of what they built; everything goes under build/.
# make [pdf] [EDITION=<name>] [FORMAT=screen|print] [CHORDS=red|black] [SIZE=A4|A5]
#              generate the edition's .tex files and the score images, then compile
#              build/editions/<name>/zpevnik.pdf (default edition: full). The paper options (D-185):
#              FORMAT=print   for paper, into build/editions/<name>/print/ (tools/formats.py; default: screen)
#              CHORDS=black   with FORMAT=print: everything in black ink, into .../print-black/ (default: red)
#              SIZE=A5        with FORMAT=print: also place it on A5 for the edition's printer, as the
#                             [print] table of its edition.toml asks, zpevnik-a5.pdf next to it
#                             (tools/print_pdf.py, D-188; default: A4); it prints the margins it
#                             measured on the finished PDF
#              Any other value, or a paper option without FORMAT=print, stops make with an error.
# make generate [EDITION=<name>]  only run the generator (tools/generate.py)
# make scores   only export the score images from MuseScore into build/scores/
#               (tools/scores.py; skips scores that are up to date; with CHORDS=black also their
#               black-ink images)
# make song SONG=<id>  build only that song into build/songs/<id>.pdf (tools/build_song.py)
# make json    build the full book, write build/songs.json for the website (tools/songs_json.py) and
#              check it against tools/songs.schema.json (tools/validate_songs_json.py)
# make check [EDITION=<name>] [paper options]  the unit tests, the lints and the converter, then build the
#               edition (which fails on a link to a missing target; with SIZE=A5 also the A5 PDF and its
#               check) and run the one-page and chord checks on it
# make clean    delete build/
# PYTHON=<command>  the Python the tools run with (default python3); it must be 3.11 or newer
EDITION ?= full
FORMAT ?= screen
CHORDS ?= red
SIZE ?= A4
PYTHON ?= python3
REQUIRED_PYTHON := 3.11
REQUIREMENTS_DEV := requirements-dev.txt

# The paper options (D-185). The tools know a build by one format name (tools/formats.py):
# make's FORMAT and CHORDS choose it, SIZE only adds the A5 step after it.
SCREEN_FORMAT := screen
PRINT_FORMAT := print
BLACK_PRINT_FORMAT := print-black
DEFAULT_CHORDS := red
BLACK_CHORDS := black
DEFAULT_SIZE := A4
A5_SIZE := A5
FORMATS := $(SCREEN_FORMAT) $(PRINT_FORMAT)
CHORD_COLORS := $(DEFAULT_CHORDS) $(BLACK_CHORDS)
SIZES := $(DEFAULT_SIZE) $(A5_SIZE)

# $(call require-one-of,VARIABLE,values): stop unless the variable is exactly one of the values.
require-one-of = $(if $(and $(filter 1,$(words $($(1)))),$(filter $($(1)),$(2))),,\
	$(error $(1)=$($(1)) is not one of: $(2)))
# $(call require-paper,what): stop unless FORMAT is print.
require-paper = $(if $(filter $(PRINT_FORMAT),$(FORMAT)),,$(error $(1) needs FORMAT=$(PRINT_FORMAT)))

$(call require-one-of,FORMAT,$(FORMATS))
$(call require-one-of,CHORDS,$(CHORD_COLORS))
$(call require-one-of,SIZE,$(SIZES))
$(if $(filter-out $(DEFAULT_CHORDS),$(CHORDS)),$(call require-paper,CHORDS=$(CHORDS)))
$(if $(filter-out $(DEFAULT_SIZE),$(SIZE)),$(call require-paper,SIZE=$(SIZE)))
$(if $(PRINT_ARGS),$(error PRINT_ARGS is gone: the A5 step reads the margins and the pages to leave out from the [print] table of the edition's edition.toml (D-188)))

# Recursively expanded, so that a target's own FORMAT (json) chooses it too.
BUILD_FORMAT = $(if $(filter $(BLACK_CHORDS),$(CHORDS)),$(BLACK_PRINT_FORMAT),$(FORMAT))
A5_STEP = $(filter $(A5_SIZE),$(SIZE))
BUILD_ARGS = --edition $(EDITION) --format $(BUILD_FORMAT)
# The tool that makes the last file of the build says where it is (--path), so make does not repeat
# the layout of build/.
RESULT_TOOL = $(if $(A5_STEP),tools/print_pdf.py,tools/build_edition.py)

# make check prints a heading per step; make and make check end with the path of the PDF.
step = @printf '\n==> %s\n' '$(1)'
finish = @printf '\n==> %s\n    %s/%s\n\n' '$(1)' "$(CURDIR)" "$$($(PYTHON) $(RESULT_TOOL) $(BUILD_ARGS) --path)"

.PHONY: all generate scores compile pdf song json check check-python check-dev clean

all: pdf

check-python:
	@if ! $(PYTHON) -c 'import sys; sys.exit(sys.version_info[:2] < tuple(map(int, "$(REQUIRED_PYTHON)".split("."))))' 2>/dev/null; then \
		echo "error: the tools need Python $(REQUIRED_PYTHON) or newer, but '$(PYTHON)' is: $$($(PYTHON) --version 2>&1)" >&2; \
		echo "       Activate the virtual environment (source .venv/bin/activate) or run make PYTHON=python3.12" >&2; \
		echo "       (README, Nastavení lokální kopie)" >&2; \
		exit 1; \
	fi

# The tests and the check of songs.json need jsonschema (D-165, D-166); the other tools only the standard library.
check-dev: check-python
	@if ! $(PYTHON) -c 'import jsonschema' 2>/dev/null; then \
		echo "error: the tests and the check of songs.json need the packages of $(REQUIREMENTS_DEV) (jsonschema)" >&2; \
		echo "       Install them into the virtual environment: pip install -r $(REQUIREMENTS_DEV)" >&2; \
		echo "       (README, Nastavení lokální kopie)" >&2; \
		exit 1; \
	fi

generate: check-python
	@$(PYTHON) tools/generate.py --edition $(EDITION)

scores: check-python
	@$(PYTHON) tools/scores.py --format $(BUILD_FORMAT)

compile: generate scores
	@$(PYTHON) tools/build_edition.py $(BUILD_ARGS) > /dev/null
	$(if $(A5_STEP),@$(PYTHON) tools/print_pdf.py $(BUILD_ARGS))

pdf: compile
	$(call finish,The PDF is ready:)

song: scores
	@$(PYTHON) tools/build_song.py $(SONG)

# The website is built from the full book only (D-165): its pages are the screen PDF's.
json: override EDITION = full
json: override FORMAT = $(SCREEN_FORMAT)
json: override CHORDS = $(DEFAULT_CHORDS)
json: override SIZE = $(DEFAULT_SIZE)
json: check-dev compile
	@$(PYTHON) tools/songs_json.py
	@$(PYTHON) tools/validate_songs_json.py

check: check-dev
	$(call step,Unit tests)
	@$(PYTHON) -m unittest discover -s tools -q
	$(call step,Lint)
	@$(PYTHON) tools/lint.py
	$(call step,Converter)
	@$(PYTHON) tools/convert.py
	$(call step,Build of the $(EDITION) edition)
	@$(MAKE) --no-print-directory compile
	$(call step,Checks of the built edition)
	@$(PYTHON) tools/check_pages.py $(BUILD_ARGS)
	@$(PYTHON) tools/chord_gaps.py $(BUILD_ARGS)
	@$(PYTHON) tools/song_lines.py $(BUILD_ARGS)
	$(call finish,All checks passed. The PDF:)

clean:
	rm -rf build
