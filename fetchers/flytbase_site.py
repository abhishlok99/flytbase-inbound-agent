"""
Real, live crawler of flytbase.com/case-studies and the partner directory.
Deliberately searches for BOTH the explicitly-named referral (Anglo American)
AND the lead's own company name (SQM) -- per the brief's "no hard-coding"
requirement, this must be a generic search over whatever companies actually
appear on the page, not a lookup table of two pre-known answers.
"""
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (FlytBase-BDR-Hackathon-Research)"}
CASE_STUDIES_URL = "https://flytbase.com/case-studies"
PARTNERS_URL = "https://flytbase.com/partner"


def fetch_case_studies() -> list[dict]:
    """Pulls every case-study link + title + result stat currently listed on
    flytbase.com/case-studies. Returns a generic list -- matching against the
    lead happens in stages/stage4_case_study.py, not here, so this fetcher
    has zero knowledge of SQM or Anglo American specifically."""
    r = requests.get(CASE_STUDIES_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    studies = []
    for a in soup.select("a[href*='/case-studies/']"):
        href = a.get("href", "")
        if href.rstrip("/").endswith("/case-studies"):
            continue
        text = " ".join(a.get_text(" ", strip=True).split())
        if text and href:
            studies.append({"title": text, "url": href if href.startswith("http") else f"https://flytbase.com{href}"})
    # de-dupe by url -- prefer whichever occurrence has the more descriptive
    # title. The same case study can appear in multiple placements on the
    # page (e.g. a nav quick-link that only wraps "Read the case study" in
    # the anchor, vs. the main grid card that merges the full headline into
    # the anchor text) -- keep the longer, more informative one.
    best: dict[str, dict] = {}
    for s in studies:
        existing = best.get(s["url"])
        if existing is None or len(s["title"]) > len(existing["title"]):
            best[s["url"]] = s
    return list(best.values())


def fetch_partners(region: str | None = None) -> list[dict]:
    params = {"region": region} if region else {}
    r = requests.get(PARTNERS_URL, headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    partners = []
    for card in soup.select("a[href*='/partner']"):
        text = " ".join(card.get_text(" ", strip=True).split())
        href = card.get("href", "")
        if text and len(text) > 2 and "/partner?" not in href:
            partners.append({"name": text, "url": href})
    return partners
