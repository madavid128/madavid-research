#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Michael A. David
"""
Generate .webp variants alongside existing images.

Usage:
  python tools/make_webp.py images

Notes:
  - Requires Pillow built with WebP support.
  - Writes sibling files: `foo.jpg` -> `foo.webp`.
  - Skips files that already have a .webp neighbor.

"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def iter_images(root: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png"}
    out: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in exts:
            out.append(path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate .webp variants for images.")
    parser.add_argument(
        "root",
        nargs="?",
        default="images",
        help="Root folder to scan (default: images)",
    )
    parser.add_argument("--quality", type=int, default=82, help="WebP quality (default: 82)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Input folder not found: {root}")

    try:
        from PIL import Image  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Pillow is required. Install it with:\n  python -m pip install Pillow"
        ) from exc

    images = iter_images(root)
    if not images:
        print(f"No images found under {root}")
        return 0

    written = 0
    skipped = 0
    errors = 0

    for src in images:
        dst = src.with_suffix(".webp")
        if dst.exists():
            skipped += 1
            continue

        try:
            with Image.open(src) as im:
                im = im.convert("RGBA") if im.mode in ("P", "LA") else im
                im.save(
                    dst,
                    format="WEBP",
                    quality=int(args.quality),
                    method=6,
                )
            written += 1
        except Exception as exc:
            errors += 1
            print(f"Failed: {src} ({exc})")

    print(
        f"Done. Wrote {written} webp files (skipped {skipped}, errors {errors}) under {root}"
    )
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
