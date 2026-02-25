---
id: GOV-0014-devsecops-implementation-matrix
title: DevSecOps Implementation Matrix
type: governance
owner: platform-team
status: active
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: high
  coupling_risk: medium
schema_version: 1
relates_to:
  - 2026-01-19-build-and-release-workflow-implementation
  - 2026-02-01-phase1-cicd-consolidation
  - ADR-0170
  - PHASE1_CICD_IMPLEMENTATION_STRATEGY
  - session-2026-01-19-build-pipeline-architecture
  - standardized-image-delivery
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
related_govs:
  - GOV-0012
  - GOV-0013
  - GOV-0015
related_adrs:
  - ADR-0170
---

# GOV-0014: DevSecOps Implementation Matrix

## Purpose

Provide a comprehensive reference matrix of all DevSecOps principles, tools, integration points, and implementation phases for GoldenPath IDP.

---

## 1. Core Principles Adopted

### 1.1 Shift-Left Security

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Detect Early** | Catch vulnerabilities in IDE before commit | Snyk extension, Gitleaks pre-commit |
| **Fail Fast** | Block bad code at earliest stage | Pre-commit hooks, PR checks |
| **Cost Efficiency** | Fix bugs where they're cheapest | IDE > PR > Build > Deploy > Prod |
| **Developer Ownership** | Developers responsible for security | Mandatory tooling, training |

### 1.2 Defense in Depth

| Layer | Protection | Tools |
|-------|------------|-------|
| IDE | First line of defense | Snyk, Gitleaks, linters |
| Pre-commit | Prevent secrets in repo | Gitleaks hooks |
| PR/Source | Gate before merge | SAST, SCA, secrets scan |
| Build | Artifact security | Image scan, SBOM |
| Test | Runtime validation | DAST (OWASP ZAP) |
| Release | Final gate | CVE check, policy enforcement |
| Production | Continuous monitoring | Periodic scans, alerts |

### 1.3 Pipeline Architecture

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Canonical Pipeline** | Single source of truth | `_build-and-release.yml` reusable workflow |
| **Thin Callers** | Apps provide config only | `delivery.yml` ~15 lines |
| **No Copy/Paste** | Prevent drift | All apps use canonical workflow |
| **Parallel Build** | Fast feedback | No concurrency limits on build |
| **Serialized Deploy** | Prevent conflicts | `concurrency: deploy-${{ env }}` |

---

## 2. Security Tool Matrix

### 2.1 Tool Selection by Category

| Category | Primary Tool | Secondary | Alternatives | Decision Rationale |
|----------|--------------|-----------|--------------|-------------------|
| **SCA** | Snyk | Dependabot | OWASP Dep-Check | Best IDE integration, fix suggestions |
| **SAST** | Semgrep | CodeQL | SonarQube | Fast, customizable, CI-friendly |
| **Secrets** | Gitleaks | TruffleHog | GitHub Secret Scanning | Pre-commit support, fast |
| **Image Scan** | Trivy | Docker Scout | Grype | SARIF output, comprehensive |
| **DAST** | OWASP ZAP | Nuclei | Burp Suite | Free, CI integration |
| **SBOM** | Syft | Trivy SBOM | Docker Scout | Fast, no auth required |
| **Signing** | Cosign | Notary | - | Keyless, SLSA compatible |

### 2.2 Tool Integration by Stage

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEVELOPMENT LIFECYCLE                              │
├─────────┬─────────────┬─────────────┬─────────────┬─────────────┬──────────┤
│   IDE   │  Pre-commit │   Source    │    Build    │    Test     │  Release │
├─────────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────┤
│ Snyk    │ Gitleaks    │ Semgrep     │ Trivy       │ OWASP ZAP   │ Trivy    │
│ Semgrep │ pre-commit  │ Snyk        │ Syft (SBOM) │             │ Cosign   │
│ Linters │ hooks       │ Gitleaks    │ Gitleaks    │             │ Policy   │
│         │             │ CodeQL      │             │             │ Gate     │
├─────────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────┤
│ Phase 1 │ Phase 1     │ Phase 1/3   │ Phase 1     │ Phase 3     │ Phase 1  │
│ Advisory│ Blocking    │ Blocking    │ Blocking    │ Advisory→   │ Blocking │
│         │             │ (test+)     │ (test+)     │ Blocking    │ (test+)  │
└─────────┴─────────────┴─────────────┴─────────────┴─────────────┴──────────┘
```

---

## 3. Environment Matrix

### 3.1 Security Gate Enforcement

| Gate | local | dev | test | staging | prod |
|------|-------|-----|------|---------|------|
| **Gitleaks (secrets)** | Advisory | Advisory | Blocking | Blocking | Blocking |
| **SAST (Semgrep)** | Advisory | Advisory | Blocking | Blocking | Blocking |
| **SCA (Snyk/Trivy)** | Advisory | Advisory | Blocking | Blocking | Blocking |
| **Image Scan (Trivy)** | Advisory | Advisory | Blocking | Blocking | Blocking |
| **DAST (ZAP)** | N/A | N/A | Advisory | Advisory | Blocking |
| **SBOM Required** | No | No | Yes | Yes | Yes |
| **SARIF Upload** | No | No | Yes | Yes | Yes |

### 3.2 Image Tagging Strategy

| Environment | Tag Format | Mutable | Update Strategy | ECR Setting |
|-------------|------------|---------|-----------------|-------------|
| local | `:latest` | Yes | digest | MUTABLE |
| dev | `:latest` | Yes | digest | MUTABLE |
| test | `test-<sha>` | No | semver/tag | IMMUTABLE |
| staging | `staging-<sha>` | No | semver/tag | IMMUTABLE |
| prod | `prod-<sha>` | No | semver/tag | IMMUTABLE |

### 3.3 Authentication and Write-back

| Environment | Write-back Method | Auth Method | Credentials | Approval |
|-------------|-------------------|-------------|-------------|----------|
| local | `argocd` (in-cluster) | N/A | N/A | None |
| dev | `git` | GitHub App | Secrets Manager | None |
| test | `git` | GitHub App | Secrets Manager | None |
| staging | `git` | GitHub App | Secrets Manager | Optional |
| prod | `git` + gate | GitHub App | Secrets Manager | Required |

### 3.4 Concurrency Rules

| Environment | Build | Deploy | Rationale |
|-------------|-------|--------|-----------|
| local | Parallel | N/A | Fast iteration |
| dev | Parallel | Serialized | Prevent GitOps conflicts |
| test | Parallel | Serialized | Reproducible deploys |
| staging | Parallel | Serialized | Pre-prod stability |
| prod | Parallel | Serialized + Approval | Safety gate |

---

## 4. Image Base Standards

### 4.1 Allowed Base Images

| Image Type | Attack Surface | Shell | Pkg Mgr | local | dev | test | staging | prod |
|------------|----------------|-------|---------|-------|-----|------|---------|------|
| **Distroless** | Minimal | No | No | Yes | Yes | Yes | Yes | **Required** |
| **Chainguard** | Minimal | No | No | Yes | Yes | Yes | Yes | **Required** |
| **Alpine** | Small | Yes | apk | Yes | Yes | Yes | No | No |
| **Slim** | Medium | Yes | apt | Yes | Yes | No | No | No |
| **Standard** | Large | Yes | Full | Yes | No | No | No | No |

### 4.2 Dockerfile Standards

```dockerfile
# Required pattern for production
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage - distroless REQUIRED
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
WORKDIR /app
CMD ["app.py"]
```

---

## 5. Implementation Phases

### 5.1 Phase Overview

| Phase | Name | Timeline | Focus |
|-------|------|----------|-------|
| **Phase 1** | Foundation | Current Sprint | Core pipeline, blocking gates, SBOM |
| **Phase 2** | Auth & Promotion | Next Sprint | GitHub App, env-specific tagging |
| **Phase 3** | Governance & DAST | Following Sprint | ZAP, Semgrep, runbooks |
| **Phase 4** | V1.1 Enhancements | Future | Signing, SLSA, distroless mandate |

### 5.2 Phase 1: Foundation (Current Sprint)

| Item | Tool/Tech | Integration Point | Status | Owner |
|------|-----------|-------------------|--------|-------|
| Canonical workflow | GitHub Actions | `.github/workflows/_build-and-release.yml` | Done | platform-team |
| Trivy blocking gates | Trivy | Build job, `exit-code: 1` | Done | platform-team |
| SARIF upload | GitHub Security | `codeql-action/upload-sarif` | Done | platform-team |
| Concurrency groups | GitHub Actions | `concurrency: deploy-${{ env }}` | Done | platform-team |
| SBOM generation | Syft | Build job, artifact upload | Done | platform-team |
| Gitleaks CI | Gitleaks | PR check job | Done | platform-team |
| Pre-commit config | pre-commit | `.pre-commit-config.yaml` template | Done | platform-team |
| Thin caller workflow | GitHub Actions | App repos `delivery.yml` | Done | platform-team |

**Phase 1 Workflow Structure:**

```yaml
# _build-and-release.yml (canonical)
jobs:
  build:
    steps:
      - checkout
      - setup-docker
      - build-image
      - trivy-scan (advisory or blocking based on env)
      - syft-sbom
      - push-ecr
      - upload-sarif
      - upload-sbom-artifact

  deploy:
    needs: build
    concurrency:
      group: deploy-${{ inputs.environment }}
      cancel-in-progress: false
    steps:
      - update-gitops
      - wait-for-sync (optional)
```

### 5.3 Phase 2: Authentication and Promotion (Next Sprint)

| Item | Tool/Tech | Integration Point | Status | Owner |
|------|-----------|-------------------|--------|-------|
| GitHub App creation | GitHub | Org settings | Pending | platform-team |
| App credentials storage | AWS Secrets Manager | `goldenpath/{env}/github-app` | Pending | platform-team |
| Git write-back config | argocd-image-updater | Values per environment | Pending | platform-team |
| Promotion workflow | GitHub Actions | `_promote.yml` | Pending | platform-team |
| `<env>-<sha>` tagging | GitHub Actions | Build job | Pending | platform-team |
| ECR immutability | Terraform | Per-env configuration | Pending | platform-team |

**Phase 2 Promotion Flow:**

```
dev (auto) → test (manual) → staging (manual) → prod (approval)
     ↓           ↓              ↓                 ↓
  :latest    test-abc123    staging-abc123    prod-abc123
```

### 5.4 Phase 3: Governance and DAST (Following Sprint)

| Item | Tool/Tech | Integration Point | Status | Owner |
|------|-----------|-------------------|--------|-------|
| OWASP ZAP integration | ZAP | Test environment workflow | Pending | platform-team |
| Semgrep SAST | Semgrep | PR check job | Pending | platform-team |
| Bootstrap runbook | Docs | `docs/70-operations/runbooks/` | Pending | platform-team |
| Onboarding guide | Docs | `docs/30-onboarding/` | Pending | platform-team |
| GitHub template repo | GitHub | Template repository | Pending | platform-team |
| Periodic scan workflow | GitHub Actions | Scheduled workflow | Pending | platform-team |
| Platform health dashboard | TBD | Metrics integration | Pending | platform-team |

**Phase 3 DAST Integration:**

```yaml
# In test environment workflow
dast-scan:
  needs: deploy-test
  steps:
    - name: OWASP ZAP Scan
      uses: zaproxy/action-full-scan@v0
      with:
        target: 'https://app.test.goldenpath.example.com'
        rules_file_name: '.zap/rules.tsv'
        cmd_options: '-a'
```

### 5.5 Phase 4: V1.1 Enhancements (Future)

| Item | Tool/Tech | Integration Point | Status | Owner |
|------|-----------|-------------------|--------|-------|
| Image signing | Cosign | Build job | Deferred | platform-team |
| SLSA provenance | slsa-github-generator | Build job | Deferred | platform-team |
| Rollback playbook | Docs | `docs/70-operations/runbooks/` | Deferred | platform-team |
| Distroless mandate | Policy | Dockerfile validation | Deferred | platform-team |
| Platform health dashboard | Grafana/etc | Metrics aggregation | Deferred | platform-team |
| Snyk enterprise | Snyk | Org-wide integration | Deferred | platform-team |

---

## 6. Developer Requirements Matrix

### 6.1 Onboarding Checklist

| Requirement | Mandatory | Timeline | Verification |
|-------------|-----------|----------|--------------|
| Install pre-commit | Yes | Day 1 | `pre-commit --version` |
| Install Gitleaks hook | Yes | Day 1 | `pre-commit run gitleaks` |
| Configure IDE linting | Yes | Week 1 | Code review |
| Install Snyk extension | Recommended | Week 1 | Self-attestation |
| Complete security training | Yes | Month 1 | Training record |

### 6.2 Pre-commit Configuration

```yaml
# .pre-commit-config.yaml (template)
repos:
  # MANDATORY: Secret detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  # MANDATORY: Basic checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: trailing-whitespace
      - id: end-of-file-fixer

  # RECOMMENDED: YAML validation
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.33.0
    hooks:
      - id: yamllint
        args: ['-d', '{extends: relaxed, rules: {line-length: {max: 120}}}']
```

---

## 7. Governance Registry Integration

### 7.1 Artifacts Stored

| Artifact | Format | Location | Retention |
|----------|--------|----------|-----------|
| SBOM | SPDX JSON | `environments/{env}/latest/sbom.spdx.json` | Per release |
| SARIF results | SARIF | GitHub Security tab | 90 days |
| Scan summaries | CSV | `environments/{env}/latest/scan_summary.csv` | Per release |
| Audit logs | JSON | `audit/{env}/{date}/` | 1 year |

### 7.2 Platform Health Metrics

| Metric | Source | Dashboard |
|--------|--------|-----------|
| CVE count by severity | Trivy | Platform Health |
| Dependency vulnerabilities | Snyk/Trivy | Platform Health |
| Secret scan failures | Gitleaks | Platform Health |
| DAST findings | ZAP | Platform Health |
| SBOM coverage | Syft | Platform Health |

---

## 8. Exception Process

### 8.1 Security Gate Exceptions

| Step | Action | Owner | Timeline |
|------|--------|-------|----------|
| 1 | Document exception in ADR | Requestor | Day 1 |
| 2 | Risk assessment | Security team | Day 2-3 |
| 3 | Platform-team approval | Platform lead | Day 3-5 |
| 4 | Time-boxed remediation plan | Requestor | With approval |
| 5 | Compensating controls | Security team | With approval |
| 6 | Review at expiry | All parties | Max 30 days |

### 8.2 Tool Exceptions

| Requirement | Evidence Required |
|-------------|-------------------|
| Equivalent coverage | Comparison matrix |
| Platform-team approval | Signed ADR |
| Governance integration | Audit log compatibility |

---

## 9. Success Criteria

### 9.1 Phase 1 Complete When

- [x] Canonical workflow deployed and tested
      Evidence: `.github/workflows/_build-and-release.yml`
- [x] Trivy blocking gates active for test/staging/prod
      Evidence: `_build-and-release.yml` (exit-code: 1 for test/staging/prod)
- [x] SARIF uploads to GitHub Security tab
      Evidence: `_build-and-release.yml` (upload-sarif step)
- [x] SBOM generated for every build
      Evidence: Syft step in `_build-and-release.yml`
- [x] Gitleaks in PR checks
      Evidence: `.github/workflows/gitleaks.yml` + build job integration
- [x] Pre-commit template available
      Evidence: `.pre-commit-config.yaml`
- [x] `hello-goldenpath-idp` using thin caller
      Evidence: `hello-goldenpath-idp/.github/workflows/delivery.yml`

### 9.2 Phase 2 Complete When

- [ ] GitHub App created and credentials stored
- [ ] Git write-back working for all cloud environments
- [ ] `<env>-<sha>` tags working
- [ ] Promotion workflow tested end-to-end
- [ ] ECR immutability enforced for test/staging/prod

### 9.3 Phase 3 Complete When

- [ ] OWASP ZAP running in test environment
- [ ] Semgrep in PR checks
- [ ] Bootstrap runbook documented
- [ ] Onboarding guide complete
- [ ] Template repo available
- [ ] Periodic scans scheduled

### 9.4 Phase 4 (V1.1) Complete When

- [ ] Images signed with Cosign
- [ ] SLSA provenance attached
- [ ] Rollback playbook documented
- [ ] Distroless mandate enforced
- [ ] Platform health dashboard live

---

## Changelog

| Date       | Change                                       | Author        |
|------------|----------------------------------------------|---------------|
| 2026-02-01 | Phase 1 marked complete with evidence links  | platform-team |
| 2026-01-19 | Initial version                              | platform-team |

---

## Related Documents

- GOV-0012: Build Pipeline Standards
- GOV-0013: DevSecOps Security Standards
- GOV-0015: Build Pipeline Testing Matrix
- OB-0001: Developer Security Tooling Onboarding
- ADR-0170: Build Pipeline Architecture and Multi-Repo Strategy
- Session: `session_capture/2026-01-19-build-pipeline-architecture.md`

Signed: platform-team (2026-01-19)
