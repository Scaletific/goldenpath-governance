---
id: ADR-0086-federated-metadata-validation
title: 'ADR-0086: Federated Metadata Validation Strategy'
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
  - ADR-0086-federated-metadata-validation
  - CL-0045-federated-governance-onboarding
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
dependencies:
  - module:github-actions
  - module:pre-commit
breaking_change: false
---

# ADR-0086: Federated Metadata Validation Strategy

## Context
Our current metadata compliance engine (`validate_metadata.py`) is locked within the `goldenpath-idp-infra` repository. As the platform scales, new application repositories (workloads) are being created without consistent metadata, leading to gaps in the IDP Knowledge Graph and inaccurate Health Reports.

## Decision
We will decentralize the **execution** of metadata validation while centralizing the **definition** of the policy.

1.  **Shared Action**: Extract `validate_metadata.py` into a standalone GitHub Action repo.
2.  **Global pre-commit**: Mandate the inclusion of this hook in all "Golden Templates."
3.  **Soft-fail Grace Period**: Initially implement as a warning (non-blocking) for 30 days before moving to hard-fail PR blocking.

## Consequences
- **Positive**: 100% visibility into all workload ownership and risk profiles across the org.
- **Negative**: Adds a mandatory check to developer workflows; may cause friction if metadata requirements are too complex.
- **Neutral**: Requires a centralized "Governance Registry" to manage allowed owners/categories.
