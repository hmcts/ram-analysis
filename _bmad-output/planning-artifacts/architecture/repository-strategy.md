---
type: 'Architecture Shard'
description: 'Decision: 11 service repos + 1 mock-auth repo + 2 UI repos (business + admin) + 1 architecture/scaffolding repo. No monorepo, no Gradle root project.'
resource: 'architecture/tobe/repository-strategy.html'
tags: [ram-pathfinder, architecture]
timestamp: '2026-05-07'
parent: ../architecture.md
title: Repository Strategy & List
last_updated: 2026-05-07
---

# Repository Strategy & List

> Sibling of [`../architecture.md`](../architecture.md). The parent links here from its *Project Structure & Boundaries* section.

## Repository Strategy: Polyrepo

**Decision:** 11 service repos + 1 mock-auth repo + 2 UI repos (business + admin) + 1 architecture/scaffolding repo. No monorepo, no Gradle root project.

A monorepo would either share `build.gradle` config (breaks no-shared-coupling), coordinate releases (breaks per-region phased rollout independence), or add Bazel-style hermetic build complexity that RAM Pathfinder's requirements don't need.

Polyrepo gives each service its own repo, pipeline, release cadence, CODEOWNERS, branch protection, and review policy. What stays cross-repo: API contracts (OpenAPI specs), the architecture documents and ADRs, the scaffolding script.

## Repository List

| Repo | Phase | Purpose | Key Functions |
|---|---|---|---|
| **`ram-architecture`** | 0 | Architecture index + siblings, ADRs, scaffolding script. *(The `migration/` ETL is retracted — revised D3, 2026-06-10.)* | Maintain architecture docs and ADRs; generate new service repos via `ram-scaffold.sh`. |
| **`ram-mock-auth`** | 0 | OIDC issuer for dev / CI / integration (human users **and** batch service principals). **Never deployed to production.** | Issue JWTs via OIDC `authorization_code` for human users; **issue service tokens via OAuth `client_credentials`** for batch components (initially `ram-payment-batch`); refuse to start with `production` profile (G5.3). |
| **`ram-reference-data`** | 0 | Owns all 32 reference-data tables — tier (a) upstream-sourced (15 `jo_*` + `mrd_*`) and tier (b) RAM-owned (`ram_regions` / `ram_offices` / `ram_calendar_periods` + vocabularies), plus `ram_sync_status`. **First service scaffolded** (integrations-first sequencing, decision #12 / SCP 2026-06-17); **carries the shared Azure estate Terraform** (relocated from `ram-authorisation` per the AR53 first-consumer rule). | In-process JOH eLinks nightly sync + MRD weekly blob pick-up (tier a — the programme's first deliverable and first external integration); versioned read API (jurisdiction-filtered[^d8] — downstream of auth, lands after the auth epic); tier-(b) maintenance by DBAs via SQL in MVP[^d10]; reads happen via direct SQL by other services. |
| **`ram-authorisation`** | 0 | Owns the 6 Authorisation tables; **the per-request authz authority**. | Manage `ram_auth_users`, `ram_auth_staff_identities`, `ram_auth_roles`, `ram_auth_user_roles`, `ram_auth_user_region_scopes`, `ram_auth_user_activation_flags`; expose `POST /authz/check` with two-population identity resolution (IdP email → `jo_people` personnel number for JOHs; → `ram_auth_staff_identities` RAM UUID for admin staff,[^d9]); enforce per-(jurisdiction, region) phased activation (FR57). |
| **`ram-notification`** | 0 | Outbound transactional email dispatch. | Send booking ack (FR32) / absence ack / JFEPS-shaped payment-schedule emails (FR43); record dispatch log; retry on transient failure. |
| **`ram-joh`** | 1 | JOH operational state — working patterns + ticket/location overlays + jurisdictional split, keyed by `personnel_number`. *(Renamed from `ram-joh`[^d11]; the canonical JOH person record is `jo_people`, owned by Reference Data.)* | Manage working patterns (FR12); generate forward sittings (FR13); manage ticket overlays (FR15b) and location overlays (FR17); jurisdictional splits with 100% sum constraint (FR16); JOH search/profile views compose `jo_*` + overlays (FR10, FR11). |
| **`ram-absence`** | 2 | Absence records + approval workflow. | Create / approve / NTBF-flag / sickness-extend (FR19–FR22); on approval, call Vacancy to create cover-required vacancies (R4); send acknowledgements via Notification. |
| **`ram-vacancy`** | 3 | Cover-requirement records + per-day breakdown. | Create vacancies (FR23, FR24); manage `ram_vacancy_days` (FR25); accept `filled` / `filled_at` UPDATEs from Booking. |
| **`ram-booking`** | 4 | Fee-paid bookings + verification. | Create / verify / cancel fee-paid bookings (FR29, FR31); within the booking transaction, mark the target vacancy as filled (R5, Principle 1); retry-safe via native DB primitives (see [`../architecture.md`](../architecture.md) → *Data Architecture*). |
| **`ram-sitting`** | 5 | Salaried-judge sittings + verification. | Maintain sitting records (generated from working patterns); confirm and verify sittings (FR37); AM/PM session split (FR38); post-verification re-open via RBAC (FR40 — RSU Admin only at MVP, with mandatory justification + audit; no external RFC process); work-type override on confirmation. |
| **`ram-payment`** | 6 | Payment processing + reconciliation. JFEPS-shaped Excel output. **Two parts: a synchronous API (RSU reconciliation) and a scheduled batch component (`ram-payment-batch`).** | **Batch component** (scheduled; runs as service principal `ram-payment-batch` per v2.6): SQL JOIN read across confirmed bookings + sittings without an existing payment record; generate JFEPS Excel (FR41–FR44); persist payments and schedules; call Notification with bearer service token to dispatch the schedule (FR43). **Synchronous API**: RSU lists unreconciled payments and marks them reconciled (FR46). FR45 retry safety via native DB primitives (see [`../architecture.md`](../architecture.md) → *Data Architecture*). **Never stores bank details** (NFR14). |
| **`ram-itinerary`** | 7 | Operational read model. **No own tables** — SQL JOINs across judges, absences, vacancies, bookings, sittings. | Court itinerary view; Judge itinerary view (scoped to own profile per R2); Forward Look (≤ 30 s p95 — NFR8). |
| **`ram-mi-feed`** | 8 | Aggregate MI read model. **No own tables**. | Standard reports (utilisation, sittings, payments) with same parameter shape as APEX; aggregate-only — **no case-level data** (NFR23); Excel/PDF export; DA&I consumer interface (post-MVP). |
| **`ram-ui`** | 0–8 | **Business-user-facing SPA**, modules per domain. Excludes admin workflows. | Per-phase UI module replicating APEX functional surface for business roles (RSU operational work, Court users, Judges, Judges' Clerks, Finance/Payment Authoriser, MI); role-scoped Home with Outstanding-Actions tiles (FR55); SSO via HMCTS IdP / mock auth; GOV.UK Design System with WCAG 2.2 AA (NFR17). |
| **`ram-admin-ui`** | 0 | **Admin-facing SPA**, separated from business workflows. Same stack as `ram-ui` but distinct repo, pipeline, and deployment. | Reference Data maintenance (FR6 — Regions, Offices, judicial vocabularies, calendar / financial-year boundaries with named-owner sign-off); User & Role admin (FR4 — system administrators update role and Region/Area assignments for migrated and new users). **Post-MVP repo[^d10]** — in MVP these operations are DBA-via-SQL per runbook. Future admin surfaces reserved: per-(jurisdiction, region) activation flag dashboard (FR57), post-MVP user-action audit viewer (D7 roadmap). Same SSO + Authorisation pattern as `ram-ui`. |

**15 repos total** (11 production services + 2 UI + architecture + mock-auth). `ram-mock-auth` is dev/integration-only and never deploys to production.

**Why split admin and business UI:** business operational workflows (judges, absences, vacancies, bookings, sittings, payments, itineraries, reports) are continuously evolving with HMCTS judicial process. Admin work (managing the controlled vocabularies and user role assignments those workflows depend on) is lower-cadence, higher-stakes (a wrong Region rename or role flip cascades into operational chaos), and has a different audience (system administrators, not RSU/Court/Judges). Keeping them in separate repos gives independent CI/CD, independent rollout, distinct CODEOWNERS, and prevents accidental coupling — for example, admin-only screens cannot leak into a business user's nav by misconfiguration. Same as the backend's per-service polyrepo discipline: minimise shared code, accept duplication, gain independence.

[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d9]: Restructured D9 (2026-06-10) — two user populations: JOHs resolve via jo_people to a personnel number; HMCTS admin staff via a RAM-internal identity table. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
[^d11]: D11 (2026-06-10) — SSCS-first pilot: wave 1 replaces the combined ListAssist/GAPS usage for SSCS; waves 2+ replace JI/APEX per Courts region.
