---
parent: 'epics/index.md'
phase: 0
phaseName: 'Foundations'
status: 'restructured-pending-revalidation'
storiedAt: '2026-05-15'
validatedAt: '2026-05-15 (SUPERSEDED — see revisionNote)'
revisedAt: '2026-06-11'
revisionNote: 'SCP 2026-06-10 cascade: the Phase 0 Data Migration ETL is retracted (revised D3) — reference data is ingested from JOH eLinks + MRD (now Stories 0.1.3/0.1.4); user records are bootstrapped outside the PRD''s scope (restructured D9). Two-population identity, jurisdiction dimension, FR renumbering FR58–FR61 → FR57–FR60. Story count 11 → 12. The 2026-05-15 validation assessed the Courts cohort + ETL world and is superseded; revalidation happens via the SSCS-cohort implementation-readiness check.'
---

# Phase 0 — Foundations

> Phase 0 is the platform smoke-test (per PRD Key Characteristic 4). All API-as-Product standards (versioning, OpenAPI, [RFC 9457](https://datatracker.ietf.org/doc/html/rfc9457), `Deprecation`/`Sunset`) are exercised on Reference Data **reads** and Authorisation lookups before any domain service is built.
>
> The Phase 0 areas in [../framework.md](../framework.md) are an **architectural map**. The four concrete user-value epics below are the **implementation plan** — each delivers a demoable user outcome and consolidates the supporting technical work as stories within the epic.

## Phase 0 scope model

- **No legacy data migration**[^d3] — no data migrates from APEX or GAPS, ever. Judicial-holder reference data is **ingested from upstream sources of truth**: the JOH eLinks API (nightly in-process sync) and MRD (weekly Excel via blob drop). Historical data stays in each jurisdiction's incumbent system.
- **Upstream ingestion lives in Epic 0.1** — JOH sign-in resolves identity against `jo_people`, so the eLinks sync (Story 0.1.3) and MRD ingestion (Story 0.1.4) are part of the authentication vertical slice, and the first external integration the programme tackles.
- **Two user populations**[^d9]: JOH users resolve IdP email → `jo_people` → personnel number; HMCTS admin staff resolve via `ram_auth_staff_identities` → RAM-assigned UUID. Both share one authorisation model.
- **Jurisdiction is first-class**[^d8]: authz responses carry roles + jurisdiction + Region/Area scope; reference-data API responses are jurisdiction-filtered; activation flags key on the (jurisdiction, region) tuple (FR57).
- **Admin UI is post-MVP**[^d10]: tier-(b) reference data and user/role/scope maintenance are DBA-via-SQL per runbook.

## Epics

| Epic | Title | Stories | Status |
|---|---|---|---|
| [0.1](epic-0.1-user-authenticates.md) | User authenticates and lands on a role-scoped Home page (incl. JOH eLinks + MRD ingestion) | 7 | 🟡 pending revalidation |
| [0.2](epic-0.2-reference-data-read-only.md) | RAM-owned reference data is maintained and all reference data is served read-only | 2 | 🟡 pending revalidation |
| [0.3](epic-0.3-user-populations-bootstrapped.md) | Both user populations are bootstrapped and verifiable against the IdP | 1 | 🟡 pending revalidation |
| [0.4](epic-0.4-system-dispatches-emails.md) | Notification service is scaffolded and contractually ready | 2 | 🟡 pending revalidation |
| **Total** | | **12 stories** | |

## Epic summaries

### Epic 0.1: User authenticates and lands on a role-scoped Home page (7 stories)

**User outcome:** A user from **either identity population** — JOH (Judge, Tribunal Judge, Tribunal Member) or HMCTS admin staff (RSU, Court user, Tribunal Caseworker, Finance, MI) — signs in via SSO, has their canonical identity resolved (personnel number via the eLinks-synced `jo_people`; staff UUID via `ram_auth_staff_identities`), and lands on a role-scoped Home page. The epic includes the **JOH eLinks nightly sync** (0.1.3) and **MRD weekly ingestion** (0.1.4) because `jo_people` is the JOH identity-lookup target — sign-in depends on it.

**FRs covered:** FR1, FR2, FR3, FR55, FR56 (business stack); FR6/FR7 tier-(a) ingestion portion (NFR24)

→ [Full epic with stories](epic-0.1-user-authenticates.md)

### Epic 0.2: RAM-owned reference data is maintained and all reference data is served read-only (2 stories)

**User outcome:** Tier-(b) RAM-owned reference data (regions, offices, calendar, operational vocabularies) is created, seeded, and DBA-maintained per runbook[^d10]; all reference data — both tiers — is served by the versioned **read-only**, **jurisdiction-filtered** REST API.

**FRs covered (Phase 0 surface):** FR6 (tier-(b) maintenance + read API), FR7, FR58, FR59

→ [Full epic with stories](epic-0.2-reference-data-read-only.md)

### Epic 0.3: Both user populations are bootstrapped and verifiable against the IdP (1 story)

**User outcome:** Authorisation records for both populations exist (seeded in dev/CI; programme-bootstrapped in production per the runbook) with all-FALSE (jurisdiction, region) activation flags, and a re-runnable **bootstrap-verification job** proves every user maps to an IdP principal — a standing wave-cutover gate artefact (also used at the pre-Phase-9 IdP cutover per G1.3).

**FRs covered (Phase 0 surface):** FR1 (lookup data), FR4 (MVP data-layer criterion), FR57 (initial flag state)

→ [Full epic with stories](epic-0.3-user-populations-bootstrapped.md)

### Epic 0.4: Notification service is scaffolded and contractually ready (2 stories)

**User outcome:** `ram-notification` is deployed with its API contract published, delivery log table created, SMTP integration configured, and `POST /v1/notifications/send` working. The contract is consumable from Phase 2+ via **user-JWT propagation**. Integration testing in MVP happens via Postman — **no admin UI**.

**FRs covered:** FR9

→ [Full epic with stories](epic-0.4-system-dispatches-emails.md)

## Phase 0 Epic Stories Summary

| Epic | Stories | FRs covered | Phase 0 demo |
|---|---|---|---|
| 0.1 | 7 stories (0.1.1–0.1.7) | FR1, FR2, FR3, FR8, FR55, FR56, FR57 (activation surface), FR58, FR59; FR6/FR7 tier (a) + NFR24 | JOH data flows in from eLinks/MRD → user (either population) signs in → role-scoped Home renders |
| 0.2 | 2 stories (0.2.1–0.2.2) | FR6 (tier b + read API), FR7, FR58, FR59 | Jurisdiction-filtered Reference Data API serves both tiers read-only |
| 0.3 | 1 story (0.3.1) | FR1 (lookup data), FR4 (data layer), FR57 (flag bootstrap) | Seeded users across both populations verified against the IdP; Epic 0.1 sign-in works against them |
| 0.4 | 2 stories (0.4.1–0.4.2) | FR9 | `POST /v1/notifications/send` works end-to-end via Postman against Mailpit |
| **Total** | **12 stories** | | All four demos chain together for the Phase 0 stakeholder walkthrough |

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
