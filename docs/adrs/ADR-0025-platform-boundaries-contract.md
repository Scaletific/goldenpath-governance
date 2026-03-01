---
id: ADR-0025-platform-boundaries-contract
title: 'ADR-0025: Platform boundaries and contract'
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
  - 44_DOC_TIGHTENING_PLAN
  - ADR-0025-platform-boundaries-contract
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0025: Platform boundaries and contract

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Governance | Operations
- **Related:** docs/20-contracts/02_PLATFORM_BOUNDARIES.md, docs/governance/GOV-0023-platform-governance.md, docs/onboarding/23_NEW_JOINERS.md

---

## Context

The platform and workload planes must be separated explicitly to avoid duplicate governance and
confusion. A clear contract defines what the platform guarantees and what teams own.

---

## Decision

> We will maintain a single platform boundary contract and keep it referenced from governance and
> onboarding docs.

---

## Scope

Applies to platform governance, onboarding, and the delivery contract between platform and teams.

---

## Consequences

### Positive

- Clear ownership boundaries and reduced ambiguity.
- Governance becomes easier to apply without blocking teams.

### Tradeoffs / Risks

- Requires ongoing documentation upkeep to prevent drift.

### Operational impact

- Keep the boundary document current.
- Reference it in governance and onboarding.

---

## Alternatives considered

- Implicit boundaries (rejected: leads to confusion and inconsistent expectations).
- Multiple boundary documents (rejected: duplication and drift).

---

## Follow-ups

- Update links in docs when the boundary contract changes.

---

## Notes
