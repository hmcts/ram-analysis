# Delivery Control Plane

This folder is the **control plane** for RAM Pathfinder delivery. It lives in
`ram-analysis` and orchestrates *what to build next*, *whether it traces to a
requirement*, and *how a finished story reports back* — **without ever editing
service code**. Full rationale: [`../architecture/delivery-operating-model.md`](../architecture/delivery-operating-model.md).

## Files

| File | Role |
|---|---|
| `dispatch-graph.yaml` | Machine-readable build order + dependencies (epic-level). Source of truth for "what is buildable next". |
| `ledger/` | Traceability ledger, **sharded one file per epic** (`ledger/epic-0.x.yaml`) so multiple people update different epics without conflicts. Each shard carries epic-level `status`+`owner` and per-story `status`+`owner`+`pr`. Schema + concurrency rules: [`ledger/README.md`](ledger/README.md). |
| `README.md` | This file — the dispatch/signal loop and how it maps to BMad skills. |

Not here (deliberately): the **context bus** (`ram-architecture` publish + `arch-v1.0` tag) and **per-repo scaffolding** (`ram-scaffold.sh`, `_arch/` submodule, per-repo `CLAUDE.md`) — those are downstream. The control plane only *references* `bus_version` as a string.

## The delivery loop

```
[ram-analysis: control plane]                    [ram-{service}: execution unit]
  1. SELECT next  ── read dispatch-graph + ledger → next buildable epic/story
        │
  2. DISPATCH ──── compile story packet (story + Gherkin ACs + distilled context
        │          + pinned bus_version) → land as docs/stories/<id>.md in repo
        │          ledger: status not-started → dispatched
        │                                                 ▼
        │                                    3. EXECUTE dev-story in the repo
        │                                       (reads CLAUDE.md → _arch/ bus)
        │                                       ledger: dispatched → in-progress → in-review
        │                                                 │  (human commits via VSCode)
  4. SIGNAL ◄──────────────────────────────────────────────┘
        └ ledger: → done, fill `pr`, record bus_version
```

**Buildable-now rule:** an epic is dispatchable iff every epic in its
`depends_on` is `done` in the ledger. Epics with disjoint dependency sets and no
shared state may run **in parallel**.

## BMad skill mapping

| Step | Skill | Runs in |
|---|---|---|
| Select / plan | `bmad-sprint-planning` (reads `dispatch-graph.yaml`) | `ram-analysis` |
| Dispatch | `bmad-create-story` / `compile-epic-context` → story packet | `ram-analysis` |
| Execute | `bmad-dev-story` → `bmad-code-review` | target repo |
| Signal | `bmad-sprint-status` (updates `ledger.yaml`) | `ram-analysis` |

## Conventions

- **Status lifecycle:** `not-started → dispatched → in-progress → in-review → done`.
- **FR granularity:** epic-level unless a story narrows it. Every FR/NFR should trace to at least one story once all phases are decomposed.
- **Git writes are external.** Claude prepares packets, code, and ledger diffs; the human commits via VSCode (per repo CODEOWNERS/branch protection).
- **Bus pinning:** a story records the `bus_version` it was built against; repos re-sync only via an explicit submodule bump.

## Multi-user & ownership

The ledger is **sharded per epic** for conflict-free concurrent updates, and every epic and story carries a `status` and an `owner` so it is always visible who is driving what. Claim-before-you-start (set story `status: dispatched` + `owner` and push) is the coordination primitive. Full rules and the status vocab: [`ledger/README.md`](ledger/README.md).

## Current state (2026-07-09)

- **Phase 0 fully seeded:** 6 epics, 19 stories, all `not-started`, unassigned (`owner: null`).
- **Phases 1–8 + post-MVP:** repo-level placeholders in `dispatch-graph.yaml` under `future:` (`decomposed: false`). Promote each to an epic node with a `stories:` list after running `bmad-create-epics-and-stories` for that phase, and add its rows to `ledger.yaml`.
- **Optional resolver** ("what's buildable now?") is intentionally deferred until dispatch begins.
