---
id: ADR-0067-platform-labeler-base-ref
title: 'ADR-0067: Use base ref for labeler checkout'
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
  - ADR-0067-platform-labeler-base-ref
  - CL-0016-labeler-base-ref-checkout
  - RB-0019-relationship-extraction-script
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0067: Use base ref for labeler checkout

- **Status:** Proposed
- **Date:** 2026-01-02
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `.github/workflows/pr-labeler.yml`, PR #107

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

The PR labeler workflow checked out the base commit SHA. When the base SHA
pointed to an older labeler config, the v5 labeler action failed due to config
schema drift. This blocked PRs even when the current base branch config was
valid.

## Decision

We will **checkout the base ref** (branch) for the labeler workflow instead of a
specific base SHA.

## Scope

Applies only to the PR labeler workflow checkout behavior.

## Consequences

### Positive

- Labeler uses the latest base branch config and avoids stale schema failures.

### Tradeoffs / Risks

- Labeler may use config updates that were not present at the PR base SHA.

### Operational impact

- None.

## Alternatives considered

- Keep base SHA checkout and tolerate occasional labeler failures (rejected).

## Follow-ups

- None.

## Notes

This decision prioritizes stable labeling over strict historical config fidelity.
