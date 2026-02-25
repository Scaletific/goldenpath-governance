---
id: SCRIPTS_POLICIES
title: Policy Governance Framework
type: policy
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0093-automated-policy-enforcement
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
status: active
supported_until: '2028-01-01'
version: '1.0'
breaking_change: false
---

# Policy Governance Framework

**Version:** 1.0
**Owner:** Platform Team
**Last Updated:** 2026-01-05
**Status:** Planned

## Overview

This directory will contain machine-readable policies (YAML) that define governance rules for ECR registries. The goal is to automate policy enforcement rather than rely on manual reviews.

## Core Principles

1. **Machine-Readable:** Policies defined as YAML, not just markdown
2. **Automated Enforcement:** Terraform validation + daily compliance checks
3. **Version Controlled:** All changes tracked in Git

---

## Directory Structure

```
docs/governance/policies/                          # ← YAML policies (source of truth)
├── registry-governance.yaml            # POL-ECR-001 (planned)
├── image-scanning.yaml                 # POL-ECR-002 (planned)
├── lifecycle-retention.yaml            # POL-ECR-003 (planned)
└── README.md                           # This file

docs/governance/                        # ← Human-readable docs
├── registry-governance-policy.md       # References POL-ECR-001
├── image-scanning-policy.md            # References POL-ECR-002
└── lifecycle-retention-policy.md       # References POL-ECR-003

scripts/policy-enforcement/             # ← Automation (planned)
├── check-policy-compliance.py          # Daily compliance checker
├── enforce-registry-governance.py      # Checks POL-ECR-001
├── enforce-image-scanning.py           # Checks POL-ECR-002
└── enforce-lifecycle-retention.py      # Checks POL-ECR-003

.github/workflows/
└── policy-enforcement.yml              # Daily checks at 09:00 UTC (planned)
```

---

## Enforcement Approach

### Layer 1: Prevention (Terraform Validation)
Block non-compliant resources at creation time.

**Example:**
```hcl
variable "ecr_repositories" {
  validation {
    condition = alltrue([
      for name, repo in var.ecr_repositories :
      can(regex("^[A-Z0-9_]+$", repo.metadata.id))
    ])
    error_message = "Policy POL-ECR-001-R03: IDs must be UPPERCASE_WITH_UNDERSCORES"
  }
}
```

### Layer 2: Detection (Daily Checks)
GitHub Action queries AWS daily, compares to policy rules, creates issues for violations.

**Daily Check Flow:**
```
09:00 UTC - GitHub Action triggers
  ↓
Load policies from docs/governance/policies/*.yaml
  ↓
For each ECR registry in AWS:
  ├─ Check POL-ECR-001-R03: Has required metadata? ✅/
  ├─ Check POL-ECR-002-R01: Scanning enabled? ✅/
  ├─ Check POL-ECR-003-R01: Lifecycle policy exists? ✅/
  └─ Check POL-ECR-002-R04: CVEs remediated within SLA? ✅/
  ↓
Generate compliance report:
  - 5/6 registries compliant (83%)
  - 1 violation: wordpress-platform missing lifecycle policy
  ↓
Create GitHub issue: "Policy Violation: wordpress-platform"
  ↓
Send Slack alert to #platform-team
```

### Layer 3: Remediation (Automated Fixes)
Safe fixes applied automatically (e.g., add lifecycle policy). Unsafe fixes require manual approval.

---

## Monitoring (Planned)

- **Dashboard:** Grafana showing compliance rate, violations, trends
- **Daily Report:** JSON report posted to Slack
- **Alerts:** GitHub issues for violations

---

## Policy Lifecycle

1. **Create:** Author YAML policy → PR review → Merge
2. **Enforce:** Terraform validation + daily checks
   ```
   09:00 UTC - GitHub Action triggers
     ↓
   Load policies from docs/governance/policies/*.yaml
     ↓
   For each ECR registry in AWS:
     ├─ Check POL-ECR-001-R03: Has required metadata? ✅/
     ├─ Check POL-ECR-002-R01: Scanning enabled? ✅/
     ├─ Check POL-ECR-003-R01: Lifecycle policy exists? ✅/
     └─ Check POL-ECR-002-R04: CVEs remediated within SLA? ✅/
     ↓
   Generate compliance report:
     - 5/6 registries compliant (83%)
     - 1 violation: wordpress-platform missing lifecycle policy
     ↓
   Create GitHub issue: "Policy Violation: wordpress-platform"
     ↓
   Send Slack alert to #platform-team
   ```
3. **Monitor:** Dashboard + reports
4. **Review:** Quarterly review meeting
5. **Update:** Update YAML → PR → Merge

---

## Current Policies

| Policy ID | Name | Status |
|-----------|------|--------|
| POL-ECR-001 | Registry Governance | Planned |
| POL-ECR-002 | Image Scanning | Planned |
| POL-ECR-003 | Lifecycle Retention | Planned |

---

## Related Documents

- [ADR-0093: Automated Policy Enforcement](../adrs/ADR-0093-automated-policy-enforcement.md)
- [ADR-0092: ECR Registry Product Strategy](../adrs/ADR-0092-ecr-registry-product-strategy.md)
---

## Questions?

**Slack:** #platform-team
