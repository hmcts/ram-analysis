# ram-analysis

Central **planning, analysis, and delivery-coordination hub** for **RAM Pathfinder** — HMCTS's greenfield Judicial Office Holder (JOH) availability-and-scheduling platform.

This repository is **not** the implementation and holds no runtime code. RAM Pathfinder is built as a separate **16-repo polyrepo** (`ram-*` repositories); this repo holds the PRD, architecture, epics/stories, the delivery operating model, the delivery control plane, and the AS-IS analysis of the legacy system. Delivery is **AI-led (Claude Code) using the BMAD method**.

## Programme summary

- **What it replaces (SSCS-first rollout).** Wave 1 replaces **ListAssist** (the SSCS Tribunals judicial-scheduling tool); **GAPS** (SSCS case management) is *retained*, not replaced. Waves 2+ replace the as-is **JI application on Oracle APEX** per Courts region. Scope boundary: availability/scheduling only — case and hearing management live in external systems that consume RAM's APIs.
- **What it is.** API-driven greenfield build. Java 25 + Spring Boot 4 on Azure (AKS + APIM + PostgreSQL 17 + Key Vault), HMCTS IdP via OIDC, React + Vite + GOV.UK Design System UI. Becomes the integration platform downstream HMCTS programmes consume directly, replacing today's export-by-email model.
- **Strategy: greenfield, not strangler.** Built end-to-end before any user moves; **jurisdiction-first then per-region** phased cutover via per-(jurisdiction, region) activation flags (FR57); incumbents run unchanged for non-activated cohorts. No dual-write, no event bus.
- **No legacy data migration** (revised D3). Reference data is **ingested from upstream sources of truth** — the JOH eLinks API (nightly) and MRD (weekly) — not migrated from APEX.
- **Parity verification: manual UAT by jurisdiction-incumbent-experienced users** (D5). No automated incumbent-comparison harness.

Requirements baseline: **60 FRs, 42 NFRs, decisions D1–D12** (see `prd.md`).

## Delivery: the 16-repo polyrepo

Per-service code lives in dedicated repositories (no monorepo; no shared runtime library). The canonical list and rationale are in [`architecture/repository-strategy.md`](_bmad-output/planning-artifacts/architecture/repository-strategy.md).

| Cluster | Repo | Phase | Responsibility |
|---|---|---|---|
| Platform | `ram-shared-infrastructure` | 0 | Shared Azure estate (AKS, PostgreSQL, ACR, APIM, App Insights, Key Vault) — Terraform only |
| Platform | `ram-architecture` | 0 | Architecture docs + ADRs + scaffolding script; the version-pinned **context bus** for service repos |
| Cross-cutting | `ram-mock-auth` | 0 | OIDC issuer for dev / CI / integration — never deployed to production |
| Cross-cutting | `ram-reference-data` | 0 | 33 reference-data tables (two-tier: upstream `jo_*`/`mrd_*` + RAM-owned) + eLinks/MRD ingestion + `ram_joh_identities` |
| Cross-cutting | `ram-authorisation` | 0 | Per-request authz; two-population identity; roles, jurisdiction, Region/Area scope, activation flags |
| Cross-cutting | `ram-notification` | 0 | Outbound transactional email + JFEPS-shaped payment-schedule emails |
| Domain | `ram-joh` | 1 | JOH operational state — working patterns, ticket/location overlays, jurisdictional split |
| Domain | `ram-absence` | 2 | Absence records + approval workflow; triggers vacancy creation |
| Domain | `ram-vacancy` | 3 | Cover-required vacancies; `filled` flag UPDATE-granted to Booking |
| Domain | `ram-booking` | 4 | Fee-paid bookings + verification |
| Domain | `ram-sitting` | 5 | Salaried-JOH sittings; verification; AM/PM split |
| Domain | `ram-payment` | 6 | Payments + reconciliation; JFEPS Excel via a scheduled batch (`ram-payment-batch`) |
| Read-model | `ram-itinerary` | 7 | Court + Judge itinerary; Forward Look; SQL JOINs over the shared schema (no own tables) |
| Read-model | `ram-mi-feed` | 8 | Aggregate reports; DA&I consumer feed (post-MVP); aggregate-only, no case-level data |
| Frontend | `ram-ui` | 0–8 | Business-user SPA; per-domain modules; GOV.UK Design System; WCAG 2.2 AA |
| Frontend | `ram-admin-ui` | post-MVP | Admin SPA (Reference Data + User/Role admin), separated from business workflows |

*JOH identity:* every JOH carries a RAM-assigned UUID (`ram_joh_identities`); `personnel_number` is the upstream link to `jo_people` only (per SCP 2026-07-09).

## How this repository is organised

`_bmad-output/planning-artifacts/` is the **canonical, git-tracked source of truth** (despite living under `_bmad-output/`):

- **PRD & business case** — `prd.md`, `business-case.md`, plus dated validation/readiness reports and `sprint-change-proposal-*` (historical records).
- **Architecture** — `architecture.md` + `architecture/` shards: `repository-strategy.md`, `repo-structure.md`, `conventions.md` (the consistency contract), `data-tables.md`, `delivery-operating-model.md`, `gaps.md`, `assumptions.md`, `changelog.md`, FR/NFR coverage, `diagrams/`, `sequence-diagrams/`.
- **Epics** — `epics/framework.md` + `epics/phase-0/` (stories embedded in each epic; only Phase 0 is decomposed so far — 6 epics, 19 stories).
- **Delivery control plane** — `delivery/dispatch-graph.yaml` (deterministic build order) + `delivery/ledger/` (per-epic traceability shards with `status`+`owner`) + `delivery/README.md`.
- **`project-context.md`** — lean, LLM-optimised implementation rules for the service code.

The [`docs/`](docs/) folder is the **published static HTML site** (GitHub Pages), generated from the Markdown by `scripts/build-html.sh` — the Markdown is authoritative; regenerate rather than hand-editing HTML.

## Delivery operating model

See [`architecture/delivery-operating-model.md`](_bmad-output/planning-artifacts/architecture/delivery-operating-model.md). In brief:

- **Control plane** (this repo) — canonical planning + dispatch + traceability; never edits service code.
- **Context bus** (`ram-architecture`) — version-pinned published architecture each service repo consumes as a submodule; API contracts stay producer-owned (this repo holds a read-only mirror only).
- **Execution units** (the 15 service/UI/infra repos) — where code lands; each receives a self-contained story packet.
- Build order is deterministic (`dispatch-graph.yaml`); progress is tracked per epic in `delivery/ledger/`. BMAD skills map on: create-story = dispatch, dev-story + code-review = execute, sprint-status = signal.

## Repository layout

```
ram-analysis/
├── _bmad-output/
│   ├── planning-artifacts/     # CANONICAL, tracked: PRD, architecture, epics, delivery control plane
│   │   ├── architecture/       # architecture.md shards + diagrams + sequence-diagrams
│   │   ├── epics/              # framework + phase-0 epics (stories embedded)
│   │   └── delivery/          # dispatch-graph.yaml + ledger/ (per-epic shards)
│   ├── project-context.md      # lean implementation rules for service code
│   └── brainstorming/          # local scratch (early discovery)
├── docs/                       # PUBLISHED HTML site (generated by scripts/build-html.sh)
│   └── architecture/asis/      # AS-IS JI analysis pack (source + renders)
├── scripts/                    # build-html.sh + Python helpers (site + diagrams)
├── .claude/
│   ├── commands/ + lib/        # analysis slash commands (supporting tooling)
│   └── hooks/                  # block-git-writes.sh
├── sql/ · queries/ · openspec/ # legacy/exploratory — not part of the delivery workflow
└── _bmad/                      # BMAD-METHOD plugin (gitignored; user-local install)
```

## How to navigate as a new joiner

1. **[`architecture-summary.md`](_bmad-output/planning-artifacts/architecture-summary.md)** — one-page target-state reference.
2. **[`prd.md`](_bmad-output/planning-artifacts/prd.md)** — scope, decisions (D1–D12), success criteria, user journeys, FR/NFR contracts.
3. **[`architecture.md`](_bmad-output/planning-artifacts/architecture.md)** + its shards — decisions, gaps (`gaps.md`), assumptions, data-table inventory, conventions.
4. **[`delivery-operating-model.md`](_bmad-output/planning-artifacts/architecture/delivery-operating-model.md)** + [`delivery/`](_bmad-output/planning-artifacts/delivery/) — how implementation is coordinated across the polyrepo.
5. **[`epics/`](_bmad-output/planning-artifacts/epics/)** — the Phase 0 breakdown and FR coverage map.
6. **[`changelog.md`](_bmad-output/planning-artifacts/architecture/changelog.md)** + the latest `sprint-change-proposal-*` — most recent product-direction shifts.
7. **AS-IS context** — the legacy JI pack under [`docs/architecture/asis/`](docs/architecture/asis/).

Everything renders for browser viewing on the published `docs/` site.

## Analysis toolchain (supporting tooling)

A set of Claude Code slash commands used to produce parts of the AS-IS pack and run repeatable analyses — **not** the deliverable:

| Command | Output |
|---|---|
| `/create-data-dependency-architecture` | Styled PDF cataloguing inbound + outbound data dependencies |
| `/create-functional-modules-architecture` | Styled PDF cataloguing functional modules |
| `/check-for-owasp-top10` | Markdown + PDF audit against the OWASP Top 10 for Agentic Applications 2026 |
| `/docs-to-c4` | *(retired — use the `build_html.py` static-site pipeline instead)* |

Commands live in `.claude/commands/` with pipelines in `.claude/lib/<command>/`; a shared house-style PDF pipeline at `.claude/lib/_shared/` is consumed by the PDF commands. Operating contract for Claude Code instances working here: [`CLAUDE.md`](CLAUDE.md).

## License

[MIT License](LICENSE).
