---
id: GOV-0052-platform-health-guide
title: Platform Health Dashboard Guide
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
  - ADR-0090-automated-platform-health-dashboard
  - GOV-0046-metadata-injection-guide
  - PLATFORM_HEALTH
category: governance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
aliases:
  - PLATFORM_HEALTH_GUIDE
---

## Platform Health Dashboard Guide

The `PLATFORM_HEALTH.md` file at the repository root is the "Single Source of Truth" for the operational status, compliance, and governance reach of the GoldenPath IDP.

## Purpose & Usage

### 1. Operational Intelligence

The dashboard provides leadership and platform engineers with a high-level view of:

- **Metadata Compliance**: What percentage of our resources carry standardized governance data?
- **Lifecycle Distribution**: How many components are "Active" vs. "Draft" or "Deprecated"?
- **Risk Distribution**: What is our footprint of "High Impact" production resources?

### 2. Dark Infrastructure Detection

The **"Injection Coverage"** metric is specifically designed to identify "Dark Infrastructure." It cross-references our documentation (sidecars) with our deployment manifests (Helm/ArgoCD). If a component exists but is NOT advertising its ownership/risk as Kubernetes annotations, it is flagged as an **Injection Gap**.

### 3. Compliance Enforcement

Identify and remediate:

- **Orphaned Resources**: Components with no defined owner.
- **Stale Documents**: Information that has passed its `supported_until` date.

## How it is Updated

The dashboard is maintained by a fully automated "Closed-Loop" process:

|Trigger|Frequency|Action|
|:---|:---|:---|
|**Push**|Repository-wide|Re-generates report and commits it to `development`.|
|**Schedule**|Daily (Midnight)|Audits lifecycle staleness and commits updates.|
|**Manual**|On Demand|Can be triggered via [GitHub Actions](../../.github/workflows/quality-platform-health.yaml).|

## Technical Implementation

- **Engine**: [`scripts/platform_health.py`](../../scripts/platform_health.py)
- **Workflow**: [`.github/workflows/quality-platform-health.yaml`](../../.github/workflows/quality-platform-health.yaml)
- **Automation**: Uses the `git-auto-commit-action` to ensure the dashboard state is persisted as a "stateful record" in Git.

## How to use this data

- **Audit Reports**: Use the "Injection Gaps" list as a task queue for governance remediation.
- **Backstage Integration**: The dashboard is a compliant Markdown file, allowing Backstage users to view "Platform Vitals" directly from the TechDocs portal.
- **Compliance Certification**: Use the **Metadata Compliance %** as a KPI for platform maturity.
