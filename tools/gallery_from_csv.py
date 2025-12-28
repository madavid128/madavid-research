#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Michael A. David
"""
CSV-first pipeline for gallery data.

This script makes a single CSV file the "source of truth" for gallery items, then
generates the YAML that the Jekyll site consumes:

- `_data/pictures.yaml`
- `_data/art.yaml`
 - `_data/home_feature_images.yaml` (optional: home page highlight images)
 - `_data/project_area_images.yaml` (optional: project area images)
 - `_data/header_backgrounds.yaml` (optional: rotating home header backgrounds)

Why CSV-first:
- Non-coders can update titles/tags/years/subtitles in a spreadsheet.
- The script validates rows and prevents common YAML mistakes.

CSV columns (recommended):
- `collection` : `pictures` or `art` (required)
- `image`      : filename or `images/<filename>` (required)
- `title`      : display title (required)
- `tags`       : tags separated by `;` (required, can be empty for `art` if desired)
- `date`       : `YYYY-MM-DD` (optional; default: today)
- `year`       : 4-digit year (optional; can also be derived from `-YYYY` filename suffix)
- `style`      : `square` or `banner` (optional; default: `square`)
- `subtitle`   : shown only in the lightbox when clicked (optional)
- `alt`        : accessibility alt text (optional)
- `home_slot`  : choose an image for the home page highlight (optional; one of:
                 `publications`, `projects`, `team`, `art`)
- `project_area`: choose an image for a project area card (optional; one of:
                  `cartilage`, `tendon`, `imaging-ml`, `other`)
- `project_area_rank`: priority when multiple images share a `project_area` (optional; lower wins)
- `project_page_section`: include this image on a specific project subpage (optional; one of:
                         `cartilage`, `tendon`, `imaging-ml`, `other`)
- `project_page_rank`: ordering for project subpage images when multiple rows share a `project_page_section`
                      (optional; lower wins)
- `header_background`: include this image in the rotating home header background (optional; true/false)
- `header_background_rank`: ordering for header background rotation (optional; 1..N)

Notes:
- Keep `image` values pointing at `images/...` (NOT `images/wm/...`).
  The site can be configured to serve published images from `images/wm/` while
  keeping originals private.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "tools" / "gallery_master.csv"
PICTURES_YAML = ROOT / "_data" / "pictures.yaml"
ART_YAML = ROOT / "_data" / "art.yaml"
HOME_FEATURES_YAML = ROOT / "_data" / "home_feature_images.yaml"
PROJECT_AREA_IMAGES_YAML = ROOT / "_data" / "project_area_images.yaml"
HEADER_BACKGROUNDS_YAML = ROOT / "_data" / "header_backgrounds.yaml"
PAGE_SHARE_IMAGES_YAML = ROOT / "_data" / "page_share_images.yaml"

KNOWN_IMAGE_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".svg",
    ".tif",
    ".tiff",
    ".heic",
    ".heif",
    ".JPG",
}


class FlowSeqDumper(yaml.SafeDumper):
    """YAML dumper that renders short lists (e.g., tags) in flow style."""


def _represent_short_list(dumper: yaml.Dumper, data: list[Any]) -> yaml.Node:  # type: ignore[name-defined]
    # Render short lists in `[a, b, c]` style for readability.
    flow = len(data) <= 16
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow)


FlowSeqDumper.add_representer(list, _represent_short_list)


_YEAR_SUFFIX_RE = re.compile(r"-(\d{4})(?=\.[A-Za-z0-9]+$)")


def _parse_year_from_filename(filename: str) -> int | None:
    match = _YEAR_SUFFIX_RE.search(filename)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _normalize_image(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return value
    if value.startswith("images/"):
        return value
    if "/" in value:
        # Accept absolute or other paths, but keep only the basename to reduce errors.
        value = Path(value).name
    return f"images/{value}"


def _infer_image_path(image_value: str) -> str:
    """
    Normalize `image` and (optionally) infer an extension if missing.

    Spreadsheet users sometimes omit the extension (e.g., `nature_42`).
    We try to resolve that by searching:
      1) `images/originals/`
      2) `images/wm/`
      3) `images/`

    If multiple matches exist, we raise an error and ask the user to specify the
    exact filename (including extension) in the CSV.
    """
    normalized = _normalize_image(image_value)
    if not normalized or normalized == "images/":
        return normalized

    filename = Path(normalized).name
    suffix = Path(filename).suffix
    # If the CSV includes a non-web-friendly extension, normalize it to what the
    # watermark pipeline will output (HEIC->JPG, TIFF->PNG).
    if suffix:
        suffix_lower = suffix.lower()
        if suffix_lower in {".heic", ".heif"}:
            return f"images/{Path(filename).stem}.jpg"
        if suffix_lower in {".tif", ".tiff"}:
            return f"images/{Path(filename).stem}.png"
        return normalized

    stem = Path(filename).stem
    search_dirs = [ROOT / "images" / "originals", ROOT / "images" / "wm", ROOT / "images"]

    candidates: list[Path] = []
    for dir_path in search_dirs:
        if not dir_path.exists():
            continue
        for ext in sorted(KNOWN_IMAGE_EXTS):
            p = dir_path / f"{stem}{ext}"
            if p.exists():
                candidates.append(p)

    if not candidates:
        raise ValueError(
            f"Image '{image_value}' has no extension and no matching file was found. "
            "Use the full filename with extension (e.g., nature_42.jpeg)."
        )

    # If multiple exist, prefer common web formats. If still ambiguous, error.
    preference = [".jpeg", ".jpg", ".png", ".webp", ".gif", ".tiff", ".tif", ".heic", ".heif", ".svg"]
    by_ext: dict[str, list[Path]] = {}
    for p in candidates:
        by_ext.setdefault(p.suffix.lower(), []).append(p)

    chosen: Path | None = None
    for ext in preference:
        if ext in by_ext:
            chosen = sorted(by_ext[ext])[0]
            break

    if chosen is None:
        chosen = sorted(candidates)[0]

    # If there are candidates in *different* extensions beyond the chosen, warn by raising
    # an informative error instead of guessing incorrectly.
    unique_exts = sorted({p.suffix.lower() for p in candidates})
    if len(unique_exts) > 1:
        examples = ", ".join(sorted(p.name for p in candidates)[:8])
        raise ValueError(
            f"Image '{image_value}' is ambiguous (multiple extensions exist: {unique_exts}). "
            f"Use the exact filename in the CSV. Found: {examples}"
        )

    # If the original is HEIC/HEIF or TIFF, normalize to the web output
    # extension that the watermark pipeline will write.
    chosen_suffix = chosen.suffix.lower()
    if chosen_suffix in {".heic", ".heif"}:
        return f"images/{chosen.stem}.jpg"
    if chosen_suffix in {".tif", ".tiff"}:
        return f"images/{chosen.stem}.png"
    return f"images/{chosen.name}"


def _split_tags(value: str) -> list[str]:
    value = (value or "").strip()
    if not value:
        return []
    if ";" in value:
        parts = value.split(";")
    else:
        # Allow comma-separated if user pasted from another system.
        parts = value.split(",")
    tags: list[str] = []
    for part in parts:
        tag = part.strip()
        if not tag:
            continue
        tags.append(tag)
    # De-dup while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for tag in tags:
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(tag)
    return out


def _fix_common_mojibake(text: str) -> str:
    """
    Fix common mojibake sequences produced by spreadsheet exports.

    Example: an em dash (—) can end up as:
    - "â€”" (UTF-8 bytes interpreted as Windows-1252/Latin-1)
    - "‚Äî" (UTF-8 bytes interpreted as mac_roman)
    """
    if not text:
        return text
    replacements = {
        "â€”": "—",
        "â€“": "–",
        "â€\"": "—",
        "‚Äî": "—",
        "‚Äì": "–",
        "Ã—": "×",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def _parse_date(value: str | None, fallback: dt.date) -> str:
    if not value:
        return fallback.isoformat()
    value = value.strip()
    if not value:
        return fallback.isoformat()
    # Accept YYYY-MM-DD.
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        # Accept common spreadsheet formats like M/D/YY or M/D/YYYY.
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})$", value)
        if m:
            month = int(m.group(1))
            day = int(m.group(2))
            year = int(m.group(3))
            if year < 100:
                year += 2000
            try:
                return dt.date(year, month, day).isoformat()
            except ValueError as exc2:
                raise ValueError(f"Invalid date '{value}'.") from exc2

        raise ValueError(f"Invalid date '{value}'. Expected YYYY-MM-DD (or M/D/YY).") from exc


def _parse_style(value: str | None) -> str:
    value = (value or "").strip().lower()
    if not value:
        return "square"
    if value in {"square", "banner"}:
        return value
    raise ValueError("Invalid style. Use 'square' or 'banner'.")


def _normalize_collection(value: str) -> str:
    value = (value or "").strip().lower()
    if value in {"pictures", "picture", "pics", "pic"}:
        return "pictures"
    if value in {"art", "scientific art", "science art"}:
        return "art"
    raise ValueError("Invalid collection. Use 'pictures' or 'art'.")


def _parse_home_slot(value: str | None) -> str | None:
    """
    Parse the optional `home_slot` CSV column.

    Supported slots (normalized):
    - publications
    - projects
    - team
    - art
    - pictures
    """
    value = (value or "").strip().lower()
    if not value:
        return None
    aliases = {
        "pub": "publications",
        "pubs": "publications",
        "publication": "publications",
        "publications": "publications",
        "projects": "projects",
        "project": "projects",
        "team": "team",
        "collaborators": "team",
        "art": "art",
        "scientific art": "art",
        "pictures": "pictures",
        "pics": "pictures",
        "photos": "pictures",
    }
    normalized = aliases.get(value, value)
    if normalized in {"publications", "projects", "team", "art", "pictures"}:
        return normalized
    raise ValueError("Invalid home_slot. Use publications/projects/team/art/pictures (or leave blank).")


def _parse_project_area(value: str | None) -> str | None:
    """
    Parse the optional `project_area` CSV column.

    Supported areas (normalized):
    - cartilage
    - tendon
    - imaging-ml
    - other
    """
    value = (value or "").strip().lower()
    if not value:
        return None
    aliases = {
        "cartilage": "cartilage",
        "synovium": "cartilage",
        "tendon": "tendon",
        "imaging": "imaging-ml",
        "ml": "imaging-ml",
        "imaging-ml": "imaging-ml",
        "imaging + ml": "imaging-ml",
        "other": "other",
    }
    normalized = aliases.get(value, value)
    if normalized in {"cartilage", "tendon", "imaging-ml", "other"}:
        return normalized
    raise ValueError("Invalid project_area. Use cartilage/tendon/imaging-ml/other (or leave blank).")


def _parse_project_page_section(value: str | None) -> str | None:
    """
    Parse the optional `project_page_section` CSV column.

    This attaches images to *project subpages* (e.g., `projects/cartilage/`)
    without selecting them as the featured image on the main Projects page.
    """
    return _parse_project_area(value)


def _parse_share_page(value: str | None) -> str | None:
    """
    Parse the optional `share_page` CSV column.

    This selects a single gallery image to be used as the OpenGraph/Twitter
    preview image (og:image) for a specific page.

    Supported pages (normalized):
    - home
    - publications
    - projects
    - team
    - art
    - pictures
    - updates
    """
    value = (value or "").strip().lower()
    if not value:
        return None
    aliases = {
        "home": "home",
        "/": "home",
        "index": "home",
        "publications": "publications",
        "publication": "publications",
        "research": "publications",
        "projects": "projects",
        "project": "projects",
        "team": "team",
        "collaborators": "team",
        "art": "art",
        "scientific art": "art",
        "pictures": "pictures",
        "photos": "pictures",
        "updates": "updates",
        "news": "updates",
        "blog": "updates",
        "news/blog": "updates",
    }
    normalized = aliases.get(value, value)
    if normalized in {"home", "publications", "projects", "team", "art", "pictures", "updates"}:
        return normalized
    raise ValueError(
        "Invalid share_page. Use home/publications/projects/team/art/pictures/updates (or leave blank)."
    )


@dataclass(frozen=True)
class GalleryRow:
    collection: str
    image: str
    title: str
    tags: list[str]
    date: str
    year: int | None
    style: str
    subtitle: str | None
    alt: str | None
    featured: bool
    featured_rank: int | None
    home_slot: str | None
    project_area: str | None
    project_area_rank: int | None
    project_page_section: str | None
    project_page_rank: int | None
    header_background: bool
    header_background_rank: int | None
    share_page: str | None
    share_page_rank: int | None
    line_no: int


def _read_csv_rows(path: Path) -> list[GalleryRow]:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    today = dt.date.today()
    rows: list[GalleryRow] = []
    # `utf-8-sig` handles BOM-prefixed CSVs (common from Excel exports).
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = {c for c in ["collection", "image", "title", "tags"] if c not in (reader.fieldnames or [])}
        if missing:
            raise ValueError(f"CSV is missing required columns: {sorted(missing)}")
        for idx, raw in enumerate(reader, start=2):  # header is line 1
            if raw is None:
                continue
            # Skip fully blank lines.
            if not any((v or "").strip() for v in raw.values()):
                continue
            try:
                collection = _normalize_collection(raw.get("collection") or "")
                image = _infer_image_path(raw.get("image") or "")
                title = _fix_common_mojibake((raw.get("title") or "")).strip()
                tags = _split_tags(raw.get("tags") or "")
                date = _parse_date(raw.get("date"), today)
                year_raw = (raw.get("year") or "").strip()
                year = int(year_raw) if year_raw else _parse_year_from_filename(Path(image).name)
                style = _parse_style(raw.get("style"))
                subtitle = _fix_common_mojibake((raw.get("subtitle") or "")).strip() or None
                alt = _fix_common_mojibake((raw.get("alt") or "")).strip() or None
                featured_raw = (raw.get("featured") or "").strip().lower()
                featured = featured_raw in {"1", "true", "yes", "y", "featured"}
                featured_rank_raw = (raw.get("featured_rank") or "").strip()
                featured_rank = int(featured_rank_raw) if featured_rank_raw else None
                home_slot = _parse_home_slot(raw.get("home_slot"))
                project_area = _parse_project_area(raw.get("project_area"))
                project_area_rank_raw = (raw.get("project_area_rank") or "").strip()
                project_area_rank = int(project_area_rank_raw) if project_area_rank_raw else None
                project_page_section = _parse_project_page_section(raw.get("project_page_section"))
                project_page_rank_raw = (raw.get("project_page_rank") or "").strip()
                project_page_rank = int(project_page_rank_raw) if project_page_rank_raw else None
                header_background_raw = (raw.get("header_background") or "").strip().lower()
                header_background = header_background_raw in {"1", "true", "yes", "y", "on"}
                header_background_rank_raw = (raw.get("header_background_rank") or "").strip()
                header_background_rank = int(header_background_rank_raw) if header_background_rank_raw else None

                share_page = _parse_share_page(raw.get("share_page"))
                share_page_rank_raw = (raw.get("share_page_rank") or "").strip()
                share_page_rank = int(share_page_rank_raw) if share_page_rank_raw else None
            except Exception as exc:
                raise ValueError(f"CSV parse error on line {idx}: {exc}") from exc

            if not image or image == "images/":
                raise ValueError(f"CSV parse error on line {idx}: missing image")
            if not title:
                raise ValueError(f"CSV parse error on line {idx}: missing title")

            rows.append(
                GalleryRow(
                    collection=collection,
                    image=image,
                    title=title,
                    tags=tags,
                    date=date,
                    year=year,
                    style=style,
                    subtitle=subtitle,
                    alt=alt,
                    featured=featured,
                    featured_rank=featured_rank,
                    home_slot=home_slot,
                    project_area=project_area,
                    project_area_rank=project_area_rank,
                    project_page_section=project_page_section,
                    project_page_rank=project_page_rank,
                    header_background=header_background,
                    header_background_rank=header_background_rank,
                    share_page=share_page,
                    share_page_rank=share_page_rank,
                    line_no=idx,
                )
            )
    return rows


def _find_any_by_stem(dir_path: Path, stem: str) -> list[Path]:
    if not dir_path.exists():
        return []
    matches: list[Path] = []
    for p in dir_path.iterdir():
        if not p.is_file():
            continue
        if p.suffix not in KNOWN_IMAGE_EXTS:
            continue
        if p.stem == stem:
            matches.append(p)
    return matches


def validate_rows(rows: Iterable[GalleryRow]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    seen: set[tuple[str, str]] = set()
    home_slots: dict[str, GalleryRow] = {}
    project_area_ranks: dict[tuple[str, int], GalleryRow] = {}
    project_area_counts: dict[str, int] = {}
    project_page_ranks: dict[tuple[str, int], GalleryRow] = {}
    header_bg_ranks: dict[int, GalleryRow] = {}
    share_page_ranks: dict[tuple[str, int], GalleryRow] = {}
    share_page_counts: dict[str, int] = {}
    originals_dir = ROOT / "images" / "originals"
    wm_dir = ROOT / "images" / "wm"

    for row in rows:
        key = (row.collection, row.image)
        if key in seen:
            errors.append(f"Duplicate image in {row.collection}: {row.image} (line {row.line_no})")
        else:
            seen.add(key)

        filename = Path(row.image).name
        stem = Path(filename).stem
        original_exact = originals_dir / filename
        wm_exact = wm_dir / filename

        has_original = original_exact.exists() or bool(_find_any_by_stem(originals_dir, stem))
        has_wm = wm_exact.exists() or bool(_find_any_by_stem(wm_dir, stem))

        if not has_original and not has_wm:
            warnings.append(
                f"Image not found in images/originals/ or images/wm/ (stem match): {filename} (line {row.line_no})"
            )
        elif not has_original and has_wm:
            warnings.append(
                f"Missing original for {filename} (line {row.line_no}). "
                "This is ok if you already generated images/wm/, but you won't be able to regenerate it."
            )

        if row.home_slot:
            prev = home_slots.get(row.home_slot)
            if prev:
                errors.append(
                    f"Multiple rows set home_slot={row.home_slot!r}: {prev.image} (line {prev.line_no}) "
                    f"and {row.image} (line {row.line_no})"
                )
            else:
                home_slots[row.home_slot] = row

        if row.project_area:
            project_area_counts[row.project_area] = project_area_counts.get(row.project_area, 0) + 1
            if row.project_area_rank is not None:
                key_rank = (row.project_area, row.project_area_rank)
                prev = project_area_ranks.get(key_rank)
                if prev:
                    errors.append(
                        f"Multiple rows set project_area={row.project_area!r} with project_area_rank={row.project_area_rank}: "
                        f"{prev.image} (line {prev.line_no}) and {row.image} (line {row.line_no})"
                    )
                else:
                    project_area_ranks[key_rank] = row

        if row.project_page_section and row.project_page_rank is not None:
            key_rank = (row.project_page_section, row.project_page_rank)
            prev = project_page_ranks.get(key_rank)
            if prev:
                errors.append(
                    f"Multiple rows set project_page_section={row.project_page_section!r} with project_page_rank={row.project_page_rank}: "
                    f"{prev.image} (line {prev.line_no}) and {row.image} (line {row.line_no})"
                )
            else:
                project_page_ranks[key_rank] = row

        if row.header_background and row.header_background_rank is not None:
            prev = header_bg_ranks.get(row.header_background_rank)
            if prev:
                errors.append(
                    f"Multiple rows set header_background_rank={row.header_background_rank}: {prev.image} (line {prev.line_no}) "
                    f"and {row.image} (line {row.line_no})"
                )
            else:
                header_bg_ranks[row.header_background_rank] = row

        if row.share_page:
            share_page_counts[row.share_page] = share_page_counts.get(row.share_page, 0) + 1
            if row.share_page_rank is not None:
                key_rank = (row.share_page, row.share_page_rank)
                prev = share_page_ranks.get(key_rank)
                if prev:
                    errors.append(
                        f"Multiple rows set share_page={row.share_page!r} with share_page_rank={row.share_page_rank}: "
                        f"{prev.image} (line {prev.line_no}) and {row.image} (line {row.line_no})"
                    )
                else:
                    share_page_ranks[key_rank] = row

    for area, count in sorted(project_area_counts.items()):
        if count > 1:
            warnings.append(
                f"Multiple rows set project_area={area!r} ({count} rows). "
                "The Projects page can only display one image per area; "
                "use project_area_rank to control which one is chosen."
            )

    for page_key, count in sorted(share_page_counts.items()):
        if count > 1:
            warnings.append(
                f"Multiple rows set share_page={page_key!r} ({count} rows). "
                "Each page can only use one share image; "
                "use share_page_rank to control which one is chosen."
            )

    return errors, warnings


def _sort_rows(rows: list[GalleryRow]) -> list[GalleryRow]:
    # Most recent first: year (if present) desc, then date desc, then stable by line number.
    def sort_key(r: GalleryRow) -> tuple[int, int, str, int]:
        has_year = 1 if r.year else 0
        year = r.year or 0
        return (has_year, year, r.date, -r.line_no)

    return sorted(rows, key=sort_key, reverse=True)


def _pick_project_area_images(rows: Iterable[GalleryRow]) -> dict[str, str]:
    """
    Choose the single image used for each Projects page area card.

    If multiple rows are assigned to the same `project_area`, selection order is:
    1) lowest `project_area_rank` (if provided)
    2) most recent year (desc)
    3) title (asc)
    4) file order (stable)
    """
    buckets: dict[str, list[GalleryRow]] = {}
    for r in rows:
        if r.project_area:
            buckets.setdefault(r.project_area, []).append(r)

    out: dict[str, str] = {}
    for area, items in buckets.items():
        items_sorted = sorted(
            items,
            key=lambda r: (
                10_000 if r.project_area_rank is None else r.project_area_rank,
                -(r.year or 0),
                r.title.lower(),
                r.line_no,
            ),
        )
        out[area] = items_sorted[0].image
    return out


def _pick_share_page_images(rows: Iterable[GalleryRow]) -> dict[str, str]:
    """
    Pick per-page social share preview images (og:image) from CSV rows.

    Selection order (per page key):
      1) lowest `share_page_rank` (if provided)
      2) latest year
      3) stable tie-break by title
      4) file order (stable)
    """
    buckets: dict[str, list[GalleryRow]] = {}
    for r in rows:
        if r.share_page:
            buckets.setdefault(r.share_page, []).append(r)

    out: dict[str, str] = {}
    for page_key, items in buckets.items():
        items_sorted = sorted(
            items,
            key=lambda r: (
                10_000 if r.share_page_rank is None else r.share_page_rank,
                -(r.year or 0),
                r.title.lower(),
                r.line_no,
            ),
        )
        out[page_key] = items_sorted[0].image
    return out


def _row_to_yaml_item(row: GalleryRow) -> dict[str, Any]:
    item: dict[str, Any] = {
        "date": row.date,
        "title": row.title,
        "image": row.image,
        "tags": row.tags,
        "style": row.style,
    }
    if row.year:
        item["year"] = row.year
    if row.subtitle:
        item["subtitle"] = row.subtitle
    if row.alt:
        item["alt"] = row.alt
    if row.featured:
        item["featured"] = True
    if row.featured_rank is not None:
        item["featured_rank"] = row.featured_rank
    if row.project_area:
        item["project_area"] = row.project_area
    if row.project_area_rank is not None:
        item["project_area_rank"] = row.project_area_rank
    if row.project_page_section:
        item["project_page_section"] = row.project_page_section
    if row.project_page_rank is not None:
        item["project_page_rank"] = row.project_page_rank
    return item


def build_yaml_from_csv(csv_path: Path, out_pictures: Path, out_art: Path) -> None:
    rows = _read_csv_rows(csv_path)
    errors, warnings = validate_rows(rows)
    if errors:
        msg = "\n".join(["Validation errors:"] + [f"- {e}" for e in errors])
        raise SystemExit(msg)
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"- {w}")
        print()

    pictures_rows = _sort_rows([r for r in rows if r.collection == "pictures"])
    art_rows = _sort_rows([r for r in rows if r.collection == "art"])

    pictures_data = [_row_to_yaml_item(r) for r in pictures_rows]
    art_data = [_row_to_yaml_item(r) for r in art_rows]

    home_features: dict[str, str] = {}
    project_area_images = _pick_project_area_images(rows)
    page_share_images = _pick_share_page_images(rows)
    header_background_rows: list[GalleryRow] = []
    for r in rows:
        if r.home_slot:
            home_features[r.home_slot] = r.image
        if r.header_background:
            header_background_rows.append(r)

    header_background_rows_sorted = sorted(
        header_background_rows,
        key=lambda r: (
            10_000 if r.header_background_rank is None else r.header_background_rank,
            -(r.year or 0),
            r.title.lower(),
        ),
    )
    header_background_images = [r.image for r in header_background_rows_sorted]

    out_pictures.write_text(
        yaml.dump(pictures_data, Dumper=FlowSeqDumper, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    out_art.write_text(
        yaml.dump(art_data, Dumper=FlowSeqDumper, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    HOME_FEATURES_YAML.write_text(
        yaml.safe_dump(home_features, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
    PROJECT_AREA_IMAGES_YAML.write_text(
        yaml.safe_dump(project_area_images, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
    PAGE_SHARE_IMAGES_YAML.write_text(
        yaml.safe_dump(page_share_images, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
    HEADER_BACKGROUNDS_YAML.write_text(
        yaml.safe_dump(
            {
                # Applied only on the home page header to respect attention and
                # readability on other pages.
                "images": header_background_images,
                "interval_ms": 14000,
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def export_csv(out_path: Path, pictures_path: Path, art_path: Path) -> None:
    """Export current YAML into a single master CSV."""
    def load_yaml_list(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if not isinstance(data, list):
            raise ValueError(f"Expected YAML list in {path}")
        return [x for x in data if isinstance(x, dict)]

    rows: list[dict[str, str]] = []
    for collection, path in [("pictures", pictures_path), ("art", art_path)]:
        for item in load_yaml_list(path):
            image = str(item.get("image", "")).strip()
            title = str(item.get("title", "")).strip()
            tags = item.get("tags") or []
            if isinstance(tags, list):
                tags_str = "; ".join(str(t).strip() for t in tags if str(t).strip())
            else:
                tags_str = str(tags).strip()
            rows.append(
                {
                    "collection": collection,
                    "image": image,
                    "title": title,
                    "tags": tags_str,
                    "date": str(item.get("date", "")).strip(),
                    "year": str(item.get("year", "")).strip(),
                    "style": str(item.get("style", "")).strip(),
                    "subtitle": str(item.get("subtitle", "")).strip(),
                    "alt": str(item.get("alt", "")).strip(),
                    "featured": "true" if item.get("featured") is True else "",
                    "featured_rank": str(item.get("featured_rank", "")).strip(),
                    "home_slot": "",
                    "project_area": "",
                    "project_area_rank": "",
                    "project_page_section": "",
                    "project_page_rank": "",
                    "header_background": "",
                    "header_background_rank": "",
                    "share_page": "",
                    "share_page_rank": "",
                }
            )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "collection",
            "image",
            "title",
            "tags",
            "date",
            "year",
            "style",
            "subtitle",
            "alt",
            "featured",
            "featured_rank",
            "home_slot",
            "project_area",
            "project_area_rank",
            "project_page_section",
            "project_page_rank",
            "header_background",
            "header_background_rank",
            "share_page",
            "share_page_rank",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_preview_html(csv_path: Path, out_path: Path) -> None:
    """
    Write a local HTML preview of the master CSV with thumbnail images.

    This is useful for quickly sanity-checking that filenames map to the images
    you expect, without trying to embed thumbnails into the CSV itself (most
    spreadsheet programs don't store images inside CSV files).
    """
    rows = _read_csv_rows(csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def pick_src(image_path: str) -> tuple[str, str]:
        name = Path(image_path).name
        candidates = [
            (ROOT / "images" / "wm" / "thumb" / name, f"../images/wm/thumb/{name}"),
            (ROOT / "images" / "wm" / name, f"../images/wm/{name}"),
            (ROOT / image_path, f"../{image_path}"),
        ]
        for abs_path, rel in candidates:
            if abs_path.exists():
                return rel, name
        return "", name

    lines: list[str] = []
    lines.append("<!doctype html>")
    lines.append("<html><head><meta charset='utf-8'>")
    lines.append("<meta name='viewport' content='width=device-width, initial-scale=1'>")
    lines.append("<title>Gallery master preview</title>")
    lines.append(
        "<style>"
        "body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:18px;background:#111;color:#eee}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{border:1px solid #2a2a2a;padding:8px;vertical-align:top}"
        "th{position:sticky;top:0;background:#1a1a1a}"
        "a{color:#2dd4bf}"
        ".thumb{width:64px;height:64px;object-fit:cover;border-radius:10px;background:#222;display:block}"
        ".muted{color:#aaa;font-size:12px}"
        "</style>"
    )
    lines.append("</head><body>")
    lines.append("<h1 style='margin:0 0 6px'>Gallery master preview</h1>")
    lines.append(f"<div class='muted'>Source: {csv_path.as_posix()}</div>")
    lines.append("<div class='muted'>Tip: edit the CSV in a spreadsheet, then rebuild YAML and watermarks.</div>")
    lines.append(
        "<details style='margin:12px 0'>"
        "<summary style='cursor:pointer'>Column reference (what each column can do)</summary>"
        "<div style='margin-top:10px;max-width:1100px;line-height:1.5'>"
        "<ul style='margin:0;padding-left:18px'>"
        "<li><b>collection</b>: <code>pictures</code> or <code>art</code></li>"
        "<li><b>image</b>: filename or <code>images/&lt;name&gt;</code>; web-friendly ext preferred (<code>.jpg/.png</code>)</li>"
        "<li><b>tags</b>: semicolon-separated (<code>tag1; tag2; tag3</code>)</li>"
        "<li><b>style</b>: <code>square</code> or <code>banner</code> (controls aspect ratio in the grid)</li>"
        "<li><b>subtitle</b> / <b>alt</b>: optional text shown in the lightbox and for accessibility</li>"
        "<li><b>featured</b>: mark as a gallery highlight card</li>"
        "<li><b>featured_rank</b>: ordering for highlights (lower shows first)</li>"
        "<li><b>home_slot</b>: selects the Home page highlight image: "
        "<code>publications</code>, <code>projects</code>, <code>team</code>, <code>art</code></li>"
        "<li><b>project_area</b>: selects the main Projects page card image: "
        "<code>cartilage</code>, <code>tendon</code>, <code>imaging-ml</code>, <code>other</code></li>"
        "<li><b>project_area_rank</b>: priority when multiple rows share the same <code>project_area</code> (lower wins)</li>"
        "<li><b>project_page_section</b>: attaches images to a project subpage without affecting the main Projects cards "
        "(same values as <code>project_area</code>)</li>"
        "<li><b>project_page_rank</b>: ordering within a project subpage image gallery (lower shows earlier)</li>"
        "<li><b>header_background</b>: <code>true/false</code> to include in the rotating Home header background</li>"
        "<li><b>header_background_rank</b>: ordering for header rotation (lower shows earlier)</li>"
        "<li><b>share_page</b>: picks an image to be used as the social preview (<code>og:image</code>) for a page: "
        "<code>home</code>, <code>publications</code>, <code>projects</code>, <code>team</code>, <code>art</code>, <code>pictures</code>, <code>updates</code></li>"
        "<li><b>share_page_rank</b>: priority when multiple rows share the same <code>share_page</code> (lower wins)</li>"
        "</ul>"
        "</div>"
        "</details>"
    )
    lines.append("<hr style='border:0;border-top:1px solid #2a2a2a;margin:14px 0'>")
    lines.append("<table>")
    lines.append(
        "<thead><tr>"
        "<th title='Preview thumbnail (from images/wm/thumb when available)'>Thumb</th>"
        "<th title='pictures or art'>Collection</th>"
        "<th title='Display title (year may be inferred from filename -YYYY)'>Title</th>"
        "<th title='Image path (usually images/&lt;name&gt;.jpg)'>Image</th>"
        "<th title='Semicolon-separated tags used for filtering'>Tags</th>"
        "<th title='Optional explicit year (otherwise inferred from filename -YYYY)'>Year</th>"
        "<th title='square or banner'>Style</th>"
        "<th title='Marks as a highlight card (optional # rank)'>Featured</th>"
        "<th title='Home highlight slot: publications/projects/team/art'>Home slot</th>"
        "<th title='Projects page card area: cartilage/tendon/imaging-ml/other'>Project area</th>"
        "<th title='Priority when multiple images share a project_area (lower wins)'>Project rank</th>"
        "<th title='Attach to a project subpage gallery'>Project page</th>"
        "<th title='Ordering within a project subpage gallery (lower shows earlier)'>Project page rank</th>"
        "<th title='Include in rotating Home header background'>Header bg</th>"
        "<th title='Ordering within header rotation (lower shows earlier)'>Header bg rank</th>"
        "<th title='Use this image as the social preview (og:image) for a page'>Share page</th>"
        "<th title='Priority when multiple rows share a share_page (lower wins)'>Share rank</th>"
        "</tr></thead><tbody>"
    )
    for r in rows:
        src, name = pick_src(r.image)
        tags = "; ".join(r.tags)
        featured = "yes" if r.featured else ""
        year = str(r.year) if r.year else ""
        thumb_html = f"<img class='thumb' src='{src}' alt='{name}'>" if src else "<div class='thumb'></div>"
        link_html = f"<a href='{src}' target='_blank' rel='noopener noreferrer'>{name}</a>" if src else name
        lines.append(
            "<tr>"
            f"<td>{thumb_html}</td>"
            f"<td>{r.collection}</td>"
            f"<td>{r.title}</td>"
            f"<td>{link_html}<div class='muted'>{r.image}</div></td>"
            f"<td>{tags}</td>"
            f"<td>{year}</td>"
            f"<td>{r.style}</td>"
            f"<td>{featured}{(' #' + str(r.featured_rank)) if r.featured_rank else ''}</td>"
            f"<td>{r.home_slot or ''}</td>"
            f"<td>{r.project_area or ''}</td>"
            f"<td>{r.project_area_rank or ''}</td>"
            f"<td>{r.project_page_section or ''}</td>"
            f"<td>{r.project_page_rank or ''}</td>"
            f"<td>{'yes' if r.header_background else ''}</td>"
            f"<td>{r.header_background_rank or ''}</td>"
            f"<td>{r.share_page or ''}</td>"
            f"<td>{r.share_page_rank or ''}</td>"
            "</tr>"
        )
    lines.append("</tbody></table>")
    lines.append("</body></html>")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _title_guess(filename: str) -> str:
    """
    Best-effort title guess from filename.

    This is only used by the `scan` command to create a starter CSV.
    """
    name = Path(filename).name
    stem = Path(name).stem

    # Strip trailing `-YYYY` if present.
    stem = re.sub(r"-(19[0-9]{2}|20[0-9]{2})$", "", stem)

    if stem.startswith("science_"):
        n = stem.replace("science_", "")
        return f"Scientific art {n}" if n.isdigit() else "Scientific art"

    if stem.startswith("nature_") or stem == "nature":
        if "pano" in stem or "panorama" in stem or stem in {"nature_0", "nature_20", "nature_23"}:
            return "Nature panorama"
        return "Nature"

    if stem.startswith("music-") or stem.startswith("music_") or stem.startswith("music"):
        # Convert `music-dave-matthews` -> `Music: Dave Matthews`
        suffix = stem.split("-", 1)[1] if "-" in stem else stem
        suffix = suffix.replace("_", " ").replace("-", " ").strip()
        suffix = " ".join(w.capitalize() for w in suffix.split())
        return f"Music: {suffix}" if suffix and suffix.lower() != "music" else "Music"

    if stem.startswith("sports") or stem.startswith("sport"):
        return "Sports"

    if stem.startswith("talk"):
        return "Research talk"

    if stem.startswith("poster"):
        return "Conference poster"

    if stem.startswith("phd"):
        return "PhD milestone"

    if stem.startswith("group"):
        return "Group photo"

    if stem.startswith("team"):
        return "Team photo"

    if stem.startswith("mentors") or stem.startswith("mentor"):
        return "Mentors"

    if stem.startswith("ors"):
        return "ORS Art in Science"

    # Fallback: humanize.
    human = stem.replace("_", " ").replace("-", " ").strip()
    human = re.sub(r"\s+", " ", human)
    return human.title() if human else "Image"


def _tags_guess(collection: str, filename: str) -> list[str]:
    """Best-effort tag guess from filename/prefix (used by `scan`)."""
    name = Path(filename).name.lower()
    if collection == "art":
        return ["art", "scientific art", "imaging"]

    if name.startswith("nature"):
        return ["nature", "outdoors", "beyond the lab"]
    if name.startswith("music"):
        return ["music", "beyond the lab"]
    if name.startswith("sports"):
        return ["sports", "beyond the lab"]
    if name.startswith(("group", "team")):
        return ["team", "group", "lab"]
    if name.startswith(("mentors", "mentor")):
        return ["mentors"]
    if name.startswith("talk"):
        return ["talk", "conference", "speaking"]
    if name.startswith("poster"):
        return ["poster", "conference"]
    if name.startswith("phd"):
        return ["milestone", "phd", "portrait"]
    return []


def _collection_guess(filename: str, prefix_map: dict[str, str]) -> str:
    """
    Guess collection from filename (used by `scan`).

    Default: pictures. Use `--prefix-map` to override (example: `science=art,ors=art`).
    """
    lower = Path(filename).name.lower()
    for prefix, collection in prefix_map.items():
        if lower.startswith(prefix.lower()):
            return collection
    return "pictures"


def scan_dir_to_csv(
    *,
    dir_path: Path,
    out_path: Path,
    prefix_map: dict[str, str],
    default_date: dt.date,
    include_subdirs: bool,
) -> None:
    """
    Create a starter `gallery_master.csv` by scanning a directory of images.

    This is useful when you want to bootstrap the gallery from scratch based on
    filenames alone. You'll still want to review titles/tags afterwards.
    """
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    files: list[Path] = []
    iterator = dir_path.rglob("*") if include_subdirs else dir_path.iterdir()
    for p in iterator:
        if not p.is_file():
            continue
        if p.suffix not in KNOWN_IMAGE_EXTS:
            continue
        files.append(p)

    files = sorted(files, key=lambda p: p.name.lower())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            field
            for field in [
                "collection",
                "image",
                "title",
                "tags",
                "date",
                "year",
                "style",
                "subtitle",
                "alt",
                "featured",
                "featured_rank",
                "home_slot",
                "project_area",
                "project_area_rank",
                "project_page_section",
                "project_page_rank",
                "header_background",
                "header_background_rank",
            ]
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for p in files:
            collection = _collection_guess(p.name, prefix_map)
            year = _parse_year_from_filename(p.name)
            title = _title_guess(p.name)
            tags = _tags_guess(collection, p.name)
            stem_lower = p.stem.lower()
            # Banner (panorama) heuristic:
            # - explicit keywords in filename
            # - known "panorama slot" stems used on the site
            pano_stems = {"nature_0", "nature_20", "nature_23", "nature_44"}
            style = (
                "banner"
                if ("panorama" in stem_lower or "pano" in stem_lower or stem_lower in pano_stems)
                else "square"
            )
            image_name = p.name
            # Store web-friendly extensions in the CSV/YAML even if originals are HEIC/TIFF.
            if p.suffix.lower() in {".heic", ".heif"}:
                image_name = f"{p.stem}.jpg"
            elif p.suffix.lower() in {".tif", ".tiff"}:
                image_name = f"{p.stem}.png"
            writer.writerow(
                {
                    "collection": collection,
                    "image": f"images/{image_name}",
                    "title": title,
                    "tags": "; ".join(tags),
                    "date": default_date.isoformat(),
                    "year": str(year) if year else "",
                    "style": style,
                    "subtitle": "",
                    "alt": "",
                    "featured": "",
                    "featured_rank": "",
                    "home_slot": "",
                    "project_area": "",
                    "project_area_rank": "",
                    "project_page_section": "",
                    "project_page_rank": "",
                    "header_background": "",
                    "header_background_rank": "",
                }
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CSV-first pipeline for gallery YAML.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_export = sub.add_parser("export", help="Export current YAML into a master CSV.")
    p_export.add_argument("--out", type=Path, default=DEFAULT_CSV, help="Output CSV path.")
    p_export.add_argument("--pictures", type=Path, default=PICTURES_YAML, help="Pictures YAML path.")
    p_export.add_argument("--art", type=Path, default=ART_YAML, help="Art YAML path.")

    p_build = sub.add_parser("build", help="Build YAML from a master CSV.")
    p_build.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Master CSV path.")
    p_build.add_argument("--out-pictures", type=Path, default=PICTURES_YAML, help="Pictures YAML output.")
    p_build.add_argument("--out-art", type=Path, default=ART_YAML, help="Art YAML output.")

    p_validate = sub.add_parser("validate", help="Validate a master CSV without writing YAML.")
    p_validate.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Master CSV path.")

    p_preview = sub.add_parser("preview", help="Generate a local HTML preview with thumbnails.")
    p_preview.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Master CSV path.")
    p_preview.add_argument(
        "--out",
        type=Path,
        default=ROOT / "tools" / "gallery_master_preview.html",
        help="Output HTML path (default: tools/gallery_master_preview.html).",
    )

    p_scan = sub.add_parser("scan", help="Create a starter master CSV by scanning an image directory.")
    p_scan.add_argument(
        "--dir",
        type=Path,
        default=ROOT / "images" / "originals",
        help="Directory to scan (default: images/originals).",
    )
    p_scan.add_argument("--out", type=Path, default=DEFAULT_CSV, help="Output CSV path.")
    p_scan.add_argument(
        "--include-subdirs",
        action="store_true",
        help="Recursively scan subdirectories.",
    )
    p_scan.add_argument(
        "--prefix-map",
        default="science=art,ors=art",
        help="Comma-separated prefix=collection rules (default: science=art,ors=art).",
    )
    p_scan.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Default date for all rows (YYYY-MM-DD; default: today).",
    )

    args = parser.parse_args(argv)

    if args.cmd == "export":
        export_csv(args.out, args.pictures, args.art)
        print(f"Wrote {args.out}")
        return 0

    if args.cmd == "validate":
        rows = _read_csv_rows(args.csv)
        errors, warnings = validate_rows(rows)
        for e in errors:
            print(f"ERROR: {e}")
        for w in warnings:
            print(f"WARN: {w}")
        if errors:
            return 2
        print("OK")
        return 0

    if args.cmd == "preview":
        write_preview_html(args.csv, args.out)
        print(f"Wrote {args.out}")
        return 0

    if args.cmd == "build":
        build_yaml_from_csv(args.csv, args.out_pictures, args.out_art)
        print(f"Wrote {args.out_pictures}")
        print(f"Wrote {args.out_art}")
        return 0

    if args.cmd == "scan":
        prefix_map: dict[str, str] = {}
        for rule in str(args.prefix_map).split(","):
            rule = rule.strip()
            if not rule:
                continue
            if "=" not in rule:
                raise SystemExit(f"Invalid --prefix-map rule: {rule!r} (expected prefix=collection)")
            prefix, collection = rule.split("=", 1)
            prefix_map[prefix.strip()] = _normalize_collection(collection.strip())
        try:
            default_date = dt.date.fromisoformat(str(args.date))
        except ValueError as exc:
            raise SystemExit("Invalid --date. Expected YYYY-MM-DD.") from exc

        scan_dir_to_csv(
            dir_path=args.dir,
            out_path=args.out,
            prefix_map=prefix_map,
            default_date=default_date,
            include_subdirs=bool(args.include_subdirs),
        )
        print(f"Wrote {args.out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
