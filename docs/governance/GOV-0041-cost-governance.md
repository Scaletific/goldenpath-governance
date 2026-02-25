---
id: GOV-0041-cost-governance
title: Cost Governance (Visibility First)
type: policy
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - GOV-0023-platform-governance
  - GOV-0042-resource-tagging
  - 40_COST_VISIBILITY
  - ADR-0076-platform-infracost-ci-visibility
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
aliases:
  - 06_COST_GOVERNANCE
---

# Cost Governance (Visibility First)

Doc contract:

- Purpose: Define cost visibility guardrails and decision ownership.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/governance/GOV-0023-platform-governance.md, docs/70-operations/40_COST_VISIBILITY.md, docs/adrs/ADR-0076-platform-infracost-ci-visibility.md, docs/governance/GOV-0042-resource-tagging.md

Cost governance ensures we expose cost impact early and consistently, without
slowing delivery. In V1, the emphasis is visibility and shared accountability,
not blocking gates.

## Principles

1. **Visibility before enforcement**
   - Surface cost impact on PRs before applying hard thresholds.

2. **Tagging enables attribution**
   - Cost awareness depends on the tag contract in
     `docs/governance/GOV-0042-resource-tagging.md`.

3. **Low-friction first**
   - Cost signals should be advisory and easy to adopt.

4. **Escalate based on evidence**
   - Add budget gates only after repeated drift or risk is observed.

## Current policy (V1)

- Terraform PRs must include a cost visibility signal when Infracost is
  configured (PR comment in CI).
- Cost visibility is **advisory** and does **not** block merges.
- Missing `INFRACOST_API_KEY` skips cost reporting to avoid failing CI.

## Ownership

- Platform team owns cost visibility tooling and updates.
- App teams review cost impact in PRs and document notable deltas.

## What triggers review

- Large or unexpected cost deltas in Infracost output.
- Unusual resource class changes (e.g., large instances, cross-region adds).

## Future escalation (when needed)

- Add diff baselines against `main`.
- Add budget thresholds for high-risk changes.
- Integrate cost signals into Backstage scorecards.
