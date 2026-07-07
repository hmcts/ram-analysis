---
type: 'Epic'
description: 'User outcome: A RAM Pathfinder user from either identity population — a JOH (Judge, Tribunal Judge, Tribunal Member) or HMCTS admin staff (RSU, Court user, Tribunal Caseworker, Finance/Payment…'
resource: 'epics/phase-0/epic-0.2-user-authenticates.html'
tags: [ram-pathfinder, epics, phase-0]
timestamp: '2026-06-17'
parent: 'epics/phase-0/index.md'
epic: 0.2
title: 'User authenticates and lands on a role-scoped Home page'
storyCount: 5
---

# Epic 0.2: User authenticates and lands on a role-scoped Home page

**User outcome:** A RAM Pathfinder user from **either identity population** — a JOH (Judge, Tribunal Judge, Tribunal Member) or HMCTS admin staff (RSU, Court user, Tribunal Caseworker, Finance/Payment Authoriser, MI/Reporting) — opens RAM Pathfinder, signs in via SSO, has their canonical identity resolved (personnel number via `jo_people` for JOHs; RAM staff UUID via `ram_auth_staff_identities` for admin staff,[^d9]), has their roles + **jurisdiction** + Region/Area scope resolved, and lands on a Home page showing the navigation and tiles they're authorised to see.

**Depends on Epic 0.1:** `jo_people` (the JOH identity-lookup target) is populated by the eLinks sync (Story 0.1.3); the shared Azure estate (AKS, PostgreSQL, ACR, APIM, App Insights) is provisioned by `ram-reference-data` (Story 0.1.1) and consumed here.

**Vertical slice:**
- `ram-authorisation` scaffolded from the HMCTS Crime SpringBoot template via `ram-scaffold.sh`, following the pattern established by the first-scaffolded service (Epic 0.1, Story 0.1.1); **consumes** the shared Azure estate
- `ram-mock-auth` OIDC issuer for non-prod, with a test-user roster spanning **both identity populations** (per AR35)
- 6-table `ram-authorisation` schema (`ram_auth_users`, `ram_auth_staff_identities`, `ram_auth_roles`, `ram_auth_user_roles`, `ram_auth_user_region_scopes`, `ram_auth_user_activation_flags` with the (jurisdiction, region) tuple) via service-owned Liquibase changelog (per AR18–AR20)
- Custom `JWTFilter` validating tokens against IdP JWKS + `POST /authz/check` performing **two-population identity resolution** and populating request-scoped `AuthDetails` (per AR34)
- `ram-ui` repo scaffolded (React + TypeScript + Vite + Vitest + Playwright; per AR42–AR43)
- `HmctsIdpProvider`, `ProtectedRoute`, `useAuth`, HTTP client with RFC 9457 error handling (per AR44)
- GOV.UK Design System base + HMCTS/RAM Pathfinder extensions
- Home shell with role-scoped nav + Region/Area selector (FR55)

**FRs covered:** FR1, FR2, FR3, FR55, FR56 (business stack portion).

**Key NFRs first exercised here:** NFR12 (JWT propagation), NFR13 (authz enforcement incl. jurisdiction), NFR15 (GovS 7), NFR16 (Key Vault), NFR17–NFR19 (WCAG 2.2 AA + assistive tech + Accessibility Regs 2018), NFR20 (HMCTS IdP integration via mock), NFR40 (per-service deployable on Kubernetes).

**Out of scope (explicitly):** All upstream ingestion + `ram-reference-data` scaffold + shared-estate provisioning + tier-(a) tables (Epic 0.1). Tier-(b) RAM-owned reference data + the read API (Epic 0.3). FR5 machine-to-machine consumer auth (post-MVP per PRD v2.5). Real HMCTS IdP integration (mock-only at Phase 0; cuts over pre-Phase-9 per AR34). Production identity bootstrap + verification job (Epic 0.4).

---

## Story 0.2.1: Scaffold `ram-authorisation` service from the HMCTS Crime SpringBoot template

As a **platform engineer**,
I want to scaffold `ram-authorisation` from the HMCTS Crime SpringBoot template using `ram-scaffold.sh`, consuming the shared Azure estate already provisioned in Epic 0.1,
So that **the authorisation service follows the same consistent, version-pinned, supply-chain-secured baseline** as the first-scaffolded service, and the team can demonstrate the deployment pipeline end-to-end before any domain logic is written.

**Acceptance Criteria:**

**Given** the engineer has performed the GitHub manual-setup checklist (`ram-architecture/runbooks/github-setup.md`) **before** running the scaffold (the canonical manual-setup pattern is established in Epic 0.1, Story 0.1.1):
  - Created an empty private GitHub repo `ram-authorisation` under the HMCTS org **via the GitHub web UI**
  - Enabled branch protection on `main` via Settings → Branches (require PR review, require status checks, require linear history)
  - Note: the `gh` CLI is **NOT** available — all GitHub admin config happens manually via the web UI per the runbook,
**And** the engineer has a clean local development environment with Java 25, Gradle Wrapper, and Docker,
**When** the engineer runs `ram-scaffold.sh ram-authorisation` from `ram-architecture/scaffolding/`,
**Then** the script scaffolds a Spring Boot 4.0.x project **locally** from `https://github.com/hmcts/service-hmcts-crime-springboot-template`, then commits and pushes to the pre-created remote on a feature branch via plain `git` (no `gh` CLI invocation),
**And** Gradle build uses Groovy DSL with Spring Boot Gradle plugin 4.1.0 and `io.spring.dependency-management:1.1.7` (per AR5),
**And** Group ID is `uk.gov.hmcts.ram`, artefact is `ram-authorisation`, base package is `uk.gov.hmcts.ram.authorisation`, default port is 8082 (per AR3),
**And** initial commit message is exactly *"Scaffold RAM Pathfinder authorisation from HMCTS starter"* (per AR4),
**And** Lombok 1.18.46 + MapStruct 1.6.3 are configured (per AR6),
**And** JJWT 0.13.0 + OWASP Encoder 1.4.0 are on the classpath (per AR7),
**And** springdoc-openapi is configured for OpenAPI 3.x generation (per AR8),
**And** JaCoCo, CycloneDX SBOM, gradle-git-properties, gradle-versions, and gradle-docker-compose plugins are configured (per AR9–AR13),
**And** Spring Boot Test with JUnit 5 (`junit-bom:6.0.3`), Testcontainers PostgreSQL 1.21.4, Spring Boot Testcontainers 4.1.0, and spring-boot-starter-webmvc-test are configured (per AR14–AR15),
**And** Spectral, ArchUnit, Spotless, and Checkstyle are configured (per AR17),
**And** a Helm chart skeleton exists at `charts/ram-authorisation/` with `values-dev.yaml`, `values-staging.yaml`, `values-production.yaml` overlays (per AR24),
**And** a `terraform/` directory skeleton exists with per-environment stacks (`dev` / `staging` / `production`) for **this service's own resources only** (e.g. its Key Vault namespace, APIM per-API policy) — the shared estate lives in `ram-reference-data` per AR53,
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

**Given** the shared Azure estate (AKS, encrypted-at-rest PostgreSQL Flexible Server, ACR, APIM, Application Insights / Log Analytics, Key Vault) was provisioned and independently verified in `ram-shared-infrastructure` in **Epic 0.0** (AR53 revised),
**When** `ram-authorisation` deploys,
**Then** it **consumes** the shared cluster, database, registry, gateway, and observability workspace without re-provisioning them,
**And** `ram-authorisation`'s `terraform/` contains only its own resources (Key Vault namespace, APIM per-API policy),
**And** its `values-dev.yaml` connection string references the shared encrypted PostgreSQL instance (per NFR11).

**Given** the `ram-architecture` Liquibase baseline changelog already created the shared `ram_configuration_values` table ahead of `ram-reference-data` (Epic 0.1, Story 0.1.1),
**When** `ram-authorisation` is granted access,
**Then** `ram-authorisation`'s DB role has `SELECT` on `ram_configuration_values` (per FR8, AR19, AR22),
**And** `ram-authorisation`'s own service-owned Liquibase changelog directory (`src/main/resources/db/changelog/`, master `db.changelog-master.yaml`) exists but is empty (auth tables created in Story 0.2.3).

**Given** the deployed service is publicly reachable through the shared APIM (provisioned in Epic 0.1),
**When** an HTTP request reaches APIM,
**Then** the APIM endpoint terminates TLS using the latest TLS version supported by the platform (per NFR10),
**And** HTTP-only requests are rejected with a redirect to HTTPS,
**And** the APIM TLS policy is verified by a CI check using `testssl.sh` (or equivalent) in `ci.yml` that fails on any TLS version below the platform's current minimum.

**Given** the engineer pushes the initial commit to a feature branch via `git push`,
**And** opens a Pull Request from that branch to `main` **manually via the GitHub web UI** (no `gh` CLI),
**When** the GitHub Actions `ci.yml` workflow runs,
**Then** the workflow runs build + test + Spectral lint + ArchUnit + Spotless + Checkstyle + Helm lint,
**And** all checks pass on the scaffolded baseline,
**And** code coverage report is produced by JaCoCo.

**Given** the PR is merged to `main` **via the GitHub web UI** (no `gh` CLI),
**When** `deploy-dev.yml` triggers automatically,
**Then** the service deploys to the dev AKS cluster in UK South (per AR23, NFR31),
**And** the container image is pushed to Azure Container Registry,
**And** the deployed pod passes liveness + readiness probes (per NFR28),
**And** Azure Application Insights receives structured log entries via OpenTelemetry Collector (per AR31, NFR27).

**References:** FR8, FR58, FR59; NFR10, NFR11, NFR15, NFR16, NFR25–NFR28, NFR31, NFR40, NFR42; AR2–AR17, AR23–AR32, AR41, AR53; **D10** (`gh` CLI not available — manual GitHub web-UI setup).

---

## Story 0.2.2: User can authenticate against `ram-mock-auth` and receive a JWT

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

## Story 0.2.3: `ram-authorisation` validates JWTs and resolves identity, roles, jurisdiction + Region/Area scope (read-only API)

As a **calling service or UI**,
I want every RAM Pathfinder HTTP request to flow through `JWTFilter` and resolve the principal's canonical identity, roles, **jurisdiction**, and Region/Area scope via `ram-authorisation`'s **read-only** API,
So that **every domain operation is authorised against bootstrapped user data across both identity populations** (per FR1/FR2, restructured D9, NFR13) and no operation can bypass the Authorisation service. **Admin write endpoints are out of scope for Phase 0 (and MVP)** — user/role/scope edits happen via direct SQL in MVP; an admin UI surface is post-MVP[^d10].

**Acceptance Criteria:**

**Given** `ram-authorisation` is scaffolded per Story 0.2.1,
**When** the engineer adds the authorisation tables via the service-owned Liquibase changeset `db/changelog/001-init-auth-schema.sql`,
**Then** the **6 tables** `ram_auth_users`, `ram_auth_staff_identities`, `ram_auth_roles`, `ram_auth_user_roles`, `ram_auth_user_region_scopes`, `ram_auth_user_activation_flags` exist with the schema specified in `architecture/data-tables.md` (per AR18, AR20),
**And** `ram_auth_users` carries `principal_kind` (JOH / staff / service) and links to `jo_people.personnel_number` (JOH users) or `ram_auth_staff_identities.id` (admin-staff users — RAM-assigned UUID[^d9]),
**And** `ram_auth_users` carries the user's jurisdiction (FK → `jo_jurisdictions`,[^d8]),
**And** `ram_auth_user_activation_flags` carries the **(jurisdiction, region) tuple** per FR57,
**And** the `ram_authorisation` DB role owns the tables (per AR19) and holds SELECT on `jo_people` (identity lookup — `jo_people` is owned by `ram-reference-data` and populated by the Epic 0.1 eLinks sync),
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
**When** the engineer publishes the artefact (via Gradle `maven-publish`) to the internal Maven-format artefact repository,
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
- The auth tables are created here; they're populated by Epic 0.4's seed scripts (dev/CI) and the production bootstrap mechanism outside the PRD's scope[^d9], not by API writes

---

## Story 0.2.4: Scaffold `ram-ui` repo with React + TypeScript + Vite + GOV.UK base + auth wrapper

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

**References:** FR55 (foundation only — Home content populated in Story 0.2.5), FR56; NFR17, NFR18, NFR19, NFR31, NFR40; AR42–AR45b, AR53.

---

## Story 0.2.5: User signs into RAM Pathfinder via SSO and lands on a role-scoped Home page

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
**Then** they see a banner *"Your jurisdiction/region has not yet moved to RAM Pathfinder. Please continue using your current system."* and the workflow nav is disabled (per FR57 surface — full wave activation orchestration is Phase 9+; the incumbent is ListAssist for SSCS wave 1, APEX for Courts waves 2+).

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
**Then** they can show a stakeholder: the platform scaffold + shared estate (Epic 0.1, Story 0.1.1), JOH reference data flowing in from eLinks (Story 0.1.3) and MRD (Story 0.1.4), the auth service scaffold (Story 0.2.1), SSO via mock-auth (Story 0.2.2), two-population authorisation enforcement (Story 0.2.3), UI foundation (Story 0.2.4), and the end-to-end sign-in flow (this story),
**And** Postman collection `ram-authorisation-phase0.postman_collection.json` exercises `POST /v1/authz/check` (both populations + unresolvable principal) and `GET /v1/users/{id}/effective-permissions` against the dev deployment.

**References:** FR1, FR2, FR3, FR55, FR56, FR57 (activation surface); NFR12, NFR13, NFR17, NFR18, NFR19, NFR20, NFR42.

[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d9]: Restructured D9 (2026-06-10) — two user populations: JOHs resolve via jo_people to a personnel number; HMCTS admin staff via a RAM-internal identity table. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
