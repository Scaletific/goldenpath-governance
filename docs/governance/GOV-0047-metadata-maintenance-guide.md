---
id: GOV-0047-metadata-maintenance-guide
title: Metadata Maintenance & Evolution Guide
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0101-pr-metadata-auto-heal
category: governance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
aliases:
  - METADATA_MAINTENANCE_GUIDE
---

## Metadata Maintenance & Evolution Guide

## Overview

This guide outlines the protocol for updating the global metadata schema across all repository resources (300+ files). Our strategy relies on **Automated Remediation** rather than manual entry.

## The Evolution Workflow

When the governance schema needs to change (e.g., adding a `cost_center` field or changing an owner), follow these steps:

### 1. Update the Remediator

Modify `scripts/standardize-metadata.py`.

- Add the new field to the `SKELETON` dictionary with a sensible default value or a "TBD" placeholder.
- If the field can be derived (e.g., from path or filename), add that logic to the script.
- **Reference**: See [METADATA_SIDECAR_TEMPLATE.yaml](../templates/METADATA_SIDECAR_TEMPLATE.yaml) for the latest gold standard.

### 2. Execute Bulk Update

Run the standardized script across the entire repository:

```bash
python3 scripts/standardize-metadata.py
```

This script will safely merge the new schema into all Markdown headers and `metadata.yaml` sidecars without affecting the body content.

### 3. Update the Validator

Modify `scripts/validate_metadata.py`.

- Add the new field to `REQUIRED_FIELDS`.
- Add specific validation logic (e.g., regex checks for billing codes).

### 4. PR Auto-Healing & Audit

The CI/CD pipeline (`ci-metadata-validation.yml`) implements **Auto-Healing** (see ADR-0101).

- **Automated Fixes**: If a PR touches files with outdated metadata, the CI will automatically run the remediator and commit the fixes back to the PR branch.
- **Developers**: Replace the default/placeholder values injected by the auto-healer with real data.
- **Platform Team**: Run `scripts/platform_health.py` to see a "Compliance Coverage" map of the new field across the organization.

## Key Principles

- **No Manual Backfills**: Never ask engineers to manually update 100+ files. Always update the script first.
- **Remediation > Validation**: The validator should only catch new errors; the remediator should fix existing ones.
- **Schema Parity**: Ensure `metadata.yaml` sidecars and Markdown frontmatter always share the same skeleton.
