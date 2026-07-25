"""
Stage 5: Partner Identification for the LATAM go-to-market motion.

Reuses whatever the Stage-4 case-study match surfaced (rather than a second
hard-coded lookup) -- if the best-matching case study for this lead's region
was executed with a named regional partner, that's real, load-bearing
precedent for a partner-led recommendation. If nothing partner-related turns
up, the system says so and defaults to direct AE engagement rather than
inventing a partner.
"""
import re


PARTNER_SIGNAL_PATTERNS = [
    r"partner(?:ing|ed) with ([A-Z][A-Za-z0-9]+)",
    r"in collaboration with ([A-Z][A-Za-z0-9]+)",
    r"partnership with ([A-Z][A-Za-z0-9]+)",
    r"(?:implementation partner|integrator),? ([A-Z][A-Za-z0-9]+)",
    r"led them to ([A-Z][A-Za-z0-9]+), a[n]? [A-Za-z\- ]+ integrator",
]


def recommend_motion(email: dict, case_study_match: dict, case_study_full_text: str = "", is_existing_account_match: bool = False) -> dict:
    country = email.get("country", "")
    region = "LATAM" if country.lower() in ("chile", "peru", "brazil", "argentina", "colombia", "mexico") else country

    partner_name = None
    for pattern in PARTNER_SIGNAL_PATTERNS:
        m = re.search(pattern, case_study_full_text)
        if m:
            partner_name = m.group(1).strip()
            break

    if partner_name and is_existing_account_match:
        motion = "partner-led (continuity)"
        justification = (
            f"The matched case study is this SAME lead's own existing site, already delivered with "
            f"'{partner_name}' as the on-the-ground implementation partner. This is a stronger, more "
            f"specific signal than a generic regional partner -- '{partner_name}' already has a working "
            f"relationship and technical trust with this exact account. Recommend continuity with "
            f"'{partner_name}' for the new sites rather than introducing a different regional partner, "
            f"unless '{partner_name}' lacks coverage in the new sites' specific location."
        )
    elif partner_name:
        motion = "partner-led"
        justification = (
            f"The best-matching case study for this region was itself executed with a named regional "
            f"partner ('{partner_name}') -- real precedent that FlytBase already routes {region} mining "
            f"deployments through a regional partner rather than direct AE delivery. Recommend engaging "
            f"the same partner motion for consistency and faster mobilization on the ground in {country}."
        )
    else:
        motion = "direct AE engagement, with partner-fit review"
        justification = (
            f"No regional partner signal was found in the matched case study text for {region}/{country}. "
            f"Defaulting to direct AE engagement rather than inventing a partner -- an AE should manually "
            f"check FlytBase's partner directory for {region} before the first call, since deal complexity "
            f"(3 concurrent sites, referral-sourced) may still justify a partner for on-ground deployment "
            f"even without a documented precedent."
        )

    return {
        "region": region,
        "recommended_motion": motion,
        "partner_identified": partner_name,
        "justification": justification,
    }
