---
id: ADR-0136
title: 'ADR-0136: Tooling config identity sidecars'
type: adr
status: proposed
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: proposed
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0082-platform-metadata-validation
  - ADR-0111-platform-documentation-auto-healing
  - ADR-0136
  - ADR-0137
  - ADR-0145
  - CL-0097
  - GOV-0044-metadata-artifact-adoption
  - ROADMAP
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-09
version: 1.0
breaking_change: false
---

# ADR-0136: Tooling config identity sidecars

- **Status:** Proposed
- **Date:** 2026-01-09
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Governance | Operations
- **Related:** ADR-0082, ADR-0111

---

## Context

We want every artifact that influences platform behavior to have a clear identity,
owner, and audit trail. Tooling configs such as `.pre-commit-config.yaml`,
`.yamllint`, `.markdownlint.json`, and `mkdocs.yml` materially affect guardrails
and documentation workflows, but they lack explicit metadata. This reduces
traceability and makes governance reviews harder to audit.

## Decision

We will introduce **tooling config identity sidecars** for root-level config files.
Each config file will have an adjacent metadata file using the pattern
`<config>.metadata.yaml`, with an explicit `id`, `owner`, `risk_profile`, and
other required fields.

This keeps the tooling config valid for its parser while providing an auditable
identity record alongside it.

## Scope

**Applies to:**
- Root-level tooling configs that affect CI, linting, and docs.
- Configs that cannot embed metadata directly.

**Does not apply to:**
- Application runtime configs owned by workload teams.
- Generated files under `logs/` or `test-output/`.

## Consequences

### Positive

- Every tooling config has an explicit identity and owner.
- Governance reviews become auditable and traceable.
- No changes required to upstream tool parsers.

### Tradeoffs / Risks

- Adds small sidecar files to maintain.
- Slightly more files to review per change.

### Operational impact

- Metadata validators will include these sidecars as standard artifacts.
- Contributors must update sidecars when renaming or relocating config files.

## Alternatives considered

### Embed metadata inside configs

Rejected because most tooling formats would fail parsing (invalid schema).

### Central registry document

Rejected due to drift risk and lack of locality to the config file.

## Follow-ups

- Add sidecars for `.pre-commit-config.yaml`, `.yamllint`,
  `.markdownlint.json`, and `mkdocs.yml`.
- Evaluate extending enforcement to require sidecars for other governance-
  critical config files.

## Notes

This pattern aligns with the platform’s “every artifact has an identity” principle
without introducing changes to tool parsers.
