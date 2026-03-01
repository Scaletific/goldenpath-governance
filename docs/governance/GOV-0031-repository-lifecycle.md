---
id: GOV-0031-repository-lifecycle
title: Repository Lifecycle Governance
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
  - 10_REPO_DECOMMISSIONING
  - ADR-0078-platform-governed-repo-scaffolder
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
aliases:
  - 05_REPOSITORY_LIFECYCLE
---

# Repository Lifecycle Governance

Doc contract:

- Purpose: Define the repo lifecycle and required governance evidence.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/governance/GOV-0023-platform-governance.md, docs/70-operations/runbooks/10_REPO_DECOMMISSIONING.md, docs/adrs/ADR-0078-platform-governed-repo-scaffolder.md

This policy defines how repositories enter, live within, and exit the
organization. A repo is governed only if its **creation and decommissioning**
are controlled and auditable.

## Lifecycle stages

| Stage | Action | Audit trail | Governance value |
| --- | --- | --- | --- |
| Creation | Repo created via the scaffolder workflow or Backstage template. | Request metadata, owner team, template selection. | No shadow IT; every repo is owned from day zero. |
| Active development | PRs merged through guardrails; CI/CD runs. | Signed commits, PR approvals, workflow runs. | Quality gates and traceability for changes. |
| Maintenance | CVE fixes, dependency updates, small patches. | Dependabot alerts and remediation logs. | Prevents "stable" repos from becoming insecure. |
| Deprecation | Repo marked as deprecated; new work discouraged. | ADR or ticket links to deprecation decision. | Avoids new feature work on a dying service. |
| Decommissioning | Repo archived or deleted after resources are removed. | Tombstone record with approvals and resource teardown evidence. | Reduces attack surface and confirms data removal. |

## Decommissioning: why it matters

### Governance (no zombie code)

If a repo has no commits for 12 months and its owner team is dissolved, it
enters a **stale** state. A review is triggered. If no owner claims the repo,
it must be archived.

### Auditing (paper trail)

Decommissioning must prove that code and data were removed. This includes
teardown of associated cloud resources and a final record of who approved it.

### Security (attack surface reduction)

Archived or deleted repos remove stale secrets, old dependencies, and unused
access paths that attackers target.

## Definition of done for a repo

- **Creation:** repo created via the scaffolder; owner team and metadata set.
- **Decommissioning:** repo archived/deleted **and** associated infrastructure
  is torn down with evidence recorded.

## Policy rules

- All new repos must be created via the scaffolder (workflow or Backstage).
- Owner team is required; no orphan repositories.
- Deprecation requires an ADR or ticket and lifecycle set to `deprecated`.
- Decommissioning follows the runbook and produces a tombstone record.

## Tracking beyond documentation

For any repo lifecycle automation:

- Run at least **three** scaffold drills and **one** decommission drill.
- Record evidence links (workflow runs, approvals) in the backlog entry.
- Do not mark as "done" until the drills are repeatable.

## Metrics (required signals)

- Scaffold/decommission duration.
- Success rate for lifecycle runs.
- First-run success vs retries.
- Time-to-ready (repo created → first CI green).
- Policy compliance coverage (metadata + branch protection).
- Stale repo count and archive rate.
