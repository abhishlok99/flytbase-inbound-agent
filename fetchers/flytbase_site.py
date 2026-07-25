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
    # de-dupe by url
    seen = set()
    deduped = []
    for s in studies:
        if s["url"] not in seen:
            seen.add(s["url"])
            deduped.append(s)
    return deduped


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
