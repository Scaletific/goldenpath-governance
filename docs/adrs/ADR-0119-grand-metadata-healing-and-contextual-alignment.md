---
id: ADR-0119-grand-metadata-healing-and-contextual-alignment
title: 'ADR-0119: Grand Metadata Healing & Contextual Alignment'
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
  observability_tier: bronze
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0113-platform-queryable-intelligence-enums
  - ADR-0118-config-driven-metadata-governance
  - ADR-0119-grand-metadata-healing-and-contextual-alignment
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

## ADR-0119: Grand Metadata Healing & Contextual Alignment

## Status

Accepted

## Context

As the Golden Path IDP scales, we have transitioned to a config-driven metadata model (ADR-0118). However, a repository-wide audit revealed over 475 instances of "Governance Debt," where legacy records use placeholder values (`unknown`, `none`) or generic types (`documentation`) that no longer satisfy our queryable intelligence requirements (ADR-0113).

Manual remediation of 500+ files is unsustainable and prone to human error.

## Decision

We will implement an **Automated Contextual Mapping** engine within `standardize_metadata.py` (The Healer) to perform a one-time "Grand Healing" pass.

The engine will:

1. **Infer Categories**: Map `category: unknown` to canonical enums based on directory structure (e.g., `gitops/` -> `delivery`, `idp-tooling/` -> `platform`).
2. **Resolve Functional Types**: Upgrade generic `type: documentation` to precise types (`runbook`, `adr`, `contract`) inferred from the source path.
owner: platform-team3.  **Enforce Minimum Reliability**: Force legacy `observability_tier: none` to the platform's mandatory baseline of `bronze`.
3. **Preserve Intent**: Only placeholder values will be overwritten; explicit metadata provided by authors will remain untouched unless it violates schema bounds.

## Consequences

### Positive

* **Zero-Effort Compliance**: 100% of the repository is brought into alignment with the `enums.yaml` policy without manual labor.
* **High-Integrity Reporting**: The platform health dashboard will no longer report "Dark Infrastructure" due to placeholder values.
* **Architectural Consistency**: Metadata becomes a reliable source of truth for the IDP Knowledge Graph.

### Tradeoffs

* **Bulk Changes**: A single PR will modify ~500 files, requiring careful review of the mapping logic.
* **Inferred Truth**: Automated mapping based on path is highly accurate (>95%) but may require minor manual adjustments for edge-case files.
