---
id: GOV-0051-auto-healing-guide
title: Governance - Documentation Auto-Healing Guide
type: guide
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
relates_to:
  - 01_adr_index
  - ADR-0111-platform-documentation-auto-healing
category: governance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
aliases:
  - AUTO_HEALING_GUIDE
---

## Governance: Documentation Auto-Healing Guide

**Status**: Active | **Owner**: Platform-Team | **Last Updated**: 2026-01-06

## Overview

To maintain a high-integrity developer portal (Backstage) and a clear operational landscape, the platform enforces "Zero-Drift" documentation. This is achieved via a **Closed-Loop Auto-Healing** mechanism that ensures indices for scripts and workflows are always in sync with the physical state of the repository.

## The Auto-Healing Flow

```text
  Developer Action             CI/CD Quality Gate (Auto-Healer)
  +----------------+           +----------------------------------+
  |                |           |                                  |
  |  Add new script|           |  1. Trigger on PR Push           |
  |  or workflow   |---------->|                                  |
  |                |           |  2. Scan repository files        |
  +----------------+           |                                  |
           |                   |  3. Validate against Index files |
           |                   |     (Drift Detected?)            |
           |                   |           |                      |
           |                   |           |-- [YES] -------------|
           |                   |           |                      |
           |                   |           v                      |
           |                   |  4. Execute Index Generators     |
           |                   |                                  |
           |                   |  5. Commit fixes back to PR      |
           |<------------------|     (github-actions[bot])        |
           |                   |                                  |
  +----------------+           |  6. Re-validate Final State      |
  |                |           |                                  |
  | PR updated with|           |  7. Pass PR Gate                |
  | latest docs    |           |                                  |
  +----------------+           +----------------------------------+
```

## PR Review & Gate Mechanics

### Who reviews the PR?

- **Primary**: The `platform-team` is the designated owner for all governance and automation indices.
- **Enforcement**: This is managed via the `CODEOWNERS` file, which requires approval from the platform team for any changes to `scripts/index.md` or `ci-workflows/CI_WORKFLOWS.md`.

### How does it pass the gate?

The PR gate is managed by the `.github/workflows/ci-index-auto-heal.yml` workflow and relies on a **Success/Failure contract**:

1. **Strict Validation**: The workflow runs `generate_script_index.py --validate` and `generate_workflow_index.py --validate`.
2. **Exit Code Policy**:
    - **Exit 0**: The index matches the physical files. The gate turns **GREEN** .
    - **Exit 1**: Drift is detected. The workflow attempts to auto-heal.
3. **The "Safety Loop"**: After the bot commits the updated indices, the workflow runs the validation **one final time**.
    - If the second validation confirms the index is now perfect, the gate turns **GREEN** .
    - If it still fails (indicating a deeper script error), the gate stays **RED**  and blocks the merge.

## Key Components

1. **Enforcement Script**: `scripts/generate_script_index.py --validate`
2. **Workflow Scraper**: `scripts/generate_workflow_index.py --validate`
3. **The Healer**: `.github/workflows/ci-index-auto-heal.yml`

## � Security & Integrity

To prevent the automated bot from being used as an injection vector for malicious content, we employ a **Defense in Depth** strategy:

### 1. Zero-Execution Parsing

The indexing scripts do not "run" the code they scan.

- **Python**: Uses `ast.parse` to look at the document tree without execution.
- **YAML**: Uses `yaml.safe_load` which blocks the execution of arbitrary Python objects or tags.

### 2. Automated Indexing

The system maintains the following indices in real-time:

- **Script Index**: [scripts/index.md](../../scripts/index.md)
- **Workflow Index**: [.github/workflows/index.md](.github/workflows/index.md)
- **ADR Index**: [docs/adrs/01_adr_index.md](../adrs/01_adr_index.md)

### 3. Limited File Scope

The bot is cryptographically restricted (via the workflow definition) to only modify three files: `scripts/index.md`, `ci-workflows/CI_WORKFLOWS.md`, and `docs/adrs/01_adr_index.md`. It cannot touch `.tf`, `.py`, or `.sh` logic.

### 4. Human-in-the-Loop (HITL) Mandate

Automation is for **drafting**, not **authorizing**.

- **The Mandatory Signature**: Per the **[CODEOWNERS Policy](GOV-0032-codeowners-policy.md)**, every bot-generated commit requires an explicit human approval (thumbs-up) from the `platform-team` before it can be merged.
- **Verification Gate**: The PR will remain blocked until a human has inspected the bot's diff for side-effects.
- **No Self-Approval**: The bot is technically barred from merging its own changes, ensuring a separation of concerns between "Generation" and "Verification."

### 5. GITHUB_TOKEN Restrictions

The workflow uses a short-lived, least-privilege `GITHUB_TOKEN` scoped only to `contents: write` for the specific repository, preventing lateral movement or broader account exploitation.

## Bot & Token Management

The auto-healing system is designed to be **Zero-Ops**, requiring no manual secret management or external bot accounts.

- **The Bot Identity**: We use the built-in `github-actions[bot]`. It requires no separate account or SSH keys.
- **Token Scope**: We utilize the ephemeral `${{ secrets.GITHUB_TOKEN }}`. This token is automatically generated for the lifecycle of the workflow and destroyed immediately after.
- **Workflow Permissions**: The workflow explicitly requests `contents: write` for the individual job, ensuring the bot can push updates to PR branches without having broad repository-wide admin rights.
- **Non-Recursive CI**: Commits by this bot use the default GITHUB_TOKEN, which intentionally does not trigger further CI runs, preventing infinite recursive "auto-heal" loops.

## Latency & Cycle Time

The "Time-to-Sync" for documentation is tied to the GitHub Actions execution lifecycle:

- **Trigger Event**: A `git push` to any branch with an active Pull Request targeting `main` or `development`.
- **Detection Lag**: Typical CI startup time (10–15 seconds).
- **Execution Time**: The auto-healing scripts run in < 1 second.
- **Commit Cycle**: The bot usually pushes the documentation fix within **30–60 seconds** of your initial push.

> [!TIP]
> **Pro Tip for Zero Latency**:
> If you want to see the documentation changes instantly before you even push, you can run the scripts locally in your terminal:
> `python3 scripts/generate_script_index.py && python3 scripts/generate_workflow_index.py`

## Operational Rules

- **Automatic**: No manual action is required. If drift is detected, the bot commits the fix.
- **Atomic**: The healer only updates index files; it never touches logic or configuration.
- **Traceable**: All automated doc updates are committed with `chore: auto-heal documentation indices [skip ci]`.
