---
type: 'Epic'
description: 'User outcome: The shared Azure estate (AKS, PostgreSQL, ACR, APIM, App Insights, Key Vault) is stood up via Terraform in its own ram-shared-infrastructure repo per the HMCTS CNP standard, provisioned layer-by-layer with each layer independently verifiable…'
resource: 'epics/phase-0/epic-0.0-platform-estate-provisioned.html'
tags: [ram-pathfinder, epics, phase-0, infrastructure]
timestamp: '2026-07-06'
parent: 'epics/phase-0/index.md'
epic: 0.0
title: 'Platform estate is provisioned, verifiable, and CNP-compliant'
storyCount: 5
---

# Epic 0.0: Platform estate is provisioned, verifiable, and CNP-compliant

**User outcome:** The shared Azure estate — **AKS, a global PostgreSQL Flexible Server, Azure Container Registry, APIM, Application Insights / Log Analytics, and Key Vault** — is stood up via **Terraform** in its own dedicated repository, **`ram-shared-infrastructure`**, following the HMCTS Cloud Native Platform standard that product-level shared infrastructure lives in a `{product}-shared-infrastructure` repo (not colocated in a service repo). The estate is provisioned **layer-by-layer, and each layer is independently verifiable at deploy time** — so that every Phase 0 service (`ram-reference-data` first, then `ram-authorisation`, `ram-notification`, `ram-ui`) has a *tested* platform to deploy onto, and the team can prove the platform works before any domain service is scaffolded.

**Hosting:** the shared estate lives in **`ram-shared-infrastructure`** (CNP `{product}-shared-infrastructure` convention). This **supersedes AR53's colocated first-consumer rule** — the shared estate is no longer carried inside `ram-reference-data/terraform/`. Each service repo's own `terraform/` continues to hold **only that service's own resources** (e.g. the MRD storage account in `ram-reference-data`, Story 0.1.4).

**Why this is Epic 0.0 (precedes ingestion):** the shared cluster/database/registry/gateway/observability were always an implicit prerequisite of Story 0.1.1. Making them a first-class, independently-tested epic (a) aligns RAM with the CNP `-shared-infrastructure` standard, (b) lets the estate be validated on its own before a service depends on it, and (c) tightens `ram-reference-data` down to its domain — consistent with the polyrepo "minimise shared coupling" principle. The integrations-first ordering of the **domain** deliverables (0.1 → 0.5) is unchanged.

**Vertical slice:**
- **New dedicated repo `ram-shared-infrastructure`** (CNP naming), scaffolded per the manual GitHub web-UI setup runbook (`ram-architecture/runbooks/github-setup.md` — the `gh` CLI is not available)
- **Terraform-only** provisioning (no Bicep, no portal click-ops), remote state backend, per-environment stacks (`dev` / `staging` / `production`)
- Shared estate: **AKS** (UK South, multi-AZ) → **PostgreSQL Flexible Server** (zone-redundant HA) + **Key Vault** → **ACR** + **App Insights / Log Analytics** → **APIM**
- Each layer carries its own **deploy-time acceptance test** so infrastructure is verified as it lands, not assumed

**FRs covered:** none — this is foundational platform infrastructure with no functional-requirement surface. It is the enablement layer for every Phase 0 FR.

**Key NFRs first exercised here:** NFR10 (TLS at APIM), NFR11 (data-at-rest), NFR16 (Key Vault), NFR25–NFR28 (structured logs + Application Insights ingestion + liveness/readiness plumbing), NFR31 (Azure UK South data residency), NFR40 (per-service deployable on Kubernetes — the cluster it deploys to).

**Architecture requirements:** **AR53 (revised — dedicated `ram-shared-infrastructure` per CNP)**; A34 (zone-redundant SKUs); gaps.md G9 (Terraform state backend + plan/apply pipeline pattern).

**Out of scope (explicitly):** any domain service scaffolding (`ram-reference-data` — Epic 0.1, Story 0.1.1); any service's own per-repo `terraform/` resources (they stay in their service repos); production-region rollout gating (Phase 9+); the `ram_configuration_values` Liquibase baseline (owned by `ram-architecture`, lands ahead of Epic 0.1).

---

## Story 0.0.1: Scaffold `ram-shared-infrastructure` and establish the Terraform foundation

As a **platform engineer**,
I want the dedicated **`ram-shared-infrastructure`** repo scaffolded per the HMCTS CNP standard, with a working Terraform backend, per-environment stacks, and a plan/apply CI pipeline,
So that **the shared estate has a CNP-compliant home with safe, reviewable, state-backed change management before any resource is provisioned**.

**Acceptance Criteria:**

**Given** the engineer has performed the GitHub manual-setup checklist (`ram-architecture/runbooks/github-setup.md`) **before** scaffolding:
  - Created the repo **`ram-shared-infrastructure`** under the HMCTS org **via the GitHub web UI** (name follows the CNP `{product}-shared-infrastructure` convention — `product` = `ram`),
  - Enabled branch protection on `main` (require PR review, require status checks, require linear history),
  - Configured `CODEOWNERS` scoped to the platform/infra team,
  - Note: the `gh` CLI is **NOT** available — all GitHub admin config happens manually via the web UI per the runbook,
**When** the engineer lays down the Terraform skeleton,
**Then** the repo contains per-environment stacks `terraform/dev/`, `terraform/staging/`, `terraform/production/` with pinned provider versions (`azurerm`),
**And** a remote state backend is configured (Azure Storage account + container, per the HMCTS-confirmed pattern — gaps.md G9),
**And** `.github/workflows/ci.yml` runs `terraform fmt -check`, `terraform validate`, and `terraform plan` on every PR,
**And** a gated `apply` workflow runs only on merge to `main`, per environment, with manual approval for staging/production,
**And** `CODEOWNERS` and `PULL_REQUEST_TEMPLATE.md` (infra-change checklist) exist.

**Given** the Terraform skeleton is in place with no resources yet defined,
**When** the engineer opens a PR,
**Then** `terraform validate` passes and `terraform plan` renders a clean, empty (no-op) plan in CI,
**And** on merge, a no-op `apply` against the dev stack succeeds and writes state to the remote backend,
**And** the run is observable in the CI logs with the plan output attached to the PR.

**References:** AR53 (revised); gaps.md G9; D10 (`gh` CLI not available — manual GitHub web-UI setup).

**Explicitly NOT in scope:**
- Any actual Azure resources — Stories 0.0.2–0.0.5
- Any service repo scaffolding — Epic 0.1

---

## Story 0.0.2: Provision networking and the AKS cluster (dev), verifiable via kubectl

As a **platform engineer**,
I want the resource group, virtual network, and AKS cluster provisioned in UK South via Terraform,
So that **there is a verified Kubernetes target — zone-spread and reachable — for every RAM Pathfinder service to deploy onto**.

**Acceptance Criteria:**

**Given** the Terraform foundation exists per Story 0.0.1,
**When** the engineer adds the networking + AKS module and runs `terraform apply` for the dev stack,
**Then** a resource group, VNet, and subnets are created in **UK South** (per NFR31),
**And** an AKS cluster is provisioned with a **multi-AZ node pool** and zone-spread configuration (per NFR31, A34),
**And** cluster and node SKUs match the documented Phase 0 baseline,
**And** the kubeconfig is retrievable by authorised engineers via Azure RBAC (no cluster-admin static credentials committed).

**Given** the AKS cluster is provisioned,
**When** the engineer runs `kubectl get nodes`,
**Then** all nodes report `Ready` and are distributed across availability zones,
**And** a throwaway `hello`/echo pod (e.g. `kubectl run`) schedules successfully and responds to an in-cluster request,
**And** the smoke check is captured as a documented post-apply verification step (runnable in CI or by hand) — infrastructure is verified as deployed.

**References:** AR53 (revised); NFR31, NFR40; A34.

**Explicitly NOT in scope:**
- PostgreSQL, Key Vault, ACR, App Insights, APIM — Stories 0.0.3–0.0.5
- Deploying any RAM service — Epic 0.1

---

## Story 0.0.3: Provision PostgreSQL and Key Vault (dev), verifiable over TLS from the cluster

As a **platform engineer**,
I want a PostgreSQL Flexible Server and a Key Vault provisioned via Terraform, with AKS workload identity wired to the vault,
So that **services have an encrypted, TLS-only shared database and a secret store — proven reachable and secure from inside the cluster before any service needs them**.

**Acceptance Criteria:**

**Given** the AKS cluster exists per Story 0.0.2,
**When** the engineer adds the PostgreSQL + Key Vault module and runs `terraform apply` for dev,
**Then** an Azure Database for **PostgreSQL Flexible Server** is provisioned with **zone-redundant HA** (per A34), **storage encryption at rest** (per NFR11), and **TLS enforced / plaintext connections refused** (per NFR10),
**And** an **Azure Key Vault** is provisioned with soft-delete + purge protection,
**And** AKS **workload identity** is configured so pods can read Key Vault secrets without static credentials (per NFR16),
**And** no database or vault secrets are committed to the repo — all live in Key Vault.

**Given** PostgreSQL and Key Vault are provisioned,
**When** the engineer runs the verification from an in-cluster pod,
**Then** a TLS connection to PostgreSQL succeeds and a **non-TLS connection is refused** (NFR10 verified as deployed),
**And** a scratch database can be created and dropped (connectivity + privilege baseline confirmed),
**And** a test secret written to Key Vault round-trips back to the pod via workload identity (NFR16 verified),
**And** these checks are captured as documented post-apply verification steps.

**References:** AR53 (revised); NFR10, NFR11, NFR16; A34.

**Explicitly NOT in scope:**
- Per-service DB roles/grants and the `ram_configuration_values` baseline (owned by `ram-architecture`; consumed in Epic 0.1)
- ACR, App Insights, APIM — Stories 0.0.4–0.0.5

---

## Story 0.0.4: Provision ACR and observability (dev), verifiable via image pull and a test trace

As a **platform engineer**,
I want an Azure Container Registry and an Application Insights / Log Analytics workspace provisioned via Terraform and wired to AKS,
So that **there is a proven image supply chain and a proven telemetry sink before any service ships a container or emits a log**.

**Acceptance Criteria:**

**Given** the AKS cluster exists per Story 0.0.2,
**When** the engineer adds the ACR + observability module and runs `terraform apply` for dev,
**Then** an **Azure Container Registry** is provisioned (zone-redundant SKU per A34) with AKS granted pull access via managed identity (no registry passwords in cluster),
**And** an **Application Insights** resource backed by a **Log Analytics workspace** is provisioned in UK South,
**And** log retention is set to the agreed Phase 0 default (**90 days non-prod**, subject to HMCTS sign-off; per NFR26) via Terraform,
**And** the App Insights connection string is stored in Key Vault (not committed).

**Given** ACR and observability are provisioned,
**When** the engineer runs the verification,
**Then** a test image pushes to ACR and pulls successfully into AKS (supply chain confirmed),
**And** a test trace and a structured log entry emitted from an in-cluster pod appear in Application Insights within the query window (NFR25–NFR28 telemetry pipeline verified as deployed),
**And** these checks are captured as documented post-apply verification steps.

**References:** AR53 (revised); NFR25, NFR26, NFR27, NFR28; A34.

**Explicitly NOT in scope:**
- Per-service log dashboards / alerts (land with each service)
- APIM — Story 0.0.5

---

## Story 0.0.5: Provision APIM (dev), verifiable end-to-end via a smoke API over TLS

As a **platform engineer**,
I want APIM provisioned via Terraform with base policies and a smoke API,
So that **the shared public gateway is proven to terminate TLS and route to the cluster before any real service publishes an API through it**.

**Acceptance Criteria:**

**Given** the AKS cluster exists per Story 0.0.2,
**When** the engineer adds the APIM module and runs `terraform apply` for dev,
**Then** an **APIM instance** is provisioned (zone-redundant SKU per A34) with base policies (TLS termination at the latest platform-supported version — NFR10; correlation-ID pass-through; default rate limits),
**And** a **smoke API** is registered pointing at an in-cluster echo service,
**And** HTTP-only requests are rejected/redirected to HTTPS.

**Given** APIM and the smoke API are provisioned,
**When** the engineer calls the smoke operation through the APIM gateway,
**Then** the call returns `200` over TLS from the in-cluster echo service (end-to-end path gateway → AKS confirmed),
**And** a request below the platform's minimum TLS version is refused (verified by a CI check using `testssl.sh` or equivalent — NFR10 verified as deployed),
**And** an unauthenticated call to a policy-protected route is rejected,
**And** these checks are captured as documented post-apply verification steps.

**Given** all five layers are applied,
**When** the engineer reviews the dev estate,
**Then** the full shared estate (AKS + PostgreSQL + Key Vault + ACR + App Insights + APIM) exists in UK South, each layer independently verified,
**And** the estate is ready for `ram-reference-data` to scaffold and deploy onto (Epic 0.1, Story 0.1.1).

**References:** AR53 (revised); NFR10, NFR31; A34; gaps.md G9.

**Explicitly NOT in scope:**
- Per-service API registration in APIM (each service publishes its own OpenAPI-backed API)
- Any domain service — Epic 0.1 onward

[^d3]: Revised D3 (2026-06-10) — no data migration from any legacy system; judicial-holder reference data is ingested from the JOH eLinks API and MRD.
[^d8]: D8 — rollout is jurisdiction-first, then per-region; jurisdiction is a first-class hierarchical attribute.
[^d10]: D10 (2026-05-15) — admin UI is post-MVP; MVP admin operations are DBA-via-SQL per operational runbooks.
