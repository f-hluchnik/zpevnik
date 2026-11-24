# The build targets print the path of what they built; everything goes under build/.
# make [pdf] [EDITION=<name>]  generate the edition's .tex files and the score images, then compile
#               build/editions/<name>/zpevnik.pdf, the PDF for the screen (default edition: full)
# make print [EDITION=<name>]  the PDF for the edition's printer, as the [print] table of its
#               edition.toml asks (docs/printing.md): the book typeset for paper in the format the
#               table chooses (tools/formats.py) and checked like make check checks it, then placed on
#               the printer's paper and checked again (tools/print_pdf.py), into build/print/<name>/
# make generate [EDITION=<name>]  only run the generator (tools/generate.py)
# make scores   only export the score images from MuseScore into build/scores/
#               (tools/scores.py; skips scores that are up to date)
# make song SONG=<id>  build only that song into build/songs/<id>.pdf (tools/build_song.py)
# make json    build the full book, write build/songs.json for the website (tools/songs_json.py) and
#              check it against tools/songs.schema.json (tools/validate_songs_json.py)
# make check [EDITION=<name>]  the unit tests, the lints and the converter, then build the edition
#               (which fails on a link to a missing target) and run the one-page and chord checks on it
# make clean    delete build/
# PYTHON=<command>  the Python the tools run with (default python3); it must be 3.11 or newer
EDITION ?= full
PYTHON ?= python3
REQUIRED_PYTHON := 3.11
REQUIREMENTS_DEV := requirements-dev.txt

# The format a build is typeset in (tools/formats.py). Not an option: make print sets it from the
# edition's [print] table for the build it starts.
BUILD_FORMAT := screen
# Options of earlier versions: an edition's paper, colours and size are set in its edition.toml.
REMOVED_OPTIONS := FORMAT CHORDS SIZE PRINT_ARGS
$(foreach option,$(REMOVED_OPTIONS),$(if $(filter command line,$(origin $(option))),\
	$(error $(option) is gone: make print EDITION=<name> prints an edition as the [print] table of its edition.toml asks (docs/printing.md))))

BUILD_ARGS = --edition $(EDITION) --format $(BUILD_FORMAT)

# make check and make print print a heading per step; the build targets end with the path of what
# they built. $(call finish,heading,tool): the tool says where its file is (--path), so make does not
# repeat the layout of build/.
step = @printf '\n==> %s\n' '$(1)'
finish = @printf '\n==> %s\n    %s/%s\n\n' '$(1)' "$(CURDIR)" "$$($(PYTHON) $(2) --edition $(EDITION) --path)"

.PHONY: all generate scores compile pdf print song json check edition-checks check-python check-dev clean

all: pdf

check-python:
	@if ! $(PYTHON) -c 'import sys; sys.exit(sys.version_info[:2] < tuple(map(int, "$(REQUIRED_PYTHON)".split("."))))' 2>/dev/null; then \
		echo "error: the tools need Python $(REQUIRED_PYTHON) or newer, but '$(PYTHON)' is: $$($(PYTHON) --version 2>&1)" >&2; \
		echo "       Activate the virtual environment (source .venv/bin/activate) or run make PYTHON=python3.12" >&2; \
		echo "       (README, Nastavení lokální kopie)" >&2; \
		exit 1; \
	fi

# The tests and the check of songs.json need jsonschema and Pillow (which a book in CMYK needs too);
# the other tools only the standard library.
check-dev: check-python
	@if ! $(PYTHON) -c 'import jsonschema, PIL' 2>/dev/null; then \
		echo "error: the tests and the check of songs.json need the packages of $(REQUIREMENTS_DEV) (jsonschema, Pillow)" >&2; \
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

pdf: compile
	$(call finish,The PDF is ready:,tools/build_edition.py)

# The format comes from the edition's [print] table, so the build and its checks run in a make of
# their own that is told it.
print: check-python
	@format=$$($(PYTHON) tools/print_pdf.py --edition $(EDITION) --block-format) && \
		printf '\n==> %s\n' "Build of the $(EDITION) edition for paper ($$format)" && \
		$(MAKE) --no-print-directory edition-checks BUILD_FORMAT=$$format
	$(call step,The PDF for the printer)
	@$(PYTHON) tools/print_pdf.py --edition $(EDITION)
	$(call finish,The PDF for the printer is ready:,tools/print_pdf.py)

song: scores
	@$(PYTHON) tools/build_song.py $(SONG)

# The website is built from the full book only: its pages are the screen PDF's.
json: override EDITION = full
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
	@$(MAKE) --no-print-directory edition-checks
	$(call finish,All checks passed. The PDF:,tools/build_edition.py)

# Run in a make of its own (check, print), so that it comes after the steps before it.
edition-checks: compile
	$(call step,Checks of the built edition)
	@$(PYTHON) tools/check_pages.py $(BUILD_ARGS)
	@$(PYTHON) tools/chord_gaps.py $(BUILD_ARGS)
	@$(PYTHON) tools/song_lines.py $(BUILD_ARGS)

clean:
	rm -rf build
