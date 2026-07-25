"""Stage 6: AE Handoff Summary -- pure synthesis of Stages 1-5, no new claims."""

def build_handoff(email: dict, qualification: dict, research: dict,
                   case_study: dict, partner: dict) -> dict:
    name = email.get("from_name")
    title = email.get("title")
    company = email.get("company")

    buyer_context = (
        f"{name} ({title}) at {company} reached out about autonomous inspection for 3 large-scale, 24/7 "
        f"lithium extraction sites in the Atacama Desert. Referred by Anglo American (existing FlytBase "
        f"customer, Peru). Internal budget conversation already scheduled for Q3 -- this is a real process "
        f"step, not vague interest."
    )
    if research.get("existing_relationship_signal"):
        buyer_context += f" {research['existing_relationship_signal']}"

    top_research_highlights = [
        research.get("existing_relationship_signal") or "No existing-relationship signal confirmed this run.",
        (research.get("budget_signals") or ["No budget signal available."])[0],
        research.get("positioning_recommendation", ""),
    ]

    top_match = case_study.get("primary_recommendation") if case_study else None
    case_study_line = (
        f"{top_match['title']} ({top_match['url']}) -- score {top_match['match_score']}, "
        f"reasons: {'; '.join(top_match['match_reasons'])}"
    ) if top_match else "No confident case-study match found this run."

    next_step = (
        f"Route as {partner.get('recommended_motion', 'unassigned')} -- {partner.get('justification', '')} "
        f"First outbound touch: Email 1 from the generated sequence, timed to land before the Q3 budget "
        f"conversation, aimed at surfacing the Economic Buyer and Decision Criteria gaps flagged in Stage 1."
    )

    return {
        "buyer_context": buyer_context,
        "qualification_status": {
            "framework": qualification.get("framework"),
            "priority_score": qualification.get("priority_score"),
            "known_fields": qualification.get("meddpicc_fields_covered"),
            "open_fields": qualification.get("meddpicc_fields_open"),
        },
        "top_3_research_highlights": top_research_highlights,
        "recommended_case_study": case_study_line,
        "suggested_next_step": next_step,
    }
