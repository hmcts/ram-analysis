---
type: 'Epic'
description: 'User outcome: RAM Pathfinder''s two user populations — JOH users (resolved via jo_people → personnel number) and HMCTS admin staff (resolved via ram_auth_staff_identities → RAM-assigned UUID) — have…'
resource: 'epics/phase-0/epic-0.4-user-populations-bootstrapped.html'
tags: [ram-pathfinder, epics, phase-0, sscs]
timestamp: '2026-06-17'
parent: 'epics/phase-0/index.md'
epic: 0.4
title: 'Both user populations are bootstrapped and verifiable against the IdP'
storyCount: 1
status: 'integrations-first-restructure-2026-06-17'
revisedAt: '2026-06-17'
revisionNote: 'Integrations-first restructure (SCP 2026-06-17 / architecture decision #12): renumbered Epic 0.3 → 0.4; story 0.3.1 → 0.4.1. Sign-in (which this epic''s seeded data serves) is now Epic 0.2 Story 0.2.5 (was Epic 0.1 / 0.1.7). No content change. File renamed from epic-0.3-user-populations-bootstrapped.md.'
revisionNotePrior: 'SCP 2026-06-10 cascade: the APEX Users/Roles SQL-ETL story (old 0.3.1) is retracted with the ETL (revised D3 + restructured D9 — no legacy user migration; auth data is strictly RAM-internal, bootstrapped outside the PRD''s scope). The epic now delivers what RAM itself owns: dev/CI seeds spanning both identity populations, the bootstrap-verification job, and the production bootstrap runbook. File renamed from epic-0.3-admin-manages-users-roles.md.'
---

# Epic 0.4: Both user populations are bootstrapped and verifiable against the IdP

**User outcome:** RAM Pathfinder's two user populations[^d9] — **JOH users** (resolved via `jo_people` → personnel number) and **HMCTS admin staff** (resolved via `ram_auth_staff_identities` → RAM-assigned UUID) — have authorisation records (roles, jurisdiction, Region/Area scope, all-FALSE activation flags) in place: seeded by scripts in dev/CI, bootstrapped by programme-management mechanisms in production (outside the PRD's scope), and **verifiable** by a bootstrap-verification job that confirms every user maps to a real IdP principal before any wave cutover. Epic 0.2's sign-in works against this data.

**No legacy user migration of any kind**[^d3]: no APEX user dump, no IdP reconciliation ETL, no unmatched-record CSV workflow — none of these exist or will exist. **No admin UI in MVP**[^d10] — operational user/role/scope maintenance happens via direct SQL by DBAs; an admin UI surface is on the post-MVP roadmap.

**Vertical slice:**
- Dev/CI seed scripts (one-off, per AR52) populating **both populations**: `jo_*` fixtures (where no live eLinks connection exists), `ram_auth_staff_identities` rows, `ram_auth_users` (with `principal_kind` + jurisdiction), `ram_auth_user_roles`, `ram_auth_user_region_scopes`, `ram_auth_user_activation_flags` (all FALSE, keyed by (jurisdiction, region) per FR57) — mirroring `ram-mock-auth`'s test-user roster (AR35)
- **Bootstrap-verification job**: confirms every `ram_auth_users` row (both populations) resolves to an IdP principal — by email against the IdP directory (mock in Phase 0–8; real HMCTS IdP at the pre-Phase-9 cutover per G1.3) — and produces a verification report; failures block the wave gate
- **Production bootstrap runbook** at `ram-architecture/runbooks/identity-bootstrap.md`: documents what programme management must supply (the staff identity list, role/jurisdiction/scope assignments), the SQL load pattern, the verification-job invocation, and the FR4 maintenance pattern (DBA-via-SQL[^d10])

**FRs covered (Phase 0 surface):**
- **FR1** — the data both identity-lookup paths resolve against
- **FR4** — MVP data-layer success criterion ("an authorised DBA can update role / jurisdiction / scope per the operational runbook")
- **FR57** — initial all-FALSE flag state at bootstrap; cutover flips per (jurisdiction, region) in Phase 9+

**FRs deferred to post-MVP:**
- **FR4 admin UI surface** (`ram-admin-ui` Users & Roles module — D10)

**Out of scope for Phase 0:**
- The production bootstrap mechanism itself (programme-management / operational, outside the PRD's scope[^d9] — RAM provides the runbook and the verification job, not the source data)
- `ram-authorisation` admin write endpoints, admin UI modules, activation toggle UI (post-MVP[^d10])
- *(There is no APEX Users/Roles ETL, IdP-reconciliation matching, or unmatched-record decisions CSV — revised D3 / restructured D9.)*

---

## Story 0.4.1: Identity seed scripts (both populations), bootstrap-verification job, and the production bootstrap runbook

As an **identity / HMCTS IT lead** (and the engineers who need working sign-in in every environment),
I want dev/CI seed scripts covering both identity populations, a re-runnable bootstrap-verification job proving every user maps to an IdP principal, and a production bootstrap runbook,
So that **Epic 0.2's two-population sign-in works end-to-end in every environment, and no wave cutover can proceed with unverifiable users** (restructured D9, AR52, G1.3).

**Acceptance Criteria:**

**Given** the engineer creates the dev/CI seed scripts (one-off scripts per AR52; not a runtime API, not Liquibase changesets),
**When** the scripts run against a fresh dev/CI database,
**Then** they populate: representative `jo_*` fixtures (incl. `jo_people` rows whose emails match `ram-mock-auth`'s JOH test users, with stable personnel numbers, and `jo_jurisdictions` covering Tribunals/SSCS + Courts examples) where no live eLinks connection exists,
**And** `ram_auth_staff_identities` rows (RAM-assigned UUIDs) whose emails match the mock-auth admin-staff test users,
**And** `ram_auth_users` rows for both populations with `principal_kind`, the link to `jo_people.personnel_number` or `ram_auth_staff_identities.id`, and a jurisdiction (FK → `jo_jurisdictions`),
**And** role assignments (`ram_auth_user_roles`) and Region/Area scopes (`ram_auth_user_region_scopes`) covering every documented role across both populations,
**And** `ram_auth_user_activation_flags` rows keyed by (jurisdiction, region), **all FALSE** except designated test users flagged TRUE so the Epic 0.2 demo can show both the activated and non-activated paths (FR57),
**And** the scripts are idempotent (safe re-run on an already-seeded database).

**Given** the bootstrap-verification job is implemented (a re-runnable script/k8s Job owned by `ram-architecture`),
**When** it runs against an environment,
**Then** for every `ram_auth_users` row it verifies the principal resolves at the configured IdP — by email against the IdP directory (`ram-mock-auth` roster in Phase 0–8; real HMCTS IdP principal export/query at the pre-Phase-9 cutover per gaps.md G1.3),
**And** it verifies referential integrity per population: every JOH `ram_auth_users` row links to an existing, active `jo_people` personnel number; every staff row links to an existing `ram_auth_staff_identities` UUID,
**And** it produces a verification report (total users per population, verified count, failures with per-row reason),
**And** a non-empty failure list exits non-zero — wiring the job into the wave-cutover gate (the Phase 9+ rollout runbook and the pre-Phase-9 cutover checklist both require a clean run; per architecture *Wave rollout flow* gate 3),
**And** the job never modifies data — it is verification-only.

**Given** the production bootstrap runbook is written at `ram-architecture/runbooks/identity-bootstrap.md`,
**When** programme management prepares a wave's users,
**Then** the runbook documents: the inputs programme management must supply (staff identity list with emails; role / jurisdiction / Region-Area assignments for both populations — JOH person data itself arrives via the eLinks sync, not via bootstrap),
**And** the SQL load pattern per table (DBA-operated,[^d10]), including the all-FALSE initial activation state (FR57),
**And** the verification-job invocation and the rule that a clean verification run is a precondition for the wave gate,
**And** the FR4 maintenance pattern: how a DBA updates a user's role / jurisdiction / scope per request, with the change-trail convention,
**And** the runbook states explicitly what is out of scope: no legacy-system user import exists or will exist[^d3]; the bootstrap data source is programme-management-owned.

**Given** the seeds have run in dev,
**When** the Epic 0.2 Playwright suite executes,
**Then** the JOH test user signs in and resolves to a personnel number, the admin-staff test user signs in and resolves to a staff UUID (Story 0.2.5),
**And** the bootstrap-verification job passes cleanly against the seeded environment in CI.

**References:** FR1, FR4 (MVP data-layer criterion), FR57 (initial flag state); NFR13, NFR15 (change trail per runbook), NFR16; AR18–AR20, AR34, AR35, AR52; restructured D9; gaps.md G1.3.

**Explicitly NOT in scope (deferred post-MVP or external):**
- Admin API / admin UI for user, role, jurisdiction, scope, or activation management[^d10]
- The production bootstrap mechanism's data sourcing (programme-management-owned, outside the PRD)
- *(No APEX user ETL, IdP-reconciliation matching, or unmatched-decisions CSV workflow exists — revised D3)*

[^d3]: Revised D3 (2026-06-10) — no data migration from any legacy system; judicial-holder reference data is ingested from the JOH eLinks API and MRD.
[^d9]: Restructured D9 (2026-06-10) — two user populations: JOHs resolve via jo_people to a personnel number; HMCTS admin staff via a RAM-internal identity table. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
