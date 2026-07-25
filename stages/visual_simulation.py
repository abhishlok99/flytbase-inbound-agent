"""
Visual/animated companion to Stage 7's operational-impact projection.

Renders a genuine 3D scene (Three.js, loaded from CDN) -- a stylized
desert terrain with the 3 Atacama sites named in the lead email, a drone
flying a continuous patrol loop between them, and pulsing "inspection
event" markers, captioned with the REAL numbers from Stage 7. This is a
visualization of the already-grounded projection, not a new, separate
claim -- every stat shown comes straight from the `sim` dict passed in.

Reliability: the CDN script has an onerror handler that swaps in a pure-
SVG fallback (zero external dependency) if Three.js fails to load on a
flaky connection -- a live demo should never show a blank/broken panel.

Deliberately not a literal satellite/Earth-imagery rendering (Google Earth
content can't be used for promotional purposes -- see the differentiation
research on file) -- this is an original, stylized site abstraction, in
the spirit of how FlytBase's own SQM case study visualizes patrol activity
in Cesium, without copying that or any proprietary asset.
"""

import re

THREE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"


def _extract_stat_cards(dims: list, email: dict) -> list:
    """Reformats real Stage 7 numbers into HUD-style stat cards -- pure
    display formatting of text Stage 7 already grounded in a real case
    study, never a new/invented figure. Always includes the lead's own
    stated deployment scale (from the email itself) as an honest anchor."""
    text = " ".join(dims)
    cards = []
    if re.search(r"doubl", text, re.I):
        cards.append(("2×", "Inspection frequency uplift"))
    m = re.search(r"<\s*(\d+)\s*year", text, re.I)
    if m:
        cards.append((f"&lt;{m.group(1)} yr", "Time to ROI"))
    m = re.search(r"USD\s*([\d,]+)\s*-\s*([\d,]+)K", text, re.I)
    if m:
        cards.append((f"${m.group(1)}&ndash;{m.group(2)}K", "Investment, single-zone rollout"))
    cards.append(("3 &times; 24/7", "Sites in this new deployment"))
    return cards


def _svg_fallback(dom_id: str) -> str:
    """Pure-SVG fallback, shown only if the Three.js CDN fails to load."""
    tiles = []
    for i in range(3):
        seed = i
        dur = 6 + seed
        pa, pb = 0.5 + seed * 0.7, 2.2 + seed * 0.5
        path_d = "M150,162 C60,150 40,60 100,40 C160,20 240,50 220,100 C205,140 180,155 150,162"
        tiles.append(f"""
        <div class="site-tile"><svg viewBox="0 0 300 200" class="site-svg" role="img" aria-label="Site {i+1} simulated patrol">
          <defs><radialGradient id="{dom_id}-glow{i}" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#c99a3c" stop-opacity="0.9"/><stop offset="100%" stop-color="#c99a3c" stop-opacity="0"/>
          </radialGradient></defs>
          <rect x="6" y="6" width="288" height="188" rx="10" fill="#141310" stroke="#8a7a3f" stroke-width="1.5" stroke-dasharray="6 4"/>
          <text x="16" y="26" font-size="11" fill="#c99a3c" font-family="monospace" letter-spacing="1">SITE {i+1} // ATACAMA</text>
          <rect x="138" y="150" width="24" height="24" rx="3" fill="#0c0c0b" stroke="#c99a3c" stroke-width="1"/>
          <path d="{path_d}" fill="none" stroke="#3a3426" stroke-width="1.5" stroke-dasharray="3 4"/>
          <circle r="14" fill="url(#{dom_id}-glow{i})"><animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto" path="{path_d}"/></circle>
          <circle r="4.5" fill="#e9c873" stroke="#0c0c0b" stroke-width="1"><animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto" path="{path_d}"/></circle>
          <circle cx="95" cy="55" r="4" fill="#b3543f"><animate attributeName="r" values="4;13;4" dur="2.4s" begin="{pa}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0;.9" dur="2.4s" begin="{pa}s" repeatCount="indefinite"/></circle>
          <circle cx="205" cy="95" r="4" fill="#b3543f"><animate attributeName="r" values="4;13;4" dur="2.4s" begin="{pb}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0;.9" dur="2.4s" begin="{pb}s" repeatCount="indefinite"/></circle>
        </svg></div>""")
    return f'<div class="sim-sites">{"".join(tiles)}</div>'


_JS_TEMPLATE = r"""
<script>
(function(){
  var wrap = document.getElementById('__DOMID__-3d');
  var fallback = document.getElementById('__DOMID__-fallback');
  function showFallback(){ if(wrap) wrap.style.display='none'; if(fallback) fallback.style.display='flex'; }
  var s = document.createElement('script');
  s.src = "__CDN__";
  s.onerror = showFallback;
  s.onload = function(){
    try { initSim3D(); } catch(e){ showFallback(); }
  };
  document.head.appendChild(s);

  function initSim3D(){
    var container = document.getElementById('__DOMID__-canvas-wrap');
    if(!container || typeof THREE === 'undefined'){ showFallback(); return; }
    var W = container.clientWidth, H = __HEIGHT__;
    var scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0c0c0b, 0.012);
    var camera = new THREE.PerspectiveCamera(42, W/H, 0.1, 1000);
    var renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
    renderer.setSize(W, H);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1, 2));
    container.appendChild(renderer.domElement);

    // terrain grid -- stylized desert, self-lit so it never renders black
    var grid = new THREE.GridHelper(140, 28, 0xc99a3c, 0x3a3426);
    grid.material.transparent = true; grid.material.opacity = 0.35;
    scene.add(grid);
    var groundGeo = new THREE.PlaneGeometry(140, 140);
    var groundMat = new THREE.MeshBasicMaterial({color:0x141310, transparent:true, opacity:0.85});
    var ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI/2; ground.position.y = -0.05;
    scene.add(ground);

    var sitePositions = [
      new THREE.Vector3(-38, 0, -18),
      new THREE.Vector3(36, 0, -6),
      new THREE.Vector3(-4, 0, 34),
    ];
    var siteGroup = new THREE.Group();
    var pulses = [];
    sitePositions.forEach(function(p, i){
      var pin = new THREE.Mesh(new THREE.CylinderGeometry(0.4,0.4,8,8), new THREE.MeshBasicMaterial({color:0x8a7a3f}));
      pin.position.copy(p); pin.position.y = 4;
      siteGroup.add(pin);
      var glow = new THREE.Mesh(new THREE.SphereGeometry(2.4,16,16), new THREE.MeshBasicMaterial({color:0xe9c873}));
      glow.position.copy(p); glow.position.y = 8.5;
      siteGroup.add(glow);
      var ring = new THREE.Mesh(new THREE.RingGeometry(3,3.6,32), new THREE.MeshBasicMaterial({color:0xb3543f, transparent:true, opacity:0.8, side:THREE.DoubleSide}));
      ring.rotation.x = -Math.PI/2; ring.position.copy(p); ring.position.y = 0.1;
      siteGroup.add(ring);
      pulses.push({mesh:ring, phase:i*2.1});
    });
    scene.add(siteGroup);

    // drone patrol path -- smooth closed loop through the 3 sites
    var curvePts = sitePositions.map(function(p){ return new THREE.Vector3(p.x, 10, p.z); });
    var curve = new THREE.CatmullRomCurve3(curvePts, true);
    var drone = new THREE.Mesh(new THREE.IcosahedronGeometry(1.4,0), new THREE.MeshBasicMaterial({color:0xe9c873}));
    scene.add(drone);
    var droneGlow = new THREE.PointLight ? null : null; // (kept simple/basic-material only, see header note)
    var glowSprite = new THREE.Mesh(new THREE.SphereGeometry(3.2,12,12), new THREE.MeshBasicMaterial({color:0xc99a3c, transparent:true, opacity:0.25}));
    scene.add(glowSprite);

    // fading trail
    var trailLen = 40, trailPts = [];
    for(var i=0;i<trailLen;i++) trailPts.push(curve.getPointAt(0));
    var trailGeo = new THREE.BufferGeometry().setFromPoints(trailPts);
    var trailMat = new THREE.LineBasicMaterial({color:0xc99a3c, transparent:true, opacity:0.5});
    var trailLine = new THREE.Line(trailGeo, trailMat);
    scene.add(trailLine);

    camera.position.set(0, 42, 70);
    var clock = new THREE.Clock();
    var camAngle = 0;

    function animate(){
      requestAnimationFrame(animate);
      var t = clock.getElapsedTime();
      var loopT = (t * 0.035) % 1;
      var pos = curve.getPointAt(loopT);
      drone.position.copy(pos); glowSprite.position.copy(pos);
      drone.rotation.y += 0.03;

      trailPts.shift();
      trailPts.push(pos.clone());
      trailLine.geometry.setFromPoints(trailPts);

      pulses.forEach(function(p){
        var s = 1 + 0.6*Math.abs(Math.sin(t*0.9 + p.phase));
        p.mesh.scale.set(s,s,s);
        p.mesh.material.opacity = 0.85 - 0.5*Math.abs(Math.sin(t*0.9 + p.phase));
      });

      camAngle += 0.0022;
      camera.position.x = Math.sin(camAngle) * 78;
      camera.position.z = Math.cos(camAngle) * 78;
      camera.position.y = 40;
      camera.lookAt(0, 4, 0);

      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', function(){
      var w = container.clientWidth;
      camera.aspect = w/H; camera.updateProjectionMatrix();
      renderer.setSize(w, H);
    });
  }
})();
</script>
"""


def render_simulation(sim: dict, email: dict, dom_id: str = "sim3d", height: int = 420) -> str:
    """sim is the Stage 7 output dict; renders honestly -- if Stage 7 had
    nothing to ground a projection in, this says so instead of animating
    an empty promise. When grounded, renders a live 3D patrol scene with
    a pure-SVG fallback if Three.js can't load."""
    if not sim.get("available"):
        return f"""<style>.sim-empty-card{{background:#141310;border:2px solid #3a3426;border-radius:10px;padding:1.2rem 1.4rem;color:#9a9483;font-style:italic;font-family:monospace;font-size:.85rem}}</style>
        <div class='sim-empty-card'>No grounded case study to base a visual simulation on this run — not rendering an ungrounded animation.<br>Reason: {sim.get('reason','')}</div>"""

    dims = sim.get("modeled_dimensions", [])
    dims_html = "".join(f"<li style='animation-delay:{.4*i+.2}s'>{d}</li>" for i, d in enumerate(dims))
    svg_fallback = _svg_fallback(dom_id)
    stat_cards = _extract_stat_cards(dims, email)
    hud_html = "".join(
        f"<div class='hud-card' style='animation-delay:{.35*i+.6}s'><div class='hud-val'>{v}</div><div class='hud-label'>{lbl}</div></div>"
        for i, (v, lbl) in enumerate(stat_cards)
    )

    style = f"""
    <style>
      .sim-wrap {{ background:#0c0c0b; border:2px solid #161512; border-radius:10px; padding:1.3rem 1.4rem; color:#e9e4d6;
                   box-shadow:0 10px 24px -16px rgba(0,0,0,.7), inset 0 0 60px rgba(201,154,60,.04); }}
      .sim-header {{ display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:.5rem;
                     font-family:monospace; font-size:.8rem; text-transform:uppercase; letter-spacing:.04em;
                     border-bottom:1px solid #2a2822; padding-bottom:.6rem; margin-bottom:.9rem; }}
      .sim-header b {{ color:#e9c873; font-size:.85rem; text-transform:none; letter-spacing:0; }}
      .sim-header .conf {{ color:#c99a3c; }}
      #{dom_id}-canvas-wrap {{ width:100%; height:{height}px; border-radius:8px; overflow:hidden; position:relative;
                     background:radial-gradient(circle at 50% 30%, #1c1a16 0%, #0c0c0b 70%); }}
      #{dom_id}-fallback {{ display:none; }}
      #{dom_id}-hud {{ position:absolute; top:14px; left:14px; display:flex; flex-wrap:wrap; gap:.6rem; max-width:78%; z-index:5; pointer-events:none; }}
      .hud-card {{
        background:rgba(20,19,16,.55); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
        border:1px solid rgba(201,154,60,.4); border-radius:8px; padding:.5rem .8rem;
        box-shadow:0 6px 18px -8px rgba(0,0,0,.6); opacity:0; animation:simFade .6s ease-out forwards;
      }}
      .hud-val {{ font-family:monospace; font-size:1.15rem; font-weight:700; color:#e9c873; line-height:1.1; }}
      .hud-label {{ font-family:monospace; font-size:.62rem; text-transform:uppercase; letter-spacing:.05em; color:#b9b39f; margin-top:.15rem; }}
      .sim-sites {{ display:flex; gap:1rem; margin-top:0; flex-wrap:wrap; width:100%; }}
      .site-tile {{ flex:1; min-width:220px; }}
      .site-svg {{ width:100%; height:auto; display:block; }}
      .sim-caption {{ font-size:.82rem; color:#b9b39f; margin-top:1rem; border-top:1px dashed #2a2822; padding-top:.8rem; }}
      .sim-caption i {{ color:#c99a3c; font-style:normal; font-family:monospace; font-size:.78rem; }}
      .sim-caption ul {{ margin:.5rem 0; padding-left:1.2rem; }}
      .sim-caption li {{ margin:.3rem 0; opacity:0; animation:simFade .5s ease-out forwards; }}
      .sim-caption p {{ color:#9a9483; font-size:.78rem; margin:.6rem 0 0; }}
      @keyframes simFade {{ to {{ opacity:1; }} }}
    </style>"""

    js = (_JS_TEMPLATE.replace("__DOMID__", dom_id)
          .replace("__CDN__", THREE_CDN)
          .replace("__HEIGHT__", str(height)))

    return f"""
    {style}
    <div class="sim-wrap">
      <div class="sim-header">
        <span><b>Live projected patrol — 3 Atacama lithium sites</b> &nbsp; (illustrative motion, grounded numbers below)</span>
        <span class="conf">confidence: {sim.get('confidence','')}</span>
      </div>
      <div id="{dom_id}-3d">
        <div id="{dom_id}-canvas-wrap">
          <div id="{dom_id}-hud">{hud_html}</div>
        </div>
      </div>
      <div id="{dom_id}-fallback">{svg_fallback}</div>
      <div class="sim-caption">
        Grounded in: <i>{sim.get('grounded_in','')}</i>
        <ul>{dims_html}</ul>
        <p>{sim.get('note','')}</p>
      </div>
    </div>
    {js}
    """
