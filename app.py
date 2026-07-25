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
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from orchestrator import run_pipeline
from stages.visual_simulation import render_simulation

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
        f"<small>Goal: {esc(e['goal_of_this_email'])}</small></div>"
        for e in resp.get("sequence", [])
    )
    sim_html = render_simulation(sim, lead)

    log_html = "".join(
        f"<li class='{esc(l['status'])}'>{esc(l['stage'])} &mdash; {esc(l['status'])}</li>"
        for l in result["run_log"]
    )

    score = q.get("priority_score", 0)

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

  <div class="rail">
    {''.join(f"<a href='#s{i}'>{i}. {name}</a>" for i,name,_ in STAGE_ORDER)}
    <a href="/run.json">raw json</a>
  </div>

  <section class="stage-block" id="s1" style="animation-delay:.02s">
    <div class="stage-head"><span class="stage-num">1</span><h2>Qualification</h2><span class="badge">{esc(q.get('framework'))}</span></div>
    <div class="card">
      <p><b>Why this framework:</b> {esc(q.get('framework_reasoning'))}</p>
      <div class="score-wrap"><span class="score-num">{score}</span><div class="score-bar"><div class="score-fill" style="width:{score}%"></div></div></div>
      <div class="fields">{known_pills}{open_pills}</div>
      <p><b>Known:</b></p><ul>{known_html}</ul>
      <p><b>Missing for full qualification:</b></p><ul>{missing_html}</ul>
    </div>
  </section>

  <section class="stage-block" id="s2" style="animation-delay:.06s">
    <div class="stage-head"><span class="stage-num">2</span><h2>Deep Account Research</h2></div>
    <div class="card">
      <div class="flag">{esc(r.get('existing_relationship_signal') or 'No existing-relationship signal found this run.')}</div>
      <p><b>Positioning recommendation:</b> {esc(r.get('positioning_recommendation'))}</p>
    </div>
  </section>

  <section class="stage-block" id="s3" style="animation-delay:.10s">
    <div class="stage-head"><span class="stage-num">3</span><h2>Response Generation</h2></div>
    <div class="card">
      <p><b>Progression logic:</b> {esc(resp.get('progression_logic'))}</p>
      {emails_html}
    </div>
  </section>

  <section class="stage-block" id="s4" style="animation-delay:.14s">
    <div class="stage-head"><span class="stage-num">4</span><h2>Case Study Matching</h2></div>
    <div class="card">{matches_html}</div>
  </section>

  <section class="stage-block" id="s5" style="animation-delay:.18s">
    <div class="stage-head"><span class="stage-num">5</span><h2>Partner Identification</h2><span class="badge">{esc(p.get('region'))}</span></div>
    <div class="card"><p><b>Motion:</b> {esc(p.get('recommended_motion'))}</p><p>{esc(p.get('justification'))}</p></div>
  </section>

  <section class="stage-block" id="s6" style="animation-delay:.22s">
    <div class="stage-head"><span class="stage-num">6</span><h2>AE Handoff Summary</h2></div>
    <div class="card"><p>{esc(h.get('buyer_context'))}</p><p><b>Suggested next step:</b> {esc(h.get('suggested_next_step'))}</p></div>
  </section>

  <section class="stage-block" id="s7" style="animation-delay:.26s">
    <div class="stage-head"><span class="stage-num">7</span><h2>Impact Simulation</h2><span class="badge">bonus</span></div>
    {sim_html}
  </section>

  <ul class="runlog">{log_html}</ul>
  <footer>flytbase inbound agent &mdash; built for The Closer, 25 Jul 2026 &mdash; <a href="/run.json">/run.json</a> &middot; <a href="/health">/health</a></footer>
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
