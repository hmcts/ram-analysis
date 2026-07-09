---
type: 'Epic'
description: 'User outcome: Judicial-holder reference data flows into RAM Pathfinder from its upstream sources of truth — the JOH eLinks API (15 jo_ entities, nightly) and the MRD weekly dataset (supplementary…'
resource: 'epics/phase-0/epic-0.1-upstream-reference-data-ingested.html'
tags: [ram-pathfinder, epics, phase-0]
timestamp: '2026-06-17'
parent: 'epics/phase-0/index.md'
epic: 0.1
title: 'Upstream JOH/MRD reference data is ingested'
storyCount: 4
---

# Epic 0.1: Upstream JOH/MRD reference data is ingested

**User outcome:** Judicial-holder reference data flows into RAM Pathfinder from its upstream sources of truth — the **JOH eLinks API** (15 `jo_*` entities, nightly) and the **MRD** weekly dataset (supplementary `mrd_*` data) — so that `jo_people` exists and is current, `jo_jurisdictions` is available as the first-class jurisdiction dimension (D8), and judicial-holder reference data is authoritative in RAM **without any legacy migration** (revised D3, NFR24). This is the platform's foundational data layer: every downstream consumer of JOH identity and reference data depends on it, and JOH sign-in (Epic 0.2) is impossible until `jo_people` — the identity-lookup target — is populated.

**Hosting:** the ingestion runs in-process inside `ram-reference-data` — no separate `ram-integrations` repo. `ram-reference-data` is the first **domain** service scaffolded; it deploys onto the shared Azure estate provisioned in **Epic 0.0** (`ram-shared-infrastructure`) and carries only its **own** per-repo Terraform (Key Vault namespace; MRD storage — Story 0.1.4).

**Vertical slice:**
- **GitHub manual-setup runbook** at `ram-architecture/runbooks/github-setup.md` (the `gh` CLI is **not** available — all GitHub admin operations are manual via the web UI; `ram-scaffold.sh` handles only local scaffolding + `git push` to a pre-created remote)
- **First scaffolded backend service: `ram-reference-data`** (HMCTS Crime SpringBoot template + `ram-scaffold.sh` conventions per AR2–AR4)
- **Consumes the shared Azure estate** (AKS, shared global PostgreSQL Flexible Server + per-service DB roles, ACR, APIM, App Insights, Key Vault) **provisioned in Epic 0.0** per AR53 (revised — dedicated `ram-shared-infrastructure`)
- Shared `ram_configuration_values` Liquibase baseline changelog established by `ram-architecture` ahead of `ram-reference-data` (FR8); SELECT-granted to every service role
- Tier-(a) upstream-sourced tables: 15 `jo_*` + `mrd_specialisms` + `ram_sync_status` (RAM-internal ingestion run log), service-owned Liquibase changelogs (AR18–AR20), tier-(a) write-protection (only `ram_reference_data` holds INSERT/UPDATE — AR49, FR6)
- **JOH eLinks nightly in-process `@Scheduled` sync** (AR46, AR48)
- **MRD weekly Excel blob ingestion** via Azure Blob drop + scheduled pick-up (AR47)

**FRs covered:** FR1 (the identity-lookup *target* data — `jo_people` populated), FR6 tier-(a), FR7 tier-(a) grants, FR8 (shared `ram_configuration_values` baseline first lands here); NFR24 (JOH eLinks + MRD MVP integrations).

**Key NFRs first exercised here:** NFR10 (TLS at APIM), NFR11 (data-at-rest), NFR16 (Key Vault — incl. the eLinks API credential), NFR24 (JOH eLinks + MRD integrations), NFR25–NFR28 (structured logs + Application Insights ingestion + liveness/readiness probes), NFR31 (Azure UK South data residency), NFR40 (per-service deployable on Kubernetes), NFR42 (Postman collections), NFR59 (structured logs first exercised at scaffold).

**Out of scope (explicitly):** the read-only Reference Data API + jurisdiction filtering (Epic 0.3, Story 0.3.2 — downstream of auth). Tier-(b) RAM-owned reference tables (Epic 0.3, Story 0.3.1). All authentication / authorisation / UI (Epic 0.2). MRD API integration (post-MVP — when MRD ships public APIs). Hand-editing of tier-(a) data in RAM (never, in any phase — corrections at source per FR6).

---

## Story 0.1.1: Scaffold `ram-reference-data` from the HMCTS starter (onto the Epic 0.0 estate)

As a **platform engineer**,
I want to scaffold the **first** RAM Pathfinder backend service — `ram-reference-data` — from the HMCTS Crime SpringBoot template using `ram-scaffold.sh`, and to deploy it onto the shared Azure estate provisioned in Epic 0.0,
So that **subsequent services follow a consistent, version-pinned, supply-chain-secured baseline**, and the team can demonstrate the deployment pipeline end-to-end against the already-verified platform estate before any domain logic is written.

**Acceptance Criteria:**

**Given** the engineer has performed the GitHub manual-setup checklist (`ram-architecture/runbooks/github-setup.md`) **before** running the scaffold:
  - Created an empty private GitHub repo `ram-reference-data` under the HMCTS org **via the GitHub web UI**
  - Enabled branch protection on `main` via Settings → Branches (require PR review, require status checks, require linear history)
  - Note: the `gh` CLI is **NOT** available in the engineering environment — all GitHub admin config (repo creation, branch protection, team access) happens manually via the web UI per the runbook,
**And** the engineer has a clean local development environment with Java 25, Gradle Wrapper, and Docker,
**When** the engineer runs `ram-scaffold.sh ram-reference-data` from `ram-architecture/scaffolding/`,
**Then** the script scaffolds a Spring Boot 4.0.x project **locally** from `https://github.com/hmcts/service-hmcts-crime-springboot-template`, then commits and pushes to the pre-created remote on a feature branch via plain `git` (no `gh` CLI invocation),
**And** the project contents include a Spring Boot 4.0.x scaffold from `https://github.com/hmcts/service-hmcts-crime-springboot-template`,
**And** Gradle build uses Groovy DSL with Spring Boot Gradle plugin 4.1.0 and `io.spring.dependency-management:1.1.7` (per AR5),
**And** Group ID is `uk.gov.hmcts.ram`, artefact is `ram-reference-data`, base package is `uk.gov.hmcts.ram.referencedata`, default port is 8082 (per AR3),
**And** initial commit message is exactly *"Scaffold RAM Pathfinder reference-data from HMCTS starter"* (per AR4),
**And** Lombok 1.18.46 + MapStruct 1.6.3 are configured (per AR6),
**And** JJWT 0.13.0 + OWASP Encoder 1.4.0 are on the classpath (per AR7),
**And** springdoc-openapi is configured for OpenAPI 3.x generation (per AR8),
**And** JaCoCo, CycloneDX SBOM, gradle-git-properties, gradle-versions, and gradle-docker-compose plugins are configured (per AR9–AR13),
**And** Spring Boot Test with JUnit 5 (`junit-bom:6.0.3`), Testcontainers PostgreSQL 1.21.4, Spring Boot Testcontainers 4.1.0, and spring-boot-starter-webmvc-test are configured (per AR14–AR15),
**And** Spectral, ArchUnit, Spotless, and Checkstyle are configured (per AR17),
**And** a Helm chart skeleton exists at `charts/ram-reference-data/` with `values-dev.yaml`, `values-staging.yaml`, `values-production.yaml` overlays (per AR24),
**And** a `terraform/` directory exists with per-environment stacks (`dev` / `staging` / `production`) holding **only this service's own resources** (Key Vault namespace; the MRD storage added in Story 0.1.4) — the shared estate lives in `ram-shared-infrastructure` (Epic 0.0), per AR53 (revised),
**And** GitHub Actions workflows exist at `.github/workflows/ci.yml`, `deploy-dev.yml`, `deploy-staging.yml`, `deploy-production.yml` (per AR28),
**And** `CODEOWNERS` and `PULL_REQUEST_TEMPLATE.md` exist (per AR29),
**And** a Postman collection skeleton exists at `postman/ram-reference-data-phase0.postman_collection.json` (per AR41).

**Given** the scaffolded service runs locally via `./gradlew bootRun` after a `docker-compose up postgres`,
**When** the engineer queries `http://localhost:8082/actuator/health`,
**Then** the response is `200 OK` with body `{"status":"UP"}`,
**And** `/actuator/info` returns Git metadata embedded by gradle-git-properties (per NFR28, AR11),
**And** `/actuator/readiness` returns `200 OK`,
**And** structured JSON logs via Logstash Logback Encoder 9.0 appear on stdout (per AR30, NFR25),
**And** logs include a `correlationId` populated by `CorrelationIdFilter` for each request (per AR32) — FR59 structured logging is first exercised here.

**Given** the shared Azure estate has been provisioned and independently verified in **Epic 0.0** (`ram-shared-infrastructure`) — AKS, PostgreSQL Flexible Server, ACR, APIM + base policies, Application Insights / Log Analytics, Key Vault — all in UK South with the documented SKUs (per A34, gaps.md G9),
**When** `ram-reference-data`'s Helm chart is deployed to the dev AKS cluster,
**Then** the service reaches the shared cluster, database, registry, gateway, and observability estate provisioned in Epic 0.0 (this story **consumes** the estate; it does not provision it — AR53 revised),
**And** the deployment fails fast with a clear diagnostic if any Epic 0.0 estate dependency is absent (making the Epic 0.0 → 0.1 sequencing explicit).

**Given** the `ram-architecture` Liquibase baseline changelog runs **before** `ram-reference-data` (it owns the shared infrastructure table),
**When** the baseline is applied to the dev PostgreSQL instance,
**Then** the shared `ram_configuration_values` infrastructure table exists (per FR8, AR19),
**And** `ram-reference-data`'s DB role has `SELECT` on `ram_configuration_values` (per AR22),
**And** `ram-reference-data`'s own service-owned Liquibase changelog directory (`src/main/resources/db/changelog/`, master `db.changelog-master.yaml`) exists but is empty (tier-(a) tables created in Story 0.1.2).

**Given** the shared APIM gateway (provisioned + TLS-verified in Epic 0.0, Story 0.0.5),
**When** `ram-reference-data` registers its API through APIM and an HTTP request reaches the gateway,
**Then** the service's API is reachable over TLS (the gateway TLS floor itself is verified in Epic 0.0 per NFR10),
**And** HTTP-only requests are rejected with a redirect to HTTPS.

**Given** the shared PostgreSQL Flexible Server (provisioned + encryption/TLS-verified in Epic 0.0, Story 0.0.3),
**When** the Helm chart's `values-dev.yaml` is applied,
**Then** the database connection string references the shared Epic 0.0 PostgreSQL instance (storage-encrypted at rest per NFR11; TLS-only per NFR10 — both verified in Epic 0.0),
**And** `ram-reference-data` connects successfully using its own DB role.

**Given** the shared Application Insights workspace (provisioned in Epic 0.0, Story 0.0.4, with the agreed retention policy),
**When** the deployed service emits telemetry,
**Then** `ram-reference-data`'s structured logs and traces land in the shared workspace (retention is owned by Epic 0.0 per NFR26).

**Given** the engineer pushes the initial commit to a feature branch via `git push`,
**And** opens a Pull Request from that branch to `main` **manually via the GitHub web UI** (no `gh` CLI),
**When** the GitHub Actions `ci.yml` workflow runs,
**Then** the workflow runs build + test + Spectral lint + ArchUnit + Spotless + Checkstyle + Helm lint,
**And** all checks pass on the scaffolded baseline,
**And** code coverage report is produced by JaCoCo.

**Given** the PR is merged to `main` **via the GitHub web UI** (the engineer clicks "Merge pull request" after reviewer approval; no `gh` CLI),
**When** `deploy-dev.yml` triggers automatically,
**Then** the service deploys to the dev AKS cluster in UK South (per AR23, NFR31),
**And** the container image is pushed to Azure Container Registry,
**And** the deployed pod passes liveness + readiness probes (per NFR28),
**And** Azure Application Insights receives the first structured log entries via OpenTelemetry Collector (per AR31, NFR27).

**References:** FR8, FR58, FR59; NFR10, NFR11, NFR15, NFR16, NFR24, NFR25–NFR28, NFR31, NFR40, NFR42; AR2–AR17, AR23–AR32, AR41, AR53 (revised — estate provisioned in Epic 0.0); **D10** (`gh` CLI not available — manual GitHub web-UI setup per `ram-architecture/runbooks/github-setup.md`); **depends on Epic 0.0** (shared estate).

> **Scaffolding note:** the HMCTS Crime SpringBoot template base is minimal; `ram-scaffold.sh` assembles the remaining dependencies (Liquibase, Testcontainers, MapStruct, OWASP encoder, docker-compose plugin, OpenAPI tooling, Helm, Key Vault, the CI quality gates) from `hmcts/service-hmcts-springboot-demo` + RAM conventions — inventory in `architecture/starter-template.md` §B (G1.4).

**Explicitly NOT in scope:**
- Tier-(a) `jo_*` / `mrd_*` tables and `ram_sync_status` — Story 0.1.2
- The eLinks sync and MRD ingestion mechanisms — Stories 0.1.3 / 0.1.4
- Tier-(b) RAM-owned tables + the read-only API — Epic 0.3

---

## Story 0.1.2: Tier-(a) upstream `jo_*` tables, `ram_sync_status`, and tier-(a) write protection

As a **RAM Pathfinder platform** (and every downstream consumer of JOH identity and reference data),
I want the 15 `jo_*` upstream-sourced tables and the `ram_sync_status` run-log created with service-owned Liquibase changelogs and enforced single-writer ownership,
So that **`jo_people` and the rest of the tier-(a) surface exist with the correct schema and write protection before the eLinks sync populates them** (FR6 tier (a), AR49).

**Acceptance Criteria:**

**Given** `ram-reference-data` is scaffolded per Story 0.1.1,
**When** the engineer adds the Liquibase changeset `db/changelog/001-init-tier-a-upstream-tables.sql` (formatted-SQL, included from `db.changelog-master.yaml`),
**Then** the 15 `jo_*` tables exist with schemas per `architecture/data-tables.md` (`jo_people`, `jo_appointments`, `jo_judiciary_role_assignments`, `jo_authorisations_with_dates`, `jo_appointment_titles`, `jo_base_locations`, `jo_contract_types`, `jo_genders`, `jo_judiciary_roles`, `jo_jurisdictions`, `jo_locations`, `jo_location_types`, `jo_tickets`, `jo_ticket_categories`, `jo_ticket_category_types`),
**And** `ram_sync_status` exists (RAM-internal ingestion run log),
**And** `jo_people.personnel_number` is the upstream natural key, to which RAM binds a stable `ram_joh_identities.id` (UUID) — the RAM-assigned canonical JOH identifier referenced by every downstream domain table (per AR22); `personnel_number` is the upstream link only,
**And** `jo_jurisdictions` preserves the upstream parent-child hierarchy shape (or establishes it on ingest)[^d8],
**And** the `ram_reference_data` DB role owns the tables; **no other role holds INSERT/UPDATE on any `jo_*` table** (tier-(a) write protection per AR49, FR6),
**And** SELECT grants exist for `ram_authorisation` (identity lookup, Epic 0.2) and placeholder roles for future services,
**And** the ArchUnit/grants fitness function in CI verifies the tier-(a) write-protection rule.

**References:** FR6 tier (a), FR7 (writes follow the tier); NFR15; AR18–AR20, AR22, AR49; D3 (revised), D8, D9 (restructured).

**Explicitly NOT in scope:**
- The eLinks sync that populates these tables — Story 0.1.3
- The `mrd_*` tables — Story 0.1.4
- Tier-(b) RAM-owned tables (regions, offices, vocabularies) — Epic 0.3, Story 0.3.1
- The read-only REST API — Epic 0.3, Story 0.3.2

---

## Story 0.1.3: JOH reference data flows into RAM nightly from the JOH eLinks API

As a **RAM Pathfinder platform** (and every downstream consumer of JOH identity and reference data),
I want an in-process scheduled sync that pulls the JOH eLinks API nightly and refreshes the tier-(a) `jo_*` tables,
So that **`jo_people` exists and is current — making JOH sign-in resolvable (FR1), jurisdiction available (`jo_jurisdictions`, D8), and judicial-holder reference data authoritative without any legacy migration** (revised D3, NFR24).

**Acceptance Criteria:**

**Given** the tier-(a) `jo_*` tables and `ram_sync_status` exist per Story 0.1.2,
**When** the engineer implements the eLinks sync as an in-process `@Scheduled` task (per AR46 — no new deployable, no service principal),
**Then** the sync runs on its nightly schedule and pulls all 15 entities from the JOH eLinks API using the outbound credential held in Azure Key Vault (per NFR16),
**And** it **full-refresh-upserts** each table keyed on the upstream natural key (`personnel_number` for `jo_people`), and mints a `ram_joh_identities` row (a stable RAM JOH UUID keyed to `personnel_number`) for any `jo_people` row lacking one,
**And** rows absent upstream are **marked inactive — never hard-deleted** (FK protection per AR46),
**And** the run is recorded in `ram_sync_status` with source, started/finished timestamps, outcome, per-entity row counts, and error detail (per AR48),
**And** the sync is also manually triggerable by ops (e.g. an actuator-adjacent admin endpoint or k8s Job) for out-of-cycle refreshes.

**Given** the JOH eLinks API is unreachable or returns a malformed payload mid-sync,
**When** the sync fails,
**Then** the previous good state remains fully in place (ingestion is transactional per entity set — never partially written, per AR48),
**And** the failure is recorded in `ram_sync_status` and surfaced via structured logs with correlation ID for ops triage,
**And** reference data is at most one sync cycle stale.

**Given** the sync has run successfully at least once in dev,
**When** `ram-authorisation` (Epic 0.2, Story 0.2.3) looks up a seeded JOH email,
**Then** the lookup resolves against `jo_people` to a `personnel_number`, and via `ram_joh_identities` to the RAM JOH UUID,
**And** dev/CI environments use seeded `jo_*` fixtures loaded by the one-off seed scripts where a live eLinks connection is unavailable (per AR52 — the sync code path is integration-tested against a WireMock/stub eLinks API in CI).

**Given** the JOH eLinks API contract has not yet been confirmed (gaps.md G8.1),
**When** the contract lands,
**Then** the ingestion mapping is validated against it (every upstream field RAM needs has a slot; the natural-key scheme holds; cadence/SLA workable),
**And** any unmapped upstream structure raises an architectural PR (per G8.1) — this AC is the story's external-dependency gate and is tracked explicitly in sprint planning.

**References:** FR1 (identity lookup target), FR6 tier (a), FR7 (writes follow the tier); NFR16, NFR24, NFR25–NFR28; AR46, AR48, AR49; gaps.md G8.1; D3 (revised), D8, D9 (restructured).

**Explicitly NOT in scope:**
- MRD ingestion — Story 0.1.4
- The read-only REST API — Epic 0.3, Story 0.3.2

---

## Story 0.1.4: MRD supplementary reference data is ingested from the weekly Excel feed

As a **RAM Pathfinder platform** (and downstream consumers of JOH Specialisations),
I want the MRD team's weekly Excel workbook ingested from an Azure Blob drop into the `mrd_*` tables,
So that **supplementary judicial reference data not present in JOH eLinks (notably JOH Specialisations) is available in RAM** (revised D3, NFR24) without waiting for MRD's public APIs.

**Acceptance Criteria:**

**Given** a dedicated Azure storage account + Blob container exists for the MRD feed — provisioned via **Terraform in this repo's `terraform/` directory** (per AR53: `ram-reference-data` is the first repo to need this resource; access for the MRD team or ops to drop the weekly workbook),
**And** the Liquibase changeset `db/changelog/002-init-mrd-tables.sql` creates `mrd_specialisms` (further `mrd_*` tables added as MRD entities enter scope) owned by `ram_reference_data` with the same tier-(a) write protection as the `jo_*` tables (per AR49),
**When** the weekly workbook lands in the container,
**Then** a `@Scheduled` task in `ram-reference-data` detects it on its polling cycle (per AR47).

**Given** the ingestion task picks up a workbook,
**When** processing runs,
**Then** the workbook is validated before any write — shape (expected sheets/columns), vocabulary (values resolvable against controlled lists), and referential checks (Specialisations reference resolvable JOH personnel numbers / jurisdiction codes),
**And** valid rows are upserted into the `mrd_*` tables keyed on the upstream natural key,
**And** the processed file is **archived** (moved to an `archive/` path in the container, retained for lineage/audit per AR47),
**And** the run is recorded in `ram_sync_status` (source = `mrd-excel`) with row counts and outcome (per AR48).

**Given** the same workbook is dropped twice (or the task restarts mid-cycle),
**When** ingestion re-runs,
**Then** the result is idempotent per file — no duplicate rows, no spurious updates (per AR47).

**Given** a workbook fails validation,
**When** the task rejects it,
**Then** no `mrd_*` table is modified (previous good state intact, per AR48),
**And** the file is moved to a `rejected/` path with a validation report alongside it,
**And** the failure is recorded in `ram_sync_status` and surfaced via structured logs for ops to liaise with the MRD team (corrections happen at source per FR6 tier (a)).

**Given** MRD's public APIs become available post-MVP,
**When** the integration is upgraded,
**Then** only the reader component swaps (blob pick-up → API client); the `mrd_*` tables and downstream consumers are unchanged (per AR47 — the blob-drop seam is the explicit upgrade point).

**References:** FR6 tier (a), FR7; NFR16, NFR24, NFR25–NFR28; AR47, AR48, AR49, AR53; gaps.md G8.1; D3 (revised).

**Explicitly NOT in scope:**
- MRD API integration (post-MVP — when MRD ships public APIs)
- Hand-editing of `mrd_*` data in RAM (never, in any phase — tier (a) per FR6)

[^d3]: Revised D3 (2026-06-10) — no data migration from any legacy system; judicial-holder reference data is ingested from the JOH eLinks API and MRD.
[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d9]: Restructured D9 (2026-06-10; refined 2026-07-09 per SCP) — two user populations. JOHs resolve IdP email → `jo_people` → `personnel_number` → a **RAM-assigned JOH UUID** (`ram_joh_identities`); HMCTS admin staff via a RAM-internal identity table. Both key on a RAM-assigned UUID; `personnel_number` is the upstream link only. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
