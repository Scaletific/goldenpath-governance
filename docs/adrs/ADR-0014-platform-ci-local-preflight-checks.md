---
id: ADR-0014-platform-ci-local-preflight-checks
title: 'ADR-0014: Local preflight checks before PRs'
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
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0014-platform-ci-local-preflight-checks
  - ADR-0138
  - CL-0107
  - CL-0108
  - CL-0109
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0014: Local preflight checks before PRs

- **Status:** Proposed
- **Date:** 2025-12-26
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `.github/workflows/infra-terraform.yml`

---

## Context

We want consistent, low-friction quality gates while avoiding false confidence from local tooling
that does not perfectly match CI. Teams should run fast, local checks before opening PRs, but CI
remains the source of truth for merge decisions.

---

## Decision

> We will require a minimal set of local preflight checks before PRs and treat CI as the
> authoritative gate. `act` is recommended for workflow changes, not required.

Local preflight baseline (as applicable):

- Lint/format (e.g., pre-commit hooks or project lint scripts).
- Unit tests where available.
- Terraform `fmt` and `validate` for infra changes.

`act` guidance:

- Recommended when editing GitHub Actions workflows.
- Not a merge gate; differences from GitHub runners are expected.

---

## Scope

Applies to contributors and PRs in this repository. Does not require perfect parity between local
and CI execution environments.

---

## Consequences

### Positive

- Faster feedback before PRs and fewer avoidable CI failures.
- Clear expectation that CI remains authoritative.

### Tradeoffs / Risks

- Local results can differ from CI, producing false positives or negatives.
- Additional contributor overhead if tooling is not well documented.

### Operational impact

- Document recommended local checks in contributor guidance.
- Maintain small, stable local scripts to keep friction low.

---

## Alternatives considered

- Mandate `act` as a hard gate (rejected: mismatch with CI can create false positives).
- CI-only checks (rejected: slower feedback loop and more churn).

---

## Follow-ups

- Add a short checklist in `CONTRIBUTING.md`.
- Consider a lightweight pre-commit configuration for lint/format checks.

---

## Notes

If local/CI drift becomes frequent, prioritize fixing the CI workflows and tool versions.
