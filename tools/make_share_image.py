# SPDX-License-Identifier: MIT
"""
Generate an Open Graph / social share image for the site.

This script creates `images/share.jpg` (1200x630) with:
  - a dark, slightly textured background
  - a simple "MAD" network-style logo mark (transparent overlay)
  - name + subtitle text (optional)

Why this exists:
  Social previews (iMessage, Slack, Twitter/X, etc.) prefer a 1200x630 image.
  A plain background photo often looks empty in a small preview, so this
  provides a clean, readable card that matches the site’s theme.

Usage:
  python tools/make_share_image.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont


@dataclass(frozen=True)
class ShareSpec:
    width: int = 1200
    height: int = 630
    background_top: Tuple[int, int, int] = (7, 14, 20)
    background_bottom: Tuple[int, int, int] = (10, 22, 30)
    accent: Tuple[int, int, int] = (0, 168, 120)  # ~site primary
    ink: Tuple[int, int, int] = (240, 240, 240)
    muted: Tuple[int, int, int] = (180, 180, 180)


def _find_font(candidates: Sequence[Path], size: int) -> Optional[ImageFont.FreeTypeFont]:
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except Exception:
                continue
    return None


def _load_fonts() -> Tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
    """
    Best-effort font lookup.
    Falls back to PIL’s default bitmap font if no TTF is available.
    """
    # Common font locations (Linux + macOS). This repo runs on GH Actions/Linux.
    title_candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/Library/Fonts/Arial Bold.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]
    subtitle_candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]

    title = _find_font(title_candidates, size=64)
    subtitle = _find_font(subtitle_candidates, size=32)

    if title is None or subtitle is None:
        # Very small, but still produces a valid image in constrained envs.
        fallback = ImageFont.load_default()
        return fallback, fallback
    return title, subtitle


def _lerp(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))


def _vertical_gradient(spec: ShareSpec) -> Image.Image:
    img = Image.new("RGB", (spec.width, spec.height), spec.background_top)
    px = img.load()
    for y in range(spec.height):
        t = y / max(1, spec.height - 1)
        r = _lerp(spec.background_top[0], spec.background_bottom[0], t)
        g = _lerp(spec.background_top[1], spec.background_bottom[1], t)
        b = _lerp(spec.background_top[2], spec.background_bottom[2], t)
        for x in range(spec.width):
            px[x, y] = (r, g, b)
    return img


def _add_vignette(img: Image.Image, strength: float = 0.55) -> Image.Image:
    w, h = img.size
    overlay = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(overlay)
    # Darken edges; keep center brighter
    for i in range(0, max(w, h), 6):
        t = i / max(w, h)
        alpha = int(255 * strength * t)
        draw.rectangle([0 + i, 0 + i, w - i, h - i], outline=alpha)
    overlay = overlay.filter(ImageFilter.GaussianBlur(18))
    out = img.copy()
    out.putalpha(255)
    out = Image.composite(out, Image.new("RGBA", (w, h), (0, 0, 0, 255)), overlay)
    return out.convert("RGBA")


def _draw_network_logo(spec: ShareSpec, size: int = 420) -> Image.Image:
    """
    Create a transparent logo-like mark inspired by images/logo-mad-green-transparent.svg
    without relying on SVG rendering at build time.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Coordinates normalized to a 1024 viewbox (from the SVG), then scaled.
    def s(v: float) -> float:
        return v * size / 1024.0

    # Network polygon + chords
    network_paths = [
        [(150, 400), (300, 200), (520, 160), (750, 220), (880, 380), (830, 580), (620, 680), (400, 620), (240, 720), (150, 400)],
        [(300, 200), (400, 620)],
        [(520, 160), (620, 680)],
        [(750, 220), (400, 620)],
        [(880, 380), (520, 160)],
        [(240, 720), (620, 680)],
        [(150, 400), (750, 220)],
        [(240, 720), (830, 580)],
    ]

    stroke = (255, 255, 255, 160)
    for path in network_paths:
        pts = [(s(x), s(y)) for x, y in path]
        d.line(pts, fill=stroke, width=max(2, int(size * 0.008)), joint="curve")

    # Nodes
    node_r = max(4, int(size * 0.012))
    for x, y in [(150, 400), (300, 200), (520, 160), (750, 220), (880, 380), (830, 580), (620, 680), (400, 620), (240, 720)]:
        cx, cy = s(x), s(y)
        d.ellipse([cx - node_r, cy - node_r, cx + node_r, cy + node_r], fill=(255, 255, 255, 210))

    # Letters (approximate positioning)
    title_font, _ = _load_fonts()
    # Scale font size to fit the square.
    font_size = int(size * 0.34)
    if hasattr(title_font, "path"):  # FreeType font detected
        try:
            title_font = ImageFont.truetype(getattr(title_font, "path"), size=font_size)  # type: ignore[arg-type]
        except Exception:
            title_font = ImageFont.load_default()
    else:
        title_font = ImageFont.load_default()

    green = (*spec.accent, 255)
    d.text((s(110), s(370) - font_size), "M", fill=green, font=title_font)
    d.text((s(370), s(650) - font_size), "A", fill=green, font=title_font)
    d.text((s(610), s(820) - font_size), "D", fill=green, font=title_font)

    # Subtle glow
    glow = img.copy().filter(ImageFilter.GaussianBlur(10))
    glow = ImageEnhanceBrightness(glow, 1.25)
    out = Image.alpha_composite(glow, img)
    return out


def ImageEnhanceBrightness(img: Image.Image, factor: float) -> Image.Image:
    # Local helper to avoid importing ImageEnhance for one operation.
    # Simple brightness scaling in linear-ish space.
    if factor == 1:
        return img
    r, g, b, a = img.split()
    r = r.point(lambda x: max(0, min(255, int(x * factor))))
    g = g.point(lambda x: max(0, min(255, int(x * factor))))
    b = b.point(lambda x: max(0, min(255, int(x * factor))))
    return Image.merge("RGBA", (r, g, b, a))


def make_share_image(
    out_path: Path,
    name: str = "Michael A. David, PhD",
    subtitle: str = "Translational Orthopedics • Machine Learning • Multimodal Imaging • Scientific Art",
) -> None:
    spec = ShareSpec()
    base = _vertical_gradient(spec)
    base = _add_vignette(base, strength=0.55)

    # Logo mark (transparent overlay)
    mark = _draw_network_logo(spec, size=420)
    # Position: left-center
    x = 90
    y = (spec.height - mark.height) // 2
    base.alpha_composite(mark, (x, y))

    # Text
    title_font, subtitle_font = _load_fonts()
    draw = ImageDraw.Draw(base)

    text_x = x + mark.width + 60
    text_y = int(spec.height * 0.33)

    draw.text((text_x, text_y), name, fill=spec.ink, font=title_font)
    draw.text((text_x, text_y + 80), subtitle, fill=spec.muted, font=subtitle_font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out_path, format="JPEG", quality=92, optimize=True, progressive=True)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    out_path = repo_root / "images" / "share.jpg"
    make_share_image(out_path=out_path)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

