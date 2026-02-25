---
id: ADR-0120-metadata-inheritance-and-active-governance
title: metadata
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
  - ADR-0120-metadata-inheritance-and-active-governance
  - CL-0076-metadata-inheritance-and-active-governance
  - PLATFORM_URGENT_FIX
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

id: ADR-0120-metadata-inheritance-and-active-governance
title: 'ADR-0120: Metadata Inheritance, Versioning, and Active Governance Loop'
type: adr
owner: platform-team---

## ADR-0120: Metadata Inheritance, Versioning, and Active Governance Loop

## Status

Proposed

## Context

As we reach V1 readiness for the Golden Path IDP, we need a metadata system that is both robust and fluid. Maintaining 500+ explicit metadata files is a velocity bottleneck, while a static "set and forget" governance model risks becoming stale or detached from platform reality.

## Decision

We will implement **Cascading Metadata Inheritance** paired with an **Active Governance Loop** and **Contract Versioning**.

### 1. Cascading Inheritance

- Resources inherit metadata (owner, domain, reliability) from parent `metadata.yaml` files.
- **Identity Rule**: Every asset must still declare a unique `id` locally.
- **Override Rule**: Local definitions always supersede inherited parent values.

### 2. Contract Versioning

- Both `enums.yaml` and `*.schema.yaml` will carry a `version` field (starting at `v1`).
- Artifacts can optionally specify `schema_version` to facilitate smooth v1 -> v2 migrations.

### 3. Active Governance Loop

- **Automated Audit**: A recurring process (`audit_metadata.py`) will validate all artifacts and generate immutable health snapshots.
- **Freshness TTL**: Parent metadata must be reviewed periodically (90-day TTL).
- **Migration Capability**: Formalized `scripts/migrations/` directory to handle schema evolutions as first-class capabilities.

### 4. CI Protection

- CI gates will validate not just the metadata, but the **schemas themselves** (ensuring valid enum references and no circular dependencies).

## Consequences

### Positive

- **Boilerplate Reduction**: ~85% reduction in redundant metadata lines.
- **Fluidity**: Operations (like team reorgs) become O(1) parent updates.
- **V1 Robustness**: The platform "watches itself," ensuring the Knowledge Graph never drifts from reality.

### Tradeoffs

- **Validation Overhead**: Scripts must now search up the tree (O(depth)).
- **Change Control**: Evolution follows strict conservative/additive rules to prevent breaking the catalog.
