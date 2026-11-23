#!/usr/bin/env python3
"""The pictures of the cover (design.tex), made from the illustrator's scan (scan.jpg, 600 dpi).

Run once; its output is committed in assets/ (the cover is built by hand, README.md), so building
the cover and the book needs no Python. Deterministic: the same scan gives the same files.

  assets/front.jpg        the drawing with its rough painted edges, on white with even margins
  assets/paper-beige.jpg  the paper of the back: a texture in the tone of the drawing's sky
Each is the bleed box (A5 with 3 mm on every side) at 300 dpi.

Needs numpy and Pillow (not the songbook's tools, which use the standard library only):
  python3 -m pip install numpy pillow
  python3 editions/skaut-kravare/print-cover/make_assets.py [path/to/scan.jpg]
"""
import argparse
import colorsys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).parent
ASSETS = HERE / "assets"
SCAN = HERE / "scan.jpg"
DPI = 300
MM_PER_INCH = 25.4
JPEG_QUALITY = 92
TRIM_MM = (148, 210)
BLEED_MM = 3
WHITE = 255.0

# Boxes in the scan's pixels (left, top, right, bottom), measured on the scan: a column or row
# counts as painted where most of it is not bare paper (bright and grey).
SCAN_PAPER = (5, 1000, 60, 4000)               # bare paper in the left margin
SCAN_SKY = (2600, 300, 3300, 600)              # the sky's light wash, under the branch
SCAN_PAINTING = (99, 92, 3416, 4936)           # the painted area, rough edges included
ROUGH_EDGE_ROOM_PX = 40                        # paper kept around the painting's edges
ROUGH_MARGIN_MM = 6                            # from the trim to the painting, top and bottom

# The back's beige: the sky's hue, a step deeper so that it reads as beige, not as off-white.
BEIGE_SATURATION = 1.6
BEIGE_VALUE = 0.975
PAPER_SEED = 7
# The paper's shading, as fractions of its brightness: broad clouds, fine mottling, grain, fibres.
CLOUDS = (0.008, 150)  # (strength, blur radius in px)
MOTTLING = (0.004, 6)
GRAIN = 0.010
FIBRES = 0.012
FIBRE_COUNT = 900
FIBRE_LENGTH_PX = (15, 60)


def to_px(mm: float) -> int:
    return round(mm / MM_PER_INCH * DPI)


BLEED_BOX_PX = (to_px(TRIM_MM[0] + 2 * BLEED_MM), to_px(TRIM_MM[1] + 2 * BLEED_MM))


def mean_colour(scan: Image.Image, box: tuple[int, int, int, int]) -> np.ndarray:
    return np.asarray(scan.crop(box), dtype=float).reshape(-1, 3).mean(axis=0)


def white_balanced(scan: Image.Image) -> Image.Image:
    """The scan with its bare paper made pure white, so it meets a white page without a seam."""
    paper = mean_colour(scan, SCAN_PAPER)
    pixels = np.asarray(scan, dtype=float) * (WHITE / paper)
    return Image.fromarray(pixels.clip(0, WHITE).astype(np.uint8))


def front(scan: Image.Image) -> Image.Image:
    """The painting with its edges and some paper round them, centred on white."""
    left, top, right, bottom = SCAN_PAINTING
    room = ROUGH_EDGE_ROOM_PX
    painting = scan.crop((left - room, top - room, right + room, bottom + room))
    scale = to_px(TRIM_MM[1] - 2 * ROUGH_MARGIN_MM) / (bottom - top)
    painting = painting.resize((round(painting.width * scale), round(painting.height * scale)),
                               Image.Resampling.LANCZOS)
    page = Image.new("RGB", BLEED_BOX_PX, "white")
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
    shape = (BLEED_BOX_PX[1], BLEED_BOX_PX[0])
    shade = (CLOUDS[0] * blurred_noise(rng, shape, CLOUDS[1])
             + MOTTLING[0] * blurred_noise(rng, shape, MOTTLING[1])
             + GRAIN * rng.standard_normal(shape)
             + FIBRES * fibres(rng, shape))
    rgb = np.array(tint)[None, None, :] * (1 + shade[..., None])
    return Image.fromarray(rgb.clip(0, WHITE).astype(np.uint8))


def save(image: Image.Image, name: str) -> None:
    image.save(ASSETS / name, quality=JPEG_QUALITY, dpi=(DPI, DPI))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("scan", type=Path, nargs="?", default=SCAN,
                        help="the illustrator's scan of the drawing (default: scan.jpg)")
    scan = Image.open(parser.parse_args().scan).convert("RGB")
    ASSETS.mkdir(exist_ok=True)
    save(front(white_balanced(scan)), "front.jpg")
    tint = beige(scan)
    print("beige: #{:02X}{:02X}{:02X}".format(*(round(c) for c in tint)))
    save(paper(tint), "paper-beige.jpg")


if __name__ == "__main__":
    main()
