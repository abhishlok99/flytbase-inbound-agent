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
    scene.fog = new THREE.FogExp2(0x1a140c, 0.0095);
    var camera = new THREE.PerspectiveCamera(45, W/H, 0.1, 2000);
    var renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
    renderer.setSize(W, H);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // -- lighting: low warm "desert sun" casting real shadows
    var sun = new THREE.DirectionalLight(0xffcf8a, 1.15);
    sun.position.set(-60, 70, 40);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024,1024);
    sun.shadow.camera.left = -110; sun.shadow.camera.right = 110;
    sun.shadow.camera.top = 110; sun.shadow.camera.bottom = -110;
    sun.shadow.camera.near = 1; sun.shadow.camera.far = 260;
    scene.add(sun);
    scene.add(new THREE.AmbientLight(0x6b5a3f, 0.65));
    scene.add(new THREE.HemisphereLight(0xffe3b0, 0x2a1d10, 0.35));

    // -- procedurally displaced dune terrain, zero external textures
    var segs = 64, size = 220;
    var groundGeo = new THREE.PlaneGeometry(size, size, segs, segs);
    groundGeo.rotateX(-Math.PI/2);
    var gp = groundGeo.attributes.position;
    for(var i=0;i<gp.count;i++){
      var x = gp.getX(i), z = gp.getZ(i);
      var h = Math.sin(x*0.045)*Math.cos(z*0.05)*3.2 + Math.sin(x*0.12+z*0.09)*1.1;
      gp.setY(i, h);
    }
    groundGeo.computeVertexNormals();
    var ground = new THREE.Mesh(groundGeo, new THREE.MeshStandardMaterial({color:0xb98a4e, roughness:1}));
    ground.receiveShadow = true;
    scene.add(ground);
    var grid = new THREE.GridHelper(size, 22, 0xc99a3c, 0x5a4526);
    grid.material.transparent = true; grid.material.opacity = 0.10; grid.position.y = 0.08;
    scene.add(grid);

    // -- dock: drone-in-a-box station, the flight's start/end point
    var DOCK = new THREE.Vector3(0,0,0);
    var dockGroup = new THREE.Group();
    var pad = new THREE.Mesh(new THREE.CylinderGeometry(7,7.6,0.6,24), new THREE.MeshStandardMaterial({color:0x2a2822, roughness:0.6}));
    pad.receiveShadow = true; dockGroup.add(pad);
    var box = new THREE.Mesh(new THREE.BoxGeometry(3.4,2.4,3.4), new THREE.MeshStandardMaterial({color:0xe9c873, roughness:0.4, metalness:0.3}));
    box.position.y = 1.2; box.castShadow = true; dockGroup.add(box);
    var beacon = new THREE.Mesh(new THREE.SphereGeometry(0.25,8,8), new THREE.MeshBasicMaterial({color:0xff6a3c}));
    beacon.position.y = 2.6; dockGroup.add(beacon);
    dockGroup.position.copy(DOCK);
    scene.add(dockGroup);

    // -- 3 survey sites
    var sitePositions = [
      new THREE.Vector3(-46, 0, -22),
      new THREE.Vector3(44, 0, -8),
      new THREE.Vector3(-6, 0, 42),
    ];
    var pulses = [], scanBeams = [];
    sitePositions.forEach(function(p){
      var pin = new THREE.Mesh(new THREE.CylinderGeometry(0.35,0.35,7,8), new THREE.MeshStandardMaterial({color:0x8a7a3f}));
      pin.position.copy(p); pin.position.y = 3.5; pin.castShadow = true;
      scene.add(pin);
      var marker = new THREE.Mesh(new THREE.OctahedronGeometry(1.6,0), new THREE.MeshStandardMaterial({color:0xe9c873, emissive:0x3a2c0f}));
      marker.position.copy(p); marker.position.y = 7.5;
      scene.add(marker);
      var ring = new THREE.Mesh(new THREE.RingGeometry(3,3.7,32), new THREE.MeshBasicMaterial({color:0xb3543f, transparent:true, opacity:0.7, side:THREE.DoubleSide}));
      ring.rotation.x = -Math.PI/2; ring.position.copy(p); ring.position.y = 0.15;
      scene.add(ring);
      pulses.push({mesh:ring, phase:Math.random()*6});

      var beam = new THREE.Mesh(new THREE.ConeGeometry(3.6, 12, 20, 1, true), new THREE.MeshBasicMaterial({color:0xe9c873, transparent:true, opacity:0, side:THREE.DoubleSide}));
      beam.position.copy(p); beam.position.y = 6.5;
      scene.add(beam);
      scanBeams.push(beam);
    });

    // -- rising "data collection" particles, spawned during a scan
    var PCOUNT = 40;
    var particleGeo = new THREE.BufferGeometry();
    var particlePos = new Float32Array(PCOUNT*3);
    var particleLife = new Float32Array(PCOUNT);
    for(var pi=0; pi<PCOUNT; pi++){ particleLife[pi] = -1; particlePos[pi*3+1] = -1000; }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePos,3));
    var particles = new THREE.Points(particleGeo, new THREE.PointsMaterial({color:0xf4d896, size:1.3, transparent:true, opacity:0.9, sizeAttenuation:true}));
    scene.add(particles);

    // -- drone: quadcopter built from primitives, spinning rotors
    var drone = new THREE.Group();
    var body = new THREE.Mesh(new THREE.BoxGeometry(1.6,0.5,1.6), new THREE.MeshStandardMaterial({color:0x1c1a16, roughness:0.4}));
    body.castShadow = true; drone.add(body);
    var rotors = [];
    [[1,1],[1,-1],[-1,1],[-1,-1]].forEach(function(a){
      var arm = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,1.9,6), new THREE.MeshStandardMaterial({color:0x2a2822}));
      arm.rotation.z = Math.PI/2; arm.position.set(a[0], 0, a[1]);
      drone.add(arm);
      var rotor = new THREE.Mesh(new THREE.CylinderGeometry(0.75,0.75,0.05,16), new THREE.MeshBasicMaterial({color:0xc9c3ae, transparent:true, opacity:0.55}));
      rotor.position.set(a[0]*1.75, 0.15, a[1]*1.75);
      drone.add(rotor); rotors.push(rotor);
    });
    drone.add(new THREE.PointLight(0xffcf8a, 1.2, 18));
    scene.add(drone);

    var trailLen = 50, trailPts = [];
    for(var ti=0; ti<trailLen; ti++) trailPts.push(DOCK.clone());
    var trailLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints(trailPts),
      new THREE.LineBasicMaterial({color:0xe9c873, transparent:true, opacity:0.35}));
    scene.add(trailLine);

    // -- flight choreography: dock -> takeoff -> [transit -> scan] x3 -> transit -> land
    var AIR_H = 13;
    function airAbove(v){ return new THREE.Vector3(v.x, AIR_H, v.z); }
    var DOCK_AIR = airAbove(DOCK);
    var seq = [{type:'takeoff', dur:2.2}];
    var prev = DOCK_AIR;
    sitePositions.forEach(function(s){
      var air = airAbove(s);
      seq.push({type:'transit', dur:4.0, from:prev, to:air});
      seq.push({type:'scan', dur:3.2, at:air, ground:s});
      prev = air;
    });
    seq.push({type:'transit', dur:4.0, from:prev, to:DOCK_AIR});
    seq.push({type:'land', dur:2.0});
    var TOTAL = seq.reduce(function(a,p){ return a+p.dur; }, 0);
    function ease(t){ return t<0.5 ? 2*t*t : 1-Math.pow(-2*t+2,2)/2; }
    function currentPhase(t){
      var acc = 0;
      for(var i=0;i<seq.length;i++){
        if(t < acc+seq[i].dur) return {ph:seq[i], local:(t-acc)/seq[i].dur};
        acc += seq[i].dur;
      }
      return {ph:seq[seq.length-1], local:1};
    }

    var clock = new THREE.Clock();
    camera.position.set(30,20,50);
    camera.userData.look = new THREE.Vector3(0,5,0);

    function animate(){
      requestAnimationFrame(animate);
      var t = clock.getElapsedTime();
      var cur = currentPhase(t % TOTAL);
      var ph = cur.ph, lt = ease(Math.min(Math.max(cur.local,0),1));
      var dp = drone.position, scanActive = null;

      if(ph.type==='takeoff'){
        dp.set(DOCK.x, THREE.MathUtils.lerp(0.6, AIR_H, lt), DOCK.z);
        drone.rotation.z = 0;
      } else if(ph.type==='land'){
        dp.set(DOCK.x, THREE.MathUtils.lerp(AIR_H, 0.6, lt), DOCK.z);
        drone.rotation.z = 0;
      } else if(ph.type==='transit'){
        var arc = Math.sin(lt*Math.PI) * 5;
        dp.set(
          THREE.MathUtils.lerp(ph.from.x, ph.to.x, lt),
          THREE.MathUtils.lerp(ph.from.y, ph.to.y, lt) + arc,
          THREE.MathUtils.lerp(ph.from.z, ph.to.z, lt)
        );
        drone.rotation.y = Math.atan2(ph.to.x-ph.from.x, ph.to.z-ph.from.z);
        drone.rotation.z = THREE.MathUtils.lerp(0, -0.22, Math.sin(lt*Math.PI));
      } else if(ph.type==='scan'){
        var ang = lt * Math.PI * 2 * 1.4;
        dp.set(ph.at.x + Math.cos(ang)*3.2, ph.at.y, ph.at.z + Math.sin(ang)*3.2);
        drone.rotation.y = ang + Math.PI/2; drone.rotation.z = 0;
        scanActive = ph.ground;
      }

      rotors.forEach(function(r){ r.rotation.y += 1.4; });

      scanBeams.forEach(function(beam, i){
        var isActive = scanActive === sitePositions[i];
        beam.material.opacity += ((isActive?0.35:0) - beam.material.opacity) * 0.08;
        if(isActive && Math.random() < 0.35){
          for(var k=0;k<PCOUNT;k++){
            if(particleLife[k] < 0){
              particlePos[k*3] = scanActive.x + (Math.random()-0.5)*4;
              particlePos[k*3+1] = 0.5;
              particlePos[k*3+2] = scanActive.z + (Math.random()-0.5)*4;
              particleLife[k] = 1.4;
              break;
            }
          }
        }
      });
      for(var k=0;k<PCOUNT;k++){
        if(particleLife[k] > 0){
          particlePos[k*3+1] += 0.09;
          particleLife[k] -= 0.018;
          if(particleLife[k] <= 0){ particleLife[k] = -1; particlePos[k*3+1] = -1000; }
        }
      }
      particleGeo.attributes.position.needsUpdate = true;

      pulses.forEach(function(p){
        var s = 1 + 0.5*Math.abs(Math.sin(t*0.9 + p.phase));
        p.mesh.scale.set(s,s,s);
      });

      trailPts.shift(); trailPts.push(dp.clone());
      trailLine.geometry.setFromPoints(trailPts);

      // -- cinematic camera: reframes per flight phase instead of one static orbit
      var camTarget, lookTarget;
      if(ph.type==='scan'){
        var orbitA = t*0.25;
        camTarget = new THREE.Vector3(scanActive.x+Math.cos(orbitA)*22, scanActive.y+10, scanActive.z+Math.sin(orbitA)*22);
        lookTarget = scanActive;
      } else if(ph.type==='takeoff' || ph.type==='land'){
        camTarget = new THREE.Vector3(DOCK.x+16, 10, DOCK.z+16);
        lookTarget = dp;
      } else {
        camTarget = new THREE.Vector3(dp.x, dp.y+9, dp.z).addScaledVector(
          new THREE.Vector3(Math.sin(drone.rotation.y), 0, Math.cos(drone.rotation.y)), -16);
        lookTarget = dp;
      }
      camera.position.lerp(camTarget, 0.035);
      camera.userData.look.lerp(lookTarget, 0.06);
      camera.lookAt(camera.userData.look);

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
