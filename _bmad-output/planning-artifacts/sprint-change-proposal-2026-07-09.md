---
type: 'Sprint Change Proposal'
title: 'RAM-assigned JOH identity — personnel_number demoted to upstream link'
description: 'Introduce a RAM-owned stable JOH UUID (ram_joh_identities) as the canonical internal JOH identifier; personnel_number becomes only the link to the upstream JO/eLinks system, insulating RAM domain data from upstream data issues.'
resource: 'sprint-change-proposal-2026-07-09.html'
tags: [ram-pathfinder, sprint-change, identity, joh, ram_joh_identities]
timestamp: '2026-07-09'
parent: 'planning-artifacts/index.md'
change_scope: 'Major (documentation only — implementation not started)'
mode: 'Batch'
last_updated: 2026-07-09
---

# Sprint Change Proposal — 2026-07-09

## Section 1 — Issue Summary

**Trigger:** Rather than using `personnel_number` as the JOH identifier *within* RAM, use it only as the **link to the upstream JO/eLinks system**, and adopt a **RAM-specific UUID** as RAM's canonical JOH identifier — so that issues with upstream data (a `personnel_number` reissue, a `jo_people` full-refresh, an upstream key change) cannot negatively affect RAM services.

**Why it matters:** This reverses the core tenet of decision **D9** — *"`personnel_number` is the canonical JOH identifier referenced by every domain table."* `personnel_number` was threaded through every JOH-touching table, `ram_auth_users`, all JOH API routes, and both sequence diagrams.

**Discovery context:** Raised as a course-correction. Because implementation has **not started**, this is a **documentation/architecture change with no code impact** (like SCP 2026-07-06) — broad surface, low execution risk.

## Section 2 — Impact Analysis

- **Architecture:** `personnel_number` demoted from canonical identifier to upstream link; new RAM-owned identity table; FK convention reversed; API keying changed; auth resolution extended. Affected: `architecture.md`, `architecture-summary.md`, `conventions.md`, `data-tables.md`, `repository-strategy.md`, `functional-requirements-coverage.md`, `user-types.md`, `assumptions.md`, both JOH/auth sequence diagrams.
- **Epics/Stories:** Epic 0.1 (`ram-reference-data`) gains the `ram_joh_identities` table + eager minting during the eLinks sync; Epic 0.2 auth resolution and `/authz/check` response now carry the RAM JOH UUID; Epic 0.4 bootstrap seeds/verifies the mapping. Also `framework.md`, `fr-coverage-map.md`, `requirements-inventory.md` (AR22/AR34/AR46), `phase-0/index.md`. **No new stories; story count unchanged (19).**
- **PRD:** JOH endpoints rekeyed to `{johId}`; FR11/FR15 overlay tables rekeyed. Requirement intent unchanged.
- **Data model:** +1 table (`ram_joh_identities`); `ram-reference-data` 32 → 33 tables.
- **Technical impact:** none to code (not started). At build time: one new Liquibase table, a minting step in the eLinks sync, `joh_id uuid` FK columns on JOH-touching tables, `UUID` path variables.
- **Not changed (intentional):** dated reports (`sprint-change-proposal-2026-06-10`, `prd-validation-report-2026-06-17`, `implementation-readiness-report-2026-06-17`) left as historical; legitimate *upstream* `personnel_number` uses kept (`jo_people` natural key, MRD workbook validation, PII-in-logs prohibition, JSON casing/wrapping anti-pattern examples).
- **Downstream:** `docs/*.html` regenerated from the edited Markdown via `build_html.py`.

## Section 3 — Recommended Approach

**Direct Adjustment.** Decisions taken (user-approved):

| Decision | Choice |
|---|---|
| Mapping-table owner | **`ram-reference-data`** — mints the UUID in the same transaction as the `jo_people` upsert (single writer; link-to-upstream stays with the upstream owner) |
| Structure | **New RAM-owned table `ram_joh_identities`** (`id uuid PK` + unique `personnel_number` + audit). *Forced:* cannot be a column on `jo_people` (tier-(a) upstream, read-only, full-refresh) |
| API keying | **`/v1/johs/{johId}`** (UUID); `personnel_number` becomes a `?personnelNumber=` filter |
| Mint timing | **Eagerly at ingestion** — every `jo_people` row gets a mapping during the nightly eLinks sync |

Risk: negligible (no code, no requirement change). Effort: documentation sweep across ~20 living files.

## Section 4 — Detailed Change Proposals

**New table (`data-tables.md`):**
> `ram_joh_identities` — RAM-assigned canonical JOH identifier. `id uuid PK` + `personnel_number` (unique, link to `jo_people`). Written mint-only by the eLinks sync; SELECT-granted to every domain service. Its own subsection (parallel to `ram_sync_status`).

**Keystone convention flip (`conventions.md`):**
> OLD: *JOH references use `personnel_number` → `jo_people` (the canonical JOH identifier), not a surrogate id.*
> NEW: *JOH references use `joh_id` (uuid) → `ram_joh_identities` — the RAM-assigned canonical JOH identifier. `personnel_number` is the upstream link, stored only on `ram_joh_identities`, never a domain FK.*

**Representative edits applied:**
- Domain tables (`ram_absences`, `ram_bookings`, `ram_sittings`, `ram-joh` overlays): "references the JOH by `personnel_number`" → "by `joh_id` → `ram_joh_identities`".
- API: `/v1/johs/{personnelNumber}` → `/v1/johs/{johId}` (conventions, prd, project-context; Java `@PathVariable UUID johId`).
- Auth resolution (architecture, architecture-summary, requirements-inventory AR34, framework, sequence diagram, epic 0.2/0.4, phase-0 index): IdP email → `jo_people` → `personnel_number` → **`ram_joh_identities` (RAM JOH UUID)**; `/authz/check` `canonicalId` = RAM JOH UUID.
- eLinks sync (architecture, requirements-inventory AR46, epic 0.1, joh-onboarding sequence): now also **mints `ram_joh_identities` per `jo_people` row**.
- `ram_auth_users` links JOH principals via `joh_id` → `ram_joh_identities` (not `personnel_number`).
- `[^d9]` footnote refined across all living files; `ram-reference-data` count 32 → 33; `data-tables.md` gains the identity subsection.
- Changelog: new **v3.9** entry.

## Section 5 — Implementation Handoff

- **Scope: Major** (identity-model change) but **documentation-only** — no code exists to rework.
- **Status:** all living-doc edits applied and verified; only legitimate upstream/PII/anti-pattern `personnel_number` references remain.
- **Remaining step:** regenerate `docs/*.html` via `build-html.sh`, then commit externally (VSCode).
- **When implementation starts:** Story 0.1.2 creates `ram_joh_identities` (Liquibase); Story 0.1.3 mints it during the eLinks sync; every JOH-touching domain table carries `joh_id uuid` FK; JOH APIs key on `{johId}`.
- **Success criteria:** no living doc treats `personnel_number` as RAM's JOH identifier; `ram_joh_identities` is the single canonical JOH id; RAM domain data is insulated from upstream churn.
