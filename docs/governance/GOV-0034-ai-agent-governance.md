---
id: GOV-0034-ai-agent-governance
title: AI Agent Governance
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
  - GOV-0029-pr-guardrails
  - GOV-0035-ai-collaboration-protocol
  - GOV-0037-agent-collaboration-matrix
  - 2026-01-24-persistent-cluster-teardown-and-deploy-fix
  - 23_NEW_JOINERS
  - 24_PR_GATES
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0079-platform-ai-agent-governance
  - ADR-0133
  - ADR-0163
  - ADR-0176
  - AI_CHANGELOG
  - CL-0141
  - CL-0163
  - EC-0014-agent-scope-registry
  - SESSION_CAPTURE_2026_01_17_02
  - agent_session_summary
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
aliases:
  - 07_AI_AGENT_GOVERNANCE
---

# AI Agent Governance

Doc contract:

- Purpose: Define governance rules for AI agents integrated into GoldenPath IDP.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/governance/GOV-0037-agent-collaboration-matrix.md, docs/onboarding/26_AI_AGENT_PROTOCOLS.md, docs/governance/GOV-0029-pr-guardrails.md, docs/90-doc-system/AI_CHANGELOG.md

This policy defines how AI agents are authorized, audited, and validated to
preserve quality and trust in the platform.

## Core principle

AI may accelerate execution, but ownership, authority, and risk acceptance
remain human.

## Collaboration registry

The living roster of agents, models, and responsibilities lives in
`docs/governance/GOV-0037-agent-collaboration-matrix.md`. Any permission changes
must be captured there and reviewed via PR.

## Session logging

Each agent session must append to the immutable session log at
`session_summary/agent_session_summary.md`. This file is append-only and captures
what changed in each session for audit and traceability.

For context-bounded efforts, create a session capture using
`session_capture/session_capture_template.md` and keep it append-only.
Each update must include a short **Outstanding** section for quick scanning.

### Session start protocol

At the start of each agent session, run:

```bash
make session-start
```

This command:

1. Checks if `agent_session_summary.md` exceeds 1000 lines
2. If so, archives entries older than 30 days to `session_summary/archive/YYYY-MM.md`
3. Keeps the main file bounded for efficient context loading

Archived entries remain searchable via grep. The archive is organized by month
for historical reference.

To preview without changes: `make session-archive-dry-run`

## 1) Scope and authority

- AI agents are contributors, not owners.
- All changes require explicit user approval and must follow PR gates.
- Agents must not merge to `main` directly; use `development` as the source of
  truth unless otherwise approved.
- All merges require explicit human approval.

## 2) Agent classes (tiered authority)

**Tier 0 — Read / Reason**

- Allowed: read repo, summarize docs, explain workflows, propose approaches.
- Disallowed: writing files, opening PRs, executing workflows.
- Use case: exploration and validation.

**Tier 1 — Write, but isolated**

- Allowed: create branches, generate code/docs, open PRs, update metadata,
  draft ADRs/runbooks.
- Required: PR description links to a user story, ADR (or "ADR needed"), and
  affected workflows.
- Disallowed: merge to main, trigger destructive workflows.
- Use case: scaffolding, refactors, documentation, templates.

**Tier 2 — Execute safely**

- Allowed: run tests/linters, terraform plan, render manifests, validate
  policies.
- Required: execution logs attached to PR; no side effects outside ephemeral
  envs.
- Disallowed: apply, destroy, auth/IAM changes.
- Use case: CI assistance and validation loops.

**Tier 3 — High risk (human only)**

- Only humans: terraform apply, destroy/teardown, IAM/auth changes, cluster
  lifecycle actions, policy enforcement changes.
- AI may recommend, but must not execute without explicit instruction.

## 3) Role mappings (execution profiles)

Role mappings bind execution roles to authority tiers, delegation modes, and
validation expectations. Every AI task must declare one role and inherit its
constraints.

Mapping rules:

- Each role maps to `ai_authority_tier`, `ai_delegation_mode`,
  `ai_context_tier`, and `ai_validation_level`.
- Declare `ai_task_domain` per task (docs, code, infra, governance, security,
  observability, ci-cd).
- Use least-privilege by default; upgrades require explicit human approval.
- Role constraints are enforceable guardrails; if a task violates them, stop
  and escalate.
- Roles and values must align with `schemas/metadata/enums.yaml`.

| Role | Authority tier | Delegation mode | Context tier | Validation level | Notes |
| --- | --- | --- | --- | --- | --- |
| junior-engineer | tier1-write-isolated | full-delegation | execution | local-checks | No new enums or schemas. |
| refactorer | tier1-write-isolated | full-delegation | refinement | local-checks | Preserve behavior. |
| auditor | tier0-read-reason | full-delegation | judgment | not-run | Read-only. |
| automation-agent | tier2-safe-execute | full-delegation | execution | ci-green | No apply/destroy/IAM. |
| advisor | tier0-read-reason | copilot | judgment | not-run | Propose options only. |
| triager | tier0-read-reason | copilot | judgment | not-run | Recommend labels/gates only. |
| documentarian | tier1-write-isolated | full-delegation | execution | local-checks | Docs only, no policy changes. |
| compliance-checker | tier2-safe-execute | full-delegation | refinement | local-checks | Validate-only, no fixes. |
| release-scribe | tier1-write-isolated | full-delegation | execution | local-checks | Changelog/runbook only. |
| threat-modeler | tier0-read-reason | copilot | judgment | not-run | Analysis only. |

## 4) Guardrails

- **Branching:** no branch create/switch/delete without explicit approval.
- **Destructive actions:** no resets, deletes, or force-pushes without approval.
- **Change discipline:** prefer Makefile targets and documented workflows.
- **Guardrail alignment:** labels must match actual changes; remove false
  positives to avoid blocking.

## 5) Auditability

- Every AI-driven change must be traceable to a PR or commit.
- Evidence (run logs, CI links, or metrics) must be recorded when available.
- Record AI contributions in `docs/90-doc-system/AI_CHANGELOG.md`.

## 6) QA and accuracy

- No unverified claims: if tests are not run, state it explicitly.
- CI must be green before work is considered complete.
- When errors occur, use the deterministic triage loop:
  read logs → fix → re-run → confirm green.

## 7) Data handling

- Never introduce secrets into the repo.
- Do not copy sensitive data into docs or logs.
- Redact or summarize external logs before adding them to docs.

## 8) Exceptions and escalation

- Emergency overrides require explicit approval in the current turn.
- If a change could impact infrastructure, evidence is mandatory.

## 9) Responsibilities

- **Agent:** execute safely, document decisions, and provide evidence.
- **Operator:** approve scope, review changes, and validate outcomes.

## 10) Forward-Thinking Solutions Mandate

**Principle:** Every fix must include prevention. A hot fix without systemic
improvement is technical debt by another name.

### Required Pattern

```text
Problem → Root Cause → Fix + Prevention → Document → Never Again
```

### Anti-Pattern (Prohibited)

```text
Problem → Hot Fix → Move On → Same Problem Later → Another Hot Fix
```

### Solution Quality Gate

Agents MUST NOT propose solutions that only address immediate symptoms.

**Required for every fix proposal:**

1. **Immediate action** - What unblocks now
2. **Root cause** - Why this happened
3. **Prevention** - Code/config change that prevents recurrence
4. **Verification** - How we know prevention works

**Example (WRONG):**

> "Import the IAM roles to fix the error"

**Example (CORRECT):**

> "Import the IAM roles to unblock deploy. Root cause: cleanup script uses
> cluster name pattern but IAM roles use `goldenpath-*` prefix.
> Prevention: Update cleanup script to also match `{prefix}-idp-*` pattern
> for IAM discovery. This ensures future teardowns clean up correctly."

### Enforcement

- PRs that fix bugs without prevention components may be rejected.
- Session captures must document both fix and prevention.
- Hot-fix-only proposals require explicit human approval with justification.
