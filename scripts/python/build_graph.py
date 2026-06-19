#!/usr/bin/env python3
"""Emit a self-contained `docs/graph.html` — a HIERARCHICAL relationship view
of the RAM Pathfinder planning artefacts (an OKF-bundle visualiser).

The artefacts form a tree via their `parent` frontmatter (architecture → shards
& sequence diagrams; epics/index → framework/maps & phase indexes; phase index
→ epics). Orphans (PRD, change-control reports, pack roots) hang off synthetic
group nodes under a single root. Layout is a **deterministic layered tree**
computed here in Python — root top-left, depth = column (stepping right),
siblings stacked top-down — so the page is stable, not a force-directed blob.

Hierarchy (parent→child) edges are drawn as org-tree elbows. The remaining
markdown cross-references (FR→epic, decision links, …) are a faint overlay,
toggled off by default so the hierarchy reads cleanly.

Reuses the site chrome (CSS + shared `nav.js` sidebar) from build_html.
Self-contained / `file://`-safe: data inlined as JSON, vanilla-canvas renderer,
no CDN, no fetch. Clicking a node opens that artefact's rendered HTML page.

Run:  python3 scripts/python/build_graph.py   (also run by build-html.sh)
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

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
LINK_RE = re.compile(r"\]\(([^)]+\.md)(?:#[^)]*)?\)")

GROUPS = {  # group -> colour
    "Product": "#7c3aed",
    "Architecture (to-be)": "#2563eb",
    "Epics & Stories": "#059669",
    "Change Control & Readiness": "#d97706",
    "Other": "#6b7280",
}
GROUP_ORDER = list(GROUPS.keys())
ROOT = "@root"


def gid(group: str) -> str:
    return "@grp:" + group


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


def group_from_tags(tags):
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


def read_meta(text: str):
    """Return (title, status, okf_type, tags, parent_raw) from frontmatter."""
    fm = FM_RE.match(text)
    title = None; status = ""; okf_type = ""; tags = []; parent = ""
    if fm:
        for line in fm.group(1).splitlines():
            s = line.strip(); low = s.lower()
            if title is None and low.startswith("title:"):
                title = s.split(":", 1)[1].strip().strip("'\"")
            if not okf_type and low.startswith("type:"):
                okf_type = s.split(":", 1)[1].strip().strip("'\"")
            if not parent and low.startswith("parent:"):
                parent = s.split(":", 1)[1].strip().strip("'\"")
            if low.startswith("tags:"):
                m = re.match(r"\[(.*)\]", s.split(":", 1)[1].strip())
                if m:
                    tags = [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]
            if low.startswith("status:"):
                status += " " + s.split(":", 1)[1].strip().lower()
            if "supersededby" in low.replace(" ", ""):
                status += " superseded"
    if title is None:
        m = H1_RE.search(FM_RE.sub("", text))
        if m:
            title = m.group(1).strip()
    return title, status, okf_type, tags, parent


def resolve_parent(rel: str, parent_raw: str, ids: set):
    """Parent frontmatter is inconsistent (file-relative ../x.md vs SRC-relative
    epics/index.md). Try both; return the one that is a real node id."""
    if not parent_raw:
        return None
    p = parent_raw[:-3] if parent_raw.endswith(".md") else parent_raw
    cand1 = posixpath.normpath(posixpath.join(posixpath.dirname(rel), p))
    if cand1 in ids:
        return cand1
    if p in ids:
        return p
    return None


def trunc(s: str, n: int = 44) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def main() -> int:
    src: Path = bh.SRC
    out: Path = bh.OUT
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        return 1

    raw = {}  # rel -> dict(text, title, status, okftype, tags, parent_raw)
    for md in sorted(src.rglob("*.md")):
        rel = md.relative_to(src).with_suffix("").as_posix()
        text = md.read_text(encoding="utf-8", errors="replace")
        title, status, okftype, tags, parent_raw = read_meta(text)
        raw[rel] = dict(text=text, title=title, status=status, okftype=okftype,
                        tags=tags, parent_raw=parent_raw)
    ids = set(raw)

    # nodes (real)
    nodes = {}
    for rel, r in raw.items():
        group = group_from_tags(r["tags"]) or classify(rel)
        faded = "supersed" in r["status"]
        nodes[rel] = dict(id=rel, label=trunc(r["title"] or rel.split("/")[-1]),
                          group=group, okftype=r["okftype"] or classify(rel),
                          href=bh.map_out_relpath(rel) + ".html",
                          faded=bool(faded), deg=0, synthetic=False)

    # cross-reference edges (markdown links) + degree
    cross = []
    seen = set()
    for rel, r in raw.items():
        base = posixpath.dirname(rel)
        for m in LINK_RE.finditer(r["text"]):
            t = m.group(1).strip()
            if t.startswith(("http://", "https://")):
                continue
            tgt = posixpath.normpath(posixpath.join(base, t[:-3]))
            if tgt in nodes and tgt != rel and (rel, tgt) not in seen:
                seen.add((rel, tgt))
                cross.append({"s": rel, "t": tgt})
                nodes[rel]["deg"] += 1
                nodes[tgt]["deg"] += 1

    # effective parent: real parent, else the group node
    used_groups = set()
    parent_of = {}
    for rel, r in raw.items():
        pid = resolve_parent(rel, r["parent_raw"], ids)
        if not pid:
            pid = gid(nodes[rel]["group"])
            used_groups.add(nodes[rel]["group"])
        parent_of[rel] = pid

    # synthetic nodes: root + group nodes (only groups actually used as a parent)
    nodes[ROOT] = dict(id=ROOT, label="RAM Pathfinder", group="", okftype="root",
                       href="", faded=False, deg=0, synthetic=True)
    for g in GROUP_ORDER:
        if g in used_groups:
            nodes[gid(g)] = dict(id=gid(g), label=g, group=g, okftype="group",
                                 href="", faded=False, deg=0, synthetic=True)
            parent_of[gid(g)] = ROOT
    parent_of[ROOT] = None

    # children map (ordered)
    children = {nid: [] for nid in nodes}
    for nid, pid in parent_of.items():
        if pid is not None:
            children[pid].append(nid)

    def order_key(nid):
        return nid  # natural id sort (epic-0.1 < epic-0.2; groups handled below)

    for nid in children:
        if nid == ROOT:
            children[nid].sort(key=lambda g: GROUP_ORDER.index(nodes[g]["group"])
                               if nodes[g]["group"] in GROUP_ORDER else 99)
        else:
            children[nid].sort(key=order_key)

    # Indented-outline layout (pre-order DFS): every node gets its OWN row —
    # parent on the line above its children — so no two labels share a row and
    # nothing overlaps. Column = depth (steps right); row increments per node.
    COLW, ROWH, PADX, PADY = 220, 44, 24, 28
    slot = [0]
    def layout(nid, depth):
        n = nodes[nid]
        n["level"] = depth
        n["x"] = PADX + depth * COLW
        n["y"] = PADY + slot[0] * ROWH
        slot[0] += 1
        for k in children[nid]:
            layout(k, depth + 1)
    layout(ROOT, 0)

    tree = [{"s": pid, "t": nid} for nid, pid in parent_of.items() if pid is not None]
    # cross edges that are NOT already tree edges (avoid double-drawing)
    tree_pairs = {(e["s"], e["t"]) for e in tree} | {(e["t"], e["s"]) for e in tree}
    cross = [e for e in cross if (e["s"], e["t"]) not in tree_pairs]

    graph = {"nodes": list(nodes.values()), "tree": tree, "cross": cross,
             "groups": GROUPS, "rows": slot[0]}
    data_json = json.dumps(graph, ensure_ascii=False)

    real = [n for n in nodes.values() if not n["synthetic"]]
    html = (PAGE.replace("__CSS__", bh.CSS).replace("__EXTRA_CSS__", EXTRA_CSS)
            .replace("__GRAPH_JSON__", data_json).replace("__GRAPH_JS__", GRAPH_JS)
            .replace("__NODE_COUNT__", str(len(real)))
            .replace("__EDGE_COUNT__", str(len(graph["tree"]) + len(cross))))
    out.mkdir(parents=True, exist_ok=True)
    (out / "graph.html").write_text(html, encoding="utf-8")
    print(f"build: graph.html  ({len(real)} artefacts, {len(tree)} hierarchy + {len(cross)} cross-links)")
    return 0


EXTRA_CSS = """
.content.graph-main{max-width:none;padding:0;display:flex;flex-direction:column;height:100vh}
.graph-head{padding:.55rem 1rem;border-bottom:1px solid #e5e7eb;display:flex;gap:1rem;align-items:center;flex-wrap:wrap}
.graph-head h1{font-size:1.05rem;margin:0}
.graph-head .muted{color:#6b7280;font-size:.82rem}
.graph-tools{display:flex;gap:.5rem;flex-wrap:wrap;margin-left:auto;align-items:center}
.graph-tools button{border:1px solid #d1d5db;background:#fff;border-radius:999px;padding:.18rem .65rem;font-size:.78rem;cursor:pointer;display:inline-flex;align-items:center;gap:.4rem}
.graph-tools button[aria-pressed=false]{opacity:.4}
.graph-tools .dot{width:.7rem;height:.7rem;border-radius:50%}
.graph-tools .sep{width:1px;height:1.1rem;background:#e5e7eb}
#graph-wrap{position:relative;flex:1;min-height:0}
#graph-canvas{display:block;width:100%;height:100%;background:#fbfbfd;cursor:grab}
#graph-canvas.dragging{cursor:grabbing}
.graph-hint{position:absolute;left:.8rem;bottom:.6rem;font-size:.74rem;color:#9ca3af;background:rgba(255,255,255,.85);padding:.2rem .5rem;border-radius:4px}
.graph-tip{position:absolute;pointer-events:none;background:#111827;color:#fff;font-size:.78rem;padding:.3rem .5rem;border-radius:4px;max-width:20rem;display:none;z-index:5}
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
    <span class="muted">__NODE_COUNT__ artefacts · hierarchy by <code>parent</code> · click a node to open</span>
    <div class="graph-tools" id="tools">
      <button id="toggle-cross" aria-pressed="false"><span class="dot" style="background:#9ca3af"></span>Cross-links</button>
      <button id="fit">Fit</button>
      <span class="sep"></span>
    </div>
  </div>
  <div id="graph-wrap">
    <canvas id="graph-canvas"></canvas>
    <div class="graph-tip" id="tip"></div>
    <div class="graph-hint">Drag to pan · scroll to zoom · click a node to open</div>
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
  var cv=document.getElementById('graph-canvas'),ctx=cv.getContext('2d');
  var wrap=document.getElementById('graph-wrap'),tip=document.getElementById('tip');
  var groups=GRAPH.groups,nodes=GRAPH.nodes,tree=GRAPH.tree,cross=GRAPH.cross;
  var byId={};nodes.forEach(function(n){byId[n.id]=n;});
  var nbr={};nodes.forEach(function(n){nbr[n.id]=new Set();});
  tree.concat(cross).forEach(function(e){if(nbr[e.s])nbr[e.s].add(e.t);if(nbr[e.t])nbr[e.t].add(e.s);});
  var off={};for(var g in groups){off[g]=true;}
  var showCross=false;

  var dpr=window.devicePixelRatio||1,W=0,H=0,view={x:24,y:24,k:1};
  function resize(){W=wrap.clientWidth;H=wrap.clientHeight;cv.width=W*dpr;cv.height=H*dpr;cv.style.width=W+'px';cv.style.height=H+'px';ctx.setTransform(dpr,0,0,dpr,0,0);draw();}
  window.addEventListener('resize',resize);

  function bbox(){var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;nodes.forEach(function(n){if(!vis(n))return;x0=Math.min(x0,n.x);y0=Math.min(y0,n.y);x1=Math.max(x1,n.x+170);y1=Math.max(y1,n.y);});return{x0:x0,y0:y0,x1:x1,y1:y1};}
  function fit(){var b=bbox();var cw=b.x1-b.x0+40;view.k=Math.min(1,(W-20)/cw);if(!isFinite(view.k)||view.k<=0)view.k=1;view.x=14-b.x0*view.k;view.y=16-b.y0*view.k;draw();}

  function vis(n){return n.synthetic?true:off[n.group]!==false;}
  function P(n){return{x:n.x*view.k+view.x,y:n.y*view.k+view.y};}

  function elbow(s,t){ // outline-tree connector: straight down from parent, across to child
    var ps=P(s),pt=P(t);
    ctx.beginPath();ctx.moveTo(ps.x,ps.y+7);ctx.lineTo(ps.x,pt.y);ctx.lineTo(pt.x-4,pt.y);ctx.stroke();
  }
  function curve(s,t){var ps=P(s),pt=P(t);var mx=(ps.x+pt.x)/2;
    ctx.beginPath();ctx.moveTo(ps.x,ps.y);ctx.bezierCurveTo(mx,ps.y,mx,pt.y,pt.x,pt.y);ctx.stroke();}

  var hover=null;
  function draw(){
    ctx.clearRect(0,0,W,H);
    // cross-links (faint overlay)
    if(showCross){ctx.lineWidth=1;
      cross.forEach(function(e){var s=byId[e.s],t=byId[e.t];if(!vis(s)||!vis(t))return;
        var hl=hover&&(e.s===hover.id||e.t===hover.id);
        ctx.strokeStyle=hl?'rgba(217,119,6,.55)':'rgba(120,120,140,.12)';curve(s,t);});}
    // hierarchy edges
    ctx.lineWidth=1.1;
    tree.forEach(function(e){var s=byId[e.s],t=byId[e.t];if(!vis(s)||!vis(t))return;
      var hl=hover&&(e.s===hover.id||e.t===hover.id);
      ctx.strokeStyle=hl?'rgba(37,99,235,.6)':'rgba(150,150,160,.45)';elbow(s,t);});
    // nodes
    ctx.textBaseline='middle';
    nodes.forEach(function(n){if(!vis(n))return;var p=P(n);
      var dim=hover&&hover.id!==n.id&&!nbr[hover.id].has(n.id);
      ctx.globalAlpha=(n.faded?0.5:1)*(dim?0.25:1);
      if(n.synthetic){
        ctx.font=(n.okftype==='root'?'700 ':'600 ')+(n.okftype==='root'?13:12)+'px system-ui,sans-serif';
        var w=ctx.measureText(n.label).width+16;
        ctx.fillStyle=n.okftype==='root'?'#111827':(groups[n.group]||'#555');
        roundRect(p.x-3,p.y-9,w,18,9);ctx.fill();
        ctx.fillStyle='#fff';ctx.fillText(n.label,p.x+5,p.y+1);
      }else{
        var r=(4+Math.min(8,n.deg))*Math.max(.7,Math.min(1.4,view.k));
        ctx.fillStyle=groups[n.group]||'#888';
        ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill();
        if(hover&&hover.id===n.id){ctx.lineWidth=2;ctx.strokeStyle='#111827';ctx.stroke();}
        ctx.fillStyle='#111827';ctx.font='11px system-ui,sans-serif';
        ctx.fillText(n.label,p.x+r+5,p.y+1);
      }
      ctx.globalAlpha=1;});
  }
  function roundRect(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}

  function pick(mx,my){var best=null,bd=18*18;
    for(var i=0;i<nodes.length;i++){var n=nodes[i];if(!vis(n))continue;var p=P(n);
      var dx=mx-p.x,dy=my-p.y,d=dx*dx+dy*dy;if(d<bd){bd=d;best=n;}}return best;}
  function posn(e){var r=cv.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top};}

  var panning=false,lx=0,ly=0,moved=false,downNode=null;
  cv.addEventListener('mousedown',function(e){var m=posn(e);downNode=pick(m.x,m.y);panning=!downNode;moved=false;lx=m.x;ly=m.y;if(panning)cv.classList.add('dragging');});
  window.addEventListener('mousemove',function(e){var m=posn(e);
    if(panning){view.x+=m.x-lx;view.y+=m.y-ly;lx=m.x;ly=m.y;moved=true;draw();return;}
    var n=pick(m.x,m.y);if(n!==hover){hover=n;draw();}
    if(n&&!n.synthetic){tip.style.display='block';tip.style.left=(m.x+14)+'px';tip.style.top=(m.y+12)+'px';
      tip.textContent=n.label+'  ·  '+n.okftype+(n.faded?'  (superseded)':'')+'  ·  '+n.deg+' links';cv.style.cursor='pointer';}
    else{tip.style.display='none';cv.style.cursor=n?'default':'grab';}});
  window.addEventListener('mouseup',function(){if(downNode&&!moved&&downNode.href){window.location.href=downNode.href;}downNode=null;panning=false;cv.classList.remove('dragging');});
  cv.addEventListener('wheel',function(e){e.preventDefault();var m=posn(e),s=Math.exp(-e.deltaY*0.0012);
    view.x=m.x-(m.x-view.x)*s;view.y=m.y-(m.y-view.y)*s;view.k*=s;draw();},{passive:false});

  // tools: legend filters + cross toggle + fit
  var tools=document.getElementById('tools');
  Object.keys(groups).forEach(function(g){if(g==='Other')return;
    var b=document.createElement('button');b.setAttribute('aria-pressed','true');
    b.innerHTML='<span class="dot" style="background:'+groups[g]+'"></span>'+g.replace(' & Readiness','').replace(' (to-be)','');
    b.onclick=function(){off[g]=!off[g];b.setAttribute('aria-pressed',off[g]?'true':'false');draw();};
    tools.appendChild(b);});
  document.getElementById('toggle-cross').onclick=function(){showCross=!showCross;this.setAttribute('aria-pressed',showCross?'true':'false');draw();};
  document.getElementById('fit').onclick=fit;

  resize();fit();
})();
"""


if __name__ == "__main__":
    sys.exit(main())
