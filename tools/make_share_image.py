# SPDX-License-Identifier: MIT
"""
Generate an Open Graph / social share image for the site.

This script creates `images/share.jpg` (1200x630) with:
  - a dark background (matching the site theme)
  - a subtle “network” accent pattern
  - your MAD mark (recommended: `web-app-manifest-512x512.png`)
  - name + subtitle text (optional)

Why this exists:
  Social previews (iMessage, Slack, Twitter/X, etc.) prefer a 1200x630 image.
  A plain background photo often looks empty in a small preview, so this
  provides a clean, readable card that matches the site’s theme.

Usage:
  python tools/make_share_image.py

Recommended:
  python tools/make_share_image.py --icon web-app-manifest-512x512.png
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


@dataclass(frozen=True)
class ShareSpec:
    width: int = 1200
    height: int = 630
    background_top: Tuple[int, int, int] = (7, 14, 20)
    background_bottom: Tuple[int, int, int] = (10, 22, 30)
    accent: Tuple[int, int, int] = (0, 168, 120)  # ~site primary
    ink: Tuple[int, int, int] = (240, 240, 240)
    muted: Tuple[int, int, int] = (180, 180, 180)
    seed: int = 2025


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
    # Stop once the rectangle would invert.
    max_inset = max(0, (min(w, h) // 2) - 1)
    for i in range(0, max_inset + 1, 6):
        t = i / max(w, h)
        alpha = int(255 * strength * t)
        x0, y0 = 0 + i, 0 + i
        x1, y1 = (w - 1) - i, (h - 1) - i
        if x1 < x0 or y1 < y0:
            break
        draw.rectangle([x0, y0, x1, y1], outline=alpha)
    overlay = overlay.filter(ImageFilter.GaussianBlur(18))
    out = img.copy()
    out.putalpha(255)
    out = Image.composite(out, Image.new("RGBA", (w, h), (0, 0, 0, 255)), overlay)
    return out.convert("RGBA")


def _round_corners(img: Image.Image, radius: int) -> Image.Image:
    if radius <= 0:
        return img
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    out = img.copy()
    out.putalpha(mask)
    return out


def _alpha_shadow(
    alpha: Image.Image,
    blur: int,
    color: Tuple[int, int, int, int],
) -> Image.Image:
    """Create a blurred shadow image from an alpha mask."""
    shadow = Image.new("RGBA", alpha.size, (0, 0, 0, 0))
    shadow.paste(color, (0, 0), alpha)
    return shadow.filter(ImageFilter.GaussianBlur(blur))


def _paste_with_shadow(
    base: Image.Image,
    fg: Image.Image,
    xy: Tuple[int, int],
    *,
    shadow_offset: Tuple[int, int] = (0, 10),
    shadow_blur: int = 18,
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 160),
) -> None:
    """Paste an RGBA image onto base with a soft drop shadow."""
    alpha = fg.split()[-1]
    shadow = _alpha_shadow(alpha, blur=shadow_blur, color=shadow_color)
    base.alpha_composite(shadow, (xy[0] + shadow_offset[0], xy[1] + shadow_offset[1]))
    base.alpha_composite(fg, xy)


def _draw_network_accent(spec: ShareSpec) -> Image.Image:
    """
    Create a subtle network/graph accent layer (RGBA) for the background.

    This avoids depending on the icon background, and keeps the share card
    readable at small sizes.
    """
    rng = random.Random(spec.seed)
    layer = Image.new("RGBA", (spec.width, spec.height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Concentrate points toward the left (near the mark), taper to the right.
    points: list[tuple[float, float]] = []
    for _ in range(36):
        x = rng.random() ** 1.8  # bias toward 0
        y = rng.random()
        px = int(spec.width * (0.06 + 0.72 * x))
        py = int(spec.height * (0.18 + 0.64 * y))
        points.append((px, py))

    # Connect each point to a few nearest neighbors.
    for i, (x0, y0) in enumerate(points):
        dists = sorted(
            ((j, (x0 - x1) ** 2 + (y0 - y1) ** 2) for j, (x1, y1) in enumerate(points) if j != i),
            key=lambda t: t[1],
        )[:3]
        for j, _ in dists:
            x1, y1 = points[j]
            draw.line((x0, y0, x1, y1), fill=(*spec.accent, 26), width=2)

    for (x, y) in points:
        r = rng.randint(4, 7)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*spec.accent, 36))

    # Soft blur so it reads as texture, not foreground.
    return layer.filter(ImageFilter.GaussianBlur(1.4))


def _icon_letters_only(icon: Image.Image) -> Image.Image:
    """
    Attempt to isolate the bright (near-white) parts of the icon as a “mark”.

    This gives a transparent look even if the input icon has a solid background.
    """
    rgb = icon.convert("RGB")
    lum = ImageOps.grayscale(rgb)

    # Keep only bright pixels (letters), drop everything else.
    mask = lum.point(lambda p: 255 if p >= 220 else 0, mode="L")

    bbox = mask.getbbox()
    if bbox:
        # Pad the tight bounding box so the mark doesn’t touch edges.
        x0, y0, x1, y1 = bbox
        pad = int(round(max(icon.size) * 0.06))
        x0 = max(0, x0 - pad)
        y0 = max(0, y0 - pad)
        x1 = min(icon.size[0], x1 + pad)
        y1 = min(icon.size[1], y1 + pad)
        icon = icon.crop((x0, y0, x1, y1))
        mask = mask.crop((x0, y0, x1, y1))

    # Slightly soften edges without blurring the mark.
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))

    out = icon.copy()
    out.putalpha(mask)

    # Boost contrast a touch for crispness.
    return ImageEnhance.Contrast(out).enhance(1.08)


def _load_icon(icon_path: Path, size: int, *, mode: str) -> Image.Image:
    if mode == "full":
        icon = Image.open(icon_path).convert("RGBA").resize((size, size), Image.LANCZOS)
        icon = _round_corners(icon, radius=max(18, size // 12))
        return icon
    if mode == "letters":
        icon = Image.open(icon_path).convert("RGBA")
        mark = _icon_letters_only(icon)
        # Fit the mark into a square canvas (keeps it centered and consistent).
        mark = ImageOps.contain(mark, (size, size), Image.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.alpha_composite(mark, ((size - mark.size[0]) // 2, (size - mark.size[1]) // 2))
        return canvas
    raise ValueError(f"Unknown icon mode: {mode!r}. Expected 'full' or 'letters'.")


def _text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int, int, int]:
    try:
        return draw.textbbox((0, 0), text, font=font)
    except Exception:
        w, h = draw.textsize(text, font=font)  # deprecated but OK as fallback
        return (0, 0, w, h)


def make_share_image(
    out_path: Path,
    icon_path: Optional[Path] = None,
    name: str = "Michael A. David, PhD",
    subtitle: str = "Translational Orthopedics • Machine Learning • Multimodal Imaging • Scientific Art",
    icon_mode: str = "letters",
) -> None:
    spec = ShareSpec()
    base = _vertical_gradient(spec)
    base = _add_vignette(base, strength=0.55)
    base.alpha_composite(_draw_network_accent(spec))

    # Icon mark
    icon_size = 320
    if icon_path and icon_path.exists():
        mark = _load_icon(icon_path, icon_size, mode=icon_mode)
    else:
        raise FileNotFoundError(
            "Icon file not found. Provide --icon web-app-manifest-512x512.png (or another PNG)."
        )
    x = 96
    y = (spec.height - icon_size) // 2
    _paste_with_shadow(base, mark, (x, y), shadow_offset=(0, 16), shadow_blur=22)

    # Text
    title_font, subtitle_font = _load_fonts()
    draw = ImageDraw.Draw(base)

    text_x = x + icon_size + 70
    title_box = _text_bbox(draw, name, title_font)
    subtitle_box = _text_bbox(draw, subtitle, subtitle_font)
    text_h = (title_box[3] - title_box[1]) + 18 + (subtitle_box[3] - subtitle_box[1])
    text_y = (spec.height - text_h) // 2

    draw.text((text_x, text_y), name, fill=spec.ink, font=title_font)
    draw.text((text_x, text_y + (title_box[3] - title_box[1]) + 18), subtitle, fill=spec.muted, font=subtitle_font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out_path, format="JPEG", quality=92, optimize=True, progressive=True)


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a social share card (OpenGraph/Twitter preview).")
    p.add_argument(
        "--icon",
        default="web-app-manifest-512x512.png",
        help="Path to a square PNG icon (default: web-app-manifest-512x512.png).",
    )
    p.add_argument("--out", default="images/share.jpg", help="Output path (default: images/share.jpg).")
    p.add_argument("--name", default="Michael A. David, PhD", help="Title line.")
    p.add_argument(
        "--subtitle",
        default="Translational Orthopedics • Machine Learning • Multimodal Imaging • Scientific Art",
        help="Subtitle line.",
    )
    p.add_argument(
        "--icon-mode",
        choices=("letters", "full"),
        default="letters",
        help="Use 'letters' (transparent mark) or 'full' (rounded-square icon).",
    )
    return p.parse_args(argv)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    args = _parse_args()
    out_path = (repo_root / args.out).resolve()
    icon_path = (repo_root / args.icon).resolve()
    make_share_image(
        out_path=out_path,
        icon_path=icon_path,
        name=args.name,
        subtitle=args.subtitle,
        icon_mode=args.icon_mode,
    )
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
