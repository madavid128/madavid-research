#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Michael A. David
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]


DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "PyYAML is required to read citations.yaml. Install with: pip install pyyaml"
        ) from exc
    return yaml.safe_load(read_text(path))


def load_front_matter(path: Path) -> Dict[str, Any]:
    text = read_text(path)
    parts = re.split(r"^---\s*$", text, flags=re.MULTILINE)
    if len(parts) < 3:
        return {}
    front = parts[1]
    return load_yaml_from_string(front) or {}


def load_yaml_from_string(text: str) -> Any:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "PyYAML is required. Install with: pip install pyyaml"
        ) from exc
    return yaml.safe_load(text)


def normalize_name(name: str) -> str:
    name = re.sub(r"[^\w\s\-]", "", name, flags=re.UNICODE)
    return re.sub(r"\s+", " ", name.strip().lower())


def extract_dois(citations: Any) -> List[str]:
    dois: List[str] = []
    if not isinstance(citations, list):
        return dois
    for item in citations:
        if not isinstance(item, dict):
            continue
        raw_id = str(item.get("id") or "")
        if raw_id.lower().startswith("doi:"):
            doi = raw_id.split(":", 1)[1].strip()
            if doi:
                dois.append(doi)
                continue
        link = str(item.get("link") or "")
        match = DOI_RE.search(link)
        if match:
            dois.append(match.group(0))
    # preserve order while de-duping
    seen = set()
    out = []
    for doi in dois:
        key = doi.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(doi)
    return out


def ncbi_get(url: str, *, email: str, tool: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", f"{tool} (mailto:{email})")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def pubmed_doi_to_pmid(doi: str, *, email: str, tool: str) -> Optional[str]:
    term = f"{doi}[AID]"
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": term, "retmode": "json"}
    )
    raw = ncbi_get(url, email=email, tool=tool)
    try:
        data = json.loads(raw)
        ids = data.get("esearchresult", {}).get("idlist", [])
        if ids:
            return str(ids[0])
    except Exception:
        return None
    return None


def pubmed_fetch_xml(pmid: str, *, email: str, tool: str) -> str:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "retmode": "xml"}
    )
    return ncbi_get(url, email=email, tool=tool)


@dataclass
class Author:
    name: str
    affiliations: List[str]


def parse_pubmed_authors(xml_text: str) -> List[Author]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    authors: List[Author] = []
    for author in root.findall(".//AuthorList/Author"):
        last = (author.findtext("LastName") or "").strip()
        fore = (author.findtext("ForeName") or "").strip()
        collective = (author.findtext("CollectiveName") or "").strip()

        if collective:
            name = collective
        else:
            name = " ".join([fore, last]).strip()
        if not name:
            continue

        affiliations: List[str] = []
        for aff_el in author.findall(".//AffiliationInfo/Affiliation"):
            aff = (aff_el.text or "").strip()
            if aff:
                affiliations.append(aff)
        # de-dupe preserving order
        seen = set()
        uniq: List[str] = []
        for a in affiliations:
            key = a.strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            uniq.append(a)

        authors.append(Author(name=name, affiliations=uniq))

    return authors


YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def parse_pubmed_year(xml_text: str) -> Optional[int]:
    """
    Best-effort publication year extractor from PubMed XML.

    Prefers explicit <Year> nodes and falls back to parsing <MedlineDate>.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None

    year_paths = [
        ".//JournalIssue/PubDate/Year",
        ".//ArticleDate/Year",
        ".//PubmedData/History/PubMedPubDate[@PubStatus='pubmed']/Year",
        ".//PubmedData/History/PubMedPubDate[@PubStatus='entrez']/Year",
        ".//PubmedData/History/PubMedPubDate/Year",
    ]
    for path in year_paths:
        val = (root.findtext(path) or "").strip()
        if not val:
            continue
        try:
            y = int(val)
        except Exception:
            continue
        if 1900 <= y <= 2100:
            return y

    # MedlineDate can look like "2021 Jan-Feb" or "2019"
    medline = (root.findtext(".//JournalIssue/PubDate/MedlineDate") or "").strip()
    if medline:
        m = YEAR_RE.search(medline)
        if m:
            try:
                y = int(m.group(0))
            except Exception:
                y = None
            if y and 1900 <= y <= 2100:
                return y

    return None


US_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}

US_STATE_NAMES = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
    "district of columbia": "DC",
}


def clean_affiliation(aff: str) -> str:
    aff = re.sub(r"\s+", " ", aff).strip()
    aff = re.sub(r"[\s,;]*\b[Ee]-?mail:.*$", "", aff).strip()
    aff = re.sub(r"[\s,;]*\bElectronic address:.*$", "", aff).strip()
    return aff


def guess_place_from_affiliation(aff: str) -> Tuple[str, str, str, str]:
    """
    Returns: department, institution, city, region, country
    Heuristic only; leave blanks when unsure.
    """
    aff = clean_affiliation(aff)
    if not aff:
        return ("", "", "", "", "")

    parts = [p.strip() for p in re.split(r"[;,]", aff) if p.strip()]
    if not parts:
        return ("", "", "", "", "")

    institution_keywords = (
        "university",
        "college",
        "school",
        "hospital",
        "medical center",
        "medical centre",
        "institute",
        "centre",
        "center",
        "clinic",
        "laboratory",
        "laboratories",
        "foundation",
    )

    def looks_like_department(text: str) -> bool:
        t = text.lower()
        return (
            t.startswith("department of ")
            or t.startswith("division of ")
            or t.startswith("dept of ")
            or t.startswith("dept. of ")
            or t.startswith("department ")
            or t.startswith("division ")
        )

    def looks_like_institution(text: str) -> bool:
        t = text.lower()
        return any(k in t for k in institution_keywords)

    department_parts: List[str] = []
    for part in parts[:3]:
        if looks_like_department(part):
            department_parts.append(part)
        else:
            break
    department = " / ".join(department_parts).strip()

    institution = ""
    for part in parts:
        if looks_like_institution(part) and not looks_like_department(part):
            institution = part
            break
    if not institution:
        # fall back to first non-department chunk
        for part in parts:
            if not looks_like_department(part):
                institution = part
                break
    if not institution:
        institution = parts[0]

    tail = parts[-4:] if len(parts) >= 4 else parts
    tail = [re.sub(r"[.]+$", "", t).strip() for t in tail if t.strip()]

    # remove trailing zip/postal code tokens
    if tail and re.fullmatch(r"\d{5}(-\d{4})?", tail[-1]):
        tail = tail[:-1]
    country = ""
    region = ""
    city = ""

    # country heuristics
    last = tail[-1] if tail else ""
    if re.search(r"\b(USA|United States|U\.S\.A\.)\b", last, re.IGNORECASE):
        country = "USA"
    elif re.search(r"\b(UK|United Kingdom)\b", last, re.IGNORECASE):
        country = "United Kingdom"
    elif last.upper() in US_STATES:
        country = "USA"
        region = last.upper()
    elif last.lower() in US_STATE_NAMES:
        country = "USA"
        region = US_STATE_NAMES[last.lower()]
    elif len(last) >= 3 and not re.search(r"@\w+", last):
        country = last

    # US city/region heuristics: "... City, ST, USA"
    if country == "USA" and len(tail) >= 2:
        maybe_region = tail[-2]
        if maybe_region.upper() in US_STATES:
            region = maybe_region.upper()
            if len(tail) >= 3:
                city = tail[-3]
        elif maybe_region.lower() in US_STATE_NAMES:
            region = US_STATE_NAMES[maybe_region.lower()]
            if len(tail) >= 3:
                city = tail[-3]

    if not city and len(tail) >= 2:
        city = tail[-2]

    return (department, institution, city, region, country)


def parse_tags(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    tags = [t.strip().lower() for t in re.split(r"[,;]+", raw) if t.strip()]
    return ";".join(dict.fromkeys(tags))


def nominatim_geocode(
    query: str,
    *,
    email: str,
    tool: str,
    cache: Dict[str, Any],
    sleep_s: float,
    retries: int = 6,
) -> Tuple[Optional[float], Optional[float]]:
    query = query.strip()
    if not query:
        return (None, None)
    if query in cache:
        item = cache[query] or {}
        return (item.get("lat"), item.get("lon"))

    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"format": "json", "q": query, "limit": 1}
    )

    def retry_after_seconds(headers: Any) -> Optional[float]:
        try:
            value = headers.get("Retry-After")
        except Exception:
            value = None
        if not value:
            return None
        try:
            return float(value)
        except Exception:
            return None

    last_error: Optional[Exception] = None
    for attempt in range(retries):
        req = urllib.request.Request(url)
        req.add_header("User-Agent", f"{tool} (mailto:{email})")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = resp.read().decode("utf-8", errors="replace")

            data = json.loads(payload)
            if data and isinstance(data, list):
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                cache[query] = {"lat": lat, "lon": lon, "raw": data[0]}
            else:
                # successful response, but no match
                cache[query] = None
            time.sleep(max(0.0, sleep_s))
            item = cache.get(query) or {}
            return (item.get("lat"), item.get("lon"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            # transient / rate-limit conditions
            if exc.code in (429, 500, 502, 503, 504):
                wait = retry_after_seconds(getattr(exc, "headers", None)) or (2 ** attempt)
                time.sleep(min(60.0, max(1.0, wait)))
                continue
            return (None, None)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            time.sleep(min(60.0, max(1.0, 2 ** attempt)))
            continue

    # If we exhausted retries, don't cache failure so a later run can try again.
    _ = last_error
    return (None, None)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    fieldnames = [
        "name",
        "status",
        "department",
        "institution",
        "institutions",
        "city",
        "region",
        "country",
        "first_year",
        "last_year",
        "lat",
        "lon",
        "link",
        "tags",
        "papers",
        "affiliation",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = {k: row.get(k, "") for k in fieldnames}
            writer.writerow(out)


def read_existing_csv(path: Path) -> Dict[str, Dict[str, str]]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            out: Dict[str, Dict[str, str]] = {}
            for row in reader:
                name = (row.get("name") or "").strip()
                if not name:
                    continue
                out[normalize_name(name)] = {k: (v or "").strip() for k, v in row.items()}
            return out
    except Exception:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build _data/collaborators_map.csv from PubMed using DOIs in _data/citations.yaml."
    )
    parser.add_argument("--email", required=True, help="Contact email for NCBI + Nominatim User-Agent.")
    parser.add_argument("--tool", default="madavid-research-collabmap", help="Tool name for User-Agent.")
    parser.add_argument("--input-citations", default=str(ROOT / "_data" / "citations.yaml"))
    parser.add_argument("--self-member", default=str(ROOT / "_members" / "michael-david.md"))
    parser.add_argument("--output", default=str(ROOT / "_data" / "collaborators_map.csv"))
    parser.add_argument("--default-status", default="current", choices=["current", "past"])
    parser.add_argument("--default-tags", default="collaborator", help="Default tags (e.g. 'collaborator;institution').")
    parser.add_argument("--geocode", action="store_true", help="Geocode inferred locations via Nominatim (network).")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds to sleep between network requests.")
    parser.add_argument("--cache", default=str(ROOT / "tools" / ".cache" / "geocode.json"))
    parser.add_argument("--geocode-retries", type=int, default=6, help="Retries per geocode query.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of DOIs processed (0 = all).")
    parser.add_argument(
        "--no-merge-existing",
        action="store_true",
        help="Do not merge with an existing output CSV (otherwise preserves curated fields like status/tags/link/lat/lon).",
    )
    args = parser.parse_args()

    citations_path = Path(args.input_citations)
    member_path = Path(args.self_member)
    out_path = Path(args.output)
    existing = {} if args.no_merge_existing else read_existing_csv(out_path)

    citations = load_yaml(citations_path) or []
    dois = extract_dois(citations)
    if args.limit and args.limit > 0:
        dois = dois[: args.limit]

    self_names: List[str] = []
    if member_path.exists():
        fm = load_front_matter(member_path) or {}
        if isinstance(fm.get("name"), str):
            self_names.append(fm["name"])
        aliases = fm.get("aliases")
        if isinstance(aliases, list):
            self_names.extend([a for a in aliases if isinstance(a, str)])
    self_names_norm = {normalize_name(n) for n in self_names if n.strip()}

    counts: Dict[str, int] = {}
    aff_counts: Dict[str, Dict[str, int]] = {}
    inst_counts: Dict[str, Dict[str, int]] = {}
    year_ranges: Dict[str, Tuple[int, int]] = {}

    for i, doi in enumerate(dois, start=1):
        pmid = pubmed_doi_to_pmid(doi, email=args.email, tool=args.tool)
        if not pmid:
            continue
        xml_text = pubmed_fetch_xml(pmid, email=args.email, tool=args.tool)
        authors = parse_pubmed_authors(xml_text)
        year = parse_pubmed_year(xml_text)

        for author in authors:
            norm = normalize_name(author.name)
            if not norm or norm in self_names_norm:
                continue
            counts[author.name] = counts.get(author.name, 0) + 1
            for raw_aff in author.affiliations or []:
                aff = clean_affiliation(raw_aff)
                if not aff:
                    continue
                if author.name not in aff_counts:
                    aff_counts[author.name] = {}
                aff_counts[author.name][aff] = aff_counts[author.name].get(aff, 0) + 1

                _dept, inst, _city, _region, _country = guess_place_from_affiliation(aff)
                inst = (inst or "").strip()
                if inst:
                    if author.name not in inst_counts:
                        inst_counts[author.name] = {}
                    inst_counts[author.name][inst] = inst_counts[author.name].get(inst, 0) + 1
            if year:
                cur = year_ranges.get(author.name)
                if not cur:
                    year_ranges[author.name] = (year, year)
                else:
                    year_ranges[author.name] = (min(cur[0], year), max(cur[1], year))

        time.sleep(max(0.0, args.sleep))

    def pick_best_aff(name: str) -> str:
        counts_map = aff_counts.get(name) or {}
        if not counts_map:
            return ""
        # prefer the most frequent affiliation; break ties by longest string
        items = sorted(counts_map.items(), key=lambda kv: (-kv[1], -len(kv[0]), kv[0].lower()))
        return items[0][0]

    def pick_institutions(name: str, limit: int = 6) -> str:
        counts_map = inst_counts.get(name) or {}
        if not counts_map:
            return ""
        items = sorted(counts_map.items(), key=lambda kv: (-kv[1], kv[0].lower()))
        top = [k for (k, _v) in items[:limit] if k.strip()]
        # store as semicolon-separated for CSV readability
        return ";".join(top)

    # optional geocode cache
    cache_path = Path(args.cache)
    cache: Dict[str, Any] = {}
    if args.geocode:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if cache_path.exists():
            try:
                cache = json.loads(read_text(cache_path)) or {}
            except Exception:
                cache = {}

    rows: List[Dict[str, Any]] = []
    geocode_attempted = 0
    geocode_succeeded = 0
    for name, paper_count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower())):
        aff = pick_best_aff(name)
        department, institution, city, region, country = guess_place_from_affiliation(aff)
        institutions = pick_institutions(name)
        y0, y1 = ("", "")
        yr = year_ranges.get(name)
        if yr:
            y0, y1 = yr[0], yr[1]
        lat: Optional[float] = None
        lon: Optional[float] = None
        if args.geocode:
            query_parts = [p for p in [city, region, country] if p]
            query = ", ".join(query_parts) if query_parts else aff
            if query.strip():
                geocode_attempted += 1
            lat, lon = nominatim_geocode(
                query,
                email=args.email,
                tool=args.tool,
                cache=cache,
                sleep_s=args.sleep,
                retries=args.geocode_retries,
            )
            if lat is not None and lon is not None:
                geocode_succeeded += 1

        rows.append(
            {
                "name": name,
                "status": args.default_status,
                "department": department,
                "institution": institution,
                "institutions": institutions,
                "city": city,
                "region": region,
                "country": country,
                "first_year": y0,
                "last_year": y1,
                "lat": "" if lat is None else lat,
                "lon": "" if lon is None else lon,
                "link": "",
                "tags": parse_tags(args.default_tags),
                "papers": paper_count,
                "affiliation": aff,
            }
        )

    # Merge with existing CSV to preserve manual curation.
    if existing:
        preserve_fields = [
            "status",
            "active",
            "tags",
            "link",
            "lat",
            "lon",
            "department",
            "institution",
            "institutions",
            "city",
            "region",
            "country",
        ]
        merged: List[Dict[str, Any]] = []
        for row in rows:
            key = normalize_name(str(row.get("name") or ""))
            prev = existing.get(key)
            if prev:
                for field in preserve_fields:
                    prev_val = (prev.get(field) or "").strip()
                    if prev_val != "":
                        row[field] = prev_val
            merged.append(row)
        rows = merged

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_csv(out_path, rows)

    if args.geocode:
        cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote {out_path} ({len(rows)} rows).")
    if args.geocode:
        print(f"Geocoded {geocode_succeeded}/{geocode_attempted} rows (lat/lon filled).")
    print("Next: edit status/tags and fix any locations/links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
