---
id: ADR-0123
title: 'ADR-0123: Delivery Automation Suite (ECR & Logs)'
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
  - ADR-0123
  - CL-0079
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

## ADR-0123: Delivery Automation Suite (ECR & Logs)

## Status

Accepted (Backfill)

## Context

The GoldenPath IDP requires a standardized set of utilities to handle ECR registry provisioning and build/teardown telemetry. These utilities were developed early in the project but lacked formal architectural records.

## Decision

We officially adopt the following scripts as the core Delivery Automation Suite:

1. **`scaffold_ecr.py`**: Handles standardized ECR repository creation with baseline policies.
2. **`ecr-build-push.sh`**: The primary wrapper for ECR authentication and image delivery.
3. **`generate-build-log.sh` / `generate-teardown-log.sh`**: Standardizes telemetry capture for build and destruction phases.
4. **`resolve-cluster-name.sh`**: Provides deterministic cluster naming across environments.

## Consequences

- **Positive**: Consistent ECR configuration across all services.
- **Positive**: Uniform logs for CI auditability.
- **Positive**: Automated ECR lifecycle management.
- **Negative**: Adds shell dependencies for logging scripts.
