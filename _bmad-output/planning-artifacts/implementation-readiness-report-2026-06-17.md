---
type: 'Readiness Report'
title: 'Implementation Readiness Assessment Report'
description: 'Date: 2026-06-17'
resource: 'implementation-readiness-report-2026-06-17.html'
tags: [ram-pathfinder, change-control, sscs]
timestamp: '2026-06-17'
assessmentDate: '2026-06-17'
project: 'ram-analysis (RAM Pathfinder)'
assessmentScope: 'SSCS-cohort, integrations-first Phase 0 (post SCP 2026-06-17 / architecture decision #12)'
stepsCompleted: ['step-01-document-discovery', 'step-02-prd-analysis', 'step-03-epic-coverage-validation', 'step-04-ux-alignment', 'step-05-epic-quality-review', 'step-06-final-assessment']
documentsUsed:
  prd: 'prd.md (5/5, re-validated 2026-06-17)'
  architecture: 'architecture.md (v3.4) + architecture/ shards (11) + architecture-summary.md'
  epics: 'epics/ (sharded) — index, framework, fr-coverage-map, requirements-inventory + phase-0/ (5 canonical epics)'
  ux: 'NOT PRESENT (accepted gap — documented in epics/index.md)'
status: COMPLETE
readinessVerdict: 'READY for Phase 0 sprint planning — 2 conditions to handle at planning; 0 critical'
---

# Implementation Readiness Assessment Report

**Date:** 2026-06-17
**Project:** ram-analysis (RAM Pathfinder)
**Scope:** SSCS-cohort readiness for the integrations-first Phase 0 (per D11 + SCP 2026-06-17 / architecture decision #12)

## Document Inventory

### PRD
- **`prd.md`** (whole, 111 KB) — re-validated 2026-06-17 → 5/5, consistent with D1–D12. **Use.**
- No sharded `prd/` folder. Validation reports (`prd-validation-report-2026-06-10.md`, `-2026-06-17.md`) are reports, not PRD source.

### Architecture
- **`architecture.md`** (whole index, v3.4) + **`architecture/`** (11 shards: assumptions, changelog, conventions, data-tables, FR/NFR coverage, gaps, repo-structure, repository-strategy, starter-template, user-types) + **`architecture-summary.md`**. Parent-index + shards is the intended structure (not a conflicting duplicate). **Use all.**

### Epics & Stories
- **`epics/`** (sharded — canonical): `index.md`, `framework.md`, `fr-coverage-map.md`, `requirements-inventory.md`, and `phase-0/` with **5 canonical epics**:
  - `epic-0.1-upstream-reference-data-ingested.md` (4 stories)
  - `epic-0.2-user-authenticates.md` (5)
  - `epic-0.3-reference-data-read-only-api.md` (2)
  - `epic-0.4-user-populations-bootstrapped.md` (1)
  - `epic-0.5-system-dispatches-emails.md` (2)
  - **= 14 stories.** **Use.**

### UX Design
- **NOT PRESENT** — accepted gap (downstream epics inherit UI requirements from PRD FR55/FR56 + GOV.UK / WCAG 2.2 AA per architecture). Documented in `epics/index.md`.

## Issues Found (resolved by selection)

1. **`epics.md` (33-line pointer) vs `epics/` (sharded canonical).** `epics.md` is a superseded stub pointing to the folder. → **Use `epics/`; ignore `epics.md`.**
2. **4 superseded redirect stubs in `phase-0/`** alongside the 5 canonical epics — `epic-0.1-user-authenticates.md`, `epic-0.2-reference-data-read-only.md`, `epic-0.3-user-populations-bootstrapped.md`, `epic-0.4-system-dispatches-emails.md` (left as pointers by the 2026-06-17 restructure, pending deletion). → **Use the 5 canonical epics; exclude the 4 stubs.**
3. **No UX document** — WARNING; accepted gap (see above).

No unresolved conflicts: each "duplicate" resolves cleanly to the canonical version.

## PRD Analysis

PRD read in full during the 2026-06-17 re-validation. Every FR/NFR enumerated below; full text in `prd.md`.

### Functional Requirements (60)

**Identity & Authorisation:** FR1 SSO + canonical-identity resolution (JOH→`jo_people` personnel number; staff→RAM UUID) · FR2 roles + jurisdiction + Region/Area authz · FR3 effective-permissions retrieval · FR4 admin updates role/jurisdiction/scope (MVP: DBA-via-SQL) · FR5 external M2M auth (post-MVP).
**Foundational Data:** FR6 two-tier Reference Data (tier-a upstream read-only; tier-b RAM-owned) · FR7 direct-SQL reads, writes-follow-the-tier · FR8 shared `ram_configuration_values` · FR9 transactional email + delivery log.
**JOH Records & Working Patterns:** FR10 search/filter JOHs · FR11 view JOH profile · FR12 working patterns · FR13 auto-populate itineraries to 31 Mar · FR14 salaried FT/PT from eLinks (display) · FR15 ticket info (upstream + overlay) · FR16 jurisdictional-split 100% validation · FR17 base-location switch (RAM-owned) · FR18 link off-circuit/cross-Region JOHs.
**Absence:** FR19 record absences · FR20 auto-confirm vs confirm + ack · FR21 sickness extend · FR22 NTBF / needs-cover.
**Vacancy & Cover:** FR23 auto-create vacancy from approved absence · FR24 standalone vacancies · FR25 edit daily breakdown · FR26 mark filled on booking · FR27 fee-paid match hint · FR28 cancel/close.
**Booking:** FR29 create fee-paid booking · FR30 markFilled in-transaction · FR31 status tracking · FR32 ack emails · FR33 fee-entitlement Y/N prompt · FR34 double-booking prevention.
**Sitting:** FR35 generate planned sittings · FR36 filter sittings · FR37 confirm sitting + outcome · FR38 AM/PM split · FR39 ad-hoc sittings · FR40 verify + RBAC re-open (no RFC).
**Payment & Reconciliation:** FR41 list payment-eligible · FR42 payment batch (auto) · FR43 JFEPS Excel dispatch · FR44 content-negotiated schedule API · FR45 double-submission prevention · FR46 reconcile · FR47 no bank details.
**Itineraries & Reporting:** FR48 Court Itinerary · FR49 Judge Itinerary (scoped) · FR50 Forward Look · FR51 drill-down cells · FR52 Excel/PDF export · FR53 standard report catalogue · FR54 aggregate-only MI Feed API.
**Platform Ops:** FR55 role-scoped Home · FR56 business UI replicates APEX (WCAG 2.2 AA) · FR57 per-(jurisdiction,region) phased activation · FR58 versioned API + RFC 9457 + OpenAPI + deprecation · FR59 structured logs + correlation IDs · FR60 manual UAT per domain service.

### Non-Functional Requirements (42)

**Performance:** NFR1 static ≤3s · NFR2 dashboard ≤5s · NFR3 list/filter ≤10s · NFR4 batch/annual ≤15s · NFR5 reports/Forward Look ≤30s · NFR6 single read ≤500ms p95 · NFR7 write ≤1s p95 · NFR8 federated read ≤30s p95 (Strategy A; C fallback) · NFR9 capacity ~50–100/region, ~200–500 national.
**Security:** NFR10 latest TLS · NFR11 data-at-rest encryption · NFR12 authn (SSO; JWT propagation; batch `client_credentials`) · NFR13 authz enforcement (incl. jurisdiction) · NFR14 forbidden data (no bank/case-level) · NFR15 GovS 7 · NFR16 secret management (Key Vault).
**Accessibility:** NFR17 WCAG 2.2 AA · NFR18 assistive tech · NFR19 PSBAR 2018.
**Integration:** NFR20 HMCTS IdP (Phase 0 hard dep) · NFR21 JFEPS/Liberata unchanged · NFR22 HMCTS email · NFR23 DA&I aggregate-only · NFR24 JOH eLinks + MRD (MVP integrations).
**Observability:** NFR25 structured logging · NFR26 log retention · NFR27 Azure-native ingestion · NFR28 health/readiness probes · NFR29 audit/metrics (post-MVP roadmap).
**Data Privacy & Sovereignty:** NFR30 UK GDPR/DPA 2018 · NFR31 Azure UK residency · NFR32 retention (no migration) · NFR33 FOI scope.
**Reliability & Availability:** NFR34 operational hours · NFR35 payment-cycle continuity · NFR36 per-wave rollback · NFR37 Strategy A degraded mode · NFR38 wave-scope rollout isolation.
**Maintainability:** NFR39 API-as-Product · NFR40 per-service deployment · NFR41 behavioural-parity UAT · NFR42 Postman collections.

### Additional Requirements & Constraints

- **Architecture-derived requirements AR1–AR53** (in `epics/requirements-inventory.md`) — scaffolding, API-as-Product, DB-role/grants, ingestion ARs (AR46–AR49), AR52 (dev/CI seeds), AR53 (Terraform first-consumer).
- **Decisions D1–D12** — incl. D11 (SSCS-first wave), D3 revised (no migration; eLinks+MRD ingestion), D9 restructured (two-population identity), D8 (jurisdiction first-class), D10 (admin UI post-MVP), D12 (scope = scheduling only).
- **UX:** no UX-DRs — accepted gap; UI requirements inherited from FR55/FR56 + GOV.UK/WCAG.

### PRD Completeness Assessment

PRD is BMAD Standard, re-validated 5/5 today (0 blocking issues), internally consistent with D1–D12 and aligned with architecture v3.4 + the restructured Phase 0 epics. Implementation specificity in some FRs is intentional (brownfield rebuild). No completeness gaps for the SSCS-cohort scope.

## Epic Coverage Validation

**Scope of this assessment:** Phase 0 (SSCS-cohort, integrations-first) — the only phase with concrete epics + stories. Phases 1–9+ are **framework-only by design** (per-phase storying; Phase 0 sets the pattern). Source of truth: `epics/fr-coverage-map.md` (updated 2026-06-17), cross-checked against the 5 canonical Phase 0 epic files.

### Phase 0 FR Coverage Matrix (concrete stories)

| FR | Capability | Epic / Story | Status |
|---|---|---|---|
| FR1 | SSO + canonical identity | Epic 0.2 (0.2.3 resolve, 0.2.5 sign-in) + Epic 0.1 (`jo_people` ingested) + Epic 0.4 (auth records) | ✓ |
| FR2 | roles + jurisdiction + scope authz | Epic 0.2 Story 0.2.3 | ✓ |
| FR3 | effective permissions | Epic 0.2 Story 0.2.3 | ✓ |
| FR4 | admin updates (MVP data layer) | Epic 0.4 (DBA-via-SQL; UI post-MVP) | ✓ (MVP criterion) |
| FR6 | two-tier Reference Data | Epic 0.1 (0.1.2 tables, 0.1.3 eLinks, 0.1.4 MRD) + Epic 0.3 (0.3.1 tier-b, 0.3.2 read API) | ✓ |
| FR7 | direct-SQL reads, writes-follow-tier | Epic 0.1 Story 0.1.2 + Epic 0.3 Story 0.3.1 | ✓ |
| FR8 | shared `ram_configuration_values` | Epic 0.1 Story 0.1.1 | ✓ |
| FR9 | transactional email + log | Epic 0.5 (0.5.1/0.5.2) | ✓ |
| FR55 | role-scoped Home | Epic 0.2 Story 0.2.5 | ✓ |
| FR56 | business UI (WCAG 2.2 AA) | Epic 0.2 (`ram-ui`; admin stack post-MVP) | ✓ (business) |
| FR57 | per-(jurisdiction,region) activation | Epic 0.4 (flag bootstrap) + Epic 0.2 Story 0.2.5 (banner) | ✓ |
| FR58 | versioned API + RFC 9457 + OpenAPI | Epic 0.2 Story 0.2.3 (authz API) + Epic 0.3 Story 0.3.2 (read API) | ✓ |
| FR59 | structured logs + correlation IDs | Epic 0.1 Story 0.1.1 (first) + every story | ✓ |
| NFR24 | JOH eLinks + MRD ingestion | Epic 0.1 Stories 0.1.3 / 0.1.4 | ✓ |

**Phase 0 surface: 13 FRs + NFR24 → 100% covered** across the 5 epics / 14 stories. No missing Phase-0 FR.

### Requirements deferred by design (not gaps)

| FR(s) | Disposition |
|---|---|
| FR5 | Post-MVP (external M2M auth) — intentional, no MVP coverage required |
| FR10–FR18 | Phase 1 (JOH) — framework-mapped, storying pending |
| FR19–FR22 | Phase 2 (Absence) — framework-mapped |
| FR23–FR28 | Phase 3 (Vacancy) — framework-mapped |
| FR29–FR34 | Phase 4 (Booking) — framework-mapped |
| FR35–FR40 | Phase 5 (Sitting) — framework-mapped |
| FR41–FR47 | Phase 6 (Payment) — framework-mapped |
| FR48–FR52 | Phase 7 (Itineraries) — framework-mapped |
| FR53–FR54 | Phase 8 (MI Feed) — framework-mapped |
| FR60 | Phase 9+ (wave rollout UAT) — framework-mapped |

Every FR10–FR54 + FR60 is mapped to a phase/area in `framework.md` + `fr-coverage-map.md` — **no orphan FRs** — but is intentionally not yet decomposed into stories (BMAD phased storying; the next `bmad-create-epics-and-stories` run targets Phase 1 after Phase 0 ships).

### FRs in epics but not in PRD

None — every Phase 0 story references valid FR numbers.

### Coverage Statistics

- **Phase 0 (assessment scope):** 13 FRs + NFR24 → **100% storied** (14 stories).
- **Full programme (FR1–FR60):** 100% accounted for (Phase 0 storied; FR5 post-MVP; FR10–54, FR60 framework-mapped, storying pending per phase).
- **Orphan FRs:** 0. **Missing Phase-0 coverage:** 0.

## UX Alignment Assessment

### UX Document Status

**Not Found** — no dedicated UX/UI design specification. UI **is** implied (FR55 role-scoped Home, FR56 business UI replicating APEX, D4 puts UX/visual-design/journeys in scope, WCAG 2.2 AA per NFR17–19). This is a **documented, accepted gap** (recorded in `epics/index.md` and the 2026-05-06 readiness report).

### Alignment (what substitutes for a UX spec)

- **PRD → UI:** FR55/FR56 + the six user journeys define the interaction surface; the parity reference is the **incumbent system** (GAPS for SSCS wave 1; APEX layouts via `docs/architecture/asis/functional-modules.md` for Courts), verified by manual UAT (FR60/NFR41).
- **Architecture → UI:** the architecture pack **supports** the UI — Frontend Architecture (`ram-ui`: React + TypeScript + Vite, GOV.UK Design System base, TanStack Query, OIDC auth wrapper, RFC 9457 error handling), repo-structure module layout, axe-core accessibility CI. No architectural gap for the UI need.
- **Epics → UI:** Phase 0's UI scope is a **foundation/shell** (Epic 0.2 Story 0.2.4 scaffolds `ram-ui` with GOV.UK + auth + axe-core CI; Story 0.2.5 renders the role-scoped Home + activation banner). No domain screens in Phase 0.

### Warnings

- **WARNING (accepted, low risk for Phase 0):** no forward UX design artefact. For Phase 0 this is low-risk — the UI is a foundation shell with accessibility CI, not domain screens.
- **Carry-forward (medium, Phases 1–8):** domain-phase UI fidelity (replicating APEX/GAPS layouts per D4) relies on **incumbent-parity UAT (FR60)** and the as-is functional-modules pack rather than a forward UX spec. Acceptable for a replication rebuild, but each domain phase should treat the incumbent layout + functional-modules.md as its UX reference and gate on parity UAT. Recommend confirming this is the intended operating model before Phase 1 storying.

## Epic Quality Review

Assessed the 5 canonical Phase 0 epics (14 stories) against the create-epics-and-stories standards.

### Best-Practices Checklist (Phase 0)

| Check | Result |
|---|---|
| Epics deliver user/consumer value | Pass (with note — see Minor #2) |
| Epic independence (no Epic N → N+1) | **1 forward dependency** (Major #1) |
| Story sizing (single dev-agent session) | Pass (1 large story — Minor #1) |
| No forward story dependencies | Pass within epics; 1 cross-epic (Major #1) |
| DB tables created when needed (not upfront) | Pass — 0.1.2 tier-a, 0.3.1 tier-b, 0.2.3 auth, 0.5.1 notification |
| Acceptance criteria (Given/When/Then, testable, error paths) | Pass — strong; failure + boundary ACs present |
| Traceability to FRs maintained | Pass — every story carries a References line |
| Starter template as first story | Pass — Epic 0.1 Story 0.1.1 scaffolds from the HMCTS Crime SpringBoot starter |
| Brownfield integration points | Pass — eLinks + MRD ingestion (Epic 0.1) |

### 🔴 Critical Violations

None.

### 🟠 Major Issues

1. **Forward dependency: Epic 0.2's end-to-end sign-in demo requires Epic 0.4's seeds.** Epic 0.2 Story 0.2.3 creates the 6 auth tables but explicitly defers population to "Epic 0.4's seed scripts"; Story 0.2.5's Playwright E2E ("one JOH + one admin-staff user sign in") therefore needs Epic 0.4 (Story 0.4.1) data — but Epic 0.4 is sequenced *after* Epic 0.2. This breaks strict Epic-N-independence.
   - **Pre-existing:** this auth-schema-vs-seed split existed in the prior structure (old Epic 0.1 ↔ old Epic 0.3) and was not introduced by the integrations-first restructure.
   - **Resolution (pick one at sprint planning):** (a) run the dev/CI seed scripts (Story 0.4.1) *before* Epic 0.2's E2E demo — i.e. treat 0.4.1 seeds as a prerequisite of 0.2.5; or (b) have Epic 0.2 carry a minimal inline auth-table test fixture for its own 0.2.3/0.2.5 dev+CI, while Epic 0.4 retains ownership of the comprehensive seed scripts + bootstrap-verification job + production runbook. Recommend (b) — keeps Epic 0.2 independently demoable and Epic 0.4 as the standing wave-gate artefact.

2. **External-dependency risk on the first epic: JOH eLinks API contract unconfirmed (gaps.md G8.1).** Epic 0.1 — the programme's first deliverable — ingests from the JOH eLinks API whose contract is not yet confirmed. Story 0.1.3 carries this as an explicit external-dependency gate AC.
   - **Mitigation already in the stories:** the sync code path is integration-tested against a WireMock/stub eLinks API in CI (AR52); dev/CI use seeded `jo_*` fixtures. So Epic 0.1 is **buildable and testable without the live contract** — but the contract must land and be validated before any production cutover, and unmapped upstream structure raises an architectural PR (per G8.1).
   - **Action:** track the eLinks contract confirmation as the #1 external dependency / risk in sprint planning; it gates Epic 0.1 production-readiness (not its development).

### 🟡 Minor Concerns

1. **Story 0.1.1 is large.** It combines the `ram-reference-data` scaffold + the entire shared Azure estate Terraform (AKS, PostgreSQL, ACR, APIM, App Insights) + the `ram_configuration_values` baseline + TLS/data-at-rest/log-retention + CI/deploy (~10 AC blocks). Consider splitting shared-estate provisioning into its own story (e.g. 0.1.1 scaffold, 0.1.1b estate) so each fits a single dev-agent session. (Pre-existing sizing inherited from old Story 0.1.1.)

2. **Epics 0.1 / 0.3 / 0.5 are enabling/foundational** (ingestion, read API, notification-contract) rather than end-user-feature epics. This is **acceptable and expected** for Phase 0 — the PRD frames Phase 0 as the platform smoke-test (Key Characteristic 4), and each epic ties to a demoable gate (data flows in; API serves both tiers; `POST /notifications/send` works via Postman). Noted, not a violation.

3. **`ram_configuration_values` baseline ownership.** Story 0.1.1 has the `ram-architecture` Flyway baseline run "ahead of `ram-reference-data`". Confirm at sprint planning that the baseline migration is a discrete, owned step (it's cross-service infrastructure, not part of `ram-reference-data`'s own migrations).

### Remediation Summary

- **Before Phase 0 sprint execution:** resolve Major #1 (auth seed vs demo ordering — recommend inline fixture in Epic 0.2 + full seed in Epic 0.4) and register Major #2 (eLinks contract) as the top external dependency.
- **Optional polish:** split Story 0.1.1 (Minor #1).
- All findings are sequencing/dependency refinements — **no structural rewrite of the epics is required.**

## Summary and Recommendations

### Overall Readiness Status

**READY for Phase 0 sprint planning** — with 2 conditions to handle *at* planning. **0 critical issues.**

The planning artifacts for the integrations-first Phase 0 (SSCS-cohort) are implementation-ready: PRD re-validated 5/5 and consistent with D1–D12; architecture v3.4 aligned and supporting the UI need; Phase 0 FR coverage 100% across 5 epics / 14 stories; strong Given/When/Then ACs with traceability. The two Major items are sprint-planning inputs, not artifact-blockers.

### Assessment scorecard

| Dimension | Result |
|---|---|
| PRD | 5/5, 0 blocking (re-validated today) |
| Epic FR coverage (Phase 0) | 100% (13 FR + NFR24; 0 orphans) |
| Later-phase coverage | Framework-mapped, storying pending (by design) |
| UX | Accepted gap; architecture supports UI |
| Epic quality | 0 Critical · 2 Major · 3 Minor |

### Conditions to resolve at sprint planning (not blockers to starting)

1. **Auth seed-vs-demo ordering (Major #1).** Decide: Epic 0.2 carries a minimal inline auth-table fixture for its own 0.2.3/0.2.5 dev+CI demo, while Epic 0.4 owns the full seed scripts + bootstrap-verification job + production runbook (recommended) — or run Story 0.4.1 seeds before Epic 0.2's E2E. Removes the only forward dependency.
2. **JOH eLinks contract (Major #2).** Register the unconfirmed eLinks API contract (gaps.md G8.1) as the #1 external dependency. Epic 0.1 is buildable against the WireMock stub now; the contract gates production cutover, not development. Track contract confirmation as an explicit sprint risk.

### Recommended Next Steps

1. **Proceed to `[SP]` `bmad-sprint-planning`** for Phase 0, leading with Epic 0.1 (ingestion). Bake the two conditions above into the sprint plan (sequencing decision + eLinks risk).
2. **Optional pre-sprint polish:** split Story 0.1.1 (scaffold vs shared-estate Terraform) — Minor #1; and confirm the `ram_configuration_values` baseline is a discrete owned step — Minor #3.
3. **Housekeeping:** delete the 4 superseded phase-0 stub files (pending from the restructure) for a clean epic folder.

### Final Note

This assessment found **6 items across 3 categories (0 critical, 2 major, 3 minor, 1 accepted UX gap)**. None block starting Phase 0 sprint planning; the two Major items are planning-time decisions. The artifacts may be taken into sprint planning as-is with those two conditions tracked.

**Assessor:** bmad-check-implementation-readiness · **Date:** 2026-06-17 · **Supersedes:** the four 2026-05-xx readiness reports (pre-SSCS-pivot, Courts-cohort + ETL world).
