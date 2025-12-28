#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Michael A. David
"""
Generate large diagonal watermarks for gallery images.

This script reads `_data/pictures.yaml` and `_data/art.yaml`, finds the referenced
image files under `images/originals/`, and
writes copies under `images/wm/`.

By default, it applies watermarks only to files whose names start with
`nature`, `science`, `music`, or `sports` (configurable with
`--watermark-prefixes`).
All other images are copied into `images/wm/` without modification.

Why this exists:
  - Browsers make it trivial to right-click/save or screenshot.
  - You cannot fully prevent copying, but a prominent watermark discourages
    casual reuse and preserves attribution if images are shared.

"""

from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
import tempfile
import time
import io
from pathlib import Path
from shutil import copy2
from typing import Iterable, Iterator

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Install it with:\n  python -m pip install PyYAML"
    ) from exc

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install it with:\n  python -m pip install Pillow"
    ) from exc

try:
    from PIL import ImageCms  # type: ignore
except Exception:  # pragma: no cover
    ImageCms = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEXT = "© 2025 Michael A. David • michaeladavid.com"
DEFAULT_PREFIXES = ("nature", "science", "music", "sports")
SOURCE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
    ".heif",
    ".tif",
    ".tiff",
    ".webp",
    ".gif",
)


def _iter_gallery_images(data_file: Path) -> Iterator[str]:
    """
    Yield `image:` paths from a gallery YAML file.

    Expected schema: a list of dicts where each dict may include "image".
    """
    if not data_file.exists():
        return

    raw = yaml.safe_load(data_file.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        return

    for item in raw:
        if not isinstance(item, dict):
            continue
        image = item.get("image")
        if isinstance(image, str) and image.strip():
            yield image.strip()


def _should_watermark(name: str, prefixes: Iterable[str]) -> bool:
    name_lower = name.lower()
    for prefix in prefixes:
        prefix_clean = prefix.strip().lower()
        if prefix_clean and name_lower.startswith(prefix_clean):
            return True
    return False


def _find_font_path() -> Path | None:
    """
    Return a usable TTF font path if available on this system.

    We avoid bundling fonts in-repo. Instead we search common system locations.
    """
    candidates = [
        # Linux (GitHub Actions)
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        # macOS
        Path("/Library/Fonts/Arial Bold.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Helvetica.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _rotated_bbox(text_w: float, text_h: float, angle_deg: float) -> tuple[float, float]:
    """Approximate bounding box after rotation (no expansion)."""
    angle = math.radians(angle_deg)
    c = abs(math.cos(angle))
    s = abs(math.sin(angle))
    return (text_w * c + text_h * s, text_w * s + text_h * c)


def _fit_font_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    canvas_w: int,
    canvas_h: int,
    angle_deg: float,
    margin_frac: float,
) -> ImageFont.FreeTypeFont:
    """
    Choose the largest font size whose rotated bbox fits within the image.
    """
    max_w = int(canvas_w * (1 - 2 * margin_frac))
    max_h = int(canvas_h * (1 - 2 * margin_frac))
    # Start very large and binary search down.
    lo, hi = 10, max(canvas_w, canvas_h)

    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        font = ImageFont.truetype(str(font_path), mid)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        rot_w, rot_h = _rotated_bbox(text_w, text_h, angle_deg)
        if rot_w <= max_w and rot_h <= max_h:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1

    return ImageFont.truetype(str(font_path), best)


def _watermark_image(
    img: Image.Image,
    *,
    text: str,
    angle_deg: float,
    opacity: float,
    margin_frac: float,
    stroke_frac: float,
) -> Image.Image:
    """
    Return a copy of img with a centered diagonal watermark overlay.

    - `opacity` is 0..1 for the main text fill.
    - `stroke_frac` is relative stroke width (scaled by font size).
    """
    base = img.convert("RGBA")
    w, h = base.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_path = _find_font_path()
    if font_path is None:
        # Fall back to PIL's default font (less pretty, but always available).
        # The default font doesn't scale well; we still draw it prominently.
        font = ImageFont.load_default()
        # Approximate a "big" render by drawing text multiple times offset.
        # This is only used if no system TTF is available.
        font_size = 0
    else:
        font = _fit_font_size(draw, text, font_path, w, h, angle_deg, margin_frac)
        font_size = getattr(font, "size", 0) or 0

    alpha = max(0, min(255, int(255 * opacity)))
    fill = (255, 255, 255, alpha)

    # Stroke improves readability across mixed backgrounds.
    stroke_w = max(1, int(font_size * stroke_frac)) if font_size else 2
    stroke_fill = (0, 0, 0, max(0, min(255, int(alpha * 0.55))))

    # Centered unrotated draw, then rotate whole overlay.
    # Use textbbox to compute exact size for precise centering.
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (w - text_w) / 2
    y = (h - text_h) / 2

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_w,
        stroke_fill=stroke_fill,
    )

    rotated = overlay.rotate(angle_deg, resample=Image.Resampling.BICUBIC, expand=False)
    out = Image.alpha_composite(base, rotated)
    return out.convert(img.mode) if img.mode in ("RGB", "RGBA") else out.convert("RGB")


def _to_repo_rel(path_str: str) -> str:
    """Normalize a path string from YAML to a repo-relative path."""
    # YAML entries typically look like "images/foo.jpg" (no leading slash).
    # We also tolerate "/images/foo.jpg".
    return path_str.lstrip("/")


def _should_skip(src: Path, dst: Path, force: bool) -> bool:
    if force:
        return False
    if not dst.exists():
        return False
    try:
        return dst.stat().st_mtime >= src.stat().st_mtime
    except OSError:
        return False


def _write_image(
    out: Image.Image,
    dst: Path,
    *,
    icc_profile: bytes | None = None,
    webp_quality: int = 82,
    webp_method: int = 4,
) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    suffix = dst.suffix.lower()

    # Some browsers handle wide-gamut ICC profiles inconsistently for WebP/PNG.
    # Best-effort: convert to sRGB at write time so images look consistent.
    if icc_profile and ImageCms is not None:
        try:
            src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_profile))
            dst_profile_raw = ImageCms.createProfile("sRGB")
            dst_profile = ImageCms.ImageCmsProfile(dst_profile_raw)
            srgb_bytes = dst_profile.tobytes()

            if out.mode in ("RGBA", "LA"):
                alpha = out.getchannel("A")
                rgb = out.convert("RGB")
                converted = ImageCms.profileToProfile(rgb, src_profile, dst_profile, outputMode="RGB")
                converted.putalpha(alpha)
                out = converted
            else:
                rgb = out.convert("RGB") if out.mode != "RGB" else out
                out = ImageCms.profileToProfile(rgb, src_profile, dst_profile, outputMode="RGB")

            icc_profile = srgb_bytes
        except Exception:
            # If conversion fails, fall back to embedding the original profile.
            pass

    if suffix in (".jpg", ".jpeg"):
        out.convert("RGB").save(
            dst,
            format="JPEG",
            quality=92,
            optimize=True,
            progressive=True,
            icc_profile=icc_profile,
        )
    elif suffix == ".png":
        out.save(dst, format="PNG", optimize=True, icc_profile=icc_profile)
    elif suffix == ".webp":
        # WebP `method` trades CPU time for compression:
        #   0 = fastest, 6 = slowest/best.
        # For local iteration we default to a balanced value.
        out.convert("RGB").save(
            dst,
            format="WEBP",
            quality=int(webp_quality),
            method=int(webp_method),
            icc_profile=icc_profile,
        )
    else:
        out.save(dst, icc_profile=icc_profile)


def _resolve_destination(src: Path, out_dir: Path) -> Path:
    """
    Choose the output path for a source image.

    TIFF sources are converted to PNG for web compatibility.
    """
    if src.suffix.lower() in {".tif", ".tiff"}:
        return out_dir / f"{src.stem}.png"
    if src.suffix.lower() in {".heic", ".heif"}:
        return out_dir / f"{src.stem}.jpg"
    return out_dir / src.name


def _resize_long_edge(img: Image.Image, *, max_edge: int) -> Image.Image:
    """
    Resize an image so its longest edge is <= `max_edge` (keeps aspect ratio).

    If the image is already small enough, returns it unchanged.
    """
    if max_edge <= 0:
        return img
    w, h = img.size
    long_edge = max(w, h)
    if long_edge <= max_edge:
        return img
    scale = max_edge / float(long_edge)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    return img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)


def _find_original_image(*, preferred_name: str, originals_dir: Path) -> Path | None:
    """
    Return the most likely original image path for a gallery entry.

    Primary mode: the original is present under `images/originals/` with the same
    filename as referenced in YAML (recommended workflow).

    Convenience fallback: if that exact filename does not exist, try matching by
    stem across common extensions. This supports workflows where YAML points to
    `images/foo.png` but the original is stored as `images/originals/foo.tiff`.

    Year-suffix helper:
      - If your originals are renamed to include `-YYYY` (example: `foo-2021.jpg`)
        but YAML still references `foo.jpg`, we attempt to find any
        `foo-????.*` match.
      - If YAML references `foo-2021.jpg` but your original is `foo.jpg`, we
        also attempt the reverse (strip the year suffix).
    """
    preferred = originals_dir / preferred_name
    if preferred.exists():
        return preferred

    stem = Path(preferred_name).stem
    for ext in SOURCE_EXTENSIONS:
        candidate = originals_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate

    # If YAML omits the year but originals include `-YYYY`, try globbing.
    for ext in SOURCE_EXTENSIONS:
        for candidate in originals_dir.glob(f"{stem}-????{ext}"):
            if candidate.exists():
                return candidate

    # If YAML includes the year but originals don't, strip `-YYYY` and try again.
    m = re.match(r"^(?P<base>.+)-(?P<year>19[0-9]{2}|20[0-9]{2})$", stem)
    if m:
        base = m.group("base")
        for ext in SOURCE_EXTENSIONS:
            candidate = originals_dir / f"{base}{ext}"
            if candidate.exists():
                return candidate

    return None


def _ensure_heic_support() -> None:
    """
    Register HEIC/HEIF support if the optional dependency is installed.

    Pillow can decode HEIC/HEIF only if a decoder plugin is available.
    If you have HEIC originals and see failures, install:
      python -m pip install pillow-heif
    """
    try:
        from pillow_heif import register_heif_opener  # type: ignore

        register_heif_opener()
    except Exception:
        # Optional; only required when processing HEIC/HEIF originals.
        return


def _convert_heic_with_sips(src: Path) -> Path | None:
    """
    Convert a HEIC/HEIF image to JPEG using macOS `sips`.

    This provides a no-network fallback for local development on macOS when
    `pillow-heif` is not installed.
    """
    if sys.platform != "darwin":
        return None

    if src.suffix.lower() not in {".heic", ".heif"}:
        return None

    if not Path("/usr/bin/sips").exists():
        return None

    try:
        tmp_dir = Path(tempfile.mkdtemp(prefix="mad-heic-"))
        out = tmp_dir / f"{src.stem}.jpg"
        subprocess.run(
            ["/usr/bin/sips", "-s", "format", "jpeg", str(src), "--out", str(out)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return out if out.exists() else None
    except Exception:
        return None


def _open_image(src: Path) -> tuple[Image.Image, bytes | None]:
    """
    Open an image with EXIF transpose and return (image, icc_profile).

    For HEIC/HEIF sources, this tries (in order):
      1) pillow-heif (if installed via _ensure_heic_support())
      2) macOS `sips` conversion to a temp JPEG (local dev convenience)
    """
    try:
        img = Image.open(src)
        icc_profile = img.info.get("icc_profile")
        img = ImageOps.exif_transpose(img)
        return img, icc_profile
    except Exception:
        if src.suffix.lower() in {".heic", ".heif"}:
            tmp_jpg = _convert_heic_with_sips(src)
            if tmp_jpg is not None:
                img = Image.open(tmp_jpg)
                icc_profile = img.info.get("icc_profile")
                img = ImageOps.exif_transpose(img)
                return img, icc_profile
            raise SystemExit(
                "Cannot read HEIC/HEIF originals.\n"
                "Install the optional decoder:\n"
                "  python -m pip install pillow-heif\n"
                "Or convert the file to JPG/PNG before running this script."
            )
        raise


def generate(
    *,
    data_files: Iterable[Path],
    out_dir: Path,
    text: str,
    watermark_prefixes: Iterable[str],
    angle_deg: float,
    opacity: float,
    margin_frac: float,
    stroke_frac: float,
    force: bool,
    make_webp: bool,
    webp_quality: int,
    webp_method: int,
    clean: bool,
    max_edge: int,
    thumb_edge: int,
    make_thumbs: bool,
) -> int:
    # Ensure HEIC/HEIF support is registered even if this function is called
    # directly (main() also calls this).
    _ensure_heic_support()

    images = sorted({p for f in data_files for p in _iter_gallery_images(f)})
    if not images:
        print("No gallery images found.")
        return 0

    thumb_dir = out_dir / "thumb"
    written = 0
    skipped = 0
    missing = 0
    failed = 0

    expected_outputs: set[Path] = set()

    for image_path in images:
        rel = _to_repo_rel(image_path)
        rel_path = Path(rel)
        # Read from images/originals/* but write to images/wm/.
        if rel_path.parts[:1] == ("images",):
            originals_dir = REPO_ROOT / "images" / "originals"
            src = _find_original_image(
                preferred_name=rel_path.name,
                originals_dir=originals_dir,
            )
        else:
            src = REPO_ROOT / rel
        if src is None or not src.exists():
            # If the original is missing but a previously generated output exists,
            # keep the build moving (useful when you only keep originals for
            # watermarked categories).
            if rel.startswith("images/") and not force:
                expected = out_dir / rel_path.name
                if expected.exists():
                    skipped += 1
                    continue

            missing += 1
            print(f"Missing: {rel}")
            continue

        if not rel.startswith("images/"):
            # Only watermark images under images/ to avoid surprises.
            skipped += 1
            continue

        dst = _resolve_destination(src, out_dir)
        expected_outputs.add(dst)
        if _should_skip(src, dst, force):
            skipped += 1
            continue

        try:
            apply_mark = _should_watermark(dst.name, watermark_prefixes)
            img, icc_profile = _open_image(src)
            img = _resize_long_edge(img, max_edge=max_edge)
            if apply_mark:
                img = _watermark_image(
                    img,
                    text=text,
                    angle_deg=angle_deg,
                    opacity=opacity,
                    margin_frac=margin_frac,
                    stroke_frac=stroke_frac,
                )

            _write_image(
                img,
                dst,
                icc_profile=icc_profile,
                webp_quality=webp_quality,
                webp_method=webp_method,
            )

            written += 1

            if make_webp and dst.suffix.lower() in (".jpg", ".jpeg", ".png"):
                webp_dst = dst.with_suffix(".webp")
                expected_outputs.add(webp_dst)
                # Only overwrite if needed.
                if not _should_skip(src, webp_dst, force):
                    try:
                        _write_image(
                            img,
                            webp_dst,
                            icc_profile=icc_profile,
                            webp_quality=webp_quality,
                            webp_method=webp_method,
                        )
                    except Exception:
                        # WebP support depends on Pillow build; ignore quietly.
                        pass

            if make_thumbs:
                thumb_dir.mkdir(parents=True, exist_ok=True)
                thumb_dst = thumb_dir / dst.name
                expected_outputs.add(thumb_dst)
                thumb_img = _resize_long_edge(img, max_edge=thumb_edge)
                _write_image(
                    thumb_img,
                    thumb_dst,
                    icc_profile=icc_profile,
                    webp_quality=webp_quality,
                    webp_method=webp_method,
                )

                if make_webp and thumb_dst.suffix.lower() in (".jpg", ".jpeg", ".png"):
                    thumb_webp = thumb_dst.with_suffix(".webp")
                    expected_outputs.add(thumb_webp)
                    try:
                        _write_image(
                            thumb_img,
                            thumb_webp,
                            icc_profile=icc_profile,
                            webp_quality=webp_quality,
                            webp_method=webp_method,
                        )
                    except Exception:
                        pass
        except Exception as exc:
            failed += 1
            print(f"Failed: {rel} ({exc})")

    print(
        f"Watermark generation complete: wrote={written} skipped={skipped} missing={missing} failed={failed}"
    )
    if clean:
        removed = 0
        for p in sorted(out_dir.rglob("*")):
            if not p.is_file():
                continue
            # Only touch likely image outputs.
            if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                continue
            if p not in expected_outputs:
                try:
                    p.unlink()
                    removed += 1
                except OSError:
                    pass
        if removed:
            print(f"Cleaned {removed} orphan files from {out_dir}")
    _write_build_marker(
        out_dir=out_dir,
        text=text,
        angle_deg=angle_deg,
        opacity=opacity,
        prefixes=list(watermark_prefixes),
    )
    return 0 if failed == 0 else 1


def _write_build_marker(
    *,
    out_dir: Path,
    text: str,
    angle_deg: float,
    opacity: float,
    prefixes: list[str],
) -> None:
    """
    Write a small data file to help bust browser caches in local development.

    Jekyll does not always notice binary/static file changes on mounted volumes.
    By writing a `_data/*.yaml` file at the end of this script, we ensure Jekyll
    sees a change, rebuilds the site, and updates the query-string cache-bust
    values in rendered HTML.
    """
    marker = REPO_ROOT / "_data" / "watermark_build.yaml"
    payload = {
        "nonce": int(time.time()),
        "out_dir": str(out_dir.relative_to(REPO_ROOT)) if out_dir.is_absolute() else str(out_dir),
        "text": text,
        "angle": angle_deg,
        "opacity": opacity,
        "prefixes": prefixes,
    }
    marker.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate diagonal watermarked copies for pictures/art galleries."
    )
    parser.add_argument(
        "--text",
        default=DEFAULT_TEXT,
        help=f"Watermark text (default: {DEFAULT_TEXT!r})",
    )
    parser.add_argument(
        "--angle",
        type=float,
        default=-22.0,
        help="Rotation angle in degrees (default: -22)",
    )
    parser.add_argument(
        "--opacity",
        type=float,
        default=0.20,
        help="Text opacity 0..1 (default: 0.20)",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0.06,
        help="Margin as fraction of image size (default: 0.06)",
    )
    parser.add_argument(
        "--stroke-frac",
        type=float,
        default=0.03,
        help="Stroke width as fraction of font size (default: 0.03)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing outputs even if up-to-date.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete orphan files in the output directory that are no longer referenced by the gallery YAML.",
    )
    parser.add_argument(
        "--no-webp",
        action="store_true",
        help="Do not generate WebP copies in images/wm/.",
    )
    parser.add_argument(
        "--webp-quality",
        type=int,
        default=82,
        help="WebP quality 0..100 (default: 82).",
    )
    parser.add_argument(
        "--webp-method",
        type=int,
        default=4,
        help="WebP method 0..6 (0 fastest, 6 slowest; default: 4).",
    )
    parser.add_argument(
        "--max-edge",
        type=int,
        default=2400,
        help="Resize outputs so the longest edge is at most this many pixels (default: 2400).",
    )
    parser.add_argument(
        "--thumb-edge",
        type=int,
        default=640,
        help="Thumbnail longest-edge size in pixels (default: 640).",
    )
    parser.add_argument(
        "--no-thumbs",
        action="store_true",
        help="Do not generate thumbnails under images/wm/thumb/.",
    )
    parser.add_argument(
        "--out-dir",
        default="images/wm",
        help="Output directory for watermarked images (default: images/wm).",
    )
    parser.add_argument(
        "--watermark-prefixes",
        default=",".join(DEFAULT_PREFIXES),
        help="Comma-separated filename prefixes to watermark (default: nature,science,music,sports).",
    )
    parser.add_argument(
        "--data",
        action="append",
        default=["_data/pictures.yaml", "_data/art.yaml"],
        help="Gallery YAML file to process (repeatable).",
    )
    args = parser.parse_args(argv)

    _ensure_heic_support()

    out_dir = REPO_ROOT / args.out_dir
    data_files = [REPO_ROOT / p for p in args.data]

    watermark_prefixes = [p.strip() for p in args.watermark_prefixes.split(",")]

    return generate(
        data_files=data_files,
        out_dir=out_dir,
        text=args.text,
        watermark_prefixes=watermark_prefixes,
        angle_deg=args.angle,
        opacity=args.opacity,
        margin_frac=args.margin,
        stroke_frac=args.stroke_frac,
        force=args.force,
        make_webp=(not args.no_webp),
        webp_quality=args.webp_quality,
        webp_method=args.webp_method,
        clean=args.clean,
        max_edge=args.max_edge,
        thumb_edge=args.thumb_edge,
        make_thumbs=(not args.no_thumbs),
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
