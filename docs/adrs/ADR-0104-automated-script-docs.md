---
id: ADR-0104-automated-script-docs
title: Automated Script Documentation
type: adr
status: superseded
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
  - ADR-0103-automated-workflow-docs
  - ADR-0104-automated-script-docs
  - ADR-0111-platform-documentation-auto-healing
  - CL-0066-automate-script-docs
supersedes: []
superseded_by: ADR-0111
tags: []
inheritance: {}
supported_until: 2027-01-06
version: '1.0'
created_date: 2026-01-06
breaking_change: false
---

# ADR-0104: Automated Script Documentation

## Context
The platform relies on a large suite of Python and Shell scripts (~25) for governance, documentation, and delivery. Maintaining a manual index of these scripts (`scripts/index.md`) is tedious and error-prone, leading to stale documentation where new utility scripts (like `test_hotfix.py` or `generate_workflow_index.py`) are undocumented.

## Decision
We will automate the generation of the Platform Automation Scripts Index using a Python script (`scripts/generate_script_index.py`).

1.  **Dynamic Discovery**: Scans `scripts/*.py` and `scripts/*.sh` to find all tools.
2.  **Metadata Extraction**: Extracts the first line of the docstring (Python) or header comment (Shell) as the description.
3.  **Categorization**: Maps filenames to logical categories (Governance, Delivery, Documentation, Utilities) based on keywords.
4.  **Linking**: Automatically generates absolute file links for easy navigation.

## Consequences
### Positive
- **Completeness**: Every script in the directory is indexed by default.
- **Accuracy**: Descriptions are pulled directly from the code, encouraging better inline documentation.
- **Consistency**: The index format is uniform across all categories.

### Negative
- **Descriptions**: Scripts without docstrings will show "No description provided," requiring developers to improve code comments.

## Implementation
- Generator: `scripts/generate_script_index.py`
- Output: `scripts/index.md`
