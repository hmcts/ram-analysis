---
type: 'FR Coverage Map'
title: 'FR Coverage Map'
description: 'This is the canonical FR-to-Epic mapping. It is updated each time a phase advances from framework to concrete epics + stories.'
resource: 'epics/fr-coverage-map.html'
tags: [ram-pathfinder, epics, sscs]
timestamp: '2026-06-17'
parent: 'epics/index.md'
purpose: 'Single source of truth for FR → Epic mapping across all phases'
revisedAt: '2026-06-17'
revisionNote: 'Integrations-first restructure (SCP 2026-06-17 / architecture decision #12): Phase 0 re-mapped to the new 5-epic structure — Epic 0.1 ingestion (jo_*/mrd_* + eLinks sync + MRD), Epic 0.2 auth+UI, Epic 0.3 reference-data read API (+ tier-(b) tables), Epic 0.4 user bootstrap, Epic 0.5 notification. Story-level references and epic file names updated throughout the Phase 0 table.'
revisionNotePrior: 'SCP 2026-06-10 cascade (2026-06-11): ETL FR retracted; FR58–FR61 renumbered FR57–FR60 (60 FRs); upstream ingestion mapped to Epic 0.1; two-population identity; jurisdiction dimension; JOH terminology; Phase 9+ jurisdiction-first.'
---

# FR Coverage Map

This is the canonical FR-to-Epic mapping. It is updated each time a phase advances from framework to concrete epics + stories. The Phase × Area framework in [framework.md](framework.md) is the architectural spine; this map is the implementation index.

## Phase 0 (concrete epics 0.1–0.5 — integrations-first restructure 2026-06-17 / decision #12; pending SSCS-cohort revalidation)

| FR | Phase 0 epic / coverage | Post-MVP residual? | Notes |
|---|---|---|---|
| FR1 | [Epic 0.2](phase-0/epic-0.2-user-authenticates.md) (sign-in + two-population identity resolution, Stories 0.2.3/0.2.5) + [Epic 0.1](phase-0/epic-0.1-upstream-reference-data-ingested.md) (`jo_people` ingested — the JOH lookup target) + [Epic 0.4](phase-0/epic-0.4-user-populations-bootstrapped.md) (the auth records resolved against) | — | IdP email → `jo_people` personnel number (JOH) or `ram_auth_staff_identities` UUID (staff),[^d9] |
| FR2 | [Epic 0.2](phase-0/epic-0.2-user-authenticates.md) Story 0.2.3 | — | Authorisation principal → roles + **jurisdiction** + Region/Area scope (read-only API) |
| FR3 | [Epic 0.2](phase-0/epic-0.2-user-authenticates.md) Story 0.2.3 | — | `GET /v1/users/{id}/effective-permissions` |
| **FR4** | **Data layer only** in [Epic 0.4](phase-0/epic-0.4-user-populations-bootstrapped.md) (auth tables maintainable by DBAs via SQL per the identity-bootstrap runbook) | **YES — UI surface** for sysadmins **is post-MVP**[^d10] | Bootstrap mechanism itself is outside the PRD's scope[^d9] |
| FR5 | — | — | Post-MVP per PRD v2.5 (intentional deferral; pre-existing) |
| **FR6** | **Tier (a)**: [Epic 0.1](phase-0/epic-0.1-upstream-reference-data-ingested.md) Story 0.1.2 (tables) + Stories 0.1.3/0.1.4 (eLinks sync + MRD ingestion — read-only in RAM, corrections at source). **Tier (b)**: [Epic 0.3](phase-0/epic-0.3-reference-data-read-only-api.md) Story 0.3.1 (tables + seed + DBA runbook). Read API over both tiers: Story 0.3.2. | **YES — tier-(b) RSU maintenance UI** is post-MVP[^d10]. Tier (a) never gets a RAM write surface in any phase. | Two ownership tiers in separate tables preserve lineage |
| FR7 | [Epic 0.1](phase-0/epic-0.1-upstream-reference-data-ingested.md) Story 0.1.2 (tier-(a) grants) + [Epic 0.3](phase-0/epic-0.3-reference-data-read-only-api.md) Story 0.3.1 (tier-(b) grants + pattern complete) | — | Direct SQL via SELECT grants; **writes follow the tier** (ingestion for tier (a); DBA SQL for tier (b)) |
| FR8 | distributed (lands in [Epic 0.1](phase-0/epic-0.1-upstream-reference-data-ingested.md) Story 0.1.1 first) | — | Shared `ram_configuration_values` Liquibase baseline changelog |
| FR9 | [Epic 0.5](phase-0/epic-0.5-system-dispatches-emails.md) | — | Notification dispatch + delivery log (`ram_notification_dispatches`). User-JWT propagation only at Phase 0; `client_credentials` flow moved to Phase 6 |
| FR55 | [Epic 0.2](phase-0/epic-0.2-user-authenticates.md) Story 0.2.5 | — | Home shell with role-scoped navigation |
| FR56 | [Epic 0.2](phase-0/epic-0.2-user-authenticates.md) (business stack) | **Partial — admin stack** is post-MVP[^d10] | `ram-ui` delivered in Phase 0; `ram-admin-ui` post-MVP |
| **FR57** *(was FR58)* | [Epic 0.4](phase-0/epic-0.4-user-populations-bootstrapped.md) (initial all-FALSE flag state keyed by (jurisdiction, region)) — cutover orchestration in Phase 9+ (per-wave flip via direct SQL by DBA) | **Partial — activation toggle UI** is post-MVP | Cutover: `UPDATE ram_auth_user_activation_flags SET activated = TRUE WHERE jurisdiction = '…' AND region = '…'` per rollout runbook |
| **FR58** *(was FR59)* | [Epic 0.2](phase-0/epic-0.2-user-authenticates.md) Story 0.2.3 (Authorisation read API — first exercise) + [Epic 0.3](phase-0/epic-0.3-reference-data-read-only-api.md) Story 0.3.2 (Reference Data read API) + every service story | — | API-as-Product read-side standards |
| **FR59** *(was FR60)* | [Epic 0.1](phase-0/epic-0.1-upstream-reference-data-ingested.md) Story 0.1.1 (first exercise — first scaffolded service) + every service story | — | Structured logs + correlation IDs |
| *(NFR24)* | [Epic 0.1](phase-0/epic-0.1-upstream-reference-data-ingested.md) Stories 0.1.3/0.1.4 | MRD reader swaps to API post-MVP (when MRD APIs ship) | JOH eLinks + MRD are MVP integrations[^d11] — the programme's first deliverable under the integrations-first carve-out (decision #12) |

> There is no data-migration FR: the former Phase 0 ETL was retracted[^d3] and FR58–FR61 became FR57–FR60. Reference data arrives via upstream ingestion (Epic 0.1, now the first epic under the integrations-first carve-out / decision #12); user records are bootstrapped outside the PRD's scope[^d9]; tier-(a) corrections happen at source and tier-(b) changes follow the DBA runbook change-trail.

## Phases 1–9+ (FR10–FR54, FR60) — pending

To be populated by subsequent runs of `bmad-create-epics-and-stories` step 2 against the corresponding Phase × Area entries in [framework.md](framework.md). Phase 0 sets the pattern; later phases follow the same vertical-slice user-value framing.

| FR | Phase | Area | Status |
|---|---|---|---|
| FR10–FR18 | 1 | JOH Records & Working Patterns (profiles are *views* over tier (a) + `ram-joh` overlays; FR14 is display-only — conversions happen upstream) | ⚪ |
| FR19–FR22 | 2 | Absence Workflow (first user-initiated Notification consumer via FR20 ack email) | ⚪ |
| FR23–FR28 | 3 | Vacancy & Cover | ⚪ |
| FR29–FR34 | 4 | Booking Management (second user-initiated Notification consumer via FR32 ack email; bookings reference JOHs by `personnel_number`) | ⚪ |
| FR35–FR40 | 5 | Sitting Management | ⚪ |
| FR41 | 6 | Payment Processing | ⚪ |
| FR42, FR43, FR45 | 6 | Payment Batch (**first non-user-initiated Notification consumer** — `client_credentials` flow established here) | ⚪ |
| FR44, FR46, FR47 | 6 | Payment Processing (JFEPS preserved for SSCS wave 1[^d11]/NFR21) | ⚪ |
| FR48–FR52 | 7 | Itineraries | ⚪ |
| FR53, FR54 | 8 | MI Feed & Reporting (external case-management systems consume from Phase 9[^d12] — read-only) | ⚪ |
| FR60 *(was FR61)* | 9+ | Wave Rollout (jurisdiction-first: SSCS/GAPS-experienced UAT wave 1; Courts/APEX-experienced waves 2+) | ⚪ |

## Post-MVP roadmap (consolidated, revised 2026-06-11)

| Capability | Owner |
|---|---|
| `ram-admin-ui` repo scaffold + auth wrapper | Post-MVP UI programme |
| Reference Data maintenance module (**tier (b) only**) | Post-MVP UI programme |
| Reference Data API write endpoints (**tier (b) only**) | Post-MVP — paired with the admin UI |
| `ram-authorisation` admin write endpoints | Post-MVP — paired with the admin UI |
| Users & Roles admin module (roles, jurisdiction, Region/Area scope) | Post-MVP UI programme |
| Admin "Send Test Email" UI | Post-MVP UI programme |
| Delivery-log viewer UI | Post-MVP UI programme |
| Activation-flag toggle UI (per (jurisdiction, region)) | Post-MVP UI programme |
| MRD API integration (replaces the Excel blob-drop reader) | Post-MVP — when MRD ships public APIs (the tables and consumers are unchanged; only the reader swaps) |

[^d3]: Revised D3 (2026-06-10) — no data migration from any legacy system; judicial-holder reference data is ingested from the JOH eLinks API and MRD.
[^d9]: Restructured D9 (2026-06-10) — two user populations: JOHs resolve via jo_people to a personnel number; HMCTS admin staff via a RAM-internal identity table. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
[^d11]: D11 (2026-06-10) — SSCS-first pilot: wave 1 replaces the combined ListAssist/GAPS usage for SSCS; waves 2+ replace JI/APEX per Courts region.
[^d12]: D12 (2026-06-10) — RAM is the system of record for JOH availability and scheduling only; case and hearing management live in external systems.
