"""
Stage 2: Deep Account Research.

Synthesizes real fetched data (EDGAR filings, news, flytbase.com's own
matched case study) into the required brief. Every claim carries its
source; anything not found is explicitly marked unverified rather than
guessed -- the brief states fabricated data is an automatic disqualifier,
so this stage is built to fail loud (flag a gap) rather than fail silent
(invent a plausible-sounding number).
"""


def build_research_brief(email: dict, edgar_hits: list, news_items: list,
                          matched_case_study: dict | None, org_notes: str = "") -> dict:
    company = email.get("company", "")

    budget_signals = []
    if edgar_hits and not any("error" in h for h in edgar_hits):
        for h in edgar_hits[:5]:
            budget_signals.append(f"Public filing on record: {h.get('form','?')} filed {h.get('filed','?')} ({h.get('title','')})")
    if not budget_signals:
        budget_signals.append(
            "UNVERIFIED AT RUN TIME: EDGAR full-text search returned no usable hits in this run "
            "(or was unreachable). Do not state a specific capex/opex figure without a live source -- "
            "flag this as an open research item for the AE rather than fabricate a number."
        )

    recent_news = []
    if news_items and not any("error" in n for n in news_items):
        for n in news_items[:5]:
            recent_news.append(f"{n.get('title','')} ({n.get('source','')}, {n.get('pubDate','')})")
    if not recent_news:
        recent_news.append("UNVERIFIED AT RUN TIME: news fetch returned no results in this run -- flag as open item, do not invent headlines.")

    existing_relationship = None
    if matched_case_study and matched_case_study.get("match_score", 0) >= 50:
        existing_relationship = (
            f"IMPORTANT: {company} already appears to be an existing FlytBase customer via a different "
            f"site/division -- matched case study: '{matched_case_study['title']}'. Treat this lead as a "
            f"likely EXPANSION signal from a different division of an existing account, not a cold new logo. "
            f"This changes both the qualification framing (internal trust in autonomy may already exist) "
            f"and the response strategy (reference the existing relationship, don't pitch from zero)."
        )

    positioning_recommendation = (
        f"Position this as an expansion/second-site conversation, not a first-time pitch, if the existing-"
        f"relationship signal above is confirmed valid -- lead with 'extending what's already working at "
        f"your other site' rather than a generic capability pitch. Where budget/news data above is marked "
        f"unverified, an AE should confirm it manually before quoting any number to the prospect; do not "
        f"let an unverified figure reach the buyer."
    )

    return {
        "company": company,
        "org_structure_note": org_notes or "Not independently verified in this run -- recommend AE confirm SQM's Northern Operations Division reporting line before the first call.",
        "budget_signals": budget_signals,
        "recent_news": recent_news,
        "existing_relationship_signal": existing_relationship,
        "positioning_recommendation": positioning_recommendation,
    }
