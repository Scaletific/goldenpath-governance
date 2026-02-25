---
id: ADR-0138
title: 'ADR-0138: Automated Secret Scanning with Gitleaks and TruffleHog'
type: adr
status: proposed
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle:
  supported_until: 2028-01-10
  breaking_change: false
exempt: false
risk_profile:
  production_impact: low
  security_risk: high
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 01_adr_index
  - GOV-0040-secrets-catalog-policy
  - 35_SECRET_MANAGEMENT
  - ADR-0014-platform-ci-local-preflight-checks
  - ADR-0019-platform-pre-commit-hooks
  - ADR-0135
  - ADR-0138
  - ROADMAP
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
version: '1.0'
---

# ADR-0138: Automated Secret Scanning with Gitleaks and TruffleHog

- **Status:** Proposed
- **Date:** 2026-01-10
- **Owners:** `platform-team`
- **Domain:** Security
- **Decision type:** Security | Operations

---

## Context

As we transition to using **AWS Secrets Manager** and **External Secrets Operator (ESO)** for credential management, we must ensure that secrets do not bypass these governed systems and leak into the Git repository in plain text. Plain-text secrets in Git are a "Point of No Return" security event requiring complete rotation and history scrubbing.

## Decision

We will implement a multi-layered automated secret scanning strategy using **Gitleaks** and **TruffleHog**.

### 1. Shift-Left Protection (Local Pre-Commit)
- **Tool**: Gitleaks (CLI)
- **Integration**: Added to `.pre-commit-config.yaml`.
- **Action**: Prevent a commit if a secret pattern is detected. This ensures secrets never reach the `.git` directory on origin.

### 2. CI/CD Gatekeeping (GitHub Actions)
- **Tool**: Gitleaks + TruffleHog OSS
- **Integration**: Added to Pull Request workflows.
- **Action**:
    - **Gitleaks**: Scans the entire commit history of the PR for patterns.
    - **TruffleHog**: Scans and **verifies** identified secrets (AWS, GitHub, etc.) to confirm if the secret is active.

## Consequences

### Positive
- **Drift Prevention**: Forces developers to use the governed `aws_secrets_manager` module.
- **Reduced False Positives**: TruffleHog's verification engine ensures only actionable leaks break the build.
- **Auditability**: Every PR is programmatically audited for security compliance.

### Tradeoffs / Risks
- **Build Latency**: Scanning large codebases can add 30-60 seconds to CI runs.
- **Maintenance**: Rule sets must be updated periodically to catch new secret formats.

## Operational impact

- Developers must have Gitleaks installed locally or run via `pre-commit`.
- Security incidents (detected leaks) must trigger an immediate rotation of the leaked credential, even if the commit is blocked.

## Alternatives considered

### GitHub Secret Scanning (Native)
- **Pros**: Zero configuration, native to GitHub.
- **Cons**: Only scans after push; doesn't provide local pre-commit prevention for custom/proprietary secret formats.

### Snyk / Checkov
- **Status**: Already in use for general linting/vulnerability scanning, but Gitleaks/TruffleHog provide deeper, specialized secret verification.

## Follow-ups
- Update `.pre-commit-config.yaml` with Gitleaks hook.
- Create `.github/workflows/ci-secret-scan.yml`.
