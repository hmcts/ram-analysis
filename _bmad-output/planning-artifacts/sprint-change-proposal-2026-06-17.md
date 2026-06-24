---
type: 'Sprint Change Proposal'
description: 'Trigger. The first phase of delivery should focus on the inbound integrations — ingesting judicial-holder reference data from the JOH eLinks API and supplementary data from the MRD weekly dataset —…'
resource: 'sprint-change-proposal-2026-06-17.html'
tags: [ram-pathfinder, change-control]
timestamp: '2026-06-17'
title: 'Sprint Change Proposal — Integrations-first Phase 0 carve-out'
date: '2026-06-17'
author: 'Ramnish (with BMad Correct Course)'
trigger: 'Re-scope the programme''s first deliverable around the inbound JOH eLinks + MRD integrations and their associated APIs; resolve where the orchestration components live and whether a new ram-integrations repo is needed.'
mode: batch
scope: moderate
status: approved-2026-06-17
supersedes_assessment: false
related:
  - 'sprint-change-proposal-2026-06-10.md (the SCP this builds on — SSCS-first, two-tier reference data, in-process ingestion)'
  - 'architecture.md v3.0 (2026-06-11) + architecture-phase decisions #9/#10'
  - 'epics/phase-0/index.md (12 stories, pending SSCS-cohort revalidation)'
---

# Sprint Change Proposal — Integrations-first Phase 0 carve-out

## 1. Issue Summary

**Trigger.** The first phase of delivery should focus on the **inbound integrations** — ingesting judicial-holder reference data from the **JOH eLinks API** and supplementary data from the **MRD** weekly dataset — and **their associated read APIs**. Two questions were raised:

1. Which service should host the components that orchestrate the JOH and MRD data?
2. Do we need a new **`ram-integrations`** repository to host those components?

**Context.** The integration components are already designed and storied (architecture v3.0, 2026-06-11; Stories 0.1.3 eLinks, 0.1.4 MRD, 0.2.2 read API). What this change asks is **not new capability** — it is a **re-prioritisation and re-sequencing** of Phase 0 so the integration slice is the first thing built and demoed, decoupled from the authentication/UI vertical slice it is currently bundled into.

**Decisions taken at intake (2026-06-17):**

- **Integration scope** = JO eLinks + MRD inbound only (the two upstream feeds; no outbound, no additional systems).
- **Organisation** = carve out an integrations-first deliverable as the new first epic.
- **Mode** = batch.

## 2. The repository question — resolved

**Decision: No `ram-integrations` repo. The orchestration components stay in-process inside `ram-reference-data`.**

This reaffirms architecture v3.0 decisions #9 / #10 (AR46, AR47). Three facts make a separate repo actively harmful at the current scope:

1. **Single-writer ownership invariant.** Tier-(a) tables (`jo_*`, `mrd_*`) are owned exclusively by the `ram_reference_data` DB role. **AR49** plus a CI ArchUnit/grants fitness function forbid any other role from holding `INSERT`/`UPDATE`. A separate `ram-integrations` deployable would have to either (a) be granted write access — breaking the invariant and the fitness test — or (b) write through a Reference Data write API that **deliberately does not exist** (the service is read-only by design, Story 0.2.2). Both break current contracts.
2. **No new deployable, no new service principal.** The in-process decision was chosen specifically to avoid both, sidestepping the still-open service-auth gap **G7**. A new repo reopens both.
3. **No resilience gain.** Sign-in already reads RAM's own `jo_people`, so identity resolution is decoupled from eLinks uptime. A separate service writing the same tables buys nothing.

**Host:** `ram-reference-data`, via the already-specified in-process `@Scheduled` tasks:
`src/main/java/.../ingestion/JohElinksSyncTask.java` (nightly eLinks pull) and `ingestion/MrdExcelIngestionTask.java` (weekly MRD blob pick-up), with run state in `ram_sync_status`.

**When to revisit:** only if integration scope later grows beyond these two inbound feeds — outbound flows to external case/hearing systems (D12 external consumers), additional upstream sources, or transformation orchestration spanning multiple domain schemas. That would be a fresh architecture decision (service-auth, cross-schema writes), not a Phase 0 concern.

## 3. Key finding — ingestion decouples cleanly, the read API does not

Mapping the carve-out exposed a dependency split that drives the recommended structure:

| Component | Auth dependency | Can lead the programme? |
|---|---|---|
| eLinks sync (0.1.3), MRD ingestion (0.1.4) | **None** — in-process `@Scheduled`, reads/writes its own tables, no JWT, no caller identity | **Yes** — genuinely first |
| Reference Data **read API** (0.2.2) | **`JWTFilter`** (token validation against JWKS) **+ `authz/check`** for the requester's jurisdiction used in jurisdiction-filtered responses (D8) | **No** — needs `ram-mock-auth` + the authz mechanism to exist |

**Implication.** "Integrations and their APIs as the literal first thing" cannot be taken at face value: the *secured, jurisdiction-filtered* API is downstream of auth. The honest carve-out delivers **ingestion first** (the true integration win), then the **read API as soon as its auth dependencies are satisfied** — immediately after the auth slice.

## 4. Impact Analysis

### 4.1 PRD — no change

This is a build-order change, not a requirements change. MVP scope, the 60 FRs, and the 11-service decomposition are **unchanged**. No PRD edit required.

### 4.2 Epics — restructure (the substance of this proposal)

Phase 0 is re-organised from four epics into five, re-sequenced so ingestion leads. **No stories are added or removed** — they are moved and renumbered. Content is preserved; only sequencing, epic membership, and the relocations in §4.3 change.

| New epic | Title | Stories (source) | Auth dep |
|---|---|---|---|
| **0.1** | Upstream JOH/MRD reference data is ingested | 0.1.1 scaffold `ram-reference-data` **+ shared-estate Terraform** (from old 0.1.1/0.1.3); 0.1.2 tier-(a) `jo_*` tables + `ram_sync_status` (from old 0.1.3); 0.1.3 eLinks sync (old 0.1.3); 0.1.4 MRD ingestion (old 0.1.4) | none |
| **0.2** | User authenticates and lands on a role-scoped Home page | scaffold `ram-authorisation` (old 0.1.1, **minus** shared estate); `ram-mock-auth` (old 0.1.2); authz + `JWTFilter` (old 0.1.5); `ram-ui` scaffold (old 0.1.6); sign-in + Home (old 0.1.7) | provides auth |
| **0.3** | Reference data is served read-only via a versioned, jurisdiction-filtered API | tier-(b) tables + seed + runbook (old 0.2.1); read-only API (old 0.2.2) | **consumes** 0.2 |
| **0.4** | Both user populations are bootstrapped and verifiable against the IdP | old 0.3.1 | consumes 0.2 |
| **0.5** | Notification service is scaffolded and contractually ready | old 0.4.1, 0.4.2 | none |

**Story-count check:** 4 + 5 + 2 + 1 + 2 = **14 entries**, mapping 1:1 from the existing 12 stories plus the explicit split of the old 0.1.1 (scaffold) and old 0.1.3 (which both scaffolded `ram-reference-data` *and* set up tier-(a) + sync) into discrete scaffold / tables / sync stories. No scope added.

**Recommended build sequence:** `0.1 (ingestion)` → `0.2 (auth + UI)` → `0.3 (read API)` → `0.4 (bootstrap)` → `0.5 (notification)`.

### 4.3 Architecture — amend (rule-driven ripples)

1. **Shared Azure estate Terraform relocates `ram-authorisation` → `ram-reference-data`.** Per **AR53** ("Terraform lives in the first repo that needs the resource; the first-consumer carries the shared estate"), `ram-reference-data` becomes the first service scaffolded and therefore the first consumer of AKS, PostgreSQL Flexible Server, ACR, APIM, App Insights / Log Analytics. The shared-estate provisioning ACs currently in old Story 0.1.1 move to new Story 0.1.1; `ram-authorisation` becomes a **consumer** of the shared estate, retaining only its own resources.
2. **`ram_configuration_values` Flyway baseline** (owned by `ram-architecture`) must run before `ram-reference-data`; the SELECT-grant for `ram_reference_data` is added at the baseline. (Was sequenced before `ram-authorisation`.)
3. **Implementation Sequence** section reordered: `ram-reference-data` + ingestion first; `ram-authorisation` second.
4. **New architecture-phase decision recorded** (#12, 2026-06-17): integrations-first Phase 0 sequencing; in-process ingestion reaffirmed; **`ram-integrations` repo explicitly declined** with rationale (§2) so it is not re-litigated.
5. **Changelog entry** (e.g. v3.3) capturing this SCP.
6. **Repository strategy / repo list:** phase tags unchanged (both remain Phase 0); "first scaffolded service" note flips to `ram-reference-data`; shared-estate ownership note flips on the two repos.

Files touched: `architecture.md` (Implementation Sequence, architecture-phase decisions table, Integration Points), `architecture/repo-structure.md` (shared-estate ownership line), `architecture/repository-strategy.md` (first-service note), `architecture/changelog.md`, `architecture-summary.md` (sweep).

### 4.4 UX — no change

No UX artefact exists (accepted gap); unaffected.

### 4.5 Secondary artefacts

- `epics/index.md`, `epics/phase-0/index.md`, `epics/fr-coverage-map.md`, `epics/requirements-inventory.md` (AR53 wording on which repo carries the shared estate) — updated for the renumber + Terraform relocation.
- The four superseded readiness reports are unaffected (already superseded).
- Terraform stacks: shared-estate stack moves repos; no infra is provisioned yet (greenfield), so this is a documentation/ownership move, not a live-resource migration.

## 5. Recommended Approach

**Path: Direct Adjustment + backlog reorganisation (no rollback, no MVP scope change).**

- Re-sequence Phase 0 into the five-epic structure in §4.2; ingestion leads as the genuine first deliverable.
- Reaffirm in-process hosting; decline `ram-integrations` (§2).
- Apply the AR53 Terraform relocation and the baseline re-sequence (§4.3).
- Deliver the read API in Epic 0.3, immediately after auth, honouring the dependency in §3.

**Effort:** Medium (documentation/restructure; no code exists yet). **Risk:** Low — nothing is built; this is the cheapest possible moment to re-sequence. **Timeline:** neutral-to-positive — ingestion can start without waiting on the auth slice.

**Open decision for sign-off (one):** the read API's auth dependency (§3). Recommended: deliver it in Epic 0.3 after auth. *Alternative:* pull a minimal auth subset (`ram-mock-auth` + `JWTFilter` + a jurisdiction-only `authz/check`) forward into the first phase to ship the API earlier — at the cost of dragging ~half the auth slice forward and partially defeating the decoupling. **Recommendation: do not pull forward; keep the read API in 0.3.**

## 6. Implementation Handoff

**Scope classification: Moderate** (backlog reorganisation + architecture amendment; no fundamental replan).

| Recipient | Responsibility |
|---|---|
| **Architect (Winston)** | Apply §4.3 architecture amendments — AR53 Terraform relocation, Implementation Sequence reorder, decision #11 + changelog, repo-strategy/repo-structure notes. |
| **Epics update** (`bmad-create-epics-and-stories` re-run, Phase 0) | Apply the §4.2 restructure — move/renumber stories, split old 0.1.1/0.1.3 scaffold-vs-tables-vs-sync, update epic indexes + fr-coverage-map. |
| **Readiness gate (IR)** | Fold into the already-outstanding **SSCS-cohort `bmad-check-implementation-readiness`** run — it now also validates the integrations-first sequencing and the Terraform relocation. Phase 0 was already `pending-revalidation`; this change feeds that gate rather than adding a new one. |
| **Sprint Planning (SP)** | Runs after IR passes; `implementation-artifacts/` is still empty. Epic 0.1 (ingestion) becomes the first sprint. |

**Success criteria:**

- Phase 0 epics reflect the five-epic, ingestion-first structure; story count reconciles (12 → 14 entries, no scope added).
- Architecture pack reflects the Terraform relocation and records decision #12 (incl. the `ram-integrations` decline).
- IR (SSCS-cohort) passes against the restructured Phase 0; SP produces a sprint plan leading with Epic 0.1.

**Note:** `sprint-status.yaml` does not yet exist (SP not run), so checklist item 6.4 is N/A — the epic changes land in the epics pack and are picked up at first SP.
