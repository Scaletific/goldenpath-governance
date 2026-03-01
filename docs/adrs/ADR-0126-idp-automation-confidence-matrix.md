---
id: ADR-0126
title: 'ADR-0126: IDP Automation Confidence Matrix (Five-Star Approval)'
type: adr
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
  - ADR-0126
  - ADR-0146
  - CL-0083-automation-confidence-matrix
  - CL-0116
  - CL-0117
  - GOV-0054-script-certification-audit
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

## ADR-0126: IDP Automation Confidence Matrix

## Status

Accepted

## Context

As the GoldenPath IDP moves at high velocity, the accumulation of "Dark History" (undocumented/untested scripts) and brittle automation poses a risk to platform stability. We need a rigorous, multi-dimensional framework to certify the maturity of our automation before it is promoted to core production usage.

## Decision

We officially adopt the **IDP Automation Confidence Matrix** as the standard for certifying all scripts and workflows. Approval is based on five "Surface Areas" of certification:

1. **Logic Integrity**: Verified via unit tests, linting, and graceful error handling.
2. **Operational Safety**: Verified via Idempotency and explicit Dry-Run support.
3. **Governance Context**: Verified via ADR/CL traceability and VQ classification.
4. **Interface Legibility**: Verified via `--help` documentation and clear logging.
5. **System Integration**: Verified via CI/CD gating and multi-environment parity.

### Maturity Ratings

Scripts will be assigned a **Confidence Rating** (1-5 stars) based on these areas:

- **(1 Star)**: Lint-clean only.
- **(2 Stars)**: Documented and Owned.
- **(3 Stars)**: Tested and Safe (Idempotency + Dry-run).
- **(4 Stars)**: Field-Tested (Field verification record).
- **(5 Stars)**: Immutable Core (Full observability + Multi-env parity).

## Consequences

- **Positive**: Eliminates script brittleness and improves predictability.
- **Positive**: Provides a clear roadmap for maturing "experimental" scripts into "core" utilities.
- **Positive**: Improves operator confidence through transparent "Confidence Ratings" in the health dashboard.
- **Negative**: Adds overhead to the script promotion process (balanced by the VQ of self-healing automation).
