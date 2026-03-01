---
id: GOV-0024-governance-model
title: Governance Model – Golden Path IDP (Deprecated)
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
  - 05_OBSERVABILITY_DECISIONS
  - 28_SECURITY_FLOOR_V1
  - 29_CD_DEPLOYMENT_CONTRACT
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
status: deprecated
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
aliases:
  - 02_GOVERNANCE_MODEL
---

# Governance Model – Golden Path IDP (Deprecated)

Doc contract:

- Purpose: Record the previous V1 governance draft for reference.
- Owner: platform
- Status: deprecated
- Review cadence: as needed
- Related: docs/governance/GOV-0023-platform-governance.md, docs/50-observability/05_OBSERVABILITY_DECISIONS.md, docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md, docs/60-security/28_SECURITY_FLOOR_V1.md

This draft has been consolidated to reduce duplication and keep governance
authoritative.

Use these sources instead:

- Governance principles, operating model, and Backstage lens:
  `docs/governance/GOV-0023-platform-governance.md`
- Observability ownership and tooling boundaries:
  `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`
- Delivery and change control contracts:
  `docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md`
- Security baseline:
  `docs/60-security/28_SECURITY_FLOOR_V1.md`
