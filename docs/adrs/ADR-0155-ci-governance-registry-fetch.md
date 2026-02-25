---
id: ADR-0155-ci-governance-registry-fetch
title: 'ADR-0155: CI Governance Registry Fetch for Build ID Validation'
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.5
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
  - ADR-0148-seamless-build-deployment-with-immutability
  - ADR-0155-ci-governance-registry-fetch
  - CI_TERRAFORM_WORKFLOWS
  - CL-0126-ci-governance-registry-fetch
  - CL-0127
supersedes: []
superseded_by: []
tags:
  - ci
  - governance
  - build-id
inheritance: {}
supported_until: '2028-01-14'
---

## ADR-0155: CI Governance Registry Fetch for Build ID Validation

**Status**: Accepted
**Date**: 2026-01-14
**Relates to**: [ADR-0148](./ADR-0148-seamless-build-deployment-with-immutability.md), [ADR-0149](./ADR-0149-simplified-resource-lifecycle-separation.md)

## Context

The build_id immutability guard in `envs/dev/main.tf` validates that a build_id has not been previously used by checking the governance-registry branch CSV file. However, there is a vulnerability in the current implementation:

**The Problem**: When the governance-registry branch is not available (shallow clone, branch not fetched), the validation returns `exists=false` and allows the build to proceed. This is a **fail-open** behavior that defeats the purpose of the immutability check.

This occurs because:

1. GitHub Actions uses shallow clones by default (`fetch-depth: 1`)
2. The checkout action only fetches the current branch, not `governance-registry`
3. When `git show origin/governance-registry:...` fails, the script falls through to the "not found" path

**The Risk**: A reused build_id could proceed in CI, causing terraform state collisions - the exact scenario the immutability guard was designed to prevent.

## Decision

We will explicitly fetch the governance-registry branch in all CI workflows that run terraform apply with build_id validation.

### Implementation

Add the following step after checkout in deployment workflows:

```yaml
- name: Checkout repo
  uses: actions/checkout@v4

- name: Fetch governance registry for build_id validation
  run: git fetch origin governance-registry:refs/remotes/origin/governance-registry
```

### Affected Workflows

1. `infra-terraform-apply-dev.yml`
2. `infra-terraform-apply-staging.yml`
3. `infra-terraform-apply-prod.yml`
4. `infra-terraform-apply-test.yml`
5. `ci-bootstrap.yml`

### Behavior After Fix

|Scenario|Before|After|
|----------|--------|-------|
|Registry available, build_id exists|Block|Block|
|Registry available, build_id new|Allow|Allow|
|Registry unavailable (shallow clone)|**Allow** (unsafe)|Block (safe)|
|Registry unavailable (branch not fetched)|**Allow** (unsafe)|Block (safe)|

### Local Development

Local developers running `make deploy` may encounter failures if they haven't fetched the governance-registry branch. This is acceptable because:

1. Cluster creation is primarily service-based via Backstage (CI-driven)
2. Local runs are for development/troubleshooting where friction is acceptable
3. The error message clearly indicates the fix: `git fetch origin governance-registry`

## Alternatives Considered

### 1. Full Clone (`fetch-depth: 0`)

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

**Rejected**: Slower (10-30s extra), fetches entire history when we only need one branch.

### 2. Fail-Open with Warning

Keep current behavior but log a warning when registry is unavailable.

**Rejected**: Silent failures defeat the purpose of governance. A collision error is worse than a blocked build.

### 3. CI-Only Enforcement

Only enforce strict checking in CI, allow local builds to bypass.

**Rejected**: Adds complexity and environment-specific behavior. Consistent behavior is preferable.

## Consequences

### Positive

- Build ID immutability is reliably enforced in CI
- Fail-safe behavior prevents state collisions
- Minimal performance impact (~1-2 seconds for fetch)
- Consistent with governance-first platform philosophy

### Negative

- Local developers must fetch governance-registry before running ephemeral builds
- Additional step in CI workflows (minor maintenance burden)

### Neutral

- Terraform code updated to fail-closed (returns `registry_available` flag)
- No change to Makefile or local tooling
- Existing governance-registry branch structure unchanged

## References

- [ADR-0148: Seamless Build Deployment](./ADR-0148-seamless-build-deployment-with-immutability.md)
- [ADR-0149: Simplified Resource Lifecycle Separation](./ADR-0149-simplified-resource-lifecycle-separation.md)
- [GitHub Actions checkout documentation](https://github.com/actions/checkout)
