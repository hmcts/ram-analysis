---
name: feedback-diagram-tooling-d2
description: Use D2 + ELK for new boxes-and-lines architecture diagrams; Graphviz only for record/table renders; Mermaid for sequence diagrams
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fbd0b611-5a14-4dd5-baa5-5b011a548714
---

Ramnish's standard for new diagrams (decided 2026-06-12 after comparing engines on the RAM Pathfinder system-context diagram): **author boxes-and-lines architecture diagrams in D2 with the ELK layout engine** (`d2 --pad 24 file.d2 file.png`; `scripts/render_diagram.sh` handles `.d2` inputs). Graphviz stays only for record/table-style renders (the as-is DB schema diagrams); Mermaid stays for sequence diagrams.

**Why:** Graphviz's `ortho` mode has no obstacle avoidance (lines cross boxes), no clearance control (lines hug box edges), and can't anchor labels to orthogonal edges. D2+ELK does all three. Ramnish wants orthogonal lines, no criss-crossing over boxes, straight-line paths where possible, compact layouts, and readable in-box font sizes (16pt nodes / 18pt containers / 14pt edge labels worked).

**How to apply:** new diagrams get a `.d2` source next to the rendered `.png`. Layout lessons from the system-context work: ELK layers strictly by arrow direction, so draw service edges in the direction that makes tiers flow top-down (e.g. "cross-cutting *serves* domain", "APIM → external consumer" in the data direction); place external systems as individual adjacent nodes rather than one far-away grouping box (the box is what forces long criss-crossing hauls); avoid invisible helper edges (they add layers); trim node labels to essentials — detail belongs in the architecture text. [[project-bmad-ram-pathfinder-state]]
