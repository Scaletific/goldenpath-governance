---
id: GOV-0025-governance-backstage
title: Backstage Governance (Deprecated)
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
  - 18_BACKSTAGE_MVP
  - ADR-0008-app-backstage-portal
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
  - 03_GOVERNANCE_BACKSTAGE
---

# Backstage Governance (Deprecated)

Doc contract:

- Purpose: Preserve the previous Backstage governance mapping for reference.
- Owner: platform
- Status: deprecated
- Review cadence: as needed
- Related: docs/governance/GOV-0023-platform-governance.md, docs/00-foundations/18_BACKSTAGE_MVP.md, docs/adrs/ADR-0008-app-backstage-portal.md

Backstage governance guidance has been consolidated into
`docs/governance/GOV-0023-platform-governance.md` under **Backstage Governance Lens (Summary)** to avoid
duplication.
