---
id: ADR-0111-platform-documentation-auto-healing
title: 'ADR-0111: Automated Documentation Auto-Healing'
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
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0101-pr-metadata-auto-heal
  - ADR-0103-automated-workflow-docs
  - ADR-0104-automated-script-docs
  - ADR-0111-platform-documentation-auto-healing
  - ADR-0112-automated-adr-index-generation
  - ADR-0133
  - ADR-0136
  - GOV-0051-auto-healing-guide
  - CL-0067-documentation-auto-healing
  - GOV-0032-codeowners-policy
supersedes:
  - ADR-0103
  - ADR-0104
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-06
version: 1.0
dependencies:
  - ADR-0103
  - ADR-0104
breaking_change: false
---

## ADR-0111: Automated Documentation Auto-Healing

- **Status:** Accepted (Supersedes ADR-0103, ADR-0104)
- **Date:** 2026-01-06
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Governance
owner: platform-team- **Related:** [ADR-0101: PR Metadata Auto-Heal](./ADR-0101-pr-metadata-auto-heal.md)

---

## Context

Our platform uses automated indexing scripts (`generate_script_index.py`, `generate_workflow_index.py`) to maintain documentation portals (`scripts/index.md`, `ci-workflows/CI_WORKFLOWS.md`).

Currently, these scripts are passive; they rely on developers or manual agents to run them. This has led to frequent "Documentation Drift" where new scripts or workflows are added but the indices are not updated.

While we have validation in CI, it merely flags the error, requiring manual intervention to fix.

## Decision

We will implement an **Automated Documentation Auto-Healing** mechanism.

> We will upgrade indexing scripts to support validation mode and implement a GitHub Action that automatically commits index updates back to Pull Request branches when drift is detected.

## Scope

- **Applies to**: `scripts/index.md`, `ci-workflows/CI_WORKFLOWS.md`.
- **Does not apply to**: Hand-written documentation or Architecture Decision Records (ADRs).

## Consequences

### Positive

- **Zero Drift**: Documentation is guaranteed to be in sync with the repository state.
- **Developer Velocity**: Developers don't need to remember to run indexing scripts; the platform "heals" itself.
- **Consistency**: Indices follow a standardized format enforced by the generation logic.

### Tradeoffs / Risks

- **Bot Noise**: PRs will see automated commits from `github-actions[bot]`.
- **Merge Complexity**: Automated commits might occasionally cause minor merge conflicts if the developer is actively editing the same files.

### Operational impact

- The CI bot must have `contents: write` permissions.
- Workflows must use `[skip ci]` to prevent infinite loops.

## Alternatives considered

1. **Strict Validation Only**: Keeping the current "fail in CI" model. Rejected because it adds friction to the developer experience for a purely mechanical task.
2. **Scheduled Sync**: Running a cron job to update indices. Rejected because it leads to "state delay" between PR merge and documentation update.

## Follow-ups

1. Upgrade `scripts/generate_script_index.py` with `--validate`.
2. Upgrade `scripts/generate_workflow_index.py` with `--validate`.
3. Implement `.github/workflows/ci-index-auto-heal.yml`.
