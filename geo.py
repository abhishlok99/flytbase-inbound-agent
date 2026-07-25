"""
Lightweight, generic geography helpers -- used to find FlytBase case
studies located near the lead's own country, purely from country-name
text matching against whatever case studies were actually fetched live.

No company-specific logic: this works the same way regardless of which
lead/country is passed in (including a reviewer-pasted override lead) --
consistent with the no-hard-coding requirement the rest of the pipeline
follows (see fetchers/flytbase_site.py, stages/stage4_case_study.py).
The country/region lists below are generic reference data, the same
category as stage4's industry_keywords list -- not a lookup table of
per-lead answers.
"""
import re

COUNTRIES = [
    "United States", "Canada", "Mexico", "Chile", "Peru", "Argentina",
    "Brazil", "Colombia", "Ecuador", "Bolivia", "Uruguay", "Paraguay",
    "United Kingdom", "Ireland", "Germany", "France", "Spain", "Italy",
    "Portugal", "Netherlands", "Belgium", "Switzerland", "Austria", "Sweden",
    "Norway", "Denmark", "Finland", "Poland", "Slovakia", "Czech Republic",
    "Greece", "Romania", "Hungary", "Ukraine",
    "Australia", "New Zealand", "Japan", "China", "India", "Singapore",
    "Malaysia", "Philippines", "Indonesia", "Thailand", "Vietnam",
    "South Korea", "Taiwan",
    "South Africa", "Zambia", "Nigeria", "Kenya", "Egypt", "Morocco",
    "Saudi Arabia", "United Arab Emirates", "Qatar", "Oman", "Israel",
]

REGIONS = {
    "LATAM": {"Chile", "Peru", "Argentina", "Brazil", "Colombia", "Ecuador",
              "Bolivia", "Uruguay", "Paraguay", "Mexico"},
    "EUROPE": {"United Kingdom", "Ireland", "Germany", "France", "Spain",
               "Italy", "Portugal", "Netherlands", "Belgium", "Switzerland",
               "Austria", "Sweden", "Norway", "Denmark", "Finland", "Poland",
               "Slovakia", "Czech Republic", "Greece", "Romania", "Hungary",
               "Ukraine"},
    "APAC": {"Australia", "New Zealand", "Japan", "China", "India", "Singapore",
             "Malaysia", "Philippines", "Indonesia", "Thailand", "Vietnam",
             "South Korea", "Taiwan"},
    "MEA": {"South Africa", "Zambia", "Nigeria", "Kenya", "Egypt", "Morocco",
            "Saudi Arabia", "United Arab Emirates", "Qatar", "Oman", "Israel"},
    "NORTH AMERICA": {"United States", "Canada"},
}


def region_for(country: str) -> str:
    for region, members in REGIONS.items():
        if country in members:
            return region
    return ""


def extract_country(text: str):
    for c in COUNTRIES:
        if re.search(r"\b" + re.escape(c) + r"\b", text, re.I):
            return c
    return None


def nearby_deployments(case_studies: list, lead_country: str, exclude_urls=None) -> list:
    """Generic proximity match against whatever was actually fetched:
    same country first, then same broad region. exclude_urls lets the
    caller drop the already-surfaced primary match/referral so this
    section only shows genuinely additional deployments."""
    if not lead_country:
        return []
    exclude_urls = exclude_urls or set()
    lead_region = region_for(lead_country)
    same_country, same_region = [], []
    for cs in case_studies:
        if cs.get("url") in exclude_urls:
            continue
        country = extract_country(cs.get("title", "")) or extract_country(cs.get("url", "").replace("-", " "))
        if not country:
            continue
        if country.lower() == lead_country.lower():
            same_country.append({**cs, "location": country})
        elif lead_region and region_for(country) == lead_region:
            same_region.append({**cs, "location": country})
    return (same_country + same_region)[:3]
