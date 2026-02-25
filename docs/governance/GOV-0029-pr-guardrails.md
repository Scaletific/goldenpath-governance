---
id: GOV-0029-pr-guardrails
title: PR Guardrails (GoldenPath IDP)
type: policy
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 21_CI_ENVIRONMENT_CONTRACT
  - 24_PR_GATES
  - 27_REFACTORING_VALIDATION_GUIDE
  - ADR-0044-platform-infra-checks-ref-mode
  - ADR-0046-platform-pr-plan-validation-ownership
  - ADR-0063-platform-terraform-helm-bootstrap
  - ADR-0101-pr-metadata-auto-heal
  - ADR-0173-governance-doc-naming-migration
  - CL-0002-bootstrap-refactor
  - CL-0063-pr-metadata-auto-heal
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
aliases:
  - 04_PR_GUARDRAILS
---

# PR Guardrails (GoldenPath IDP)

Doc contract:

- Purpose: Define PR guardrails, labels, and enforcement workflows.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/40-delivery/38_BRANCHING_STRATEGY.md, docs/governance/GOV-0023-platform-governance.md

This document captures the current PR guardrails, how they are enforced, and
recommended best practices for keeping the platform safe and auditable.

## Scope

The governance model uses a **Dual-Speed** approach to balance developer velocity with production safety:

- **Strict Enforcement (`main`)**: All guardrails, policies, and metadata schemas are strictly enforced. PRs must be perfectly compliant.
- **Experimental Flow (`development`)**: Governance is advisory only. No required checks, to keep iteration fast.

## Guardrails in place

### Branch policy gate

- `main` only accepts PRs from `development`.
- Enforced by `/.github/workflows/branch-policy.yml`.

### PR checklist requirements

The PR template requires explicit selections for:

- Change Type
- Decision Impact
- Production Readiness
- Testing / Validation (link + run/command or N/A)
- Risk & Rollback (rollback plan / migration / N/A)

Enforced by `/.github/workflows/pr-guardrails.yml` and `scripts/pr_guardrails.py`.

### Conditional Bypass Labels (ADR-0101)

Certain labels can bypass the checklist requirement if validated conditions are met:

| Label | Condition | Who Can Use |
| --- | --- | --- |
| `docs-only` | All changed files are `.md` | Anyone |
| `typo-fix` | < 50 lines changed, text files only | Anyone |
| `hotfix` | Target branch is `main` | Platform-team only |
| `build_id` | Terraform files changed | Platform-team only |

Labels are **validated, not trusted**. If the condition is not met, the check fails.

Template enforcement:

- PR bodies must be based on `.github/pull_request_template.md`.
- Guardrails fail if the template header is missing or the body contains
  escaped newlines (`\\n`).

### Auto-labeling by path

PRs are labeled automatically based on touched paths:

- `infra`: envs/modules/bootstrap/gitops/workflows/scripts
- `governance`: docs/governance, docs/20-contracts, docs/90-doc-system
- `docs`: remaining docs paths
- `changelog-required`: infra + governance domains
- `adr-required`: modules/bootstrap/gitops/workflows/scripts + governance domains

Configured in `/.github/labeler.yml` and applied by
`/.github/workflows/pr-labeler.yml`.

### Required status checks (branch rulesets)

Ensure branch rulesets for `main` require these checks:

- `Yamllint`
- `PR Governance Gates / governance-gates`

Both lint checks run repo-wide to keep YAML and Markdown consistent as the
knowledge graph footprint expands.

### Minimal branch protection checklist (main)

- Require status checks: `PR Governance Gates / governance-gates`.
- Require branches to be up to date before merging.
- Require at least one human approval.
- Block force-pushes and deletions.

### Changelog gate

If `changelog-required` is present, a changelog entry is required:

- `docs/changelog/entries/CL-####-short-title.md`

If `changelog-exempt` is present, the changelog gate is skipped.

Enforced by `/.github/workflows/changelog-policy.yml`.

### ADR gate

If `adr-required` is present, an ADR entry is required:

- `docs/adrs/ADR-####-short-title.md`

Enforced by `/.github/workflows/adr-policy.yml`.

## Testing / Validation guidance

Purpose: make proof visible and consistent.

- Include a plan/apply link when infrastructure changes are touched.
- Provide test commands or workflow run IDs for app/platform changes.
- Use "Not applicable" only when no validation is possible (document why).

## Risk & rollback guidance

Purpose: force explicit acknowledgment of recovery paths.

- Provide rollback notes when changes affect production paths.
- Flag data migrations explicitly (including irreversible changes).
- Use "Not applicable" only when no rollback is necessary.

## Infra plan workflow note

We treat `infra-terraform.yml` as a **manual-only** validation workflow. It is
optional and not required as a gate for PR apply flows. The default plan source
remains the PR plan workflow.

References:

- `docs/adrs/ADR-0046-platform-pr-plan-validation-ownership.md`
- `docs/adrs/ADR-0044-platform-infra-checks-ref-mode.md`
- `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

## Bootstrap guardrails reference

Bootstrap guardrails and refactors are documented here:

- `docs/adrs/ADR-0063-platform-terraform-helm-bootstrap.md`
- `docs/changelog/entries/CL-0002-bootstrap-refactor.md`
- `docs/40-delivery/27_REFACTORING_VALIDATION_GUIDE.md`

## Best-practice recommendations

- Keep the PR checklist short but mandatory; avoid optional-only sections.
- Require plan/apply links for infra changes to preserve auditability.
- Require a rollback note when touching bootstrap, CI, or infra contracts.
- Auto-label PRs by path and let labels drive ADR/changelog requirements.
- Keep guardrails “thin”: fail fast on missing metadata, not on content quality.

## Main branch hard-lock (required)

Use branch rulesets to enforce the development-only path:

- Require PRs (no direct pushes) to `main`.
- Require the `enforce-development-only` check.
- Require at least one human approval.
- Block force-pushes and deletions.
- Optional: require linear history to avoid drift.
- Exception: allow build-id branches (`build-<dd-mm-yy-NN>` or `build/<dd-mm-yy-NN>`) to merge to `main` for build validation.

## Future options (not enabled)

- Require PR reviews on `main` (adds approval gate, prevents self-merge).
- Enforce CODEOWNERS for infra/governance paths.
