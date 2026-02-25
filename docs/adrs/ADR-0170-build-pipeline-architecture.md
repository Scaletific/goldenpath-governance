---
id: ADR-0170
title: Build Pipeline Architecture and Multi-Repo Strategy
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 2026-01-19-build-and-release-workflow-implementation
  - 2026-01-21-route53-dns-terraform
  - ADR-0143
  - ADR-0144
  - ADR-0168
  - ADR-0169
  - ADR-0174-pipeline-decoupling-from-cluster-bootstrap
  - ADR-0175-externaldns-wildcard-ownership
  - ADR-0188
  - APP_BUILD_PIPELINE
  - CL-0146
  - CL-0147
  - CL-0149
  - CL-0158
  - EC-0002-shared-parser-library
  - EC-0005-kubernetes-operator-framework
  - EC-0016-bespoke-schema-validator
  - GOV-0012
  - GOV-0012-build-pipeline-standards
  - GOV-0013-devsecops-security-standards
  - GOV-0014-devsecops-implementation-matrix
  - GOV-0015-build-pipeline-testing-matrix
  - OB-0001-developer-security-tooling
  - RB-0035-s3-request
  - RB-0036
  - RB-0037
  - ROADMAP
  - S3_REQUEST_FLOW
  - s3-requests-index
  - session-2026-01-17-s3-request-flow-planning
  - session-2026-01-19-build-pipeline-architecture
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-19
deciders: platform-team
consulted: Claude Opus 4.5, Codex (GPT-5)
informed: dev-teams
---

# ADR-0170: Build Pipeline Architecture and Multi-Repo Strategy

## Status

Accepted

## Context

GoldenPath IDP needs a standardized build pipeline that:

- Supports multiple application repositories
- Enforces security gates consistently
- Enables fast iteration in dev while maintaining prod safety
- Minimizes copy/paste drift across repos

The platform currently has:

- `goldenpath-infra/` as the central infrastructure repo
- `hello-goldenpath/` as a sample application repo
- argocd-image-updater configured for local environment with digest strategy

## Decision

### Architecture

Adopt a **canonical reusable workflow pattern**:

- **Platform repo** (`goldenpath-infra/`) owns the canonical pipeline
- **App repos** call it via thin ~15-line caller workflows
- **GitOps** updates trigger ArgoCD sync

```
App Repo (intent/config)  --->  Canonical Pipeline (build/test/scan/push)  --->  GitOps update  --->  Argo sync
```

### Tagging Strategy

| Environment | Tag Format | Update Strategy | `:latest` Allowed |
|-------------|------------|-----------------|-------------------|
| local | `:latest` | digest | Yes |
| dev | `:latest` | digest | Yes |
| test | `test-<sha>` | semver/tag | No |
| staging | `staging-<sha>` | semver/tag | No |
| prod | `prod-<sha>` | semver/tag | No |

### Authentication

**GitHub App** for git write-back (not deploy keys):

- Org-wide access
- Auto-rotating tokens (1-hour expiry)
- Rich audit trail
- One app covers all repos

Exception: Deploy key acceptable for local dev (single repo, ephemeral)

### Concurrency

- **Builds**: Parallel (no contention)
- **Deploys**: Serialized per environment via concurrency groups
- **Prod**: Serialized + approval gate

```yaml
concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: false
```

### Security Gates

| Gate | local/dev | test/staging/prod |
|------|-----------|-------------------|
| Trivy scan | Advisory | Blocking (HIGH/CRITICAL) |
| SARIF upload | Optional | Required |
| Gitleaks | Advisory | Blocking |

## Consequences

### Positive

- Single source of truth for build logic
- No copy/paste drift across repos
- Consistent security enforcement
- Fast dev iteration preserved
- Audit trail via GitHub App

### Negative

- GitHub App setup overhead (~30 min one-time)
- Platform repo becomes critical path for pipeline changes
- Breaking change to canonical pipeline affects all repos

### Risks

| Risk | Mitigation |
|------|------------|
| Breaking change affects all repos | Version the reusable workflow, test in dev first |
| GitHub App compromise | Store credentials in Secrets Manager, rotate on suspicion |
| Digest strategy confusion | Document clearly, train team on content-addressable images |

## Alternatives Considered

### Deploy Keys

- Pros: Simple, scoped to single repo
- Cons: Manual rotation, no audit trail, one key per repo
- Rejected: GitHub App better for multi-repo org

### Copy/Paste Workflows

- Pros: Teams have full control
- Cons: Drift, inconsistent security, maintenance burden
- Rejected: Reusable workflows prevent drift

### `:latest` Everywhere

- Pros: Simple
- Cons: No reproducibility, can't rollback reliably
- Rejected: `:latest` only for local/dev, immutable tags for higher envs

## Implementation Phases

### Phase 1: Foundation

- Create `_build-and-release.yml` canonical workflow
- Add Trivy blocking gates with SARIF upload
- Add concurrency groups
- Refactor `hello-goldenpath` to thin caller

### Phase 2: Authentication & Promotion

- Create GitHub App
- Configure git write-back for dev/test/staging/prod
- Implement `<env>-<sha>` tagging
- Create promotion workflow

### Phase 3: Governance & Documentation

- Bootstrap prerequisites runbook
- App onboarding guide
- GitHub template repo for new apps

### Phase 4: V1.1 Enhancements (Deferred)

- SBOM generation (Syft)
- Image signing (Cosign)
- SLSA provenance
- Rollback playbook

## Related

- Session Capture: `session_capture/2026-01-19-build-pipeline-architecture.md`
- Governance: `docs/governance/policies/GOV-0012-build-pipeline-standards.md`
- Changelog: `docs/changelog/entries/CL-0149-build-pipeline-architecture.md`

Signed: Claude Opus 4.5 + Codex (GPT-5) (2026-01-19)
