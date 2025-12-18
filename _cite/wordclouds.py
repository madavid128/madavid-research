#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Michael A. David

from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from util import cache, log_cache
from util import save_data


ROOT = Path(__file__).resolve().parents[1]

NCBI_TOOL = "madavid-research-wordcloud"
NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "").strip()
NCBI_MIN_INTERVAL = float(os.environ.get("NCBI_MIN_INTERVAL", "0.34"))

_last_ncbi_request_s = 0.0


DEFAULT_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "based",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "our",
    "study",
    "the",
    "their",
    "to",
    "toward",
    "using",
    "via",
    "with",
}


def iter_phrases(citations: Iterable[Dict[str, Any]]) -> List[str]:
    phrases: List[str] = []

    for c in citations or []:
        if not isinstance(c, dict):
            continue
        title = str(c.get("title") or "").strip()
        if title:
            phrases.append(title)
        keywords = c.get("keywords")
        if isinstance(keywords, list):
            phrases.extend([str(k).strip() for k in keywords if str(k).strip()])
        elif isinstance(keywords, str) and keywords.strip():
            phrases.append(keywords.strip())

    return phrases


def build_text(citations: Iterable[Dict[str, Any]]) -> str:
    phrases = iter_phrases(citations)
    # keep letters, numbers, and hyphenated words
    cleaned = []
    for phrase in phrases:
        phrase = re.sub(r"[^\w\s\-]", " ", phrase, flags=re.UNICODE)
        phrase = re.sub(r"\s+", " ", phrase).strip()
        if phrase:
            cleaned.append(phrase)
    return "\n".join(cleaned)

def extract_id_parts(raw_id: str) -> Tuple[str, str]:
    raw_id = (raw_id or "").strip()
    if ":" not in raw_id:
        return ("", "")
    prefix, value = raw_id.split(":", 1)
    return (prefix.strip().lower(), value.strip())


def _ncbi_request(url: str) -> str:
    global _last_ncbi_request_s
    now = time.time()
    wait_s = (_last_ncbi_request_s + NCBI_MIN_INTERVAL) - now
    if wait_s > 0:
        time.sleep(wait_s)
    req = Request(url=url, headers={"User-Agent": NCBI_TOOL})
    with urlopen(req, timeout=30) as resp:
        _last_ncbi_request_s = time.time()
        return resp.read().decode("utf-8", errors="replace")


@log_cache
@cache.memoize(name=__file__ + ":doi_to_pmid", expire=30 * (60 * 60 * 24))
def doi_to_pmid(doi: str) -> str:
    term = f"{doi}[AID]"
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urlencode(
        {
            "db": "pubmed",
            "term": term,
            "retmode": "json",
            "retmax": 1,
            "tool": NCBI_TOOL,
            **({"email": NCBI_EMAIL} if NCBI_EMAIL else {}),
        }
    )
    raw = _ncbi_request(url)
    data = json.loads(raw)
    ids = data.get("esearchresult", {}).get("idlist", [])
    return str(ids[0]) if ids else ""


@log_cache
@cache.memoize(name=__file__ + ":pmid_xml", expire=30 * (60 * 60 * 24))
def pmid_to_xml(pmid: str) -> str:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urlencode(
        {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "tool": NCBI_TOOL,
            **({"email": NCBI_EMAIL} if NCBI_EMAIL else {}),
        }
    )
    return _ncbi_request(url)


def safe_pubmed_terms(citation: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Returns (mesh_terms, keywords) best-effort.
    Never raises.
    """
    try:
        raw_id = str(citation.get("id") or "")
        prefix, value = extract_id_parts(raw_id)

        pmid = ""
        if prefix == "pubmed":
            pmid = value
        elif prefix == "doi":
            pmid = doi_to_pmid(value)
        if not pmid:
            return ([], [])

        xml_text = pmid_to_xml(pmid)
        if not xml_text:
            return ([], [])

        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_text)
        mesh = []
        for desc in root.findall(".//MeshHeadingList/MeshHeading/DescriptorName"):
            if desc.text:
                mesh.append(desc.text.strip())
        keywords = []
        for kw in root.findall(".//KeywordList/Keyword"):
            if kw.text:
                keywords.append(kw.text.strip())
        return (mesh, keywords)
    except Exception:
        return ([], [])


def tokens_from_terms(terms: Iterable[str]) -> List[str]:
    tokens: List[str] = []
    for term in terms or []:
        term = re.sub(r"[^\w\s\-]", " ", str(term), flags=re.UNICODE)
        term = re.sub(r"\s+", " ", term).strip().lower()
        if not term:
            continue
        for token in term.split(" "):
            token = token.strip("-_")
            if not token:
                continue
            tokens.append(token)
    return tokens


def build_frequencies(citations: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Frequency map for wordcloud. Prefer PubMed MeSH/keywords when available.
    """
    counts: Dict[str, int] = {}

    for c in citations or []:
        mesh, keywords = safe_pubmed_terms(c)
        # weight MeSH terms a bit higher than free keywords
        for t in tokens_from_terms(mesh):
            counts[t] = counts.get(t, 0) + 3
        for t in tokens_from_terms(keywords):
            counts[t] = counts.get(t, 0) + 2

    if counts:
        return counts

    # fallback: titles/keywords embedded in citations.yaml
    text = build_text(citations)
    for t in tokens_from_terms([text]):
        counts[t] = counts.get(t, 0) + 1
    return counts


def green_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # deterministic-ish palette around a teal/green hue
    rnd = random_state or random
    hue = rnd.randint(150, 170)
    sat = rnd.randint(55, 85)
    light = rnd.randint(45, 72)
    return f"hsl({hue}, {sat}%, {light}%)"


def generate_publications_wordcloud(citations: List[Dict[str, Any]], out_path: Path) -> bool:
    try:
        from wordcloud import WordCloud, STOPWORDS  # type: ignore
    except Exception:
        return False

    stopwords = set(STOPWORDS) | set(DEFAULT_STOPWORDS)

    frequencies = build_frequencies(citations)
    if not frequencies:
        return False

    wc = WordCloud(
        width=1800,
        height=900,
        background_color=None,
        mode="RGBA",
        prefer_horizontal=0.92,
        max_words=150,
        stopwords=stopwords,
        random_state=7,
        min_font_size=10,
        max_font_size=140,
        collocations=True,
    ).generate_from_frequencies(frequencies)

    wc.recolor(color_func=green_color_func, random_state=random.Random(7))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wc.to_file(str(out_path))
    return True


def generate_all(citations: List[Dict[str, Any]]) -> List[str]:
    """
    Returns a list of generated file paths (as strings).
    Never raises; caller can log failures separately.
    """
    generated: List[str] = []
    out = ROOT / "images" / "publications-wordcloud.png"
    if generate_publications_wordcloud(citations, out):
        generated.append(str(out))

    try:
        frequencies = build_frequencies(citations)
        top = sorted(frequencies.items(), key=lambda kv: (-kv[1], kv[0]))[:24]
        terms = [{"term": k, "count": int(v)} for k, v in top if k and v]
        save_data(ROOT / "_data" / "publications_terms.yaml", terms)
        generated.append(str(ROOT / "_data" / "publications_terms.yaml"))
    except Exception:
        pass
    return generated
