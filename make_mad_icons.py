#!/usr/bin/env python3
"""
make_mad_icons.py

Generate a full icon set + animated GIF set from `web-app-manifest-512x512.png`
in the current working directory.

Outputs are written to `dist_icons/` and zipped into `MAD_icons.zip`.

Requirements:
  - Pillow (PIL) only
"""

# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Michael A. David

from __future__ import annotations

import math
import os
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps


INPUT_FILE = "web-app-manifest-512x512.png"
OUT_DIR = "dist_icons"
ZIP_NAME = "MAD_icons.zip"


PNG_OUTPUTS: Sequence[Tuple[str, int]] = (
    ("apple-touch-icon.png", 180),
    ("favicon-96x96.png", 96),
    ("web-app-manifest-192x192.png", 192),
    ("web-app-manifest-512x512.png", 512),
)

ICO_SIZES: Sequence[Tuple[int, int]] = ((16, 16), (32, 32), (48, 48), (64, 64))

GIF_OUTPUTS: Sequence[Tuple[str, int]] = (
    ("favicon-32x32.gif", 32),
    ("favicon-64x64.gif", 64),
    ("favicon-96x96.gif", 96),
    ("apple-touch-icon.gif", 180),
    ("web-app-manifest-192x192.gif", 192),
    ("web-app-manifest-512x512.gif", 512),
)


@dataclass(frozen=True)
class ElectricSignParams:
    frames: int = 10
    frame_ms: int = 100
    pulse_min: float = 0.94
    pulse_max: float = 1.10
    glow_strength_min: float = 0.40
    glow_strength_max: float = 0.85


def die(message: str, code: int = 2) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_input_image(path: Path) -> Image.Image:
    if not path.exists():
        die(f"Missing input file: {path.name}\nExpected to find it in: {path.parent}")
    try:
        img = Image.open(path)
        img.load()
        return img.convert("RGBA")
    except Exception as exc:  # noqa: BLE001
        die(f"Failed to read {path.name}: {exc}")


def resize_square_rgba(img: Image.Image, size: int) -> Image.Image:
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    if img.size == (size, size):
        return img.copy()
    return img.resize((size, size), resample=Image.LANCZOS)


def save_png_set(base: Image.Image, out_dir: Path) -> None:
    for name, size in PNG_OUTPUTS:
        out_path = out_dir / name
        resized = resize_square_rgba(base, size)
        resized.save(out_path, format="PNG", optimize=True)


def save_favicon_ico(base: Image.Image, out_dir: Path) -> None:
    out_path = out_dir / "favicon.ico"
    # Pillow will generate all requested sizes from the provided base image.
    base_rgba = resize_square_rgba(base, 512)
    base_rgba.save(out_path, format="ICO", sizes=list(ICO_SIZES))


def save_favicon_svg(out_dir: Path) -> None:
    out_path = out_dir / "favicon.svg"
    # Simple wrapper around the 512x512 PNG in the same directory.
    svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="512" height="512" viewBox="0 0 512 512">
  <image width="512" height="512" href="web-app-manifest-512x512.png" />
</svg>
"""
    out_path.write_text(svg, encoding="utf-8")


def _green_glow_mask(img_rgba: Image.Image) -> Image.Image:
    """
    Create a mask for "green-dominant" pixels while excluding near-white letters.

    Returns an 8-bit L image suitable for blurring and alpha use.
    """
    img = img_rgba.convert("RGBA")
    r, g, b, _a = img.split()

    # Green dominance: g - max(r, b)
    max_rb = ImageChops.lighter(r, b)
    dominance = ImageChops.subtract(g, max_rb)

    # Exclude whites: where min(r,g,b) is high -> likely letters
    min_rgb = ImageChops.darker(r, ImageChops.darker(g, b))
    white_mask = min_rgb.point(lambda v: 255 if v >= 215 else 0)
    not_white = ImageOps.invert(white_mask)

    # Threshold dominance into a mask; small values become 0.
    dom_mask = dominance.point(lambda v: 0 if v < 28 else min(255, int((v - 28) * 5)))

    # Also suppress very dark areas to avoid noise.
    g_floor = g.point(lambda v: 0 if v < 55 else 255)
    mask = ImageChops.multiply(dom_mask, g_floor)

    # Remove whites explicitly.
    mask = ImageChops.multiply(mask, not_white)

    return mask.convert("L")


def _make_glow_overlay(img_rgba: Image.Image, strength: float) -> Image.Image:
    """
    Create a neon-green glow overlay (RGBA) to alpha-composite over the base.

    `strength` in [0..1] controls opacity.
    """
    size = max(img_rgba.size)
    mask = _green_glow_mask(img_rgba)

    # Blur radius scaled by output size so small icons still glow a bit.
    radius = max(1.2, size / 96.0 * 2.0)
    blurred = mask.filter(ImageFilter.GaussianBlur(radius=radius))

    # Boost the glow mask to make it readable after blur.
    blurred = ImageEnhance.Contrast(blurred).enhance(1.6)
    blurred = ImageEnhance.Brightness(blurred).enhance(1.15)

    # Colorize glow to neon green; use blurred mask as alpha.
    # Keep it subtle so it doesn't wash out the logo.
    glow_color = (70, 255, 170)  # neon-ish green
    alpha_scale = int(255 * max(0.0, min(1.0, strength)))
    alpha = blurred.point(lambda v: int(v * alpha_scale / 255))

    overlay = Image.new("RGBA", img_rgba.size, glow_color + (0,))
    overlay.putalpha(alpha)
    return overlay


def _pulse_factor(t: float, lo: float, hi: float) -> float:
    # Smooth sine pulse from lo..hi.
    s = (math.sin(2.0 * math.pi * t) + 1.0) / 2.0
    return lo + (hi - lo) * s


def generate_electric_frames(base: Image.Image, size: int, params: ElectricSignParams) -> List[Image.Image]:
    """
    Generate frames with:
      - subtle global brightness pulse
      - selective neon glow on green-dominant pixels (keeps white letters crisp)
    """
    base_rgba = resize_square_rgba(base, size)

    frames: List[Image.Image] = []
    for i in range(params.frames):
        t = i / params.frames

        # Global pulse.
        pulse = _pulse_factor(t, params.pulse_min, params.pulse_max)
        pulsed = ImageEnhance.Brightness(base_rgba).enhance(pulse)

        # Flicker the glow slightly.
        flicker = 0.5 + 0.5 * math.sin(2.0 * math.pi * (t * 3.0 + 0.15))
        strength = params.glow_strength_min + (params.glow_strength_max - params.glow_strength_min) * flicker

        overlay = _make_glow_overlay(pulsed, strength=strength)
        frame = Image.alpha_composite(pulsed, overlay)

        frames.append(frame)

    return frames


def save_gif(frames: Sequence[Image.Image], out_path: Path, frame_ms: int) -> None:
    if not frames:
        die("Internal error: no GIF frames generated.")
    first, *rest = frames
    # Use RGBA frames, let Pillow handle palette conversion for GIF.
    first.save(
        out_path,
        format="GIF",
        save_all=True,
        append_images=list(rest),
        duration=frame_ms,
        loop=0,
        disposal=2,
        optimize=True,
    )


def save_gif_set(base: Image.Image, out_dir: Path) -> None:
    params = ElectricSignParams()
    for name, size in GIF_OUTPUTS:
        out_path = out_dir / name
        frames = generate_electric_frames(base, size=size, params=params)
        save_gif(frames, out_path=out_path, frame_ms=params.frame_ms)


def zip_dist(out_dir: Path, zip_path: Path) -> None:
    files = sorted([p for p in out_dir.iterdir() if p.is_file()])
    if not files:
        die(f"No files found in {out_dir} to zip.")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            # Flat zip (no folders)
            zf.write(p, arcname=p.name)


def print_readme(out_dir: Path, zip_path: Path) -> None:
    print("\nREADME")
    print("------")
    print("Run:")
    print("  python make_mad_icons.py")
    print("")
    print("Outputs:")
    print(f"  - Icons/GIFs: {out_dir}/")
    print(f"  - Zip file:   {zip_path}")
    print("")


def main(argv: Sequence[str] | None = None) -> int:
    _ = argv or []
    cwd = Path.cwd()
    input_path = cwd / INPUT_FILE
    out_dir = cwd / OUT_DIR
    zip_path = cwd / ZIP_NAME

    base = load_input_image(input_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    save_png_set(base, out_dir)
    save_favicon_ico(base, out_dir)
    save_favicon_svg(out_dir)
    save_gif_set(base, out_dir)

    zip_dist(out_dir, zip_path)
    print_readme(out_dir, zip_path)
    print(f"Done. Wrote {len(list(out_dir.iterdir()))} files to {out_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
