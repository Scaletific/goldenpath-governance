---
id: GOV-0044-metadata-artifact-adoption
title: Metadata Adoption Policy for Configs and Reports
type: governance
domain: governance
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
relates_to:
  - ADR-0087-k8s-metadata-sidecars
  - ADR-0136
  - GOV-0048-federated-metadata-strategy
  - GOV-0046-metadata-injection-guide
  - GOV-0047-metadata-maintenance-guide
tags:
  - metadata
  - sidecar
  - governance
category: governance
supported_until: 2028-01-01
aliases:
  - METADATA_ARTIFACT_ADOPTION_POLICY
---

# Metadata Adoption Policy for Configs and Reports

Doc contract:

- Purpose: Define metadata placement rules for configs and reports to ensure schema compliance.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md

## Refined Question
Where should metadata live for non-doc artifacts (config YAML/JSON and generated reports)
to remain schema-compliant and automation-friendly: sidecar files, frontmatter, or both?

## Policy Answer
- **Sidecar is the default** for machine/operational artifacts (configs + generated reports).
- **Frontmatter is for docs** that are indexed by Backstage/TechDocs.
- **Do not mix formats** unless there is a strong reason. If both exist, **frontmatter
  is the source of truth** and sidecars must be derived to prevent drift.

## Adoption Rules (by artifact type)

| Artifact | Location | Metadata Form | Source of Truth | Notes |
| --- | --- | --- | --- | --- |
| Config files (YAML/JSON) | repo root / scripts / configs | `<file>.metadata.yaml` | sidecar | Keep parsers clean; avoid schema in config body |
| Generated reports (JSON/MD) | reports/** | `<report>.metadata.yaml` | sidecar | Reports are artifacts, not docs |
| Docs indexed by Backstage | docs/** | frontmatter in `.md` | frontmatter | Required for TechDocs |
| Docs outside docs/ (non-indexed) | anywhere | sidecar | sidecar | Optional frontmatter only if needed |

## Examples
- `inventory-config.yaml` -> `inventory-config.metadata.yaml`
- `reports/aws-inventory/2026-01-09.json` -> `reports/aws-inventory/2026-01-09.json.metadata.yaml`
- `docs/governance/*.md` -> frontmatter only (no sidecar)

## Enforcement
- Sidecar presence is validated by `scripts/validate_metadata.py`.
- Schema updates are applied via `scripts/standardize-metadata.py` (the formatter).
- Mixing frontmatter + sidecar requires a documented exception and a sync rule.
