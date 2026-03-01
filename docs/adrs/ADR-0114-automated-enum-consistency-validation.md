---
id: ADR-0114-automated-enum-consistency-validation
title: Automated Enum Consistency Validation
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
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0113-platform-queryable-intelligence-enums
  - ADR-0114-automated-enum-consistency-validation
  - ADR-0115-enhanced-enum-validation-engine
  - CL-0070-automated-enum-consistency-validation
  - GOV-0048-federated-metadata-strategy
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-06
version: 1.0
date: 2026-01-06
breaking_change: false
---

## ADR-0114: Automated Enum Consistency Validation

## Context

With the introduction of unified enums in [ADR-0113](ADR-0113-platform-queryable-intelligence-enums.md), we need a mechanism to enforce these values across the repository. Manual review is insufficient for 300+ files, and existing validation scripts (`validate_metadata.py`) use hardcoded logic that is difficult to scale.

## Decision

We will implement a dedicated validation engine, `validate_enums.py`, that enforces metadata consistency against a centralized schema.

### 1. Technical Requirements

- **Schema-Driven**: The script must read `schemas/metadata/enums.yaml` as its source of truth.
- **Multi-Format Support**: Must parse both Markdown frontmatter and standalone YAML sidecars.
- **Recursive Scanning**: Must support multiple root directories (e.g., `docs`, `gitops`, `envs`) to ensure repo-wide compliance.
- **Fail-Fast**: Must return a non-zero exit code on drift, enabling its use as a CI/CD Quality Gate.

### 2. Validation Logic

- **Top-Level Fields**: Validates `status`, `type`, `domain`, and `owner`.
- **Nested Objects**: Validates `risk_profile` (impact, security, coupling) and `reliability` (observability_tier).
- **Direct Linkage**: Errors must include the file path and the list of allowed values to facilitate rapid developer remediation.

## Consequences

### Positive

- **Guaranteed Data Integrity**: Ensures that the Knowledge Graph is populated with valid, queryable states.
- **Reduced Technical Debt**: Prevents "Dark Enum Values" (e.g., typos or non-standard states) from entering the `main` branch.
- **Scalable Governance**: New domains or types can be added to `enums.yaml` without changing script logic.

### Negative

- **CI Dependency**: Minor increase in CI run time (scanning 300+ files).
- **Initial Friction**: Existing non-compliant files must be normalized to match the new enums.
