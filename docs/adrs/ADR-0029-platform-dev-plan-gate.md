---
id: ADR-0029-platform-dev-plan-gate
title: 'ADR-0029: Dev plan gate before dev apply'
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
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0028-platform-dev-branch-gate
  - ADR-0029-platform-dev-plan-gate
  - RB-0010-dev-branch-apply
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0029: Dev plan gate before dev apply

Filename: `ADR-0029-platform-dev-plan-gate.md`

- **Status:** Accepted
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Delivery
- **Related:** `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`, `docs/adrs/ADR-0028-platform-dev-branch-gate.md`

---

## Context

The dev apply workflow currently checks for any successful plan on the same SHA.
Because the plan workflow supports multiple environments, a non-dev plan can
unlock a dev apply. This weakens the dev gate and allows apply without a dev
plan.

## Decision

Dev apply must only proceed after a **dev plan** has succeeded on the same SHA.
Plans for other environments do not satisfy the gate.

## Scope

Applies to dev apply in CI. This does not change non-dev plan behavior.

## Consequences

### Positive

- Dev apply is always preceded by a dev plan.
- The dev gate accurately reflects the dev backend/state.

### Tradeoffs / Risks

- Requires explicit validation of plan context.

### Operational impact

- The apply workflow must validate the plan environment.

## Alternatives considered

- **Any plan is sufficient:** rejected due to incorrect gating.
- **Disable non-dev plans:** rejected because we still want visibility.

## Diagram

```text
Current (problem):
+---------+     plan (any env)     +----------+
|  Commit (SHA)    |  --------->  |  Plan Success?     |
+---------+                        +----------+
                                               |
                                               | (no env check)
                                               v
                                        +---------+
                                        | Apply DEV        |
                                        | (allowed)        |
                                        +---------+

Risk: a plan for staging/prod can unlock dev apply.

------------------------------

Recommended (fix):
+---------+     plan (DEV only)    +----------+
|  Commit (SHA)    |  --------->  | Plan Success?      |
+---------+                        | env == dev        |
                                            +----------+
                                               |
                                               | only if dev plan
                                               v
                                        +---------+
                                        | Apply DEV        |
                                        | (allowed)        |
                                        +---------+
```

## Follow-ups

- Enforce env-specific plan validation in the apply workflow.
