---
id: ADR-0145
title: 'ADR-0145: Governance Registry Mirror Pattern'
type: adr
domain: platform-governance
value_quantification:
  vq_class: 🔵 MV/HQ
  impact_tier: high
  potential_savings_hours: 5.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
  maturity: 3
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0026-platform-cd-deployment-contract
  - ADR-0136
  - ADR-0145
  - ADR-0159-backstage-catalog-registry-sync
  - CAPABILITY_LEDGER
  - CL-0113
  - CL-0114
  - CL-0115
  - CL-0129
  - RB-0028
  - GOV-0054-script-certification-audit
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-12'
---

## ADR-0145: Governance Registry Mirror Pattern

## Context

High-velocity interaction between humans and machine agents creates a "Commit Tug-of-War" when automated scripts attempt to mutate active development branches. Specifically, scripts updating `PLATFORM_HEALTH.md`, documentation indices, and catalog syncs frequently cause `[rejected] fetch first` errors for human contributors and generate branch drift across open PRs.

We require a mechanism that:

- Preserves high-integrity audit trails.
- Avoids branch mutation during active development.
- Scales across multiple environments without state collision.
- Remains reproducible from a specific source commit.

## Decision

We will implement the **Governance Registry Mirror Pattern**. All machine-generated outputs (metadata reports, platform health reports, documentation indices, audit logs) will be written to a dedicated branch named: `governance-registry`.

This branch is CI-owned, and acts as an **observation context (derived state)**, decoupled from human/agent intent branches (`development`, `main`).

## Source of Truth Contract

To prevent ambiguity and future drift:

1. **Canonical intent (source of truth)** lives in: `development` and `main` (code, configs, contracts, schemas, workflows).
2. **Canonical observation (derived outputs)** lives in: `governance-registry` (health reports, indices, audit artifacts).
3. **Registry content is derived-only**:
   - Every registry commit MUST reference a `source_sha` from `development` or `main`.
   - The registry outputs MUST be reproducible by rerunning the audit pipeline at that `source_sha`.
4. **No manual fixes in registry**: Humans do not "patch" dashboards in the registry branch; fixes happen in source branches and re-generate.

## Visual Architecture

```mermaid
graph TD
    subgraph "Source Control (Human/Agent Intent)"
        DEV[branch: development]
        PROD[branch: main]
    end

    subgraph "CI Pipelines (Audit Engine)"
        CI_DEV[CI Audit Job]
        CI_PROD[CI Audit Job]
    end

    subgraph "Governance Registry (Observation Context)"
        REG[branch: governance-registry]
        subgraph "Unified Dashboards"
            DASH[UNIFIED_DASHBOARD.md]
        end
        subgraph "Environment Folders"
            EDEV[environments/development/latest/PLATFORM_HEALTH.md]
            EPROD[environments/production/latest/PLATFORM_HEALTH.md]
            HDEV[environments/development/history/DATE-SHA/]
            HPROD[environments/production/history/DATE-SHA/]
        end
    end

    DEV -- "Push/Merge" --> CI_DEV
    PROD -- "Merge/Push" --> CI_PROD

    CI_DEV -- "Commit Audit Result (source_sha)" --> EDEV
    CI_PROD -- "Commit Audit Result (source_sha)" --> EPROD

    CI_DEV -- "Archive Result (date+sha)" --> HDEV
    CI_PROD -- "Archive Result (date+sha)" --> HPROD

    EDEV -- "Automatic Aggregation" --> DASH
    EPROD -- "Automatic Aggregation" --> DASH
```

## Architecture: Unified Registry Layout

The `governance-registry` branch uses environment-specific nesting:

- `environments/<env>/latest/...` (Always current view).
- `environments/<env>/history/<date>-<sha>/...` (Append-only forensic audit trail).

Every report is bound to: `source_branch`, `source_sha`, `generation timestamp (UTC)`, and `audit job ID`.

## Implementation Contract

### 1. Canonical Metadata Schema

Every artifact written to the `governance-registry` branch MUST include the following YAML frontmatter:

```yaml
---

type: governance-report
env: <ENVIRONMENT_NAME>
generated_at: <TIMESTAMP_UTC>
source:
  branch: <SOURCE_BRANCH>
  sha: <GIT_SHA>
pipeline:
  workflow: <WORKFLOW_NAME>
  run_id: <RUN_ID>
integrity:
  derived_only: true
---
```

### Required Fields (Non-Negotiable)

- `env` - Environment name (development, main, test, staging, production)
- `generated_at` - UTC timestamp in ISO 8601 format
- `source.branch` - Source branch name
- `source.sha` - Source commit SHA
- `pipeline.workflow` - GitHub Actions workflow name
- `pipeline.run_id` - GitHub Actions run ID
- `integrity.derived_only` - Must be `true`

### 2. CI Writer Identity

The registry is written exclusively by:

- **Identity**: GitHub Actions service account using `GITHUB_TOKEN`
- **Permissions**: `contents: write`
- **Branch Protection**:
  - Restrict who can push:  Enabled
  - Allow GitHub Actions to bypass:  Enabled
  - Block force-push:  Enabled
  - Require linear history:  Enabled

### 3. Concurrency Control

To prevent race conditions during high-velocity merges:

```yaml
concurrency:
  group: govreg-${{ github.ref_name }}
  cancel-in-progress: false
```

This ensures updates are queued and processed in chronological order per source branch.

### 4. Atomic Write Strategy

Every registry update MUST perform the following in a single commit:

1. Update `environments/<env>/latest/*`
2. Create `environments/<env>/history/<timestamp>-<sha>/*`
3. Regenerate `UNIFIED_DASHBOARD.md`

## Operational Rules

### 1. Write Boundary (Integrity Control)

Only the **CI identity** may push to `governance-registry`. Human contributors do not commit directly to the registry branch.

### 2. Visibility & UX

- **README Mitigation**: Root `README.md` links to `governance-registry/UNIFIED_DASHBOARD.md` and `latest/` health reports.
- **PR Delta Comments**: Every PR merge posts a comment containing registry links, `source_sha`, and a pass/fail summary with key deltas.

## Consequences

### Positive

- **Frictionless Development**: Eliminates rejections caused by background mutation.
- **Audit Integrity**: Derived outputs have a linear, append-only history independent of code churn.
- **Clear separation of concerns**: Intent branches stay clean; observation stays authoritative.
- **Reproducibility**: Every report can be regenerated from its source SHA.

### Negative

- **Split visibility**: Mitigated via README pinning + PR comments.
- **Repo growth**: Mitigated via future retention policy or periodic squashing.

## Alternatives Considered

- **GitHub Action Summaries**: Rejected as ephemeral.
- **Post-merge commits to dev**: Rejected as noisy and causes PR sync issues.
- **External object store (S3)**: Deferred; may complement git if repo growth exceeds 500MB.

## Implementation Reference

- **Runbook**: [RB-0028: Governance Registry Operations](/docs/70-operations/runbooks/RB-0028-governance-registry-operations.md)
- **Workflow**: [governance-registry-writer.yml](/.github/workflows/governance-registry-writer.yml)
- **Validator**: `validate_govreg.py`: Ensures the registry branch structure is sound.
- **Architecture**: [How it Works - Governance Registry Mirror](/85-how-it-works/governance/GOVERNANCE_REGISTRY_MIRROR.md)
