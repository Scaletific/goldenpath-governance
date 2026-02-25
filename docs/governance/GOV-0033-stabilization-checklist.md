---
id: GOV-0033-stabilization-checklist
title: 'PR #156: Stabilization & Compliance Checklist'
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 24_PR_GATES
  - ADR-0098-standardized-pr-gates
  - CL-0059-pr-156-stabilization
  - agent_session_summary
category: governance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
aliases:
  - PR-156-STABILIZATION-CHECKLIST
---

## PR #156: Stabilization & Compliance Checklist

This checklist documents the validation steps required for **PR #156** to ensure the ECR registry pipeline is stable and all governance gates pass deterministically.

## 1. Metadata Core Stabilization

- [x] **Shallow Copy Fix:** Verify `scripts/standardize_metadata.py` uses `copy.deepcopy()` to prevent metadata key truncation.
- [x] **Schema Compliance:** Run `python3 scripts/validate_metadata.py --path docs/` and confirm 100% pass rate.
- [x] **Header Injection:** Confirm all 388+ markdown files have valid YAML frontmatter.

## 2. CI/CD Workflow Alignment

- [x] **Pull Request Triggers:** Verify `.github/workflows/` files (Guardrails, ADR Policy, Changelog Policy, Metadata Validation) trigger on both `main` AND `development`.
- [x] **Guardrail Enforcement:** Confirm PR body contains the mandatory checklist selections from `.github/pull_request_template.md`.
- [x] **Branch Policy Guard:** Ensure `fix/metadata-compliance-dev` successfully targets `development`.

## 3. YAML & Linting Quality

- [x] **Duplicate Key Audit:** Confirm `enforcement:` block is consolidated in `docs/governance/policies/POL-ECR-*.yaml`.
- [x] **Catalog Indentation:** Verify `docs/20-contracts/resource-catalogs/*.yaml` comments use standardized 0-indentation to satisfy `yamllint`.
- [x] **Test Results:** Confirm `yamllint docs/governance/policies/ docs/20-contracts/resource-catalogs/` returns "ALL GREEN" locally.

## 4. Onboarding & Documentation

- [x] **ADR-0098:** Verify decision record created for Standardized PR Gates.
- [x] **CL-0059:** Verify changelog entry captures stabilization fixes.
- [x] **CONTRIBUTING.md:** Confirm branching strategy updated to `development -> main` flow.
- [x] **Walkthrough:** Confirm walkthrough documents the risk-based ECR controls and domain-based catalogs.

## 5. Verification Command Summary

```bash
# Validate metadata
python3 scripts/validate_metadata.py --path docs/

# Validate YAML linting
yamllint docs/governance/policies/POL-ECR-*.yaml docs/20-contracts/resource-catalogs/*.yaml

# Check branch current status
git branch --show-current
```
