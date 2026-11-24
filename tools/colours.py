"""Colours for a printer that wants CMYK: converted with a colour profile by littleCMS.

The profile describes the printer's press and paper: FOGRA39 (coated paper, the European
standard; TeX Live ships it in its colorprofiles package) or a .icc file the printer gives.
The conversion is relative colorimetric with black point compensation, the usual prepress
setting. Ghostscript cannot do it: its PDF writer converts with its own built-in profile,
whatever profile it is given.

littleCMS comes with the Python package Pillow (requirements-dev.txt): the only tool of the
build that needs a package, and only for an edition printed in CMYK.
"""
import re
import subprocess
from pathlib import Path

from edition import FOGRA39
from paths import STYLE_FILE

FOGRA39_FILE = "FOGRA39L_coated.icc"
KPSEWHICH = "kpsewhich"  # finds a file of TeX Live
INSTALL_HINT = "install the packages of requirements-dev.txt into the virtual environment (README)"
CHORD_COLOUR = re.compile(r"\\definecolor\{chordred\}\{RGB\}\{\s*(\d+),\s*(\d+),\s*(\d+)\s*\}")
CHANNEL_MAX = 255


class ColourError(Exception):
    """A colour cannot be converted: no Pillow, no profile."""


def profile_file(root: Path, profile: str) -> Path:
    """The file of a profile the edition names: FOGRA39 from TeX Live, or the edition's .icc file."""
    if profile != FOGRA39:
        return root / profile
    try:
        found = subprocess.run([KPSEWHICH, FOGRA39_FILE], capture_output=True, text=True).stdout.strip()
    except OSError as error:
        raise ColourError(f"{KPSEWHICH} not found: install TeX Live (README)") from error
    if not found:
        raise ColourError(f"TeX Live has no {FOGRA39_FILE}: install its package colorprofiles")
    return Path(found)


def chord_colour(root: Path) -> tuple[int, int, int]:
    """The red of the chords, as zpevnik.sty defines it for the screen."""
    match = CHORD_COLOUR.search((root / STYLE_FILE).read_text(encoding="utf-8"))
    if match is None:
        raise ColourError(f"{STYLE_FILE} defines no chordred in RGB")
    red, green, blue = (int(value) for value in match.groups())
    return red, green, blue


def to_cmyk(rgb: tuple[int, int, int], profile: Path) -> tuple[float, float, float, float]:
    """An sRGB colour in the profile's CMYK, each ink from 0 to 1."""
    try:
        from PIL import Image, ImageCms
    except ImportError as error:
        raise ColourError(f"converting to CMYK needs Pillow: {INSTALL_HINT}") from error
    transform = ImageCms.buildTransform(
        ImageCms.createProfile("sRGB"), ImageCms.getOpenProfile(str(profile)), "RGB", "CMYK",
        renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
    pixel = ImageCms.applyTransform(Image.new("RGB", (1, 1), rgb), transform).getpixel((0, 0))
    cyan, magenta, yellow, black = (channel / CHANNEL_MAX for channel in pixel)
    return cyan, magenta, yellow, black
