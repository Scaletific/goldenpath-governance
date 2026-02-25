---
id: ADR-0163
title: Agent Collaboration Governance and Living Registry
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
  - GOV-0034-ai-agent-governance
  - GOV-0036-github-agent-roles
  - GOV-0037-agent-collaboration-matrix
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0163
  - ADR-0176
  - CAPABILITY_LEDGER
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - agents
  - governance
  - collaboration
  - security
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-16
deciders:
  - platform-team
---

## Status

Accepted

## Context

The platform now relies on multiple AI agents running locally and in CI. We
already have policy guardrails for agents, but we lack a single, living source
of truth that defines who each agent is, which model it uses, and what it is
allowed to do. Without this registry, permissions sprawl and audits become
reactive.

We need a durable collaboration model that is explicit, least-privilege, and
auditable, while preserving fast iteration.

## Decision

Adopt a formal agent collaboration model backed by a living registry. The
registry will define:

- Agent names, models, and roles.
- Responsibilities and collaboration boundaries.
- Runtime context (local vs CI) and access profiles.
- Approval requirements for sensitive changes.

The living registry is the source of truth:
`docs/governance/GOV-0037-agent-collaboration-matrix.md`, including explicit
environment access levels (local/CI/cluster/cloud) per agent.

Each agent session must append to the immutable session log at
`session_summary/agent_session_summary.md`.

## Scope

Applies to all AI agents operating in this repository and any CI workflows that
use agent credentials. This does not change human ownership or approval
requirements; all merges still require human review.

## Consequences

### Positive

- Clear ownership and accountability for each agent.
- Predictable security posture via least-privilege access.
- Faster onboarding and troubleshooting.

### Tradeoffs / Risks

- Ongoing maintenance overhead for the registry.
- Additional review burden for permission changes.

### Operational impact

- Update the registry before enabling new agents.
- Require security review for permission changes.
- Add a changelog entry when collaboration changes are implemented.

## Alternatives considered

- Ad hoc agent usage without a registry (rejected due to audit gaps).
- Shared tokens across agents (rejected due to poor isolation).

## Follow-ups

1. Create and maintain the living registry document.
2. Align GitHub App/PAT permissions with the registry.
3. Add a changelog entry after implementation.
