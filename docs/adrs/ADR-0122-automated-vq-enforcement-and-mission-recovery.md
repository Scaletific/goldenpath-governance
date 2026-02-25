---
id: ADR-0122
title: 'ADR-0122: Automated VQ Enforcement and Mission Recovery'
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
  - ADR-0121-value-quantification-framework
  - ADR-0122
  - AGENT_FIRST_BOOT
  - CL-0078
  - VQ_PRINCIPLES
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

## ADR-0122: Automated VQ Enforcement and Mission Recovery

## Status

Accepted

## Context

With the introduction of the Value Quantification (VQ) framework ([ADR-0121](./ADR-0121-value-quantification-framework.md)), the platform now has a vocabulary for ROI. However, without automated enforcement, the application of VQ metadata relies on human memory and agent rigor, which is prone to drift. Agents, in particular, may over-engineer low-value tasks if not constrained by a value-led heuristic.

Additionally, as context windows fragment, both humans and agents need a "north star" mechanism to quickly re-align with the current 90-day strategy.

## Decision

We will implement three levels of automated VQ enforcement and mission recovery:

1. **Agent First-Boot Protocol**: Every AI agent must read [**`docs/onboarding/AGENT_FIRST_BOOT.md`**](../onboarding/AGENT_FIRST_BOOT.md) as a mandatory context anchor before beginning work.
2. **Mission Recovery (Pulse)**: Implement `bin/governance pulse` to provide an instant, terminal-based summary of the Platform Mission and VQ strategy.
3. **Hard Guardrails**: Update `scripts/pr_guardrails.py` to auto-detect AI-authored PRs and reject any that miss a valid `VQ Class` (e.g., `🔴 HV/HQ`) in the PR body.

## Consequences

- **Positive**: Zero "Dark Value" creation by agents; every agent action is now tied to a business impact bucket.
- **Positive**: Faster onboarding for new agents and humans via the "Pulse" command.
- **Positive**: Consistent ROI tracking enabled by mandatory PR classification.
- **Neutral**: Small increase in PR friction for agents (expected and desired "Anti-Friction" trade-off).
- **Negative**: Adds a specific dependency on the `PR_AUTHOR` environment variable in CI gates.

## Alternatives Considered

- **Human-only review**: Rejected due to high cognitive load and risk of inconsistency.
- **Agent-only tagging**: Rejected as it lacks the "Hard Gate" needed for reliable audit trails.
