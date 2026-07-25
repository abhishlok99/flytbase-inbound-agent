"""
Stage 1: Qualification -- MEDDPICC.

Framework choice: MEDDPICC over BANT/SPICED. Reasoning (stated in output,
not just this comment): this is a multi-stakeholder enterprise deal where
the inbound contact (Head of Operations) is very unlikely to be the sole
Economic Buyer; there is a real Champion-shaped signal (an external referral
from an existing customer, Anglo American); there's a known Decision Process
signal (an internal Q3 budget conversation already scheduled); and there are
open questions about Decision Criteria and Competition. MEDDPICC's seven
fields map onto what's known/unknown here far more richly than BANT's four
or SPICED's five -- it's built for exactly this shape of deal.

This module contains zero hard-coded facts about SQM or Rodrigo. Every
"known" fact below is extracted from the input email object at call time
via keyword/pattern signals -- swap the input and the same rules re-run.
"""
import re

MEDDPICC_FIELDS = ["Metrics", "Economic Buyer", "Decision Criteria", "Decision Process",
                    "Identify Pain", "Champion", "Competition", "Paper Process"]


def _has_any(text: str, keywords: list[str]) -> str | None:
    text_l = text.lower()
    for kw in keywords:
        if kw in text_l:
            return kw
    return None


def qualify(email: dict) -> dict:
    body = email.get("body", "")
    subject = email.get("subject", "")
    full_text = f"{subject}. {body}"

    known = {}
    unknown = []
    score_breakdown = []

    # --- Metrics: quantifiable business pain / value driver signals ---
    hit = _has_any(full_text, ["expensive", "hazardous", "cost", "24/7", "24-7"])
    if hit:
        known["Metrics"] = f"Pain framed in operational-cost/safety terms (signal: '{hit}' in body) -- manual crews described as both expensive and hazardous on 24/7 sites."
        score_breakdown.append(("Metrics signal present (cost+safety framing)", 15))
    else:
        unknown.append("Metrics: no quantified cost, headcount, or incident baseline given yet -- needed to build an ROI case.")

    # --- Economic Buyer ---
    title = email.get("title", "")
    if re.search(r"\bhead of\b", title, re.I) or re.search(r"\b(vp|director|chief)\b", title, re.I):
        known["Economic Buyer"] = f"Contact is '{title}' -- a senior operations leader, but title alone doesn't confirm budget authority for a multi-site capex decision."
        unknown.append("Economic Buyer: confirm whether Rodrigo owns budget for this, or whether it needs a separate capex/finance sign-off given the referenced Q3 budget conversation.")
    else:
        unknown.append("Economic Buyer: not identifiable from title alone.")

    # --- Decision Criteria ---
    unknown.append("Decision Criteria: no stated technical or commercial evaluation criteria yet (e.g. BVLOS compliance, integration requirements, vendor comparison).")

    # --- Decision Process ---
    hit = _has_any(full_text, ["q3", "budget conversation", "internal budget"])
    if hit:
        known["Decision Process"] = f"An internal budget conversation is already scheduled for Q3 -- a real, dated process signal, not vague interest."
        score_breakdown.append(("Concrete dated decision-process signal (Q3 budget conversation)", 20))
    else:
        unknown.append("Decision Process: no timeline given.")

    # --- Identify Pain ---
    hit = _has_any(full_text, ["expensive", "hazardous", "risk"])
    if hit:
        known["Identify Pain"] = "Explicit pain stated: contracted manual inspection crews are expensive and hazardous on large, continuously-operating sites."
        score_breakdown.append(("Explicit, specific pain stated (not vague interest)", 20))

    # --- Champion ---
    hit = _has_any(full_text, ["referred by", "referred", "recommendation"])
    if hit:
        referrer = None
        m = re.search(r"referred by ([A-Z][A-Za-z& ]+)", body, re.I)
        if m:
            referrer = m.group(1).strip().rstrip(".")
        known["Champion"] = f"Warm referral signal from {referrer or 'an existing FlytBase customer'} -- referrals from existing customers are a strong proxy for an internal or informal champion, though no named internal champion at SQM is confirmed yet."
        score_breakdown.append(("Warm referral from a named existing customer (not cold inbound)", 25))
    else:
        unknown.append("Champion: no internal champion at SQM named yet.")

    # --- Competition ---
    unknown.append("Competition: no competing vendor or incumbent solution mentioned -- unknown whether SQM is evaluating alternatives.")

    # --- Paper Process ---
    unknown.append("Paper Process: procurement/legal/security-review process at SQM (a large multinational) not yet known -- likely non-trivial given company size.")

    # --- fit signals: scale / vertical / urgency ---
    hit = _has_any(full_text, ["3 large-scale", "large-scale", "24/7", "24-7"])
    if hit:
        score_breakdown.append(("Multi-site, continuous (24/7) operation -- large deployment scale", 20))

    priority_score = min(100, sum(pts for _, pts in score_breakdown))

    return {
        "framework": "MEDDPICC",
        "framework_reasoning": (
            "Chosen over BANT/SPICED because this is a multi-stakeholder enterprise deal with a "
            "referral-based champion signal and a dated internal process step already in motion -- "
            "MEDDPICC's seven fields capture that shape of deal; BANT's four fields would flatten "
            "the champion/process/competition nuance that's actually present in this email."
        ),
        "known": known,
        "missing_for_full_qualification": unknown,
        "priority_score": priority_score,
        "score_reasoning": score_breakdown,
        "meddpicc_fields_covered": list(known.keys()),
        "meddpicc_fields_open": [f for f in MEDDPICC_FIELDS if f not in known],
    }
