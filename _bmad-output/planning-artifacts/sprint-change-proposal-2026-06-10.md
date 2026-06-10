---
date: '2026-06-10'
mode: 'incremental'
scope_classification: 'major'
triggers:
  - 'A: SSCS-first pilot wave — MVP wave 1 targets SSCS, not a Courts judicial region'
  - 'B: No legacy data migration — Reference Data sourced from JOH eLinks API + MRD Excel; user records bootstrapped outside the PRD'
  - 'C: Two distinct user populations — JOH users (via jo_people) + HMCTS admin staff (RAM-internal table)'
  - 'D: Jurisdiction as first-class hierarchical data dimension (Tribunals/SSCS, Courts/Civil, …)'
  - 'E: JOH (Judicial Office Holder) terminology replaces "judge" project-wide where panels include non-judge members'
  - 'F: RAM scope boundary — availability/scheduling only; case/hearing management lives in external systems'
artefactsModified:
  - 'prd.md (extensive — Executive Summary, Decisions Log D1–D12, Glossary, FRs 1/2/4/6/7/10–18/23/27/29/32/33/34/35/36/39/57/60, NFR24, Authentication Model, User Journeys, Phase-by-Phase Journey Mapping, Integration Requirements)'
artefactsRequiringFollowUp:
  - 'epics/index.md (Phase 0 + Phase 1–8 framework — no longer accurate; ETL-based Phase 0 epics are obsolete)'
  - 'epics/requirements-inventory.md (FR list copy — needs renumbering FR58–FR61 → FR57–FR60 plus FR1/FR2/FR4/FR6/FR7/FR10–FR18/FR23/FR27/FR29/FR32/FR33/FR34/FR35/FR36/FR39/FR57/FR60 amendments)'
  - 'epics/fr-coverage-map.md (FR→Epic mapping — same renumbering and amendments)'
  - 'epics/phase-0/index.md (Phase 0 epics 0.2 and 0.3 fundamentally restructured by retraction of the ETL)'
  - 'epics/phase-0/epic-0.2-admin-manages-ref-data.md (ETL stories obsolete)'
  - 'epics/phase-0/epic-0.3-admin-manages-users-roles.md (ETL stories obsolete)'
  - 'epics/phase-0/validation-report-2026-05-15.md (assessed Courts cohort + ETL bootstrap; SSCS-cohort readiness assessment required)'
  - 'architecture.md (service decomposition still applies; data tier needs the two-tier (a)/(b) reference-data ownership model; JOH eLinks + MRD integrations; D12 scope boundary)'
  - 'architecture-summary.md (cohort/service framing; ram-judge → ram-joh naming; JOH eLinks + MRD facade architecture; D12 boundary)'
  - 'architecture/data-tables.md (table inventory needs the two-tier model + RAM-overlay tables keyed by personnel_number)'
  - 'architecture/sequence-diagrams/payment-batch-flow.md (preserved unchanged per D11; verify SSCS applicability)'
  - 'README.md (programme summary needs SSCS-first reflection)'
  - 'resources/architecture/asis/ (new SSCS as-is analysis pack required parallel to the existing JI/APEX pack)'
---

# Sprint Change Proposal — 2026-06-10

## 1. Issue Summary

Six product-direction decisions, communicated by the Product Manager during the **Correct Course** workflow run on **2026-06-10**, require structural amendments to the PRD and cascade into multiple downstream artefacts:

### Trigger A — SSCS-first pilot wave

RAM Pathfinder's MVP pilot rollout (Phase 9, wave 1) targets the **SSCS** jurisdiction within the Tribunals jurisdiction, not a single HMCTS Courts judicial region as previously documented. RAM Pathfinder replaces **GAPS** (SSCS's incumbent scheduling system, expected to be decommissioned) for the SSCS cohort in wave 1; APEX/JI continues to serve Courts users in waves 2+. The 11-service architecture and Phase 0–8 build sequence are unchanged.

**Evidence:** direct stakeholder statement, 2026-06-10.

### Trigger B — No legacy data migration

RAM Pathfinder does **not** migrate data from any legacy system (APEX, GAPS). Judicial-holder reference data is sourced from upstream APIs — **JOH eLinks API** (canonical source for the 15 `jo_*` entities listed in the revised D3) and **MRD (Master Reference Data)** via a weekly Excel feed pending availability of MRD's public APIs. Historical data stays in the cohort's incumbent system and is accessed there as needed. The Phase 0 Data Migration ETL is retracted; the directory `ram-architecture/migration/` is no longer a deliverable.

**Evidence:** direct stakeholder statement, 2026-06-10.

### Trigger C — Two distinct user populations

RAM Pathfinder serves two distinct user populations, both authenticating via the HMCTS IdP tenant but identified through different lookup paths: (a) **Judicial Office Holders (JOHs)** — IdP email looked up against `jo_people` to resolve the personal number (canonical RAM identifier); (b) **HMCTS administrative staff** — RSU, Court users, Tribunal Caseworkers, Finance/Payment Authoriser, MI/Reporting users — *not present* in JOH eLinks data; RAM maintains a separate RAM-internal staff identity table. Both populations share the same authorisation model.

**Evidence:** direct stakeholder statement, 2026-06-10.

### Trigger D — Jurisdiction as first-class hierarchical data dimension

Jurisdiction (e.g. Tribunals/SSCS, Courts/Civil, Courts/Crime) is a first-class attribute in `ram-authorisation` (user scope) and `ram-reference-data` (API filtering). Modelled as a **hierarchy** where parent jurisdictions (Tribunals, Courts) contain child jurisdictions (SSCS, Civil, Crime, etc.). Sourced from JOH eLinks (`jo_jurisdictions`); the parent-child shape is preserved natively if upstream provides it, or established on ingest. No separate tagging step.

**Evidence:** direct stakeholder statement, 2026-06-10.

### Trigger E — JOH terminology replaces "judge"

Project-wide adoption of **JOH (Judicial Office Holder)** as the umbrella term where the meaning includes non-judge panel members (Medical Members, Disability-Qualified Members, Disability (Other) Members). "Judge" remains valid where the meaning is specifically a judge (Circuit Judge, Recorder, salaried Tribunal Judge, etc.). Service naming `ram-judge` → `ram-joh` (or architecture-phase equivalent) flagged as a follow-up.

**Evidence:** direct stakeholder statement, 2026-06-10.

### Trigger F — RAM scope boundary clarification

RAM Pathfinder is the **system of record** for JOH availability and scheduling — **not** for case management or hearing management. Allocation decisions are made by admin staff via the off-system advertising/matching process (FR27) and recorded in RAM via the UI by those admin staff. Case management, panel composition for specific cases, and hearing types live in external systems (SSCS case management; Courts Listing systems) that **consume** RAM's APIs; no external system writes into RAM.

**Evidence:** direct stakeholder statement, 2026-06-10.

## 2. Impact Analysis

### Decisions Log impact

| Decision | Impact |
|---|---|
| **D3** | Superseded by D11 — no data migration of any kind; reference data sourced from JOH eLinks + MRD. Multi-paragraph rewrite. |
| **D5** | Reframed per D11 — the cohort's incumbent system is the parity reference (GAPS for wave 1; APEX for waves 2+). |
| **D8** | Reframed per D11 — rollout boundary is jurisdiction first, then per-region within jurisdiction. Jurisdiction is a first-class hierarchical attribute. |
| **D9** | Superseded + restructured 2026-06-10 — no user migration; two distinct user populations (JOH + admin staff) with different identity-lookup paths. |
| **D10** | Amended — SQL-ETL bootstrap sub-clause superseded by D11. Admin-UI-removed-from-MVP thrust unchanged. |
| **D11** *(new)* | SSCS-first pilot wave. Cascades through D3, D5, D8, D9 (reframed as jurisdiction-aware); JOH terminology; SSCS-cohort readiness assessment required before Phase 9. |
| **D12** *(new)* | RAM scope boundary — availability/scheduling, not case/hearing management. Bounds the 11-service decomposition. |

### Functional Requirements impact

| FR | Impact |
|---|---|
| **FR1** | Amended — adds email→personal-number / staff-identifier resolution at authentication time. |
| **FR2** | Amended — adds jurisdiction to authorisation scope. |
| **FR4** | Reframed — role, jurisdiction, Region/Area scope updates for any user; ETL reference removed. |
| **FR6** | Substantially reshaped — RSU can **view** reference data; two ownership tiers (upstream-sourced read-only + RAM-owned) held in separate tables; corrections at source for tier (a). |
| **FR7** | Reshaped — cross-service direct-SQL reads unchanged; writes follow the tier; `ram-reference-data` is the single owner of all reference-data tables. |
| **FR10–FR18** | JOH terminology sweep across the JOH Records & Working Patterns section. Section heading renamed (Judge → JOH). FR14 reframed (contract-type is upstream-only). FR15 reshaped (tickets are upstream-sourced + RAM-overlay layered on top, keyed by personnel_number). FR17 marks location changes as RAM-owned operational state. |
| **FR23, FR27** | JOH terminology fixes in the Vacancy & Cover section. |
| **FR29, FR32, FR33, FR34** | JOH terminology fixes in the Booking Management section. "court / tribunal" used where venue/jurisdiction-specific. |
| **FR35, FR36, FR39** | JOH terminology fixes in the Sitting Management section. DJ(MC) / Legal Advisers / County Courts kept as Courts-cohort-specific examples. |
| **FR57** *(activation flags — was FR58)* | Reframed — per-jurisdiction, per-region phased activation. Cutover flips include both jurisdiction and region in the SQL `WHERE` clause. |
| **FR60** *(UAT — was FR61)* | Reframed — jurisdiction-incumbent-experienced users perform UAT (GAPS for wave 1; APEX for waves 2+). |
| **FR57 (Phase 0 Data Migration ETL)** | **Retracted entirely**. FR slot removed; FR58–FR61 renumbered to FR57–FR60. |
| **NFR24** | Flipped — JOH eLinks API + MRD are MVP integrations (was "out of MVP"). |

### User Journeys impact

The User Journeys section restructured to add a wave-1 SSCS journey and re-label existing journeys for waves 2+:

| Old | New |
|---|---|
| *(none)* | Journey 1 — Tribunal Caseworker SSCS panel coverage (wave 1) |
| Journey 1 — RSU cover-creation through payment | Journey 2 — RSU cover-creation through payment, Courts canonical cycle (wave 2+) |
| Journey 2 — Court daily sitting confirmation | Journey 3 — Court daily sitting confirmation (wave 2+) |
| Journey 3 — Judge views itinerary | Journey 4 — Judge views itinerary (wave 2+) |
| Journey 4 — DA&I MI Feed | Journey 5 — DA&I MI Feed (cohort-neutral; post-MVP) |
| Journey 5 — Cross-region edge case | Journey 6 — Cross-region edge case, Courts (Risk #1) |

Phase-by-Phase Journey Mapping table updated accordingly (now 6 rows).

### Glossary impact

New entries: **GAPS**, **JOH**, **Jurisdiction**, **MRD**, **RTJ**, **SSCS**, **Tribunal Member**, **Tribunal Panel**.

Amended entries: **JI** (now defined as the Courts cohort's legacy system specifically), **RAM Pathfinder** (replaces GAPS for SSCS wave 1 and JI/APEX for Courts waves 2+).

### Cascade into separate artefacts (NOT modified in this run)

| Artefact | Required follow-up |
|---|---|
| `epics/index.md` | Phase 0 + Phase 1–8 framework references retracted ETL; Phase 0 epics 0.2 and 0.3 obsolete in their current form |
| `epics/requirements-inventory.md` | Renumber FR58–FR61 → FR57–FR60; carry across the JOH terminology + tier-(a)/tier-(b) reshape |
| `epics/fr-coverage-map.md` | Renumber + reshape per FR amendments |
| `epics/phase-0/*.md` | Stories 0.2.x and 0.3.x assume the ETL exists; fundamentally restructure or remove |
| `architecture.md` + `architecture-summary.md` | Two-tier reference-data ownership; JOH eLinks + MRD facade architecture; D12 scope boundary; `ram-judge` → `ram-joh` rename; personnel_number-keyed RAM-overlay tables |
| `architecture/data-tables.md` | Table inventory needs the two-tier model + overlay-table pattern |
| `README.md` | Programme summary needs SSCS-first reflection; replace Courts-centric framing |
| `resources/architecture/asis/` | **New SSCS as-is analysis pack required** parallel to the existing JI/APEX pack — JOH eLinks data shape, MRD entities, SSCS operational processes, GAPS as-is capture |

### Implementation Readiness impact

Prior readiness reports (2026-05-05, -06, -15, -15-rev2) assessed the **Courts cohort + ETL bootstrap**. A new **SSCS-cohort readiness assessment** is required before Phase 9, covering:
- JOH eLinks API integration readiness
- MRD Excel feed ingestion readiness
- Two-population identity model implementation
- Jurisdiction-aware authorisation
- SSCS-experienced UAT panel coverage (GAPS users)

## 3. Recommended Approach

**Hybrid: Direct Adjustment as the primary path, with the cohort retarget being the MVP scope change.**

**Rationale:**

- **Option 1 — Direct Adjustment** is viable and the bulk of the work. The 11-service architecture and Phase 0–8 build sequence are preserved per the user's chosen scope. PRD wording, Decisions Log entries, FR text, journeys, and integration requirements are amendable in place.
- **Option 2 — Rollback** is not viable. Per the chosen scope ("11 services preserved, build sequence preserved"), nothing structural needs rolling back. Rolling back would discard the validated PRD and architecture work.
- **Option 3 — MVP Review** is partially in play — the MVP target jurisdiction shifts from a Courts judicial region (wave 1) to the SSCS jurisdiction. This is a *retarget*, not a reduction. Captured as part of the Direct Adjustment.

**Effort estimate:** High — extensive PRD amendments (executed inside this run); cascading follow-up workstreams (epics, architecture, README, SSCS as-is pack) are Medium-High each.

**Risk level:** Medium — the 11-service architecture genuinely fits SSCS workflows per the user's confirmation. The main risks are: (a) the SSCS as-is pack may surface additional concepts not captured here; (b) JOH eLinks API contract details may shift the data-tier design; (c) Phase 0 epics 0.2 and 0.3 need complete restructuring before implementation can resume.

**Timeline impact:** Programme-management territory. The PRD changes themselves do not change Phase 0–8 sequencing; the wave-1 cutover target shifts from a Courts region to SSCS.

## 4. Detailed Change Proposals

All PRD amendments listed in Section 2 (Impact Analysis) were **executed in this workflow run** via 21 numbered edit proposals, each presented to and approved by the Product Manager incrementally. The detailed diffs are in the PRD itself; the high-level summary is captured in `artefactsModified` (frontmatter) and Section 2 (this proposal).

Edit proposals applied (in order):
1. Add D11 to Decisions Log + update Document Map (D1–D11)
2. Executive Summary rewrite + D11 implication amendment (JOH terminology shift)
3. Glossary additions (GAPS, JOH, RTJ, SSCS, Tribunal Member, Tribunal Panel) + JI / RAM Pathfinder amendments
4. Supersede D3 (no data migration; JOH eLinks API + MRD facade) + add MRD glossary entry
5. Reframe D5 (jurisdiction-incumbent UAT)
6. Reframe D8 (jurisdiction-first rollout; jurisdiction as hierarchical first-class attribute)
7. Restructure D9 (two distinct user populations; email→personal-number lookup at sign-in)
8. D10 supersession note + D9 restructure for two-population identity
9. Retract FR57 (Phase 0 ETL) + renumber FR58–FR61 → FR57–FR60 + cross-reference updates
10. Amend FR4 (jurisdiction-aware admin operations)
11. Terminology sweep: "cohort" → "jurisdiction" globally + add Jurisdiction glossary entry
12. Amend FR6 (two-tier ownership model: upstream-sourced + RAM-owned, separate tables)
13. Amend FR7 (cross-service reads unchanged; writes follow the tier)
14. FR1 + FR2 + FR57 + NFR24 + FR60 cascade amendments
15. JOH Records & Working Patterns section (FR10–FR18) — JOH terminology + tier-(b) overlay patterns
16. FR23 + FR27 (Vacancy & Cover) JOH terminology
17. Booking + Sitting (FR29, FR32, FR33, FR34, FR35, FR36, FR39) JOH terminology + add D12 (RAM scope boundary) + Exec Summary char #6 + D11 implication amendments
18. Authentication Model subsection — JI → RAM Pathfinder, two-population model, jurisdiction added
19. New Journey 1 (SSCS Tribunal Caseworker) + renumber existing journeys 1–5 → 2–6
20. Phase-by-Phase Journey Mapping table update (6 rows)
21. Integration Requirements table restructure (JOH eLinks + MRD + external case-management systems + JFEPS preservation note)

## 5. Implementation Handoff

### Scope classification: **Major**

- Touches PRD core scope (D11 + D12), multiple decisions (D3, D5, D8, D9, D10 cascade), terminology layer, data ownership model, and downstream user journeys.
- Requires follow-up workstreams in architecture, epics, and supporting artefacts.

### Recipients and responsibilities

| Recipient | Responsibility |
|---|---|
| **Product Manager** (Ramnish) | Already executed the PRD-level decisions during this Correct Course run. Owns the directional clarity needed for the cascade workstreams. |
| **Solution Architect (Winston, `bmad-agent-architect`)** | Lead architecture document amendments: two-tier reference-data ownership; JOH eLinks API + MRD facade; D12 scope boundary; personnel_number-keyed overlay tables; `ram-judge` → `ram-joh` rename evaluation. |
| **Product Owner / Developer agents (`bmad-create-epics-and-stories`)** | Restructure Phase 0 epics 0.2 and 0.3 (ETL stories obsolete). Renumber FR references across `epics/fr-coverage-map.md` and `epics/requirements-inventory.md`. |
| **Tech Writer (Paige, `bmad-agent-tech-writer`)** | Update `README.md` programme summary (SSCS-first framing) and `architecture-summary.md`. |
| **Business Analyst (Mary, `bmad-agent-analyst`)** | Produce the new SSCS as-is analysis pack under `resources/architecture/asis/` (parallel to the JI/APEX pack). Document JOH eLinks data shape, MRD entities, SSCS operational processes, and GAPS as-is. |

### Success criteria

- PRD internally consistent (verified at the close of this workflow run).
- Architecture documents and epics aligned with PRD before any Phase 0 implementation work resumes.
- SSCS as-is pack complete before Phase 9 wave-1 cutover plan is finalised.
- New SSCS-cohort readiness assessment signed off before Phase 9 wave-1 cutover.

### Sequencing recommendation

1. **Immediately:** review this Sprint Change Proposal; confirm scope and recipients.
2. **Next:** architecture document updates (highest impact on Phase 0 epic restructuring) — `architecture.md`, `architecture-summary.md`, `architecture/data-tables.md`.
3. **Then in parallel:**
   - Phase 0 epic restructuring (0.2 + 0.3 — ETL stories obsolete);
   - FR-coverage-map and requirements-inventory cleanup;
   - SSCS as-is analysis pack production.
4. **Finally:** SSCS-cohort readiness assessment; `README.md` programme-summary update for external visibility.
