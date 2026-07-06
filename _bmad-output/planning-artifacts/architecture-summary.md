---
type: 'Architecture Summary'
resource: 'architecture-summary.html'
tags: [ram-pathfinder, architecture, sscs]
timestamp: '2026-06-11'
title: RAM Pathfinder Architecture Summary
description: Target-state reference for RAM Pathfinder. What is built and how it runs.
last_updated: 2026-06-11
amended_in: architecture.md v3.0 — Sprint Change Proposal 2026-06-10 cascade
---

# RAM Pathfinder Architecture Summary

RAM Pathfinder — HMCTS's API-driven greenfield platform for judicial (JOH) availability and scheduling. It replaces **ListAssist** (the SSCS judicial-scheduling tool) in the SSCS Tribunals jurisdiction in wave 1 (GAPS, the SSCS case-management system, is retained) and the as-is **JI application (Oracle APEX)** in the Courts jurisdictions in waves 2+[^d11]. Scope boundary[^d12]: RAM is the **system of record for JOH availability and scheduling** — case management, panel composition, and hearing types live in external systems that consume RAM's APIs; no external system writes into RAM.

This file describes what is built and how it runs. For rationale, alternatives, gap and assumption registers, data-table inventory, conventions, repo structure, changelog, and build sequence, see [`./architecture.md`](./architecture.md) and the siblings under [`./architecture/`](./architecture/).

## System context

![RAM Pathfinder System Context — high-level service map and key interactions](./architecture/diagrams/system-context.png)

## Service decomposition (11 services + UI)

### Domain services

| Service | Responsibility |
|---|---|
| `ram-joh` | JOH operational state — working patterns, ticket/location overlays, jurisdictional split (renamed from `ram-judge`[^d11]; the canonical JOH person record is `jo_people`, owned by Reference Data) |
| `ram-absence` | Absence records + approval workflow; triggers vacancy creation |
| `ram-vacancy` | Cover-required vacancies; `filled` flag UPDATE-granted to Booking |
| `ram-booking` | Fee-paid bookings + verification; row-locks target vacancy in-transaction |
| `ram-sitting` | Salaried-JOH sittings; verification; AM/PM split |
| `ram-payment` | Payments + reconciliation; JFEPS-shaped Excel schedule via Notification |

### Cross-cutting services

| Service | Responsibility |
|---|---|
| `ram-authorisation` | Per-request authz authority; **two-population identity resolution** (JOH via `jo_people` → personnel number; admin staff via `ram_auth_staff_identities` → RAM-assigned UUID); roles, **jurisdiction**, Region/Area scope, (jurisdiction, region) activation flags |
| `ram-reference-data` | Facade over the two-tier reference datastore — tier (a) upstream-sourced `jo_*` (JOH eLinks, nightly in-process sync) + `mrd_*` (MRD weekly Excel via blob drop), read-only in RAM; tier (b) RAM-owned regions/offices/calendar/vocabularies. Read directly via SQL by other services; jurisdiction-filtered API |
| `ram-notification` | Outbound transactional email (booking / absence acks; JFEPS schedule emails) |

### Read-model services

| Service | Responsibility |
|---|---|
| `ram-itinerary` | Court + Judge itinerary; Forward Look; SQL JOINs over the shared schema (no own tables) |
| `ram-mi-feed` | Aggregate reports; DA&I consumer feed (post-MVP); SQL JOINs over the shared schema (no own tables); aggregate-only — no case-level data |

### Frontend

| Component | Description |
|---|---|
| `ram-ui` | Business SPA (MVP); per-domain modules; GOV.UK Design System; WCAG 2.2 AA; HMCTS IdP SSO. (`ram-admin-ui` is post-MVP[^d10] — MVP admin operations are DBA-via-SQL per runbook.) |

### Non-production support

| Component | Description |
|---|---|
| `ram-mock-auth` | OIDC issuer for dev / CI / integration environments only — **never deployed to production** |

## Technology stack

| Layer | Choice |
|---|---|
| Language & runtime | Java 25 (LTS) + Spring Boot 4.0.6 |
| Build | Gradle (Groovy DSL); HMCTS Crime SpringBoot template as scaffold |
| Database | PostgreSQL 17 on Azure Database for PostgreSQL Flexible Server (single global instance; single shared schema; zone-redundant HA in UK South) |
| Schema evolution | Liquibase (RAM Pathfinder DDL only) |
| Container orchestration | Azure Kubernetes Service — single production cluster in UK South with multi-AZ node pools |
| Ingress | Azure API Management — Premium SKU, zone-redundant |
| Identity provider | HMCTS IdP via OIDC `authorization_code` (production, human users only); `ram-mock-auth` in dev / CI / integration; JWKS endpoint provides JWT-signature public keys to every RAM Pathfinder service |
| Service-to-service auth | **User-initiated**: JWT propagation via `RestClient` interceptor (forward inbound user JWT). **Batch / scheduled** (payment batch only at MVP): OAuth `client_credentials` against `ram-mock-auth`; production issuer per G7.1 (default recommendation: Azure Workload Identity). |
| Per-request auth | Custom `JWTFilter` (HMCTS Crime template pattern, `io.jsonwebtoken:jjwt`) — validates JWT signature against IdP JWKS, then calls `ram-authorisation` for authz |
| Secrets | Azure Key Vault (zone-redundant) |
| Observability | Logback + Logstash JSON encoder → OpenTelemetry → Azure Application Insights / Log Analytics |
| Frontend stack | React + TypeScript + Vite + GOV.UK Design System |
| Static hosting | Azure Static Web Apps |

## Data tier

- One PostgreSQL Flexible Server instance in UK South. One shared schema. Zone-redundant HA (primary + standby in different AZs; synchronous replication; automatic failover <60 s).
- 55 tables: 52 service-owned production + 1 shared infrastructure (`ram_configuration_values`) + 2 dev-only (mock-auth).
- **Two-tier reference data (FR6/FR7):** tier (a) upstream-sourced `jo_*`/`mrd_*` tables — written only by the ingestion mechanisms, never hand-edited, corrections at source; tier (b) RAM-owned tables — maintained in RAM. Separate tables preserve lineage.
- Domain tables reference JOHs by `personnel_number` → `jo_people` (the canonical JOH identifier). The sync never hard-deletes `jo_people` rows, so FK targets are stable.
- Per-service DB roles (`ram_joh`, `ram_booking`, `ram_payment`, …) with explicit grants. A service has `ALL` on its own tables; only the specific grants it needs on others. Only `ram_reference_data` holds INSERT/UPDATE on tier-(a) tables.
- **Cross-service reads** — direct SQL JOIN using SELECT grants. No caching at MVP.
- **Cross-service simple writes** — direct UPDATE on UPDATE-granted columns within the writer's transaction (e.g. Booking writes `ram_vacancies.filled`).
- **Cross-service workflows** — REST API call to the owning service.
- **Read models** — SQL JOIN over the shared schema. No API fan-out.

Full per-table inventory: [`./architecture/data-tables.md`](./architecture/data-tables.md).

## Authentication & Authorisation

Most runtime requests are user-initiated. The one exception is the payment-processing batch (`ram-payment-batch`), which runs on a schedule and authenticates as a service principal.

The auth flow:

1. User authenticates at HMCTS IdP (SSO). IdP issues a JWT.
2. User calls `ram-ui` with the JWT; UI forwards the bearer token through APIM to the target service.
3. The service's `JWTFilter` validates the JWT against HMCTS IdP's JWKS, then calls `ram-authorisation` for authz scope.
4. Cross-service calls forward the user's JWT — the upstream service copies the inbound `Authorization` header onto outbound calls. The downstream `JWTFilter` validates the same JWT.

Details:

- **End-user authentication** — HMCTS IdP, OIDC `authorization_code`. SSO. JWT issued. `ram-mock-auth` (Spring Authorization Server) is the OIDC issuer in non-production. Mock-to-real cutover is a Spring profile change (issuer-url + JWKS URL flip; no code change).
- **JWT signature validation** — each service's `JWTFilter` (HMCTS Crime template, `io.jsonwebtoken:jjwt`) validates signature and issuer using the IdP's JWKS endpoint (`/oauth2/jwks` on mock; HMCTS IdP's JWKS URL in production). Validation runs before any controller. Public keys cached per the issuer's cache headers.
- **End-user authorisation** — after JWT validation, `JWTFilter` calls `POST /authz/check` against `ram-authorisation`. Authorisation resolves the IdP email to the canonical RAM identifier[^d9] — **personnel number** via `jo_people` for JOH users, or the **RAM-assigned staff UUID** via `ram_auth_staff_identities` for HMCTS admin staff — then returns roles + **jurisdiction** + Region/Area scope + activation flag (FR57). Both populations share the same authorisation model. Result stored in a request-scoped `AuthDetails` bean.
- **JWT propagation (user-initiated cross-service calls)** — the `RestClient` interceptor copies the inbound `Authorization: Bearer <user-jwt>` header onto outbound calls. The downstream `JWTFilter` validates the same JWT.
- **Service-principal auth (batch)** — the payment batch authenticates against `ram-mock-auth` (non-prod) via OAuth `client_credentials`, then attaches the service JWT to outbound calls (e.g. Notification). Production issuer is deferred (default: Azure Workload Identity — `architecture/gaps.md` G7.1).
- **Identity bootstrap verification** — user/authorisation records are bootstrapped by mechanisms outside the PRD's scope (restructured D9 — no legacy user migration); before each wave's cutover, a verification pass confirms every bootstrapped user in both populations maps to a real IdP principal.

**MVP non-user-initiated flows:**

- Payment batch (`ram-payment-batch`) — scheduled (e.g. weekly), authenticates as a service principal, picks up confirmed bookings/sittings without payment records, generates the JFEPS Excel, dispatches via Notification → HMCTS Email → Payment Authoriser. Sequence: [`./architecture/sequence-diagrams/payment-batch-flow.md`](./architecture/sequence-diagrams/payment-batch-flow.md).

**Out of scope at MVP:**

- Other non-user-initiated flows (more scheduled jobs, async messaging, event bus) — would use the same service-principal pattern.
- DA&I post-MVP MI Feed integration — auth model TBD. See [`./architecture/gaps.md` G7.2](./architecture/gaps.md).
- Production service-auth issuer — `ram-mock-auth` covers Phase 0–8; deferred per G7.1.

## API patterns

| Pattern | Detail |
|---|---|
| Coordination | REST-first synchronous; no domain event stream, no message bus, no webhook fabric |
| Versioning | URI prefix major version (`/v1/…`); 6-month internal / 12-month external deprecation windows; `Deprecation` header per [RFC 9745](https://datatracker.ietf.org/doc/html/rfc9745); `Sunset` header per [RFC 8594](https://datatracker.ietf.org/doc/html/rfc8594) |
| Error envelope | [RFC 9457](https://datatracker.ietf.org/doc/html/rfc9457) `application/problem+json` (obsoletes RFC 7807; same content type and field shape) |
| OpenAPI | Generated via Swagger Core; published per-service as Maven artefacts (`uk.gov.hmcts.ram:api-ram-{service}:{version}`). The OpenAPI document is the API's contract surface. |
| Pagination | Cursor-based for large or chronological lists; offset-based for small filtered lists |
| Field naming | JSON fields `camelCase`; ISO 8601 dates / instants; UTC stored, UK local for display |
| Identifiers | UUID primary keys throughout |
| Idempotency / retry safety | Native DB primitives — natural-key uniqueness (→ `409 Conflict`), optimistic locking (→ `412 Precondition Failed`), pessimistic row locking for cross-row workflows. No custom idempotency-key tables. Detail in [`./architecture/data-tables.md`](./architecture/data-tables.md) and the Data Architecture section of [`./architecture.md`](./architecture.md). |

## Cross-service interaction patterns

| Pattern | Mechanism |
|---|---|
| User authentication | User → HMCTS IdP (SSO) → JWT issued |
| User request | User (with JWT) → `ram-ui` → APIM (rate limits, routing) → service |
| Per-request JWT validation | Each RAM Pathfinder service's `JWTFilter` validates the inbound JWT signature against **HMCTS IdP's JWKS endpoint** before any controller is invoked |
| Cross-service call (within a user request) | Upstream service's outbound `RestClient` interceptor copies the inbound `Authorization: Bearer <user-jwt>` header to the downstream call; downstream service's `JWTFilter` validates the same user JWT (token propagation / forwarding pattern). No separate service identity. |
| Batch / scheduled flow (no user context) | Batch component (e.g. `ram-payment-batch`) authenticates as a service principal via OAuth `client_credentials` against the OIDC issuer (`ram-mock-auth` non-prod); attaches the resulting service JWT to outbound calls (Notification, etc.); receiving services validate via the same JWKS path. **MVP scope: payment batch only.** |
| Per-request authz | After JWT validation, the same `JWTFilter` calls `POST /authz/check` against `ram-authorisation` |
| Reference Data reads | Direct SQL (per-service `SELECT` grant); no API call |
| Reference Data writes | Via `ram-reference-data` API (admin / Phase 0 seeding) |
| Cross-service workflow | REST call to the owning service |
| Cross-row workflow safety | Pessimistic row lock on the related row + natural-key uniqueness on the new row (detail in *Data Architecture*) |
| Read-model federation | SQL JOIN over the shared schema (no API fan-out) |
| Outbound email | Domain service → `ram-notification` → HMCTS Email → recipient (or, for Payment, → JFEPS via authoriser upload) |
| Configuration | Per-service: Spring profiles + `application.yml` + Azure Key Vault. Cross-service policy values: shared `ram_configuration_values` infrastructure table (read-only via direct SQL; no API). |

## Deployment topology

- **Infrastructure provisioning** — **Terraform** (HMCTS standard). Product-level shared estate (AKS, PostgreSQL, ACR, APIM, App Insights, Key Vault) lives in the dedicated **`ram-shared-infrastructure`** repo (HMCTS CNP standard; decision #13), provisioned + independently verified in Epic 0.0; per-service resources (Key Vault namespaces, MRD blob storage, Static Web App) in their own repos. Terraform provisions; Helm deploys; Liquibase owns schema.
- **Production region** — Azure UK South.
- **HA** — multi-AZ within UK South for every component:
  - AKS node pools span all three UK South AZs with pod anti-affinity (zone topology spread).
  - PostgreSQL Flexible Server zone-redundant HA (synchronous replication; automatic failover).
  - APIM Premium, Key Vault, Azure Container Registry — all zone-redundant.
- **DR** — open gap; scope and design held in [`./architecture/gaps.md` G3.6](./architecture/gaps.md).
- **Per-service unit** — independently-deployable Spring Boot service; per-service Helm chart with per-environment values files (`values-dev.yaml`, `values-staging.yaml`, `values-production.yaml`).
- **CI/CD** — per-service pipeline (Azure DevOps Pipelines or GitHub Actions). Build → Docker image → Azure Container Registry → Helm upgrade to AKS.
- **Logging** — structured JSON logs (Logstash encoder) with correlation IDs; OpenTelemetry export to Application Insights; 30 days hot in App Insights + 90 days cold in Log Analytics archive.

## Phased rollout (jurisdiction-first)

- **Boundary** — jurisdiction first, then per-region within jurisdiction. Wave 1 = the **SSCS** jurisdiction (replacing ListAssist; GAPS case management retained), all in-jurisdiction applicable roles in one wave. Waves 2+ = Courts jurisdictions (Civil, Crime, Family, Crown) per HMCTS judicial region (replacing APEX/JI).[^d8][^d11]
- **Mechanism** — per-user activation flag in `ram_auth_user_activation_flags` carrying the (jurisdiction, region) tuple (FR57). Migrated-wave users authenticate; non-migrated users are rejected at the `JWTFilter` boundary. Cutover flip: `UPDATE ram_auth_user_activation_flags SET activated = TRUE WHERE jurisdiction = '…' AND region = '…'` per the rollout runbook; flip-off rolls back to the incumbent.
- **Wave gates** — automated tests passing (unit, integration with Testcontainers PostgreSQL, contract); manual UAT signed off by jurisdiction-incumbent-experienced users (ListAssist users for wave 1; APEX users for waves 2+); data readiness verified (reference data current per `ram_sync_status`; bootstrapped users verified against IdP principals); for wave 1, the SSCS-cohort readiness assessment[^d11]; programme sign-off.
- **Build sequence** — Phase 0 cross-cutting services (incl. upstream ingestion) + UI shell; Phases 1–6 domain services in dependency order (JOH → Absence → Vacancy → Booking → Sitting → Payment); Phases 7–8 read-models (Itinerary, MI Feed); Pre-Phase-9 real-IdP cutover; Phase 9+ jurisdiction-first rollout waves.

## Upstream reference-data ingestion (no legacy migration)

Per the revised D3 (2026-06-10), **RAM Pathfinder migrates nothing from ListAssist or APEX** — the Phase 0 Data Migration ETL is retracted. Judicial-holder reference data is ingested from upstream sources of truth, in-process within `ram-reference-data`:

- **JOH eLinks API** → 15 `jo_*` tables. Nightly `@Scheduled` pull; full-refresh upsert on the upstream natural key; rows absent upstream are marked inactive, never hard-deleted. Sync state in `ram_sync_status`.
- **MRD (Master Reference Data)** → `mrd_*` tables. Weekly Excel feed dropped into an Azure Blob container; a `@Scheduled` task validates, upserts, and archives. Transitional until MRD's public APIs ship.
- No new deployable, no new service principal — the tasks write the service's own tables. A sync failure leaves the previous good state; reference data is at most one cycle stale, never partially written.
- Historical data stays in the cohort's incumbent system and is accessed there as needed.
- User/authorisation data is **not** ingested — `auth_*` tables are strictly RAM-internal[^d9], bootstrapped outside the PRD's scope.

## External integrations

| System | Direction | Purpose |
|---|---|---|
| HMCTS IdP | inbound (human authN only) + JWKS used by RAM Pathfinder services for JWT signature validation | OIDC `authorization_code` flow for human users; every RAM Pathfinder service's `JWTFilter` validates inbound user JWTs against IdP JWKS before allowing access to RAM Pathfinder APIs. **Service-principal token issuance** for the payment batch is handled by `ram-mock-auth` in non-prod; production decision per G7.1. |
| JOH eLinks API | inbound (reference data — MVP per NFR24) | Canonical source for the 15 `jo_*` judicial-holder entities; nightly scheduled pull by `ram-reference-data`. Read-only in RAM; corrections at source; no data flows upstream from RAM. |
| MRD | inbound (reference data — MVP per NFR24) | Supplementary judicial reference data (notably JOH Specialisations); weekly Excel via blob drop until MRD public APIs ship. |
| HMCTS Email | outbound | Booking / absence acknowledgements; JFEPS payment schedules |
| JFEPS / Liberata | outbound (via authoriser email upload) | Payment processing — preserved unchanged for SSCS wave 1[^d11] |
| External case-management systems (SSCS: **GAPS** — retained case management; Courts: Listing systems) | outbound (from Phase 9,[^d12]) | Consume RAM's JOH availability + booking APIs; never write into RAM |
| DA&I | inbound (post-MVP REST) | MI consumer for aggregate reports |
| APEX (legacy, Courts waves) | inbound (read-only) | 12-month historical-data bridge for migrated Courts users post-cutover. (ListAssist historical scheduling-data access for wave 1: settled in the SSCS-cohort readiness assessment.) |

## Foundational principles

1. **API for workflows; shared database for simple data access.** Multi-step operations with business rules and state transitions are exposed as APIs by the owning service. Single-field cross-service updates (where DB grants permit) and read-model federation (SQL JOINs over the shared schema) bypass the API. No shared runtime library; each service owns its cross-cutting concerns.
2. **No premature optimisation.** Caching, distributed cache, service mesh, read replicas, async messaging — added only when measurement post-MVP shows the need. Use native platform constructs (DB locking, optimistic concurrency, uniqueness constraints, Spring profiles + Key Vault) before custom entities.

## Where to find more detail

| Topic | Location |
|---|---|
| Decision history, alternatives, validation | [`./architecture.md`](./architecture.md) |
| Conventions — naming, structure, format, communication, process, enforcement | [`./architecture/conventions.md`](./architecture/conventions.md) |
| Repo directory trees, local dev workflow, deployment pipeline | [`./architecture/repo-structure.md`](./architecture/repo-structure.md) |
| Table ownership mapping | [`./architecture/data-tables.md`](./architecture/data-tables.md) |
| HMCTS Crime SpringBoot starter, dependencies, RAM Pathfinder overlay | [`./architecture/starter-template.md`](./architecture/starter-template.md) |
| Gaps (G1–G9) | [`./architecture/gaps.md`](./architecture/gaps.md) |
| Assumptions (A1–A37) | [`./architecture/assumptions.md`](./architecture/assumptions.md) |
| Changelog | [`./architecture/changelog.md`](./architecture/changelog.md) |
| PRD | [`./prd.md`](./prd.md) |

[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d9]: Restructured D9 (2026-06-10) — two user populations: JOHs resolve via jo_people to a personnel number; HMCTS admin staff via a RAM-internal identity table. No legacy user migration.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
[^d11]: D11 (2026-06-10, amended 2026-06-18) — SSCS-first pilot: wave 1 replaces **ListAssist** (the SSCS judicial-scheduling tool); **GAPS (SSCS case management) is retained, not replaced**; waves 2+ replace JI/APEX per Courts region.
[^d12]: D12 (2026-06-10) — RAM is the system of record for JOH availability and scheduling only; case and hearing management live in external systems.
