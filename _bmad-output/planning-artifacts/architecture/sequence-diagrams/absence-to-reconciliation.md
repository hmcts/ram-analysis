---
parent: ../../architecture.md
title: End-to-end sequence — Absence → Vacancy → Booking → Sitting → Payment → Reconciliation
last_updated: 2026-05-07
---

# Absence → Vacancy → Booking → Sitting → Payment → Reconciliation

High-level sequence diagram of the canonical NJI operational cycle: a Court User logs an absence on behalf of a salaried judge, the absence triggers a vacancy, RSU fills the vacancy with a fee-paid booking, the Court User confirms the sitting, RSU processes the payment, the Payment Authoriser uploads the schedule to JFEPS / Liberata, and finally the payment is reconciled.

The flow is split into **seven phases** — each one driven by a different user (or external actor). Phases are colour-tinted in the diagram for visual separation. Within a phase the sequence is ordered top-to-bottom; phases follow each other in business-process order.

**Cross-cutting steps omitted for clarity** (they apply on every UI→service call but would clutter the diagram):

- All UI→service calls flow through Azure API Management.
- Each service's `JWTFilter` validates the inbound JWT signature against HMCTS IdP's JWKS endpoint **before** the controller runs.
- The same `JWTFilter` calls `POST /authz/check` against `nji-authorisation` to resolve role + Region/Area scope + per-region activation flag (FR58).
- Cross-service calls forward the user's JWT (token propagation; no service principals at MVP).

```mermaid
%%{init: {'sequence': {'actorFontSize': 16, 'actorFontWeight': 'bold', 'messageFontSize': 15, 'noteFontSize': 13, 'mirrorActors': false, 'actorMargin': 30, 'boxMargin': 6, 'messageMargin': 30}}}%%
sequenceDiagram
    autonumber

    actor Court as Court User
    actor RSU
    actor PA as Payment Authoriser

    participant Abs as nji-absence
    participant Vac as nji-vacancy
    participant Bk as nji-booking
    participant Pay as nji-payment
    participant Notif as nji-notification
    participant JFEPS as JFEPS / Liberata

    rect rgb(232, 240, 250)
        Note over Court,JFEPS: Phase 1 — Court User logs absence (with cover request)
        Court->>Abs: POST /v1/absences
        Abs->>Abs: validate (FR15)
        Abs-->>Court: 201 (pending)
        Abs->>Notif: send absence ack
        Notif->>Notif: dispatch to salaried judge via HMCTS Email
    end

    rect rgb(232, 250, 232)
        Note over Court,JFEPS: Phase 2 — RSU approves absence, vacancy auto-created (R4)
        RSU->>Abs: POST /v1/absences/{id}/approve
        Abs->>Abs: pending to approved
        Abs->>Vac: POST /v1/vacancies
        Vac-->>Abs: 201 (needs-allocation)
        Abs-->>RSU: 200
    end

    rect rgb(250, 240, 230)
        Note over Court,JFEPS: Phase 3 — RSU creates fee-paid booking, vacancy filled in-tx (R5)
        Note right of RSU: Advertising is out-of-system. RSU records the booking once a fee-paid judge replies.
        RSU->>Bk: POST /v1/bookings
        Bk->>Vac: SELECT FOR UPDATE
        Bk->>Bk: INSERT booking
        Bk->>Vac: UPDATE filled = true
        Bk->>Bk: COMMIT
        Bk-->>RSU: 201 booking
        Bk->>Notif: send booking ack
        Notif->>Notif: dispatch to fee-paid judge via HMCTS Email
    end

    rect rgb(250, 232, 240)
        Note over Court,JFEPS: Phase 4 — Court User confirms sitting after the day
        Court->>Bk: POST /v1/bookings/{id}/confirm
        Bk->>Bk: status = confirmed
        Bk-->>Court: 200 — eligible for payment
    end

    rect rgb(240, 232, 250)
        Note over Court,JFEPS: Phase 5 — RSU processes payments, JFEPS schedule emailed
        RSU->>Pay: POST /v1/payments/process
        Pay->>Pay: SQL JOIN bookings + sittings
        Pay->>Pay: generate JFEPS Excel
        Pay->>Pay: INSERT payments + schedules
        Pay-->>RSU: 201 processed
        Pay->>Notif: send JFEPS schedule
        Notif->>PA: JFEPS Excel email
    end

    rect rgb(232, 250, 250)
        Note over Court,JFEPS: Phase 6 — Authoriser uploads to Liberata (out-of-band)
        PA->>JFEPS: upload JFEPS Excel
        JFEPS->>JFEPS: process payments and pay judge
    end

    rect rgb(250, 250, 232)
        Note over Court,JFEPS: Phase 7 — RSU marks payment reconciled (manual at MVP)
        RSU->>Pay: POST /v1/payments/{id}/reconcile
        Pay->>Pay: status = matched
        Pay-->>RSU: 200
    end
```

## Phase summary

| Phase | Driver | Architectural rule | Outcome |
|---|---|---|---|
| 1 — Absence logged | Court User | Validation (FR15-style) | Absence record created (pending); ack email to salaried judge |
| 2 — Absence approved | RSU | **R4** — approval triggers vacancy creation | Vacancy created (needs-allocation) |
| 3 — Booking created | RSU | **R5** — pessimistic row lock + in-transaction UPDATE on `vacancies.filled` | Booking persisted; vacancy filled; ack email to fee-paid judge |
| 4 — Sitting confirmed | Court User | State transition (eligible for payment) | Booking status = confirmed |
| 5 — Payment processed | RSU | SQL JOIN over confirmed bookings + sittings; JFEPS Excel content-type | Payment + payment_schedules persisted; JFEPS email to authoriser |
| 6 — Liberata upload | Payment Authoriser | Out-of-band; NJI is not in the loop | Judge paid via JFEPS / Liberata |
| 7 — Reconciliation | RSU | Manual at MVP (automated feed post-MVP) | `payment_reconciliations.status = matched` |

## Where to find more detail

| Detail | Location |
|---|---|
| Service responsibilities and key functions | [`../../architecture.md` → Repository List](../../architecture.md) |
| Data Architecture (shared schema, per-service DB roles, R5 pessimistic-lock pattern) | [`../../architecture.md` → Step 4 *Data Architecture*](../../architecture.md) |
| Integration Points — internal call patterns + external systems | [`../../architecture.md` → Step 6 *Integration Points*](../../architecture.md) |
| Authentication / authorisation cross-cutting steps (omitted from diagram) | [`../../architecture.md` → Step 4 *Authentication & Security*](../../architecture.md), [`../../architecture-summary.md` → *Authentication & Authorisation*](../../architecture-summary.md) |
| Per-table column-level detail (`bookings`, `vacancies`, `payments`, `payment_schedules`, `payment_reconciliations`, `notification_dispatches`, `auth_users`) | [`../data-tables.md`](../data-tables.md) |
| Reconciliation lifecycle (MVP manual; post-MVP roadmap) | [`../../architecture.md` → Step 4 *Data Flow — Canonical Operational Cycle*](../../architecture.md); PRD `FR46` |
| Retry-safety conventions (`@Version` optimistic locking, natural-key unique constraints, `SELECT … FOR UPDATE`) | [`../conventions.md` → *Retry safety and concurrency control*](../conventions.md) |
| JWT propagation pattern (the cross-cutting auth step omitted from the diagram) | [`../conventions.md` → *Communication Patterns / JWT propagation*](../conventions.md) |
