---
id: ADR-0079-platform-ai-agent-governance
title: 'ADR-0079: AI Agent Governance and Auditability'
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
  - GOV-0034-ai-agent-governance
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0079-platform-ai-agent-governance
  - AI_CHANGELOG
  - CL-0032-ai-agent-governance
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0079: AI Agent Governance and Auditability

Date: 2026-01-03
Status: Proposed
Owners: platform

## Context

AI agents are increasingly used for documentation, workflow updates, and
automation changes. Without explicit governance, changes risk drift, poor
traceability, and inconsistent QA.

We need lightweight rules that preserve speed while ensuring auditability,
guardrails, and reproducible outcomes.

## Decision

Adopt an AI governance layer with three concrete artifacts and a tiered
authority model:

1. `docs/governance/GOV-0034-ai-agent-governance.md`
   - Defines authority, guardrails, auditability, QA expectations, and
     escalation rules.
2. `docs/onboarding/26_AI_AGENT_PROTOCOLS.md`
   - Detailed operating procedures aligned to governance policy.
3. `docs/90-doc-system/AI_CHANGELOG.md`
   - A living ledger to record AI-driven changes with evidence.

The tiered model defines what actions are allowed per risk class (read-only,
write isolated, safe execution, human-only high risk).

## Consequences

**Positive**

- Clear rules for safe AI use, with traceable evidence.
- Faster onboarding and fewer repeated debates.
- Consistent QA expectations (green gate, evidence links).

**Negative**

- Additional documentation overhead per change.
- Requires discipline to keep the ledger and references current.

## Alternatives considered

1. **No formal governance, rely on ad-hoc reviews.**
   - Rejected: insufficient auditability and inconsistent QA.
2. **Only add protocols (no governance policy).**
   - Rejected: protocols alone lack enforcement and escalation rules.
3. **Tooling-only enforcement (no docs).**
   - Rejected: obscures reasoning and reduces transferability.

## Related

- docs/governance/GOV-0034-ai-agent-governance.md
- docs/onboarding/26_AI_AGENT_PROTOCOLS.md
- docs/90-doc-system/AI_CHANGELOG.md
