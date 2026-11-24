"""Colours for a printer that wants CMYK: converted with a colour profile by littleCMS.

The profile describes the printer's press and paper: FOGRA39 (coated paper, the European
standard; TeX Live ships it in its colorprofiles package) or a .icc file the printer gives.
The conversion is relative colorimetric with black point compensation, the usual prepress
setting. Ghostscript cannot do it: its PDF writer converts with its own built-in profile,
whatever profile it is given.

Two things are converted: the red of the chords (to_cmyk, for a block in CMYK) and the RGB JPEG
pictures of a cover's design (convert_picture, for a cover in CMYK). A picture that carries its own
colour profile is converted from it; any other RGB is taken as sRGB.

littleCMS comes with the Python package Pillow (requirements-dev.txt): the only tool of the
build that needs a package, and only for an edition printed in CMYK.
"""
import io
import re
import subprocess
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

from edition import FOGRA39
from paths import STYLE_FILE

if TYPE_CHECKING:
    from PIL.ImageCms import ImageCmsTransform

FOGRA39_FILE = "FOGRA39L_coated.icc"
KPSEWHICH = "kpsewhich"  # finds a file of TeX Live
INSTALL_HINT = "install the packages of requirements-dev.txt into the virtual environment (README)"
CHORD_COLOUR = re.compile(r"\\definecolor\{chordred\}\{RGB\}\{\s*(\d+),\s*(\d+),\s*(\d+)\s*\}")
CHANNEL_MAX = 255
RGB_MODE, CMYK_MODE = "RGB", "CMYK"  # Pillow's names of the colour models
JPEG_QUALITY = 95  # a converted picture is compressed once more: little loss on top of its own


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


def pillow() -> tuple[ModuleType, ModuleType]:
    """Pillow's Image and ImageCms; ColourError if Pillow is not installed."""
    try:
        from PIL import Image, ImageCms
    except ImportError as error:
        raise ColourError(f"converting to CMYK needs Pillow: {INSTALL_HINT}") from error
    return Image, ImageCms


def cmyk_transform(profile: Path, source_profile: bytes | None = None) -> "ImageCmsTransform":
    """littleCMS's transform from RGB (sRGB, or the profile given as bytes) to the profile's CMYK:
    relative colorimetric with black point compensation."""
    _, image_cms = pillow()
    source = (image_cms.ImageCmsProfile(io.BytesIO(source_profile)) if source_profile
              else image_cms.createProfile("sRGB"))
    return image_cms.buildTransform(
        source, image_cms.getOpenProfile(str(profile)), RGB_MODE, CMYK_MODE,
        renderingIntent=image_cms.Intent.RELATIVE_COLORIMETRIC, flags=image_cms.Flags.BLACKPOINTCOMPENSATION)


def to_cmyk(rgb: tuple[int, int, int], profile: Path) -> tuple[float, float, float, float]:
    """An sRGB colour in the profile's CMYK, each ink from 0 to 1."""
    image, image_cms = pillow()
    pixel = image_cms.applyTransform(image.new(RGB_MODE, (1, 1), rgb), cmyk_transform(profile)).getpixel((0, 0))
    cyan, magenta, yellow, black = (channel / CHANNEL_MAX for channel in pixel)
    return cyan, magenta, yellow, black


def convert_picture(source: Path, target: Path, profile: Path) -> bool:
    """Write an RGB picture as a JPEG in the profile's CMYK, at its resolution; False, and nothing
    written, for a picture that is not RGB (grey or CMYK already)."""
    image, image_cms = pillow()
    image.MAX_IMAGE_PIXELS = None  # a cover at print resolution is larger than Pillow's guard
    with image.open(source) as picture:
        if picture.mode != RGB_MODE:
            return False
        transform = cmyk_transform(profile, picture.info.get("icc_profile"))
        options = {"dpi": picture.info["dpi"]} if "dpi" in picture.info else {}
        image_cms.applyTransform(picture, transform).save(target, "JPEG", quality=JPEG_QUALITY, **options)
    return True
