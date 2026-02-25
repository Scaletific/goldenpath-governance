---
id: ADR-0098-standardized-pr-gates
title: 'ADR-0098: Standardized PR Gates for ECR Pipeline'
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
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0093-automated-policy-enforcement
  - ADR-0098-standardized-pr-gates
  - ADR-0101-pr-metadata-auto-heal
  - CL-0059-pr-156-stabilization
  - GOV-0033-stabilization-checklist
  - GOV-0030-pr-guardrails-index
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-12-31
version: 1.0
breaking_change: false
---

## ADR-0098: Standardized PR Gates for ECR Pipeline

## Context

The ECR pipeline PRs were experiencing repeated CI failures due to inconsistent guardrail checks, YAML linting errors, and missing metadata. Multiple workflows needed to trigger on both `main` and `development` branches, and the PR template required explicit checklist selections.

## Decision

We introduce a unified set of PR gate workflows that enforce:

- Mandatory checklist selections in the PR body.
- Consistent `pull_request` triggers for all relevant CI jobs.
- Centralized YAML linting and pre‑commit formatting.
- Automated metadata validation.

All future PRs targeting `development` or `main` must pass these gates before merge.

## Consequences

### Positive

- CI checks become deterministic and pass reliably.
- Reduced manual re‑work for reviewers.
- Clear governance for ECR‑related changes.

### Trade‑offs / Risks

- Slight increase in CI runtime due to additional linting steps.
- Contributors must keep the PR template up‑to‑date.

### Operational Impact

- Documentation updated (this ADR, changelog entry).
- Existing PRs may need to be rebased to satisfy new checks.

## Alternatives considered

- Keep existing ad‑hoc guardrails – rejected due to high failure rate.
- Disable linting – rejected because code quality would degrade.

## Follow‑ups

- Update the PR template to include the required checkboxes.
- Communicate the new process to all engineering teams.
