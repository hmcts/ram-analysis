# Business Case — RAM Pathfinder

| Field | Detail |
|---|---|
| **Author** | Ramnish |
| **Date** | 2026-06-24 |
| **Status** | Draft for review |
| **Decision sought** | Approval to fund and proceed with the RAM Pathfinder MVP, delivering the SSCS Tribunals jurisdiction as wave 1. |

> All financial figures, dates, headcounts and named milestones marked `[PLACEHOLDER]` require confirmation before this case is submitted for approval. 

---

## 1. Executive Summary

RAM Pathfinder is a greenfield, API-driven platform for judicial scheduling across HMCTS Tribunals and Courts — the planning, allocation, confirmation and payment of sittings for Judicial Office Holders (JOHs). This case seeks approval to fund the **MVP**, rolled out **jurisdiction by jurisdiction**, starting with the **SSCS Tribunals jurisdiction in wave 1**.

Two problems drive the investment:

1. **Aged and unsupported incumbents.** In Courts, the JI application runs on **Oracle APEX (OPT)**, which is unsupported with a fixed end-of-life `Dec 2028`. In Tribunals, SSCS judicial scheduling runs on a combination of **ListAssist** (used by Cardiff only) and other legacy systems (used by other SSCS jurisdictions), which RAM Pathfinder replaces in wave 1.
2. **An export-only integration model** (Excel, PDF, email) that cannot serve the upcoming HMCTS programmes (Actuals, Scheduling & Listing reform, DA&I MI consumption).

The recommended option is to build RAM Pathfinder as a modern, accessible, API-first platform on the HMCTS-approved cloud stack (Azure, Java/Spring Boot, Kubernetes), and to **prove it on SSCS first** before committing to the wider Courts rollout. SSCS is a contained, lower-risk wave that exercises the full platform end-to-end and de-risks every subsequent wave.

**Investment sought:** `[PLACEHOLDER: total MVP cost / wave 1 funding envelope]`.
**Indicative benefit:** retirement of ListAssist for SSCS scheduling, a reusable API platform for all judicial jurisdictions, and a path to decommissioning the unsupported APEX estate in later waves — quantified benefits at `[PLACEHOLDER]`.

---

## 2. Strategic Context

RAM Pathfinder aligns with HMCTS's strategic direction on several fronts:

- **Reform and digital service standards.** A modern, WCAG 2.2 AA, GDS-aligned service replaces two dated legacy user interfaces.
- **Platform over point solutions.** One API driven platform serves both Tribunals and Courts. Capability is built once and reused per jurisdiction, rather than rebuilt per system.
- **API-as-Product.** Versioned, documented, deprecation-governed APIs let downstream HMCTS programmes integrate directly, replacing brittle file exports.
- **Risk reduction.** The unsupported APEX platform is a standing operational and security risk; this programme provides the only credible replacement path.

**Why now:** APEX is unsupported with its own end-of-life; every month on the legacy systems delays the API integration the wider HMCTS ecosystem depends on. SSCS is ready as a first wave and provides a low-risk proving ground.

---

## 3. The Problem

| # | Problem | Impact if not addressed |
|---|---|---|
| 1 | JI runs on **unsupported Oracle APEX** with a fixed end-of-life | Operational, security and continuity risk to Courts judicial scheduling; no vendor support |
| 2 | SSCS scheduling depends on **ListAssist**, a separate aged tool | Fragmented tooling; no shared platform or modern UX for Tribunals |
| 3 | **Export-only integration** (Excel/PDF/email) | Cannot support Actuals, Scheduling & Listing reform, or DA&I MI; manual, error-prone, non-scalable |
| 4 | **Dated, less-accessible legacy UIs** | Accessibility and usability below modern public-sector standards; re-training burden |

---

## 4. Options Considered

| Option | Description | Assessment |
|---|---|---|
| **A — Do nothing** | Keep APEX and ListAssist as-is | **Rejected.** APEX is unsupported; continuity and security risk grows; integration debt compounds. Not viable past APEX EOL. |
| **B — Do minimum** | Lift-and-shift / extend the existing systems | **Rejected.** Neither incumbent supports incremental decomposition (no strangler path); does not deliver the API platform or modern UX; spends money without removing the core risk. |
| **C — Greenfield platform, phased per jurisdiction (Recommended)** | Build RAM Pathfinder end-to-end; prove on SSCS wave 1; roll out to Courts regions in later waves | **Recommended.** Removes the legacy risk, delivers the strategic API platform, and contains delivery risk through phased, wave-by-wave cutover. |

**Why greenfield, not strangler:** neither ListAssist nor APEX supports strangler decomposition. RAM Pathfinder is built end-to-end before any user moves; each jurisdiction's legacy system runs unchanged for non-migrated users during phased rollout. No dual-write, no synchronisation layer — a simpler, lower-risk delivery model.
---

## 5. Recommended Option (C) — Scope

**This investment decision covers the MVP, delivered as SSCS wave 1.**

In scope for the MVP:

- All services built end-to-end (Reference Data, Authorisation, Notification, JOH, Absence, Vacancy, Booking, Sitting, Payment, Itinerary, MI Feed).
- Reference data sourced live from the **JOH eLinks API + MRD feed** — no legacy data migration, no ETL.
- SSO authentication (HMCTS IdP) with RAM-owned authorisation; two user populations (JOHs and admin staff).
- Modern, accessible business-user UI replicating the SSCS incumbent's functional surface.
- **SSCS Tribunals jurisdiction cutover (wave 1)**, with behavioural parity verified by manual UAT performed by ListAssist-experienced users.
- API-as-Product standards from Phase 0; JFEPS-compatible payment export preserved unchanged.

Deferred (post-MVP roadmap, **not in this case**): admin UI and admin-write APIs; structured user-action audit; full metrics/traces observability; event streams/webhooks; active matching/allocation (an external-system concern); historical-data access policy.

**Strategic horizon (subsequent business cases / waves):** Courts jurisdictions (Civil, Family, Crown, Crime) migrate region by region in waves 2+, retiring APEX; external HMCTS programmes onboard onto RAM Pathfinder's APIs.

---

## 6. Expected Benefits

| Benefit | Type | Measure |
|---|---|---|
| ListAssist replaced for Tribunals/SSCS judicial scheduling | Operational | SSCS jurisdiction live on RAM Pathfinder; ListAssist retired for scheduling |
| Reusable API platform for judicial scheduling | Strategic | Same core services serve later Courts waves with no re-architecture |
| Path to retiring unsupported APEX | Risk reduction | APEX decommissioned progressively as Courts regions migrate (waves 2+) |
| Modern, accessible, performant UX | Quality / compliance | WCAG 2.2 AA; page-level performance meets or beats incumbent baselines |
| Direct API integration for downstream programmes | Strategic / efficiency | At least one HMCTS programme (Actuals / Scheduling & Listing) integrating via API `[PLACEHOLDER: target date]`, replacing exports |
| Payment continuity at cutover | Operational | Zero failed JFEPS payment cycles attributable to cutover |
| Quantified cost / efficiency savings | Financial | `Reduced licence/support costs, manual-effort savings, avoided APEX risk cost` |

---

## 7. Costs & Funding

> Figures to be confirmed with programme finance. All values below are placeholders.

| Cost category | Wave 1 / MVP | Notes |
|---|---|---|
| Build / delivery (team) | `[PLACEHOLDER]` | `[PLACEHOLDER: team size, blended day rate, duration]` |
| Cloud / infrastructure (Azure) | `[PLACEHOLDER]` | AKS, Key Vault, database, App Insights; UK South region |
| Licences / tooling | `[PLACEHOLDER]` | |
| UAT, accessibility & security assurance | `[PLACEHOLDER]` | |
| Contingency | `[PLACEHOLDER: % of total]` | |
| **Total MVP (wave 1)** | **`[PLACEHOLDER]`** | |
| Indicative whole-programme (waves 2+) | `[PLACEHOLDER]` | For context only; funded under subsequent cases |

**Funding source:** `[PLACEHOLDER: programme budget line / sponsor]`.
**Commercial route:** delivered by ScrumConnect as delivery partner under `[PLACEHOLDER: framework / contract vehicle]`.

---

## 8. Delivery Approach & Timeline

Delivery follows a phased build (Phase 0 foundations → Phases 1–8 domain services) then a per-jurisdiction cutover (Phase 9 — SSCS wave 1). Phase 0 doubles as a **platform smoke-test**, exercising the API, deployment and authorisation foundations before any domain service is built.

| Milestone | Target | Status |
|---|---|---|
| Phase 0 — Foundations (ingestion-first; reference data, auth, notification, CI/CD) | `[PLACEHOLDER]` | Planned — implementation-ready (readiness assessed 2026-06-17) |
| Phases 1–8 — Domain services build | `[PLACEHOLDER]` | Planned |
| Phase 9 — SSCS wave 1 cutover | `[PLACEHOLDER]` | Planned |
| Waves 2+ — Courts regions / APEX retirement | `[PLACEHOLDER]` | Future cases |

The Phase 0 implementation-readiness assessment (2026-06-17) returned **READY for sprint planning** with no critical issues, indicating the MVP is well-defined and de-risked at the requirements and architecture level.

---

## 9. Key Risks & Mitigations

| # | Risk | Likelihood / Impact | Mitigation |
|---|---|---|---|
| 1 | JOH eLinks API contract unconfirmed | Med / High | Build against a WireMock stub now; contract gates production cutover only. Tracked as the #1 external dependency. |
| 2 | Cross-region operations during partial Courts rollout | Med / Med | Documented manual coordination for the rollout window; resolves as regions migrate (waves 2+, not wave 1). |
| 3 | Federated read-model performance (Itinerary, Forward Look) | Med / Med | Strategy A federation at MVP; Strategy C cache fallback designed as contingency. |
| 4 | Behavioural-parity gaps vs incumbent | Med / Med | Manual UAT by incumbent-experienced users; sign-off is the wave gate. |
| 5 | Historical-data access at cutover | Low / Med | History remains in the incumbent (ListAssist/APEX); access policy is a separate, deferred decision. |
| 6 | Funding / resourcing certainty | `[PLACEHOLDER]` | `[PLACEHOLDER]` |

---

## 10. Assumptions & Dependencies

- Judiciary/HMCTS IdP (SSO) available for authentication; password/session/account lifecycle owned centrally, external to RAM Pathfinder.
- JOH eLinks API and MRD weekly feed available as the reference-data sources (no legacy migration).
- JFEPS / Liberata payment process unchanged; RAM generates the JFEPS-shaped Excel only.
- RAM Pathfinder serves the Tribunals/SSCS case-management system via APIs (RAM manages availability/scheduling, not case/hearing management/listing cases).
- HMCTS-approved technology stack confirmed (Azure UK South, Java 25 / Spring Boot 4, Kubernetes).
- Tribunals/SSCS as the chosen wave-1 jurisdiction.
- `[PLACEHOLDER: any procurement / commercial / security-accreditation dependencies]`.

---

## 11. Recommendation

Proceed with **Option C** and fund the **RAM Pathfinder MVP delivered as Tribunals/SSCS wave 1**. It is the only option that removes the unsupported-APEX risk over time, delivers the strategic API platform HMCTS programmes need, and contains delivery risk by proving the platform on a single, lower-risk jurisdiction before the wider Courts rollout.

**Decision requested from the Programme Board:**

1. Approve the MVP / SSCS wave-1 funding envelope of `[PLACEHOLDER]`.
2. Confirm the funding source and commercial route.
3. Endorse the phased, per-jurisdiction rollout strategy, with Courts waves 2+ funded under subsequent business cases.

---
