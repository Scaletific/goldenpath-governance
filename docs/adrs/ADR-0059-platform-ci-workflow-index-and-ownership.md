---
id: ADR-0059-platform-ci-workflow-index-and-ownership
title: 'ADR-0059: CI workflow index, ownership, and UI grouping'
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
  - ADR-0059-platform-ci-workflow-index-and-ownership
  - CI_WORKFLOWS
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0059: CI workflow index, ownership, and UI grouping

Filename: `ADR-0059-platform-ci-workflow-index-and-ownership.md`

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations | Governance
- **Related:** `ci-workflows/CI_WORKFLOWS.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

The CI workflow list is growing. Without a single index, naming conventions,
and clear ownership markers, workflows become hard to find, easy to misuse,
and harder to audit. This creates operational risk, slows onboarding, and
increases the chance of drift between docs and automation.

---

## Decision

We will:

- Maintain a single workflow index at `ci-workflows/CI_WORKFLOWS.md` listing
  name, trigger, owner, inputs, purpose, and runbook links.
- Prefix workflow names for UI grouping (Policy/Plan/Apply/Bootstrap/Ops/Quality).
- Add an owner comment line to each workflow YAML.
- Add a runbook link to each workflow’s `GITHUB_STEP_SUMMARY`.

---

## Scope

Applies to:

- All workflows under `.github/workflows/`.

Does not apply to:

- External automation outside this repo.

---

## Consequences

### Positive

- Clear discoverability and accountability.
- Faster onboarding and fewer misuse incidents.
- Easier audit and change review.

### Tradeoffs / Risks

- Requires ongoing upkeep when workflows change.
- Adds a small amount of maintenance overhead per workflow update.

### Operational impact

- Contributors must update the workflow index when adding or renaming workflows.
- Workflow changes include owner line and runbook summary updates.

---

## Alternatives considered

- **Do nothing:** rejected due to growing workflow sprawl and poor discoverability.
- **Single README only:** rejected because it would not improve UI grouping or
  ownership clarity in workflows themselves.

---

## Follow-ups

- Add and maintain `ci-workflows/CI_WORKFLOWS.md`.
- Apply naming prefixes across existing workflows.
- Add owner comment and runbook summary links to each workflow.

---

## Notes

If these conventions become too heavy, revisit and simplify the requirements
while preserving a single index and clear ownership.
