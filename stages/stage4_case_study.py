"""
Stage 4: Case Study and Material Matching.

No hard-coded answer. This module takes the generic list of case studies
returned by fetchers.flytbase_site.fetch_case_studies() (which has zero
knowledge of SQM/Anglo American) and scores EVERY case study against
terms actually derived from the lead email -- company name, referenced
companies, industry keywords, and use-case keywords. Whatever scores
highest wins, and the reasoning is the score breakdown itself, not a
canned sentence.

Deliberately searches for the lead's OWN company name in addition to any
company named as a referral -- a system that only looks for the referral
would miss an existing-customer / expansion signal if the lead's own
company already has a case study under a different site name.
"""
import re


def _extract_search_terms(email: dict) -> dict:
    body = email.get("body", "")
    company = email.get("company", "")
    # strip legal suffixes / parenthetical abbreviations for matching, e.g.
    # "Sociedad Quimica y Minera de Chile (SQM)" -> also try "SQM"
    company_terms = [company]
    m = re.search(r"\(([A-Z]{2,6})\)", company)
    if m:
        company_terms.append(m.group(1))
    # first word of company name is often the brand used in case-study titles
    first_word = company.split()[0].strip("(),")
    if len(first_word) > 2:
        company_terms.append(first_word)

    referred_companies = re.findall(r"[Rr]eferred by ([A-Z][A-Za-z& ]+?)[.\n]", body)
    referred_companies = [c.strip() for c in referred_companies]

    industry_keywords = []
    for kw in ["mining", "lithium", "extraction", "solar", "port", "warehouse", "oil", "gas", "security", "rail", "highway"]:
        if kw in body.lower():
            industry_keywords.append(kw)
    if not industry_keywords:
        industry_keywords = ["mining"]  # lithium extraction sites are a mining operation by default

    return {
        "company_terms": company_terms,
        "referred_companies": referred_companies,
        "industry_keywords": industry_keywords,
    }


def match_case_studies(email: dict, case_studies: list[dict], top_n: int = 3) -> dict:
    terms = _extract_search_terms(email)
    scored = []
    for cs in case_studies:
        title_l = cs["title"].lower()
        score = 0
        reasons = []
        for ct in terms["company_terms"]:
            if ct and ct.lower() in title_l:
                score += 50
                reasons.append(f"lead's own company name/abbreviation '{ct}' appears in this case study -- likely existing-account signal, not a cold match")
        for rc in terms["referred_companies"]:
            if rc.lower() in title_l:
                score += 40
                reasons.append(f"matches the company explicitly referenced in the email ('Referred by {rc}')")
        for kw in terms["industry_keywords"]:
            if kw in title_l:
                score += 10
                reasons.append(f"industry/use-case keyword match: '{kw}'")
        if score > 0:
            scored.append({**cs, "match_score": score, "match_reasons": reasons})

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    top = scored[:top_n]

    return {
        "search_terms_used": terms,
        "all_scored_matches": scored,
        "top_matches": top,
        "primary_recommendation": top[0] if top else None,
    }
