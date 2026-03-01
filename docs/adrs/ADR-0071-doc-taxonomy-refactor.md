---
id: ADR-0071-doc-taxonomy-refactor
title: 'ADR-0071: Standardized Documentation Taxonomy'
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
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0071-doc-taxonomy-refactor
  - ADR-0103-automated-workflow-docs
  - CL-0021-doc-taxonomy-refactor
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0071: Standardized Documentation Taxonomy

## Status

Accepted

## Context

The documentation structure has grown organically, leading to scattered "product-like" definitions (Requirements, Catalog, SLAs) and ambiguous homes for operational policies (Upgrade/Deprecation rules).

New files were introduced without a clear home:

- `production-readiness-gates/ROADMAP.md` (formerly `V1_03_TODO.md`)
- `production-readiness-gates/READINESS_CHECKLIST.md` (formerly `V1_05_DUE_DILIGENCE_SCORECARD.md`)

We need a standardized taxonomy to ensure every document has a predictable, discoverable location that aligns with the "Dewey Decimal" system (e.g., `20-contracts`, `70-operations`).

## Decision

We will restructure the documentation as follows:

1. **Foundations (`00-foundations`)**: Hosts high-level Product Requirements.
2. **Contracts (`20-contracts`)**: Hosts Service Agreements (SLAs) and Service Catalogs.
3. **Operations (`70-operations`)**: Hosts Lifecycle Policies (Upgrades/Deprecation).
4. **Readiness (`production-readiness-gates`)**: Renamed to clearer filenames (`ROADMAP.md`, `READINESS_CHECKLIST.md`) but kept as a distinct folder for visibility.

We will strictly enforce this taxonomy via `DOC_INDEX.md`.

## Consequences

- **Positive:** clearer navigation for users; less "folder sprawl" at the root level.
- **Negative:** Existing links might break (though we are fixing `DOC_INDEX.md` immediately).
