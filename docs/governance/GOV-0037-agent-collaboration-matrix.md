---
id: GOV-0037-agent-collaboration-matrix
title: Agent Collaboration Registry & Responsibility Matrix
type: documentation
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - GOV-0034-ai-agent-governance
  - GOV-0036-github-agent-roles
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0163
  - agent_session_summary
category: governance
supported_until: 2028-01-16
version: '1.0'
breaking_change: false
aliases:
  - 09_AGENT_COLLABORATION_MATRIX
---

# Agent Collaboration Registry & Responsibility Matrix

## Doc contract

- Purpose: Maintain a living roster of AI agents, their models, responsibilities, and permissions.
- Owner: platform
- Status: living
- Review cadence: 30d or on any agent access change
- Source of truth: this document

## Update rules

- Add/update an agent here before enabling it in local or CI contexts.
- Permission changes require a PR and security review.
- Retire agents by changing status to `retired` and removing credentials.
- Each session appends a summary to `session_summary/agent_session_summary.md`.
- After implementation, add a changelog entry for the operational change.

## Environment access levels

- **Local**: actions on a developer machine (edit files, run tests).
- **CI**: actions on CI runners (workflows, artifacts, logs).
- **Cluster**: Kubernetes access (read/list or apply changes).
- **Cloud**: cloud APIs (Terraform plan/apply, IAM, secrets).

## Agent registry (living)

|Agent|Model|Role|Strengths|Primary Responsibilities|Runtime|Local|CI|Cluster|Cloud|Access Profile|Owner|Status|
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|TBD-agent-docs|TBD-model|documentarian|clear summaries|docs updates, runbooks, ADR drafts|local|write|none|none|none|gh-app-pr-writer|platform-team|planned|
|TBD-agent-validate|TBD-model|automation-agent|fast validation|lint/tests/metadata checks|ci|none|run|read-only|none|gh-app-ci-executor|platform-team|planned|
|TBD-agent-advisor|TBD-model|advisor|decision support|options, tradeoffs, reviews|local|read-only|none|none|none|read-only|platform-team|planned|

## Responsibility matrix

|Capability|Primary Role|Secondary Role|Approval Required|Notes|
|---|---|---|---|---|
|Docs and runbooks|documentarian|advisor|platform|No policy changes.|
|Metadata compliance|compliance-checker|automation-agent|platform|Validate only unless approved.|
|Template changes|refactorer|documentarian|platform|Preserve behavior.|
|Workflow dispatch|automation-agent|advisor|platform|No apply/destroy/IAM.|
|Governance updates|advisor|documentarian|platform + security|ADR required for new policy.|
|Infra changes|human-only|advisor|platform + security|AI may propose only.|

## Model usage and boundaries

- Use least-capable models for low-risk tasks; escalate only when necessary.
- Models that can execute actions must be isolated to scoped roles and repos.
- All agents must declare a role before starting work.

## Collaboration flow

1. Agent proposes plan and scope.
2. Human approves scope and role.
3. Agent executes within role constraints.
4. Human reviews output and approves PR merge.

## Security and best practices

- Use a per-agent identity (GitHub App preferred) with least-privilege repo access.
- Use short-lived tokens in CI; avoid long-lived tokens on developer machines.
- Never share tokens across agents; rotate on schedule or after incidents.
- Do not log secrets, tokens, or raw credentials in terminal output or files.
- Keep branch protections and required reviews enabled for all merges.
- Capture audit trails: prompts, command logs, and validation outputs.

## Changelog trigger

After implementing or enabling any new agent or permission change, add a
changelog entry documenting the change and effective date.
