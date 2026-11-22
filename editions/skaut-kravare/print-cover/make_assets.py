#!/usr/bin/env python3
"""The generated pictures of the back cover (back.tex): tinted paper and spruce silhouettes.

Run once; its output is committed in assets/ (the cover is built by hand, README.md), so
building the cover needs no Python. Deterministic: the same seeds give the same files.

  assets/paper-<tint>.jpg   a paper texture over the bleed box, 300 dpi
  assets/spruces-<row>.tex  TikZ paths of a row of spruces, in mm from the row's bottom left

Needs numpy and Pillow (not the songbook's tools, which use the standard library only):
  python3 -m pip install numpy pillow
  python3 editions/skaut-kravare/print-cover/make_assets.py
"""
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ASSETS = Path(__file__).parent / "assets"
DPI = 300
MM_PER_INCH = 25.4
JPEG_QUALITY = 90
BLEED_BOX_MM = (154, 216)  # A5 with 3 mm bleed on every side

PAPER_TINTS = {  # name in back.tex: sRGB of the paper
    "cream": (237, 231, 214),
    "sage": (214, 220, 199),
    "moss": (186, 195, 166),
}
PAPER_SEED = 7
# The paper's shading, as fractions of its brightness: broad clouds, fine mottling, grain, fibres.
CLOUDS = (0.008, 150)  # (strength, blur radius in px)
MOTTLING = (0.004, 6)
GRAIN = 0.010
FIBRES = 0.012
FIBRE_COUNT = 900
FIBRE_LENGTH_PX = (15, 60)


@dataclass(frozen=True)
class SpruceRow:
    seed: int
    count: int
    min_height_mm: float
    max_height_mm: float
    base_jitter_mm: float  # how far a tree's foot may sit above the row's bottom


SPRUCE_ROWS = {
    "row": SpruceRow(seed=3, count=26, min_height_mm=14, max_height_mm=30, base_jitter_mm=2),
    "far": SpruceRow(seed=5, count=20, min_height_mm=55, max_height_mm=85, base_jitter_mm=0),
    "near": SpruceRow(seed=11, count=14, min_height_mm=40, max_height_mm=70, base_jitter_mm=3),
}
ROW_SPAN_MM = (-6, 154)  # the row runs a little past both edges of the bleed box
SPRUCE_WIDTH = 0.24      # half the width of a spruce's lowest tier, per its height
TRUNK_WIDTH = 0.02       # half the width of the trunk, per the height
MM_PER_TIER = 4


def to_px(mm: float) -> int:
    return round(mm / MM_PER_INCH * DPI)


def blurred_noise(rng: np.random.Generator, shape: tuple[int, int], radius: float) -> np.ndarray:
    """Gaussian-blurred white noise, normalised to mean 0 and deviation 1."""
    noise = Image.fromarray((rng.random(shape) * 255).astype(np.uint8))
    blurred = np.asarray(noise.filter(ImageFilter.GaussianBlur(radius)), dtype=float)
    return (blurred - blurred.mean()) / (blurred.std() + 1e-9)


def fibres(rng: np.random.Generator, shape: tuple[int, int]) -> np.ndarray:
    """Short horizontal streaks, lighter or darker, softened; values about -1 to 1."""
    height, width = shape
    streaks = np.zeros(shape)
    for _ in range(FIBRE_COUNT):
        y, x = rng.integers(0, height), rng.integers(0, width)
        streaks[y, x:x + rng.integers(*FIBRE_LENGTH_PX)] += rng.choice([-1, 1]) * 0.6
    image = Image.fromarray(((streaks + 1) * 127).clip(0, 255).astype(np.uint8))
    return np.asarray(image.filter(ImageFilter.GaussianBlur(1.2)), dtype=float) / 127 - 1


def paper(tint: tuple[int, int, int]) -> Image.Image:
    rng = np.random.default_rng(PAPER_SEED)
    shape = (to_px(BLEED_BOX_MM[1]), to_px(BLEED_BOX_MM[0]))
    shade = (CLOUDS[0] * blurred_noise(rng, shape, CLOUDS[1])
             + MOTTLING[0] * blurred_noise(rng, shape, MOTTLING[1])
             + GRAIN * rng.standard_normal(shape)
             + FIBRES * fibres(rng, shape))
    rgb = np.array(tint, dtype=float)[None, None, :] * (1 + shade[..., None])
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8))


def spruce(x: float, foot: float, height: float, rng: random.Random) -> list[tuple[float, float]]:
    """A spruce as a closed polygon (mm): the tip, then tiers of drooping branches down each side."""
    tiers = max(5, int(height / MM_PER_TIER))
    droop = height / tiers * 0.45
    sides = []
    for side in (1, -1):
        points = []
        for tier in range(1, tiers + 1):
            share = tier / tiers
            y = foot + height * (1 - share)
            reach = height * SPRUCE_WIDTH * share ** 0.9 * rng.uniform(0.85, 1.1)
            points += [(x + side * reach, y - droop), (x + side * reach * rng.uniform(0.45, 0.6), y)]
        sides.append(points)
    right, left = sides
    trunk = height * TRUNK_WIDTH
    return [(x, foot + height)] + right + [(x + trunk, foot), (x - trunk, foot)] + left[::-1]


def spruce_row(row: SpruceRow) -> list[list[tuple[float, float]]]:
    rng = random.Random(row.seed)
    start, end = ROW_SPAN_MM
    step = (end - start) / row.count
    return [spruce(start + step * (i + rng.uniform(0.1, 0.9)), rng.uniform(0, row.base_jitter_mm),
                   rng.uniform(row.min_height_mm, row.max_height_mm), rng)
            for i in range(row.count)]


def tikz_fills(polygons: list[list[tuple[float, float]]], name: str) -> str:
    lines = [f"% A row of spruces ({name}), made by make_assets.py: do not edit."]
    for polygon in polygons:
        lines.append("\\fill " + " -- ".join(f"({x:.2f}mm,{y:.2f}mm)" for x, y in polygon) + " -- cycle;")
    return "\n".join(lines) + "\n"


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for name, tint in PAPER_TINTS.items():
        paper(tint).save(ASSETS / f"paper-{name}.jpg", quality=JPEG_QUALITY, dpi=(DPI, DPI))
    for name, row in SPRUCE_ROWS.items():
        (ASSETS / f"spruces-{name}.tex").write_text(tikz_fills(spruce_row(row), name))


if __name__ == "__main__":
    main()
