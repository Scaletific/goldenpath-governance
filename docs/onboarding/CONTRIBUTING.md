---
id: CONTRIBUTING
title: Contributing
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 24_PR_GATES
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

# Contributing

## Branch Strategy

Use short-lived branches and keep `main` deployable.

- `main`: protected, always deployable; only merged PRs.
- `feature/<topic>`: new work.
- `fix/<topic>`: urgent bugfixes.
- `chore/<topic>`: docs, tooling, cleanup.

Flow:

1. Branch from `development`.
2. Open a PR early for visibility into `development`. Focus on functionality; governance is relaxed on this branch.
3. Merge after quality checks (linting) pass.
4. Promote via a PR from `development` to `main`. This is where all **Quality Gates** are enforced (ADR, Changelog, Schema).
5. Ensure all quality gates are green (see [PR Gates and How to Unblock Them](./24_PR_GATES.md)).
6. Delete the branch after merge.

Examples:

- `feature/ci-bootstrap`
- `fix/teardown-timeout`
- `chore/docs-bootstrap`

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

## Terraform lockfile policy

CI must not upgrade Terraform providers or modules. Use `terraform init` locally for upgrades and
commit the resulting `.terraform.lock.hcl` changes. If CI reports lockfile drift, update the
lockfile in a dedicated change and rerun the checks.
