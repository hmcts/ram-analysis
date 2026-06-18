#!/usr/bin/env python3
"""Prototype: emit a self-contained `docs/graph.html` — an interactive
relationship graph of the RAM Pathfinder planning artefacts.

Nodes = planning-artefact markdown files; edges = markdown links between them.
Reuses the site chrome (CSS + shared `nav.js` sidebar) from build_html so the
page looks native and carries the same navigation as every other docs page.

Self-contained and `file://`-safe: all graph data is inlined as JSON, the
renderer is vanilla canvas JS (no CDN, no fetch). Clicking a node opens that
artefact's rendered HTML page.

Run:  python3 scripts/python/build_graph.py
Output: docs/graph.html
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_html as bh  # reuse CSS, SRC, OUT, map_out_relpath

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
LINK_RE = re.compile(r"\]\(([^)]+\.md)(?:#[^)]*)?\)")

GROUPS = {
    "Product": "#7c3aed",
    "Architecture (to-be)": "#2563eb",
    "Epics & Stories": "#059669",
    "Change Control & Readiness": "#d97706",
    "Other": "#6b7280",
}


def classify(rel: str) -> str:
    name = rel.lower()
    if rel == "prd":
        return "Product"
    if rel == "architecture" or rel.startswith("architecture"):
        return "Architecture (to-be)"
    if rel.startswith("epics"):
        return "Epics & Stories"
    if any(k in name for k in ("sprint-change-proposal", "implementation-readiness",
                               "prd-validation", "validation-report")):
        return "Change Control & Readiness"
    return "Other"


def read_meta(text: str):
    """Return (title, status_str, okf_type, tags) — consumes OKF frontmatter."""
    fm = FRONTMATTER_RE.match(text)
    title = None
    status = ""
    okf_type = ""
    tags = []
    if fm:
        block = fm.group(1)
        for line in block.splitlines():
            s = line.strip()
            low = s.lower()
            if title is None and low.startswith("title:"):
                title = s.split(":", 1)[1].strip().strip("'\"")
            if not okf_type and low.startswith("type:"):
                okf_type = s.split(":", 1)[1].strip().strip("'\"")
            if low.startswith("tags:"):
                m = re.match(r"\[(.*)\]", s.split(":", 1)[1].strip())
                if m:
                    tags = [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]
            if low.startswith("status:"):
                status += " " + s.split(":", 1)[1].strip().lower()
            if "supersededby" in low.replace(" ", ""):
                status += " superseded"
    if title is None:
        m = H1_RE.search(FRONTMATTER_RE.sub("", text))
        if m:
            title = m.group(1).strip()
    return title, status, okf_type, tags


def group_from_tags(tags):
    """Map OKF tags → display group (the OKF-consumption path)."""
    t = set(tags)
    if "prd" in t:
        return "Product"
    if "change-control" in t:
        return "Change Control & Readiness"
    if "epics" in t:
        return "Epics & Stories"
    if "architecture" in t:
        return "Architecture (to-be)"
    return None


def trunc(s: str, n: int = 46) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def main() -> int:
    src: Path = bh.SRC
    out: Path = bh.OUT
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        return 1

    nodes = {}      # rel(no .md) -> node dict
    rel_to_path = {}  # rel -> source Path

    for md in sorted(src.rglob("*.md")):
        rel = md.relative_to(src).with_suffix("").as_posix()
        text = md.read_text(encoding="utf-8", errors="replace")
        title, status, okftype, tags = read_meta(text)
        label = trunc(title or rel.split("/")[-1])
        href = bh.map_out_relpath(rel) + ".html"
        faded = ("supersed" in status) or rel.endswith((
            "epic-0.1-user-authenticates", "epic-0.2-reference-data-read-only",
            "epic-0.3-user-populations-bootstrapped", "epic-0.4-system-dispatches-emails",
        )) or rel == "epics"
        nodes[rel] = {
            "id": rel,
            "label": label,
            "group": group_from_tags(tags) or classify(rel),  # consume OKF tags
            "okftype": okftype or classify(rel),               # OKF type (tooltip)
            "href": href,
            "faded": bool(faded),
            "deg": 0,
        }
        rel_to_path[rel] = md

    # edges from markdown links
    edges = []
    seen = set()
    for rel, md in rel_to_path.items():
        text = md.read_text(encoding="utf-8", errors="replace")
        base = posixpath.dirname(rel)
        for m in LINK_RE.finditer(text):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://")):
                continue
            tgt = posixpath.normpath(posixpath.join(base, target[:-3]))  # drop .md
            if tgt in nodes and tgt != rel:
                key = (rel, tgt)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({"source": rel, "target": tgt})
                nodes[rel]["deg"] += 1
                nodes[tgt]["deg"] += 1

    node_list = list(nodes.values())
    graph = {"nodes": node_list, "links": edges,
             "groups": GROUPS}
    stats = {g: sum(1 for n in node_list if n["group"] == g) for g in GROUPS}

    data_json = json.dumps(graph, ensure_ascii=False)

    html = (PAGE
            .replace("__CSS__", bh.CSS)
            .replace("__EXTRA_CSS__", EXTRA_CSS)
            .replace("__GRAPH_JSON__", data_json)
            .replace("__GRAPH_JS__", GRAPH_JS)
            .replace("__NODE_COUNT__", str(len(node_list)))
            .replace("__EDGE_COUNT__", str(len(edges))))

    out.mkdir(parents=True, exist_ok=True)
    (out / "graph.html").write_text(html, encoding="utf-8")
    print(f"build: graph.html  ({len(node_list)} nodes, {len(edges)} edges)")
    for g, c in stats.items():
        print(f"   {c:>3}  {g}")
    return 0


EXTRA_CSS = """
.content.graph-main{max-width:none;padding:0;display:flex;flex-direction:column;height:100vh}
.graph-head{padding:.6rem 1rem;border-bottom:1px solid #e5e7eb;display:flex;gap:1rem;align-items:center;flex-wrap:wrap}
.graph-head h1{font-size:1.05rem;margin:0}
.graph-head .muted{color:#6b7280;font-size:.85rem}
.legend{display:flex;gap:.75rem;flex-wrap:wrap;margin-left:auto}
.legend button{border:1px solid #d1d5db;background:#fff;border-radius:999px;padding:.15rem .6rem;font-size:.78rem;cursor:pointer;display:inline-flex;align-items:center;gap:.4rem}
.legend button[aria-pressed=false]{opacity:.4}
.legend .dot{width:.7rem;height:.7rem;border-radius:50%}
#graph-wrap{position:relative;flex:1;min-height:0}
#graph-canvas{display:block;width:100%;height:100%;background:#fbfbfd;cursor:grab}
#graph-canvas.dragging{cursor:grabbing}
.graph-hint{position:absolute;left:.8rem;bottom:.6rem;font-size:.75rem;color:#9ca3af;background:rgba(255,255,255,.8);padding:.2rem .5rem;border-radius:4px}
.graph-tip{position:absolute;pointer-events:none;background:#111827;color:#fff;font-size:.78rem;padding:.3rem .5rem;border-radius:4px;max-width:18rem;display:none;z-index:5}
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Knowledge graph — RAM Pathfinder Documentation</title>
<style>__CSS__</style>
<style>__EXTRA_CSS__</style>
</head>
<body class="has-sections">
<aside class="nav" id="nav-root" aria-label="Site navigation"></aside>
<main class="content graph-main">
  <div class="graph-head">
    <h1>Knowledge graph</h1>
    <span class="muted">__NODE_COUNT__ artefacts · __EDGE_COUNT__ links · drag to pan · scroll to zoom · click a node to open</span>
    <div class="legend" id="legend"></div>
  </div>
  <div id="graph-wrap">
    <canvas id="graph-canvas"></canvas>
    <div class="graph-tip" id="tip"></div>
    <div class="graph-hint">Faded = superseded / historical · node size = number of links</div>
  </div>
</main>
<script>window.__NAV_BASE__="./";window.__PAGE__="graph";</script>
<script src="./nav.js"></script>
<script>const GRAPH=__GRAPH_JSON__;</script>
<script>__GRAPH_JS__</script>
</body>
</html>
"""

GRAPH_JS = r"""
(function(){
  var cv=document.getElementById('graph-canvas'), ctx=cv.getContext('2d');
  var wrap=document.getElementById('graph-wrap'), tip=document.getElementById('tip');
  var groups=GRAPH.groups, nodes=GRAPH.nodes, links=GRAPH.links;
  var byId={}; nodes.forEach(function(n){byId[n.id]=n;});
  var adj={}; nodes.forEach(function(n){adj[n.id]=new Set();});
  links.forEach(function(l){adj[l.source].add(l.target);adj[l.target].add(l.source);});
  var off={}; for(var g in groups){off[g]=true;}

  // deterministic-ish initial layout on a circle by group
  var i=0; nodes.forEach(function(n){var a=i/nodes.length*Math.PI*2;n.x=Math.cos(a)*250+Math.random()*40;n.y=Math.sin(a)*250+Math.random()*40;n.vx=0;n.vy=0;n.r=5+Math.min(10,(n.deg||0));i++;});

  var view={x:0,y:0,k:1}, W=0,H=0,dpr=window.devicePixelRatio||1;
  function resize(){W=wrap.clientWidth;H=wrap.clientHeight;cv.width=W*dpr;cv.height=H*dpr;cv.style.width=W+'px';cv.style.height=H+'px';ctx.setTransform(dpr,0,0,dpr,0,0);}
  window.addEventListener('resize',resize);resize();
  view.x=W/2;view.y=H/2;

  // force simulation
  var alpha=1;
  function step(){
    if(alpha<0.02)return;
    var k=alpha;
    // repulsion (O(n^2); fine for this size)
    for(var a=0;a<nodes.length;a++){var na=nodes[a];if(!off[na.group])continue;
      for(var b=a+1;b<nodes.length;b++){var nb=nodes[b];if(!off[nb.group])continue;
        var dx=na.x-nb.x,dy=na.y-nb.y,d2=dx*dx+dy*dy+0.01,d=Math.sqrt(d2);
        var f=2400/d2; var fx=dx/d*f,fy=dy/d*f;
        na.vx+=fx;na.vy+=fy;nb.vx-=fx;nb.vy-=fy;}}
    // springs
    links.forEach(function(l){var s=byId[l.source],t=byId[l.target];if(!off[s.group]||!off[t.group])return;
      var dx=t.x-s.x,dy=t.y-s.y,d=Math.sqrt(dx*dx+dy*dy)+0.01,f=(d-90)*0.02;
      var fx=dx/d*f,fy=dy/d*f;s.vx+=fx;s.vy+=fy;t.vx-=fx;t.vy-=fy;});
    // centering + integrate
    nodes.forEach(function(n){if(!off[n.group])return;n.vx+=-n.x*0.002;n.vy+=-n.y*0.002;
      n.x+=n.vx*k;n.y+=n.vy*k;n.vx*=0.85;n.vy*=0.85;});
    alpha*=0.98;
  }

  var hover=null;
  function toScreen(n){return{x:n.x*view.k+view.x,y:n.y*view.k+view.y};}
  function draw(){
    ctx.clearRect(0,0,W,H);
    // edges
    ctx.lineWidth=1;
    links.forEach(function(l){var s=byId[l.source],t=byId[l.target];if(!off[s.group]||!off[t.group])return;
      var ps=toScreen(s),pt=toScreen(t);
      var hl=hover&&(l.source===hover.id||l.target===hover.id);
      ctx.strokeStyle=hl?'rgba(37,99,235,.55)':'rgba(150,150,160,.18)';
      ctx.beginPath();ctx.moveTo(ps.x,ps.y);ctx.lineTo(pt.x,pt.y);ctx.stroke();});
    // nodes
    nodes.forEach(function(n){if(!off[n.group])return;var p=toScreen(n);
      var dim=hover&&hover.id!==n.id&&!adj[hover.id].has(n.id);
      ctx.globalAlpha=(n.faded?0.45:1)*(dim?0.25:1);
      ctx.fillStyle=groups[n.group]||'#888';
      ctx.beginPath();ctx.arc(p.x,p.y,n.r*Math.sqrt(view.k),0,Math.PI*2);ctx.fill();
      if(hover&&hover.id===n.id){ctx.lineWidth=2;ctx.strokeStyle='#111827';ctx.stroke();}
      if(view.k>0.6||n.deg>=4||(hover&&(hover.id===n.id||adj[hover.id].has(n.id)))){
        ctx.globalAlpha=dim?0.3:1;ctx.fillStyle='#111827';ctx.font='11px system-ui,sans-serif';
        ctx.fillText(n.label,p.x+n.r+3,p.y+3);}
      ctx.globalAlpha=1;});
  }
  function frame(){step();draw();requestAnimationFrame(frame);}
  frame();

  // hit testing
  function pick(mx,my){var best=null,bd=400;
    for(var i=0;i<nodes.length;i++){var n=nodes[i];if(!off[n.group])continue;var p=toScreen(n);
      var dx=mx-p.x,dy=my-p.y,d=dx*dx+dy*dy;var rr=(n.r*Math.sqrt(view.k)+6);
      if(d<rr*rr&&d<bd){bd=d;best=n;}}return best;}

  var dragNode=null,panning=false,lx=0,ly=0,moved=false;
  function pos(e){var r=cv.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top};}
  cv.addEventListener('mousedown',function(e){var m=pos(e);var n=pick(m.x,m.y);moved=false;
    if(n){dragNode=n;}else{panning=true;cv.classList.add('dragging');}lx=m.x;ly=m.y;});
  window.addEventListener('mousemove',function(e){var m=pos(e);
    if(dragNode){dragNode.x=(m.x-view.x)/view.k;dragNode.y=(m.y-view.y)/view.k;alpha=Math.max(alpha,0.3);moved=true;}
    else if(panning){view.x+=m.x-lx;view.y+=m.y-ly;lx=m.x;ly=m.y;moved=true;}
    else{var n=pick(m.x,m.y);hover=n;
      if(n){tip.style.display='block';tip.style.left=(m.x+14)+'px';tip.style.top=(m.y+12)+'px';
        tip.textContent=n.label+'  ·  '+(n.okftype||n.group)+(n.faded?'  (superseded)':'')+'  ·  '+n.deg+' links';cv.style.cursor='pointer';}
      else{tip.style.display='none';cv.style.cursor='grab';}}});
  window.addEventListener('mouseup',function(e){
    if(dragNode&&!moved&&dragNode.href){window.location.href=dragNode.href;}
    dragNode=null;panning=false;cv.classList.remove('dragging');});
  cv.addEventListener('wheel',function(e){e.preventDefault();var m=pos(e);var s=Math.exp(-e.deltaY*0.0012);
    view.x=m.x-(m.x-view.x)*s;view.y=m.y-(m.y-view.y)*s;view.k*=s;},{passive:false});

  // legend
  var leg=document.getElementById('legend');
  Object.keys(groups).forEach(function(g){var b=document.createElement('button');
    b.setAttribute('aria-pressed','true');
    b.innerHTML='<span class="dot" style="background:'+groups[g]+'"></span>'+g;
    b.onclick=function(){off[g]=!off[g];b.setAttribute('aria-pressed',off[g]?'true':'false');alpha=Math.max(alpha,0.3);};
    leg.appendChild(b);});
})();
"""


if __name__ == "__main__":
    sys.exit(main())
