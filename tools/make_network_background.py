#!/usr/bin/env python3
"""
Generate a dark abstract "network" header background image.

Creates a black/charcoal gradient with subtle teal/green network lines + nodes,
leaving extra negative space near the top-center for header text/logo.

Writes to `images/background.jpg` by default.

Usage:
  python tools/make_network_background.py

Options:
  --out images/background.jpg
  --width 2400 --height 1350
  --seed 128
"""

# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Michael A. David

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Palette:
    bg_top: Tuple[int, int, int] = (9, 16, 26)  # deep navy
    bg_bottom: Tuple[int, int, int] = (6, 10, 16)  # near-black
    teal: Tuple[int, int, int] = (0, 168, 120)  # site primary-ish
    mint: Tuple[int, int, int] = (167, 243, 208)  # site secondary-ish


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_rgb(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return (
        int(_lerp(c1[0], c2[0], t)),
        int(_lerp(c1[1], c2[1], t)),
        int(_lerp(c1[2], c2[2], t)),
    )


def make_vertical_gradient(width: int, height: int, top: Tuple[int, int, int], bottom: Tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (width, height))
    px = img.load()
    for y in range(height):
        t = y / max(1, height - 1)
        c = _lerp_rgb(top, bottom, t)
        for x in range(width):
            px[x, y] = c
    return img


def add_soft_glow(base: Image.Image, center_xy: Tuple[float, float], radius: float, color: Tuple[int, int, int], opacity: float) -> Image.Image:
    """Add a blurred radial glow centered at center_xy."""
    width, height = base.size
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = center_xy
    r = radius
    alpha = int(255 * max(0.0, min(1.0, opacity)))
    bbox = (cx - r, cy - r, cx + r, cy + r)
    draw.ellipse(bbox, fill=color + (alpha,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=max(8, radius / 8)))
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def add_noise(base: Image.Image, amount: float = 0.08) -> Image.Image:
    """Add subtle film grain noise."""
    width, height = base.size
    noise = Image.effect_noise((width, height), 32).convert("L")
    noise = ImageEnhance.Contrast(noise).enhance(1.3)
    noise = ImageEnhance.Brightness(noise).enhance(0.9)
    noise_rgba = Image.merge("RGBA", (noise, noise, noise, noise.point(lambda v: int(v * 0.35))))
    out = Image.alpha_composite(base.convert("RGBA"), noise_rgba).convert("RGB")
    return ImageEnhance.Contrast(out).enhance(1.02 if amount > 0 else 1.0)


def _avoid_header_zone(x: float, y: float, width: int, height: int) -> bool:
    """
    Reserve negative space for header title/logo.
    This is intentionally conservative: a wide band near the top-center.
    """
    # Header zone: top 35% and middle 60% of width.
    if y < height * 0.35 and (width * 0.2) < x < (width * 0.8):
        return True
    return False


def sample_nodes(rng: random.Random, width: int, height: int, count: int) -> List[Tuple[float, float]]:
    nodes: List[Tuple[float, float]] = []
    attempts = 0
    while len(nodes) < count and attempts < count * 80:
        attempts += 1
        # Bias nodes away from top: square the random to weight toward 1.0
        y = height * (0.12 + 0.88 * (rng.random() ** 0.55))

        # Bias nodes slightly toward edges for more negative space in center.
        r = rng.random()
        if r < 0.45:
            x = width * (rng.random() ** 0.7) * 0.38  # left region
        elif r < 0.9:
            x = width * (1.0 - (rng.random() ** 0.7) * 0.38)  # right region
        else:
            x = width * rng.random()  # anywhere (rare)

        if _avoid_header_zone(x, y, width, height):
            continue

        # Enforce a small minimum distance so nodes don't clump.
        ok = True
        for ox, oy in nodes:
            if (x - ox) ** 2 + (y - oy) ** 2 < (min(width, height) * 0.035) ** 2:
                ok = False
                break
        if not ok:
            continue

        nodes.append((x, y))
    return nodes


def k_nearest(nodes: List[Tuple[float, float]], idx: int, k: int) -> List[int]:
    x, y = nodes[idx]
    d = []
    for j, (x2, y2) in enumerate(nodes):
        if j == idx:
            continue
        d.append((j, (x - x2) ** 2 + (y - y2) ** 2))
    d.sort(key=lambda t: t[1])
    return [j for (j, _dist) in d[:k]]


def render_network(
    base: Image.Image,
    nodes: List[Tuple[float, float]],
    palette: Palette,
    rng: random.Random,
) -> Image.Image:
    width, height = base.size
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Draw lines.
    for i in range(len(nodes)):
        neighbors = k_nearest(nodes, i, k=rng.randint(2, 4))
        for j in neighbors:
            if j < i:
                continue
            x1, y1 = nodes[i]
            x2, y2 = nodes[j]
            dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            # Skip very long connections.
            if dist > min(width, height) * 0.42:
                continue

            # Fade with distance.
            t = min(1.0, dist / (min(width, height) * 0.45))
            alpha = int(255 * (0.18 * (1.0 - t) + 0.04))
            color = palette.teal if rng.random() < 0.75 else palette.mint
            draw.line((x1, y1, x2, y2), fill=color + (alpha,), width=1)

    # Add a subtle glow to the line layer.
    glow = layer.filter(ImageFilter.GaussianBlur(radius=max(1.2, min(width, height) / 900)))
    glow = ImageEnhance.Brightness(glow).enhance(1.3)
    glow = ImageEnhance.Contrast(glow).enhance(1.05)

    combined = Image.alpha_composite(base.convert("RGBA"), glow)
    combined = Image.alpha_composite(combined, layer)

    # Draw nodes: small crisp dot + larger blurred glow.
    node_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    nd = ImageDraw.Draw(node_layer)

    for (x, y) in nodes:
        base_r = rng.uniform(2.2, 4.2) * (min(width, height) / 1350)
        base_r = max(2.0, min(6.5, base_r))
        color = palette.mint if rng.random() < 0.25 else palette.teal

        # Glow
        glow_r = base_r * rng.uniform(3.4, 5.2)
        nd.ellipse((x - glow_r, y - glow_r, x + glow_r, y + glow_r), fill=color + (40,))
        # Core
        nd.ellipse((x - base_r, y - base_r, x + base_r, y + base_r), fill=color + (210,))

    node_glow = node_layer.filter(ImageFilter.GaussianBlur(radius=max(2.2, min(width, height) / 700)))
    node_glow = ImageEnhance.Brightness(node_glow).enhance(1.2)

    combined = Image.alpha_composite(combined, node_glow)
    combined = Image.alpha_composite(combined, node_layer)
    return combined.convert("RGB")


def generate_background(width: int, height: int, seed: int) -> Image.Image:
    rng = random.Random(seed)
    palette = Palette()

    base = make_vertical_gradient(width, height, palette.bg_top, palette.bg_bottom)

    # Glow behind logo/title (upper center), but subtle to keep text readable.
    base = add_soft_glow(
        base,
        center_xy=(width * 0.5, height * 0.16),
        radius=min(width, height) * 0.32,
        color=palette.teal,
        opacity=0.18,
    )
    # Secondary glow to add depth (lower left).
    base = add_soft_glow(
        base,
        center_xy=(width * 0.22, height * 0.78),
        radius=min(width, height) * 0.36,
        color=palette.mint,
        opacity=0.09,
    )

    base = add_noise(base, amount=0.08)

    nodes = sample_nodes(rng, width, height, count=int(70 + (width * height) / (2400 * 1350) * 10))
    out = render_network(base, nodes, palette, rng)

    # Gentle vignette.
    vignette = Image.new("L", (width, height), 0)
    vd = ImageDraw.Draw(vignette)
    pad = min(width, height) * 0.06
    vd.rectangle((pad, pad, width - pad, height - pad), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=min(width, height) / 12))
    out_rgba = out.convert("RGBA")
    out_rgba.putalpha(vignette)
    out = Image.alpha_composite(Image.new("RGBA", (width, height), (0, 0, 0, 255)), out_rgba).convert("RGB")

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "images" / "background.jpg"), help="Output JPG path")
    parser.add_argument("--width", type=int, default=2400, help="Output width")
    parser.add_argument("--height", type=int, default=1350, help="Output height")
    parser.add_argument("--seed", type=int, default=128, help="Random seed for deterministic output")
    args = parser.parse_args()

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = generate_background(args.width, args.height, seed=args.seed)
    img.save(out_path, format="JPEG", quality=92, optimize=True, progressive=True)
    print(f"Wrote {out_path} ({args.width}x{args.height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
