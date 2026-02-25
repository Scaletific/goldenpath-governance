---
id: ADR-0024-platform-security-floor-v1
title: 'ADR-0024: Security floor for V1'
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
  - 28_SECURITY_FLOOR_V1
  - 44_DOC_TIGHTENING_PLAN
  - ADR-0024-platform-security-floor-v1
  - SECURITY_POSTURE
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0024: Security floor for V1

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Security | Governance
- **Related:** docs/governance/GOV-0023-platform-governance.md, docs/60-security/22_CONTAINER_REGISTRY_STANDARD.md, docs/60-security/27_CI_IMAGE_SCANNING.md

---

## Context

We need a minimal, non-negotiable security baseline that reduces catastrophic risk without slowing
delivery. V1 must be secure-by-default and leave heavier DevSecOps capabilities to V2.

---

## Decision

> We will establish a V1 security floor with a small set of mandatory guardrails.

This floor is the minimum for platform and reference workloads; teams can exceed it.

---

## Scope

Applies to platform-owned and reference workloads in this repository. It does not mandate advanced
DevSecOps controls (SBOM signing, runtime agents) in V1.

---

## Consequences

### Positive

- Prevents high-risk mistakes without heavy process.
- Keeps delivery deterministic and low-friction.
- Creates a clear baseline for future DevSecOps layers.

### Tradeoffs / Risks

- Does not provide full compliance posture.
- Relies on CI and GitOps for enforcement.

### Operational impact

- Maintain the V1 checklist and keep it aligned with CI and governance.
- Document exceptions explicitly.

---

## Alternatives considered

- Full DevSecOps in V1 (rejected: too heavy for current delivery maturity).
- No explicit baseline (rejected: inconsistent and risky).

---

## Follow-ups

- Publish the V1 checklist in a living document.
- Add a governance reference to the V1 floor.

---

## Notes

V2 can introduce SBOMs, signing, and runtime security once delivery is stable.
