---
id: ADR-0080-platform-github-agent-roles
title: 'ADR-0080: GitHub App Roles for AI/Automation Access'
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
  - ADR-0080-platform-github-agent-roles
  - CL-0033-github-agent-roles
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0080: GitHub App Roles for AI/Automation Access

Date: 2026-01-03
Status: Proposed
Owners: platform

## Context

We need a way to grant AI and automation roles without creating new human
GitHub accounts. The solution must be auditable, least-privilege, and easy to
rotate.

## Decision

Adopt GitHub Apps as the default mechanism for AI/automation access, with
minimal permissions scoped to specific repositories.

## Consequences

**Positive**

- Fine-grained permissions and auditability.
- Tokens are short-lived and easier to rotate.
- No human accounts required.

**Negative**

- Requires App setup and lifecycle management.
- Additional documentation and onboarding steps.

## Alternatives considered

1. **Service accounts (bot users)**
   - Rejected: requires additional user accounts and broader permissions.
2. **Personal access tokens**
   - Rejected: long-lived secrets, higher risk and poorer auditability.

## Related

- docs/governance/GOV-0036-github-agent-roles.md
- docs/governance/GOV-0034-ai-agent-governance.md
