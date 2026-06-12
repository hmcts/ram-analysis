---
name: project-bmad-ram-pathfinder-state
description: Where the RAM Pathfinder BMAD workflow stands and what the SCP 2026-06-10 cascade still requires
metadata: 
  node_type: memory
  type: project
  originSessionId: fbd0b611-5a14-4dd5-baa5-5b011a548714
---

The repo's `_bmad-output/planning-artifacts/` tracks the **RAM Pathfinder** programme (HMCTS judicial scheduling replacement). Sprint Change Proposal 2026-06-10 pivoted MVP wave 1 to the **SSCS jurisdiction** (replacing GAPS), retracted the Phase 0 ETL (reference data now ingested from JOH eLinks API + MRD weekly Excel), introduced two user populations (JOH via `jo_people` personnel number; admin staff via `auth_staff_identities` RAM UUID), made jurisdiction a first-class hierarchical dimension, renamed `ram-judge` → `ram-joh`, and renumbered FR58–FR61 → FR57–FR60 (60 FRs total).

**Done (2026-06-11):** architecture pack fully amended to v3.0 — `architecture.md`, `architecture-summary.md`, all `architecture/` shards, sequence diagrams (incl. rename to `joh-onboarding-and-sitting-generation.*`), system-context diagram regenerated. Four architecture decisions taken with Ramnish: full rename now; in-process `@Scheduled` eLinks sync inside `ram-reference-data`; MRD via Azure Blob drop + scheduled pick-up; RAM-assigned UUID for staff identity.

**Done (2026-06-11, epics):** epics pack restructured per SCP — Phase 0 now 12 stories. Ramnish directed the eLinks/MRD ingestion stories into **Epic 0.1** (Stories 0.1.3/0.1.4 — sign-in depends on `jo_people`); Epic 0.2 renamed `epic-0.2-reference-data-read-only.md` (2 stories: tier-(b) tables/runbook + jurisdiction-filtered read API); Epic 0.3 renamed `epic-0.3-user-populations-bootstrapped.md` (1 story: seeds + bootstrap-verification job + runbook). requirements-inventory (FR1–FR60, AR46–AR49 now ingestion ARs, new AR52), fr-coverage-map, framework.md (incl. fixing never-applied D10 admin-UI area) all rewritten. 2026-05-15 validation report marked superseded.

**Standing constraint (2026-06-11, architecture v3.2): table naming** — every RAM-owned table carries the `ram_` prefix (`ram_bookings`, `ram_auth_users`, `ram_regions`, `ram_configuration_values`); upstream tier-(a) keep source prefixes (`jo_`, `mrd_`); no `_overlays` suffix (Ramnish's rule — `ram_joh_ticket`, `ram_joh_location`); `ram_sync_status` (was `jo_sync_status`); `mock_*` dev-only tables exempt.

**Standing constraint (2026-06-11, architecture v3.1 / AR53):** HMCTS uses **Terraform** for all infra provisioning — and Ramnish's rule: *Terraform lives in the first repo that needs the resource; infra cannot live separate from the application that needs it* (shared estate → `ram-authorisation`; MRD storage → `ram-reference-data`; Static Web App → `ram-ui`). Apply this to any future infra story.

**Remaining cascade (BMAD path order):** [IR] `bmad-check-implementation-readiness` (SSCS-cohort assessment per D11 — revalidates the restructured Phase 0) → [SP] `bmad-sprint-planning` (implementation-artifacts/ still empty). Also outstanding: SSCS as-is analysis pack under `docs/architecture/asis/` (Mary/analyst), README.md SSCS-first reframe (Paige/tech-writer). Note: as-is sources live at `docs/architecture/asis/` (moved back inside docs 2026-06-11 — docs/ is the GitHub Pages root and must be self-contained; `resources/architecture/asis/` no longer exists).
