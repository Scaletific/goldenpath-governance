---
id: ADR-0094-automated-catalog-docs
title: 'ADR-0094: Automated Registry Catalog Documentation'
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
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0094-automated-catalog-docs
  - ADR-0097-domain-based-resource-catalogs
  - CL-0054-automated-catalog-docs
  - CL-0057-domain-based-catalogs
  - REGISTRY_CATALOG
  - GOV-0054-script-certification-audit
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
version: '1.0'
breaking_change: false
---

# ADR-0094: Automated Registry Catalog Documentation

## Status
Accepted

## Context

The ECR registry catalog (`docs/registry-catalog.yaml`) is the single source of truth for all container registries, but YAML is not easily scannable for humans. Teams need a quick, readable reference to find registries, understand their configuration, and access related documentation.

## Decision

Create an automated script (`scripts/generate_catalog_docs.py`) that transforms the YAML catalog into formatted markdown documentation.

### What It Does

1. **Loads** `docs/registry-catalog.yaml`
2. **Generates** `docs/REGISTRY_CATALOG.md` with:
   - Summary statistics (total, active, deprecated, risk distribution)
   - Inventory table (all registries at a glance)
   - Detailed registry cards (metadata, AWS details, governance, images)
   - Risk-based grouping (high/medium/low sections)
   - Links to related documentation

### Automation

- Run manually: `python scripts/generate_catalog_docs.py`
- Run on catalog updates (future: GitHub Action)
- Output is auto-generated (do not edit manually)

## Consequences

**Pros:**
- Human-readable catalog for quick reference
- Auto-generated (no manual sync needed)
- Risk-based grouping for prioritization
- Links to runbooks and ADRs

**Cons:**
- Requires running script after catalog changes
- Generated file can become stale if not automated

**Mitigations:**
- Add GitHub Action to auto-generate on catalog changes
- Include "do not edit" warning in generated file

## Related
- [ADR-0092: ECR Registry Product Strategy](./ADR-0092-ecr-registry-product-strategy.md)
