---
id: pull_request_template
title: Pull Request Template
type: template
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
lifecycle: active
version: 1.0
relates_to:
  - 24_PR_GATES
  - GOV-0029-pr-guardrails
supported_until: 2028-01-01
breaking_change: false
---

Select at least one checkbox per section by changing `[ ]` to `[x]`.

## Change Type
- [ ] Feature
- [ ] Bug fix
- [ ] Infra change
- [ ] Governance / Policy

## Decision Impact
- [ ] Requires ADR
- [ ] Updates existing ADR
- [ ] No architectural impact

## Production Readiness
- [ ] Readiness checklist completed
- [ ] No production impact

## Testing / Validation
- [ ] Plan/apply link provided (paste below)
- [ ] Test command or run ID provided (paste below)
- [ ] Not applicable

Testing/Validation details:
- Plan/apply link:
- Test command/run:

## Code Audit (PROMPT-0013)
- [ ] Post-implementation audit completed — all critical/high findings resolved
- [ ] Audit not applicable (docs-only, typo, or config change)

## Risk & Rollback
- [ ] Rollback plan documented (link or notes below)
- [ ] Data migration required
- [ ] No data migration
- [ ] Not applicable

Rollback notes/link:

## Notes / Summary (optional)
-
