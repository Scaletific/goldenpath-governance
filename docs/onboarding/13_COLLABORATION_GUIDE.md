---
id: 13_COLLABORATION_GUIDE
title: Collaboration Guide
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 23_NEW_JOINERS
  - 26_AI_AGENT_PROTOCOLS
  - 38_BRANCHING_STRATEGY
  - CL-0078
  - SHARED_RESPONSIBILITY
  - agent_session_summary
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Collaboration Guide

## Branch Strategy

Use short-lived branches and keep `main` deployable.

- `main`: protected, always deployable; only merged PRs.
- `development`: integration branch, only source allowed to merge into `main`.
- `feature/<topic>`: new work.
- `fix/<topic>`: urgent bugfixes.
- `chore/<topic>`: docs, tooling, cleanup.

Flow:

1. Branch from `development`.
2. Open a PR early for visibility into `development`.
3. Merge after checks pass.
4. Promote via a PR from `development` to `main`.
5. Delete the branch after merge.

### Value-Led Review

All Pull Requests are reviewed through the lens of [**VQ Principles**](../product/VQ_PRINCIPLES.md).

- **Is it 🔴 HV/HQ?** (Core/Governance/Trust): Requires deep review, high-test coverage, and zero-compromise on auditability.
- **Is it 🟡 HV/LQ?** (UX/Dashboard/README): Prioritize velocity. If it works and is reversible, ship it. 🟡
- **Is it 🔵 MV/HQ?** (Levers/Multipliers): Build safely, then freeze.
- **Is it ⚫ LV/LQ?** (Bloat/Noise): Actively resist.

Examples:

- `feature/ci-bootstrap`
- `fix/teardown-timeout`
- `chore/docs-bootstrap`

Reference: `docs/40-delivery/38_BRANCHING_STRATEGY.md` is the source of truth.

## Roles & Responsibilities (Summary)

- Platform team owns infra lifecycle, CI/CD rails, GitOps controllers, baseline
  security/observability, and governance artifacts (ADRs/changelog rules).
- App teams own application code, runtime behavior, and service-level choices
  within platform contracts (tags, CI inputs, promotion flow).
- AI agents are contributors; humans approve scope, merges, and any high-risk
  actions (apply/destroy/IAM).
- Shared responsibility is tracked in `docs/60-security/SHARED_RESPONSIBILITY.md`
  and must be kept current before production use.
- If onboarding guidance conflicts with governance/contract docs, defer to the
  contract doc and open a fix.

## Branch Protection Checklist (GitHub)

Recommended settings for `main`:

- Require pull requests before merging.
- Require approvals: at least 1.
- Require status checks to pass.
- Require branches to be up to date before merging.
- Restrict who can push to `main`.
- Require linear history (no merge commits).
- Dismiss stale approvals when new commits are pushed.
- Enforce code owner reviews (if `CODEOWNERS` exists).

## Local Development Health

Core contributors are expected to maintain a healthy local environment.

- Run `bin/governance setup` after cloning or pulling major changes.
- Run `bin/governance lint` before pushing any PR to catch syntax or metadata drift early.
- Use `scripts/scaffold_doc.py` for new docs; pre-commit auto-fix will normalize metadata headers.
- If CI reports issues, the fastest path to a fix is usually `bin/governance heal`.
