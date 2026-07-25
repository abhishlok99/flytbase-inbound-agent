"""
Visual/animated companion to Stage 7's operational-impact projection.

Pure inline SVG + CSS animation -- zero external JS libraries, zero CDN
dependency, so it loads instantly and never breaks a live demo on a flaky
connection. Renders 3 stylized site tiles (one per Atacama lithium site
named in the lead email) with an animated dock->patrol->return drone loop
and staggered "inspection event" pulses, captioned with the REAL numbers
from Stage 7 -- this is a visualization of the already-grounded projection,
not a new, separate claim.

Deliberately not a literal satellite/Earth-imagery rendering (Google Earth
content can't be used for promotional purposes -- see the differentiation
research on file) -- this is an original, stylized site abstraction, in
the spirit of how FlytBase's own SQM case study visualizes patrol activity
in Cesium, without copying that or any proprietary asset.
"""


def _site_svg(site_num: int, seed_offset: int) -> str:
    dur = 6 + seed_offset  # slight stagger per site so all 3 don't move in lockstep
    pulse_delay_a = 0.5 + seed_offset * 0.7
    pulse_delay_b = 2.2 + seed_offset * 0.5
    path_d = "M150,162 C60,150 40,60 100,40 C160,20 240,50 220,100 C205,140 180,155 150,162"
    return f"""
    <svg viewBox="0 0 300 200" class="site-svg" role="img" aria-label="Site {site_num} simulated patrol">
      <defs>
        <radialGradient id="glow{site_num}" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#c99a3c" stop-opacity="0.9"/>
          <stop offset="100%" stop-color="#c99a3c" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect x="6" y="6" width="288" height="188" rx="10" fill="#141310" stroke="#8a7a3f" stroke-width="1.5" stroke-dasharray="6 4"/>
      <text x="16" y="26" font-size="11" fill="#c99a3c" font-family="'JetBrains Mono',monospace" letter-spacing="1">SITE {site_num} // ATACAMA</text>
      <circle cx="272" cy="20" r="3" fill="#5f8a5b">
        <animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/>
      </circle>

      <!-- dock -->
      <rect x="138" y="150" width="24" height="24" rx="3" fill="#0c0c0b" stroke="#c99a3c" stroke-width="1"/>
      <text x="150" y="188" font-size="8" text-anchor="middle" fill="#8a7a3f" font-family="'JetBrains Mono',monospace">DOCK</text>

      <!-- patrol path (guide) -->
      <path d="{path_d}" fill="none" stroke="#3a3426" stroke-width="1.5" stroke-dasharray="3 4"/>

      <!-- drone glow + body -->
      <circle r="14" fill="url(#glow{site_num})">
        <animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto" path="{path_d}"/>
      </circle>
      <circle r="4.5" fill="#e9c873" stroke="#0c0c0b" stroke-width="1">
        <animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto" path="{path_d}"/>
      </circle>

      <!-- inspection-event pulses (two stationary points of interest) -->
      <circle cx="95" cy="55" r="4" fill="#b3543f">
        <animate attributeName="r" values="4;13;4" dur="2.4s" begin="{pulse_delay_a}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.9;0;0.9" dur="2.4s" begin="{pulse_delay_a}s" repeatCount="indefinite"/>
      </circle>
      <circle cx="205" cy="95" r="4" fill="#b3543f">
        <animate attributeName="r" values="4;13;4" dur="2.4s" begin="{pulse_delay_b}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.9;0;0.9" dur="2.4s" begin="{pulse_delay_b}s" repeatCount="indefinite"/>
      </circle>
    </svg>
    """


def render_simulation(sim: dict, email: dict) -> str:
    """sim is the Stage 7 output dict; renders honestly -- if Stage 7 had
    nothing to ground a projection in, this says so instead of animating
    an empty promise."""
    if not sim.get("available"):
        return f"""<style>.sim-empty-card{{background:#141310;border:2px solid #3a3426;border-radius:10px;padding:1.2rem 1.4rem;color:#9a9483;font-style:italic;font-family:'JetBrains Mono',monospace;font-size:.85rem}}</style>
        <div class='sim-empty-card'>No grounded case study to base a visual simulation on this run — not rendering an ungrounded animation.<br>Reason: {sim.get('reason','')}</div>"""

    sites_html = "".join(f'<div class="site-tile">{_site_svg(i+1, i)}</div>' for i in range(3))
    dims_html = "".join(f"<li>{d}</li>" for d in sim.get("modeled_dimensions", []))

    return f"""
    <style>
      .sim-wrap {{ background:#0c0c0b; border:2px solid #161512; border-radius:10px; padding:1.3rem 1.4rem; color:#e9e4d6;
                   box-shadow:0 10px 24px -16px rgba(0,0,0,.7), inset 0 0 60px rgba(201,154,60,.04); }}
      .sim-header {{ display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:.5rem;
                     font-family:'JetBrains Mono',monospace; font-size:.8rem; text-transform:uppercase; letter-spacing:.04em;
                     border-bottom:1px solid #2a2822; padding-bottom:.6rem; }}
      .sim-header b {{ color:#e9c873; font-size:.85rem; text-transform:none; letter-spacing:0; }}
      .sim-header .conf {{ color:#c99a3c; }}
      .sim-sites {{ display:flex; gap:1rem; margin-top:1rem; flex-wrap:wrap; }}
      .site-tile {{ flex:1; min-width:250px; }}
      .site-svg {{ width:100%; height:auto; display:block; }}
      .sim-caption {{ font-size:.82rem; color:#b9b39f; margin-top:1rem; border-top:1px dashed #2a2822; padding-top:.8rem; }}
      .sim-caption i {{ color:#c99a3c; font-style:normal; font-family:'JetBrains Mono',monospace; font-size:.78rem; }}
      .sim-caption ul {{ margin:.5rem 0; padding-left:1.2rem; }}
      .sim-caption li {{ margin:.3rem 0; }}
      .sim-caption p {{ color:#9a9483; font-size:.78rem; margin:.6rem 0 0; }}
    </style>
    <div class="sim-wrap">
      <div class="sim-header">
        <span><b>Simulated patrol — 3 Atacama lithium sites</b> &nbsp; (illustrative motion, grounded numbers below)</span>
        <span class="conf">confidence: {sim.get('confidence','')}</span>
      </div>
      <div class="sim-sites">{sites_html}</div>
      <div class="sim-caption">
        Grounded in: <i>{sim.get('grounded_in','')}</i>
        <ul>{dims_html}</ul>
        <p>{sim.get('note','')}</p>
      </div>
    </div>
    """
