---
id: ADR-0113-platform-queryable-intelligence-enums
title: Platform Queryable Intelligence Enums
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - 2026-01-06_2145_queryable-intelligence-validation
  - ADR-0084-platform-enhanced-metadata-schema
  - ADR-0113-platform-queryable-intelligence-enums
  - ADR-0114-automated-enum-consistency-validation
  - ADR-0119-grand-metadata-healing-and-contextual-alignment
  - ADR-0131
  - CL-0069-platform-queryable-intelligence-enums
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

## ADR-0113: Platform Queryable Intelligence Enums

## Context

The GoldenPath IDP relies on metadata sidecars to drive automated governance, health reporting, and Knowledge Graph traversal. However, drift has been identified in the values used for key fields (Status, Risk, Type), leading to "Micro-Gaps" in query integrity. We need a unified set of enums that serve as the foundation of the platform's Queryable Intelligence.

## Decision

We will standardize the following enums across all platform layers (Validation, Reporting, Scaffolding, and UI).

### 1. Unified Enums

#### **Risk Profile (`risk_profile.production_impact`)**

- `none`: No impact to production workloads.
- `low`: Minimal impact, non-critical services.
- `medium`: Noticeable impact, standard services.
- `high`: Critical impact, tier-0 services.

#### **Status (`status`)**

- `pending`: Resource requested/provisioning.
- `active`: Resource live and governed.
- `deprecated`: Scheduled for removal, no new dependencies.
- `archived`: Historical record, no longer live.
- `draft`: Work-in-progress (specifically for docs/ADRs).

#### **Type (`type`)**

- `app`: Frontend/Backend application services (Backstage: `service`).
- `infra`: Infrastructure resources (VPC, EKS, RDS).
- `tool`: Internal platform tooling.
- `adr`: Architecture Decision Records.
- `changelog`: Change tracking entries.
- `registry`: Container registries (ECR).

#### **Observability Tier (`reliability.observability_tier`)**

- `gold`: Full RED/Golden signals, centralized alerting.
- `silver`: Standard metrics, dashboard-only.
- `bronze`: Basic uptime/liveliness.

### 2. Implementation Rules

- **Ingestion Mapping**: The Knowledge Graph engine (`extract_relationships.py`) will map Backstage-native types (e.g., `service`) to platform types (e.g., `app`).
- **Validation Drift**: Any metadata value not in these enums will trigger a `SCHEMA_VIOLATION` in the validation gates.

## Consequences

### Positive

- **Deterministic Reporting**: Accurate risk-weighted scoring in `PLATFORM_HEALTH.md`.
- **Queryable Blast Radius**: Instant identification of `high` risk nodes affected by an incident.
- **Improved UX**: Unified dropdowns in software templates.

### Negative

- **Validation Friction**: Non-compliant metadata must be fixed before merging.
- **Migration Effort**: Existing files needs normalization to match the new enums.
