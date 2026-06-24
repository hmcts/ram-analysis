# ram-analysis

Programme analysis and target-state planning workspace for **RAM Pathfinder** — HMCTS's greenfield rebuild of the Judicial Itineraries (JI) system.

This repository is **not** the implementation. Per-service code will live in separate `ram-*` repositories (`ram-judge`, `ram-booking`, …). This repository holds the PRD, architecture, epics, AS-IS analysis of legacy JI, and the supporting tooling used to produce them.

## Programme summary

- **Legacy system: JI (Judicial Itineraries).** Plans, allocates, confirms and pays judicial sittings across Civil, Family and Crown Courts. Runs on Oracle APEX (OPT) — an unsupported platform with a fixed end-of-life. Board-endorsed for full replacement.
- **Replacement: RAM Pathfinder.** API-driven greenfield rebuild. Java 25 + Spring Boot 4 on Azure (AKS + APIM + PostgreSQL 17 + Key Vault), HMCTS IdP via OIDC, React + GOV.UK Design System UI. Replicates APEX's functional surface, then becomes the integration platform that downstream HMCTS programmes (DA&I, finance, Tribunals coverage, Actuals, Scheduling & Listing) consume directly — replacing today's export-by-email model.
- **Strategy: greenfield, not strangler.** APEX does not support strangler decomposition. RAM Pathfinder is built end-to-end before any user moves; per-region phased cutover with a per-user activation flag (FR58); APEX runs unchanged for non-migrated regions during rollout. No dual-write, no event bus, no synchronisation layer.
- **Parity verification: manual UAT by APEX-experienced users** (D5 revised). No automated APEX-comparison harness.

## Service decomposition (11 services + UI)

| Cluster | Service | Responsibility |
|---|---|---|
| Domain | `ram-judge` | Judges, working patterns, tickets, jurisdictional split |
| Domain | `ram-absence` | Absence records + approval workflow; triggers vacancy creation |
| Domain | `ram-vacancy` | Cover-required vacancies; `filled` flag UPDATE-granted to Booking |
| Domain | `ram-booking` | Fee-paid bookings + verification |
| Domain | `ram-sitting` | Salaried-judge sittings; verification; AM/PM split |
| Domain | `ram-payment` | Payments + reconciliation; JFEPS-shaped Excel schedule via Notification |
| Cross-cutting | `ram-authorisation` | Per-request authz; users, roles, Region/Area scope, activation flags |
| Cross-cutting | `ram-reference-data` | Regions, offices, calendar periods, 12 vocabularies |
| Cross-cutting | `ram-notification` | Outbound transactional email + JFEPS schedule emails |
| Read-model | `ram-itinerary` | Court + Judge itinerary; Forward Look; SQL JOINs over the shared schema |
| Read-model | `ram-mi-feed` | Aggregate reports; DA&I consumer feed (post-MVP); aggregate-only, no case-level data |
| Frontend | `ram-ui` | Single SPA; per-domain modules; GOV.UK Design System; WCAG 2.2 AA |
| Non-prod | `ram-mock-auth` | OIDC issuer for dev / CI / integration — never deployed to production |

## Programme state (as of last update)

| Artefact | Status | Source |
|---|---|---|
| PRD (FR1–FR61, NFR1–NFR42, D1–D10) | Complete 2026-05-05 | [`_bmad-output/planning-artifacts/prd.md`](_bmad-output/planning-artifacts/prd.md) |
| Architecture summary (v2.2) | 2026-05-08 | [`_bmad-output/planning-artifacts/architecture-summary.md`](_bmad-output/planning-artifacts/architecture-summary.md) |
| Architecture deep-dive (decisions, alternatives, AR list) | Aligned with summary | [`_bmad-output/planning-artifacts/architecture.md`](_bmad-output/planning-artifacts/architecture.md) |
| Phase 0 epics (Auth, Ref Data, Users/Roles, Notification) | Drafted; restructured 2026-05-15 | [`_bmad-output/planning-artifacts/epics/phase-0/`](_bmad-output/planning-artifacts/epics/phase-0/) |
| Sprint Change Proposal (D10: Admin UI deferred, no `gh` CLI) | 2026-05-15 | [`_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-15.md`](_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-15.md) |
| Implementation Readiness Report (latest) | 2026-05-15-rev2 | [`_bmad-output/planning-artifacts/implementation-readiness-report-2026-05-15-rev2.md`](_bmad-output/planning-artifacts/implementation-readiness-report-2026-05-15-rev2.md) |
| AS-IS analysis (legacy JI on APEX) | Captured | [`resources/architecture/asis/`](resources/architecture/asis/) |
| TO-BE artefacts | Empty placeholder | [`resources/architecture/tobe/`](resources/architecture/tobe/) |

The PRD and the architecture summary are the authoritative documents. The HTML renders under [`docs/`](docs/) mirror the Markdown sources in `_bmad-output/planning-artifacts/` for browser viewing — when content differs, the Markdown wins.

## Recent direction changes worth knowing

- **D10 (2026-05-15) — Admin UI deferred post-MVP.** `ram-admin-ui` and admin-write API endpoints on `ram-reference-data` and `ram-authorisation` move to the Growth Features list. Reference data and users continue to be loaded in MVP via direct-SQL ETLs; named-owner sign-off happens via versioned git commits to a `signoffs/` directory; ongoing operational maintenance is DBA via direct SQL per runbooks.
- **D10 (2026-05-15) — No `gh` CLI in the engineering environment.** All GitHub admin operations (private repo creation, branch protection, CODEOWNERS, PR open/review/merge) are performed manually via the GitHub web UI. The `ram-scaffold.sh` script handles local scaffold + `git push` only.
- **D5 revised (2026-05-06) — UAT is manual, by APEX-experienced users.** No automated APEX-comparison harness. UAT sign-off is the per-wave cutover gate.
- **D9 + D10 — Phase 0 ETL loads via direct SQL INSERT**, not via the Reference Data and Authorisation APIs. The API-as-Product standards (versioning, OpenAPI, deprecation via [RFC 9745](https://datatracker.ietf.org/doc/html/rfc9745) + [RFC 8594](https://datatracker.ietf.org/doc/html/rfc8594)) are exercised on **read endpoints** before any domain service is built.

## Repository layout

```
ram-analysis/
├── _bmad-output/
│   ├── planning-artifacts/     # PRD, architecture, epics, sprint change proposals, readiness reports
│   └── brainstorming/          # Early discovery sessions (Apr–May 2026)
├── docs/                       # HTML renders of the planning artefacts for browser viewing
│   ├── architecture/
│   ├── asis/                   # AS-IS HTML renders
│   ├── epics/
│   └── *.html                  # PRD, architecture, sprint-change-proposal, readiness reports
├── resources/
│   ├── analysis/               # Meeting transcript summaries and similar raw analysis input
│   └── architecture/
│       ├── asis/               # AS-IS JI: data dependencies, functional modules, integration deps, components
│       └── tobe/               # Placeholder for TO-BE (RAM Pathfinder) artefacts
├── sql/                        # Mock data (judge + reference data) for development sandboxes
├── openspec/                   # Change-driven spec workflow (specs + changes)
├── scripts/                    # Local helpers (HTML build, schema diagram renderer)
├── .claude/                    # Analysis toolchain — four slash commands (see docs/claude-skills.md)
└── _bmad/                      # BMAD-METHOD plugin (gitignored; user-local install)
```

## How to navigate as a new joiner

1. **Read [`architecture-summary.md`](_bmad-output/planning-artifacts/architecture-summary.md) first** — one-page target-state reference.
2. **Then [`prd.md`](_bmad-output/planning-artifacts/prd.md)** — scope, decisions (D1–D10), success criteria, the five canonical user journeys, FR/NFR contracts.
3. **Then [`architecture.md`](_bmad-output/planning-artifacts/architecture.md)** — decision history, alternatives considered, gap (G1–G7) and assumption (A1–A35) registers, data-table inventory, conventions.
4. **Scan [`sprint-change-proposal-2026-05-15.md`](_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-15.md)** — most recent product-direction shifts.
5. **For delivery state**, walk the Phase 0 epics under [`epics/phase-0/`](_bmad-output/planning-artifacts/epics/phase-0/) and the latest implementation-readiness report.
6. **For legacy context**, read the AS-IS pack under [`resources/architecture/asis/`](resources/architecture/asis/) — particularly `functional-modules.md`, `data-dependencies.md` and `integration-dependencies.md`.

## Analysis toolchain

Four Claude Code slash commands were built to produce parts of the AS-IS pack and to run repeatable analyses on input documents and source code:

| Command | Output |
|---|---|
| `/docs-to-c4` | Browsable C4 architecture model (Structurizr DSL + static site) from a folder of source documents |
| `/create-data-dependency-architecture` | Styled PDF cataloguing inbound + outbound data dependencies |
| `/create-functional-modules-architecture` | Styled PDF cataloguing functional modules |
| `/check-for-owasp-top10` | Markdown + PDF audit against OWASP Top 10 for Agentic Applications 2026 |

The commands live in `.claude/commands/` with their pipelines in `.claude/lib/<command>/`. A shared house-style PDF pipeline at `.claude/lib/_shared/` is consumed by three of the four. Full prerequisites, usage and output shapes: see [`docs/claude-skills.md`](docs/claude-skills.md). Operating contract for Claude Code instances working in this repo: see [`CLAUDE.md`](CLAUDE.md).

## License

[MIT License](LICENSE).
