---
type: 'Architecture Shard'
description: 'This is the inventory of RAM Pathfinder database tables, grouped by owning service. The table list, column shapes, FK relationships, and ownership boundaries are RAM Pathfinder''s design.'
resource: 'architecture/tobe/data-tables.html'
tags: [ram-pathfinder, architecture, sscs]
timestamp: '2026-06-11'
parent: ../architecture.md
title: Authoritative Table Ownership Mapping
last_updated: 2026-06-11
extracted_in: architecture.md v1.8 — Strategy B refactor
amended_in: architecture.md v3.0 — Sprint Change Proposal 2026-06-10 cascade (two-tier reference-data ownership; JOH eLinks + MRD ingestion; ram-judge → ram-joh rename; ETL retraction)
---

# Authoritative Table Ownership Mapping

> Sibling of [`../architecture.md`](../architecture.md). The parent's *Data Architecture* section holds the strategy (shared schema, per-service DB roles, table-name convention, Liquibase, the two-tier reference-data ownership model, upstream ingestion). This file holds the per-table inventory.

## RAM Pathfinder tables, not legacy tables

This is the inventory of RAM Pathfinder database tables, grouped by owning service. The table list, column shapes, FK relationships, and ownership boundaries are RAM Pathfinder's design.

ListAssist and APEX have their own (different) schemas; neither is in this inventory and neither is owned by any RAM Pathfinder service. **No legacy data is migrated from either system**[^d3] — the Phase 0 Data Migration ETL is retracted. Judicial-holder reference data is ingested from the upstream sources of truth:

- **JOH eLinks API** → the 15 `jo_*` tables (nightly in-process scheduled sync inside `ram-reference-data`).
- **MRD (Master Reference Data)** → the `mrd_*` tables (weekly Excel feed via blob drop + scheduled pick-up, until MRD's public APIs ship).

Both paths are **source-of-truth integration, not legacy-system migration**: the upstream data is current and authoritative; only the ingestion mechanism differs.

For naming convention rules (**`ram_` prefix on every RAM-owned table**; `jo_`/`mrd_` source-system prefixes on upstream-sourced tier-(a) tables; `mock_` on dev-only mock-auth tables), see [`./conventions.md` → "Naming Patterns"](./conventions.md).

## The two ownership tiers (FR6/FR7)

| Tier | Written by | Hand-editable in RAM? | Corrections |
|---|---|---|---|
| **(a) Upstream-sourced** (`jo_*`, `mrd_*`) | The ingestion mechanisms only (`ram_reference_data` role) | **Never** | At source — Judicial Office for `jo_*`; the MRD team for `mrd_*`. Picked up by the next sync. No data flows upstream from RAM. |
| **(b) RAM-owned** (everything else) | The owning service; DBAs via SQL per runbook in MVP[^d10] | Yes (per tier-(b) rules) | Within RAM |

Separate tables preserve lineage; `ram-reference-data`'s API exposes both tiers as appropriate but does not blend them.

## Reference Data service (`ram-reference-data`) — 33 tables

Single owner of every reference-data table in the shared schema (FR7). Reads by other services go directly via SQL JOIN with per-service SELECT grants. Writes follow the tier.

### Tier (a) — JOH eLinks upstream-sourced — 15 tables

The 15 `jo_*` entities named in the revised D3, refreshed nightly by the in-process scheduled sync. Upserts key on the upstream natural key; rows absent upstream are **marked inactive, never hard-deleted** (protects FKs from domain tables).

| Table | Purpose | Key consumers |
|---|---|---|
| `jo_people` | JOH person records; `personnel_number` is the **upstream natural key** and the link target for `ram_joh_identities`. RAM's canonical JOH identifier is the UUID in `ram_joh_identities`, resolved at sign-in from the IdP email[^d9] | Authorisation (identity lookup), JOH, Booking, Sitting, Itinerary, MI Feed |
| `jo_appointments` | JOH appointments | JOH profile views (FR11) |
| `jo_judiciary_role_assignments` | JOH judiciary-role assignments | JOH profile views |
| `jo_authorisations_with_dates` | JOH authorisations with effective dates | JOH profile views, Vacancy matching |
| `jo_appointment_titles` | Appointment-title vocabulary (CJ, DJ, Recorder, Tribunal Judge, …) | JOH search/filter (FR10) |
| `jo_base_locations` | JOH base locations | JOH (FR17 overlay base), Itinerary |
| `jo_contract_types` | Contract types — salaried full-time / part-time status lives here (FR14: conversions happen upstream, reflected at next sync) | JOH, Sitting generation |
| `jo_genders` | Gender vocabulary | JOH profile views |
| `jo_judiciary_roles` | Judiciary-role vocabulary | JOH, Authorisation |
| `jo_jurisdictions` | **Jurisdiction hierarchy** (Tribunals/SSCS, Courts/Civil, …) — the first-class rollout/authorisation/filtering dimension[^d8]. Parent-child shape preserved natively if upstream provides it, or established on ingest. | Authorisation (user jurisdiction scope), Reference Data API filtering, activation flags (FR57) |
| `jo_locations` | Location records | JOH, Booking, Itinerary |
| `jo_location_types` | Location-type vocabulary | Office/location views |
| `jo_tickets` | Upstream ticket assignments per JOH (FR15 layer (a)) | JOH ticket views, Vacancy matching |
| `jo_ticket_categories` | Ticket categories | JOH, Vacancy |
| `jo_ticket_category_types` | Ticket category types | JOH, Vacancy |

### Tier (a) — MRD upstream-sourced — 1 table

Weekly Excel feed via blob drop until MRD's public APIs ship; the reader swaps for an API client then, the table stays.

| Table | Purpose | Key consumers |
|---|---|---|
| `mrd_specialisms` | JOH Specialisations — supplementary attributes not present in JOH eLinks[^d3]. Further `mrd_*` tables are added as MRD entities enter scope. | JOH profile views (FR11), Vacancy matching |

### RAM-internal sync tracking — 1 table

| Table | Purpose |
|---|---|
| `ram_sync_status` | Ingestion run log — per-run source, started/finished, outcome, row counts, error detail. RAM-internal tracking entity with no upstream source[^d3]. Feeds the wave-gate "reference data current" check and ops triage. |

### RAM-owned JOH identity — 1 table

RAM's canonical JOH identifier, decoupled from upstream. Written by the eLinks sync **mint-only** (a new `personnel_number` gets a new UUID; existing mappings are never changed or deleted) and SELECT-granted to every domain service. This insulates RAM domain data from upstream `jo_people` churn.

| Table | Type | Purpose | Key consumers |
|---|---|---|---|
| `ram_joh_identities` | Domain | **RAM-assigned canonical JOH identifier.** `id uuid PK` + `personnel_number` (unique — the link to `jo_people`) + audit columns. Every RAM domain table references the JOH by `joh_id` → `ram_joh_identities.id`, **never** by `personnel_number`. Minted eagerly during the nightly eLinks sync. | Authorisation (identity resolution), JOH, Absence, Booking, Sitting, Itinerary, MI Feed |

### Tier (b) — RAM-owned — 15 tables

Maintained in RAM (DBAs via SQL per runbook in MVP[^d10]; admin UI post-MVP). Never overwritten by upstream sync.

| Table | Type | Purpose | Key consumers |
|---|---|---|---|
| `ram_regions` | Domain | HMCTS judicial regions (Region/Area scoping; rollout waves within a jurisdiction) | All services (scoping), Authorisation |
| `ram_offices` | Domain | Offices within regions | JOH, Booking, Sitting, Itinerary |
| `ram_calendar_periods` | Domain | Financial-year boundaries; term dates | JOH (working-pattern horizon to 31st March), Reports |
| `ram_joh_types` | Vocabulary | JOH-type controlled list. **Upstream-overlap candidate** — may be retired in favour of `jo_appointment_titles` / `jo_judiciary_roles` once the eLinks contract is confirmed (G8.2). | JOH, Vacancy, Booking |
| `ram_work_types` | Vocabulary | Work-type controlled list (Crime, Civil, Family, …) | Sitting, Booking, Vacancy, Itinerary |
| `ram_court_types` | Vocabulary | Court / location-type controlled list. **Upstream-overlap candidate** vs `jo_location_types` (G8.2). | Office records, Itinerary |
| `ram_ticket_types` | Vocabulary | Ticket-type controlled list. **Upstream-overlap candidate** vs `jo_tickets` / `jo_ticket_categories` (G8.2). | JOH tickets, Vacancy matching |
| `ram_session_types` | Vocabulary | Session-type controlled list (full / AM / PM / evening / reserved-matter) | Booking, Sitting |
| `ram_absence_types` | Vocabulary | Absence-type controlled list (leave, sickness, training, …) | Absence (FR19) |
| `ram_working_pattern_types` | Vocabulary | Working-pattern-type list (None / Daily / Weekly) | JOH (FR12) |
| `ram_booking_statuses` | Vocabulary | Booking status list (planned / provisional / confirmed / cancelled / rejected) | Booking (FR31) |
| `ram_sitting_outcomes` | Vocabulary | Sitting outcome list (confirmed / cancelled / rejected) | Sitting (FR37) |
| `ram_joh_fee_entitlements` | Vocabulary | Per-JOH fee-entitlement list (yes / no / ask-when-booking). Set on the JOH profile (FR11); consumed at booking time (FR33). | JOH (FR11), Booking (FR33) |
| `ram_payment_lifecycle_statuses` | Vocabulary | Payment-record lifecycle (pending / requested / paid / reconciled / queried). | Payment (FR41, FR46), Booking (`payment_lifecycle_status_id` column UPDATE-granted to `ram_payment`) |
| `ram_reconciliation_statuses` | Vocabulary | Reconciliation status list (matched / queried / unreconciled) | Payment (FR46) |

## Authorisation service (`ram-authorisation`) — 6 tables

Strictly RAM-internal[^d9] — populated by programme-management / operational mechanisms outside the PRD's scope; **no external authority provides this data and no legacy system seeds it**. Service prefix used because "users" / "roles" are domain-overloaded terms.

| Table | Type | Purpose |
|---|---|---|
| `ram_auth_users` | Domain | RAM Pathfinder principal records spanning **both user populations**[^d9]: JOH users link to `ram_joh_identities` via `joh_id` (the RAM JOH UUID; `ram_joh_identities` in turn carries `personnel_number` → `jo_people`); admin-staff users link to `ram_auth_staff_identities`; `principal_kind` distinguishes them (and service principals). Carries the user's jurisdiction (FK → `jo_jurisdictions`). |
| `ram_auth_staff_identities` | Domain | **RAM-internal staff identity table** for HMCTS administrative staff (RSU, Court users, Tribunal Caseworkers, Finance/Payment Authoriser, MI/Reporting) — not present in JOH eLinks data. Canonical identifier: **RAM-assigned UUID** (architecture decision, 2026-06-11); IdP email is the lookup key, mirroring the JOH email → personnel-number pattern. |
| `ram_auth_roles` | Domain | RAM Pathfinder authorisation roles (shared by both populations — the populations differ in identity source, not authorisation semantics) |
| `ram_auth_user_roles` | Domain | User-role junction (many-to-many) |
| `ram_auth_user_region_scopes` | Domain | Per-user Region/Area scope assignments |
| `ram_auth_user_activation_flags` | Domain | Per-user "active in RAM Pathfinder" flag carrying the **(jurisdiction, region) tuple** (FR57 — jurisdiction-first phased activation). Wave cutover: `UPDATE … SET activated = TRUE WHERE jurisdiction = '…' AND region = '…'` per the rollout runbook. |

## Shared infrastructure tables (no owning service) — 1 table

Schema-managed by `ram-architecture`'s Liquibase baseline changelog; SELECT-granted to every RAM Pathfinder service DB role; writes are admin-or-Liquibase-only (no API). *(Introduced in v2.2, 2026-05-07 — replaces the dedicated `ram-configuration` service.)*

| Table | Type | Purpose |
|---|---|---|
| `ram_configuration_values` | Shared infra | Typed cross-service policy values (D1 — runtime policy keys that need to be visible to multiple services). Per-service configuration that is scoped to a single service uses Spring profiles + `application.yml` + Azure Key Vault, **not** this table. |

## Notification service (`ram-notification`) — 1 table

| Table | Type | Purpose |
|---|---|---|
| `ram_notification_dispatches` | Domain | Outbound email dispatch log (recipient, content type, dispatched-at, status, retry count, FR9) |

## JOH service (`ram-joh`) — 5 tables

The upstream JOH person record is **`jo_people`** (tier (a), owned by `ram-reference-data`); RAM's canonical JOH *identifier* is the UUID in `ram_joh_identities`. There is no separate `johs` profile table. `ram-joh` owns the **RAM-owned operational state and overlays** layered over the upstream entities (FR6 tier (b)), all **keyed by `joh_id` → `ram_joh_identities`** (`personnel_number` is the upstream link held only on `ram_joh_identities`). Profile *views* (FR11, FR15) compose tier-(a) data with these overlays via `ram-reference-data`'s read API; the overlay tables are SELECT-granted to `ram_reference_data` for that composition (Principle 1 cross-service read).

| Table | Type | Purpose |
|---|---|---|
| `ram_working_patterns` | Domain | Per-JOH working-pattern definition (target sit %, active period, FR12) — RAM-owned operational state |
| `ram_working_pattern_days` | Domain | Per-day breakdown within a working pattern (per-day work-type, FR12) |
| `ram_joh_ticket` | Domain | RAM-overlay tickets and other authorisations layered on top of the upstream `jo_tickets` set (FR15 layer (b)); add/edit/remove by admin staff — DBAs via SQL in MVP |
| `ram_joh_location` | Domain | JOH base-location changes recorded in RAM (FR17) — not captured by JOH eLinks and **not propagated back**; RAM-owned operational state over the upstream `jo_base_locations` baseline |
| `ram_jurisdictional_splits` | Domain | Per-JOH jurisdictional split percentages (must total 100%, FR16) |

## Absence service (`ram-absence`) — 1 table

| Table | Type | Purpose |
|---|---|---|
| `ram_absences` | Domain | Absence records (start/end, type, NTBF flag, status, FR19–FR22); references the JOH by `joh_id` → `ram_joh_identities` |

## Vacancy service (`ram-vacancy`) — 2 tables

| Table | Type | Purpose |
|---|---|---|
| `ram_vacancies` | Domain | Cover-requirement records (FR23, FR24); `filled` and `filled_at` columns are UPDATE-granted to `ram_booking` per Principle 1 |
| `ram_vacancy_days` | Domain | Per-day breakdown for vacancies (FR25 — cancel individual days with reason) |

## Booking service (`ram-booking`) — 1 table

| Table | Type | Purpose |
|---|---|---|
| `ram_bookings` | Domain | Fee-paid booking records (FR29, FR31); references the JOH by `joh_id` → `ram_joh_identities`; `payment_lifecycle_status_id` column is UPDATE-granted to `ram_payment` per Principle 1. Has `version integer NOT NULL DEFAULT 0` (`@Version` for optimistic locking) and a `uq_ram_bookings_vacancy_joh_session_date_type` unique constraint enforcing natural-key dedup on retries. |

## Sitting service (`ram-sitting`) — 1 table

| Table | Type | Purpose |
|---|---|---|
| `ram_sittings` | Domain | Salaried-JOH sitting records (FR35, FR37, FR38, FR39, FR40 — including verification state); references the JOH by `joh_id` → `ram_joh_identities` |

## Payment service (`ram-payment`) — 3 tables

| Table | Type | Purpose |
|---|---|---|
| `ram_payments` | Domain | Payment request records (FR41, FR42). Has `version` (`@Version`) and a `uq_ram_payments_cycle_run_date` unique constraint enforcing natural-key dedup on retries (FR45 — no double payment submission). |
| `ram_payment_schedules` | Domain | JFEPS-shaped schedule snapshots (FR43, FR44). JFEPS format preserved for SSCS wave 1[^d11]. |
| `ram_payment_reconciliations` | Domain | Reconciliation records (FR46). |

## Itinerary service (`ram-itinerary`) — 0 tables

Read-model service. No persistent state at MVP per Principle 2 — every read is a SQL JOIN over the shared schema across `ram_joh_identities` (the JOH spine; joined to `jo_people` for upstream attributes and to `ram-joh` overlays), `ram_absences`, `ram_vacancies`, `ram_bookings`, `ram_sittings`. Strategy C cache is post-MVP if measurement justifies.

## MI Feed service (`ram-mi-feed`) — 0 tables

Read-model service. Same pattern as Itinerary; SQL JOIN over the shared schema for aggregate reporting. Aggregate-only by contract — no case-level data (D12: case/hearing data has no tables anywhere in RAM).

## Mock authentication service (`ram-mock-auth`) — 2 tables (dev/integration only)

Per `ram_mock_auth` DB role. **Never deployed to production**; production deployments reject mock-auth issuer URLs (per G5.3 in [`./gaps.md`](./gaps.md)).

| Table | Type | Purpose |
|---|---|---|
| `mock_oauth_clients` | Dev-only | OAuth client registrations (Spring Authorization Server backend). Holds **(a)** the SPA client for human `authorization_code` flow, and **(b)** service-principal client registrations for **batch / scheduled components** that need a service identity (initially: `ram-payment-batch`). User-initiated runtime calls between services use **JWT propagation** (no service principal needed); batch / scheduled components — which have no upstream user context — use OAuth `client_credentials` against this mock issuer. *(v2.5 narrowing reverted in v2.6 to support the payment batch. The eLinks sync and MRD pick-up need no service identity — they run in-process inside `ram-reference-data` writing its own tables.)* |
| `mock_user_roster` | Dev-only | Test user roster mirroring a representative subset of `ram_auth_users` **across both identity populations** (JOH + admin staff) for realistic Authorisation testing (G5.2) |

## Inventory totals

- **Reference Data:** 32 tables (15 `jo_*` + 1 `mrd_*` + 1 sync tracking + 15 RAM-owned)
- **Authorisation:** 6 tables
- **Notification:** 1 table
- **JOH:** 5 tables
- **Absence:** 1 table
- **Vacancy:** 2 tables
- **Booking:** 1 table
- **Sitting:** 1 table
- **Payment:** 3 tables
- **Itinerary, MI Feed:** 0 tables (read models)
- **Shared infrastructure:** 1 table (`ram_configuration_values`; no owning service)
- **Mock auth:** 2 tables (dev/integration only)

**Total: 55 tables** across the shared schema (52 service-owned production + 1 shared infrastructure + 2 dev-only).

**Retry safety convention:** every RAM Pathfinder domain table that supports create has a `uq_{table}_{columns}` unique constraint on its natural key, and every entity that supports update has a `version` column for JPA `@Version` optimistic locking. There are *no* per-service `*_idempotency_keys` tables — those were dropped in v2.1 in favour of these PostgreSQL-native primitives. Tier-(a) tables are exempt (single writer: the ingestion mechanism; upserts key on the upstream natural key). See [`./conventions.md` → "Retry safety and concurrency control"](./conventions.md) for the pattern.

**On upstream contract validation:** when the JOH eLinks API contract and the first MRD workbook land in Phase 0 (G8.1 in [`./gaps.md`](./gaps.md)), the validation focus is the **ingestion mapping** — does each `jo_*`/`mrd_*` table have a slot for every upstream field RAM needs, and does the upstream natural-key scheme hold? The tier-(b) and domain-table design is fixed by RAM Pathfinder. Upstream-overlap candidates (`ram_joh_types`, `ram_court_types`, `ram_ticket_types` — G8.2) are resolved at that point: retire the RAM-owned vocabulary where the upstream entity covers it. If a fundamental mismatch surfaces, it lands via PR against the architecture document set, exactly as any other architectural change would.

**Fitness function** (Step 4 *ArchUnit-style fitness functions* in [`../architecture.md`](../architecture.md)) operates against this inventory: every table created by Liquibase DDL must appear here with the matching owning service (or under "Shared infrastructure"); DB role grants must align — including the tier-(a) rule that only `ram_reference_data` holds INSERT/UPDATE on `jo_*`/`mrd_*` tables.

[^d3]: Revised D3 (2026-06-10) — no data migration from any legacy system; judicial-holder reference data is ingested from the JOH eLinks API and MRD.
[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d9]: Restructured D9 (2026-06-10; refined 2026-07-09 per SCP) — two user populations. JOHs resolve IdP email → `jo_people` → `personnel_number` → a **RAM-assigned JOH UUID** (`ram_joh_identities`); HMCTS admin staff via a RAM-internal identity table. Both key on a RAM-assigned UUID; `personnel_number` is the upstream link only. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
[^d11]: D11 (2026-06-10, amended 2026-06-18) — SSCS-first pilot: wave 1 replaces **ListAssist** (the SSCS judicial-scheduling tool); **GAPS (SSCS case management) is retained, not replaced**; waves 2+ replace JI/APEX per Courts region.
