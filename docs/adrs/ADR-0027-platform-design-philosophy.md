---
id: ADR-0027-platform-design-philosophy
title: 'ADR-0027: Platform design philosophy and reference implementation'
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
  - 00_DESIGN_PHILOSOPHY
  - 00_DOC_INDEX
  - GOV-0023-platform-governance
  - 01_adr_index
  - 02_PLATFORM_BOUNDARIES
  - ADR-0027-platform-design-philosophy
  - CAPABILITY_LEDGER
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0027: Platform design philosophy and reference implementation

Filename: `ADR-0027-platform-design-philosophy.md`

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `docs/00-foundations/00_DESIGN_PHILOSOPHY.md`, `docs/90-doc-system/00_DOC_INDEX.md`, `docs/governance/GOV-0023-platform-governance.md`, `docs/20-contracts/02_PLATFORM_BOUNDARIES.md`

---

## Context

GoldenPath is intended to be operable without a single maintainer and usable by
humans and machines. That requires durable, explicit documentation and a clear
statement of the platform’s founding principles. Without a named philosophy,
teams risk duplicating rules, drifting from the original model, or treating the
platform itself as a special case.

## Decision

We will preserve the platform’s origin philosophy as a first-class, living
document and treat the platform as the reference implementation for how
workloads are built and delivered.

Specifically:

- The platform uses the same delivery rails it provides to teams.
- The design philosophy document is the canonical expression of these principles.
- Core living docs are indexed and reviewed on a defined cadence.

## Scope

Applies to platform governance, platform-owned workloads, and all living
documents listed in `docs/90-doc-system/00_DOC_INDEX.md`.

Does not mandate that product teams adopt identical tooling, but it defines the
baseline experience and reference behavior they can expect.

## Consequences

### Positive

- Documentation remains credible and auditable over time.
- The platform does not ask teams to follow patterns it does not use itself.
- Machine-readable doc metadata enables future automation and AI assistants.

### Tradeoffs / Risks

- Requires discipline to review and update living docs.
- Adds light metadata overhead for core documents.

### Operational impact

- Owners must review living docs on their cadence.
- Doc freshness validation can be added to CI as warning or gate.

## Alternatives considered

- **Implicit philosophy with no formal doc:** rejected due to drift risk.
- **Heavy compliance process for all docs:** rejected as too expensive for V1.
- **Only ADRs (no living docs):** rejected because ADRs are not operational docs.

## Follow-ups

- Maintain `docs/90-doc-system/00_DOC_INDEX.md` as the canonical list of living docs.
- Use `scripts/check-doc-freshness.py` to monitor review cadence.
- Add a TODO to test the mechanism before enforcing it.

## Notes

This ADR preserves the “GoldenPath is built using GoldenPath” principle while
keeping documentation operable at scale.
