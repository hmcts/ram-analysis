---
type: 'Sprint Change Proposal'
title: 'Build-tool terminology clarification (Gradle vs Maven-format) + contract-placement read-only mirror'
description: 'Clarify that Gradle is the sole build/publish tool and "Maven" in the docs refers only to the artefact-repository format; make the ram-architecture read-only-mirror rule for API contracts explicit in the delivery operating model.'
resource: 'sprint-change-proposal-2026-07-07.html'
tags: [ram-pathfinder, sprint-change, build-tool, gradle, contracts]
timestamp: '2026-07-07'
parent: 'planning-artifacts/index.md'
change_scope: 'Minor'
mode: 'Batch'
last_updated: 2026-07-07
---

# Sprint Change Proposal — 2026-07-07

## Section 1 — Issue Summary

**Trigger:** Requirement to confirm **Gradle (not Maven) as the build tool**, and to make explicit that `ram-architecture` holds only a **read-only mirror** of API contracts.

**What the change analysis found:** Gradle is *already* the build tool across every artifact — 57 Gradle references, `build.gradle`/`gradlew`, "Gradle Groovy DSL (per HMCTS template)", and `changelog.md` v1.4 records "Build: Gradle Kotlin DSL → Groovy DSL". **There was no "Maven as build tool" statement anywhere.**

All 16 "Maven" occurrences referred to the **OpenAPI spec artefact being published to a Maven-*format* artefact repository** (coordinate system `groupId:artifactId:version`), which is **build-tool-agnostic** — Gradle publishes Maven-format artefacts via its `maven-publish` plugin (already named correctly in `starter-template.md`). A literal "Maven → Gradle" swap would have introduced errors ("Gradle artefact", "internal Gradle repo") and mis-renamed the real `maven-publish` Gradle plugin.

**Resolution chosen (user-approved):** *Clarify the wording* — name Gradle as the build/publish tool and reduce "Maven" to "Maven-format" (the repository/coordinate format) throughout the live docs. Leave the `changelog.md` historical record untouched.

## Section 2 — Impact Analysis

- **PRD impact:** 2 wording clarifications (`prd.md`). No requirement/scope change.
- **Epic/Story impact:** 4 clarifications across `epic-0.2`, `epic-0.3` (×2), `epic-0.5`, plus AR8 in `requirements-inventory.md`. **Acceptance-criteria intent preserved** (publish coordinates and behaviour unchanged; only the publisher/format is named explicitly).
- **Architecture impact:** 9 clarifications across `architecture.md` (×4), `architecture-summary.md`, `conventions.md`, `starter-template.md` (×2), `repo-structure.md`. No component, pattern, or technology decision changed — Gradle + Swagger Core + Maven-format artefact repo were already the design.
- **Delivery operating model:** new **"Contract placement within the bus: producer-owned source, read-only mirror only"** subsection added to `delivery-operating-model.md`.
- **Technical impact:** none to code/infra — this is a documentation-consistency change. The `maven-publish` Gradle plugin and artefact coordinates are unchanged.
- **Not changed (intentional):** `changelog.md:64` — changelogs record the decision as made at the time.
- **Downstream:** published `docs/*.html` must be regenerated from the edited Markdown via `build_html.py`.

## Section 3 — Recommended Approach

**Direct Adjustment** — in-place wording clarification. No rollback, no MVP-scope change. Effort: trivial (documentation). Risk: negligible (no behavioural or requirement change; ACs preserved). Timeline impact: none.

## Section 4 — Detailed Change Proposals

Canonical rewording pattern:

> **OLD:** published as a Maven artefact (`uk.gov.hmcts.ram:api-ram-{service}:{version}`)
> **NEW:** published by Gradle (via the `maven-publish` plugin) as a Maven-format artefact (`uk.gov.hmcts.ram:api-ram-{service}:{version}`) to the internal artefact repository

Applied edits (15 live references across 10 files):

| File | Ref | Change |
|---|---|---|
| `prd.md` | :400 | "published as a Maven artefact" → "published by Gradle via the `maven-publish` plugin as a Maven-format artefact" |
| `prd.md` | :514 | "(Maven artefact; …)" → "(Maven-format artefact published by Gradle `maven-publish`; …)" |
| `architecture.md` | :224 | "**API spec Maven artefacts**" → "**API spec artefacts (Maven-format, published by Gradle `maven-publish`)**" |
| `architecture.md` | :453 | full canonical rewording (publisher + format + internal artefact repository) |
| `architecture.md` | :649 | table row → "published by Gradle (`maven-publish`) as a Maven-format artefact" |
| `architecture.md` | :761 | "as Maven artefacts" → "as Maven-format artefacts (published by Gradle)" |
| `architecture-summary.md` | :131 | "published per-service as Maven artefacts" → "published per-service by Gradle (via the `maven-publish` plugin) as Maven-format artefacts" |
| `conventions.md` | :302 | full canonical rewording |
| `starter-template.md` | :70 | "`maven-publish` for artefact publication" → "`maven-publish` (the Gradle publishing plugin) for publishing Maven-format artefacts" |
| `starter-template.md` | :97 | "Maven-published spec artefact" → "spec artefact published by Gradle `maven-publish` in Maven format" |
| `repo-structure.md` | :56 | "Swagger Core + Maven-published spec artefact" → "Swagger Core; spec published by Gradle maven-publish as a Maven-format artefact" |
| `requirements-inventory.md` | :198 (AR8) | "published as a Maven artefact" → "published by Gradle (via the `maven-publish` plugin) as a Maven-format artefact" |
| `epic-0.3` | :22 | "published as Maven artefact" → "published (by Gradle `maven-publish`) as a Maven-format artefact" |
| `epic-0.3` | :101 | AC → "published by Gradle (`maven-publish`) to the internal Maven-format artefact repository as …" |
| `epic-0.2` | :203 | AC → "publishes the artefact (via Gradle `maven-publish`) to the internal Maven-format artefact repository" |
| `epic-0.5` | :25 | "published as Maven artefact" → "published (by Gradle `maven-publish`) as a Maven-format artefact" |

**Left untouched (historical):** `changelog.md:64` (v1.4 record).

**New content — `delivery-operating-model.md`:** added subsection **"Contract placement within the bus: producer-owned source, read-only mirror only"** establishing that (a) the delivering service repo is the contract source of truth (Gradle `maven-publish` → Maven-format artefact), (b) consumers pin the producer's versioned artefact, and (c) `ram-architecture/api-specs/` is a **read-only, automation-regenerated mirror** for discovery/Spectral/diagrams only — never hand-edited, never a build dependency, never a source of truth.

## Section 5 — Implementation Handoff

- **Scope classification: Minor** — documentation-consistency change, implemented directly.
- **Status:** all Markdown edits applied and verified (sweep confirms every live reference now reads "Maven-format" / "`maven-publish`"; changelog historical entry preserved).
- **Remaining step:** regenerate published `docs/*.html` from the edited Markdown via `build_html.py`, then commit (externally, via VSCode, per repo policy).
- **Success criteria:** no reader can mistake "Maven" for a build tool; Gradle is unambiguously the build/publish tool; the read-only-mirror rule for contracts is explicit in the operating model.
