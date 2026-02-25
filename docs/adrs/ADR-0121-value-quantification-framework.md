---
id: ADR-0121-value-quantification-framework
title: Value Quantification (VQ) Framework
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
  production_impact: none
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0121-value-quantification-framework
  - ADR-0122
  - CAPABILITY_LEDGER
  - CL-0077-value-quantification-framework
  - CL-0082-value-heartbeat-roi-telemetry
  - CL-0120
  - SESSION_CAPTURE_2026_01_20_VQ
  - VQ_TAGGING_GUIDE
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-07
---

## ADR-0121: Value Quantification (VQ) Framework

## Status

Accepted

## Context

As the Golden Path Platform grows, engineering efforts often become "invisible" to business stakeholders. Manual governance, schema refactors, and pipeline optimizations are critical for stability but are frequently viewed as overhead. We need a way to quantify the financial and operational value of platform work to drive ROI-based prioritization and resource allocation.

## Decision

We will implement a **Value Quantification (VQ) Framework** that integrates directly with our existing metadata governance model.

### The 4 VQ Rules

1. **Metadata Tagging**: Every automation script and workflow will carry a `value_quantification` object in its metadata sidecar (`metadata.yaml`).
2. **Impact Tiers**: Assets will be categorized into `tier-1` (Mission Critical), `tier-2`, `tier-3`, or `low` based on their business impact.
3. **Reclaim Metrics**: We will track `potential_savings_hours` per asset usage to calculate the aggregate "Engineering Reclaim" provided by the platform.
4. **HITL Alignment**: VQ metrics will be used to identify high-friction governance gates and transition them into "Human-In-The-Loop" (HITL) auto-healing guidance.

## Consequences

- **Positive**: Platform work becomes financially quantifiable; prioritization is driven by data rather than intuition; developer friction is systematically identified and reduced.
- **Negative**: Adds a small metadata maintenance overhead for new automation assets.
- **Neutral**: Requires engineers to adopt a "Value Provider" mindset when creating new capabilities.

## References

- [VQ_PRINCIPLES.md](../product/VQ_PRINCIPLES.md)
- [VQ_TAGGING_GUIDE.md](../product/VQ_TAGGING_GUIDE.md)
- [CAPABILITY_LEDGER.md](../product/CAPABILITY_LEDGER.md)

### Implementation

- `cost_logger.py`: Provides automated ROI and spend telemetry for governance reporting.
