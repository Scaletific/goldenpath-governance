---
id: ADR-0093-automated-policy-enforcement
title: 'ADR-0093: Automated Policy Enforcement Framework'
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
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0093-automated-policy-enforcement
  - ADR-0095-self-service-registry-creation
  - ADR-0096-risk-based-ecr-controls
  - ADR-0098-standardized-pr-gates
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - CL-0053-daily-policy-enforcement-workflow
  - CL-0056-risk-based-ecr-controls
  - CL-0120
  - SCRIPTS_POLICIES
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
version: '1.0'
breaking_change: false
---

# ADR-0093: Automated Policy Enforcement Framework

## Status
Accepted

## Context

We need policies to be enforceable, not just documentation. Manual enforcement doesn't scale and policies become stale without automation.

## Decision

### 1. Machine-Readable Policies

Policies are defined as **YAML files** in `docs/governance/policies/`, not just markdown.

**Structure:**
```yaml
policy_id: POL-{DOMAIN}-{NUMBER}
version: "1.0"
status: "active"
owner: platform-team
rules:
  - rule_id: "{POLICY_ID}-R{NUMBER}"
    enforcement: "automated|manual"
    check_frequency: "on_creation|daily"
    violation_action: "block|alert|log"
```

### 2. Three-Layer Enforcement

**Layer 1: Prevention (Terraform Validation)**
- Block non-compliant resources at creation time
- Example: Validate naming conventions, metadata requirements

**Layer 2: Detection (Daily Compliance Checks)**
- GitHub Action queries AWS daily
- Compare actual state to policy rules
- Create GitHub issues for violations

**Layer 3: Remediation (Automated Fixes)**
- Safe fixes applied automatically (e.g., add lifecycle policy)
- Unsafe fixes require manual approval (e.g., delete registry)

### 3. Monitoring

**Dashboard:** Grafana showing compliance rate, violations, trends (planned)

**Reports:** Daily JSON report posted to Slack (planned)

**Alerts:**
- Critical: PagerDuty + Slack
- High: GitHub Issue + Slack
- Medium/Low: GitHub Issue

### 4. Policy Lifecycle

1. **Create:** Author YAML → PR review → Merge
2. **Enforce:** Terraform validation + daily checks
3. **Monitor:** Dashboard + reports
4. **Review:** Quarterly review meeting
5. **Update:** Update YAML → PR → Merge

## Consequences

**Pros:**
- Policies are enforceable (code, not docs)
- Measurable compliance (real-time visibility)
- Proactive detection (before incidents)
- Audit trail (for compliance frameworks)

**Cons:**
- Initial effort to build framework
- Ongoing maintenance of policies and scripts
- Potential for false positives
- Alert fatigue if not tuned

**Mitigations:**
- Phased rollout (start with ECR, expand gradually)
- Clear exception process
- Alert tuning based on feedback

## Related
- [ADR-0092: ECR Registry Product Strategy](./ADR-0092-ecr-registry-product-strategy.md)
