---
project_name: 'ram-analysis (RAM Pathfinder)'
user_name: 'Ramnish'
date: '2026-07-08'
sections_completed: ['technology_stack', 'delivery_discipline', 'backend', 'data_persistence', 'api_formats', 'frontend', 'testing', 'workflow_enforcement', 'critical_dont_miss']
existing_patterns_found: 40
status: 'complete'
rule_count: 45
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

> **Scope note:** `ram-analysis` is the planning/architecture hub — it holds no runtime code. These rules govern the **RAM Pathfinder service code** the agents implement in the polyrepo (`ram-reference-data`, `ram-authorisation`, … `ram-ui`, `ram-admin-ui`). This file is the lean, LLM-optimised distillation of `conventions.md` + `architecture.md` + `repo-structure.md` + `delivery-operating-model.md`; those remain authoritative.

---

## Technology Stack & Versions

- **Backend:** Java 25 (LTS) · Spring Boot 4 · Gradle **Groovy** DSL + Wrapper · scaffold from `hmcts/service-hmcts-crime-springboot-template`
- **Data:** PostgreSQL 17 (Azure Flexible Server; 16 acceptable) · **Liquibase** (RAM standard — the template ships Flyway; **do not use Flyway**)
- **Frontend:** React 18.x · TypeScript 5.x · Vite 5.x · GOV.UK Design System (**no Tailwind**) · TanStack Query · React Hook Form + Zod · axe-core
- **Platform:** AKS (UK South, multi-AZ) · Helm · Terraform · APIM · Azure Key Vault · OpenTelemetry → App Insights · TLS 1.3 min (1.2 fallback)
- **Libraries:** Lombok · MapStruct · OWASP Java Encoder · JaCoCo · CycloneDX · Swagger Core

## Critical Implementation Rules

### Delivery & repo discipline (polyrepo)

- **No shared runtime library** — duplication is accepted; consistency is enforced by CI / ArchUnit / Spectral / Pact / review, never a lib. Never introduce a shared code module.
- Each service = own repo, pipeline, release cadence. Cross-service work goes via **API contracts, not shared code**.
- **Reference Data is read directly via JPA** from the shared schema — there is **no `ReferenceDataClient`**. Other services are called via typed clients.
- **Contracts are producer-owned:** each service generates its OpenAPI (Swagger Core) and publishes by Gradle `maven-publish` as a Maven-format artefact (`uk.gov.hmcts.ram:api-ram-{service}:{version}`); consumers pin the version. `ram-architecture` holds a **read-only mirror only**.
- Implementation output lands in the **target repo**; the planning repo is never written to. **Git commits happen externally (VSCode) — do not run git write commands.**

### Backend (Java / Spring Boot)

- Package `uk.gov.hmcts.ram.{service}.{layer}` (controller/service/repository/domain/dto/client/config/error/exception).
- **Per-request auth:** custom `JWTFilter` validates JWT vs IdP JWKS → `POST /authz/check` → populates request-scoped `AuthDetails` (roles + jurisdiction + Region/Area scope + activation flag). RAM variance from the template's claims-only approach (FR2/FR57). Every service implements it; no shared lib.
- **Errors:** per-service `@ControllerAdvice` → RFC 9457 `application/problem+json`. Fixed exception→status map (validation 422, authorisation 403, business-rule 409/422, dependency 502, concurrency 409, unexpected 500).
- **Retry/concurrency = native PostgreSQL + JPA only:** unique constraints (dup-create → 409), optimistic locking, pessimistic row locks. **No idempotency-key tables, no IdempotencyFilter.**
- **Inter-service:** typed client per callee in `client/`, wrapping Spring Boot 4 `RestClient` with JWT-propagation + correlation-ID interceptors; **domain-language method names**, not HTTP verbs. Two auth modes: JWT propagation (user flows) vs OAuth `client_credentials` (batch, e.g. `ram-payment-batch`).

### Data & persistence

- Single shared schema; per-service DB roles enforce writes. **Whoever writes the Liquibase changelog owns the table.**
- **Prefix = ownership:** `ram_` (RAM-owned, entity-plural) · `jo_`/`mrd_` (upstream tier-a, **read-only in RAM**, written only by `ram-reference-data` ingestion) · `mock_` (dev-only, never prod). No `_overlays` suffix (use `ram_joh_ticket`).
- **PK `id uuid` (never bigint).** FKs `{entity_singular}_id`; JOH refs use `personnel_number` → `jo_people`, not a surrogate. `created_at`/`updated_at timestamptz NOT NULL` on every table.
- **Liquibase for DDL only** (`src/main/resources/db/changelog/NNN-name.sql`) — not for loading upstream data. Cross-table grants are explicit in the owning service's changelog (tier-a: only `ram_reference_data` writes; others SELECT at most).

### API & formats

- `/v1/` prefix; plural-noun resources (`/v1/johs`, `/v1/bookings`); actions as URL segments (`POST /v1/absences/{id}/approve`) — **never RPC route names**.
- Path vars/query params `camelCase`; JOH keyed on `{personnelNumber}`. Headers `Title-Kebab-Case`, no `X-` prefix (`Correlation-Id`, `Idempotency-Key`, `Deprecation`, `Sunset`).
- **JSON `camelCase` everywhere** (DB `snake_case` → API `camelCase` via JPA/Jackson). Success = bare resource (**no `{data,error}` wrapper**). Booleans `true/false` (no 0/1, Y/N). **Timestamps ISO 8601 UTC always (`Z`)**; UI converts to UK local for display only.
- Pagination: cursor-based for large/chronological lists; offset for small filtered lists. Rate limiting at APIM, not in-service.

### Frontend (React / TypeScript)

- React 18 + TS 5 + Vite 5. GOV.UK Design System required for WCAG 2.2 AA — no Tailwind, no ad-hoc spinners (use GOV.UK loading patterns).
- **Module-per-domain** (`modules/{domain}/pages|components|hooks|api`), not by-type. Two UI repos (`ram-ui` business, `ram-admin-ui` admin) — no shared client lib between them.
- Server state: TanStack Query (`isLoading`/`isError` pattern). Forms: React Hook Form + Zod matching the OpenAPI shape. **Server is source of truth — UI validation is UX-only, never enforces a constraint the server doesn't.**
- API clients generated per backend service from its OpenAPI (`openapi-typescript-codegen`/`orval`), regenerated in the repo's own CI.

### Testing

- Unit `*Test.java` (mock deps) · Integration `*IT.java` (Testcontainers PostgreSQL) · Contract (Pact) — every commit. E2E (Playwright) one suite per phase as a gate.
- **Coverage target = behaviour coverage, not line coverage;** PRs justify behaviour, not coverage stats.
- **Incumbent parity (ListAssist SSCS / APEX Courts) is MANUAL UAT** under `docs/uat/` per service — a wave-cutover sign-off gate, **not** a CI harness. No `*ApexParityTest.java`.

### Workflow & enforcement

- Scaffold every service from the HMCTS Crime SpringBoot template; Gradle Groovy DSL + Wrapper.
- **CI gates (fail build on violation):** Spotless+Checkstyle (Java), ESLint+Prettier (TS), SQLFluff (SQL), ArchUnit (package/naming/deps), Spectral (OpenAPI ruleset), Pact, JaCoCo + CycloneDX SBOM, axe-core (UI).
- Git: branch `feature/{ticket}-{desc}`; Conventional Commits (`feat:`/`fix:`/`docs:`/`refactor:`/`test:`/`chore:`), imperative, ≤72-char subject; PRs → `main` (trunk-based). **Commits made externally by the user.**
- Pattern changes = PR against `architecture.md`/`conventions.md`; **existing services are not force-retrofitted** (no version cascade); new services adopt the new pattern.
- Logging: SLF4J per class (or Lombok `@Slf4j`); Logstash JSON encoder + OpenTelemetry trace context; `correlationId` in MDC on every line.

### Critical don't-miss / security

- **NEVER log** PII (judge data, payroll/personnel numbers), bank details, case-level identifiers, or raw request bodies.
- **NEVER store bank details** (NFR14); MI/read models hold **no case-level data** (NFR23).
- Timestamps stored UTC only. TLS 1.3 min (1.2 fallback). Secrets via Azure Key Vault (Spring Cloud Azure), never in code/repo.
- **Anti-patterns:** bigint PKs · `snake_case` JSON · success wrappers · custom error shapes · `200` with `success:false` · RPC-style routes · shared runtime library · `ReferenceDataClient` (read Reference Data via JPA) · Flyway · local-tz timestamps.

---

## Usage Guidelines

**For AI agents:**

- Read this file before implementing any code in a RAM Pathfinder service repo.
- Follow ALL rules exactly; when in doubt, prefer the more restrictive option.
- This is a lean summary — `conventions.md`, `architecture.md`, `repo-structure.md`, and `delivery-operating-model.md` (via the `ram-architecture` context bus) remain authoritative for detail.
- Do not run git write commands; surface the diff for the human to commit externally.

**For humans:**

- Keep this file lean and agent-focused; update when the tech stack or a convention changes (via a PR against `conventions.md`/`architecture.md` first).
- When the `ram-architecture` context bus is stood up, this file seeds each service repo's `CLAUDE.md`; keep it in sync with the pinned bus version.
- Review periodically; remove rules that become obvious.

Last Updated: 2026-07-08
