---
id: ADR-0125
title: 'ADR-0125: Compliance & Maintenance Suite'
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
  - ADR-0125
  - CL-0081
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

## ADR-0125: Compliance & Maintenance Suite

## Status

Accepted (Backfill)

## Context

The GoldenPath IDP requires continuous auditing and maintenance of its metadata and governance state. These utilities provide the "Janitorial" and "Auditing" functions for the platform.

## Decision

We officially adopt the following scripts as the core Compliance & Maintenance Suite:

1. **`check_compliance.py`**: A CLI tool for scanning assets against the latest governance policy.
2. **`fix_yaml_syntax.py`**: Remediates syntactical issues in YAML templates.
3. **`migrate_partial_metadata.py`**: Handles bulk migration of legacy metadata to the enhanced schema.
4. **`backfill_metadata.py`**: Injects mandatory tags into untagged or legacy assets.
5. **`reliability-metrics.sh`**: Collects MTTR/MTTF metrics for the Platform Health dashboard.
6. **`test_platform_health.py` / `test_hotfix.py`**: Ensures the integrity of the health and guardrail logic.
7. **`render_template.py`**: Standardizes how Backstage templates are tested and rendered locally.

## Consequences

- **Positive**: Clean, auditable, and migratable metadata state.
- **Positive**: Reliable health reporting through vetted metrics.
- **Negative**: High cognitive load to maintain diverse maintenance scripts.
