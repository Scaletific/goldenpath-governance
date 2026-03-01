---
id: ADR-0137
title: 'ADR-0137: Metadata placement for configs and reports'
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
  - ADR-0087-k8s-metadata-sidecars
  - ADR-0136
  - ADR-0137
  - CL-0098
  - GOV-0044-metadata-artifact-adoption
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-09
version: 1.0
breaking_change: false
---

# ADR-0137: Metadata placement for configs and reports

- **Status:** Proposed
- **Date:** 2026-01-09
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Governance | Operations
- **Related:** ADR-0087, ADR-0136, GOV-0044-metadata-artifact-adoption

---

## Context

We need a single, consistent rule for where metadata lives for non-doc artifacts
(config YAML/JSON and generated reports). Mixing frontmatter and sidecars has led
to confusion, validation gaps, and drift between machine artifacts and the
governance model.

## Decision

We will use **sidecar metadata** (`<file>.metadata.yaml`) for configs and
generated reports. We will use **frontmatter** only for docs under `docs/` that
are indexed by Backstage/TechDocs. If both exist, **frontmatter is the source of
truth** and sidecars must be derived.

## Scope

**Applies to:**
- Config files (YAML/JSON) that drive automation or reporting.
- Generated reports (JSON/MD) stored under `reports/**`.

**Does not apply to:**
- Docs in `docs/` (use frontmatter).
- Source code files and binaries.

## Consequences

### Positive

- Clear rule reduces ambiguity and drift.
- Tool parsers remain valid (no schema injected into configs).
- Metadata remains discoverable and auditable.

### Tradeoffs / Risks

- Adds extra sidecar files to manage.
- Requires discipline to keep sidecars in sync.

### Operational impact

- Sidecar creation becomes part of new artifact creation.
- Validation and reporting should evolve to include `<file>.metadata.yaml`.

## Alternatives considered

### Embed schema in config headers

Rejected because most tool parsers will fail on non-standard headers.

### Use only frontmatter everywhere

Rejected because configs and JSON reports cannot safely include frontmatter.

### Maintain a central registry file

Rejected due to drift risk and loss of locality.

## Follow-ups

- Add sidecars for the inventory config and report outputs.
- Update validators/reporting to include tooling-style sidecars.
- Track `scripts/aws_inventory.py` as the first governed report generator under this policy.

## Notes

This decision formalizes the sidecar pattern already used for tooling configs
and aligns it with metadata governance goals.
