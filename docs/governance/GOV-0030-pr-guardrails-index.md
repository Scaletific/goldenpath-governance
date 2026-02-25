---
id: GOV-0030-pr-guardrails-index
title: PR Guardrails Index
type: documentation
domain: governance
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - GOV-0029-pr-guardrails
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0017-platform-policy-as-code
  - ADR-0065-platform-branch-policy-guard
  - ADR-0098-standardized-pr-gates
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0165
  - CI_WORKFLOWS
  - CL-0150
  - PR_GUARDRAILS
  - RDS_DUAL_MODE_AUTOMATION
  - RDS_REQUEST_FLOW
  - SESSION_CAPTURE_2026_01_17_02
  - agent_session_summary
  - session-2026-01-19-build-pipeline-architecture
aliases:
  - PR_GUARDRAILS_INDEX
---

# PR Guardrails Index

This document provides a comprehensive catalog of all PR guardrail workflows, their triggers, enforcement scope, and current status.

## Overview

| Category | Count | Status |
| -------- | ----- | ------ |
| Core PR Gates | 4 | Active |
| Resource Guards | 3 | Warn-Only (Rollout) |
| Session Guards | 1 | Active |
| Scheduled Enforcement | 1 | Active |

---

## Core PR Gates

These guardrails enforce governance standards on every PR.

### Policy - PR Guardrails

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/pr-guardrails.yml` |
| Owner | platform-team |
| Trigger | `pull_request` to `main`, `development` |
| Enforcement | **Blocking** |

**What it checks:**

- PR checklist completion (Change Type, Impact, Testing, Rollback)
- PR template header present
- Bypass label validation (`docs-only`, `typo-fix`, `hotfix`, `build_id`)
- Script traceability (ADR + CL references for new scripts)

**Related:** [GOV-0029-pr-guardrails](GOV-0029-pr-guardrails.md), [PR_GUARDRAILS](../85-how-it-works/governance/PR_GUARDRAILS.md)

---

### Policy - Branch Policy Guard

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/branch-policy.yml` |
| Owner | platform-team |
| Trigger | `pull_request` to `main` |
| Enforcement | **Blocking** |

**What it checks:**

- Only `development`, `build-<dd-mm-yy-NN>`, or `hotfix/*` branches can merge to `main`
- Prevents direct feature branch merges to `main`

**Related:** [ADR-0065](../adrs/ADR-0065-platform-branch-policy-guard.md)

---

### Policy - ADR Policy

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/adr-policy.yml` |
| Owner | platform-team |
| Trigger | `pull_request` to `main` with `adr-required` label |
| Enforcement | **Blocking** (when labeled) |

**What it checks:**

- If `adr-required` label is present, PR must include a file matching `docs/adrs/ADR-####-*.md`

**Related:** [GOV-0029-pr-guardrails](GOV-0029-pr-guardrails.md)

---

### Policy - Changelog Policy

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/changelog-policy.yml` |
| Owner | platform-team |
| Trigger | `pull_request` to `main` with `changelog-required` label |
| Enforcement | **Blocking** (when labeled) |

**What it checks:**

- If `changelog-required` label is present, PR must include a file matching `docs/changelog/entries/CL-####-*.md`
- Can be bypassed with `changelog-exempt` label

**Related:** [GOV-0029-pr-guardrails](GOV-0029-pr-guardrails.md)

---

## Resource Guards

These guardrails enforce resource-specific governance and are currently in warn-only mode during rollout.

### RDS Size Approval Guard

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/rds-size-approval-guard.yml` |
| Owner | platform-team |
| Trigger | `pull_request` modifying `docs/20-contracts/resource-catalogs/rds-catalog.yaml` or `docs/20-contracts/rds-requests/**/*.yaml` |
| Enforcement | **Warn-Only** (rollout) |

**What it checks:**

- `size: large` or `size: xlarge` requires platform-team or security-team approval
- Applies to both catalog entries and individual RDS request files
- Non-dev environments require explicit approval for larger sizes

**Related:** [RDS_REQUEST_FLOW](../85-how-it-works/self-service/RDS_REQUEST_FLOW.md), [ADR-0165](../adrs/ADR-0165-rds-user-db-provisioning-automation.md)

---

### RDS tfvars Drift Guard

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/rds-tfvars-drift-guard.yml` |
| Owner | platform-team |
| Trigger | `pull_request` modifying `envs/*/terraform.tfvars` |
| Enforcement | **Warn-Only** (rollout) |

**What it checks:**

- `application_databases` keys in coupled tfvars must match standalone tfvars
- Prevents drift between coupled and standalone RDS configurations

**Related:** [RDS_DUAL_MODE_AUTOMATION](../85-how-it-works/self-service/RDS_DUAL_MODE_AUTOMATION.md), [ADR-0158](../adrs/ADR-0158-platform-standalone-rds-bounded-context.md)

---

### Quality - RDS Request Validation

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/ci-rds-request-validation.yml` |
| Owner | platform-team |
| Trigger | `pull_request` modifying `docs/20-contracts/rds-requests/**/*.yaml`, schema, or parser |
| Enforcement | **Blocking** |

**What it checks:**

- RDS request files conform to `schemas/requests/rds.schema.yaml`
- Enum values match `schemas/metadata/enums.yaml`
- Parser can successfully process request files

**Related:** [RDS_REQUEST_FLOW](../85-how-it-works/self-service/RDS_REQUEST_FLOW.md)

---

## Session Guards

These guardrails enforce documentation and session capture standards.

### Session Capture Guardrail

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/session-capture-guard.yml` |
| Owner | platform-team |
| Trigger | `pull_request` modifying `session_capture/**/*.md` (excludes templates) |
| Enforcement | **Blocking** |

**What it checks:**

- Session capture files are append-only (body content cannot be modified, only appended)
- New content must include timestamped update header (`## Update - YYYY-MM-DDTHH:MM:SSZ`)
- Frontmatter updates are allowed (e.g., `relates_to` changes)

**Related:** [GOV-0034-ai-agent-governance](GOV-0034-ai-agent-governance.md), [26_AI_AGENT_PROTOCOLS](../80-onboarding/26_AI_AGENT_PROTOCOLS.md)

---

### Session Log Requirement

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/session-log-required.yml` |
| Owner | platform-team |
| Trigger | `pull_request` modifying critical paths (workflows, gitops, bootstrap, modules, scripts, governance, ADRs, runbooks) |
| Enforcement | **Blocking** |

**What it checks:**

- Any change in critical paths requires:
  - a session capture update (`session_capture/**/*.md`, append-only)
  - a session summary update (`session_summary/agent_session_summary.md`)

**Related:** [GOV-0034-ai-agent-governance](GOV-0034-ai-agent-governance.md), [26_AI_AGENT_PROTOCOLS](../80-onboarding/26_AI_AGENT_PROTOCOLS.md)

---

## Scheduled Enforcement

These workflows run on a schedule to detect and report policy violations.

### Daily Policy Enforcement

| Property | Value |
| -------- | ----- |
| File | `.github/workflows/policy-enforcement.yml` |
| Owner | platform-team |
| Trigger | Daily at 09:00 UTC (cron), `workflow_dispatch` |
| Enforcement | **Reporting** (creates issues) |

**What it checks:**

- ECR registry compliance with metadata policies
- Resource tagging compliance
- Policy drift detection

**Related:** [ADR-0017](../adrs/ADR-0017-platform-policy-as-code.md)

---

## Enforcement Modes

| Mode | Behavior | Use Case |
| ---- | -------- | -------- |
| **Blocking** | PR cannot be merged if check fails | Core governance requirements |
| **Warn-Only** | Check runs but failure doesn't block PR | Rollout phase for new guards |
| **Reporting** | Violations logged/issued but no PR impact | Scheduled compliance checks |

---

## Adding New Guardrails

When creating a new guardrail workflow:

1. Add metadata header: `# Owner:` and `# Relates-To:`
2. Include `workflow_dispatch` trigger for manual testing
3. Start in `WARN_ONLY: "true"` mode during rollout
4. Add entry to this index
5. Create or update related ADR/runbook

---

## Quick Reference

```text
PR Guardrails (Blocking)
├── pr-guardrails.yml          → Checklist + template + traceability
├── branch-policy.yml          → development → main only
├── adr-policy.yml             → ADR entry if labeled
├── changelog-policy.yml       → CL entry if labeled
├── ci-rds-request-validation.yml → RDS schema validation
└── session-capture-guard.yml  → Append-only session files

Resource Guards (Warn-Only)
├── rds-size-approval-guard.yml → Size tier approvals
└── rds-tfvars-drift-guard.yml  → Coupled/standalone sync

Scheduled
└── policy-enforcement.yml     → Daily compliance check
```

---

**Last Updated:** 2026-01-17
**Maintainer:** platform-team
