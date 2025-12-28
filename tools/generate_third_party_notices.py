#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Michael A. David
"""
Generate (or refresh) the Python dependencies section in THIRD_PARTY_NOTICES.md.

This script is designed to run in CI after installing `_cite/requirements.txt`
so that versions/licenses are accurate for the environment used to build the site.

It uses only the Python standard library.

Usage:
  python tools/generate_third_party_notices.py
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
NOTICES = ROOT / "THIRD_PARTY_NOTICES.md"

BEGIN = "<!-- BEGIN AUTO-GENERATED PYTHON LICENSES -->"
END = "<!-- END AUTO-GENERATED PYTHON LICENSES -->"


REQ_FILES: Sequence[Path] = (
    ROOT / "_cite" / "requirements.txt",
    ROOT / "tools" / "requirements-collaborators.txt",
    ROOT / "tools" / "requirements-icons.txt",
    ROOT / "tools" / "requirements-watermark.txt",
)


@dataclass(frozen=True)
class Dep:
    name: str
    version: str
    license: str
    homepage: str
    installed: bool


def _parse_requirement_name(line: str) -> Optional[str]:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # Strip inline comments.
    line = line.split("#", 1)[0].strip()
    if not line:
        return None

    # Remove environment markers; keep left side.
    line = line.split(";", 1)[0].strip()
    if not line:
        return None

    # Get the leading distribution name (before any version specifiers).
    # Handles: name~=x, name==x, name>=x, name[extra]~=x
    m = re.match(r"^([A-Za-z0-9_.-]+)", line)
    if not m:
        return None
    return m.group(1)


def read_requirements(req_files: Iterable[Path]) -> List[str]:
    names: List[str] = []
    for path in req_files:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            name = _parse_requirement_name(raw)
            if name:
                names.append(name)
    # de-dupe preserving order
    out: List[str] = []
    seen = set()
    for n in names:
        key = n.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(n)
    return out


def _license_from_metadata(dist: metadata.Distribution) -> str:
    meta = dist.metadata
    lic = (meta.get("License") or "").strip()
    if lic and lic.lower() not in {"unknown", "none"}:
        return lic
    # Fall back to classifiers.
    classifiers = meta.get_all("Classifier") or []
    lic_cls = [c for c in classifiers if c.startswith("License :: ")]
    if lic_cls:
        return lic_cls[-1].replace("License :: ", "").strip()
    return ""


def _homepage_from_metadata(dist: metadata.Distribution) -> str:
    meta = dist.metadata
    home = (meta.get("Home-page") or "").strip()
    if home:
        return home
    # Project-URL can appear multiple times; try to pick homepage-ish.
    urls = meta.get_all("Project-URL") or []
    for u in urls:
        # Format: "Label, https://…"
        if "," in u:
            label, url = [x.strip() for x in u.split(",", 1)]
            if label.lower() in {"homepage", "home", "repository", "source"} and url:
                return url
    if urls:
        # Otherwise return the first URL string.
        return urls[0]
    return ""


def resolve_deps(names: Sequence[str]) -> List[Dep]:
    out: List[Dep] = []
    for name in names:
        try:
            dist = metadata.distribution(name)
        except Exception:
            out.append(Dep(name=name, version="", license="", homepage="", installed=False))
            continue

        out.append(
            Dep(
                name=name,
                version=dist.version or "",
                license=_license_from_metadata(dist),
                homepage=_homepage_from_metadata(dist),
                installed=True,
            )
        )
    return out


def render_section(deps: Sequence[Dep]) -> str:
    lines: List[str] = []
    lines.append(BEGIN)
    lines.append("")
    lines.append("## Python dependencies (build-time)")
    lines.append("")
    lines.append(
        "The site build and citation pipeline use Python packages. Versions/licenses below are captured from the build environment."
    )
    lines.append("")
    lines.append("- Python (standard library) — PSF License: https://docs.python.org/3/license.html")
    lines.append("")

    for dep in sorted(deps, key=lambda d: d.name.lower()):
        if dep.installed:
            lic = dep.license or "(license not reported in package metadata)"
            home = dep.homepage or ""
            line = f"- {dep.name} {dep.version} — {lic}"
            if home:
                line += f": {home}"
            lines.append(line)
        else:
            lines.append(f"- {dep.name} — (not installed in this environment)")

    lines.append("")
    lines.append(END)
    lines.append("")
    return "\n".join(lines)


def upsert_python_section(notices_path: Path, deps: Sequence[Dep]) -> None:
    text = notices_path.read_text(encoding="utf-8") if notices_path.exists() else "# Third-party notices\n\n"

    section = render_section(deps)

    if BEGIN in text and END in text:
        before = text.split(BEGIN, 1)[0].rstrip() + "\n\n"
        after = text.split(END, 1)[1].lstrip()
        notices_path.write_text(before + section + after, encoding="utf-8")
        return

    # If no markers exist, append to end.
    if not text.endswith("\n"):
        text += "\n"
    notices_path.write_text(text + "\n" + section, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    _ = argv or []
    names = read_requirements(REQ_FILES)
    deps = resolve_deps(names)
    if not NOTICES.exists():
        print(f"ERROR: {NOTICES} not found.", file=sys.stderr)
        return 2
    upsert_python_section(NOTICES, deps)
    print(f"Updated {NOTICES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
