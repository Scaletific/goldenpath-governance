---
id: ADR-0033-platform-ci-orchestrated-modes
title: 'ADR-0033: CI orchestrated modes for infra lifecycle'
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
  - ADR-0033-platform-ci-orchestrated-modes
  - ADR-0168
  - HELM_DATREE
  - RB-0019-relationship-extraction-script
  - RELATIONSHIP_EXTRACTION_GUIDE
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0033: CI orchestrated modes for infra lifecycle

- **Status:** Accepted
- **Date:** 2025-12-28
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Operations | Delivery
- **Related:** docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, .github/workflows/ci-bootstrap.yml

---

## Context

The infra lifecycle requires multiple phases (apply, bootstrap, teardown). When
operators must manually toggle flags, the workflow becomes brittle and error-prone.
We saw repeated failures caused by applying when we only needed bootstrap, or
reusing build IDs in the wrong phase.

We need a clear, enforceable model that reduces human error while keeping the
process flexible for V1.

## Decision

We will use **explicit CI modes** for the infra lifecycle:

1) **build + bootstrap** (default)
2) **bootstrap-only** (skip apply, reuse existing cluster/build)
3) **teardown**

Each mode enforces the correct phase ordering and input expectations.

## Scope

Applies to:

- CI bootstrap workflow
- Infra lifecycle runs in dev/test/staging/prod

Does not apply to:

- Ad-hoc local runs (allowed but not the default path)

## Consequences

### Positive

- Reduces human error by encoding intent in workflow inputs.
- Prevents accidental apply when only bootstrap is needed.
- Makes infra runs more repeatable and auditable.

### Tradeoffs / Risks

- Adds workflow complexity (more inputs).
- Requires documentation so operators choose the right mode.

### Operational impact

- Operators must select the correct mode at dispatch time.
- Build ID reuse is allowed for bootstrap-only, not for apply.

## Alternatives considered

- **Single workflow with manual flags only:** rejected due to error-prone runs.
- **Separate workflows for each phase:** rejected to avoid fragmentation.

## Follow-ups

- Document mode behavior in the CI environment contract.
- Consider a single orchestrator workflow once CI stabilizes.

## Notes

Accepted for V1 with openness to refine mode enforcement as CI matures.
