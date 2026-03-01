---
id: ADR-0140
title: 'ADR-0140: Doc scaffolding and metadata auto-fix'
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
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0088-automated-metadata-remediation
  - ADR-0140
  - CL-0101
  - METADATA_STRATEGY
  - METADATA_VALIDATION_GUIDE
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-10
version: 1.0
breaking_change: false
---

## ADR-0140: Doc scaffolding and metadata auto-fix

- **Status:** Accepted
- **Date:** 2026-01-10
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Governance | Operations
- **Related:** METADATA_STRATEGY, METADATA_VALIDATION_GUIDE, ADR-0088

---

## Context

New docs are often created without the required metadata headers. The missing
frontmatter is usually only discovered at PR time, which creates friction and
burns review cycles. We need a path that makes compliant headers the default,
not an afterthought.

## Decision

We will enforce a three-layer flow for new documentation:

1. **Scaffold** new docs via `scripts/scaffold_doc.py` so headers match the
   metadata schema from day one.
2. **Auto-fix** doc headers in pre-commit using `scripts/standardize_metadata.py`
   for any changed Markdown file under `docs/`.
3. **Validate** in CI with `scripts/validate_metadata.py` as a backstop only.

## Scope

### Applies to

- Markdown docs under `docs/`.

### Does not apply to

- Generated reports or config files (use sidecar metadata).
- Non-doc source code.

## Consequences

### Positive

- Authors get compliant headers automatically.
- PRs fail less often on missing metadata.
- Governance remains enforced without slowing delivery.

### Tradeoffs / Risks

- Pre-commit will modify files, requiring a re-stage.
- Authors must use the scaffold for best results.

### Operational impact

- Add `scripts/scaffold_doc.py`.
- Add a pre-commit hook for doc header normalization.

## Alternatives considered

### CI-only validation

Rejected because it shifts enforcement to the end of the workflow and causes
avoidable rework.

### Manual templates only

Rejected because manual copying still leads to inconsistent metadata.

## Follow-ups

- Update onboarding docs to reference the scaffold script.
- Monitor pre-commit friction and adjust scope if needed.
