# Submission.md — FlytBase Inbound BDR Agent

> Note: if the eval platform's submission form provides its own prompt to regenerate this file against the final codebase, run that and let it supersede this version. This is the accurate, as-built version as of final submission.

## What was built

A 7-stage inbound-lead processing pipeline (6 required by the brief + 1 bonus) that takes the fixed test email (Rodrigo Castillo, SQM, Atacama lithium sites, referred by Anglo American) and, live on every page load: qualifies it via MEDDPICC with an itemized priority score, builds a real-data account research brief (SEC EDGAR, Google News, flytbase.com), drafts a 3-email adaptive response sequence, matches it against flytbase.com's actual live case studies, recommends a partner/GTM motion, produces an AE handoff summary, and — the bonus stage — projects operational impact using only numbers FlytBase already measured at this same customer's other site.

Two things go beyond the brief's minimum:

1. **A live "agent reasoning" console** on the main page — real strings pulled from each stage's actual output (not filler text), revealed in sequence as the corresponding stage section animates in below it. This makes the delegation across stages visible as it happens, not just describable afterward.
2. **A client-facing landing page** (`/client-preview`), linked directly from the drafted Email 1 — what the lead themselves would see if this were actually sent. It embeds a cinematic 3D simulation (a drone taking off from a dock, flying to each of the 3 sites, hovering to scan with a visible beam and rising data particles, then returning) with a glass HUD showing the real grounded numbers, plus a "nearby, live today" section built from a generic geo-scan of FlytBase's actual case-study locations against the lead's own stated country — for this lead, it correctly surfaces their own existing SQM site in Chile.

## Why this architecture

Delegated across independently callable, typed stages (`stages/stage1_...py` through `stage7_...py`, plus `geo.py` and `stages/visual_simulation.py`) orchestrated by a thin `orchestrator.py` with zero business logic of its own — the delegation is visible by reading the file, not just claimed. See `mindmap.html` for the full flow and the two real decision points (existing-account detection, partner continuity).

## Framework choice: MEDDPICC

Chosen over BANT/SPICED because this is a multi-stakeholder enterprise deal with a referral-shaped Champion signal, a dated Decision Process step (Q3 budget conversation), and open Decision Criteria/Competition questions — MEDDPICC's seven fields fit this deal's actual shape; BANT's four fields would flatten it. Full reasoning is generated live in Stage 1's output, not hard-coded here.

## The single most important finding

Stage 4 deliberately searches for the lead's own company name, not just the explicitly-named referral (Anglo American) — matching against both the scraped case-study title and its URL slug, since page markup isn't always consistent. Doing so surfaces a real, verified fact: SQM already has a live FlytBase case study (the "Hermosa" mine, via partner Adentu — doubled inspection frequency, <1yr ROI, USD 70-80K single-zone investment). This reframes the lead from a cold new-logo to a likely internal expansion signal, which changes the qualification framing, the response strategy, the partner recommendation (continuity with Adentu over a generic regional partner), and the client landing page's "visit us nearby" section (their own site, not a stranger's).

## Research quality / anti-fabrication

Every fact in Stage 2's output is traced to a live fetch (SEC EDGAR full-text search, Google News RSS, flytbase.com's own case-study pages — all free and keyless, deliberately, so research quality never depends on paid tool access). Anything not found at run time is explicitly marked `UNVERIFIED AT RUN TIME` rather than filled with a plausible-sounding guess. Stage 7's simulation refuses to render at all if there's no real case study to ground it in.

## Path to production (what's simulated here vs. what a real deployment needs)

This runs today as a page you paste a lead into and load. A real BDR wouldn't use it that way — here's the honest gap between this build and production, and what's already designed to close it:

- **Trigger**: a real webhook from flytbase.com/contact firing this pipeline automatically, instead of a manual paste into the try-a-different-lead form.
- **Send**: Stage 3's drafted emails go out through a real send API (Gmail/Outlook API) instead of just being displayed on the page.
- **Track**: the app already includes a small working proof-of-concept of this — `/client-preview` records each open in-memory and the main page shows a live "opened Nx, last at HH:MM" pill next to the email's CTA link. It's intentionally minimal (single-process, resets on restart, no persistence) rather than a fabricated dashboard of fake numbers. A real deployment would swap this for standard link/open tracking on a real send.
- **Follow-up**: Stage 3's progression logic already anticipates this — email 2 is explicitly written to fire "only if no reply," email 3 "only if still no reply." A scheduler checking the same open/reply signal the tracking POC demonstrates would trigger those automatically, so the follow-up logic doesn't need to be rebuilt, just connected to a real signal.
- **Where this would live**: most naturally as a browser extension/CRM plugin a BDR opens against an inbound thread, rather than a standalone page — the pipeline and its output are already structured as reusable, typed functions (see `orchestrator.py`), so wrapping them behind a different front end doesn't require touching the logic itself.

## Known limitations (candor over polish)

- flytbase.com's per-case-study numeric result badges (e.g. "Reduced Travel Time") are client-side rendered and not reliably extractable via a static fetch — the system does not claim a specific percentage it cannot verify from source.
- The Stage 3 email sequence runs in structured-template mode unless an LLM API key is configured (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GOOGLE_API_KEY` / `GROQ_API_KEY`) — template mode is real logic assembled from Stage 1/2 output, not pre-written copy.
- The 3D simulation loads Three.js from a CDN; if that fails on a flaky connection, a pure-SVG fallback (zero external dependency) renders instead automatically — a live demo should never show a blank panel.
- The "nearby deployments" geo-scan is generic (a country/region gazetteer matched against whatever case studies were actually fetched, same code path regardless of which lead is loaded) — for this specific lead it currently surfaces one real result (the lead's own Chile site); it will surface more or fewer depending on what FlytBase has actually published, which is the honest behavior.
- Live fetches (EDGAR/News/flytbase.com) require outbound network access from wherever this is deployed; a restricted network environment degrades gracefully (flagged, not fabricated) rather than failing the whole run.

## How to run

```
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
Open `/` for the rendered run, `/client-preview` for the client-facing page, `/run.json` for raw output, `/health` for a liveness check.

## Deliverables checklist

- [x] Submission.md (this file)
- [x] mindmap.html (self-contained, no external dependencies)
- [x] GitHub repo — https://github.com/abhishlok99/flytbase-inbound-agent
- [x] Live deployed link — https://flytbase-inbound-agent.onrender.com
- [ ] 5-minute walkthrough, recorded on the platform
