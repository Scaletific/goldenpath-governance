---
id: ADR-0101-pr-metadata-auto-heal
title: 'ADR-0101: PR Metadata Auto-Heal and Scoped Validation'
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
  - GOV-0023-platform-governance
  - 01_adr_index
  - GOV-0029-pr-guardrails
  - GOV-0036-github-agent-roles
  - 24_PR_GATES
  - ADR-0098-standardized-pr-gates
  - ADR-0101-pr-metadata-auto-heal
  - ADR-0111-platform-documentation-auto-healing
  - CL-0063-pr-metadata-auto-heal
  - GOV-0047-metadata-maintenance-guide
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# ADR-0101: PR Metadata Auto-Heal and Scoped Validation

## Status
Accepted

## Context
The platform's metadata validation workflow was blocking PRs due to:
1. **Full-repo scanning**: Any `.md` file change triggered validation of the entire repository, causing unrelated failures
2. **Manual remediation**: Developers had to manually fix metadata issues, creating friction and slowing velocity
3. **No escape hatch**: No way to bypass validation for CI/infrastructure PRs that don't need governance checks

This friction contradicted the platform's "Born Governed" philosophy—governance should enable velocity, not block it.

## Decision

### 1. Scope Validation to Changed Files Only
The metadata validator now only checks files modified in the current PR, not the entire repository.

### 2. Auto-Heal Before Blocking
When metadata issues are detected, the workflow runs `standardize_metadata.py` to auto-fix issues and commits the changes. The PR continues without developer intervention.

### 3. Conditional Label Bypass (Validated, Not Trusted)
Labels are **claims** that must be **verified**. The workflow validates conditions before allowing bypass:

| Label | Condition | Who Can Use |
| :--- | :--- | :--- |
| `docs-only` | All changed files are `.md` | Anyone (verifiable) |
| `typo-fix` | < 50 lines changed, text files only | Anyone (verifiable) |
| `hotfix` | Target branch is `main` | Platform-team only |
| `build_id` | Terraform files changed | Platform-team only |

**Removed:** `governance-exempt` was removed as it provided unconditional bypass (security risk).

### 4. Python-Based Guardrails
The PR guardrails logic was rewritten as `scripts/pr_guardrails.py` to:
- Align with the platform's Python ecosystem
- Enable local testing
- Provide clear, structured error messages

## Consequences

### Positive
- **90% faster validation**: Only changed files are scanned
- **Zero-friction governance**: Auto-heal removes manual remediation
- **Consistent metadata**: All files get standardized frontmatter automatically
- **Escape hatch**: Exempt labels allow CI pipelines to proceed without governance overhead

### Negative
- **Unexpected commits**: Bot commits may surprise developers unfamiliar with auto-heal
- **Permissions**: Requires `contents: write` for the workflow to push commits
- **History noise**: Auto-heal commits appear in git log

### Mitigation
- Commit message includes `[skip ci]` to prevent infinite loops
- Clear logging explains what was auto-healed
- Exempt labels documented in workflow README
