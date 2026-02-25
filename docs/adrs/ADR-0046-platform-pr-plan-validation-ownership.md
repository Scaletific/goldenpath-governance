---
id: ADR-0046-platform-pr-plan-validation-ownership
title: 'ADR-0046: PR plan owns validation (no auto infra checks dispatch)'
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
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - GOV-0029-pr-guardrails
  - 21_CI_ENVIRONMENT_CONTRACT
  - 36_STATE_KEY_STRATEGY
  - ADR-0044-platform-infra-checks-ref-mode
  - ADR-0046-platform-pr-plan-validation-ownership
  - READINESS_CHECKLIST
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0046: PR plan owns validation (no auto infra checks dispatch)

Filename: `ADR-0046-platform-pr-plan-validation-ownership.md`

- **Status:** Proposed
- **Date:** 2025-12-30
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `.github/workflows/pr-terraform-plan.yml`, `.github/workflows/infra-terraform.yml`, `.github/workflows/infra-terraform-apply-dev.yml`, `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`, `docs/70-operations/36_STATE_KEY_STRATEGY.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

The PR plan workflow has been dispatching Infra Terraform Checks automatically.
This adds an extra workflow hop and creates confusion about what must run before
apply. We already enforce the critical validations (fmt, validate, and
lifecycle/build_id guards) inside the PR plan, so the extra dispatch is
redundant for the default PR-driven flow.

Constraints:

- Keep the PR flow simple and deterministic.
- Preserve an optional manual checks path for operators.
- Avoid breaking apply guardrails that require a successful plan.

---

## Decision

We will remove the auto-dispatch of `infra-terraform.yml` from
`pr-terraform-plan.yml`. The PR plan workflow will remain the authoritative
validation gate by running:

- `terraform fmt -check`
- `terraform validate`
- lifecycle/build_id guards and state key resolution

`infra-terraform.yml` remains available as a **manual-only** checks workflow for
operators who want an extra validation pass.

---

## Scope

Applies to:

- PR-driven plan flow (`pr-terraform-plan.yml`)
- CI docs that describe the PR → apply path

Does not apply to:

- Manual checks (`infra-terraform.yml`)
- Apply workflows and their plan prerequisites

---

## Consequences

### Positive

- Removes a redundant workflow hop in the PR flow.
- Reduces confusion about which checks are required before apply.
- Keeps validations close to the plan that operators review.

### Tradeoffs / Risks

- Operators lose automatic infra checks on a second ref.
- Teams that relied on auto-dispatched infra checks must run them manually.

### Operational impact

- PR plan remains the default gate for apply.
- Optional manual checks are run via `infra-terraform.yml` when desired.

---

## Alternatives considered

- **Keep auto-dispatch with ref mode:** rejected as redundant complexity for the
  default PR flow.
- **Add another workflow layer:** rejected to avoid extra hops and confusion.

---

## Follow-ups

- Update CI docs to remove auto-dispatch references.
- Mark ADR-0044 as superseded by this decision.

---

## Notes

This decision reduces workflow coupling while keeping an optional manual checks
path for deeper validation when needed.
