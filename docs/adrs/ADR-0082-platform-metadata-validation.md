---
id: ADR-0082-platform-metadata-validation
title: Platform Metadata Validation Strategy
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
  - ADR-0066-platform-dashboards-as-code
  - ADR-0082-platform-metadata-validation
  - ADR-0083-platform-metadata-backfill-protocol
  - ADR-0084-platform-enhanced-metadata-schema
  - ADR-0088-automated-metadata-remediation
  - ADR-0136
  - CL-0037-metadata-schema
  - CL-0042-metadata-backfill-batch-1
  - CL-0043-complete-metadata-backfill
  - METADATA_BACKFILL_RUNBOOK
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-01
version: '1.0'
breaking_change: false
---

## ADR-0082: Platform Metadata Validation Strategy

## Context

As the Golden Path IDP scales, we are introducing a "Knowledge Graph" approach to link artifacts (Code, Docs, Decisions). We need a way to enforce the integrity of these links.

## Options Considered

1. **Generic Linters (SuperLinter / Yamllint):** Good for syntax, bad for logic.
2. **Custom Script (`validate_metadata.py`):** Can check business logic and referential integrity.

## Comparison

| Feature | Generic Linter (Yamllint) | Custom Validator (`validate_metadata.py`) |
| :--- | :--- | :--- |
| **Check Type** | Syntax (Formatting) | Semantics (Meaning) |
| **Validation** | "Is this valid YAML?" | "Is this a valid Owner?" |
| **Integrity** | None | Checks if linked ADRs actually exist |
| **Custom Rules** | Limited | Infinite (Python logic) |
| **Maintenance** | Low (Off the shelf) | Medium (Owned code) |

## Decision

We will implement **BOTH**, but rely on the **Custom Validator** for the "Green Gate".
We choose to write and maintain `scripts/validate_metadata.py`.

## Consequences

- **Positive:** Guaranteed referential integrity. No "Dead Links" in our graph.
- **Negative:** We must maintain the python script.
