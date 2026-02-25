---
id: GOV-0012-build-pipeline-standards
title: Build Pipeline Standards
type: governance
owner: platform-team
status: active
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
schema_version: 1
relates_to:
  - 2026-01-19-build-and-release-workflow-implementation
  - ADR-0170
  - BACKEND_APP_RDS_REQUEST_FLOW
  - CL-0149
  - CL-0162
  - RB-0036
  - RB-0037
  - session-2026-01-19-build-pipeline-architecture
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
effective_date: 2026-01-19
review_date: 2026-07-19
related_adrs:
  - ADR-0170
related_govs:
  - GOV-0013
  - GOV-0015
---

# GOV-0012: Build Pipeline Standards

## Purpose

Define mandatory standards for application build pipelines in GoldenPath IDP.

## Scope

All application repositories that deploy to GoldenPath-managed infrastructure.

---

## 1. Pipeline Architecture

### 1.1 Canonical Pipeline Requirement

All application repos MUST use the canonical reusable workflow:

```yaml
# App repo: .github/workflows/delivery.yml
name: Delivery

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    uses: [GITHUB_ORG]/[REPO_NAME]/.github/workflows/_build-and-release.yml@main
    with:
      ecr_repository: <app-name>
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN }}
```

**Rationale**: Single source of truth prevents drift and ensures consistent security enforcement.

### 1.2 Custom Pipelines

Custom pipelines are NOT permitted without explicit ADR approval from platform-team.

---

## 2. Image Tagging Standards

### 2.1 Tag Format by Environment

| Environment | Tag Format | Mutable | Example |
|-------------|------------|---------|---------|
| local | `:latest` | Yes | `hello-app:latest` |
| dev | `:latest` | Yes | `hello-app:latest` |
| test | `test-<sha>` | No | `hello-app:test-a1b2c3d` |
| staging | `staging-<sha>` | No | `hello-app:staging-a1b2c3d` |
| prod | `prod-<sha>` | No | `hello-app:prod-a1b2c3d` |

### 2.2 Digest Strategy

Local and dev environments use **digest-based tracking**:

- Image-updater watches the content hash, not the tag name
- Enables fast iteration while detecting actual changes
- Configuration: `argocd-image-updater.argoproj.io/app.update-strategy: digest`

### 2.3 Immutability

Test, staging, and prod tags MUST be immutable:

- ECR repository configured with `imageTagMutability: IMMUTABLE`
- Re-pushing to an existing tag is blocked

---

## 3. Authentication Standards

### 3.1 Git Write-back

| Environment | Method | Auth |
|-------------|--------|------|
| local | `argocd` (in-cluster) | N/A |
| dev/test/staging/prod | `git` | GitHub App |

### 3.2 GitHub App Requirements

- App ID and private key stored in AWS Secrets Manager
- Minimum permissions: `contents: write` on target repos
- Tokens auto-rotate (1-hour expiry)

### 3.3 Deploy Keys

Deploy keys are permitted ONLY for local development environments.

---

## 4. Security Gates

### 4.1 Gate Configuration by Environment

| Gate | local/dev | test/staging/prod |
|------|-----------|-------------------|
| Trivy vulnerability scan | Advisory | Blocking |
| Trivy severity threshold | N/A | HIGH, CRITICAL |
| SARIF upload to GitHub | Optional | Required |
| Gitleaks secret scan | Advisory | Blocking |

### 4.2 Blocking Gates

For test/staging/prod:

- Pipeline MUST fail if HIGH or CRITICAL vulnerabilities found
- Pipeline MUST fail if secrets detected in code
- SARIF results MUST be uploaded to GitHub Security tab

### 4.3 Trivy Configuration

```yaml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    exit-code: '1'  # Fail on vulnerabilities
    severity: 'HIGH,CRITICAL'

- name: Upload Trivy scan results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: 'trivy-results.sarif'
```

### 4.4 Exceptions

Security gate exceptions require:

1. ADR documenting the exception and risk acceptance
2. Platform-team approval
3. Time-boxed remediation plan

---

## 5. Concurrency Standards

### 5.1 Build Concurrency

Builds run in **parallel** - no restrictions.

### 5.2 Deploy Concurrency

Deploys are **serialized per environment**:

```yaml
concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: false
```

### 5.3 Approval Gates

| Environment | Approval Required |
|-------------|-------------------|
| local | No |
| dev | No |
| test | No |
| staging | Optional |
| prod | Required |

---

## 6. Bootstrap Prerequisites

Before an environment is "deploy ready":

- [ ] DNS: Route records configured for services (backstage, argocd, keycloak)
- [ ] Secrets: AWS Secrets Manager populated (OIDC, GitHub token, admin creds)
- [ ] GitHub App: Created and installed with repo write permissions
- [ ] ECR: Repositories created with correct tag mutability
- [ ] Approvals: GitHub environment protection rules configured (staging/prod)

---

## 7. Compliance

### 7.1 Audit

All builds produce:

- Build summary in GitHub Actions step summary
- SARIF security results uploaded to GitHub Security tab (test/staging/prod)
- Image digest logged in build output

### 7.2 Violations

Violations of this policy will:

1. Block the pipeline (for enforced gates)
2. Generate alerts to platform-team
3. Require remediation before promotion

---

## 8. Promotion Flow

```
PR Merge to main
       │
       ▼
Build/Test/Scan/Push  ←── Parallel (no concurrency limit)
       │
       ▼
Update GitOps (dev)   ←── concurrency: deploy-dev
       │
       ▼
Argo Sync to dev      ←── Auto-sync enabled
       │
       ▼ (manual trigger)
Promote to test       ←── concurrency: deploy-test
       │
       ▼ (manual trigger)
Promote to staging    ←── concurrency: deploy-staging
       │
       ▼ (approval gate)
Promote to prod       ←── concurrency: deploy-prod
```

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-19 | Initial version | platform-team |

---

## Related Documents

- ADR-0170: Build Pipeline Architecture and Multi-Repo Strategy
- GOV-0013: DevSecOps Security Standards
- GOV-0015: Build Pipeline Testing Matrix
- CL-0149: Build Pipeline Architecture and Governance
- OB-0001: Developer Security Tooling Onboarding
- Session: `session_capture/2026-01-19-build-pipeline-architecture.md`

Signed: platform-team (2026-01-19)
