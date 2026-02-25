---
id: ADR-0115-enhanced-enum-validation-engine
title: Enhanced Enum Validation Engine
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
  - 2026-01-06_2145_queryable-intelligence-validation
  - ADR-0114-automated-enum-consistency-validation
  - ADR-0115-enhanced-enum-validation-engine
  - CL-0071-enhanced-enum-validation-engine
  - IDP_PRODUCT_FEATURES
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-06
version: 1.0
date: 2026-01-06
breaking_change: false
---

## ADR-0115: Enhanced Enum Validation Engine

## Context

ADR-0114 introduced the `validate_enums.py` script to enforce metadata consistency. However, the initial implementation relied on flat field matching, making it difficult to validate nested objects like `risk_profile.security_risk` or `reliability.observability_tier`.

## Decision

We will upgrade the `validate_enums.py` engine to use recursive dot-path traversal and a flexible mapping architecture.

### 1. Dot-Path Traversal

The script will implement a `get_dot(dict, "a.b.c")` utility to reach into nested YAML structures. This allows us to validate the platform's full schema without flattening the metadata files.

### 2. Flexible Mapping

Instead of hardcoding "if status check X", the script uses a `checks` mapping list:

- **Scope**: (file_kind, field_path, allowed_enum_list)
- **Extensibility**: New validation rules can be added by declaring a new mapping in the central list.

### 3. CI/CD Integration

The script is designed for "Changed Files Only" validation. By accepting positional file arguments, it can be seamlessly embedded into GitHub Actions and pre-commit hooks to provide fast feedback during development.

## Consequences

### Positive

- **Deep Validation**: Prevents drift in nested reliability and risk fields.
- **Improved Performance**: Allows CI to validate only what changed rather than scanning the entire repo.
- **Maintainability**: Centralized mapping logic makes the script easier to update as the metadata schema evolves.

### Negative

- **Validation Strictness**: Deep validation may reveal more legacy drift that requires remediation.
