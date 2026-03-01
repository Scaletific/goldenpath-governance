---
id: ADR-0193-native-issue-tracking-pipeline
title: 'ADR-0193: Native Issue Tracking Pipeline'
type: adr
status: proposed
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
  maturity: 1
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0164-agent-trust-and-identity
  - ADR-0192-multi-agent-coordination-protocol
  - GOV-0026-governance-vocabulary
supersedes: []
superseded_by: []
tags:
  - issue-tracking
  - governance
  - sla
  - ci-enforcement
inheritance: {}
supported_until: 2028-02-01
version: '1.0'
breaking_change: false
---

# ADR-0193: Native Issue Tracking Pipeline

- **Status:** Proposed
- **Date:** 2026-02-11
- **Owners:** platform-team
- **Domain:** Platform Core
- **Decision type:** Governance | Operations

---

## Context

Issues discovered during platform work (by agents, CI, or humans) currently
have no structured tracking path. Problems are documented in session captures,
PR comments, or ad-hoc notes, but there is no consistent lifecycle, severity
classification, or SLA enforcement.

This leads to:

1. **Lost issues** — Problems discovered during one session are forgotten in
   the next because there is no canonical issue registry.
2. **No severity triage** — All issues are treated equally regardless of
   impact, leading to critical problems sitting alongside cosmetic ones.
3. **No resolution accountability** — There is no defined path from
   "discovered" to "resolved", and no enforcement of resolution timelines.
4. **Vocabulary drift** — Different agents and humans use different terms for
   severity, domain, and resolution, making it hard to aggregate and report.

The platform already has a governance vocabulary (severity levels, domain
taxonomy, component categories) used across ADRs and governance documents.
We should reuse this vocabulary for issue tracking rather than inventing a
parallel taxonomy.

## Decision

We adopt **GitHub Issues with governance vocabulary labels** as the native
issue tracking pipeline, with CI-enforced SLA constraints.

### Issue Lifecycle

```
Discovered --> Triaged --> Tracked --> Resolved
```

1. **Discovered** — Agent or human identifies an issue during work. Logged in
   agent report or session capture using the structured issue table format.
2. **Triaged** — Severity, domain, and resolution path are assigned. For
   `fix-now` issues, resolution happens immediately (no GitHub Issue needed).
3. **Tracked** — For deferred issues, a GitHub Issue is created with
   governance labels. Issue is linked to the discovering session/PR.
4. **Resolved** — Issue is fixed, PR merged, GitHub Issue closed. Resolution
   evidence (PR link, test results) is recorded.

### Resolution Path Enum

Every issue must have exactly one resolution path:

| Resolution | When to Use | GitHub Issue Required | SLA |
|---|---|---|---|
| `fix-now` | Can be resolved in this session | No | Immediate |
| `defer-to-roadmap` | Medium/low severity only. Deferred to future work. | Yes | 30 days (medium), none (low) |
| `needs-adr` | High severity. Requires architectural decision before fix. | Yes | ADR must be drafted within 14 days |
| `needs-human` | Any severity. Requires human judgment or access. | Yes (P0) | Human SLA (best effort) |
| `blocked` | External dependency. Not actionable by the team. | Yes | Tracked, no SLA |

### SLA Enforcement

- **critical/high severity** — MUST use `fix-now` or `needs-human`. Using
  `defer-to-roadmap` on critical/high issues is a **CI failure** (enforced by
  `issue-severity-sla.yml` workflow).
- **medium severity** — 30-day resolution window. At 21 days, a warning label
  (`sla:warning`) is added. At 30 days, the issue auto-escalates to P1
  priority and adds `sla:overdue` label (enforced by `issue-sla-monitor.yml`
  weekly cron).
- **low severity** — No SLA. Tracked for awareness but not time-bound.

### GitHub Labels Schema

Labels use the governance vocabulary with category prefixes:

#### Severity
| Label | Color | Description |
|---|---|---|
| `severity:critical` | `#B60205` | Platform down or data loss risk |
| `severity:high` | `#D93F0B` | Major feature broken or security concern |
| `severity:medium` | `#FBCA04` | Degraded experience, workaround exists |
| `severity:low` | `#0E8A16` | Cosmetic, minor improvement |

#### Domain
| Label | Color | Description |
|---|---|---|
| `domain:platform-core` | `#0052CC` | Core infrastructure and platform |
| `domain:delivery` | `#006B75` | CI/CD and deployment pipelines |
| `domain:observability` | `#1D76DB` | Monitoring, logging, dashboards |
| `domain:security` | `#5319E7` | Security, auth, secrets |
| `domain:governance` | `#0075CA` | Policies, ADRs, compliance |
| `domain:identity` | `#0075CA` | Identity and access management |
| `domain:cost` | `#006B75` | Cost optimization and tracking |

#### Component
| Label | Color | Description |
|---|---|---|
| `component:infra` | `#D4C5F9` | Terraform, AWS resources |
| `component:ci` | `#D4C5F9` | GitHub Actions, CI workflows |
| `component:gitops` | `#D4C5F9` | ArgoCD, GitOps pipelines |
| `component:argo` | `#D4C5F9` | ArgoCD specific |
| `component:backstage` | `#D4C5F9` | Backstage developer portal |
| `component:kong` | `#D4C5F9` | Kong API Gateway |
| `component:agents` | `#D4C5F9` | AI agent infrastructure |
| `component:keycloak` | `#D4C5F9` | Keycloak identity provider |
| `component:ecr` | `#D4C5F9` | ECR container registry |
| `component:github` | `#D4C5F9` | GitHub repository configuration |

#### Resolution
| Label | Color | Description |
|---|---|---|
| `resolution:defer-to-roadmap` | `#C5DEF5` | Deferred to future work |
| `resolution:needs-adr` | `#D4C5F9` | Requires ADR before fix |
| `resolution:needs-human` | `#F9D0C4` | Requires human decision |
| `resolution:blocked` | `#E4E669` | Blocked by external dependency |

#### Source
| Label | Color | Description |
|---|---|---|
| `source:agent-discovered` | `#BFD4F2` | Found by AI agent during work |
| `source:human-reported` | `#C2E0C6` | Reported by human |
| `source:ci-detected` | `#FEF2C0` | Detected by CI pipeline |

#### SLA
| Label | Color | Description |
|---|---|---|
| `sla:warning` | `#FBCA04` | Approaching SLA deadline (21 days) |
| `sla:overdue` | `#B60205` | Past SLA deadline (30 days) |

#### Priority
| Label | Color | Description |
|---|---|---|
| `priority:P0` | `#B60205` | Drop everything |
| `priority:P1` | `#D93F0B` | Next sprint |
| `priority:P2` | `#FBCA04` | This quarter |
| `priority:P3` | `#0E8A16` | Backlog |

### Issue Table Format (for Agent Reports)

When agents discover issues during work, they log them in the structured
table format within their agent report:

```markdown
| ID | Severity | Domain | Component | Description | Files | Resolution |
|---|---|---|---|---|---|---|
| W1-001 | medium | platform-core | infra | Missing metadata on 3 ADRs | docs/adrs/ADR-0045.md, ... | defer-to-roadmap |
| W1-002 | high | delivery | ci | TDD gate not enforcing bats | .github/workflows/tdd-gate.yml | fix-now |
```

The orchestrator or Session Writer is responsible for creating GitHub Issues
from agent report tables where the resolution is not `fix-now`.

## Scope

**Applies to:**
- All issues discovered during platform work (agent or human)
- GitHub Issues in `[GITHUB_ORG]/[REPO_NAME]`
- Agent reports (`.claude/agent-reports/`)
- CI enforcement workflows

**Does not apply to:**
- Feature requests (tracked in ROADMAP.md)
- ADR proposals (tracked in ADR index)
- Sprint planning or project management

## Consequences

### Positive

- **No lost issues** — Every discovered problem has a defined tracking path.
- **Consistent vocabulary** — Reusing governance vocabulary prevents taxonomy
  drift and enables aggregation.
- **SLA accountability** — Critical issues cannot be deferred; medium issues
  have a 30-day window with automatic escalation.
- **CI enforcement** — The `issue-severity-sla.yml` workflow prevents agents
  from deferring critical/high issues, catching policy violations at PR time.

### Tradeoffs / Risks

- **Label maintenance** — Labels must be created on the repository (bootstrap
  script provided: `scripts/bootstrap_github_labels.sh`).
- **SLA overhead** — Weekly cron job checks and label updates add minor
  automation overhead.
- **Agent compliance** — Agents must learn the issue table format and
  resolution path rules. Enforced by CLAUDE.md documentation and CI checks.

### Operational Impact

- Run `scripts/bootstrap_github_labels.sh` to create all labels on the repo.
- Add issue table section to CLAUDE.md for agent reference.
- Monitor `issue-sla-monitor.yml` cron output for SLA warnings.

## Alternatives Considered

1. **External issue tracker (Jira, Linear)** — Rejected: adds external
   dependency, breaks the "everything in GitHub" principle, and complicates
   agent integration.

2. **Markdown-based issue log** — A `ISSUES.md` file in the repo. Rejected:
   no label/search/filter capability, merge conflicts with multiple writers,
   and no lifecycle management.

3. **No structured tracking** — Continue with ad-hoc notes. Rejected: proven
   to lose issues and provide no accountability.

## Follow-ups

- Run `scripts/bootstrap_github_labels.sh` on the repository.
- Create `issue-severity-sla.yml` CI workflow.
- Create `issue-sla-monitor.yml` cron workflow.
- Update CLAUDE.md with issue tracking section.
- Train agents on the issue table format via prompt templates.

## Notes

The label schema is designed to be additive. New domains, components, or
resolution paths can be added by extending the label set and updating the
bootstrap script. Existing labels are never deleted (use `gh label create
--force` for idempotent updates).
