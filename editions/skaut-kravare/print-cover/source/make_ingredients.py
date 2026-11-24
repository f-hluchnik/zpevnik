#!/usr/bin/env python3
"""The pictures of the cover, made from the illustrator's scan (scan.jpg, 1200 dpi): run by hand.

The design (../design.tex) is drawn from these ingredients, committed; make print converts them to
the printer's CMYK. Deterministic: the same scan gives the same files.

  ../front.jpg           the front for the printer: the painted area with its rough edges, on
                         white, 600 ppi
  ../paper.jpg           the back's paper, in the tone of the drawing's sky, 300 ppi
  ../../cover.jpg        the front for the screen PDF's first page (../../cover.tex), 300 ppi
Each picture is the bleed box (A5 with 3 mm on every side), in sRGB.

Needs numpy and Pillow:
  python3 -m pip install numpy pillow
  python3 editions/skaut-kravare/print-cover/source/make_ingredients.py [path/to/scan.jpg]
"""
import argparse
import colorsys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).parent
DESIGN_FOLDER = HERE.parent
EDITION_FOLDER = DESIGN_FOLDER.parent
SCAN = HERE / "scan.jpg"
MM_PER_INCH = 25.4
JPEG_QUALITY = 92
TRIM_MM = (148, 210)
BLEED_MM = 3
WHITE = 255
PRINT_PPI = 600   # twice what a press resolves: the picture is not what limits the print
SCREEN_PPI = 300
PAPER_PPI = 300   # a generated texture: more pixels would only make the grain finer

# Boxes in the scan's pixels (left, top, right, bottom), measured on scan.jpg: a column or row
# counts as painted where most of it is not bare paper (bright and grey). The scan has a yellow
# strip of the scanner's lid, under 1 mm, along three edges; every box stays inside it.
SCAN_PAPER = (100, 2000, 160, 8000)     # bare paper in the left margin
SCAN_SKY = (5200, 600, 6600, 1200)      # the sky's light wash, under the branch
SCAN_PAINTING = (234, 220, 6864, 9904)  # the painted area, rough edges included
ROUGH_EDGE_ROOM_PX = 80                 # paper kept around the painting's edges
ROUGH_MARGIN_MM = 6                     # from the trim to the painting, top and bottom

# The back's beige: the sky's hue, a step deeper so that it reads as beige, not as off-white.
BEIGE_SATURATION = 1.6
BEIGE_VALUE = 0.975
PAPER_SEED = 7
# The paper's shading, as fractions of its brightness: broad clouds, fine mottling, grain, fibres.
CLOUDS = (0.008, 150)  # (strength, blur radius in px at PAPER_PPI)
MOTTLING = (0.004, 6)
GRAIN = 0.010
FIBRES = 0.012
FIBRE_COUNT = 900
FIBRE_LENGTH_PX = (15, 60)


def to_px(mm: float, ppi: int) -> int:
    return round(mm / MM_PER_INCH * ppi)


def bleed_box_px(ppi: int) -> tuple[int, int]:
    return to_px(TRIM_MM[0] + 2 * BLEED_MM, ppi), to_px(TRIM_MM[1] + 2 * BLEED_MM, ppi)


def mean_colour(image: Image.Image, box: tuple[int, int, int, int]) -> np.ndarray:
    return np.asarray(image.crop(box), dtype=float).reshape(-1, 3).mean(axis=0)


def white_balanced(scan: Image.Image) -> Image.Image:
    """The scan with its bare paper made pure white, so it meets a white page without a seam."""
    paper = mean_colour(scan, SCAN_PAPER)
    tables = [[min(WHITE, round(v * WHITE / channel)) for v in range(WHITE + 1)] for channel in paper]
    return scan.point([value for table in tables for value in table])


def front(scan: Image.Image, ppi: int) -> Image.Image:
    """The painting with its edges and some paper round them, centred on white."""
    left, top, right, bottom = SCAN_PAINTING
    room = ROUGH_EDGE_ROOM_PX
    painting = scan.crop((left - room, top - room, right + room, bottom + room))
    scale = to_px(TRIM_MM[1] - 2 * ROUGH_MARGIN_MM, ppi) / (bottom - top)
    painting = painting.resize((round(painting.width * scale), round(painting.height * scale)),
                               Image.Resampling.LANCZOS)
    page = Image.new("RGB", bleed_box_px(ppi), "white")
    page.paste(painting, ((page.width - painting.width) // 2, (page.height - painting.height) // 2))
    return page


def beige(scan: Image.Image) -> tuple[float, float, float]:
    hue, saturation, value = colorsys.rgb_to_hsv(*(mean_colour(scan, SCAN_SKY) / WHITE))
    red, green, blue = colorsys.hsv_to_rgb(hue, min(1.0, saturation * BEIGE_SATURATION),
                                           value * BEIGE_VALUE)
    return red * WHITE, green * WHITE, blue * WHITE


def blurred_noise(rng: np.random.Generator, shape: tuple[int, int], radius: float) -> np.ndarray:
    """Gaussian-blurred white noise, normalised to mean 0 and deviation 1."""
    noise = Image.fromarray((rng.random(shape) * WHITE).astype(np.uint8))
    blurred = np.asarray(noise.filter(ImageFilter.GaussianBlur(radius)), dtype=float)
    return (blurred - blurred.mean()) / (blurred.std() + 1e-9)


def fibres(rng: np.random.Generator, shape: tuple[int, int]) -> np.ndarray:
    """Short horizontal streaks, lighter or darker, softened; values about -1 to 1."""
    height, width = shape
    streaks = np.zeros(shape)
    for _ in range(FIBRE_COUNT):
        y, x = rng.integers(0, height), rng.integers(0, width)
        streaks[y, x:x + rng.integers(*FIBRE_LENGTH_PX)] += rng.choice([-1, 1]) * 0.6
    image = Image.fromarray(((streaks + 1) * 127).clip(0, WHITE).astype(np.uint8))
    return np.asarray(image.filter(ImageFilter.GaussianBlur(1.2)), dtype=float) / 127 - 1


def paper(tint: tuple[float, float, float]) -> Image.Image:
    rng = np.random.default_rng(PAPER_SEED)
    width, height = bleed_box_px(PAPER_PPI)
    shape = (height, width)
    shade = (CLOUDS[0] * blurred_noise(rng, shape, CLOUDS[1])
             + MOTTLING[0] * blurred_noise(rng, shape, MOTTLING[1])
             + GRAIN * rng.standard_normal(shape)
             + FIBRES * fibres(rng, shape))
    rgb = np.array(tint)[None, None, :] * (1 + shade[..., None])
    return Image.fromarray(rgb.clip(0, WHITE).astype(np.uint8))


def save(image: Image.Image, path: Path, ppi: int) -> None:
    image.save(path, quality=JPEG_QUALITY, dpi=(ppi, ppi))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("scan", type=Path, nargs="?", default=SCAN,
                        help="the illustrator's scan of the drawing (default: scan.jpg)")
    Image.MAX_IMAGE_PIXELS = None  # the 1200 dpi scan is larger than Pillow's guard
    scan = Image.open(parser.parse_args().scan).convert("RGB")
    balanced = white_balanced(scan)
    save(front(balanced, PRINT_PPI), DESIGN_FOLDER / "front.jpg", PRINT_PPI)
    save(front(balanced, SCREEN_PPI), EDITION_FOLDER / "cover.jpg", SCREEN_PPI)
    tint = beige(scan)
    print("beige: #{:02X}{:02X}{:02X}".format(*(round(c) for c in tint)))
    save(paper(tint), DESIGN_FOLDER / "paper.jpg", PAPER_PPI)


if __name__ == "__main__":
    main()
