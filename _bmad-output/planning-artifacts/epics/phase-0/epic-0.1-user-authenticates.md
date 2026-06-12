---
parent: 'epics/phase-0/index.md'
epic: 0.1
title: 'User authenticates and lands on a role-scoped Home page'
storyCount: 7
status: 'restructured-pending-revalidation'
revisedAt: '2026-06-11'
revisionNote: 'SCP 2026-06-10 cascade: two new upstream-ingestion stories (0.1.3 JOH eLinks sync, 0.1.4 MRD ingestion) inserted ahead of authorisation — JOH sign-in resolves identity against jo_people, so ingestion is part of this epic''s vertical slice. Old stories 0.1.3–0.1.5 renumbered 0.1.5–0.1.7. Two-population identity resolution + jurisdiction added to the authz story. FR renumber FR58–FR61 → FR57–FR60.'
---

# Epic 0.1: User authenticates and lands on a role-scoped Home page

**User outcome:** A RAM Pathfinder user from **either identity population** — a JOH (Judge, Tribunal Judge, Tribunal Member) or HMCTS admin staff (RSU, Court user, Tribunal Caseworker, Finance/Payment Authoriser, MI/Reporting) — opens RAM Pathfinder, signs in via SSO, has their canonical identity resolved (personnel number via `jo_people` for JOHs; RAM staff UUID via `ram_auth_staff_identities` for admin staff,[^d9]), has their roles + **jurisdiction** + Region/Area scope resolved, and lands on a Home page showing the navigation and tiles they're authorised to see.

**Why upstream ingestion lives in this epic:** JOH sign-in is impossible without `jo_people` — the identity lookup target — being populated. The JOH eLinks sync (and its MRD companion) is therefore part of this epic's vertical slice, not a separate reference-data concern. It is also the programme's first external integration.

**Vertical slice:**
- **GitHub manual-setup runbook** at `ram-architecture/runbooks/github-setup.md` (the `gh` CLI is **not** available — all GitHub admin operations are manual via the web UI; `ram-scaffold.sh` handles only local scaffolding + `git push` to a pre-created remote)
- First scaffolded backend service: `ram-authorisation` (HMCTS Crime SpringBoot template + `ram-scaffold.sh` conventions per AR2–AR4)
- `ram-mock-auth` OIDC issuer for non-prod, with a test-user roster spanning **both identity populations** (per AR35)
- `ram-reference-data` scaffolded with the **tier-(a) upstream-sourced tables** (15 `jo_*` + `mrd_specialisms` + `ram_sync_status`) and the two ingestion mechanisms: **JOH eLinks nightly in-process sync** (AR46, AR48) and **MRD weekly Excel blob ingestion** (AR47) — tier-(b) RAM-owned tables and the read API land in Epic 0.2
- 6-table `ram-authorisation` schema (`ram_auth_users`, `ram_auth_staff_identities`, `ram_auth_roles`, `ram_auth_user_roles`, `ram_auth_user_region_scopes`, `ram_auth_user_activation_flags` with the (jurisdiction, region) tuple) via service-owned Flyway migration (per AR18–AR20)
- Custom `JWTFilter` validating tokens against IdP JWKS + `POST /authz/check` performing **two-population identity resolution** and populating request-scoped `AuthDetails` (per AR34)
- `ram-ui` repo scaffolded (React + TypeScript + Vite + Vitest + Playwright; per AR42–AR43)
- `HmctsIdpProvider`, `ProtectedRoute`, `useAuth`, HTTP client with RFC 9457 error handling (per AR44)
- GOV.UK Design System base + HMCTS/RAM Pathfinder extensions
- Home shell with role-scoped nav + Region/Area selector (FR55)
- Shared `ram_configuration_values` Flyway baseline established by `ram-architecture` (FR8)

**FRs covered:** FR1, FR2, FR3, FR55, FR56 (business stack portion); FR6/FR7 tier-(a) ingestion portion (NFR24)

**Key NFRs first exercised here:** NFR10 (TLS), NFR11 (data-at-rest), NFR12 (JWT propagation), NFR13 (authz enforcement incl. jurisdiction), NFR15 (GovS 7), NFR16 (Key Vault — incl. the eLinks API credential), NFR17–NFR19 (WCAG 2.2 AA + assistive tech + Accessibility Regs 2018), NFR20 (HMCTS IdP integration via mock), NFR24 (JOH eLinks + MRD MVP integrations), NFR25–NFR28 (structured logs + Application Insights ingestion + liveness/readiness probes), NFR31 (Azure UK South data residency), NFR40 (per-service deployable on Kubernetes)

**Out of scope (explicitly):** FR5 machine-to-machine consumer auth (post-MVP per PRD v2.5). Real HMCTS IdP integration (mock-only at Phase 0; cuts over pre-Phase-9 per AR34). Tier-(b) RAM-owned reference data + the read API (Epic 0.2). Production identity bootstrap + verification job (Epic 0.3).

---

## Story 0.1.1: Scaffold `ram-authorisation` service from HMCTS Crime SpringBoot template

As a **platform engineer**,
I want to scaffold the first RAM Pathfinder backend service from the HMCTS Crime SpringBoot template using `ram-scaffold.sh`,
So that **subsequent services follow a consistent, version-pinned, supply-chain-secured baseline** and the team can demonstrate the deployment pipeline end-to-end before any domain logic is written.

**Acceptance Criteria:**

**Given** the engineer has performed the GitHub manual-setup checklist (`ram-architecture/runbooks/github-setup.md`) **before** running the scaffold:
  - Created an empty private GitHub repo `ram-authorisation` under the HMCTS org **via the GitHub web UI**
  - Enabled branch protection on `main` via Settings → Branches (require PR review, require status checks, require linear history)
  - Note: the `gh` CLI is **NOT** available in the engineering environment — all GitHub admin config (repo creation, branch protection, team access) happens manually via the web UI per the runbook,
**And** the engineer has a clean local development environment with Java 25, Gradle Wrapper, and Docker,
**When** the engineer runs `ram-scaffold.sh ram-authorisation` from `ram-architecture/scaffolding/`,
**Then** the script scaffolds a Spring Boot 4.0.x project **locally** from `https://github.com/hmcts/spring-boot-template`, then commits and pushes to the pre-created remote on a feature branch via plain `git` (no `gh` CLI invocation),
**And** the project contents include a Spring Boot 4.0.x scaffold from `https://github.com/hmcts/spring-boot-template`,
**And** Gradle build uses Groovy DSL with Spring Boot Gradle plugin 4.0.6 and `io.spring.dependency-management:1.1.7` (per AR5),
**And** Group ID is `uk.gov.hmcts.ram`, artefact is `ram-authorisation`, base package is `uk.gov.hmcts.ram.authorisation`, default port is 8082 (per AR3),
**And** initial commit message is exactly *"Scaffold RAM Pathfinder authorisation from HMCTS starter"* (per AR4),
**And** Lombok 1.18.46 + MapStruct 1.6.3 are configured (per AR6),
**And** JJWT 0.13.0 + OWASP Encoder 1.4.0 are on the classpath (per AR7),
**And** springdoc-openapi is configured for OpenAPI 3.x generation (per AR8),
**And** JaCoCo, CycloneDX SBOM, gradle-git-properties, gradle-versions, and gradle-docker-compose plugins are configured (per AR9–AR13),
**And** Spring Boot Test with JUnit 5 (`junit-bom:6.0.3`), Testcontainers PostgreSQL 1.21.4, Spring Boot Testcontainers 4.0.6, and spring-boot-starter-webmvc-test are configured (per AR14–AR15),
**And** Spectral, ArchUnit, Spotless, and Checkstyle are configured (per AR17),
**And** a Helm chart skeleton exists at `charts/ram-authorisation/` with `values-dev.yaml`, `values-staging.yaml`, `values-production.yaml` overlays (per AR24),
**And** a `terraform/` directory skeleton exists with per-environment stacks (`dev` / `staging` / `production`) per AR53,
**And** GitHub Actions workflows exist at `.github/workflows/ci.yml`, `deploy-dev.yml`, `deploy-staging.yml`, `deploy-production.yml` (per AR28),
**And** `CODEOWNERS` and `PULL_REQUEST_TEMPLATE.md` exist (per AR29),
**And** a Postman collection skeleton exists at `postman/ram-authorisation-phase0.postman_collection.json` (per AR41).

**Given** the scaffolded service runs locally via `./gradlew bootRun` after a `docker-compose up postgres`,
**When** the engineer queries `http://localhost:8082/actuator/health`,
**Then** the response is `200 OK` with body `{"status":"UP"}`,
**And** `/actuator/info` returns Git metadata embedded by gradle-git-properties (per NFR28, AR11),
**And** `/actuator/readiness` returns `200 OK`,
**And** structured JSON logs via Logstash Logback Encoder 9.0 appear on stdout (per AR30, NFR25),
**And** logs include a `correlationId` populated by `CorrelationIdFilter` for each request (per AR32).

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

**Given** this is the first service to scaffold in RAM Pathfinder,
**When** the engineer runs the `ram-architecture` Flyway baseline migration,
**Then** the shared `ram_configuration_values` infrastructure table exists in the dev PostgreSQL instance,
**And** `ram-authorisation`'s DB role has `SELECT` on `ram_configuration_values` (per FR8, AR19, AR22),
**And** `ram-authorisation`'s own service-owned Flyway migrations directory exists but is empty (tables created in Story 0.1.5).

**Given** the shared Azure estate — AKS cluster + node pools, PostgreSQL Flexible Server, Azure Container Registry, APIM instance + base policies, Application Insights / Log Analytics workspace — is provisioned via **Terraform in this repo's `terraform/` directory** (per AR53: `ram-authorisation` is the first repo to need these resources, so their Terraform lives here; no Bicep, no portal click-ops),
**When** `terraform apply` has run for the dev stack,
**Then** every shared-estate resource above exists in UK South with the documented SKUs (multi-AZ node pools; zone-redundant PostgreSQL HA; APIM and ACR zone-redundant SKUs per A34),
**And** the Terraform state backend + plan/apply pipeline arrangement follows the HMCTS-confirmed pattern (gaps.md G9).

**Given** the deployed service is publicly reachable through APIM (Terraform-provisioned above),
**When** an HTTP request reaches APIM,
**Then** the APIM endpoint terminates TLS using the latest TLS version supported by the platform (per NFR10),
**And** HTTP-only requests are rejected with a redirect to HTTPS,
**And** the APIM policy is verified by a CI check using `testssl.sh` (or equivalent) in `ci.yml` that fails on any TLS version below the platform's current minimum.

**Given** Azure-managed PostgreSQL is provisioned for the dev environment (via the Terraform stack above, per AR53),
**When** the Helm chart's `values-dev.yaml` is applied,
**Then** the database connection string references an Azure Database for PostgreSQL Flexible Server instance with storage encryption at rest enabled (per NFR11),
**And** the AKS persistent volumes used by any stateful workload are provisioned with Azure-managed encryption at rest,
**And** the configuration is documented in `ram-architecture/ADR-XXXX-data-at-rest-encryption.md`.

**Given** the Application Insights workspace is provisioned for RAM Pathfinder (via the Terraform stack above, per AR53),
**When** the engineer configures log retention policy,
**Then** the retention period is set to the value agreed with HMCTS data-retention policy owners (default at Phase 0: **90 days for non-prod**, **365 days for production**, subject to HMCTS sign-off; per NFR26),
**And** the chosen value is recorded in `ram-architecture/ADR-XXXX-log-retention.md` with the responsible HMCTS owner identity,
**And** the retention setting is applied to the Application Insights workspace via **Terraform** (in this repo's `terraform/` stack, per AR53 — Terraform is the HMCTS standard; no Bicep).

**References:** FR8, FR58, FR59; NFR10, NFR11, NFR15, NFR16, NFR25–NFR28, NFR31, NFR40, NFR42; AR2–AR17, AR23–AR32, AR41, AR53; **D10** (admin UI removed from MVP; `gh` CLI not available — manual GitHub web-UI setup per `ram-architecture/runbooks/github-setup.md`).

---

## Story 0.1.2: User can authenticate against `ram-mock-auth` and receive a JWT

As a **RAM Pathfinder user from either identity population** (a JOH, or HMCTS admin staff — RSU, Court user, Tribunal Caseworker, Finance, MI/Reporting),
I want to authenticate against `ram-mock-auth` in non-prod environments using my email,
So that **RAM Pathfinder development and CI/UAT can proceed end-to-end without HMCTS IdP integration being live**, while preserving the same JWT shape that HMCTS IdP will issue at production cutover.

**Acceptance Criteria:**

**Given** the engineer has manually pre-created the private GitHub repo `ram-mock-auth` with branch protection on `main` via the GitHub web UI (per `ram-architecture/runbooks/github-setup.md`; the `gh` CLI is **not** available — see Story 0.1.1 for the canonical manual-setup pattern),
**And** runs `ram-scaffold.sh ram-mock-auth` (following the Story 0.1.1 pattern),
**When** the scaffold completes,
**Then** the service has the same baseline as Story 0.1.1 (Spring Boot 4.0.x, Helm chart, GitHub Actions, Actuator),
**And** the service implements OIDC `authorization_code` flow for human users,
**And** the service implements `client_credentials` flow for batch / scheduled components (used by Phase 6 — flow established here),
**And** a JWKS endpoint serves rotating signing keys at `/.well-known/jwks.json`,
**And** OIDC discovery is served at `/.well-known/openid-configuration`.

**Given** `ram-mock-auth` is starting up,
**When** the Spring profile in use is `production`,
**Then** the application refuses to start with a fatal error message *"ram-mock-auth must not be deployed to production"* (per AR35, gaps.md G5.3),
**And** the production `deploy-production.yml` workflow is configured to never deploy `ram-mock-auth`.

**Given** `ram-mock-auth` is seeded with a test-user roster spanning **both identity populations** (per AR35, restructured D9):
  - JOH test users (e.g. `joh.test@example.justice.gov.uk` — a Tribunal Judge whose email matches a seeded `jo_people` row with a known personnel number; `tribunal.member.test@example.justice.gov.uk` — a Medical Member)
  - admin-staff test users (e.g. `caseworker.test@example.justice.gov.uk` — a Tribunal Caseworker; `rsu.test@example.justice.gov.uk` — an RSU Admin; matched to seeded `ram_auth_staff_identities` rows),
**When** a user navigates to the OIDC authorisation endpoint with valid client + redirect parameters,
**Then** the user is presented with a development-mode login screen (no real password — selection by email from a seeded list, with banner *"Development authentication only — not for production"*),
**And** after selection, the user is redirected back with an authorisation code,
**And** the code can be exchanged for an ID token + access token via the token endpoint,
**And** the returned JWT contains the standard OIDC claims (`sub`, `email`, `iss`, `aud`, `exp`, `iat`),
**And** the JWT signature validates against the JWKS endpoint.

**Given** a service-token client `ram-payment-batch-client` is seeded in `ram-mock-auth`,
**When** a `client_credentials` grant is requested with valid client credentials,
**Then** a service-principal JWT is returned with claims identifying the client (per NFR12 revised v2.6, AR36),
**And** the JWT validates against the same JWKS endpoint.

**Given** `ram-mock-auth` is deployed to dev AKS,
**When** an unauthenticated request reaches a discovery URL,
**Then** the response is `200 OK` (discovery is public),
**And** all other endpoints require valid credentials and return RFC 9457 problem-details on failure (per AR37, NFR39).

**References:** FR1; NFR10, NFR12, NFR16, NFR20; AR34, AR35, AR36, AR37.

---

## Story 0.1.3: JOH reference data flows into RAM nightly from the JOH eLinks API

As a **RAM Pathfinder platform** (and every downstream consumer of JOH identity and reference data),
I want `ram-reference-data` scaffolded with the tier-(a) upstream-sourced tables and an in-process scheduled sync that pulls the JOH eLinks API nightly,
So that **`jo_people` exists and is current — making JOH sign-in resolvable (FR1), jurisdiction available (`jo_jurisdictions`, D8), and judicial-holder reference data authoritative without any legacy migration** (revised D3, NFR24).

**Acceptance Criteria:**

**Given** the engineer has manually pre-created the private GitHub repo `ram-reference-data` with branch protection on `main` via the GitHub web UI (per the Story 0.1.1 pattern),
**And** runs `ram-scaffold.sh ram-reference-data`,
**When** the scaffold completes,
**Then** the new repo follows all conventions from Story 0.1.1 (Spring Boot 4, Helm chart, GitHub Actions, Actuator, structured logs, OpenAPI tooling, Spectral, ArchUnit, Spotless, Checkstyle, Pact, Postman),
**And** Group ID is `uk.gov.hmcts.ram`, artefact is `ram-reference-data`, package is `uk.gov.hmcts.ram.referencedata`, default port is 8082,
**And** initial commit is *"Scaffold RAM Pathfinder reference-data from HMCTS starter"* (per AR4),
**And** the scaffold includes the `terraform/` directory skeleton for this service's own resources (Key Vault namespace; the MRD storage in Story 0.1.4) per AR53.

**Given** the engineer adds Flyway migration `V1__init_tier_a_upstream_tables.sql`,
**When** the migration runs,
**Then** the 15 `jo_*` tables exist with schemas per `architecture/data-tables.md` (`jo_people`, `jo_appointments`, `jo_judiciary_role_assignments`, `jo_authorisations_with_dates`, `jo_appointment_titles`, `jo_base_locations`, `jo_contract_types`, `jo_genders`, `jo_judiciary_roles`, `jo_jurisdictions`, `jo_locations`, `jo_location_types`, `jo_tickets`, `jo_ticket_categories`, `jo_ticket_category_types`),
**And** `ram_sync_status` exists (RAM-internal ingestion run log),
**And** `jo_people.personnel_number` is the primary key — the canonical JOH identifier referenced by every downstream domain table (per AR22),
**And** `jo_jurisdictions` preserves the upstream parent-child hierarchy shape (or establishes it on ingest)[^d8],
**And** the `ram_reference_data` DB role owns the tables; **no other role holds INSERT/UPDATE on any `jo_*` table** (tier-(a) write protection per AR49, FR6),
**And** SELECT grants exist for `ram_authorisation` (identity lookup) and placeholder roles for future services,
**And** the ArchUnit/grants fitness function in CI verifies the tier-(a) write-protection rule.

**Given** the engineer implements the eLinks sync as an in-process `@Scheduled` task (per AR46 — no new deployable, no service principal),
**When** the sync runs on its nightly schedule,
**Then** it pulls all 15 entities from the JOH eLinks API using the outbound credential held in Azure Key Vault (per NFR16),
**And** it **full-refresh-upserts** each table keyed on the upstream natural key (`personnel_number` for `jo_people`),
**And** rows absent upstream are **marked inactive — never hard-deleted** (FK protection per AR46),
**And** the run is recorded in `ram_sync_status` with source, started/finished timestamps, outcome, per-entity row counts, and error detail (per AR48),
**And** the sync is also manually triggerable by ops (e.g. an actuator-adjacent admin endpoint or k8s Job) for out-of-cycle refreshes.

**Given** the JOH eLinks API is unreachable or returns a malformed payload mid-sync,
**When** the sync fails,
**Then** the previous good state remains fully in place (ingestion is transactional per entity set — never partially written, per AR48),
**And** the failure is recorded in `ram_sync_status` and surfaced via structured logs with correlation ID for ops triage,
**And** reference data is at most one sync cycle stale.

**Given** the sync has run successfully at least once in dev,
**When** `ram-authorisation` (Story 0.1.5) looks up a seeded JOH email,
**Then** the lookup resolves against `jo_people` to a personnel number,
**And** dev/CI environments use seeded `jo_*` fixtures loaded by the one-off seed scripts where a live eLinks connection is unavailable (per AR52 — the sync code path is integration-tested against a WireMock/stub eLinks API in CI).

**Given** the JOH eLinks API contract has not yet been confirmed (gaps.md G8.1),
**When** the contract lands,
**Then** the ingestion mapping is validated against it (every upstream field RAM needs has a slot; the natural-key scheme holds; cadence/SLA workable),
**And** any unmapped upstream structure raises an architectural PR (per G8.1) — this AC is the story's external-dependency gate and is tracked explicitly in sprint planning.

**References:** FR1 (identity lookup target), FR6 tier (a), FR7 (writes follow the tier); NFR16, NFR24, NFR25–NFR28; AR2–AR4, AR18–AR20, AR46, AR48, AR49; gaps.md G8.1; D3 (revised), D8, D9 (restructured).

**Explicitly NOT in scope:**
- Tier-(b) RAM-owned tables (regions, offices, vocabularies) and their seed — Epic 0.2 Story 0.2.1
- The read-only REST API — Epic 0.2 Story 0.2.2
- MRD ingestion — Story 0.1.4

---

## Story 0.1.4: MRD supplementary reference data is ingested from the weekly Excel feed

As a **RAM Pathfinder platform** (and downstream consumers of JOH Specialisations),
I want the MRD team's weekly Excel workbook ingested from an Azure Blob drop into the `mrd_*` tables,
So that **supplementary judicial reference data not present in JOH eLinks (notably JOH Specialisations) is available in RAM** (revised D3, NFR24) without waiting for MRD's public APIs.

**Acceptance Criteria:**

**Given** a dedicated Azure storage account + Blob container exists for the MRD feed — provisioned via **Terraform in this repo's `terraform/` directory** (per AR53: `ram-reference-data` is the first repo to need this resource; access for the MRD team or ops to drop the weekly workbook),
**And** Flyway migration `V2__init_mrd_tables.sql` creates `mrd_specialisms` (further `mrd_*` tables added as MRD entities enter scope) owned by `ram_reference_data` with the same tier-(a) write protection as the `jo_*` tables (per AR49),
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

---

## Story 0.1.5: `ram-authorisation` validates JWTs and resolves identity, roles, jurisdiction + Region/Area scope (read-only API)

As a **calling service or UI**,
I want every RAM Pathfinder HTTP request to flow through `JWTFilter` and resolve the principal's canonical identity, roles, **jurisdiction**, and Region/Area scope via `ram-authorisation`'s **read-only** API,
So that **every domain operation is authorised against bootstrapped user data across both identity populations** (per FR1/FR2, restructured D9, NFR13) and no operation can bypass the Authorisation service. **Admin write endpoints are out of scope for Phase 0 (and MVP)** — user/role/scope edits happen via direct SQL in MVP; an admin UI surface is post-MVP[^d10].

**Acceptance Criteria:**

**Given** `ram-authorisation` is scaffolded per Story 0.1.1,
**When** the engineer adds the authorisation tables via service-owned Flyway migration `V1__init_auth_schema.sql`,
**Then** the **6 tables** `ram_auth_users`, `ram_auth_staff_identities`, `ram_auth_roles`, `ram_auth_user_roles`, `ram_auth_user_region_scopes`, `ram_auth_user_activation_flags` exist with the schema specified in `architecture/data-tables.md` (per AR18, AR20),
**And** `ram_auth_users` carries `principal_kind` (JOH / staff / service) and links to `jo_people.personnel_number` (JOH users) or `ram_auth_staff_identities.id` (admin-staff users — RAM-assigned UUID[^d9]),
**And** `ram_auth_users` carries the user's jurisdiction (FK → `jo_jurisdictions`,[^d8]),
**And** `ram_auth_user_activation_flags` carries the **(jurisdiction, region) tuple** per FR57,
**And** the `ram_authorisation` DB role owns the tables (per AR19) and holds SELECT on `jo_people` (identity lookup),
**And** ArchUnit fitness functions in CI verify that no other service writes to these tables.

**Given** the engineer implements `JWTFilter` per architecture pattern (AR34),
**When** an HTTP request arrives at any endpoint other than `/actuator/health`, `/actuator/readiness`, or `/actuator/info`,
**Then** the filter extracts the JWT from the `Authorization: Bearer ...` header,
**And** validates the signature against the IdP's JWKS endpoint (`ram-mock-auth` in non-prod; HMCTS IdP from pre-Phase-9 cutover — configurable via Spring profile + Key Vault),
**And** rejects unauthenticated requests with `401 Unauthorized` and an RFC 9457 problem-details body (per NFR12, AR37),
**And** on successful validation calls the service's own `POST /authz/check` to resolve the principal,
**And** populates a request-scoped `AuthDetails` bean accessible to controllers and services.

**Given** an authenticated request reaches `POST /v1/authz/check` with a body `{"principal": "joh.test@example.justice.gov.uk"}` (a **JOH** user),
**When** the email resolves against `jo_people`,
**Then** the response is `200 OK` with a body containing `{"principal": "...", "canonicalId": "<personnel_number>", "population": "joh", "roles": [...], "jurisdiction": "...", "regions": [...], "areas": [...], "activated": true/false}`,
**And** the personnel number is the canonical identifier carried in `AuthDetails` (per FR1, AR34).

**Given** an authenticated request reaches `POST /v1/authz/check` with a body `{"principal": "caseworker.test@example.justice.gov.uk"}` (an **admin-staff** user),
**When** the email resolves against `ram_auth_staff_identities`,
**Then** the response is `200 OK` with `{"canonicalId": "<staff-uuid>", "population": "staff", ...}` and the same roles/jurisdiction/scope/activation shape — **both populations share the same authorisation model**[^d9],
**And** roles and scope are resolved by joining `ram_auth_users → ram_auth_user_roles → ram_auth_roles` and `ram_auth_users → ram_auth_user_region_scopes`,
**And** the response includes the `ram_auth_user_activation_flags` state per (jurisdiction, region) tuple (FR57).

**Given** a valid IdP JWT whose email matches **neither** `jo_people` **nor** `ram_auth_staff_identities`,
**When** `POST /v1/authz/check` runs,
**Then** the principal is rejected with an RFC 9457 authorisation problem — same handling as a non-activated user (per AR34),
**And** the rejection is logged with correlation ID (no account auto-creation).

**Given** an authenticated request reaches `GET /v1/users/{id}/effective-permissions` (per FR3),
**When** the caller's `AuthDetails` indicates they're querying their own ID OR they have a system-admin role,
**Then** the response is `200 OK` with a structured permissions document,
**And** if neither condition is met, the response is `403 Forbidden` with an RFC 9457 problem-details body.

**Given** the OpenAPI spec is generated by springdoc,
**When** the engineer publishes the artefact to the internal Maven repo,
**Then** `uk.gov.hmcts.ram:api-ram-authorisation:1.0.0` is available,
**And** Spectral lint passes on the spec,
**And** the spec includes URL versioning `/v1/...` (per AR38),
**And** the spec declares the RFC 9457 problem-details schema for error responses,
**And** APIM-injected `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) header policies are documented (per AR39).

**Given** a request through APIM has its `/actuator/*` paths blocked,
**When** an external caller attempts `GET /actuator/health` via the public APIM hostname,
**Then** the request is rejected at APIM (per AR27, AR33),
**And** internal Kubernetes liveness/readiness probes still reach the pod directly.

**References:** FR1, FR2, FR3, FR57 (flag surface), FR58, FR59; NFR12, NFR13, NFR25, NFR28, NFR39, NFR40; AR18–AR22, AR27, AR32, AR33, AR34, AR37–AR39, AR52; D8, D9 (restructured).

**Explicitly NOT in scope (deferred post-MVP):**
- Admin write endpoints on `ram-authorisation` for updating user roles, jurisdiction, Region/Area scope, or activation flags
- The auth tables are created here; they're populated by Epic 0.3's seed scripts (dev/CI) and the production bootstrap mechanism outside the PRD's scope[^d9], not by API writes

---

## Story 0.1.6: Scaffold `ram-ui` repo with React + TypeScript + Vite + GOV.UK base + auth wrapper

As a **front-end engineer**,
I want to scaffold the `ram-ui` business-facing SPA repo with all RAM Pathfinder conventions (auth, design system, HTTP client, accessibility CI, Playwright),
So that **per-domain UI modules built in Phases 1–8 land on a stable, audited, accessible foundation** rather than each domain phase re-deriving its own conventions.

**Acceptance Criteria:**

**Given** the engineer has manually pre-created the private GitHub repo `ram-ui` with branch protection on `main` via the GitHub web UI (per `ram-architecture/runbooks/github-setup.md`; the `gh` CLI is **not** available — repo creation, branch protection, team access, and CODEOWNERS-setting are manual web-UI operations),
**And** the engineer initialises the `ram-ui` repo locally from a Vite React+TypeScript template and pushes via plain `git push` to the pre-created remote,
**When** scaffolding completes,
**Then** the repo uses React + TypeScript + Vite + Vitest (unit) + Playwright (E2E) per AR42,
**And** the repo is private under HMCTS org with branch protection on `main`,
**And** dependencies include GOV.UK Design System base + HMCTS/RAM Pathfinder extensions,
**And** TanStack Query is configured for HTTP request lifecycle management,
**And** OpenAPI client generation tooling is configured to consume per-service OpenAPI artefacts and emit clients into `src/modules/{domain}/api/` (per AR43).

**Given** the engineer implements the auth wrapper in `src/shared/auth/`,
**When** the wrapper is complete,
**Then** `HmctsIdpProvider.tsx` exposes the OIDC client context (configurable per environment via Vite env vars to point at `ram-mock-auth` in dev/CI and HMCTS IdP in pre-prod/prod),
**And** `ProtectedRoute.tsx` redirects unauthenticated users to the SSO sign-in flow,
**And** `useAuth.ts` exposes `{ user, isLoading, isAuthenticated, signIn, signOut }`,
**And** the HTTP client in `src/shared/api/httpClient.ts` attaches `Authorization: Bearer ...` to every authenticated request,
**And** `src/shared/api/errorHandling.ts` translates RFC 9457 problem-details responses into UI-ready error structures with title + detail + field-level errors where present (per AR44).

**Given** the engineer wires up the design system foundation,
**When** the foundation is complete,
**Then** GOV.UK Design System base CSS is loaded,
**And** HMCTS / RAM Pathfinder design tokens (colours, spacing, typography) are applied,
**And** a `<PageLayout>` component exposes a header, primary nav slot, region selector slot, main content slot, and footer,
**And** the layout is responsive (mobile / tablet / desktop breakpoints).

**Given** the engineer configures accessibility CI,
**When** axe-core checks run as part of `ci.yml`,
**Then** the build fails on any new WCAG 2.2 AA violation,
**And** keyboard navigation is verified by a Playwright smoke test (tab order through nav, focus indicator visible — per NFR18),
**And** screen-reader-relevant ARIA labels are present on tabbed and dynamic content.

**Given** the engineer publishes the first Playwright E2E suite,
**When** `tests/e2e/phase-0-foundation.spec.ts` runs in CI,
**Then** the suite verifies app starts, redirects unauthenticated users to mock-auth, and renders a placeholder landing route after authentication (per AR45 pattern).

**Given** the engineer configures deployment,
**And** the Azure Static Web App resource is provisioned via **Terraform in this repo's `terraform/` directory** (per AR53: `ram-ui` is the first repo to need it),
**When** the PR is merged,
**Then** the bundle is built and deployed to the Terraform-provisioned Azure Static Web App in UK South dev environment,
**And** the deployment is independent of any future `ram-admin-ui` deployment (per AR45b — `ram-admin-ui` itself is post-MVP[^d10]),
**And** the dev hostname (configurable in production to `ram.hmcts.gov.uk`) resolves to the new deployment.

**References:** FR55 (foundation only — Home content populated in Story 0.1.7), FR56; NFR17, NFR18, NFR19, NFR31, NFR40; AR42–AR45b, AR53.

---

## Story 0.1.7: User signs into RAM Pathfinder via SSO and lands on a role-scoped Home page

As a **RAM Pathfinder user from either identity population** (JOH or admin staff),
I want to sign into RAM Pathfinder via SSO, have my canonical identity, roles, jurisdiction, and Region/Area scope resolved, and see a Home page with navigation and tiles scoped to what I'm authorised to do,
So that **I can begin using RAM Pathfinder's workflows** — and at end of Phase 0 the platform pattern is demoable end-to-end across `ram-mock-auth` → `jo_people` (eLinks-synced) → `ram-authorisation` → `ram-ui` (per the Phase 0 demo gate).

**Acceptance Criteria:**

**Given** the user opens `ram-ui` while not authenticated,
**When** they navigate to any protected route,
**Then** `ProtectedRoute` redirects to the OIDC sign-in flow at `ram-mock-auth` (in non-prod),
**And** the user completes the dev-mode login (selects their seeded test user — JOH or admin staff),
**And** they are redirected back to `ram-ui` with the authorisation code in the URL,
**And** the HTTP client exchanges the code for an ID token + access token,
**And** the user is redirected to `/home`.

**Given** the user is authenticated,
**When** the Home page renders,
**Then** the page shows a header with the RAM Pathfinder brand, user name, sign-out button, and a Region/Area selector populated with the regions/areas the user is authorised for (resolved via `useAuth().user.regions` from `ram-authorisation`'s `POST /authz/check`, which also resolved their canonical identity and jurisdiction),
**And** the primary navigation shows only the links the user's roles authorise (e.g. a JOH sees "My Itinerary" and "Request Absence" but not operational admin workflows; a Tribunal Caseworker or RSU Admin sees the operational workflows),
**And** the page shows placeholder summary tiles (JOHs count, pending absences, vacancies, payments — all rendering "—" or "loading" at Phase 0; real values land in Phase 1+),
**And** a contextual help link is present in the footer.

**Given** the user is signed in,
**When** they click sign-out,
**Then** the OIDC end-session flow runs against `ram-mock-auth`,
**And** the user is redirected back to `ram-ui` and lands on an unauthenticated landing page,
**And** the access token and refresh token are cleared from client storage.

**Given** the user has an `ram_auth_user_activation_flags` entry indicating their (jurisdiction, region) wave is NOT activated for RAM Pathfinder yet,
**When** they land on Home,
**Then** they see a banner *"Your jurisdiction/region has not yet moved to RAM Pathfinder. Please continue using your current system."* and the workflow nav is disabled (per FR57 surface — full wave activation orchestration is Phase 9+; the incumbent is GAPS for SSCS wave 1, APEX for Courts waves 2+).

**Given** axe-core checks run on the rendered Home page,
**When** the page is in a steady state,
**Then** no new WCAG 2.2 AA violations are reported,
**And** keyboard navigation works through the header, Region/Area selector, primary nav, and tiles,
**And** focus indicators are visible.

**Given** Playwright E2E tests for Phase 0 run,
**When** `tests/e2e/phase-0-foundation.spec.ts` executes,
**Then** it covers: unauthenticated redirect → mock-auth sign-in (one JOH user + one admin-staff user) → Home renders with role-scoped nav → activation banner for a non-activated wave → sign-out flow,
**And** all assertions pass against the dev deployment.

**Given** the Phase 0 demo gate,
**When** the engineering lead runs the Phase 0 walkthrough,
**Then** they can show a stakeholder: scaffolding pattern (Story 0.1.1), SSO via mock-auth (Story 0.1.2), JOH reference data flowing in from eLinks (Story 0.1.3) and MRD (Story 0.1.4), two-population authorisation enforcement (Story 0.1.5), UI foundation (Story 0.1.6), and the end-to-end sign-in flow (this story),
**And** Postman collection `ram-authorisation-phase0.postman_collection.json` exercises `POST /v1/authz/check` (both populations + unresolvable principal) and `GET /v1/users/{id}/effective-permissions` against the dev deployment.

**References:** FR1, FR2, FR3, FR55, FR56, FR57 (activation surface); NFR12, NFR13, NFR17, NFR18, NFR19, NFR20, NFR42.

[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d9]: Restructured D9 (2026-06-10) — two user populations: JOHs resolve via jo_people to a personnel number; HMCTS admin staff via a RAM-internal identity table. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
