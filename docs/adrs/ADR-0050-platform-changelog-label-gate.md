---
id: ADR-0050-platform-changelog-label-gate
title: 'ADR-0050: Label-gated changelog entries'
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
  - 40_CHANGELOG_GOVERNANCE
  - ADR-0050-platform-changelog-label-gate
  - DOCS_CHANGELOG_README
  - METADATA_STRATEGY
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0050: Label-gated changelog entries

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md`, `docs/changelog/README.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Changelog updates are required for material behavior changes but not for
mechanical refactors or formatting fixes. A lightweight gate is needed to
require entries only when change impact warrants it, without slowing iteration
for low-risk edits.

---

## Decision

Changelog entries will be required only when a PR carries the label
`changelog-required`. CI will enforce the label gate by checking for a
`docs/changelog/entries/CL-####-*.md` entry whenever the label is present.

---

## Scope

Applies to platform repositories that use the changelog policy and template.
Does not enforce changelog entries for PRs without the label.

---

## Consequences

### Positive

- Changelog entries are created only for material, user-visible changes.
- Enforcement is explicit and easy to audit.
- Low-risk edits remain fast and lightweight.

### Tradeoffs / Risks

- Relies on label discipline and reviewer attention.
- A missed label can omit a changelog entry.

### Operational impact

- Reviewers apply the label when required change types are present.
- PR authors add a changelog entry when the label is applied.

---

## Alternatives considered

- Always require a changelog entry: rejected as too heavy for frequent
  iterations.
- No changelog enforcement: rejected due to drift in user-facing visibility.

---

## Follow-ups

- Add the `changelog-required` label to the repository.
- Add the CI workflow that enforces the label gate.
- Document the label policy and entry template.

---

## Notes

Label-gated enforcement can evolve into a stronger policy if adoption is
inconsistent.
