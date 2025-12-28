#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Michael A. David

"""
Update `_data/collaborators_map.csv` with an `active` column and correct `status`.

Rule (per user request):
  - active/current for:
    - collaborators affiliated with University of Colorado Anschutz (heuristic: affiliation contains
      "university of colorado" or "anschutz")
    - Spencer Lake at WashU (name match)
  - all others: past

Usage:
  python tools/set_collaborators_active.py
  python tools/set_collaborators_active.py --in _data/collaborators_map.csv --out _data/collaborators_map.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]


def normalize_name(name: str) -> str:
    name = (name or "").strip().lower()
    name = re.sub(r"[^\w\s\-]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def is_spencer_lake(name: str) -> bool:
    n = normalize_name(name)
    # accept common variants
    return n in {"spencer p lake", "spencer lake", "spencer p. lake"}


def is_cu_ansch_affiliation(affiliation: str) -> bool:
    a = (affiliation or "").strip().lower()
    return ("university of colorado" in a) or ("anschutz" in a) or ("cu anschutz" in a)


def update_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    for r in rows:
        name = r.get("name", "")
        aff = r.get("affiliation", "") or ""

        active = is_spencer_lake(name) or is_cu_ansch_affiliation(aff)
        r["active"] = "1" if active else "0"
        r["status"] = "current" if active else "past"
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="inp", default=str(ROOT / "_data" / "collaborators_map.csv"))
    parser.add_argument("--out", dest="out", default=str(ROOT / "_data" / "collaborators_map.csv"))
    args = parser.parse_args()

    in_path = Path(args.inp)
    out_path = Path(args.out)
    if not in_path.exists():
        raise SystemExit(f"Missing input CSV: {in_path}")

    with in_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "active" not in fieldnames:
        # Insert active after status for readability.
        if "status" in fieldnames:
            idx = fieldnames.index("status") + 1
            fieldnames.insert(idx, "active")
        else:
            fieldnames.insert(0, "active")

    rows = update_rows(rows)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    active_count = sum(1 for r in rows if r.get("active") == "1")
    print(f"Updated {out_path} ({len(rows)} rows). Active/current: {active_count}, past: {len(rows) - active_count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
