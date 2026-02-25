---
id: ADR-0065-platform-branch-policy-guard
title: 'ADR-0065: Restore branch policy guard for main'
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
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0065-platform-branch-policy-guard
  - CL-0015-branch-policy-guard-restore
  - GOV-0030-pr-guardrails-index
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0065: Restore branch policy guard for main

- **Status:** Proposed
- **Date:** 2026-01-02
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `.github/workflows/branch-policy.yml`, PR #104

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

We require a consistent release path that flows through the development branch
before reaching main. Recent changes temporarily relaxed the branch policy guard,
allowing non-development branches to merge directly into main. This increases
risk by bypassing the expected review and integration pathway.

## Decision

We will **restore the branch policy guard** so that only `development` may merge
into `main`.

## Scope

Applies to pull requests targeting `main`. Pull requests targeting other branches
remain unaffected.

## Consequences

### Positive

- Enforces a single, predictable promotion path to main.
- Reduces the chance of bypassing required checks and review flow.

### Tradeoffs / Risks

- Hotfixes must be routed through development or explicitly handled via an
  approved override process.

### Operational impact

- Contributors must open PRs to `development` first, then promote to `main`.

## Alternatives considered

- Allowlist specific branches (rejected to keep policy simple and consistent).
- Disable the guard entirely (rejected due to release risk).

## Follow-ups

- Ensure documentation explains the development-to-main flow.

## Notes

This decision intentionally prioritizes consistency over ad-hoc merges.
