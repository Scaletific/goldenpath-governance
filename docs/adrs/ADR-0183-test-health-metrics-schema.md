---
id: ADR-0183-test-health-metrics-schema
title: 'ADR-0183: Test Health Metrics Schema Contract'
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
  maturity: 1
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0090-automated-platform-health-dashboard
  - CL-0197-test-health-metrics-multi-source
  - GOV-0016-testing-stack-matrix
  - PRD-0007-platform-test-health-dashboard
  - session-2026-01-26-tdd-foundation-and-testing-stack
supersedes: []
superseded_by: []
tags:
  - testing
  - governance
  - observability
inheritance: {}
supported_until: 2028-01-26
version: 1.0
breaking_change: false
---

# ADR-0183: Test Health Metrics Schema Contract

Filename: `ADR-0183-test-health-metrics-schema.md`

- **Status:** Accepted
- **Date:** 2026-01-26
- **Owners:** platform-team
- **Domain:** Platform
- **Decision type:** Governance | Observability
- **Related:** PRD-0007, GOV-0016, ADR-0090

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.

---

## Context

Test results and coverage are emitted by multiple frameworks across multiple
repos. Without a stable contract, dashboards can drift, silently drop fields,
or report false-green states. A schema contract is required to keep test health
metrics deterministic, auditable, and compatible across repos.

---

## Decision

We will define and enforce a **Test Health Metrics Schema Contract** for all
test/coverage outputs used by `PLATFORM_HEALTH.md` and the Test Health dashboard.

---

## Scope

**Applies to**
- Test metrics payloads produced by `goldenpath-infra` and
  `goldenpath-backstage`.
- Governance-registry artifacts used to render `PLATFORM_HEALTH.md`.
- Scripts: `scripts/collect_test_metrics.py`, `scripts/generate_test_proofs.py`, `scripts/record-test-metrics.sh`.

**Does not apply to**
- Raw framework outputs (JUnit, coverage XML/JSON) before normalization.

---

## Consequences

### Positive

- Prevents false-green dashboards caused by missing or malformed fields.
- Ensures deterministic, cross-repo compatibility.
- Enables validation gates and auditability.

### Tradeoffs / Risks

- Adds a small maintenance cost for schema changes.
- Requires coordination when new fields are introduced.

### Operational impact

- CI pipelines must emit schema-compliant payloads.
- Validation failures must be addressed before reporting.

---

## Alternatives considered

1) **No schema**: rejected due to drift and false-green risk.
2) **Ad-hoc per repo**: rejected due to fragmentation and lack of comparability.

---

## Follow-ups

- Implement schema validation for the normalized payload.
- Update CI to emit schema-compliant test health metrics.
- Integrate validated metrics into `PLATFORM_HEALTH.md`.

---

## Notes

If the schema must change, create a new ADR and version the payload to avoid
breaking consumers.
