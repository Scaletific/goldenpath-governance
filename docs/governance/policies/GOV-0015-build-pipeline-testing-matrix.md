---
id: GOV-0015-build-pipeline-testing-matrix
title: Build Pipeline Testing Matrix
type: governance
owner: platform-team
status: draft
domain: platform-core
applies_to: []
lifecycle: draft
exempt: false
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: medium
schema_version: 1
relates_to:
  - ADR-0170
  - ADR-0182-tdd-philosophy
  - APP_BUILD_PIPELINE
  - RB-0036
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
effective_date: 2026-01-20
review_date: 2026-07-20
related_adrs:
  - ADR-0170
related_govs:
  - GOV-0012
  - GOV-0013
  - GOV-0014
---

# GOV-0015: Build Pipeline Testing Matrix

## Purpose

Provide a consistent, auditable testing matrix for the GoldenPath application
build and promotion pipeline. This matrix is designed to be readable by humans
and verifiable by machines.

## Scope

All application repositories using the canonical pipeline in `GOV-0012`.

## Scoring System

| Score | Meaning |
|-------|---------|
| 0 | Not implemented / Failing |
| 1 | Partially implemented / Manual workaround |
| 2 | Fully implemented / Passing |

**Passing Threshold:** Minimum 80% of max score per category.

**Must-Pass Tests (hard gates):** SEC-02, SEC-04, SEC-05, GATE-01, TAG-06, TAG-07.

## Evidence Standards

Primary evidence sources:

- GitHub Actions logs / job summary
- Git commit hash + author (for Git write-back)
- ECR tags / digests
- Argo CD UI status
- Local CLI output (for DX checks)

## Category 1: Security Gates (Max: 14 points)

| Test ID | Test Case | Env | Preconditions | Evidence | Expected Behavior | Score |
|---------|-----------|-----|---------------|----------|-------------------|-------|
| SEC-01 | Gitleaks detects hardcoded secret | dev | Pipeline run | GH logs | Advisory warning only | /2 |
| SEC-02 | Gitleaks detects hardcoded secret | test+ | Pipeline run | GH logs | Build fails | /2 |
| SEC-03 | Trivy finds HIGH/CRITICAL CVE | dev | Image built | GH logs | Advisory warning only | /2 |
| SEC-04 | Trivy finds HIGH/CRITICAL CVE | test+ | Image built | GH logs | Build fails | /2 |
| SEC-05 | SARIF uploaded | test+ | Trivy run | GH Security tab | SARIF visible | /2 |
| SEC-06 | SBOM generated (SPDX) | test+ | Image built | Build artifacts | SBOM downloadable | /2 |
| SEC-07 | Clean image passes scans | all | Image built | GH logs | Build succeeds | /2 |

## Category 2: Tagging & Promotion (Max: 14 points)

| Test ID | Test Case | Env | Preconditions | Evidence | Expected Behavior | Score |
|---------|-----------|-----|---------------|----------|-------------------|-------|
| TAG-01 | Build produces `:latest` | dev | Build run | ECR tags | `:latest` present | /2 |
| TAG-02 | Build produces `<sha>` tag | CI/build | Build run | ECR tags | `<sha>` present | /2 |
| TAG-03 | Promote dev->test | test | Source tag valid | ECR tags | `test-<sha>` exists | /2 |
| TAG-04 | Promote test->staging | staging | Source tag valid | ECR tags | `staging-<sha>` exists | /2 |
| TAG-05 | Promote staging->prod | prod | Source tag valid | ECR tags | `prod-<sha>` exists | /2 |
| TAG-06 | Invalid promotion path rejected | all | Promotion run | GH logs | dev->prod fails | /2 |
| TAG-07 | Invalid tag format rejected | test+ | Promotion run | GH logs | `:latest` rejected | /2 |

## Category 3: Pipeline Gates & Enforcement (Max: 12 points)

| Test ID | Test Case | Env | Preconditions | Evidence | Expected Behavior | Score |
|---------|-----------|-----|---------------|----------|-------------------|-------|
| GATE-01 | Pipeline-check blocks promotion | test+ | No secret | GH logs | Promotion fails with clear error | /2 |
| GATE-02 | Dev advisory only | dev->test | Secret missing | GH logs | Warning only | /2 |
| GATE-03 | Concurrency queues deploys | all | Two deploys | GH logs | Second waits | /2 |
| GATE-04 | Prod approval required | prod | Approval gate on | GH UI | Workflow waits | /2 |
| GATE-05 | Tests run before build | all | `test_command` set | GH logs | Fail fast | /2 |
| GATE-06 | Build summary generated | all | Build run | GH summary | Summary visible | /2 |

## Category 4: GitOps Integration (Max: 12 points)

| Test ID | Test Case | Env | Preconditions | Evidence | Expected Behavior | Score |
|---------|-----------|-----|---------------|----------|-------------------|-------|
| GIT-01 | Image Updater detects new tag | AWS | Pipeline enabled | Git commit hash | Commit created | /2 |
| GIT-02 | Git write-back uses GitHub App | AWS | Pipeline enabled | Git commit author | `argocd-image-updater` | /2 |
| GIT-03 | ArgoCD syncs after tag update | AWS | Auto-sync on | Argo UI | Pod runs new image | /2 |
| GIT-04 | Digest strategy works | local | Local updater | Argo logs | `:latest` change triggers update | /2 |
| GIT-05 | Name strategy works | test+ | Env-sha tags | Argo logs | `<env>-<sha>` updates | /2 |
| GIT-06 | Prod sync is manual | prod | Auto-sync off | Argo UI | Manual sync required | /2 |

## Category 5: Developer Experience (Max: 10 points)

| Test ID | Test Case | Env | Preconditions | Evidence | Expected Behavior | Score |
|---------|-----------|-----|---------------|----------|-------------------|-------|
| DX-01 | Thin caller workflow works | all | App repo setup | GH logs | Build via canonical workflow | /2 |
| DX-02 | Pre-commit hooks run | local | Hooks installed | Local logs | Gitleaks/yamllint pass | /2 |
| DX-03 | `make pipeline-status` | all | Tools installed | CLI output | Correct status | /2 |
| DX-04 | `make pipeline-enable` | AWS | Secret exists | CLI output | K8s secret created | /2 |
| DX-05 | Errors are actionable | all | Failure case | GH logs | References RB-0036/0037 | /2 |

## Scoring Summary

| Category | Max Score | Passing (80%) |
|----------|-----------|---------------|
| Security Gates | 14 | 11+ |
| Tagging & Promotion | 14 | 11+ |
| Pipeline Gates | 12 | 10+ |
| GitOps Integration | 12 | 10+ |
| Developer Experience | 10 | 8+ |
| **Total** | **62** | **50+** |

## Phase 3+ Optional Tests (Not Scored Now)

| Test ID | Test Case | Phase |
|---------|-----------|-------|
| SEC-08 | Base image policy enforced | Phase 3 |
| SEC-09 | Semgrep SAST detects vulnerability | Phase 3 |
| SEC-10 | OWASP ZAP DAST scan passes | Phase 3 |
| SEC-11 | Image signed with Cosign | Phase 4 |
| SEC-12 | SLSA provenance attached | Phase 4 |

## Notes

- Base image enforcement is intentionally excluded from scoring until Phase 3.
- Evidence should link to the specific run/commit to be machine-verifiable.
