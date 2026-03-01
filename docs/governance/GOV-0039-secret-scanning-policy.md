---
id: GOV-0039-secret-scanning-policy
title: Secret Scanning Policy (Gitleaks)
type: policy
domain: security
risk_profile:
  production_impact: low
  security_risk: high
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - GOV-0029-pr-guardrails
  - GOV-0028-governance-testing
  - CL-0100
tags:
  - security
  - secrets
  - gitleaks
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
supported_until: 2028-01-10
version: '1.0'
breaking_change: false
aliases:
  - 10_SECRET_SCANNING_POLICY
---

# Secret Scanning Policy (Gitleaks)

Doc contract:

- Purpose: Prevent secrets from entering the repository.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/governance/GOV-0029-pr-guardrails.md

## Scope

This policy applies to all code and documentation committed to the repository.

## Requirements

### Local (Pre-commit)

- Developers must run pre-commit locally before pushing changes.
- Gitleaks is included in `.pre-commit-config.yaml` and runs on staged files.

Install once:

```bash
pre-commit install
```

### CI (PR to main)

- `Security - Gitleaks` runs on every PR targeting `main`.
- A finding fails the check and blocks merge.

## Handling Findings

1. Remove the secret from the commit.
2. Rotate the secret immediately.
3. If the secret is in Git history, coordinate a rewrite with platform.

## Allowlisting

- Only allowed for known false positives.
- Add allowlist entries to `.gitleaks.toml` with justification.
- Document the exception in the PR summary and changelog if needed.

## Enforcement

- Local pre-commit + CI checks are mandatory.
- Bypass requires platform approval and documented rationale.
