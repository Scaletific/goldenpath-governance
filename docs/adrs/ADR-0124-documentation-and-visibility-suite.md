---
id: ADR-0124
title: 'ADR-0124: Documentation & Visibility Suite'
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
  - ADR-0124
  - CL-0080
  - CL-0120
  - GOV-0026-governance-vocabulary
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

## ADR-0124: Documentation & Visibility Suite

## Status

Accepted (Backfill)

## Context

Maintaining a large documentation-as-code repository requires automated validation of freshness, structure, and relationships. These tools were built to prevent "Doc Drift" and ensure the Knowledge Graph remains accurate.

## Decision

We officially adopt the following scripts as the core Documentation & Visibility Suite:

1. **`format_docs.py`**: Ensures consistent whitespace and layout across the markdown corpus.
2. **`check_doc_freshness.py`**: Identifies stale documents based on metadata and commit history.
3. **`check_doc_index_contract.py`**: Enforces the "Index Policy" (every directory must have an index).
4. **`extract_relationships.py`**: Populates the Knowledge Graph by parsing `relates_to` and `supersedes` metadata.
5. **`generate_governance_vocab.py`**: Generates the human-readable [GOV-0026-governance-vocabulary.md](../../governance/GOV-0026-governance-vocabulary.md).
6. **`sync_backstage_entities.py`**: Mirrors internal metadata to Backstage YAML entities.
7. **`generate_doc_system_map.py`**: Visualizes documentation hierarchies and logical clusters.

## Consequences

- **Positive**: High documentation quality and navigability.
- **Positive**: Automated alignment between the repo and the Backstage Catalog.
- **Negative**: Adds overhead to CI runs (mitigated by only running on doc changes).
