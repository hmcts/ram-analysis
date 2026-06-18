---
name: feedback-memory-only-when-requested
description: Do not proactively update memory after each change; only persist to memory when the user explicitly asks
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b2c7954d-1858-4630-a31b-2701d9b434da
---

Do **not** update the auto-memory after every task/change. Only write to memory when Ramnish explicitly requests it.

**Why:** Frequent per-change memory writes create churn the user doesn't want (raised 2026-06-17, after I appended a project-state note following each BMAD step / the scaffolding reconciliation).

**How to apply:** Finish the work and report it in-conversation. Skip the reflexive "update project state memory" step unless asked (e.g. "remember this", "save to memory"). Genuine standing preferences/corrections like this one are the exception worth persisting. See [[project-bmad-ram-pathfinder-state]] — keep it as-is; don't keep appending to it unprompted.
