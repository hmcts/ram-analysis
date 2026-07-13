# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## What this repository is

`ram-analysis` is the **central planning, analysis, and delivery-coordination hub for RAM Pathfinder** — HMCTS's greenfield Judicial Office Holder (JOH) availability-and-scheduling platform. It is **not** the implementation and holds no runtime application code. RAM Pathfinder ships as a **16-repo polyrepo** (`ram-shared-infrastructure`, `ram-architecture`, `ram-mock-auth`, `ram-reference-data`, `ram-authorisation`, `ram-notification`, `ram-joh`, `ram-absence`, `ram-vacancy`, `ram-booking`, `ram-sitting`, `ram-payment`, `ram-itinerary`, `ram-mi-feed`, `ram-ui`, `ram-admin-ui`); this repo is the **control plane** that plans and coordinates building those repos.

- **Programme:** SSCS-first rollout — wave 1 replaces **ListAssist** (SSCS judicial scheduling; GAPS case-management is *retained*), waves 2+ replace the as-is JI application (Oracle APEX) per Courts region. Scope is availability/scheduling only; case/hearing management stay in external systems that consume RAM's APIs.
- **Delivery is AI-led (Claude Code) using the BMAD method.** The role split is defined in `_bmad-output/planning-artifacts/architecture/delivery-operating-model.md` — read it before coordinating implementation.

This repo also carries a set of **analysis slash commands** (`/create-data-dependency-architecture`, `/create-functional-modules-architecture`, `/check-for-owasp-top10`, `/docs-to-c4`) under `.claude/lib/` and `.claude/commands/`. These are **supporting tooling** used to produce as-is analysis artifacts — not the deliverable. (`/docs-to-c4` is retired; use the `build_html.py` static-site pipeline instead.)

## Where things live

- **`_bmad-output/planning-artifacts/` — the canonical, git-tracked source of truth.** Despite living under `_bmad-output/`, this subtree is committed and authoritative; do NOT treat it as scratch.
  - `prd.md`, `business-case.md`, dated `*-validation-report` / `*-readiness-report` / `sprint-change-proposal-*` (historical records).
  - `architecture.md` + `architecture/` shards: `repository-strategy.md`, `repo-structure.md`, `conventions.md` (the consistency contract), `data-tables.md`, `delivery-operating-model.md`, `gaps.md`, `assumptions.md`, `changelog.md`, `starter-template.md`, `user-types.md`, FR/NFR coverage, plus `diagrams/` and `sequence-diagrams/`.
  - `epics/` — `framework.md` + `phase-0/` epics with **stories embedded inside each epic** (only Phase 0 is decomposed so far; run `bmad-create-epics-and-stories` per phase for 1–8).
  - `delivery/` — the **delivery control plane**: `dispatch-graph.yaml` (deterministic build order) + `ledger/` (traceability, sharded one file per epic, each with epic/story `status` + `owner`) + `README.md`.
- **`_bmad-output/project-context.md`** — lean, LLM-optimised implementation rules for the RAM Pathfinder *service* code; seeds each target repo's context.
- **`docs/` — the published static HTML site** (GitHub Pages), generated from planning-artifacts by `scripts/build-html.sh`. Never hand-edit; regenerate.
- **The rest of `_bmad-output/`** (e.g. `brainstorming/`) is local scratch, not part of any output contract.
- **Legacy/exploratory at repo root** — `sql/`, `queries/`, `openspec/`, and older `scripts/python/` helpers — earlier iterations, not part of the current delivery workflow. Don't wire new work through them.

## Delivery operating model (the coordination contract)

Full detail in `architecture/delivery-operating-model.md`. In brief:

- **Control plane** (this repo) — canonical planning + dispatch + traceability. Never edits service code.
- **Context bus** (`ram-architecture`) — version-pinned published architecture each service repo consumes as a submodule.
- **Execution units** (the 15 service/UI/infra repos) — where code lands; each gets a self-contained story packet.
- Build order is deterministic via `delivery/dispatch-graph.yaml`; progress lives in `delivery/ledger/` (per-epic shards, `status`+`owner` for multi-user coordination).
- BMAD skills map onto it: **create-story = dispatch, dev-story + code-review = execute, sprint-status = signal.**

## Working conventions

- **BMAD is the methodology.** Use the BMAD skills for planning and delivery (`bmad-create-prd`, `bmad-create-architecture`, `bmad-create-epics-and-stories`, `bmad-correct-course`, `bmad-sprint-planning`, `bmad-create-story`, `bmad-dev-story`, etc.). `_bmad/` and `.claude/skills/bmad-*` are gitignored local plugin installs — install the BMAD plugin to get them; don't add them to the repo.
- **Cross-cutting changes: sweep first, don't blind find-replace.** Run a repo-wide sweep for every affected reference, use `bmad-correct-course`, clarify ambiguous terms, record the change in a new Sprint Change Proposal + a `changelog.md` entry, then regenerate `docs/`. Leave dated reports and existing changelog entries as immutable history — add, don't rewrite.
- **Canonical architecture is sharded.** New architecture docs are shards under `architecture/` (sibling of `architecture.md`, linked from it). When adding a shard or a new SCP, add a matching entry to the `NAV` list in `scripts/python/build_html.py` so it appears on the site, then rebuild.
- **Regenerate the site after editing any planning-artifact markdown:** `scripts/build-html.sh`.

## Hard rules

- **Git/GitHub writes are blocked from inside Claude** — a `PreToolUse` hook (`.claude/hooks/block-git-writes.sh`) denies `git commit/push/pull/merge/rebase/reset/checkout/branch/tag/stash/cherry-pick/clean/rm` and any `gh`/`hub` command. Read-only git is allowed. The user reviews and commits externally via VSCode — surface the diff and stop; do not work around the hook.
- **Source documents are read-only.** Analysis/distillation writes to `output/` folders, never the originals.
- **`docs/*.html` is generated — never hand-edit it;** run `scripts/build-html.sh` (reads planning-artifacts → writes `docs/`; also runs `build_graph.py`). Requires `pandoc` + Python 3.

## Common commands

- **Rebuild the published site:** `scripts/build-html.sh`
- **(Analysis tooling) build a styled PDF:** `.claude/lib/_shared/scripts/build-pdf.sh <md>`
- **(Analysis tooling) distil binaries to text:** `.claude/lib/_shared/scripts/distil-binary-data.sh <folder>` → `<folder>/output/extracted-text/`

> The repo-root `.venv/` is stale (it points at the old `ji-analysis` path from a rename) — create a fresh virtualenv for ad-hoc Python rather than reusing it.
