---
type: 'Sprint Change Proposal'
title: 'Sprint Change Proposal — Shared infrastructure to a dedicated repo (CNP alignment)'
description: 'Date: 2026-07-06 — Move the shared Azure estate out of ram-reference-data into a dedicated ram-shared-infrastructure repo per the HMCTS Cloud Native Platform standard, provisioned and independently verified in a new Epic 0.0.'
resource: 'sprint-change-proposal-2026-07-06.html'
tags: [ram-pathfinder, change-control, infrastructure, cnp]
timestamp: '2026-07-06'
project: 'ram-analysis (RAM Pathfinder)'
author: 'Ramnish'
changeScope: 'Moderate'
decision: 13
architectureVersion: 'v3.8'
---

# Sprint Change Proposal — Shared infrastructure to a dedicated repo (CNP alignment)

**Date:** 2026-07-06
**Project:** ram-analysis (RAM Pathfinder)
**Change scope:** Moderate (backlog reorganisation + architecture doc updates; no code to unwind)
**Mode:** Incremental
**Decision:** #13 · **Architecture version:** v3.8

---

## 1. Issue Summary

**Problem statement.** The HMCTS Cloud Native Platform onboarding guidance for new components ([`new-component/github-repo.html`](https://hmcts.github.io/cloud-native-platform/new-component/github-repo.html)) states that **product-level (shared) infrastructure must live in its own dedicated repository**, named `{product}-shared-infrastructure` — for RAM Pathfinder, `ram-shared-infrastructure`.

The current architecture does the opposite. Per **AR53 (the "colocated first-consumer" rule, adopted v3.1 and re-affirmed by decision #12 / SCP 2026-06-17)**, the shared Azure estate — **AKS, PostgreSQL Flexible Server, ACR, APIM, Application Insights** — is provisioned from Terraform **inside `ram-reference-data/terraform/`**, because that is the first service scaffolded under the integrations-first sequencing. (It was itself relocated there from `ram-authorisation`.)

**Discovery.** Identified during a review of the CNP new-component standards on 2026-07-06, while orienting Phase 0 for sprint planning.

**Why it matters now.** Phase 0 is at the sprint-planning boundary. Deferring the change means either building the estate the non-standard way and re-homing it later, or blocking sprint planning. Neither is necessary: **no implementation has started** (`implementation-artifacts/` is empty), so this is a re-plan of not-yet-started stories, not a rollback of built work. This is the cheapest possible moment to absorb it.

---

## 2. Impact Analysis

**Epic impact.**
- **New Epic 0.0** — "Platform estate is provisioned, verifiable, and CNP-compliant" (5 stories). Sequenced first in Phase 0.
- **Epic 0.1** — Story 0.1.1 shed its shared-estate provisioning responsibility; it now scaffolds `ram-reference-data` and **deploys onto** the Epic 0.0 estate. Still 4 stories.
- **Epics 0.2–0.5** — dependency wording repointed from "the estate provisioned in `ram-reference-data`" to "the estate provisioned in Epic 0.0". No story-count change.
- **Phase 0 totals:** 5 → **6 epics**, 14 → **19 stories**.

**Story impact.** No stories were completed, so none are re-opened. Story 0.1.1 is reduced in scope; five new stories (0.0.1–0.0.5) are added, each carrying a **deploy-time acceptance test** so infrastructure is verified as each Terraform layer lands (the sponsor's explicit requirement).

**Artifact conflicts (all resolved in §4).**
- `requirements-inventory.md` — **AR53 inverted**; incidental AR23/AR27 mentions repointed.
- `architecture/repository-strategy.md` — repo list **15 → 16** (new `ram-shared-infrastructure` row); `ram-reference-data` row trimmed; strategy/decision lines updated.
- `architecture/repo-structure.md` — per-service `terraform/` note reworded; **new `ram-shared-infrastructure` directory structure** added (incl. a `verification/` folder for the Epic 0.0 smoke checks).
- `architecture/framework.md` — Platform scope line repointed.
- `architecture.md` — **new decision #13** (supersedes the relocation part of #12).
- `architecture/changelog.md` — **new v3.8** entry.
- `epics/index.md`, `epics/phase-0/index.md` — epic table, story counts, sequencing narrative, per-epic summaries.

**Technical impact.**
- **Repos:** +1 (`ram-shared-infrastructure`, Terraform-only, no deployable workload). 16 total.
- **Code:** none written yet — zero rework.
- **Sequencing:** the *domain* deliverable ordering (0.1 → 0.5) is unchanged; a "platform estate stands up and is verified first" unit is inserted ahead of it (it was always an implicit prerequisite of old Story 0.1.1).
- **Cleaner separation:** `ram-reference-data` is reduced to its domain, consistent with the polyrepo "minimise shared coupling" principle.

**Secondary flag (not blocking).** The CNP page also states *"Repository should be public."* This conflicts with the standing "new repos private" default; HMCTS gov-guidance governs the org here. Flagged for a conscious decision at repo-creation time — recorded, not resolved by this SCP.

---

## 3. Recommended Approach

**Chosen path: Direct Adjustment** — add/modify stories and epics within the existing plan; no rollback, no MVP-scope reduction.

**Rationale.** The change is a repo-topology and doc-wording correction plus one new foundational epic. Because nothing is built, Direct Adjustment carries no rework cost. Structuring the estate as its own independently-verified epic (a) satisfies the CNP standard, (b) makes the platform testable in isolation before a service depends on it, and (c) tightens `ram-reference-data`'s responsibilities.

- **Effort estimate:** ~1 day of planning/doc edits (this SCP, applied). The engineering effort was always required — it is re-homed and made explicit as Epic 0.0, not net-new.
- **Risk:** Low. No built work touched; the change reduces coupling. Residual risk is the public-vs-private repo policy decision (§2 secondary flag) and the standing G9 Terraform-state/pipeline confirmation.
- **Timeline impact:** Neutral-to-positive — the estate work moves earlier and becomes independently testable, de-risking every downstream Phase 0 epic.

---

## 4. Detailed Change Proposals

All seven edit groups below were reviewed and **approved incrementally**, and have been **applied** to the planning artifacts.

**Stories / Epics**
1. **NEW `epics/phase-0/epic-0.0-platform-estate-provisioned.md`** — 5 stories, each a Terraform layer + deploy-time acceptance test:
   - 0.0.1 Repo + Terraform foundation (state backend, per-env stacks, plan/apply CI) — verify: `validate` passes, clean `plan`, no-op `apply` writes state.
   - 0.0.2 Network + AKS — verify: `kubectl get nodes` Ready across AZs; hello pod schedules.
   - 0.0.3 PostgreSQL + Key Vault — verify: TLS-only connect (plaintext refused, NFR10); scratch DB; Key Vault secret round-trip (NFR16).
   - 0.0.4 ACR + observability — verify: image push/pull; test trace + log land in App Insights (NFR25–28).
   - 0.0.5 APIM + smoke API — verify: gateway → echo 200 over TLS; sub-floor TLS refused (`testssl.sh`); unauth call rejected.
2. **`epic-0.1` Story 0.1.1** — retitled "(onto the Epic 0.0 estate)"; provisioning ACs removed; consume-the-estate ACs added; header/vertical-slice/references updated.

**Architecture**
3. **AR53 inverted** (`requirements-inventory.md`) — shared estate in dedicated `ram-shared-infrastructure`; per-service repos keep own resources only. AR23/AR27 and `framework.md` repointed.
4. **`repository-strategy.md`** — new `ram-shared-infrastructure` row; `ram-reference-data` row trimmed; total 15 → 16; decision/strategy lines updated.
5. **`repo-structure.md`** — per-service `terraform/` note reworded; new `ram-shared-infrastructure` tree (Terraform modules + `verification/` smoke checks) + rationale.
6. **`epics/phase-0/index.md` + `epics/index.md`** — sequencing blockquote, scope-model bullet, epics table (+0.0), summaries, stories-summary table, totals (6 epics / 19 stories); Epics 0.2 dependency repointed.
7. **Audit trail** — new **decision #13** in `architecture.md` (supersedes #12's relocation); new **changelog v3.8**.

---

## 5. Implementation Handoff

**Change scope classification: Moderate** — backlog reorganisation across epics + architecture doc updates; no code to reorganise (implementation not started).

**Routing:**
- **Product Owner / Dev** — Epic 0.0 enters sprint planning as the **first** Phase 0 unit; Story 0.1.1 re-estimated to its reduced (scaffold-and-deploy) scope.
- **Platform/Infra** — own `ram-shared-infrastructure`: create the repo (CNP naming, manual GitHub web-UI setup per the runbook; **decide public-vs-private per §2**), stand up the Terraform foundation, and confirm the G9 state-backend/pipeline pattern before the first `apply`.

**Success criteria.**
- `ram-shared-infrastructure` exists and provisions the dev estate via Terraform.
- Each Epic 0.0 story passes its deploy-time acceptance test (nodes Ready, Postgres TLS-only, Key Vault round-trip, ACR pull, APIM smoke 200).
- `ram-reference-data` (Story 0.1.1) deploys onto the verified estate with no colocated shared-estate Terraform.
- Architecture pack self-consistent at v3.8; Phase 0 shows 6 epics / 19 stories throughout.

**Deliverables produced:** this Sprint Change Proposal; the seven applied edit groups (§4); the new Epic 0.0 file.

---

> **Next step:** re-run `bmad-check-implementation-readiness` against the updated Phase 0 (it understands the sharded shape), then proceed to `bmad-sprint-planning` with Epic 0.0 sequenced first.
