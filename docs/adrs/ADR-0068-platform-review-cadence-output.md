---
id: ADR-0068-platform-review-cadence-output
title: 'ADR-0068: Fix review cadence output delimiter'
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
  - ADR-0068-platform-review-cadence-output
  - CL-0017-review-cadence-output-delimiter
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0068: Fix review cadence output delimiter

- **Status:** Proposed
- **Date:** 2026-01-02
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `.github/workflows/production-readiness-review.yml`, PR #108

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

The production readiness review cadence workflow writes multi-line output to
`GITHUB_OUTPUT`. The current quoted heredoc delimiter breaks note parsing and
causes the check to fail even when the script runs correctly.

## Decision

We will **use an unquoted heredoc delimiter** when writing `GITHUB_OUTPUT` in the
review cadence workflow.

## Scope

Applies to the output handling in `production-readiness-review.yml` only.

## Consequences

### Positive

- Review cadence checks succeed when the script output is valid.

### Tradeoffs / Risks

- None.

### Operational impact

- None.

## Alternatives considered

- Keep the current delimiter and accept intermittent failures (rejected).

## Follow-ups

- None.

## Notes

This restores expected GitHub Actions output handling.
