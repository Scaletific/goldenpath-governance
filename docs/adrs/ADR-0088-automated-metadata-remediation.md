---
id: ADR-0088-automated-metadata-remediation
title: 'ADR-0088: Automated Metadata Remediation over Manual Compliance'
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
  - ADR-0082-platform-metadata-validation
  - ADR-0084-platform-enhanced-metadata-schema
  - ADR-0088-automated-metadata-remediation
  - ADR-0140
  - GOV-0047-metadata-maintenance-guide
  - METADATA_VALIDATION_GUIDE
  - GOV-0054-script-certification-audit
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# ADR-0088: Automated Metadata Remediation over Manual Compliance

## Status
Proposed

## Context
As the repository grows (currently 316+ files), maintaining a consistent metadata schema becomes increasingly difficult if left to manual developer effort. Traditional "governance" relies on blocking PRs until developers manually fix metadata, which leads to friction and "governance fatigue."

We need a way to evolve our schema (e.g., adding mandatory fields) that scales linearly and requires minimal human intervention.

## Decision
We will adopt an **Automated Remediation** strategy for metadata management.

### 1. Script-First Evolution
Any change to the metadata schema MUST be accompanied by a corresponding update to `scripts/standardize-metadata.py`. This script serves as the "Healer" for the repository.

### 2. Bulk Remediation vs. PR Blocking
Instead of asking developers to backfill thousands of documents, the Platform Team will periodically run bulk remediation passes to bring the entire repository into compliance. PR blocking (via `validate_metadata.py`) will be used primarily to catch *new* non-compliant files, while existing files are maintained via script.

### 3. Skeleton Merging
The remediation script will use a "Skeleton Merge" approach:
- It preserves existing data.
- It injects missing required blocks.
- It enforces standardized IDs and path-based uniqueness.

## Consequences
- **Positive**: Schema evolution effort is now O(1) instead of O(N).
- **Positive**: Reduced developer friction; developers only deal with metadata when it’s meaningful to their specific work.
- **Positive**: Guaranteed 100% compliance across all historical documents at all times.
- **Negative**: Risk of mass-corrupting headers if the script is buggy (mitigated by dry-runs and git revert).
