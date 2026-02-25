---
id: HEALTH_AUDIT_LOG
title: Platform Health Audit Log
type: report
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 01_adr_index
  - CAPABILITY_LEDGER
  - CI_WORKFLOWS
  - DOCS_CHANGELOG_README
  - GOV-0053-script-certification-matrix
  - platform_health.py
category: governance
---

# Platform Health Audit Log

Last updated: `2026-01-25 20:53:31`

- This file keeps only the latest snapshot.
- Full history can be regenerated from source data if needed.

## Latest Snapshot

---
id: PLATFORM_HEALTH
title: Platform Health & Compliance Report
type: documentation
category: governance
status: active
owner: platform-team
version: '2026-01-25'
relates_to:
  - platform_health.py
---

## 🏥 Platform Health Command Center

**Generated**: `2026-01-25 20:53:31` | **V1 Readiness**: `90.4%` | **Mean Confidence**: `⭐ (1.4/5.0)`

**Realized Value**: `115.1 Hours` | **Infra Run Rate**: `$1,250.00 USD/mo`

## V1 Platform Readiness Gate

> [!IMPORTANT]
> The platform is currently **90.4%** ready for V1 production rollout.

| Milestone | Status | Readiness |
| :--- | :--- | :--- |
| **Metadata Integrity** | ✅ | 97.9% |
| **Injection Integrity** | ✅ | 97.3% |
| **Architecture Maturity** | 🚧 | 99/171 Active |
| **Changelog Activity** | ✅ | 187 Entries |

## Knowledge Graph Vitality

| Metric | Count | Source |
| :--- | :--- | :--- |
| **Architecture Decisions** | 171 | [ADR Index](../../adrs/01_adr_index.md) |
| **Automation Scripts** | 55 | [Script Index](../../../scripts/index.md) |
| **Certified Scripts (M3)** | 1/56 (2%) | [Certification Matrix](../GOV-0053-script-certification-matrix.md) |
| **Script Maturity Distribution** | M1:4 M2:51 M3:1 | [Value Ledger](../../../.goldenpath/value_ledger.json) |
| **CI Workflows** | 65 | [Workflow Index](../../../ci-workflows/CI_WORKFLOWS.md) |
| **Change Logs** | 187 | [Changelog Index](../../changelog/README.md) |
| **Tracked Resources** | 770 | Repository Scan |

## Catalog Inventory

| Catalog | Entity Count |
| :--- | :--- |
| Ecr Registry | 1 |
| Ecr Repositories | 11 |
| Eks | 1 |
| IDP Apis | 9 |
| IDP Components | 18 |
| IDP Domains | 4 |
| IDP Resources | 14 |
| IDP Systems | 5 |
| Rds | 1 |

## AWS Inventory Snapshot

- **Last run**: `2026-01-10T00:44:01Z`
- **Accounts**: `REDACTED`
- **Regions**: `eu-west-2`
- **Total resources**: `31`
- **Tagged**: `29` | **Untagged**: `2` | **Tag violations**: `29`
- **Report**: [`reports/aws-inventory/aws-inventory-2026-01-10.md`](../../../reports/aws-inventory/aws-inventory-2026-01-10.md)

## Build Timing Metrics

- **Last Updated**: `2026-01-24T15:12:39Z`
- **Source**: `governance-registry:environments/development/latest/build_timings.csv`

| Phase | Avg Duration | Sample Count |
| :--- | :--- | :--- |
| `bootstrap` | 3m 0s | 7 |
| `bootstrap-persistent` | 16m 36s | 1 |
| `teardown` | 3m 12s | 19 |
| `teardown-persistent` | 55m 9s | 1 |
| `terraform-apply` | 8m 56s | 9 |

## 🛡️ Risk & Maturity Visualization

```mermaid
pie title Production Impact distribution
    "HIGH" : 58
    "MEDIUM" : 55
    "LOW" : 516
    "NONE" : 138
```

## Governance Maturity

- **Metadata Compliance**: `97.9%`
- **Risk-Weighted Score**: `100.0%`

## Injection Coverage

- **Sidecar Coverage**: `97.3%` (36/37)

## Project Realized Value (Heartbeat)

> [!TIP]
> Total realized value reclaimed through automation heartbeats: **115.1 hours**.

- **ROI Ledger**: [.goldenpath/value_ledger.json](../../../.goldenpath/value_ledger.json)

## Financial Governance (Cloud Cost)

> [!NOTE]
> Current monthly infrastructure run rate: **$1,250.00 USD**.

- **Estimated Annual**: `$15,000.00 USD`
- **Cost Ledger**: [.goldenpath/cost_ledger.json](../../../.goldenpath/cost_ledger.json)
- **Tooling**: Infracost (CI-integrated)

## Operational Risks

- **Orphaned (No Owner)**: 0
- **Stale (Past Lifecycle)**: 0

---

### Strategic Guidance

- **V1 Readiness Indicator**: A composite metric tracking Architecture (ADRs), Governance (Metadata/Injection), and Delivery (Changelogs). Target: 100%.
- **Visualizing Trends**: The `xychart-beta` is best viewed in GitHub/GitLab or VS Code with updated Mermaid support (v10.x+). It tracks our 'Readiness Velocity' across audit cycles.
