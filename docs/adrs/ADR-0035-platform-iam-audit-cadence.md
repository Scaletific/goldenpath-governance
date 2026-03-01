---
id: ADR-0035-platform-iam-audit-cadence
title: 'ADR-0035: IAM Audit Cadence for CI Roles'
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
  - ADR-0035-platform-iam-audit-cadence
  - RB-0003-iam-audit
  - ROADMAP
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0035: IAM Audit Cadence for CI Roles

- **Status:** Proposed
- **Date:** 2025-12-28
- **Owners:** Platform (GoldenPath IDP)
- **Decision type:** Security / Governance
- **Related:** docs/governance/GOV-0023-platform-governance.md, docs/60-security/33_IAM_ROLES_AND_POLICIES.md

## Context

CI roles are intentionally broad during early iterations to keep the platform
moving. Over time, unused permissions should be removed to reduce risk and
increase confidence in least-privilege access. Today, we do not have a defined
cadence or trigger for auditing these roles.

We need a lightweight, repeatable process that:

- identifies unused permissions
- avoids slowing delivery
- allows tightening once the platform is stable

## Decision

GoldenPath will institute a periodic IAM audit for CI roles (and key platform
roles) using CloudTrail and IAM Access Analyzer.

The audit will be triggered:

- after a stability milestone (e.g., successful multi-env CI runs), or
- on a periodic cadence (e.g., quarterly)

The outcome of each audit is a documented change set to remove unused actions
from CI roles, with changes captured in PRs.

## Consequences

### Positive

- Reduces excess permissions based on real usage.
- Creates a habit of least-privilege maintenance.
- Aligns security posture with platform maturity.

### Tradeoffs

- Requires periodic time from the platform team.
- Some permissions may need to be re-added if future needs change.

## Alternatives Considered

- **No audits:** rejected due to growing security risk over time.
- **Continuous hard gates:** rejected for V1 because it would slow iteration.

## Follow-ups

- Add an IAM audit runbook (CloudTrail filter + Access Analyzer review steps).
- Create a checklist for tightening CI role policies.
