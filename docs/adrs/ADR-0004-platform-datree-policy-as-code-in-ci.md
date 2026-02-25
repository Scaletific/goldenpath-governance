---
id: ADR-0004-platform-datree-policy-as-code-in-ci
title: 'ADR-0004: Use Datree as Kubernetes policy-as-code gate in CI'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0004-platform-datree-policy-as-code-in-ci
  - HELM_DATREE
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0004: Use Datree as Kubernetes policy-as-code gate in CI

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Governance / Quality / Security
- **Related docs:** compliance/datree/, docs/governance/GOV-0023-platform-governance.md, docs/06_REBUILD_SEQUENCE.md

## Context

We need governance that is opinionated but not authoritarian:

- catch common Kubernetes misconfigurations early
- prevent obvious policy violations from reaching GitOps
- keep enforcement lightweight for V1

We also want policies versioned alongside platform code.

## Decision

Adopt **Datree** as a **CI policy gate** for Kubernetes manifests/Helm-rendered output.

- Policies live in `compliance/datree/` and are version-controlled.
- CI runs Datree checks before changes are merged / before GitOps reconciliation.

## Scope

- Applies to: platform manifests and workloads that are deployed via GitOps.
- Out of scope (for V1): full runtime admission enforcement (Kyverno/Gatekeeper) as mandatory.

## Consequences

### Positive

- Fast feedback and low operational overhead.
- Policies are explicit, reviewable, and evolve with the platform.
- Keeps GitOps clean by blocking obviously invalid/non-compliant manifests.

### Negative / Tradeoffs

- CI-only enforcement means a determined actor could bypass via direct cluster access (mitigated by RBAC and GitOps discipline).
- Helm rendering context can differ per env; CI must render with correct values/overlays to be meaningful.
- Overly strict policies can slow iteration if not tuned.

### Operational implications

- CI must define what it checks:

- rendered Helm output per env OR baseline render + env deltas

- Governance doc must define:

- which rules are **blocking** vs **advisory**

- exception process (time-boxed, documented)

## Alternatives considered

- **No policy gate**: rejected (drift and foot-guns become inevitable).
- **Runtime admission first (Kyverno/Gatekeeper)**: deferred to later maturity; higher complexity early.
- **OPA Conftest only**: possible, but Datree offers quick value for common K8s guardrails.

## Follow-ups / Actions

- Define the initial “blocking” policy set (minimal and high-signal).
- Add CI job to run Datree on:

- `gitops/kustomize/overlays/<env>`

- Helm renders for core tooling values (as applicable)

- Document an exceptions workflow for urgent changes.
