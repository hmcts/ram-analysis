---
type: 'Architecture Shard'
description: 'Every gap is named, categorised, owned, and has a mitigation or fallback. Implementation can begin while these are tracked and resolved in parallel.'
resource: 'architecture/tobe/gaps.html'
tags: [ram-pathfinder, architecture]
timestamp: '2026-05-08'
parent: ../architecture.md
title: Documented Gaps (G1–G9)
last_updated: 2026-05-08
extracted_in: architecture.md v1.8 — Strategy B refactor
---

# Documented Gaps (G1–G9)

> Sibling of [`../architecture.md`](../architecture.md). Linked from *Architecture Validation Results*.

Every gap is named, categorised, owned, and has a mitigation or fallback. Implementation can begin while these are tracked and resolved in parallel.

## Critical Gaps

None. No gap blocks implementation.

## G1 — External Verification Dependencies (HMCTS infrastructure)

| ID | Gap | Mitigation / Fallback | Owner |
|---|---|---|---|
| **G1.1** | HMCTS IdP support for OIDC human-user authentication is assumed but not verified. | **No longer Phase 0 blocking** — mock auth covers Phase 0–8. Verification needed before pre-Phase-9 cutover. If SAML-only: swap protocol library at the integration boundary; pattern unchanged. | Pre-Phase-9 prerequisite — IdP team confirmation |
| **G1.2** *(reopened v2.6, 2026-05-07)* | HMCTS IdP support for OAuth 2.0 `client_credentials` grant — needed in production for the payment-batch service principal (`ram-payment-batch`). `ram-mock-auth` covers dev/CI/integration. Production options in G7.1: RAM Pathfinder-internal issuer, Azure Workload Identity, mTLS, or HMCTS IdP `client_credentials`. | Pre-Phase-9 — IdP team confirmation, or adopt an alternative from G7.1 |
| **G1.3** *(reworded 2026-06-11 — ETL retracted[^d3])* | HMCTS IdP principal export or query API for **bootstrap verification** is assumed — confirming every bootstrapped user (JOH + admin-staff populations, restructured D9) maps to a real IdP principal before each wave's cutover. | **No longer Phase 0 blocking** — mock auth users mirror the seeded roster in Phase 0; real verification deferred to pre-Phase-9 cutover. If unsupported: fallback to manual verification report compiled by IdP team out of band. | Pre-Phase-9 prerequisite — IdP team confirmation |
| **G1.4** *(reconciled 2026-06-17)* | HMCTS Crime SpringBoot template (`hmcts/service-hmcts-crime-springboot-template`@`main`) is the starter. **Reconciled against `main`:** the base is **deliberately minimal** — Java 25, Spring Boot **4.1.0**, Gradle Groovy DSL, Logstash JSON logging, OpenTelemetry, Lombok, JaCoCo, CycloneDX, gradle-git-properties, ben-manes-versions, Actuator, Dockerfile, `webmvc-test`. **NOT in the base** (sourced from the separate **`hmcts/service-hmcts-springboot-demo`** repo or added as RAM conventions — see `starter-template.md` §B): Liquibase, Testcontainers, MapStruct, JWTFilter/`jjwt`, OWASP encoder, docker-compose plugin, OpenAPI tooling. The earlier "all present in baseline (2026-05-06)" review **overstated** the template. | Scaffolding-script scope is larger than first scoped — it assembles ~9 capabilities onto the minimal base (track per G1.4a). Verify demo-repo branch versions at build time. | RAM Pathfinder architecture team |
| **G1.4a** *(expanded 2026-06-17)* | The base template is minimal; `ram-scaffold.sh` must add — beyond the Helm chart + per-repo `terraform/` skeleton (2026-06-11 Terraform decision) — **Liquibase, Testcontainers, MapStruct, custom `JWTFilter` + `jjwt`, OWASP encoder, the docker-compose plugin, OpenAPI tooling (springdoc/Swagger), and the CI quality gates (Spectral/ArchUnit/Spotless/Checkstyle)**, most cherry-picked from `hmcts/service-hmcts-springboot-demo`. **Liquibase is a RAM convention** — the demo repo's Database branch uses Flyway; RAM standardises on Liquibase. | Scope `ram-scaffold.sh` accordingly; verify demo-repo branch versions at build time; consider splitting Story 0.1.1 (scaffold vs shared-estate vs template overlay) given the expanded scope. | Phase 0 deliverable — RAM Pathfinder architecture team |
| **G1.4b** *(new)* | **Spring Cloud Azure Key Vault integration is not in the template baseline.** | Add per service via `com.azure.spring:spring-cloud-azure-starter-keyvault-secrets`. Phase 0 scaffolding includes this. | Phase 0 deliverable — RAM Pathfinder architecture team |
| **G1.5** | HMCTS Email infrastructure (SMTP / Microsoft Graph) availability and authentication mechanism for AKS-hosted services is assumed. | If unavailable in expected form: alternate transport (Azure Communication Services Email) is a documented fallback; Notification service contract unchanged. | Phase 0 prerequisite — HMCTS infrastructure team |
| **G1.6** | Mock-to-real-IdP cutover plan must be operationally rehearsed before pre-Phase-9. | Cutover is a Spring profile change (no code change); rehearse on staging environment with real IdP credentials before scheduling pilot wave 1. | Pre-Phase-9 deliverable — RAM Pathfinder team |

## G2 — Programme-Management Dependencies (out of architecture scope but block implementation)

Tracked in the PRD's open-items list. Restated here because they affect when the architecture can proceed.

| ID | Gap | Notes |
|---|---|---|
| **G2.1** | Pilot region selection for Phase 9 wave 1 | Affects capacity sizing for first deployment; programme decision |
| **G2.2** | Cross-region workflow handling per wave | Per-wave decision; programme template needed (Risk #1 from brainstorming) |
| **G2.3** | Operational availability hours (assumed 07:00–19:00 UK weekdays) | Programme to confirm; affects on-call expectations |
| **G2.4** | Capacity numbers (~50–100 per region, ~200–500 national assumed) | Programme to confirm; affects HPA tuning and PostgreSQL sizing |
| **G2.5** | Phase 0 migration owners (Reference Data sign-off, Users/Roles sign-off) | Programme to name owners; affects Phase 0 deliverable acceptance |
| **G2.6** | Historical-data 12-month window length | Programme to confirm; recommended in Step 4 (TBD #6 partial resolution) |

## G3 — HMCTS Technology Approval

| ID | Gap | Notes |
|---|---|---|
| **G3.1** | Azure as cloud platform (UK regions) — assumed approved per programme guidance | Confirm with HMCTS architecture/security review |
| **G3.2** | Azure Database for PostgreSQL Flexible Server — recommended; HMCTS may prefer Azure SQL | Confirm with HMCTS data team; switch is reversible at Phase 0 cost |
| **G3.3** | Azure API Management for ingress and rate limiting | Confirm with HMCTS infrastructure; Spring Cloud Gateway is named alternative |
| **G3.4** | GOV.UK Design System for React (`govuk-react` or HMCTS-internal equivalent) | Verify HMCTS-internal version exists and is preferred; otherwise use community `govuk-react` |
| **G3.5** | Azure Static Web Apps for UI hosting | Alternative: Azure Blob Storage + CDN; both viable |
| **G3.6** *(open; consolidated v2.8, 2026-05-08)* | **Disaster recovery (DR) — open gap.** MVP runs in a single Azure region (UK South) with multi-AZ HA. All DR design and scope is held here; no DR detail is asserted elsewhere. Decision points: (a) **DR in MVP scope?** Programme decision; default post-MVP (programme accepts full-region-UK-South-unavailability risk for MVP and pilot waves). (b) **Target region** — UK West is the natural candidate (data-residency-compliant per NFR31); not committed. (c) **Standby model** — cold-standby (manual failover) vs warm-standby vs active/active. Working assumption: cold-standby. Active/active is incompatible with the shared global PostgreSQL without multi-master replication (premature per Principle 2). (d) **PostgreSQL geo-redundant backup** with the chosen DR region as restore target. (e) **DR-region stack defined in Terraform** (held in `ram-shared-infrastructure` alongside the production stacks, per decision #13) + AKS Helm definitions for the DR region; cluster not pre-provisioned until activation. (f) **DNS failover** (Azure Front Door / Traffic Manager) and runbook. (g) **RTO/RPO targets** agreed with HMCTS. | Programme (in/out of MVP) + RAM Pathfinder architecture team (design once in scope). Pre-broad-GA at the latest. |

## G4 — Post-Completion Refinement Tasks (not blocking, scheduled after Step 8)

| ID | Gap | Owner |
|---|---|---|
| **G4.1** | Mermaid / C4 diagrams in `ram-architecture/diagrams/` to replace ASCII-art representations of internal communication, data flow, and deployment topology | RAM Pathfinder architecture team post-completion |
| **G4.2** | Sample ADRs (`ADR-001-greenfield-not-strangler.md`, `ADR-002-no-shared-library.md`, `ADR-003-rest-first-no-event-bus.md`, etc.) capturing locked decisions in formal ADR shape | RAM Pathfinder architecture team post-completion |
| **G4.3** | Per-service OpenAPI snippets seeded as Phase 0 paper contracts[^d1] for Itinerary and MI Feed at minimum, plus skeleton specs for the 6 domain services | Phase 0 deliverable |
| **G4.4** | ArchUnit fitness function ruleset codified for the per-service convention checks | Phase 0 deliverable as part of scaffolding |
| **G4.5** | Spectral OpenAPI lint ruleset codified for the API-as-Product standards (consistent error envelope, [RFC 9457](https://datatracker.ietf.org/doc/html/rfc9457) problem-details references, versioning prefix, deprecation headers per [RFC 9745](https://datatracker.ietf.org/doc/html/rfc9745) + [RFC 8594](https://datatracker.ietf.org/doc/html/rfc8594)) | Phase 0 deliverable as part of scaffolding |
| **G4.6** *(RETIRED 2026-06-11)* | ~~Phase 0 ETL — APEX-side input mapping validation.~~ **Retired with the ETL itself** (revised D3, 2026-06-10 — no legacy data migration of any kind). The successor concern — validating the ingestion mapping against the JOH eLinks API contract and the first MRD workbook — is **G8.1**. | Closed 2026-06-11 |
| **G4.7** *(RETIRED 2026-06-11)* | ~~Operator-initiated ETL — post-MVP refinement.~~ **Retired with the ETL itself**[^d3]. The upstream ingestion mechanisms run in-process inside `ram-reference-data` (no operator JWT, no service identity needed). | Closed 2026-06-11 |

## G5 — Mock-First Authentication Scope

| ID | Gap | Notes |
|---|---|---|
| **G5.1** | Mock auth must implement enough of the OIDC contract to be issuer-substitutable for HMCTS IdP. | Implement using Spring Authorization Server (provides full OIDC support out of the box). OIDC-contract parity is covered by automated integration / contract tests at the IdP-client level (per A26 in [`./assumptions.md`](./assumptions.md)), not by APEX-comparison UAT. |
| **G5.2** | Mock auth user roster must remain in sync with migrated APEX user/role data so that Phase 0–8 testing exercises realistic flows. | Mock auth seed-data generated from the same Phase 0 migration reconciliation report (or a sanitised subset). Refreshed when migration data changes. |
| **G5.3** | Production safeguard: mock auth must never run in production; production deployment manifests must never reference mock-auth issuer URLs. | Spring profile validation at mock-auth startup (refuses to start with `production` profile); CI lint enforces production Helm values reference real-IdP issuer. |

## G6 — Shared Database Topology Risks

| ID | Gap | Notes |
|---|---|---|
| **G6.1** | **Schema-evolution coordination across whitelisted tables.** When Service A reads or writes Service B's whitelisted tables, schema changes to those columns affect A. The owning service (B) must maintain a deprecation policy on whitelisted columns parallel to API versioning. | Mitigation: schema changes to whitelisted columns follow the same deprecation cadence as API versioning (deprecate, sunset header on the published data contract, remove no sooner than 6 months for internal consumers). Whitelist documentation lives in the owning service's repo alongside its API contract. |
| **G6.2** *(refined 2026-05-06; 2026-05-08)* | **Single-DB blast radius.** A PostgreSQL outage affects every RAM Pathfinder service simultaneously (vs per-service DBs where one DB outage affects only one service). | Mitigation: PostgreSQL Flexible Server **zone-redundant HA** within UK South — primary + standby in different AZs, synchronous replication, automatic failover (<60 s typical). Single-AZ failure inside UK South is tolerated transparently. Point-in-time restore retained. **Full-region UK South loss is the residual risk** — addressed by DR (see G3.6) if/when approved; without DR, the residual risk is accepted for MVP and pilot waves. Acceptable trade for the operational simplicity of one DB at RAM Pathfinder's bounded scale. |
| **G6.3** | **Cross-region rollout with global DB.** All regions share one DB instance, so Region B's data is visible to Region A immediately on cutover (no APEX-bridge needed for cross-region RAM Pathfinder data). However, during phased rollout, non-migrated regions still have data only in APEX, not in the shared DB. | Mitigation: per-region DB writes only happen for migrated regions; cross-region workflows during partial rollout still rely on the APEX read-only bridge for non-migrated regions' data (Risk #1 unchanged). |
| **G6.4** | **DB role grant maintenance.** Each cross-service grant is a piece of operational state (`GRANT SELECT ON ram_vacancies TO ram_booking;`) that must be applied via Liquibase changelogs owned by the granting service. Adding/removing grants requires PR coordination between services. | Mitigation: grants codified in the table-owning service's Liquibase changelogs; PR template includes "grants checklist"; ArchUnit-style fitness function in CI verifies declared grants match actual code-level cross-service table access. |
| **G6.5** | **Liquibase changeset versioning across services.** When Service A's table has consumers, A's changeset that drops or renames a column must coordinate with consumer updates. | Mitigation: deprecation-then-remove pattern — A first adds the new column in `db/changelog/NNN-add-*.sql`, both A and consumers transition, then A removes the old column in a later `NNN-remove-*.sql`. Same pattern as API versioning. |
| **G6.6** *(new)* | **Table-name collision risk.** Without schema isolation, two services could create tables with the same name in the shared schema. | Mitigation: ArchUnit-style fitness function in CI verifies no two services' Liquibase changelogs create overlapping table names. Authoritative table-ownership mapping documented in [`./data-tables.md`](./data-tables.md). Code review backs the fitness function. |

## G7 — Service-identity question (post-MVP open item)

| ID | Gap | Notes |
|---|---|---|
| **G7.1** *(revised v2.6, 2026-05-07 — now MVP-relevant for the payment batch)* | **Service-identity mechanism for non-user-initiated flows.** v2.6 introduces the **payment-processing batch** (`ram-payment-batch`) as a scheduled service principal — the first MVP non-user-initiated runtime flow. **At MVP** the batch authenticates against `ram-mock-auth` via OAuth `client_credentials` (mock issues both human and service-principal tokens). **For production**, the issuer choice is still deferred. Other future triggers that would also need a service identity: (a) DA&I post-MVP integration; (b) async messaging / event-bus patterns; (c) other scheduled background jobs (MI Feed pre-aggregation, reconciliation feed); (d) ~~Phase 0 ETL evolving from operator-initiated to automated~~ *(retired 2026-06-11 — ETL retracted; the eLinks/MRD ingestion runs in-process inside `ram-reference-data` and needs no service identity)*. | **Pre-Phase-9 decision needed** for production service-auth issuer. Options: <br/>(A) **RAM Pathfinder-internal service-auth issuer** — production-harden the mock-auth Spring Authorization Server; runs as a real (non-mock) service. JWTFilter configured for multi-issuer (HMCTS IdP for humans + ram-service-auth for services). <br/>(B) **Azure Workload Identity / Managed Identity** — cloud-native; no shared secrets; tokens issued by Entra ID and validated via its JWKS. **Likely the default given RAM Pathfinder is on AKS.** <br/>(C) **mTLS** — per-service certs at TLS layer; operationally heavy. <br/>(D) **HMCTS IdP `client_credentials`** — only if HMCTS IdP supports it (G1.2). <br/>Default recommendation: **(B) Azure Workload Identity** for the AKS pod that runs the batch — zero shared secrets, cloud-managed, fits the existing Azure stack. |
| **G7.2** *(new v2.5, 2026-05-07)* | **DA&I post-MVP integration auth model is undecided.** When DA&I starts consuming RAM Pathfinder's MI Feed API post-MVP, it needs an authentication mechanism. If DA&I has a human-user identity at HMCTS IdP it can use the same OIDC flow as other users; if DA&I is a service consumer it needs a service-identity mechanism (see G7.1). | **Open question for post-MVP.** Resolve as part of DA&I onboarding work, alongside G7.1. |

## G8 — Upstream Reference-Data Integration

| Gap | Detail | Resolution path |
|---|---|---|
| **G8.1** | **JOH eLinks API contract + MRD feed arrangements are unconfirmed.** The ingestion design (nightly in-process sync; weekly blob drop) assumes: the eLinks API exposes all 15 `jo_*` entities with stable natural keys (`personnel_number` for `jo_people`); the jurisdiction hierarchy's parent-child shape is available (natively or derivable on ingest); the MRD team can deliver the weekly workbook to an Azure Blob container in an agreed shape. When the contract and first workbook land, validate the ingestion mapping: every upstream field RAM needs has a slot, the natural-key scheme holds, and update cadence/SLA is workable. An unmapped upstream structure raises an architectural PR. | Phase 0 deliverable — confirm with Judicial Office (eLinks) + the MRD team early; the SSCS as-is analysis pack[^d11] should capture the data shapes. Closes when both ingestion paths run end-to-end against real upstream data. |
| **G8.2** | **Upstream-overlap vocabulary candidates.** Three RAM-owned vocabularies plausibly duplicate upstream entities: `ram_joh_types` (vs `jo_appointment_titles` / `jo_judiciary_roles`), `ram_court_types` (vs `jo_location_types`), `ram_ticket_types` (vs `jo_tickets` / `jo_ticket_categories` / `jo_ticket_category_types`). Kept as tier-(b) tables pending G8.1; retire each where the upstream entity covers it. | Resolved alongside G8.1 when the eLinks contract is confirmed. Each retirement is a Liquibase changeset + data-tables.md update. |
| **G8.3** | **ListAssist scheduling-data historical access for wave 1 is unsettled.** Courts waves have the 12-month read-only APEX bridge (TBD #6); ListAssist (the SSCS scheduling tool) is replaced in wave 1, and the historical-access window for its scheduling data is programme-managed. (GAPS, the SSCS case-management system, is retained, not decommissioned.) | Settle in the SSCS-cohort readiness assessment[^d11] before the wave-1 cutover plan is finalised. |

## G9 — Terraform State & Execution (new 2026-06-11)

| Gap | Detail | Resolution path |
|---|---|---|
| **G9.1** | **Terraform state backend + plan/apply pipeline arrangement unconfirmed.** The 2026-06-11 decision mandates Terraform for all Azure provisioning; per decision #13 (2026-07-06) the shared estate lives in the dedicated `ram-shared-infrastructure` repo (per-service resources per repo). To confirm with HMCTS: the state backend (Azure Storage backend per HMCTS convention vs Terraform Cloud), state isolation per environment stack, who runs plan/apply (GitHub Actions workflow per repo vs platform team), and approval gating for production applies. Cross-repo references (e.g. a service's Key Vault referencing the shared estate's AKS identity) need remote-state or data-source conventions agreed. | Phase 0 prerequisite — confirm HMCTS Terraform conventions before the Epic 0.0 estate apply; record the pattern in `ram-architecture/runbooks/terraform.md`. |

[^d1]: D1 — Phase 0 Foundations scope: Reference Data, Authorisation (SSO), Notification, API contracts, deployment platform, structured logging.
[^d3]: Revised D3 (2026-06-10) — no data migration from any legacy system; judicial-holder reference data is ingested from the JOH eLinks API and MRD.
[^d11]: D11 (2026-06-10, amended 2026-06-18) — SSCS-first pilot: wave 1 replaces **ListAssist** (the SSCS judicial-scheduling tool); **GAPS (SSCS case management) is retained, not replaced**; waves 2+ replace JI/APEX per Courts region.
