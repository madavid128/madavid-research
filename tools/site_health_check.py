#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Michael A. David
"""
Lightweight site health checks (fast, offline, no Jekyll build required).

Why:
- Catch common “broken site” issues before pushing (missing images, bad CSV, etc.).
- Provide a single command you can run locally or in CI.

Checks:
- `tools/gallery_master.csv` parses + validates (via `tools/gallery_from_csv.py` logic).
- `_data/pictures.yaml` / `_data/art.yaml` are valid YAML lists.
- Gallery images referenced by YAML exist under `images/wm/` (preferred) or `images/`.
- `_data/home_feature_images.yaml` / `_data/project_area_images.yaml` (if present) point to existing images.
- `images/share.jpg` exists (social sharing preview).

Usage:
  python tools/site_health_check.py
  python tools/site_health_check.py --strict
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path):
    if not path.exists():
        raise FileNotFoundError(str(path))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _as_list(data, *, path: Path) -> list[dict]:
    if data is None:
        return []
    if not isinstance(data, list):
        raise TypeError(f"Expected YAML list in {path}")
    out: list[dict] = []
    for item in data:
        if isinstance(item, dict):
            out.append(item)
    return out


def _check_gallery_csv(errors: list[str]) -> None:
    try:
        # Import inside function so the script can still run in minimal environments.
        sys.path.insert(0, str(REPO_ROOT))
        from tools.gallery_from_csv import _read_csv_rows, validate_rows  # type: ignore

        rows = _read_csv_rows(REPO_ROOT / "tools" / "gallery_master.csv")
        errs, _warnings = validate_rows(rows)
        for e in errs:
            errors.append(f"gallery_master.csv: {e}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"gallery_master.csv failed to validate: {exc}")


def _exists_any(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def _check_gallery_yaml_images(*, yaml_path: Path, errors: list[str], warnings: list[str]) -> None:
    items = _as_list(_load_yaml(yaml_path), path=yaml_path)
    for item in items:
        image = str(item.get("image", "")).strip()
        if not image or not image.startswith("images/"):
            continue
        name = Path(image).name
        # Prefer checking the published files under images/wm/.
        candidates = [
            REPO_ROOT / "images" / "wm" / name,
            REPO_ROOT / "images" / name,
        ]
        found = _exists_any(candidates)
        if not found:
            errors.append(f"{yaml_path.name}: missing image {image} (expected in images/wm/ or images/)")


def _check_mapping_yaml(*, path: Path, errors: list[str]) -> None:
    if not path.exists():
        return
    data = _load_yaml(path) or {}
    if not isinstance(data, dict):
        errors.append(f"{path.name}: expected YAML dict mapping slot->image")
        return
    for key, value in data.items():
        img = str(value or "").strip()
        if not img.startswith("images/"):
            errors.append(f"{path.name}: {key}: expected images/... path, got {img!r}")
            continue
        name = Path(img).name
        candidates = [
            REPO_ROOT / "images" / "wm" / name,
            REPO_ROOT / "images" / name,
        ]
        if not _exists_any(candidates):
            errors.append(f"{path.name}: {key}: missing {img} (expected in images/wm/ or images/)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    warnings: list[str] = []

    _check_gallery_csv(errors)

    for path in [REPO_ROOT / "_data" / "pictures.yaml", REPO_ROOT / "_data" / "art.yaml"]:
        try:
            _check_gallery_yaml_images(yaml_path=path, errors=errors, warnings=warnings)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path.name}: failed to parse/check: {exc}")

    _check_mapping_yaml(path=REPO_ROOT / "_data" / "home_feature_images.yaml", errors=errors)
    _check_mapping_yaml(path=REPO_ROOT / "_data" / "project_area_images.yaml", errors=errors)

    share = REPO_ROOT / "images" / "share.jpg"
    if not share.exists():
        errors.append("Missing images/share.jpg (social preview image).")

    if warnings and args.strict:
        errors.extend([f"(warning) {w}" for w in warnings])
        warnings = []

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"- {w}")
        print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"- {e}")
        return 2

    print("OK: site health checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

