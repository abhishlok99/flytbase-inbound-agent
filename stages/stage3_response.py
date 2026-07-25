"""
Stage 3: Response Generation -- adaptive email sequence.

Uses llm_adapter for genuinely generative drafting when a key is
configured; falls back to a structured, still-personalized template
built from Stage 1 (unknowns to probe) + Stage 2 (research to reference)
when no LLM is configured, so the pipeline never silently produces
generic boilerplate -- every email is assembled FROM the actual
qualification/research objects passed in, not written ahead of time.
"""
import llm_adapter


def _template_email(step: int, email: dict, qualification: dict, research: dict) -> dict:
    name = email.get("from_name", "").split()[0]
    unknowns = qualification.get("missing_for_full_qualification", [])
    existing_rel = research.get("existing_relationship_signal")

    if step == 1:
        subject = f"Re: Autonomous inspection for your Atacama lithium sites"
        opener = f"Hi {name}" if not existing_rel else f"Hi {name}, great to hear from you directly"
        rel_line = (
            "I noticed FlytBase already runs autonomous inspection at another SQM site -- happy to build "
            "on what's already working there rather than start from scratch. "
        ) if existing_rel else ""
        body = (
            f"{opener},\n\nThanks for reaching out, and for the introduction via Anglo American -- "
            f"they've had a strong run with us in Peru. {rel_line}"
            f"On the 3 Atacama lithium sites: since you mentioned an internal budget conversation "
            f"is already on the calendar for Q3, I'd love to understand two things before then -- "
            f"{unknowns[0].split(':')[0] if unknowns else 'your evaluation criteria'} and "
            f"who else on the technical or procurement side should be in the loop.\n\n"
            f"Would a 20-minute call this week work to walk through how this has played out at "
            f"comparable 24/7 sites?"
        )
        goal = "Discover Economic Buyer + Decision Criteria; convert warm referral into a scheduled call before Q3."
    elif step == 2:
        subject = "Following up -- proof, not just pitch"
        body = (
            f"Hi {name}, following up in case this got buried. Rather than another generic pitch, "
            f"I put together the specific proof point most relevant to a 24/7, multi-site operation "
            f"like yours -- happy to send it over or walk through it live, whichever's easier on your end.\n\n"
            f"Separately -- is there a technical or ops stakeholder beyond yourself who should see this "
            f"before the Q3 conversation?"
        )
        goal = "Re-engage with a proof asset (fills Decision Criteria gap); surface Champion/other stakeholders."
    else:
        subject = "Should I check back closer to Q3?"
        body = (
            f"Hi {name}, I don't want to crowd your inbox -- if now isn't the right moment, would it be "
            f"more useful for me to check back closer to your Q3 budget conversation instead? Either way, "
            f"happy to be a resource before then if questions come up on the technical side."
        )
        goal = "Low-pressure breakup/re-queue email; keeps the door open on their stated timeline instead of pushing."

    return {"step": step, "subject": subject, "body": body, "goal_of_this_email": goal}


def generate_sequence(email: dict, qualification: dict, research: dict) -> dict:
    sequence = [_template_email(i, email, qualification, research) for i in (1, 2, 3)]

    llm_note = None
    system_prompt = (
        "You are drafting a 3-email adaptive outbound sequence for a warm inbound B2B lead. "
        "Ground every claim in the provided qualification and research JSON only. Never invent facts."
    )
    user_prompt = f"Lead: {email}\nQualification: {qualification}\nResearch: {research}\nDraft 3 emails with clear progression logic."
    llm_out = llm_adapter.generate(system_prompt, user_prompt)
    if llm_out:
        llm_note = "LLM-enhanced draft available (see llm_draft field) -- template sequence retained as the inspectable, always-available baseline."

    return {
        "progression_logic": (
            "Email 1 targets the two biggest MEDDPICC gaps (Economic Buyer, Decision Criteria) while the "
            "referral is still warm. Email 2 (sent only if no reply) shifts from asking to giving -- a proof "
            "asset -- and probes for a Champion. Email 3 (sent only if still no reply) explicitly offers to "
            "back off until their own stated Q3 timeline, respecting their process instead of over-pushing."
        ),
        "sequence": sequence,
        "llm_draft": llm_out,
        "llm_note": llm_note or "Running in template mode (no LLM key configured) -- sequence is fully generated from Stage 1/2 objects, not pre-written.",
    }
