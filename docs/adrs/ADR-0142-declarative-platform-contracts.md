---
id: ADR-0142
title: 'ADR-0142: Strategic Adoption of Declarative Platform Contracts'
type: adr
domain: governance
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
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0142
  - ADR-0144
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

## ADR-0142: Strategic Adoption of Declarative Platform Contracts

## Status

Proposed

## Context

As the Golden Path IDP scales, the gap between developer intent and infrastructure implementation (Terraform, Helm, IAM) is widening. Currently, infrastructure requests are handled via manual code changes or complex, low-level YAML that requires deep cloud knowledge.

## Decision

We will adopt a Declarative Platform Contract pattern using a Kubernetes-style schema (apiVersion, kind, metadata, spec). All new platform capabilities must be exposed via these high-level contracts.

## Rationale

* Abstraction: Developers focus on "What" they need (Intent), not "How" it's built (Implementation).
* Decoupling: We can change the backend (e.g., AWS to Vault) without changing the developer's YAML.
* Governance: Contracts allow for automated validation (risk-tiers, mandatory approvals) before resources are provisioned.
