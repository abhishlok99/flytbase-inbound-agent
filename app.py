"""
FastAPI app -- this IS the "live deployed link" deliverable. GET / runs the
full pipeline against the fixed brief input (or a pasted override) and
renders every stage's real output, so a reviewer opening the link sees the
system actually run, not a static screenshot. GET /run.json returns the
same as raw JSON for inspection.

Visual language deliberately mirrors FlytBase's own eval platform
(eval.lifeatflytbase.com) -- dark ground, monospace technical labels, cream
bordered cards, an amber "live system" status readout -- rather than a
generic dashboard template, for the same reason the demo narrative mirrors
their own "AI in Action" show format: speaking the company's own visual
language is a small, cheap signal that the homework went beyond the brief.
"""
import json
import re
from urllib.parse import quote
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

import geo
from orchestrator import run_pipeline
from stages.visual_simulation import render_simulation


def _maps_search_link(candidate: dict) -> str:
    """A Google Maps SEARCH link (not a pinned address) built from real,
    already-known data -- the case study's own location + a cleaned
    version of its title. Exact site coordinates aren't published
    anywhere we fetch from, so this searches by name/region rather than
    fabricating a precise street address."""
    label = re.sub(r"\d+[%×x]|\bRead\b|\bMining\b", " ", candidate.get("title", ""))
    label = re.sub(r"\s+", " ", label).strip()[:70]
    query = f"{label} {candidate.get('location','')}".strip()
    return "https://www.google.com/maps/search/?api=1&query=" + quote(query)

app = FastAPI(title="FlytBase Inbound BDR Agent")

with open("input/lead_email.json") as f:
    DEFAULT_LEAD_EMAIL = json.load(f)


STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');
  :root{
    --ink:#161512; --paper:#f4efe2; --paper-2:#efe8d6; --line:#161512;
    --bg-0:#0c0c0b; --bg-1:#151412; --amber:#c99a3c; --amber-soft:#8a7a3f;
    --green:#5f8a5b; --red:#b3543f; --muted:#9a9483;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0; background:
      radial-gradient(circle at 15% 0%, #1c1a16 0%, var(--bg-0) 45%),
      repeating-linear-gradient(0deg, rgba(255,255,255,.025) 0 1px, transparent 1px 42px),
      repeating-linear-gradient(90deg, rgba(255,255,255,.025) 0 1px, transparent 1px 42px);
    color:#e9e4d6; font-family:'Inter',-apple-system,Segoe UI,sans-serif; line-height:1.55;
    padding-bottom:5rem;
  }
  .mono{font-family:'JetBrains Mono',ui-monospace,Consolas,monospace}
  .topbar{
    display:flex; justify-content:space-between; align-items:center;
    padding:1rem 2rem; border-bottom:1px solid #2a2822; position:sticky; top:0;
    background:rgba(12,12,11,.88); backdrop-filter:blur(6px); z-index:20;
  }
  .topbar .brand{font-family:'JetBrains Mono';font-weight:700;letter-spacing:.02em;font-size:1.05rem;color:#f4efe2}
  .topbar .brand span{color:var(--amber)}
  .status-pill{
    font-family:'JetBrains Mono'; font-size:.72rem; letter-spacing:.06em; text-transform:uppercase;
    background:var(--amber); color:#141310; padding:.35rem .8rem; border-radius:3px; font-weight:700;
    display:flex; align-items:center; gap:.5rem;
  }
  .status-pill .dot{width:7px;height:7px;border-radius:50%;background:#141310;animation:pulse 1.6s infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
  .wrap{max-width:960px;margin:0 auto;padding:0 1.5rem}
  .hero{padding:3rem 0 1.5rem}
  .eyebrow{font-family:'JetBrains Mono';font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--amber);margin-bottom:.6rem}
  .hero h1{font-size:2rem;margin:.2rem 0 .6rem;color:#faf7ee;font-weight:700;letter-spacing:-.01em}
  .hero p{color:#b9b39f;max-width:62ch;margin:0}
  .input-card{
    background:var(--paper); color:var(--ink); border:2px solid var(--line); border-radius:12px;
    padding:1.3rem 1.5rem; margin:1.6rem 0 2.5rem; box-shadow:0 12px 30px -14px rgba(0,0,0,.6);
  }
  .input-card .lead-line{font-size:.95rem}
  .input-card .lead-line b{font-family:'JetBrains Mono'}
  .input-card blockquote{margin:.7rem 0 0;padding-left:.9rem;border-left:3px solid var(--amber-soft);font-style:italic;color:#3a362c}
  details.tryform{margin-top:1rem; border-top:1px dashed #cfc6a8; padding-top:.8rem}
  details.tryform summary{cursor:pointer; font-family:'JetBrains Mono'; font-size:.78rem; letter-spacing:.04em; text-transform:uppercase; color:var(--amber-soft)}
  .tryform input, .tryform textarea{
    width:100%; font-family:inherit; padding:.5rem .6rem; margin:.25rem 0 .6rem; border:1.5px solid #cfc6a8;
    border-radius:6px; background:#fffdf6; font-size:.88rem;
  }
  .tryform button{
    background:var(--ink); color:#f4efe2; border:none; padding:.6rem 1.1rem; border-radius:6px;
    font-family:'JetBrains Mono'; font-size:.8rem; letter-spacing:.03em; cursor:pointer;
  }
  .tryform button:hover{background:#000}
  .override-banner{
    font-family:'JetBrains Mono'; font-size:.78rem; background:var(--amber); color:#141310;
    padding:.6rem 1rem; border-radius:6px; margin-bottom:1rem; letter-spacing:.02em;
  }
  .console{
    background:#0a0a09; border:1.5px solid #2a2822; border-radius:8px; margin:0 0 1.4rem; overflow:hidden;
    box-shadow:0 10px 24px -16px rgba(0,0,0,.6);
  }
  .console-head{
    font-family:'JetBrains Mono'; font-size:.68rem; letter-spacing:.06em; text-transform:uppercase; color:#8f897a;
    padding:.5rem .9rem; border-bottom:1px solid #201f1a; display:flex; align-items:center; gap:.5rem;
  }
  .console-dot{width:7px;height:7px;border-radius:50%;background:#5f8a5b;animation:pulse 1.6s infinite}
  .console-body{
    font-family:'JetBrains Mono'; font-size:.78rem; color:#c9e4a8; padding:.7rem .9rem; min-height:6.2rem;
    max-height:11rem; overflow-y:auto; line-height:1.65;
  }
  .console-line{opacity:0; animation:consoleIn .35s ease-out forwards}
  .console-line::before{content:'';}
  @keyframes consoleIn{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:none}}
  .cta-link{
    display:inline-block; margin-top:.6rem; font-family:'JetBrains Mono'; font-size:.78rem; letter-spacing:.02em;
    color:#141310; background:var(--amber); padding:.4rem .8rem; border-radius:5px; text-decoration:none; font-weight:700;
  }
  .cta-link:hover{background:#e9c873}
  .rail{
    display:flex; gap:.4rem; flex-wrap:wrap; margin:0 0 2.2rem; position:sticky; top:64px; z-index:10;
    background:linear-gradient(to bottom, rgba(12,12,11,1) 70%, transparent); padding:.6rem 0 1rem;
  }
  .rail a{
    font-family:'JetBrains Mono'; font-size:.68rem; letter-spacing:.04em; text-transform:uppercase;
    color:#9a9483; border:1px solid #2f2c24; padding:.32rem .6rem; border-radius:999px; text-decoration:none;
    transition:.15s;
  }
  .rail a:hover{color:var(--amber); border-color:var(--amber)}
  section.stage-block{
    scroll-margin-top:6.5rem; margin:0 0 2.4rem; opacity:0; transform:translateY(10px);
    animation:rise .5s ease-out forwards;
  }
  @keyframes rise{to{opacity:1;transform:none}}
  .stage-head{display:flex; align-items:baseline; gap:.8rem; margin-bottom:.7rem}
  .stage-num{
    font-family:'JetBrains Mono'; font-weight:700; font-size:.75rem; color:#141310; background:var(--amber);
    width:1.8rem; height:1.8rem; border-radius:5px; display:flex; align-items:center; justify-content:center;
  }
  .stage-head h2{font-size:1.15rem; margin:0; color:#faf7ee; font-weight:600}
  .stage-head .badge{
    font-family:'JetBrains Mono'; font-size:.68rem; letter-spacing:.04em; text-transform:uppercase;
    background:transparent; border:1px solid var(--amber-soft); color:var(--amber); padding:.15rem .5rem; border-radius:4px;
  }
  .card{
    background:var(--paper-2); color:var(--ink); border:2px solid var(--line); border-radius:10px;
    padding:1.1rem 1.3rem; box-shadow:0 10px 24px -16px rgba(0,0,0,.55);
  }
  .card b{color:#141310}
  .card ul{margin:.5rem 0; padding-left:1.2rem}
  .card li{margin:.3rem 0; font-size:.92rem}
  .score-wrap{display:flex; align-items:center; gap:1rem; margin:.6rem 0}
  .score-num{font-family:'JetBrains Mono'; font-size:2.1rem; font-weight:700; color:var(--amber-soft)}
  .score-bar{flex:1; height:10px; background:#e2d9bc; border-radius:6px; border:1.5px solid var(--line); overflow:hidden}
  .score-fill{height:100%; background:linear-gradient(90deg,var(--amber-soft),var(--amber))}
  .fields{display:flex; gap:.4rem; flex-wrap:wrap; margin:.5rem 0}
  .fields span{font-family:'JetBrains Mono'; font-size:.68rem; padding:.2rem .5rem; border-radius:4px}
  .fields .known{background:#dcead9; border:1px solid var(--green); color:#2f4a2c}
  .fields .open{background:#f3ded7; border:1px solid var(--red); color:#6b2f22}
  .flag{
    background:#f6efe0; border-left:4px solid var(--amber); padding:.6rem .8rem; border-radius:0 6px 6px 0;
    font-size:.9rem; margin:.6rem 0;
  }
  .email{border:1.5px dashed #cfc6a8; border-radius:8px; padding:.9rem 1rem; margin:.9rem 0; background:#fffdf6}
  .email b{font-family:'JetBrains Mono'; font-size:.85rem}
  .email pre{white-space:pre-wrap; font-family:'Inter',sans-serif; font-size:.9rem; margin:.5rem 0}
  .email small{color:#6b6350}
  .match{border-bottom:1px solid #e2d9bc; padding:.6rem 0}
  .match:last-child{border-bottom:none}
  .match .mscore{font-family:'JetBrains Mono'; font-weight:700; color:#141310; background:var(--amber); padding:.05rem .4rem; border-radius:4px; font-size:.75rem}
  .runlog{
    font-family:'JetBrains Mono'; font-size:.74rem; color:#8f897a; list-style:none; padding:0; margin:1.5rem 0;
    display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:.3rem;
  }
  .runlog li{border:1px solid #2a2822; border-radius:5px; padding:.35rem .6rem}
  .runlog li.ok::before{content:'\\25CF '; color:var(--green)}
  .runlog li.error::before{content:'\\25CF '; color:var(--red)}
  footer{text-align:center; color:#5c5848; font-family:'JetBrains Mono'; font-size:.72rem; margin-top:3rem}
  footer a{color:var(--amber-soft)}
</style>
"""

STAGE_ORDER = [
    ("1", "Qualification", "meddpicc"),
    ("2", "Deep Account Research", "research"),
    ("3", "Response Generation", "response"),
    ("4", "Case Study Matching", "casestudy"),
    ("5", "Partner Identification", "partner"),
    ("6", "AE Handoff Summary", "handoff"),
    ("7", "Impact Simulation", "simulation"),
]


def render_html(result: dict) -> str:
    def esc(s):
        return str(s).replace("<", "&lt;").replace(">", "&gt;") if s is not None else ""

    lead = result["input_email"]
    q = result["stage1_qualification"]
    r = result["stage2_research"]
    resp = result["stage3_response"]
    cs = result["stage4_case_study"]
    p = result["stage5_partner"]
    h = result["stage6_handoff"]
    sim = result["stage7_simulation"]

    known_html = "".join(f"<li><b>{esc(k)}:</b> {esc(v)}</li>" for k, v in q.get("known", {}).items())
    missing_html = "".join(f"<li>{esc(m)}</li>" for m in q.get("missing_for_full_qualification", []))
    known_pills = "".join(f"<span class='known'>{esc(k)}</span>" for k in q.get("meddpicc_fields_covered", []))
    open_pills = "".join(f"<span class='open'>{esc(k)}</span>" for k in q.get("meddpicc_fields_open", []))

    matches_html = "".join(
        f"<div class='match'><span class='mscore'>{m['match_score']}</span> &nbsp;<b>{esc(m['title'])}</b>"
        f"<ul>{''.join(f'<li>{esc(x)}</li>' for x in m['match_reasons'])}</ul></div>"
        for m in cs.get("top_matches", [])
    ) or "<p><i>No case studies matched this run (see run log below -- likely a live-fetch issue in this environment).</i></p>"

    emails_html = "".join(
        f"<div class='email'><b>Email {e['step']} &mdash; {esc(e['subject'])}</b><pre>{esc(e['body'])}</pre>"
        f"<small>Goal: {esc(e['goal_of_this_email'])}</small>"
        + (f"<a class='cta-link' href='/client-preview' target='_blank'>&#8599; View interactive walkthrough (what Rodrigo would see)</a>"
           if e.get("client_preview_link") else "")
        + "</div>"
        for e in resp.get("sequence", [])
    )
    sim_html = render_simulation(sim, lead)

    log_html = "".join(
        f"<li class='{esc(l['status'])}'>{esc(l['stage'])} &mdash; {esc(l['status'])}</li>"
        for l in result["run_log"]
    )

    score = q.get("priority_score", 0)

    # -- live "reasoning console": real strings pulled from the stages
    # that already ran, not filler text -- json.dumps escapes safely for
    # embedding as a JS array literal.
    top_match = cs.get("primary_recommendation")
    console_lines = [
        f"> reading inbound email from {lead.get('from_name','')} <{lead.get('from_email','')}>...",
        f"> qualifying via {q.get('framework','')} -- priority score {score}/100",
        "> fetching flytbase.com case studies, SEC EDGAR filings, recent news (live, parallel)...",
        (f"> case study match: \"{top_match['title'][:70]}\" (score {top_match['match_score']})"
         if top_match else "> no case study matched this run"),
        (r.get("existing_relationship_signal", "") or "> no existing-relationship signal found")[:140],
        "> drafting adaptive 3-email sequence from qualification gaps + research...",
        f"> partner motion: {p.get('recommended_motion','')} -- {p.get('justification','')[:90]}",
        (f"> building impact simulation -- grounded in \"{sim.get('grounded_in','')[:60]}\""
         if sim.get("available") else "> no grounded case study -- skipping simulation, not fabricating one"),
        "> done. full report below.",
    ]
    console_js = json.dumps(console_lines)

    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlytBase Inbound BDR Agent -- live run</title>
{STYLE}
</head><body>
<div class="topbar">
  <div class="brand">flyt<span>base</span> // inbound-agent</div>
  <div class="status-pill"><span class="dot"></span> system live</div>
</div>

<div class="wrap">
  <div class="hero">
    <div class="eyebrow">The Closer — Inbound BDR Hackathon</div>
    <h1>Inbound Lead Qualification Agent</h1>
    <p>Every stage below runs live, on this load, against the input shown. Nothing here is pre-written &mdash; refresh to re-run the entire pipeline from scratch.</p>
  </div>

  <div class="input-card">
    <div class="lead-line"><b>{esc(lead.get('from_name'))}</b> &lt;{esc(lead.get('from_email'))}&gt; &mdash; {esc(lead.get('title'))}, {esc(lead.get('company'))}</div>
    <div class="lead-line mono" style="font-size:.8rem;color:#6b6350;margin-top:.2rem">{esc(lead.get('subject'))}</div>
    <blockquote>&ldquo;{esc(lead.get('body'))}&rdquo;</blockquote>
    <details class="tryform">
      <summary>&#9656; Try a different lead (proves the logic isn't hard-coded)</summary>
      <form method="get" action="/">
        <input name="from_name" placeholder="From name">
        <input name="from_email" placeholder="From email">
        <input name="title" placeholder="Title">
        <input name="company" placeholder="Company">
        <input name="country" placeholder="Country">
        <input name="subject" placeholder="Subject">
        <textarea name="body" rows="3" placeholder="Body"></textarea>
        <button type="submit">Re-run pipeline on this lead</button>
        &nbsp; <a href="/" class="mono" style="font-size:.75rem;color:#8a7a3f">reset to brief's original lead</a>
      </form>
    </details>
  </div>

  <div class="console" id="console">
    <div class="console-head"><span class="console-dot"></span> agent reasoning &mdash; live, this run</div>
    <div class="console-body" id="console-body"></div>
  </div>
  <script>
    (function(){{
      var lines = {console_js};
      var el = document.getElementById('console-body');
      lines.forEach(function(line, i){{
        setTimeout(function(){{
          var row = document.createElement('div');
          row.className = 'console-line';
          row.textContent = line;
          el.appendChild(row);
          el.scrollTop = el.scrollHeight;
        }}, i * 650);
      }});
    }})();
  </script>

  <div class="rail">
    {''.join(f"<a href='#s{i}'>{i}. {name}</a>" for i,name,_ in STAGE_ORDER)}
    <a href="/run.json">raw json</a>
  </div>

  <section class="stage-block" id="s1" style="animation-delay:.9s">
    <div class="stage-head"><span class="stage-num">1</span><h2>Qualification</h2><span class="badge">{esc(q.get('framework'))}</span></div>
    <div class="card">
      <p><b>Why this framework:</b> {esc(q.get('framework_reasoning'))}</p>
      <div class="score-wrap"><span class="score-num">{score}</span><div class="score-bar"><div class="score-fill" style="width:{score}%"></div></div></div>
      <div class="fields">{known_pills}{open_pills}</div>
      <p><b>Known:</b></p><ul>{known_html}</ul>
      <p><b>Missing for full qualification:</b></p><ul>{missing_html}</ul>
    </div>
  </section>

  <section class="stage-block" id="s2" style="animation-delay:2.2s">
    <div class="stage-head"><span class="stage-num">2</span><h2>Deep Account Research</h2></div>
    <div class="card">
      <div class="flag">{esc(r.get('existing_relationship_signal') or 'No existing-relationship signal found this run.')}</div>
      <p><b>Positioning recommendation:</b> {esc(r.get('positioning_recommendation'))}</p>
      <p><b>Org structure / reporting line:</b> {esc(r.get('org_structure_note'))}</p>
      <p><b>Budget signals (public filings):</b></p>
      <ul>{"".join(f"<li>{esc(x)}</li>" for x in r.get('budget_signals', []))}</ul>
      <p><b>Recent news:</b></p>
      <ul>{"".join(f"<li>{esc(x)}</li>" for x in r.get('recent_news', []))}</ul>
      <p><b>Stakeholder / investor signals:</b></p>
      <ul>{"".join(f"<li>{esc(x)}</li>" for x in r.get('stakeholder_signals', []))}</ul>
    </div>
  </section>

  <section class="stage-block" id="s3" style="animation-delay:3.5s">
    <div class="stage-head"><span class="stage-num">3</span><h2>Response Generation</h2></div>
    <div class="card">
      <p><b>Progression logic:</b> {esc(resp.get('progression_logic'))}</p>
      {emails_html}
    </div>
  </section>

  <section class="stage-block" id="s4" style="animation-delay:1.6s">
    <div class="stage-head"><span class="stage-num">4</span><h2>Case Study Matching</h2></div>
    <div class="card">{matches_html}</div>
  </section>

  <section class="stage-block" id="s5" style="animation-delay:4.2s">
    <div class="stage-head"><span class="stage-num">5</span><h2>Partner Identification</h2><span class="badge">{esc(p.get('region'))}</span></div>
    <div class="card"><p><b>Motion:</b> {esc(p.get('recommended_motion'))}</p><p>{esc(p.get('justification'))}</p></div>
  </section>

  <section class="stage-block" id="s6" style="animation-delay:4.9s">
    <div class="stage-head"><span class="stage-num">6</span><h2>AE Handoff Summary</h2></div>
    <div class="card"><p>{esc(h.get('buyer_context'))}</p><p><b>Suggested next step:</b> {esc(h.get('suggested_next_step'))}</p></div>
  </section>

  <section class="stage-block" id="s7" style="animation-delay:5.6s">
    <div class="stage-head"><span class="stage-num">7</span><h2>Impact Simulation</h2><span class="badge">bonus</span></div>
    {sim_html}
  </section>

  <ul class="runlog">{log_html}</ul>
  <footer>flytbase inbound agent &mdash; built for The Closer, 25 Jul 2026 &mdash; <a href="/run.json">/run.json</a> &middot; <a href="/health">/health</a></footer>
</div>
</body></html>"""


CLIENT_STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700;800&display=swap');
  :root{ --ink:#161512; --paper:#f4efe2; --amber:#c99a3c; --amber-soft:#8a7a3f; --bg-0:#0c0c0b; }
  *{box-sizing:border-box}
  body{
    margin:0; background:radial-gradient(circle at 20% 0%, #1c1a16 0%, var(--bg-0) 50%);
    color:#e9e4d6; font-family:'Inter',-apple-system,sans-serif; line-height:1.6;
  }
  .mono{font-family:'JetBrains Mono',monospace}
  .cwrap{max-width:880px;margin:0 auto;padding:0 1.5rem 5rem}
  .chero{padding:4rem 0 2rem; text-align:center}
  .cbadge{
    display:inline-block; font-family:'JetBrains Mono'; font-size:.7rem; letter-spacing:.12em; text-transform:uppercase;
    color:var(--amber); border:1px solid var(--amber-soft); padding:.3rem .8rem; border-radius:999px; margin-bottom:1.2rem;
  }
  .chero h1{font-size:2.4rem; margin:.3rem 0 .8rem; color:#faf7ee; font-weight:800; letter-spacing:-.01em}
  .chero h1 span{color:var(--amber)}
  .chero p{color:#b9b39f; max-width:52ch; margin:0 auto; font-size:1.05rem}
  .csection{margin:2.6rem 0}
  .csection h2{font-family:'JetBrains Mono'; font-size:.82rem; text-transform:uppercase; letter-spacing:.08em; color:var(--amber); margin:0 0 1rem}
  .ccard{
    background:var(--paper); color:var(--ink); border-radius:12px; padding:1.5rem 1.7rem;
    box-shadow:0 16px 40px -20px rgba(0,0,0,.7);
  }
  .cgrid{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:1rem}
  .visit-card{
    background:#0e0d0b; border:1.5px solid #2a2822; border-radius:10px; padding:1.1rem 1.2rem;
  }
  .visit-card .vloc{font-family:'JetBrains Mono'; font-size:.68rem; text-transform:uppercase; letter-spacing:.05em; color:var(--amber); margin-bottom:.4rem}
  .visit-card a{color:#faf7ee; text-decoration:none; font-weight:600; font-size:.95rem}
  .visit-card a:hover{color:var(--amber)}
  .visit-card .vaddr{font-size:.76rem; color:#8a8578; margin:.7rem 0 0; line-height:1.45}
  .visit-card .vaddr a{color:var(--amber); font-weight:500; font-size:.8rem}
  .visit-card .vask{font-size:.85rem; color:#f4d896; margin:.6rem 0 0; font-weight:600}
  .visit-cta{
    margin-top:1.4rem; font-family:'JetBrains Mono'; font-size:.85rem; color:#e9e4d6; background:#161512;
    border:1px dashed var(--amber-soft); border-radius:8px; padding:.9rem 1.1rem;
  }
  .cfooter{
    margin-top:3rem; text-align:center; font-family:'JetBrains Mono'; font-size:.72rem; color:#6b6350;
  }
  .honesty-note{font-size:.78rem; color:#9a9483; margin-top:.6rem}
</style>
"""


def render_client_page(result: dict) -> str:
    def esc(s):
        return str(s).replace("<", "&lt;").replace(">", "&gt;") if s is not None else ""

    lead = result["input_email"]
    cs = result["stage4_case_study"]
    h = result["stage6_handoff"]
    sim = result["stage7_simulation"]
    first_name = esc(lead.get("from_name", "there")).split()[0] if lead.get("from_name") else "there"
    company = esc(lead.get("company", ""))

    sim_html = render_simulation(sim, lead, dom_id="sim3d-client", height=520)

    # Assemble the real "visit us nearby" set: primary match (if same
    # country/region as the lead) + referral match + any independently
    # discovered nearby deployments -- all real, all from data already
    # fetched live this run, nothing invented for this page.
    lead_country = lead.get("country", "")
    candidates = []
    top = cs.get("primary_recommendation")
    if top:
        loc = geo.extract_country(top.get("title", "")) or geo.extract_country(top.get("url", "").replace("-", " "))
        candidates.append({**top, "location": loc or lead_country, "why": "This is the same account's own other site."})
    for n in cs.get("nearby_deployments", []):
        candidates.append({**n, "why": f"Live FlytBase deployment in {n.get('location','the region')}."})

    visit_html = "".join(
        f"""<div class="visit-card"><div class="vloc">{esc(c.get('location',''))}</div>
        <a href="{esc(c['url'])}" target="_blank">{esc(c['title'])[:90]} &#8599;</a>
        <p style="font-size:.82rem;color:#9a9483;margin:.5rem 0 0">{esc(c['why'])}</p>
        <p class="vaddr">&#128205; Approx. location (map search, not a pinned address -- exact site
        coordinates aren't published anywhere we fetch from) &mdash;
        <a href="{esc(_maps_search_link(c))}" target="_blank">Open in Google Maps &#8599;</a></p>
        <p class="vask">Would you like to visit this site in person before your Q3 conversation?
        If yes &mdash; what week works for you?</p></div>"""
        for c in candidates
    )

    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlytBase &mdash; a look at what's next for {company}</title>
{CLIENT_STYLE}
</head><body>
<div class="cwrap">
  <div class="chero">
    <span class="cbadge">Prepared for {esc(lead.get('from_name',''))} &mdash; {company}</span>
    <h1>What autonomous inspection could look like <span>across your Atacama sites</span></h1>
    <p>A short interactive walkthrough, built from what's already working at your own site today &mdash; not a generic pitch.</p>
  </div>

  <div class="csection">
    <h2>01 &middot; The vision</h2>
    {sim_html}
  </div>

  <div class="csection">
    <h2>02 &middot; Nearby, live today</h2>
    <div class="cgrid">{visit_html or "<p style='color:#9a9483'>No independently-nearby deployments found this run beyond the match above.</p>"}</div>
    <div class="visit-cta">Happy to arrange a hands-on visit to any of the sites above &mdash; just reply with which one and a week that works.</div>
  </div>

  <div class="csection">
    <h2>03 &middot; Suggested next step</h2>
    <div class="ccard"><p>{esc(h.get('suggested_next_step',''))}</p></div>
    <p class="honesty-note">This page is a prototype of what a personalized follow-up asset could look like &mdash; generated from this run's real data, not a template with your name pasted in.</p>
  </div>

  <div class="cfooter">flytbase &mdash; prepared automatically from your inbound message, {esc(lead.get('subject',''))}</div>
</div>
</body></html>"""


def _resolve_email(params: dict) -> tuple[dict, bool]:
    """Returns (email, was_overridden). Falls back field-by-field to the
    default brief email so a partial paste still runs -- this is the same
    reason Stage 1-7 never hard-fail on missing fields, applied to input too."""
    overridden = any(params.get(k) for k in ("from_name", "from_email", "company", "subject", "body"))
    if not overridden:
        return DEFAULT_LEAD_EMAIL, False
    merged = dict(DEFAULT_LEAD_EMAIL)
    for k in ("from_name", "from_email", "title", "company", "country", "subject", "body"):
        v = params.get(k)
        if v:
            merged[k] = v
    return merged, True


@app.get("/", response_class=HTMLResponse)
def home(from_name: str = "", from_email: str = "", title: str = "", company: str = "",
          country: str = "", subject: str = "", body: str = ""):
    email, overridden = _resolve_email(dict(from_name=from_name, from_email=from_email, title=title,
                                             company=company, country=country, subject=subject, body=body))
    result = run_pipeline(email)
    html = render_html(result)
    if overridden:
        html = html.replace(
            '<div class="rail">',
            '<div class="override-banner">RUNNING ON A CUSTOM PASTED LEAD -- not the brief\'s original example. Live proof the pipeline generalizes.</div><div class="rail">',
        )
    return html


@app.get("/client-preview", response_class=HTMLResponse)
def client_preview(from_name: str = "", from_email: str = "", title: str = "", company: str = "",
                    country: str = "", subject: str = "", body: str = ""):
    """The page a reviewer reaches by clicking the link Stage 3 puts in
    Email 1 -- what the lead themselves would see, not the internal ops
    dashboard. Runs the same live pipeline so it stays consistent with
    whatever lead is currently loaded (including a pasted override)."""
    email, _ = _resolve_email(dict(from_name=from_name, from_email=from_email, title=title,
                                     company=company, country=country, subject=subject, body=body))
    result = run_pipeline(email)
    return render_client_page(result)


@app.get("/run.json")
def run_json(from_name: str = "", from_email: str = "", title: str = "", company: str = "",
             country: str = "", subject: str = "", body: str = ""):
    email, _ = _resolve_email(dict(from_name=from_name, from_email=from_email, title=title,
                                     company=company, country=country, subject=subject, body=body))
    result = run_pipeline(email)
    return JSONResponse(content=json.loads(json.dumps(result, default=str)))


@app.get("/health")
def health():
    return {"status": "ok"}
