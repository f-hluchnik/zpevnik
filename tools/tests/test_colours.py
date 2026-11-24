"""Unit tests for the conversion of colours to the printer's CMYK.

The conversion itself needs TeX Live's FOGRA39 profile, and is skipped without it (CI runs the unit
tests outside TeX Live).

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import colours
from colours import ColourError, chord_colour, convert_picture, profile_file, to_cmyk
from edition import FOGRA39
from paths import REPO_ROOT, STYLE_FILE


def fogra39() -> Path | None:
    try:
        return profile_file(REPO_ROOT, FOGRA39)
    except ColourError:
        return None


FOGRA39_PROFILE = fogra39()


class Chords(unittest.TestCase):
    def test_the_red_of_the_chords_is_read_from_the_style(self):
        red, green, blue = chord_colour(REPO_ROOT)
        self.assertGreater(red, max(green, blue))

    def test_a_style_without_it_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / STYLE_FILE).write_text("\\definecolor{other}{RGB}{1, 2, 3}\n", encoding="utf-8")
            with self.assertRaisesRegex(ColourError, "no chordred"):
                chord_colour(Path(tmp))


class Profiles(unittest.TestCase):
    def test_an_edition_profile_is_a_file_of_the_repository(self):
        self.assertEqual(profile_file(Path("/repo"), "editions/lite/printer.icc"),
                         Path("/repo/editions/lite/printer.icc"))

    def test_fogra39_without_tex_live_or_its_profile_is_an_error(self):
        with mock.patch.object(colours.subprocess, "run", return_value=mock.Mock(stdout="")):
            with self.assertRaisesRegex(ColourError, "colorprofiles"):
                profile_file(Path("/repo"), FOGRA39)
        with mock.patch.object(colours.subprocess, "run", side_effect=FileNotFoundError("kpsewhich")):
            with self.assertRaisesRegex(ColourError, "install TeX Live"):
                profile_file(Path("/repo"), FOGRA39)


@unittest.skipIf(FOGRA39_PROFILE is None, "TeX Live's FOGRA39 profile is not installed")
class Conversion(unittest.TestCase):
    def test_white_has_no_ink_and_black_is_mostly_black_ink(self):
        self.assertEqual(to_cmyk((255, 255, 255), FOGRA39_PROFILE), (0, 0, 0, 0))
        cyan, magenta, yellow, black = to_cmyk((0, 0, 0), FOGRA39_PROFILE)
        self.assertGreater(black, max(cyan, magenta, yellow))

    def test_the_red_of_the_chords_is_magenta_and_yellow(self):
        cyan, magenta, yellow, _ = to_cmyk(chord_colour(REPO_ROOT), FOGRA39_PROFILE)
        self.assertLess(cyan, 0.1)
        self.assertGreater(min(magenta, yellow), 0.7)

    def test_an_rgb_picture_becomes_a_cmyk_jpeg_at_its_resolution_and_grey_stays_as_it_is(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            Image.new("RGB", (4, 2), (184, 39, 39)).save(folder / "red.jpg", dpi=(600, 600))
            Image.new("L", (4, 2), 128).save(folder / "grey.jpg")
            self.assertTrue(convert_picture(folder / "red.jpg", folder / "red-cmyk.jpg", FOGRA39_PROFILE))
            self.assertFalse(convert_picture(folder / "grey.jpg", folder / "grey-cmyk.jpg", FOGRA39_PROFILE))
            with Image.open(folder / "red-cmyk.jpg") as converted:
                self.assertEqual(converted.mode, "CMYK")
                self.assertEqual(tuple(round(value) for value in converted.info["dpi"]), (600, 600))
            self.assertFalse((folder / "grey-cmyk.jpg").exists())
