#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Michael A. David
"""
CSV workflow for gallery `subtitle` + `alt` text.

Why:
- Writing subtitles directly in YAML is error-prone at scale.
- A spreadsheet/CSV makes it easy to batch-edit, sort, and share drafts.

What it does:
1) `export`: write a CSV template containing every gallery item (pictures/art),
   including existing subtitles/alts (if present). If missing, we generate a
   simple starter subtitle you can edit.
2) `merge`: read the CSV and merge `subtitle`/`alt` back into the YAML file
   (without overwriting existing values unless `--overwrite` is passed).

Notes:
- YAML `image:` paths should remain `images/...`. The site renders from
  `images/wm/...` automatically when watermarking is enabled.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

import yaml


YEAR_FROM_FILENAME = re.compile(r"-(19[0-9]{2}|20[0-9]{2})(?=\.[^.]+$)")


def _load_yaml_list(path: Path) -> list[dict[str, Any]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise SystemExit(f"Expected a YAML list in {path}")
    out: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            out.append(item)
    return out


def _dump_yaml_list(path: Path, items: list[dict[str, Any]]) -> None:
    path.write_text(
        yaml.safe_dump(items, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _parse_year(image_path: str) -> str:
    filename = Path(image_path).name
    m = YEAR_FROM_FILENAME.search(filename)
    return m.group(1) if m else ""


def _tags_to_str(tags: Any) -> str:
    if not tags:
        return ""
    if isinstance(tags, list):
        return ";".join(str(t).strip() for t in tags if str(t).strip())
    return str(tags).strip()


def _make_suggested_subtitle(title: str, year: str, tags_str: str) -> str:
    """
    Generate a minimal placeholder subtitle.

    Keep it generic; the CSV is where you'll write the real story.
    """
    base = title.strip() or "Image"
    if year:
        base = f"{base} ({year})"
    if tags_str:
        first_tag = tags_str.split(";")[0].strip()
        if first_tag and first_tag.lower() not in base.lower():
            return f"{base} — {first_tag}."
    return f"{base}."


def export_csv(*, data_path: Path, out_path: Path, only_missing: bool) -> int:
    items = _load_yaml_list(data_path)
    rows: list[dict[str, str]] = []

    for item in items:
        image = str(item.get("image", "")).strip()
        if not image or not image.startswith("images/"):
            continue

        title = str(item.get("title", "")).strip()
        year = str(item.get("year", "")).strip() or _parse_year(image)
        subtitle = str(item.get("subtitle", "")).strip()
        alt = str(item.get("alt", "")).strip()
        tags_str = _tags_to_str(item.get("tags"))

        if only_missing and (subtitle or alt):
            continue

        if not subtitle:
            subtitle = _make_suggested_subtitle(title or Path(image).stem, year, tags_str)

        rows.append(
            {
                "image": image,
                "filename": Path(image).name,
                "title": title,
                "year": year,
                "subtitle": subtitle,
                "alt": alt,
                "tags": tags_str,
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["image", "filename", "title", "year", "subtitle", "alt", "tags"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out_path} ({len(rows)} rows).")
    return 0


def _reorder_item_keys(item: dict[str, Any]) -> dict[str, Any]:
    """
    Keep YAML readable by placing `subtitle`/`alt` right after `title`.
    """
    preferred = ["date", "title", "subtitle", "alt", "image", "tags", "style"]
    out: dict[str, Any] = {}
    for key in preferred:
        if key in item and item[key] not in (None, ""):
            out[key] = item[key]
    for key, value in item.items():
        if key in out:
            continue
        out[key] = value
    return out


def merge_csv(*, data_path: Path, csv_path: Path, overwrite: bool, dry_run: bool) -> int:
    items = _load_yaml_list(data_path)

    mapping: dict[str, dict[str, str]] = {}
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            image = (row.get("image") or "").strip()
            filename = (row.get("filename") or "").strip()
            key = image or filename
            if not key:
                continue
            mapping[key] = {k: (v or "").strip() for k, v in row.items()}

    updated = 0
    skipped = 0

    for item in items:
        image = str(item.get("image", "")).strip()
        if not image or not image.startswith("images/"):
            continue

        key_exact = image
        key_name = Path(image).name
        row = mapping.get(key_exact) or mapping.get(key_name)
        if not row:
            continue

        changed = False

        sub = row.get("subtitle", "").strip()
        if sub:
            current = str(item.get("subtitle", "") or "").strip()
            if overwrite or not current:
                item["subtitle"] = sub
                changed = True

        alt = row.get("alt", "").strip()
        if alt:
            current = str(item.get("alt", "") or "").strip()
            if overwrite or not current:
                item["alt"] = alt
                changed = True

        if changed:
            updated += 1
        else:
            skipped += 1

    items = [_reorder_item_keys(i) for i in items]

    print(f"Merge summary: updated={updated} skipped={skipped} total={len(items)}")
    if dry_run:
        print("Dry run: no files written.")
        return 0

    _dump_yaml_list(data_path, items)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export/merge gallery subtitles via CSV.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_export = sub.add_parser("export", help="Export a CSV template from a gallery YAML file.")
    p_export.add_argument("--data", required=True, help="Gallery YAML file (e.g., _data/pictures.yaml).")
    p_export.add_argument("--out", required=True, help="CSV output path.")
    p_export.add_argument(
        "--only-missing",
        action="store_true",
        help="Only export rows where subtitle/alt are missing.",
    )

    p_merge = sub.add_parser("merge", help="Merge subtitle/alt from a CSV back into a gallery YAML file.")
    p_merge.add_argument("--data", required=True, help="Gallery YAML file to update.")
    p_merge.add_argument("--csv", required=True, help="CSV input path.")
    p_merge.add_argument("--overwrite", action="store_true", help="Overwrite existing subtitle/alt values.")
    p_merge.add_argument("--dry-run", action="store_true", help="Show what would change without writing.")

    args = parser.parse_args(argv)
    data_path = Path(args.data)
    if not data_path.exists():
        raise SystemExit(f"Missing --data file: {data_path}")

    if args.cmd == "export":
        return export_csv(
            data_path=data_path,
            out_path=Path(args.out),
            only_missing=bool(args.only_missing),
        )
    if args.cmd == "merge":
        csv_path = Path(args.csv)
        if not csv_path.exists():
            raise SystemExit(f"Missing --csv file: {csv_path}")
        return merge_csv(
            data_path=data_path,
            csv_path=csv_path,
            overwrite=bool(args.overwrite),
            dry_run=bool(args.dry_run),
        )

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
