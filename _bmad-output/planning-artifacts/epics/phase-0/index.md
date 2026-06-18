---
parent: 'epics/index.md'
phase: 0
phaseName: 'Foundations'
status: 'integrations-first-restructure-executed-2026-06-17-pending-revalidation'
storiedAt: '2026-05-15'
validatedAt: '2026-05-15 (SUPERSEDED — see revisionNote)'
revisedAt: '2026-06-17'
revisionNote: 'Integrations-first restructure EXECUTED (SCP 2026-06-17 / architecture decision #12): Phase 0 re-sequenced from 4 epics into 5, ingestion-first. New: Epic 0.1 (Upstream JOH/MRD ingestion — the first deliverable; ram-reference-data scaffolded first, carrying the relocated shared-estate Terraform), Epic 0.2 (auth + UI), Epic 0.3 (Reference Data read-only API + tier-(b) tables — sits after auth because the jurisdiction-filtered API needs JWTFilter + authz/check), Epic 0.4 (user bootstrap), Epic 0.5 (notification). Story count 12 → 14 (+2 from splitting the old combined ram-reference-data scaffold/tables/sync story 0.1.3 into 0.1.1/0.1.2/0.1.3 — no scope added, no stories removed). No ram-integrations repo: ingestion stays in-process in ram-reference-data. Revalidation via the SSCS-cohort implementation-readiness check.'
revisionNotePrior: 'SCP 2026-06-10 cascade (2026-06-11): Phase 0 Data Migration ETL retracted (revised D3); reference data ingested from JOH eLinks + MRD; user records bootstrapped outside the PRD scope (restructured D9); two-population identity; jurisdiction dimension; FR58–FR61 → FR57–FR60; story count 11 → 12.'
---

# Phase 0 — Foundations

> **✅ Integrations-first restructure executed — [SCP 2026-06-17](../../sprint-change-proposal-2026-06-17.md) (architecture decision #12).** Phase 0 is sequenced **integrations-first**: Epic 0.1 ingestion → Epic 0.2 auth + UI → Epic 0.3 read API → Epic 0.4 bootstrap → Epic 0.5 notification. Story count 12 → 14. Rationale and the in-process / no-`ram-integrations` decision are recorded in the SCP and architecture decision #12. The OLD→NEW mapping:
>
> | OLD (≤2026-06-11) | NEW (2026-06-17) |
> |---|---|
> | Epic 0.1 *User authenticates* (incl. ingestion), 7 stories | **Epic 0.1 *Upstream JOH/MRD ingestion*** (0.1.1 scaffold+estate, 0.1.2 tier-(a) tables, 0.1.3 eLinks sync, 0.1.4 MRD) — 4 stories |
> | Epic 0.2 *Reference data read-only*, 2 stories | **Epic 0.2 *User authenticates*** (0.2.1 auth scaffold, 0.2.2 mock-auth, 0.2.3 authz, 0.2.4 ram-ui, 0.2.5 sign-in) — 5 stories |
> | Epic 0.3 *User populations bootstrapped*, 1 story | **Epic 0.3 *Reference data read-only API*** (0.3.1 tier-(b) tables, 0.3.2 read API) — 2 stories |
> | Epic 0.4 *Notification scaffolded*, 2 stories | **Epic 0.4 *User populations bootstrapped*** — 1 story |
> | — | **Epic 0.5 *Notification scaffolded*** — 2 stories |

> Phase 0 is the platform smoke-test (per PRD Key Characteristic 4). All API-as-Product standards (versioning, OpenAPI, [RFC 9457](https://datatracker.ietf.org/doc/html/rfc9457), `Deprecation`/`Sunset`) are exercised on Authorisation lookups and Reference Data **reads** before any domain service is built.
>
> The Phase 0 areas in [../framework.md](../framework.md) are an **architectural map**. The five concrete user-value epics below are the **implementation plan** — each delivers a demoable user outcome and consolidates the supporting technical work as stories within the epic.

## Phase 0 scope model

- **No legacy data migration**[^d3] — no data migrates from APEX or GAPS, ever. Judicial-holder reference data is **ingested from upstream sources of truth**: the JOH eLinks API (nightly in-process sync) and MRD (weekly Excel via blob drop). Historical data stays in each jurisdiction's incumbent system.
- **Upstream ingestion is Epic 0.1 — the first deliverable**[^decision12]: eLinks sync (Story 0.1.3) + MRD ingestion (Story 0.1.4). `ram-reference-data` is scaffolded first and carries the shared Azure estate Terraform (AR53). In-process — **no `ram-integrations` repo** (architecture decision #12).
- **Two user populations**[^d9]: JOH users resolve IdP email → `jo_people` → personnel number; HMCTS admin staff resolve via `ram_auth_staff_identities` → RAM-assigned UUID. Both share one authorisation model.
- **Jurisdiction is first-class**[^d8]: authz responses carry roles + jurisdiction + Region/Area scope; reference-data API responses are jurisdiction-filtered; activation flags key on the (jurisdiction, region) tuple (FR57).
- **Admin UI is post-MVP**[^d10]: tier-(b) reference data and user/role/scope maintenance are DBA-via-SQL per runbook.

## Epics

| Epic | Title | Stories | Status |
|---|---|---|---|
| [0.1](epic-0.1-upstream-reference-data-ingested.md) | Upstream JOH/MRD reference data is ingested | 4 | 🟡 pending revalidation |
| [0.2](epic-0.2-user-authenticates.md) | User authenticates and lands on a role-scoped Home page | 5 | 🟡 pending revalidation |
| [0.3](epic-0.3-reference-data-read-only-api.md) | Reference data is served read-only via a versioned, jurisdiction-filtered API | 2 | 🟡 pending revalidation |
| [0.4](epic-0.4-user-populations-bootstrapped.md) | Both user populations are bootstrapped and verifiable against the IdP | 1 | 🟡 pending revalidation |
| [0.5](epic-0.5-system-dispatches-emails.md) | Notification service is scaffolded and contractually ready | 2 | 🟡 pending revalidation |
| **Total** | | **14 stories** | |

## Epic summaries

### Epic 0.1: Upstream JOH/MRD reference data is ingested (4 stories)

**User outcome:** Judicial-holder reference data flows into RAM from its upstream sources of truth — the **JOH eLinks API** (15 `jo_*` entities, nightly in-process sync, Story 0.1.3) and the **MRD** weekly Excel feed (`mrd_*`, Story 0.1.4) — so `jo_people` exists and is current. This is the platform's foundational data layer. `ram-reference-data` is scaffolded first (Story 0.1.1) and carries the shared Azure estate (decision #12 / AR53); tier-(a) tables + write protection are Story 0.1.2.

**FRs covered:** FR1 (the `jo_people` lookup target), FR6 tier-(a), FR7 tier-(a) grants, FR8 (shared config baseline first lands); NFR24, FR59 (structured logs first exercised)

→ [Full epic with stories](epic-0.1-upstream-reference-data-ingested.md)

### Epic 0.2: User authenticates and lands on a role-scoped Home page (5 stories)

**User outcome:** A user from **either identity population** — JOH (Judge, Tribunal Judge, Tribunal Member) or HMCTS admin staff (RSU, Court user, Tribunal Caseworker, Finance, MI) — signs in via SSO, has their canonical identity resolved (personnel number via the eLinks-synced `jo_people`; staff UUID via `ram_auth_staff_identities`), and lands on a role-scoped Home page. Depends on Epic 0.1 (`jo_people` populated) and consumes the shared estate provisioned there.

**FRs covered:** FR1, FR2, FR3, FR55, FR56 (business stack); FR57 (activation surface), FR58 (Authorisation read API)

→ [Full epic with stories](epic-0.2-user-authenticates.md)

### Epic 0.3: Reference data is served read-only via a versioned, jurisdiction-filtered API (2 stories)

**User outcome:** Tier-(b) RAM-owned reference data (regions, offices, calendar, operational vocabularies) is created, seeded, and DBA-maintained per runbook[^d10] (Story 0.3.1); all reference data — both tiers — is served by the versioned **read-only**, **jurisdiction-filtered** REST API (Story 0.3.2). Sequenced after Epic 0.2 (depends on `JWTFilter` + `authz/check`).

**FRs covered (Phase 0 surface):** FR6 (tier-(b) maintenance + read API over both tiers), FR7, FR58

→ [Full epic with stories](epic-0.3-reference-data-read-only-api.md)

### Epic 0.4: Both user populations are bootstrapped and verifiable against the IdP (1 story)

**User outcome:** Authorisation records for both populations exist (seeded in dev/CI; programme-bootstrapped in production per the runbook) with all-FALSE (jurisdiction, region) activation flags, and a re-runnable **bootstrap-verification job** proves every user maps to an IdP principal — a standing wave-cutover gate artefact (also used at the pre-Phase-9 IdP cutover per G1.3).

**FRs covered (Phase 0 surface):** FR1 (lookup data), FR4 (MVP data-layer criterion), FR57 (initial flag state)

→ [Full epic with stories](epic-0.4-user-populations-bootstrapped.md)

### Epic 0.5: Notification service is scaffolded and contractually ready (2 stories)

**User outcome:** `ram-notification` is deployed with its API contract published, the `ram_notification_dispatches` delivery-log table created, SMTP integration configured, and `POST /v1/notifications/send` working. The contract is consumable from Phase 2+ via **user-JWT propagation**. Integration testing in MVP happens via Postman — **no admin UI**.

**FRs covered:** FR9

→ [Full epic with stories](epic-0.5-system-dispatches-emails.md)

## Phase 0 Epic Stories Summary

| Epic | Stories | FRs covered | Phase 0 demo |
|---|---|---|---|
| 0.1 | 4 stories (0.1.1–0.1.4) | FR1 (`jo_people` target), FR6 tier (a), FR7 tier (a), FR8, FR59; NFR24 | JOH/MRD reference data flows in from eLinks + MRD → `jo_people` current (verified via `ram_sync_status` + CI WireMock stub) |
| 0.2 | 5 stories (0.2.1–0.2.5) | FR1, FR2, FR3, FR55, FR56, FR57 (activation surface), FR58 | User (either population) signs in via mock-auth → `ram-authorisation` resolves identity/roles/jurisdiction → role-scoped Home renders |
| 0.3 | 2 stories (0.3.1–0.3.2) | FR6 (tier b + read API), FR7, FR58 | Jurisdiction-filtered Reference Data API serves both tiers read-only |
| 0.4 | 1 story (0.4.1) | FR1 (lookup data), FR4 (data layer), FR57 (flag bootstrap) | Seeded users across both populations verified against the IdP; Epic 0.2 sign-in works against them |
| 0.5 | 2 stories (0.5.1–0.5.2) | FR9 | `POST /v1/notifications/send` works end-to-end via Postman against Mailpit |
| **Total** | **14 stories** | | The five demos chain together for the Phase 0 stakeholder walkthrough |

**Cross-cutting NFRs verified across Phase 0 stories:** NFR10 (TLS), NFR11 (data-at-rest), NFR12 (JWT propagation), NFR13 (authz enforcement incl. jurisdiction), NFR14 (no forbidden data), NFR15 (change trails per runbooks + delivery log), NFR16 (Key Vault incl. eLinks credential), NFR17–NFR19 (business UI WCAG — admin UI deferred), NFR20 (HMCTS IdP integration via mock), NFR22 (HMCTS email), NFR24 (JOH eLinks + MRD MVP integrations), NFR25–NFR28 (observability), NFR31 (Azure UK South), NFR39 (API-as-Product), NFR40 (per-service deployable), NFR42 (Postman collections).

## Post-MVP roadmap items

1. **`ram-admin-ui` repo** — scaffolding + auth wrapper + GOV.UK Design System admin theme[^d10]
2. **Reference Data maintenance module** (tier (b) only) in `ram-admin-ui`
3. **Users & Roles admin module** in `ram-admin-ui` — search, edit roles / jurisdiction / Region-Area scope
4. **Reference Data API write endpoints** (tier (b) only) — `POST/PUT/PATCH/DELETE`, admin-gated
5. **`ram-authorisation` admin write endpoints**
6. **Admin "Send Test Email" UI**
7. **Delivery-log viewer UI**
8. **Activation-flag toggle UI** (per (jurisdiction, region))

Tier-(a) reference data never gets a write surface in any phase (corrections at source per FR6), and there is no migration-reports surface — there is no migration to report on[^d3].

Not post-MVP (lands in a later MVP phase): **OAuth `client_credentials` flow** for batch / scheduled callers — Phase 6 alongside `ram-payment-batch`. *(The eLinks sync and MRD pick-up need no service identity — they run in-process inside `ram-reference-data`.)*

## Validation

- Phase 0 awaits validation via the **SSCS-cohort implementation-readiness assessment**[^d11]. The prior [validation report (2026-05-15)](validation-report-2026-05-15.md) assessed a superseded plan and no longer applies.

[^d3]: Revised D3 (2026-06-10) — no data migration from any legacy system; judicial-holder reference data is ingested from the JOH eLinks API and MRD.
[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d9]: Restructured D9 (2026-06-10) — two user populations: JOHs resolve via jo_people to a personnel number; HMCTS admin staff via a RAM-internal identity table. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
[^d11]: D11 (2026-06-10) — SSCS-first pilot: wave 1 replaces the combined ListAssist/GAPS usage for SSCS; waves 2+ replace JI/APEX per Courts region.
[^decision12]: Architecture decision #12 (2026-06-17, SCP 2026-06-17) — integrations-first Phase 0 carve-out; `ram-reference-data` scaffolded first and carries the shared estate; no `ram-integrations` repo; read API stays downstream of auth.
