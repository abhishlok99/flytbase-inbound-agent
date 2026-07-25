"""
Orchestrates all 7 stages end-to-end for the fixed input lead. Each stage
is a separate, independently callable module (see stages/) with structured
input/output -- this file only wires them together and does live fetching;
it contains zero business logic of its own, so the delegation is visible
by reading the file, not just by looking at a diagram.
"""
import json
import traceback

from fetchers import edgar, news, flytbase_site
from stages import (stage1_qualification, stage2_research, stage3_response,
                     stage4_case_study, stage5_partner, stage6_handoff, stage7_simulation)


def run_pipeline(email: dict) -> dict:
    log = []

    def step(name, fn, *args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            log.append({"stage": name, "status": "ok"})
            return result
        except Exception as e:
            log.append({"stage": name, "status": "error", "detail": str(e), "trace": traceback.format_exc(limit=2)})
            return None

    # --- Stage 1 (no external dependency) ---
    qualification = step("1_qualification", stage1_qualification.qualify, email)

    # --- live fetches (real network calls; degrade gracefully if unreachable) ---
    case_studies = step("fetch_case_studies", flytbase_site.fetch_case_studies) or []
    edgar_hits = step("fetch_edgar", edgar.full_text_search, email.get("company", "")) or []
    news_items = step("fetch_news", news.search_news, f"{email.get('company','')} lithium Atacama") or []

    # --- Stage 4 (needs live case studies) ---
    case_study_match = step("4_case_study_match", stage4_case_study.match_case_studies, email, case_studies) or {
        "top_matches": [], "primary_recommendation": None, "search_terms_used": {}
    }
    top_match = case_study_match.get("primary_recommendation")
    is_existing_account = bool(top_match and top_match.get("match_score", 0) >= 50)

    # --- Stage 2 ---
    research = step("2_research", stage2_research.build_research_brief,
                     email, edgar_hits, news_items, top_match) or {}

    # --- Stage 3 ---
    response_seq = step("3_response", stage3_response.generate_sequence, email, qualification, research) or {}

    # --- Stage 5 (fetch the matched case study's own full text for partner signal) ---
    matched_full_text = ""
    if top_match:
        try:
            import requests
            r = requests.get(top_match["url"], headers=flytbase_site.HEADERS, timeout=20)
            matched_full_text = r.text
        except Exception:
            matched_full_text = ""
    partner = step("5_partner", stage5_partner.recommend_motion,
                    email, top_match, matched_full_text, is_existing_account) or {}

    # --- Stage 6 ---
    handoff = step("6_handoff", stage6_handoff.build_handoff,
                    email, qualification, research, case_study_match, partner) or {}

    # --- Stage 7 (bonus) ---
    simulation = step("7_simulation", stage7_simulation.project_impact,
                       email, case_study_match, is_existing_account) or {}

    return {
        "input_email": email,
        "run_log": log,
        "stage1_qualification": qualification,
        "stage2_research": research,
        "stage3_response": response_seq,
        "stage4_case_study": case_study_match,
        "stage5_partner": partner,
        "stage6_handoff": handoff,
        "stage7_simulation": simulation,
    }


if __name__ == "__main__":
    email = json.load(open("input/lead_email.json"))
    result = run_pipeline(email)
    print(json.dumps(result, indent=2, default=str))
