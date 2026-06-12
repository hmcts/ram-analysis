---
name: Use natively-supported constructs over custom entities
description: When a concept is already implemented in the base product / framework / DB engine, use that primitive instead of designing a custom entity for it. Avoid over-engineering.
type: feedback
originSessionId: 4416fc27-4969-428d-8d1c-6e5061146cb7
---
Use **native constructs of the underlying platform** (DB engine, framework, language, OS) before introducing custom entities, tables, libraries, or services for the same concept.

**Why:** introducing custom entities for problems already solved by the platform creates: (a) maintenance burden (custom code, tests, schema, migrations); (b) divergence from well-understood industry primitives that are documented, tested, and battle-hardened; (c) carrying cost forever, even if the original justification was speculative; (d) signals over-engineering, which the user calls out as a project anti-pattern.

**How to apply:**

- Before designing a new table / class / service / library for a behaviour, ask: *does the platform already do this?*
  - **Concurrency safety / locking** → use DB row-level locking (`SELECT FOR UPDATE`), optimistic locking (`@Version`), unique constraints, and natural keys — not custom dedup tables (e.g., **avoid `*_idempotency_keys` tables**; use natural-key + unique-constraint dedup at the DB layer).
  - **Audit / change history** → use DB triggers, temporal tables, change-data-capture, or the framework's audit support — not bespoke audit-row-per-write code unless the platform truly lacks it.
  - **Authentication / authorisation** → use OAuth/OIDC libraries and standard claim mechanisms — not custom token formats.
  - **Caching** → use the framework's cache abstraction or a managed cache product — not bespoke in-memory maps.
  - **Retry / backoff / circuit-breaker** → use Resilience4j or the framework's retry annotations — not hand-rolled state machines.
- Default to the simplest workable use of the native primitive; introduce custom code only when measurement or evidence shows the primitive is insufficient (consistent with the architecture's Principle 2: no premature optimization).

**Origin:** 2026-05-06 NJI architecture review — user pushed back on per-service `*_idempotency_keys` tables, pointing out that DB-level row locking + audit trail covers the same ground using PostgreSQL primitives. We dropped the custom tables and replaced them with natural-key dedup + optimistic locking (`@Version`) + pessimistic row locking (`SELECT FOR UPDATE`). The user's exact direction: *"In future, avoid over-engineering and use natively supported constructs rather than creating custom entities for concepts that are implemented in the base product e.g. locking in this instance."*
