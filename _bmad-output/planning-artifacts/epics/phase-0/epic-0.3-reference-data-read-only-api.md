---
type: 'Epic'
description: 'User outcome: Tier-(b) RAM-owned reference data (Regions, Offices, calendar / financial-year boundaries, operational vocabularies) exists, is seeded, and is maintainable by DBAs via direct SQL per…'
resource: 'epics/phase-0/epic-0.3-reference-data-read-only-api.html'
tags: [ram-pathfinder, epics, phase-0]
timestamp: '2026-06-17'
parent: 'epics/phase-0/index.md'
epic: 0.3
title: 'Reference data is served read-only via a versioned, jurisdiction-filtered API'
storyCount: 2
---

# Epic 0.3: Reference data is served read-only via a versioned, jurisdiction-filtered API

**User outcome:** Tier-(b) RAM-owned reference data (Regions, Offices, calendar / financial-year boundaries, operational vocabularies) exists, is seeded, and is maintainable by DBAs via direct SQL per operational runbook[^d10]. All reference data — both the upstream-sourced tier-(a) tables ingested in Epic 0.1 and the tier-(b) tables created here — is queryable read-only via `ram-reference-data`'s versioned REST API, **jurisdiction-filtered**[^d8]. **No admin UI is in scope for MVP**; tier-(a) data is never hand-edited in RAM in any phase (corrections at source per FR6).

**Vertical slice:**
- Tier-(b) RAM-owned tables (15: `ram_regions`, `ram_offices`, `ram_calendar_periods` + 12 operational vocabularies incl. `ram_joh_types`, `ram_joh_fee_entitlements`) with service-owned Liquibase changelogs (per AR18–AR20) — the `ram-reference-data` service itself was scaffolded in Story 0.1.1
- Tier-(b) seed data via a Liquibase seed changeset + the DBA maintenance runbook (D10 operating model)
- Per-service `SELECT` grants pattern completed for direct-SQL reads across both tiers (per FR7 / Principle 2)
- Reference Data **read-only** REST API: `GET` endpoints over both tiers, **jurisdiction-filtered responses**[^d8], for consumption by `ram-ui`, downstream services, and OpenAPI clients. **No `POST`/`PUT`/`DELETE` endpoints** — tier (a) is written only by the Epic 0.1 ingestion mechanisms; tier (b) by DBAs via SQL per runbook
- First end-to-end exercise of API-as-Product **read-side** standards: URL versioning (`/v1/reference-data/...`), OpenAPI 3.x spec published as Maven artefact, RFC 9457 problem-details errors, RFC 9745 `Deprecation` + RFC 8594 `Sunset` deprecation signalling (FR58)
- First Postman collection for Phase 0 published under `postman/ram-reference-data-phase0.postman_collection.json` (NFR42 first instance)

**FRs covered:** FR6 (tier-(b) maintenance per runbook; read API over both tiers), FR7 (direct-SQL read pattern + writes-follow-the-tier), FR58 (versioned read API contract), FR59 (structured logs)

**FRs partially covered / deferred:**
- **FR6 tier-(b) maintenance UI** — post-MVP `ram-admin-ui`[^d10]; MVP maintenance is DBA-via-SQL per runbook
- **FR4** — admin UI for role / jurisdiction / Region-Area assignment updates is post-MVP

**Key NFRs:** NFR14 (no forbidden data — vocabularies contain no case/bank data by construction), NFR40 (service independently deployable), NFR42 (Postman collection). **NFR17–NFR19 (accessibility) do not apply in Phase 0** because no UI surface for this domain is delivered; they re-engage when the maintenance UI ships post-MVP.

**Out of scope for Phase 0 (deferred post-MVP):**
- Admin-gated `POST/PUT/DELETE` endpoints on Reference Data API (tier (b) only — tier (a) never gets a RAM write surface)
- `ram-admin-ui` Reference Data maintenance module
- *(There is no legacy-data ETL and no git-based sign-off workflow — revised D3. Upstream data arrives via Epic 0.1's ingestion mechanisms.)*

---

## Story 0.3.1: Tier-(b) RAM-owned reference tables, seed data, and the DBA maintenance runbook

As a **platform engineer** (and the DBAs who operate reference data in MVP),
I want the 15 tier-(b) RAM-owned reference tables created, seeded, and covered by an operational maintenance runbook,
So that **RAM-owned reference data that does not exist upstream (Regions, Offices, calendar boundaries, operational vocabularies) is available to every service and maintainable[^d10] operating model** — never overwritten by the upstream sync.

**Acceptance Criteria:**

**Given** `ram-reference-data` is scaffolded and carries the tier-(a) tables per Story 0.1.3,
**When** the engineer adds the Liquibase changeset `db/changelog/003-init-tier-b-ram-owned-tables.sql`,
**Then** the 15 tier-(b) tables exist with schemas per `architecture/data-tables.md`: `ram_regions`, `ram_offices`, `ram_calendar_periods`, plus the 12 operational vocabularies (`ram_joh_types`, `ram_work_types`, `ram_court_types`, `ram_ticket_types`, `ram_session_types`, `ram_absence_types`, `ram_working_pattern_types`, `ram_booking_statuses`, `ram_sitting_outcomes`, `ram_joh_fee_entitlements`, `ram_payment_lifecycle_statuses`, `ram_reconciliation_statuses`),
**And** the `ram_reference_data` DB role owns the tables (per AR19),
**And** SELECT grants exist for every current and placeholder service DB role (per FR7, AR22),
**And** the ArchUnit/grants fitness function verifies ownership and that the upstream sync code paths **cannot write tier-(b) tables** (tier separation per FR6 — RAM-owned data is never overwritten by sync),
**And** the three upstream-overlap candidates (`ram_joh_types`, `ram_court_types`, `ram_ticket_types`) carry a schema comment referencing gaps.md G8.2 (each may retire in favour of its `jo_*` counterpart once the eLinks contract is confirmed).

**Given** the engineer adds the Liquibase seed changeset for tier-(b) data,
**When** Liquibase applies it,
**Then** `ram_regions`, `ram_offices`, `ram_calendar_periods`, and all 12 vocabularies are populated with the documented controlled-list values (cross-referenced to the architecture's data-tables inventory),
**And** the seed values include the SSCS wave-1-relevant entries (e.g. session and work types applicable to tribunal sittings) flagged for confirmation against the SSCS as-is pack[^d11],
**And** dev/CI environments get the same seed via the standard Liquibase changelog path (no separate seeding mechanism for tier (b)).

**Given** the DBA maintenance runbook is written at `ram-architecture/runbooks/reference-data-maintenance.md`,
**When** a tier-(b) change is needed in MVP (e.g. a new office, a vocabulary value),
**Then** the runbook documents: the change request trail (who asked, why), the SQL pattern per table, the verification query, and the rollback statement,
**And** the runbook states explicitly that tier-(a) (`jo_*`/`mrd_*`) tables are **never** hand-edited — corrections happen at source (Judicial Office / MRD team) and arrive via the next sync (FR6),
**And** the runbook is referenced from the service README.

**References:** FR6 (tier (b)), FR7, FR59; NFR14, NFR40; AR18–AR20, AR22, AR49; D10, D11; gaps.md G8.2.

**Explicitly NOT in scope (deferred post-MVP):**
- RSU-facing maintenance UI in `ram-admin-ui`[^d10]
- Write API endpoints for tier (b)

---

## Story 0.3.2: Reference Data read-only REST API with jurisdiction filtering, versioning, OpenAPI, RFC 9457 errors

As an **API consumer** (`ram-ui` now; downstream services in Phase 1+; external case-management systems from Phase 9[^d12]),
I want a versioned **read-only** Reference Data API over both ownership tiers with **jurisdiction-filtered responses**, full OpenAPI spec, RFC 9457 error envelopes, and APIM-injected deprecation headers,
So that **Phase 1+ services can query controlled lists and JOH reference data at runtime, scoped to the requester's jurisdiction**[^d8], and the API-as-Product read-side standards are validated on Reference Data before any domain service is built (per PRD Key Characteristic 4 / D1).

**Acceptance Criteria:**

**Given** `ram-reference-data` carries both tiers (tier (a) per Stories 0.1.3/0.1.4; tier (b) per Story 0.3.1),
**When** the engineer implements read endpoints,
**Then** `GET /v1/reference-data/regions`, `/offices`, `/calendar`, `/vocabularies/{list}` (tier b) and `GET /v1/reference-data/johs`, `/jurisdictions`, `/tickets` (tier a, composing `jo_*` data) return `200 OK` with structured JSON,
**And** read endpoints are protected by `JWTFilter` (any authenticated principal can read; per NFR13),
**And** **responses are filtered by the requester's jurisdiction** resolved from `AuthDetails` (D8/FR2) — e.g. an SSCS-scoped requester sees Tribunals/SSCS-relevant entries; the jurisdiction hierarchy from `jo_jurisdictions` drives parent/child inclusion,
**And** the API does not blend tier lineage — each resource documents which tier it serves (FR6),
**And** **no write endpoints** (`POST`, `PUT`, `PATCH`, `DELETE`) are implemented — controller layer rejects with `405 Method Not Allowed` and an RFC 9457 problem-details body explaining the tier-appropriate write path (tier (a): corrections at source; tier (b): DBA runbook in MVP),
**And** OpenAPI spec generated by springdoc lists all read endpoints with full request/response schemas.

**Given** the engineer implements pagination + filtering,
**When** a consumer queries `GET /v1/reference-data/offices?region=northern&page=2&size=50`,
**Then** the response includes paginated data with a standard envelope `{items, page, size, totalElements, totalPages}`,
**And** invalid query parameters return `400 Bad Request` with RFC 9457 problem-details (per AR37, NFR39).

**Given** the OpenAPI spec is generated and Spectral lint runs in CI,
**When** the spec is built,
**Then** the spec passes Spectral lint (per AR17),
**And** the spec is published to internal Maven as `uk.gov.hmcts.ram:api-ram-reference-data:1.0.0` (per AR8),
**And** Swagger UI is exposed for developer browsing (ops-restricted at APIM).

**Given** APIM is configured for `ram-reference-data` per AR27 + AR39,
**When** a response leaves APIM to the client,
**Then** rate-limit headers are present per APIM policy,
**And** `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) headers are injected on endpoints flagged in the OpenAPI spec as `deprecated: true` (none at Phase 0; mechanism verified by a test endpoint),
**And** `/actuator/*` paths are blocked at APIM (per AR33).

**Given** the engineer publishes the first Phase 0 Postman collection,
**When** the collection runs in CI,
**Then** `postman/ram-reference-data-phase0.postman_collection.json` exercises every read endpoint across both tiers,
**And** the collection covers happy path + jurisdiction filtering (two requesters in different jurisdictions see different result sets) + 400 (invalid query) + 401 (unauthenticated) + 405 (write attempt) (per NFR42),
**And** the collection is versioned alongside the service.

**References:** FR6 (read surface over both tiers), FR7, FR58, FR59; NFR12, NFR13, NFR14, NFR39, NFR42; AR8, AR17, AR27, AR33, AR34, AR37, AR38, AR39, AR41; D8, D12.

**Explicitly NOT in scope (deferred post-MVP):**
- Admin write endpoints (`POST/PUT/PATCH/DELETE`) for tier (b)
- Any write surface for tier (a) (never, in any phase)

[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
[^d11]: D11 (2026-06-10, amended 2026-06-18) — SSCS-first pilot: wave 1 replaces **ListAssist** (the SSCS judicial-scheduling tool); **GAPS (SSCS case management) is retained, not replaced**; waves 2+ replace JI/APEX per Courts region.
[^d12]: D12 (2026-06-10) — RAM is the system of record for JOH availability and scheduling only; case and hearing management live in external systems.
