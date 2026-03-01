---
id: ADR-0147
title: Automated Governance Backfill
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
  - ADR-0146
  - ADR-0146 (Born Governed)
  - ADR-0147
  - BORN_GOVERNED_LIFECYCLE
  - CL-0118
  - CL-0119
  - CL-0120
  - CNT-001 (Script Standard)
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-12
context:
  - We established the 'Born Governed' standard (ADR-0146) requiring metadata headers
    in all scripts.
  - We have ~45 existing scripts ('Legacy Estate') that are currently ungoverned (Maturity
    0).
  - Manually adding headers to 45 files is error-prone, tedious, and likely to result
    in inconsistent IDs.
decision:
  - We will implement an **Automated Backfill Injector** (`scripts/inject_script_metadata.py`).
  - The injector will assign deterministic IDs (`SCRIPT-XXXX`) utilizing a persistent
    registry (`schemas/automation/script_ids.yaml`).
  - 'The injector will apply safe defaults: Maturity 2, Low Risk, Declared Evidence.'
  - Future scripts should be created with headers manually (or via scaffolders), but
    the injector can be used to 'repair' missing headers.
consequences:
  - Immediate compliance (jump from 2% to 100% header coverage).
  - Eliminates 'Governance Debt' in a single operation.
  - Requires committing the `script_ids.yaml` registry to git to ensure ID stability.
---

# ADR-0147: Automated Governance Backfill

## Context
Following the ratification of [ADR-0146](ADR-0146-schema-driven-script-certification.md), the platform faces a "Migration Gap". We have stringent new rules (CNT-001) but a legacy codebase that violates them.

Validation reveals 43+ scripts failing compliance. Asking developers to manually edit each one is a significant productivity tax and risks inconsistencies (e.g., duplicate IDs, typo'd schema fields).

## Decision
We choose **Automation over Manual Migration**.

### The Injector Pattern
We introduced `scripts/inject_script_metadata.py` as a purpose-built migration tool. It:
1.  **Scans** the `scripts/` directory.
2.  **Detects** file type (Python vs Bash).
3.  **Generates** a valid, schema-compliant header with sensible defaults.
4.  **Injects** the header into the file (preserving shebangs).
5.  **Registers** the assigned ID in `schemas/automation/script_ids.yaml`.

### ID Strategy (`script_ids.yaml`)
To prevent ID collisions and ensure stability (so `SCRIPT-0042` always refers to `my_script.py` even if renamed), we introduced a simple YAML registry.

```yaml
next: 43
map:
  scripts/my_script.py: SCRIPT-0042
```

## Consequences
*   **Speed**: Compliance can be achieved in seconds.
*   **Consistency**: All headers are syntactically perfect V1 headers.
*   **Maintenance**: The registry file must be version controlled. Supports `repair_shebangs.py` for automated dialect correction.
