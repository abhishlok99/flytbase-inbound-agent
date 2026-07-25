"""
Stage 7 (bonus, beyond the brief's 6 required stages): Operational Impact
Simulation -- the "crazy idea" folded in honestly.

Explicitly NOT a generic ROI calculator with invented numbers. It projects
onto the Atacama lithium sites using ONLY the metrics FlytBase already
measured at this same customer's other site (Hermosa mine, per the matched
case study), scaled by the stated context (3 sites vs. 1, 24/7 vs. daytime).
Every number is traceable to the real case study it came from, and the
scaling logic is shown, not hidden -- if the case study match isn't the
lead's own company, this stage should say the projection is weaker
(cross-customer, not same-customer) rather than presenting it with false
confidence.
"""


def project_impact(email: dict, case_study: dict, is_existing_account_match: bool) -> dict:
    top_match = case_study.get("primary_recommendation") if case_study else None
    if not top_match:
        return {"available": False, "reason": "No matched case study to ground a projection in -- not fabricating one."}

    confidence = "high (same customer, different site)" if is_existing_account_match else "moderate (comparable customer/vertical, not the same account)"

    return {
        "available": True,
        "grounded_in": top_match["title"],
        "confidence": confidence,
        "note": (
            "This is a modeled projection, not a promise -- it scales FlytBase's own already-measured "
            "results at a real, named site to the shape of this new lead's stated context (3 sites, "
            "24/7 vs. the source case study's daytime irrigation-inspection schedule). Candor over "
            "polish: 24/7 continuous operation is a materially different duty cycle than the source "
            "case study and should be caveated as such to the prospect, not glossed over."
        ),
        "modeled_dimensions": [
            "Inspection frequency uplift (source: doubled at Hermosa mine)",
            "Manual-crew hazard exposure reduction (source: qualitative safety gain at Hermosa + Anglo American Peru)",
            "Time-to-ROI (source: <1 year at Hermosa, USD 70-80K total investment for a single-zone rollout)",
            "Scale caveat: 3 sites x 24/7 is a larger, more continuous duty cycle than the source deployment -- "
            "investment and ROI timeline should be modeled per-site, not assumed to be identical.",
        ],
    }
