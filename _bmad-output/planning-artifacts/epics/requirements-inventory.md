---
type: 'Requirements Inventory'
title: 'Requirements Inventory'
description: 'All Functional, Non-Functional, Architecture-derived, and UX Design requirements for RAM Pathfinder.'
resource: 'epics/requirements-inventory.html'
tags: [ram-pathfinder, epics]
timestamp: '2026-06-11'
parent: 'epics/index.md'
purpose: 'All Functional, Non-Functional, Architecture-derived, and UX Design requirements for RAM Pathfinder'
sourceDocuments:
  - 'planning-artifacts/prd.md'
  - 'planning-artifacts/architecture.md (whole + architecture/ folder)'
---

# Requirements Inventory

## Functional Requirements

### Identity & Authorisation

- FR1: Authenticated users access RAM Pathfinder via HMCTS IdP single sign-on; password, session, and account lifecycle are owned by the IdP. At authentication time, the IdP email is resolved to RAM Pathfinder's canonical identifier — the **RAM JOH UUID** (JOH users, via `jo_people` → `personnel_number` → `ram_joh_identities`) or a RAM-internal staff identifier (admin-staff users, via `ram_auth_staff_identities`)[^d9].
- FR2: RAM Pathfinder's Authorisation service maps each authenticated principal to one or more roles, a **jurisdiction**, and a Region/Area scope, and authorises every system call against that mapping.
- FR3: Authorised users can retrieve their effective permissions for their authenticated session.
- FR4[^d10]: System administrators can update role, jurisdiction, and Region/Area assignments for any user. In MVP the data layer is editable by DBAs via direct SQL per operational runbook; the admin UI surface (`ram-admin-ui` Users & Roles module) is post-MVP.
- FR5 *(post-MVP)*: External machine-to-machine consumers require an authentication mechanism. At MVP, no machine-to-machine consumers are in scope; mechanism for genuine service-principal authentication is a post-MVP open question (see `architecture/gaps.md` G7).

### Foundational Data Management

- FR6[^d10]: RSU users can **view** Reference Data through `ram-reference-data`'s versioned read API. Two ownership tiers in **separate tables** (lineage preserved): **(a) upstream-sourced** (`jo_*` JOH eLinks entities + `mrd_*` MRD entities) — read-only in RAM, refreshed from source, corrections at source, no RAM write surface in any phase; **(b) RAM-owned** — data not existing upstream plus operational state over upstream entities; DBAs via SQL in MVP, RSU-facing maintenance UI post-MVP.
- FR7: Every RAM Pathfinder service reads Reference Data via **direct SQL** on the shared schema's Reference Data tables (SELECT-granted per service role) — no client class, no API fan-out, no cache (architecture Principle 2). **Writes follow the tier**: tier-(a) tables written exclusively by the upstream-ingestion mechanisms (JOH eLinks sync + MRD weekly Excel feed); tier-(b) tables by DBAs via SQL in MVP. `ram-reference-data` is the **single owner** of all reference-data tables; no service holds duplicate or cached copies.
- FR8: Cross-service runtime policy values are stored in a shared `ram_configuration_values` infrastructure table, schema-managed by `ram-architecture`'s Liquibase baseline changelog and SELECT-granted to every RAM Pathfinder service DB role. Per-service config uses Spring profiles + `application.yml` + Azure Key Vault.
- FR9: RAM Pathfinder dispatches transactional emails (booking acknowledgements, absence acknowledgements, payment schedules) via HMCTS email infrastructure, with a delivery log retained.

### JOH Records & Working Patterns

- FR10: RSU users can search and filter **JOHs** by name, base location, location type, and JOH type.
- FR11: RSU users can **view** JOH profiles through `ram-reference-data`'s read API — personal details, JOH type, base office, active/inactive status, payroll number, retirement date, fee entitlement, London weighting, name-for-itinerary, heading, tickets, and tribunal-member Specialisations. Upstream-sourced fields are tier (a) per FR6 (read-only, corrections at source); RAM-owned operational state and overlays (location per FR17, working patterns per FR12, ticket overlays per FR15) are tier (b) — separate tables **keyed by `joh_id` → `ram_joh_identities`**.
- FR12: Authorised users can define and update Working Patterns (None / Daily / Weekly) for JOHs, with target sit %, jurisdictional split, and per-day work-type pattern. RAM-owned operational state per FR6 tier (b).
- FR13: RAM Pathfinder auto-populates JOH itineraries up to the next 31st March from the working pattern, preserving any prior absences.
- FR14: A JOH's salaried full-time / part-time status is sourced from JOH eLinks (`jo_contract_types`); RAM displays the current status; conversions happen upstream and are reflected at the next sync. Mandatory-sitting-days adjustments follow the upstream change automatically.
- FR15: RAM Pathfinder exposes ticket information per JOH role through `ram-reference-data`'s read API, combining (a) upstream `jo_tickets` (tier (a) — read-only) and (b) RAM-overlay tickets/authorisations in RAM-owned tables keyed by `joh_id` → `ram_joh_identities` (tier (b)); overlay rows editable by admin staff — DBAs via SQL in MVP.
- FR16: RAM Pathfinder validates that jurisdictional split percentages total 100% before saving.
- FR17: RSU users can switch a JOH's base location to another office within the same Region; cross-Region changes require OPT Advice Point and are out-of-system. Location changes are RAM-owned operational state (tier (b)); not propagated back to JOH eLinks.
- FR18: Authorised users can link to JOHs managed by other offices (off-circuit / cross-Region) for booking purposes (e.g. composing tribunal panels with members from other regions).

### Absence Workflow

- FR19: Authorised users (RSU, Court, Judges where permitted) can record absence requests with start/end date, partial-day option (full / AM / PM), type from a controlled list, and an NTBF flag.
- FR20: RAM Pathfinder distinguishes auto-confirmed absences (from judicial teams) from those requiring confirmation (from Courts or judges); confirmation can trigger an acknowledgement email.
- FR21: Sickness absences can be extended without creating a new record; non-sickness extensions require a new absence record.
- FR22: Authorised users can mark absences as *Not To Be Filled* (NTBF) or as *needs fee-paid cover*.

### Vacancy & Cover

- FR23: RAM Pathfinder auto-creates a vacancy when an approved absence requires fee-paid cover, pre-populated with JOH type, work type, ticket, and dates.
- FR24: Authorised users can create standalone vacancies independent of any absence.
- FR25: Authorised users can edit a vacancy's daily breakdown — cancel individual days with a captured reason; extend or shorten the period.
- FR26: RAM Pathfinder marks a vacancy as filled when a booking is created against it; vacancy days cannot be cancelled once a booking is recorded.
- FR27: RAM Pathfinder surfaces fee-paid JOHs matching a vacancy's filter as a hint for advertising; advertising itself is performed out-of-system by judicial teams. Allocation decisions are recorded in RAM via the UI by admin staff — not pushed in from external systems[^d12].
- FR28: Authorised users can cancel or close vacancies (e.g. when a parent absence becomes NTBF).

### Booking Management

- FR29: Authorised users can create fee-paid bookings (linked to a vacancy or standalone), capturing **JOH**, **court / tribunal**, date, session type (full / AM / PM / evening / reserved-matter), booking type, and work type.
- FR30: Booking creation marks the linked vacancy as filled within the same transaction when a `vacancyId` is supplied (in-process direct DB update on the `ram_vacancies` row using a per-service DB role grant, per architecture Principle 1).
- FR31: RAM Pathfinder tracks booking status (planned, provisional, confirmed, cancelled, rejected) with reason capture for cancellation.
- FR32: RAM Pathfinder sends booking acknowledgement emails to fee-paid **JOHs**, batched overnight or sent immediately via *Create and Email Now*.
- FR33: RAM Pathfinder requires a Y/N answer at booking time when a **JOH's** fee entitlement is *Ask when booking*.
- FR34: RAM Pathfinder prevents double-booking of fee-paid **JOHs** for overlapping sessions.

### Sitting Management

- FR35: RAM Pathfinder generates planned sittings for **salaried JOHs** from their working patterns, **court / tribunal**, date, and work type.
- FR36: Authorised users can filter sitting records by Region/Office, **JOH type**, **JOH**, and date range.
- FR37: Authorised users can confirm that a sitting actually took place, updating outcome (confirmed, cancelled, rejected) and actual work type.
- FR38: Authorised users can split a sitting into AM/PM with different work types within a single day.
- FR39: Authorised users can create ad-hoc sittings for **salaried JOHs**, including DJ(MC)s and Legal Advisers in County Courts (Courts-cohort-specific examples).
- FR40: Verifiers can verify confirmed sittings; once verified, the data is read-only. Amendments after verification require **re-opening** via a UI re-open action gated by a distinct authorised role — different from the original confirmer (SIT-NFR-02) and from a standard Verifier (at MVP, the permission is granted to RSU Admin only). The action captures a mandatory justification field and is fully audited. No external Request-for-Change ticketing — re-open is a first-class UI action with RBAC controls.

### Payment & Reconciliation

- FR41: Authorised users can list confirmed bookings and salaried sittings, filterable by Region/Office, judge, date range, and payment lifecycle status (pending, requested, paid, reconciled).
- FR42: RAM Pathfinder's payment-processing batch (`ram-payment-batch`, scheduled cron — typically end-of-week) automatically marks eligible bookings as *payment requested* and creates the corresponding `ram_payments` + `ram_payment_schedules` records via SQL JOIN; no user click required.
- FR43: The payment batch generates JFEPS-compatible payment schedules and dispatches them as Excel attachments to a configured Payment Authoriser via email (using its service-principal identity to call the Notification API).
- FR44: RAM Pathfinder exposes the payment schedule via API with content-type negotiation (`application/vnd.hmcts.jfeps+json` or `+xlsx`); the JFEPS shape evolves independently of Payment internals. Preserved for SSCS wave 1[^d11].
- FR45: RAM Pathfinder prevents double submission of the same booking for payment via natural-key unique constraint on `(payment_cycle_id, booking_id)`; re-runs of the same cycle are idempotent.
- FR46: Authorised users (Finance, RSU) can flag payments as reconciled, capturing notes for mismatches; once fully reconciled, a payment cannot be re-requested.
- FR47: RAM Pathfinder does not store or expose bank details for any JOH — those remain in the finance system.

### Itineraries & Reporting (Read Models)

- FR48: Authorised users can render the Court Itinerary (monthly or annual) for a given Office, Financial Year, and Month, showing sittings, bookings, vacancies, and NTBF absences for each day.
- FR49: Authorised users can render the Judge Itinerary for one or more judges over a date range, scoped by Authorisation (judges see only their own; courts see their office; RSU sees their region).
- FR50: Authorised users can use the Forward Look view across a Region with paged or filtered access for performance.
- FR51: Itinerary cells are clickable and drill into the underlying record (Sitting, Absence, Vacancy, or Booking).
- FR52: Authorised users can copy/export Itinerary and Report contents to Excel and PDF.
- FR53: RAM Pathfinder provides a fixed catalogue of standard Reports (weekly sitting projections, weekly vacancies, absence analysis, vacancy by court, confirmed sittings/bookings by judge or judge type, judge utilisation, jurisdictional split, summary by court / work type) with parameter filters per report.
- FR54: RAM Pathfinder exposes aggregated MI Feed APIs for external consumers (DA&I, future programmes); MI Feed responses contain no case-level data and are aggregate-only by contract.

### Platform Operations

*(There is no data-migration FR[^d3].)*

- FR55: Authenticated users land on a Home page showing role-scoped navigation, Region/Area selector, summary tiles for the selected scope, and contextual help.
- FR56[^d10]: RAM Pathfinder's **business-user UI** (`ram-ui`) replicates the functional surface of the as-is APEX UI on a modern UI stack and meets WCAG 2.2 Level AA. MVP: `ram-ui` only; `ram-admin-ui` post-MVP.
- FR57: RAM Pathfinder supports **per-jurisdiction, per-region phased activation** — activation is a flag flip on `ram_auth_user_activation_flags` keyed by the (jurisdiction, region) tuple, not a data migration. Initial flag state FALSE for every user record at bootstrap (mechanism outside PRD scope[^d9]); cutover flips per wave by a DBA running `UPDATE ram_auth_user_activation_flags SET activated = TRUE WHERE jurisdiction = '…' AND region = '…'` per the rollout runbook (no UI in MVP).
- FR58: Every RAM Pathfinder service exposes a versioned API contract, RFC 9457 problem-details for errors, and a published OpenAPI specification. Deprecation signalling uses `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) headers.
- FR59: Every RAM Pathfinder service emits structured logs with correlation IDs and consistent error categorisation, retained for pilot incident triage.
- FR60[^d11][^d5]: Every RAM Pathfinder domain service has a manual UAT script verified by **jurisdiction-incumbent-experienced users** against that incumbent system before that wave's rollout: ListAssist-experienced users (RTJ, Tribunal Judges, Tribunal Members, Caseworkers, Finance, MI) for wave 1 (SSCS); APEX-experienced users (RSU, Court, Judge, Judges' Clerks, Finance, MI) for waves 2+ (Courts). Recorded with explicit per-role sign-off. No automated incumbent-comparison harness.

## Non-Functional Requirements

### Performance

- NFR1 — Static page load: ≤ 3 s for static UI loads (e.g. Home initial render).
- NFR2 — Dashboard refresh: ≤ 5 s when Region/Area selection changes.
- NFR3 — List / filter operations: ≤ 10 s for typical operational lists at Region scope.
- NFR4 — Batch / annual operations: ≤ 15 s (e.g. annual itinerary render, batch payment-request processing).
- NFR5 — Reports / Forward Look: ≤ 30 s for standard report parameters and for the Forward Look view at Region scope.
- NFR6 — Single-resource API read: ≤ 500 ms p95.
- NFR7 — Domain write API: ≤ 1 s p95 for typical write operations.
- NFR8 — Federated read (Itinerary, Forward Look): ≤ 30 s p95 under Strategy A (SQL JOIN over shared schema).
- NFR9 — Capacity: concurrent users per region ~50–100; national ~200–500 once all regions migrated.

### Security

- NFR10 — Transport encryption: Latest TLS only on every endpoint; HTTP-only endpoints rejected.
- NFR11 — Data-at-rest encryption: All personal data encrypted at rest.
- NFR12: Human users authenticated via HMCTS IdP SSO (per FR1). Inter-service authentication for user-initiated calls is JWT propagation, validated by `JWTFilter` against IdP JWKS. Batch / scheduled components use OAuth 2.0 `client_credentials` against `ram-mock-auth` in non-prod; production issuer is deferred per gaps.md G7.1. *(The eLinks sync and MRD pick-up need no service identity — they run in-process inside `ram-reference-data` writing its own tables.)*
- NFR13 — Authorisation enforcement: Every API call resolves principal's roles + jurisdiction + Region/Area scope through the Authorisation service; no operation bypasses this check.
- NFR14 — Forbidden data scope: No bank details stored or exposed (PAY-NFR-05). No case-level data in any read model or report (REP-BR-NFR-03).
- NFR15 — Government Functional Standard 7 alignment: protective marking, access control, secure development practices.
- NFR16 — Secret management: Service credentials, signing keys, integration secrets (incl. the JOH eLinks API credential) in Azure Key Vault; never in source control or env-baked images.

### Accessibility

- NFR17 — WCAG 2.2 Level AA: Every UI page meets WCAG 2.2 Level AA; tested per UI page in each domain phase before that phase's gate is passed.
- NFR18 — Assistive technology compatibility: Keyboard navigation, ARIA labels, screen-reader compatibility per HMCTS accessibility standards.
- NFR19 — Public Sector Bodies Accessibility Regulations 2018: compliance including publication of an accessibility statement.

### Integration

- NFR20 — HMCTS IdP integration: Hard Phase 0 dependency. RAM Pathfinder integrates with whichever AuthN protocol the HMCTS IdP exposes (OIDC or SAML).
- NFR21[^d11] — JFEPS / Liberata unchanged: Payment schedule format (JFEPS-compatible Excel), email-to-Authoriser delivery, authoriser-forwards-to-Liberata preserved exactly as in APEX, **and preserved for SSCS in wave 1**. No format change for finance across either cohort.
- NFR22 — HMCTS email infrastructure: Outbound transactional emails dispatch via HMCTS email; overnight batch acceptable for booking acks.
- NFR23 — DA&I MI Feed: Aggregate-only REST API contract; no case-level data under any consumer authorisation.
- NFR24[^d11] — **JOH eLinks API + MRD integration (MVP scope)**: JOH eLinks API is an MVP integration — the canonical source for judicial-holder reference data[^d3]. MRD data is ingested via a weekly Excel feed pending availability of MRD's public APIs. Manual data entry by RSU is no longer the operating model for these sources; corrections happen at source. Other HR systems beyond JOH eLinks / MRD remain out of MVP scope.

### Observability (MVP minimum)

- NFR25 — Structured logging: Every service emits structured logs with consistent fields, correlation IDs threaded through service-to-service calls, defined error-categorisation taxonomy.[^d7]
- NFR26 — Log retention: Logs retained sufficient for pilot incident triage; specific period set in Phase 0 within HMCTS data-retention policy.
- NFR27 — Log ingestion: Logs ingested into Azure-native logging (Application Insights / Log Analytics).
- NFR28 — Health and readiness probes: Every service exposes Kubernetes-compatible liveness/readiness endpoints (Spring Actuator).
- NFR29 — Roadmap commitments (post-MVP, not MVP): Structured user-action auditing[^d7]. Metrics and trace observability beyond logs is post-MVP.

### Data Privacy & Sovereignty

- NFR30 — UK GDPR / DPA 2018 compliance: Personal data scope limited to user/JOH identity, contact details, payroll numbers, operational metadata. No case-level data anywhere.
- NFR31 — Data residency: All RAM Pathfinder services and data hosted in Azure UK regions only.
- NFR32[^d3] — Retention: Per HMCTS retention schedules. Historical transactional data stays in the cohort's incumbent system (ListAssist for SSCS; APEX for Courts) and is accessed there as needed — no legacy data is migrated into RAM.
- NFR33 — FOI scope: Aggregate operational data exposable per FOI; case-level data forbidden by contract.

### Reliability & Availability

- NFR34 — Operational availability: Available during HMCTS operational hours (typically 07:00–19:00 UK weekdays).
- NFR35 — Payment-cycle continuity: Zero failed JFEPS payment cycles attributable to RAM Pathfinder. Manual handling is operational contingency, not normal-mode expectation.
- NFR36 — Per-wave rollback: Each rollout wave has a documented rollback path within one operational cycle if the wave's gate is breached post-cutover.
- NFR37 — Strategy A degraded-mode contract: If federated read latency breaches NFR8, RAM Pathfinder degrades to Strategy C cached projection.
- NFR38[^d8][^d11] — Rollout-wave isolation: Wave activation targeting one (jurisdiction, region) does not affect users in other waves. Enforcement via per-user `ram_auth_user_activation_flags` carrying the (jurisdiction, region) tuple (FR57). Production runs in a single Azure region (UK South) with multi-AZ HA. DR scope is an open gap per gaps.md G3.6.

### Maintainability

- NFR39 — API-as-Product standards: Versioned contracts, RFC 9457 problem-details, OpenAPI per service. Deprecation via RFC 9745 + RFC 8594.
- NFR40 — Per-service deployment unit: Each of the 11 services is independently deployable on Kubernetes; rolling updates per service per wave without coupling.
- NFR41[^d11][^d5] — Behavioural-parity UAT suite: Every domain service has a manual UAT script (per FR60). Jurisdiction-incumbent-experienced users walk the script comparing RAM Pathfinder vs the incumbent (ListAssist for wave 1; APEX for waves 2+); sign-off per role per wave is the wave gate. No automated parity test suite — automated CI is unit, integration (Testcontainers), and contract tests only.
- NFR42 — Postman collections: Each phase produces a Postman collection that exercises the phase's endpoints; versioned alongside the services.

## Additional Requirements

**(Derived from Architecture v3.0 — these are technical / platform requirements that materially impact Epic and Story shape, particularly each epic's scaffolding story.)**

### Repository strategy

- AR1 *(admin repo post-MVP[^d10])* — Polyrepo: **15 repositories** total — 11 production service repos + `ram-ui` (business-user-facing SPA, MVP) + `ram-admin-ui` (admin-facing SPA, **post-MVP repo[^d10]**) + `ram-architecture` + `ram-mock-auth`. Each repo has its own CI pipeline, CODEOWNERS, branch protection, and review policy. No monorepo, no Gradle root project. The two UI repos use the same stack and conventions but never share runtime code.

### Starter template (Story 1 of every service epic)

- AR2[^d10] — Each RAM Pathfinder backend service is scaffolded from the **HMCTS Crime SpringBoot template** (`https://github.com/hmcts/service-hmcts-crime-springboot-template`, default branch `main`) cloned via the `ram-scaffold.sh` script in `ram-architecture/scaffolding/`. The scaffolding script applies RAM Pathfinder conventions on top of the starter and is used at service-creation time only. **The `gh` CLI is NOT available in the engineering environment** — `ram-scaffold.sh` handles only local scaffolding + `git push` to a pre-created remote; all GitHub admin operations are performed manually via the GitHub web UI per AR51.
- AR3 — Group ID `uk.gov.hmcts.ram`; artefact `ram-{service-name}`; package `uk.gov.hmcts.ram.{service-name}`. Default port 8082.
- AR4 — Initial commit for every new service is *"Scaffold RAM Pathfinder {service-name} from HMCTS starter"* — this is the first implementation story per service.

### Locked technology stack (carried from PRD; enumerated here as architecture-confirmed dependency versions)

- AR5 — Java 25 (LTS), Spring Boot 4.1.x, Gradle Groovy DSL with Gradle Wrapper, Spring Boot Gradle plugin 4.1.0, `io.spring.dependency-management:1.1.7`.
- AR6 — Lombok 1.18.46, MapStruct 1.6.3 for boilerplate reduction and DTO ↔ entity mapping.
- AR7 — `io.jsonwebtoken:jjwt:0.13.0` for JWT validation in custom `JWTFilter`; `org.owasp.encoder:encoder:1.4.0` for XSS-safe output encoding.
- AR8 — `springdoc-openapi` (Swagger Core) for OpenAPI 3.x generation. Per-service OpenAPI spec published by Gradle (via the `maven-publish` plugin) as a Maven-format artefact `uk.gov.hmcts.ram:api-ram-{service}:{version}`.

### Build / supply-chain tooling (per HMCTS Crime template)

- AR9 — JaCoCo for code coverage reports.
- AR10 — `org.cyclonedx.bom:3.2.4` for SBOM (Software Bill of Materials) — supply-chain security.
- AR11 — `com.gorylenko.gradle-git-properties:4.0.1` to embed Git metadata in `/actuator/info`.
- AR12 — `com.github.ben-manes.versions:0.54.0` for dependency-update reports.
- AR13 — `com.avast.gradle.docker-compose:0.17.21` for local development with docker-compose-managed dependencies.

### Testing framework (per HMCTS Crime template)

- AR14 — Spring Boot Test (JUnit 5 via `junit-bom:6.0.3`), `spring-boot-testcontainers:4.1.0`, `testcontainers-postgresql:1.21.4`, `testcontainers-junit-jupiter:1.21.4` for integration tests with real PostgreSQL. AssertJ for assertions (transitive). *(Not in the template baseline — added by the scaffolding script; see AR-scaffold note below / G1.4.)*
- AR15 — `spring-boot-starter-webmvc-test` for controller-layer testing.
- AR16 — Pact (or equivalent) for consumer-driven contract tests under `src/test/java/.../contract/` — added per service (not in HMCTS template baseline).
- AR17 — Spectral for OpenAPI lint in CI; ArchUnit for architectural fitness functions (table ownership, layer rules); Spotless + Checkstyle for code style.

### Data architecture

- AR18 — One global PostgreSQL 17 instance, **single shared schema**. Per-service DB roles with explicit grants. Table ownership encoded in table name (entity-plural for primary tables; `jo_`/`mrd_` source-system prefix for upstream-sourced tier-(a) tables; service-prefix for service-internal) and enforced by ArchUnit fitness functions in CI.
- AR19 — **Liquibase** per-service for DDL (each service owns the creation of its tables, columns, indexes, grants): changelogs under `src/main/resources/db/changelog/`, master `db.changelog-master.yaml`, formatted-SQL changesets named `NNN-description.sql`. Liquibase **baseline changelog** in `ram-architecture` owns the shared `ram_configuration_values` table.
- AR20 — **55 RAM Pathfinder tables** total grouped by owning service: 32 Reference Data tables (15 `jo_*` + `mrd_specialisms` + `ram_sync_status` + 15 RAM-owned) + 6 Authorisation tables (incl. `ram_auth_staff_identities`) + 5 JOH operational-state tables + domain tables + 1 shared infra + 2 dev-only. See `architecture/data-tables.md` for the authoritative ownership mapping, including the two-tier reference-data model.
- AR21 — Retry safety uses native DB primitives: natural-key unique constraints, optimistic locking (`@Version`), pessimistic row locking. No custom idempotency-key tables. Tier-(a) tables are exempt (single writer: the ingestion mechanism; upserts key on the upstream natural key).
- AR22 — Cross-service read patterns: direct SQL on Reference Data (no client class); Itinerary and MI Feed use SQL JOINs over the shared schema (no API fan-out, no cache). Domain tables reference JOHs by `joh_id` → `ram_joh_identities`.

### Infrastructure / deployment

- AR23 — Kubernetes on Azure AKS, production in UK South, multi-AZ HA. Container images → Azure Container Registry. Each of the 11 services is a containerised Spring Boot app. The AKS/ACR estate is Terraform-provisioned per AR53 (revised — provisioned in `ram-shared-infrastructure`, Epic 0.0).
- AR24 — Helm chart per service with `values-{env}.yaml` overlay per environment (`dev`, `staging`, `production`). Production values include `topologySpreadConstraints` for AZ spread, min replicas, multi-AZ node pool selection. Helm chart is **not** in HMCTS template baseline — added by `ram-scaffold.sh` per G1.4a.
- AR25 — Secrets in Azure Key Vault (via Spring Cloud Azure); no secrets in source control or env-baked images. Each service's Key Vault namespace is Terraform-provisioned in that service's repo (AR53).
- AR26 — Per-environment configuration via Spring profiles + `application-{env}.yml`; cross-service runtime policy values in the shared `ram_configuration_values` table (read-only via direct SQL).
- AR27 — Azure API Management (APIM) at the edge for rate limits, header injection, deprecation/`Sunset` policies, and ops-restricting `/actuator/*` namespace. APIM instance + base policies Terraform-provisioned in `ram-shared-infrastructure` (Epic 0.0); per-API policy additions in each service's `terraform/` (AR53 revised).

### CI / CD pipeline (per service)

- AR28 — GitHub Actions workflows in `.github/workflows/`: `ci.yml` (build + test + lint + ArchUnit + Spectral + Helm lint), `deploy-dev.yml` (auto on PR merge to main), `deploy-staging.yml` (manual approval), `deploy-production.yml` (per-wave gated, manual UAT sign-off as gate).
- AR29 — `PULL_REQUEST_TEMPLATE.md` includes patterns checklist; `CODEOWNERS` defines RAM Pathfinder team + service-specific reviewers.

### Observability (MVP)

- AR30 — Logstash Logback Encoder (`net.logstash.logback:logstash-logback-encoder:9.0`) for structured JSON logs with async appender. Logback config in `src/main/resources/logback-spring.xml`.[^d7]
- AR31 — OpenTelemetry (`spring-boot-starter-opentelemetry`) for traces; OTel Collector → Azure Application Insights as the export target. Instrumentation key configured via env var `APPINSIGHTS_INSTRUMENTATIONKEY`.
- AR32 — `CorrelationIdFilter` at request entry; correlation ID propagated in service-to-service HTTP client calls and threaded through MDC into log statements.
- AR33 — Spring Boot Actuator endpoints exposed: `/actuator/health`, `/actuator/info`, `/actuator/readiness`. `/actuator/metrics` and Prometheus endpoint **not exposed at MVP**[^d7]. `/actuator/*` namespace ops-restricted at the APIM layer.

### Security implementation

- AR34 — Custom `JWTFilter` in `config/JWTFilter.java` validates JWTs against the IdP's JWKS endpoint (mock-auth for Phase 0–8; HMCTS IdP from pre-Phase-9 cutover). On each request, calls `ram-authorisation` `POST /authz/check`, which resolves the IdP email to the **canonical RAM identifier**[^d9] — the RAM JOH UUID via `jo_people` → `personnel_number` → `ram_joh_identities` for JOH users, or the RAM-assigned staff UUID via `ram_auth_staff_identities` for HMCTS admin staff — then returns roles + **jurisdiction** + Region/Area scope + activation flag (FR57); populates request-scoped `AuthDetails` bean. Unresolvable principals are rejected with an RFC 9457 authorisation problem.
- AR35 — `ram-mock-auth` is the OIDC issuer for dev/CI/integration: issues human-user JWTs via `authorization_code` and service tokens via `client_credentials` for batch components. Test-user roster spans **both identity populations** (JOH users resolvable against seeded `jo_people` rows; admin-staff users resolvable against seeded `ram_auth_staff_identities` rows). Refuses to start with `production` profile (per gaps.md G5.3). **Never deployed to production.**
- AR36 — Batch / scheduled component authentication: `ram-payment-batch` authenticates via OAuth 2.0 `client_credentials` to obtain a service-principal token; uses that token to call `ram-notification`. Production issuer for service tokens is a deferred decision per gaps.md G7.1 (default recommendation: Azure Workload Identity given AKS deployment).
- AR37 — Boilerplate `@ControllerAdvice` (`GlobalExceptionHandler.java`) emitting RFC 9457 problem-details with `ProblemDetailFactory`. Domain exceptions: `{Resource}NotFoundException`, `BusinessRuleViolation`, `DependencyException`.

### API surface / standards

- AR38 — Versioning via URI path prefix (e.g. `/v1/johs`, `/v2/johs`) for major versions; backwards-compatible additions don't require a new path. Versioning policy itself is a Phase 0 deliverable[^d1].
- AR39 — Deprecation signalling: `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) response headers; injected at APIM layer per AR27.
- AR40 — Versioned content-type for Payment: `application/vnd.hmcts.jfeps+json` (canonical) or `application/vnd.hmcts.jfeps+xlsx` (Excel for Liberata workflow). JFEPS shape evolves independently of Payment internals.
- AR41 — Postman collections per phase under `postman/` in each service repo, named `ram-{service}-phase{N}.postman_collection.json`. Each phase produces a collection that exercises the phase's endpoints (per NFR42); also serves as executable API documentation pre-UI demo.

### UI stack (architecture decisions on top of PRD D4)

- AR42 — **Two UI repos**, same stack, separated by audience: `ram-ui` (business-user-facing SPA, **MVP**) and `ram-admin-ui` (admin-facing SPA, **post-MVP[^d10]**). Stack for both: React + TypeScript + Vite + Vitest (unit) + Playwright (E2E). `ram-ui` carries per-domain operational modules under `src/modules/{domain}/` (JOH, Absence, Vacancy, Booking, Sitting, Payment, Itinerary, Reports). `ram-admin-ui` (when built post-MVP) carries `reference-data/` (FR6 tier (b)) and `users-roles/` (FR4) modules plus reserved hooks for `activation/` (FR57 admin) and `audit/` (D7 post-MVP). TanStack Query for HTTP. GOV.UK Design System base styling with HMCTS / RAM Pathfinder extensions.
- AR43 — Auto-generated TypeScript clients per service from per-service OpenAPI specs (regenerated in CI). Clients live under `src/modules/{domain}/api/` and `api-clients/{service}-client/`. Each UI repo regenerates its own clients independently — no shared client package.
- AR44 — `HmctsIdpProvider.tsx` (OIDC client wrapper) + `ProtectedRoute.tsx` + `useAuth.ts` hook in `src/shared/auth/`. HTTP client (`src/shared/api/httpClient.ts`) attaches auth header; `errorHandling.ts` translates RFC 9457 problem-details into UI display.
- AR45 — E2E test suites: `ram-ui` has one Playwright suite per backend phase under `tests/e2e/phase-{N}-{domain}.spec.ts`. axe-core accessibility checks in `ci.yml`.
- AR45b — **Independent deployment for the two UI repos**: separate Azure Static Web Apps (or CDN) deployments, distinct hostnames. Both share the same backend services, same SSO, same Authorisation service.

### Upstream reference-data ingestion

- AR46 — **JOH eLinks sync**: an in-process `@Scheduled` task inside `ram-reference-data` pulls the JOH eLinks API **nightly** and full-refresh-upserts the 15 `jo_*` tables. Upserts key on the upstream natural key (`personnel_number` for `jo_people`); for every `jo_people` row the sync also mints, if absent, a `ram_joh_identities` row (a stable RAM JOH UUID keyed to `personnel_number`); rows absent upstream are **marked inactive, never hard-deleted** (protects FKs from domain tables), and `ram_joh_identities` rows are never deleted. No new service principal and no new deployable — the task writes the service's own tables in-process; the only credential is the outbound JOH eLinks API credential in Key Vault.
- AR47 — **MRD ingestion**: the MRD team's weekly Excel feed lands in a dedicated Azure Blob container; a `@Scheduled` task in `ram-reference-data` polls the container, validates the workbook (shape, vocabulary, referential checks), upserts the `mrd_*` tables, and archives the file (retained for lineage/audit). Idempotent per file. The blob-drop seam swaps cleanly for direct MRD API integration when MRD's public APIs ship.
- AR48 — **Sync tracking + failure handling**: ingestion runs, outcomes, and row counts are recorded in `ram_sync_status`. A failed sync leaves the previous good state in place (transactional per entity set); failures surface via structured logs + `ram_sync_status` for ops triage. Reference data is at most one cycle stale, never partially written. The wave-gate "reference data current" check reads `ram_sync_status`.
- AR49 — **Tier-(a) write protection**: only the `ram_reference_data` DB role holds INSERT/UPDATE on `jo_*`/`mrd_*` tables; every other role gets at most SELECT — the DB enforces "read-only in RAM" (FR6 tier (a)). Enforced by the ArchUnit/grants fitness function.

### Manual UAT (FR60 / NFR41)

- AR50 — Per-service manual UAT scripts live under `docs/uat/` in each domain service repo (markdown walkthroughs for jurisdiction-incumbent-experienced users to follow side-by-side against the incumbent — ListAssist for wave 1; APEX for waves 2+). Not part of automated CI. Sign-off (per role per wave) is the wave-cutover gate.

### Manual GitHub setup

- AR51 — The `gh` CLI is **not** available in the engineering environment. All GitHub admin operations (repo creation, branch protection, team / `CODEOWNERS` access, PR merges) happen **manually via the GitHub web UI** per the runbook at `ram-architecture/runbooks/github-setup.md`. The `ram-scaffold.sh` script (AR2) operates only locally and via plain `git` push to a remote the engineer has already created in the web UI. This is a non-negotiable constraint of the engineering environment.[^d10]

### Infrastructure provisioning (HMCTS standard)

- AR53 — **(revised 2026-07-06)** **All Azure infrastructure is provisioned via Terraform** (HMCTS standard) — no Bicep, no portal click-ops. **Product-level *shared* infrastructure lives in its own dedicated repository, `ram-shared-infrastructure`**, per the HMCTS Cloud Native Platform `{product}-shared-infrastructure` standard. This **supersedes the prior "colocated first-consumer" rule** (SCP 2026-06-17): the shared estate is no longer carried inside `ram-reference-data`. Allocation under the revised rule:
  - **`ram-shared-infrastructure`** carries the **shared estate**: AKS cluster + node pools, PostgreSQL Flexible Server, Azure Container Registry, APIM instance + base policies, Application Insights / Log Analytics workspace (incl. retention settings), Key Vault — provisioned and **independently verified in Epic 0.0**, ahead of any service.
  - **Each service repo** carries Terraform for its **own resources only**: its Key Vault namespace/secrets, service-specific storage, APIM per-API policy additions.
  - **`ram-reference-data`** carries the MRD feed storage account + blob container (Epic 0.1 Story 0.1.4 — its own resource).
  - **`ram-ui`** carries its Azure Static Web App.
  - Terraform lives under `terraform/` with per-environment stacks (`dev` / `staging` / `production`) in **`ram-shared-infrastructure`** (shared estate) and in each service repo (own resources); `ram-scaffold.sh` adds the per-service `terraform/` skeleton alongside the Helm chart (same pattern as G1.4a).
  - **Helm remains the application-deployment mechanism** onto the shared AKS cluster provisioned in Epic 0.0 — Terraform provisions the estate; Helm deploys workloads onto it; Liquibase owns DB schema. The three do not overlap.
  - Terraform state backend and plan/apply pipeline arrangement are HMCTS-side details to confirm — gaps.md G9.

### Identity bootstrap + verification

- AR52 — User and authorisation records (`auth_*` tables incl. `ram_auth_staff_identities`) are **strictly RAM-internal**, populated by programme-management / operational mechanisms outside the PRD's scope — no external authority provides this data and no legacy system seeds it. RAM provides: (a) dev/CI seed scripts spanning both identity populations; (b) a **bootstrap-verification job** that confirms every bootstrapped user (both populations) maps to a real IdP principal — run before each wave's cutover and at the pre-Phase-9 IdP cutover (G1.3); (c) the production bootstrap runbook.[^d9]

## UX Design Requirements

**(Not applicable — no UX design document was produced. UI requirements inherit directly from PRD FR55, FR56 and architecture decisions AR42–AR45b. The 2026-05-06 readiness report documents this as an accepted gap.)**

[^d1]: D1 — Phase 0 Foundations scope: Reference Data, Authorisation (SSO), Notification, API contracts, deployment platform, structured logging.
[^d3]: Revised D3 (2026-06-10) — no data migration from any legacy system; judicial-holder reference data is ingested from the JOH eLinks API and MRD.
[^d5]: D5 — the jurisdiction's incumbent system is the behavioural reference, verified by manual UAT.
[^d7]: D7 — MVP observability is log-based; user-action audit is post-MVP.
[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d9]: Restructured D9 (2026-06-10; refined 2026-07-09 per SCP) — two user populations. JOHs resolve IdP email → `jo_people` → `personnel_number` → a **RAM-assigned JOH UUID** (`ram_joh_identities`); HMCTS admin staff via a RAM-internal identity table. Both key on a RAM-assigned UUID; `personnel_number` is the upstream link only. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
[^d11]: D11 (2026-06-10, amended 2026-06-18) — SSCS-first pilot: wave 1 replaces **ListAssist** (the SSCS judicial-scheduling tool); **GAPS (SSCS case management) is retained, not replaced**; waves 2+ replace JI/APEX per Courts region.
[^d12]: D12 (2026-06-10) — RAM is the system of record for JOH availability and scheduling only; case and hearing management live in external systems.
