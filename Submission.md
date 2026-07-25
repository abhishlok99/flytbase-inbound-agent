# Submission.md — FlytBase Inbound BDR Agent

> Note: the eval platform's submission form provides its own prompt to generate the final Submission.md against the actual codebase — run that prompt before submitting and let it supersede this draft. This version exists so a complete, accurate scaffold is ready ahead of time, not written after the fact.

## What was built

A 7-stage inbound-lead processing pipeline (6 required by the brief + 1 bonus) that takes the fixed test email (Rodrigo Castillo, SQM, Atacama lithium sites, referred by Anglo American) and produces, live, on every run: a MEDDPICC qualification with a priority score, a real-data account research brief, a 3-email adaptive response sequence, a case-study match against flytbase.com's actual current case studies, a partner/GTM recommendation, an AE handoff summary, and a bonus operational-impact projection with an animated SVG site-patrol visualization (no external libraries/CDN, so it never breaks a live demo) -- the visual renders only when Stage 7 has a real grounded case study to base it on; it never animates an ungrounded claim.

## Why this architecture

Delegated across independently callable, typed stages (`stages/stage1_...py` through `stage7_...py`) orchestrated by a single thin `orchestrator.py`, rather than one large prompt. Each stage can be tested and inspected on its own — see `mindmap.html` for the full flow and the two real decision points (existing-account detection, partner continuity).

## Framework choice: MEDDPICC

Chosen over BANT/SPICED because this is a multi-stakeholder enterprise deal with a referral-shaped Champion signal, a dated Decision Process step (Q3 budget conversation), and open Decision Criteria/Competition questions — MEDDPICC's seven fields fit this deal's actual shape; BANT's four fields would flatten it. Full reasoning is generated live in Stage 1's output, not hard-coded here.

## The single most important finding

Stage 4 deliberately searches for the lead's own company name, not just the explicitly-named referral. Doing so surfaces a real, verified fact: SQM already has a live FlytBase case study (a different mine, the "Hermosa" site, via partner Adentu — 2x inspection frequency, 95%+ mission reliability, 0.5%→2% extraction-yield gain, <1yr ROI). This reframes the lead from a cold new-logo to a likely internal expansion signal, which changes the qualification framing, the response strategy, and (via Stage 5) the partner recommendation — continuity with Adentu (same customer, Chile-based) rather than defaulting to a generic regional partner.

## Research quality / anti-fabrication

Every fact in Stage 2's output is traced to a live fetch (SEC EDGAR full-text search, Google News RSS, flytbase.com's own case-study pages — all free and keyless, deliberately, so research quality never depends on paid tool access). Anything not found at run time is explicitly marked `UNVERIFIED AT RUN TIME` rather than filled with a plausible-sounding guess.

## Known limitations (candor over polish)

- flytbase.com's per-case-study numeric result badges (e.g. "Reduced Travel Time") are client-side rendered and not reliably extractable via a static fetch — the system does not claim a specific percentage it cannot verify from source; an AE should confirm exact figures from the live page before quoting them.
- The Stage 3 email sequence runs in structured-template mode unless an LLM API key is configured (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GOOGLE_API_KEY` / `GROQ_API_KEY`) — the template mode is real logic assembled from Stage 1/2 output, not pre-written copy, but a configured LLM key produces more naturally adaptive prose.
- Live fetches (EDGAR/News/flytbase.com) require outbound network access from wherever this is deployed; a restricted network environment will cause those stages to degrade gracefully (flagged, not fabricated) rather than fail the whole run.

## How to run

```
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
Open `/` for the rendered run, `/run.json` for raw output, `/health` for a liveness check.

## Deliverables checklist

- [x] Submission.md (this file — regenerate via the platform's prompt before final submit)
- [x] mindmap.html (self-contained, no external dependencies)
- [x] GitHub repo (this codebase)
- [ ] Live deployed link (fill in once deployed)
- [ ] 5-minute walkthrough, recorded on the platform
