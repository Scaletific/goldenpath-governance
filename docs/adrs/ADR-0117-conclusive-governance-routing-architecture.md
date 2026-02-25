---
id: ADR-0117-conclusive-governance-routing-architecture
title: Conclusive Governance Routing & Compliance Engine
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0117-conclusive-governance-routing-architecture
  - CL-0073-conclusive-governance-routing-architecture
  - GOV-0049-decision-routing-strategy
  - agent-routing.yaml
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-06
version: 1.0
date: 2026-01-06
breaking_change: false
---

## ADR-0117: Conclusive Governance Routing & Compliance Engine

## Context

As the platform grows, managing which teams review which changes (and what documentation is required) has become a manual overhead. Architectural rigor for high-risk areas like AI Agents and Security needs to be automated to ensure consistency.

## Decision

We will implement a **Conclusive Governance Matrix** and an automated compliance engine.

### 1. The Matrix ([`agent-routing.yaml`](../../schemas/routing/agent-routing.yaml))

- **100% Coverage**: Every domain and component in the platform is mapped to a mandatory path.
- **Unified Review**: The `platform-team` is a required reviewer for all changes.
- **Specialized Gates**: `security-team`, `operations-team`, and `sre-team` are automatically included for their respective domains.

### 2. Mandatory Artifacts

The routing engine enforces a "Born Governed" standard by requiring specific artifact types based on the change scope:

- **Core Changes**: Require an `ADR` and `Changelog`.
- **Agents/Policy**: Require dual-approval and full architectural documentation.
- **Operational Changes**: Require a `Changelog`.

### 3. Compliance Engine ([`validate_routing_compliance.py`](../../scripts/validate_routing_compliance.py))

A new CI gate will analyze Pull Requests to ensure:

- The metadata in changed files aligns with the routing matrix.
- All mandatory documentation (ADRs/CLs) is included in the PR commit set.

## Consequences

### Positive

- **Guaranteed Consistency**: Eliminates "silent" changes to critical foundation layers.
- **Distributed Review**: Reduces platform-team bottleneck by clearly routing to specialized owners.
- **Auditability**: Every PR is backed by the required architectural evidence.

### Negative

- **Discovery Complexity**: Developers must ensure metadata is correctly set for the routing engine to behave as expected.
