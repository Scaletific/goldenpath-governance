---
id: ADR-0172-cd-promotion-strategy-with-approval-gates
title: 'ADR-0172: CD Promotion Strategy with Approval Gates'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: high
  potential_savings_hours: 8.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 2026-01-22-argocd-plugin-integration
  - 20_TOOLING_APPS_MATRIX
  - 29_CD_DEPLOYMENT_CONTRACT
  - ADR-0171-platform-application-packaging-strategy
  - CL-0148
  - EC-0012-backstage-plugin-scaffold
  - PRD-0003-backstage-plugin-scaffold
  - agent_session_summary
  - audit-20260103
  - session-capture-2026-01-18-local-dev-hello-app
supersedes: []
superseded_by: []
tags:
  - cd
  - gitops
  - promotion
  - approval-gates
inheritance: {}
supported_until: 2028-01-18
version: '1.0'
breaking_change: false
---

# ADR-0172: CD Promotion Strategy with Approval Gates

- **Status:** Active
- **Date:** 2026-01-18
- **Owners:** platform-team
- **Domain:** Platform
- **Decision type:** Architecture | Operations
- **Related:** `docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md`, ADR-0171

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

With CI pipelines building and pushing images to ECR, we need a clear strategy
for how those images get promoted through environments. Key requirements:

1. **Automation** - Minimize manual steps for non-production
2. **Safety** - Production requires explicit approval
3. **Rollback** - Easy recovery when staging reveals issues
4. **Audit trail** - All changes tracked in Git

---

## Decision

### Promotion Flow

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     CD PROMOTION FLOW                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CI Build ──► ECR Push ──► Image Updater ──► Git Commit ──► Argo    │
│                                                                      │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │   DEV   │───►│  TEST   │───►│ STAGING │───►│  PROD   │          │
│  │  auto   │    │  auto   │    │  auto   │    │ MANUAL  │          │
│  │ sync    │    │ sync    │    │ sync    │    │ approval│          │
│  └─────────┘    └─────────┘    └─────────┘    └────┬────┘          │
│       │              │              │              │                 │
│       ▼              ▼              ▼              ▼                 │
│   Immediate      Immediate     Validation     Human gate            │
│   feedback       feedback      gate           + rollback            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Argo CD Sync Policies by Environment

| Environment | Sync Policy | Prune | Self-Heal | Rationale |
| ----------- | ----------- | ----- | --------- | --------- |
| local/dev   | `automated` | true  | true      | Fast iteration, immediate feedback |
| test        | `automated` | true  | true      | Integration testing, auto-deploy |
| staging     | `automated` | true  | true      | Pre-prod validation, mirrors prod |
| prod        | `manual`    | false | false     | Explicit approval required |

### Image Update Strategy

Use **Argo CD Image Updater** to:

1. Watch ECR repositories for new tags
2. Auto-commit image tag updates to Git
3. Trigger Argo CD sync (for automated envs)

Configuration per environment:

```yaml
# Dev/Test/Staging - auto-update to latest
argocd-image-updater.argoproj.io/image-list: app=<ecr-repo>
argocd-image-updater.argoproj.io/app.update-strategy: latest

# Prod - update strategy but manual sync
argocd-image-updater.argoproj.io/image-list: app=<ecr-repo>
argocd-image-updater.argoproj.io/app.update-strategy: semver
```

### Approval Gate Implementation

**Production deployments require:**

1. Image validated in staging (same SHA)
2. Manual Argo CD sync trigger
3. Git commit as audit trail

**Methods to trigger prod sync:**

```bash
# Option 1: Argo CD CLI
argocd app sync <app-name> --prune=false

# Option 2: Argo CD UI
# Click "Sync" button with review

# Option 3: GitHub PR (recommended for audit)
# Merge PR that updates prod overlay image tag
```

### Rollback Strategy

| Scenario | Action | Command |
| -------- | ------ | ------- |
| Staging fails | Revert Git commit | `git revert <commit> && git push` |
| Prod fails | Argo rollback | `argocd app rollback <app> <revision>` |
| Emergency | Revert + sync | Revert Git, force Argo sync |

**Rollback is always available because:**
- Git history preserves all previous states
- Argo CD tracks deployment revisions
- No destructive operations (prune disabled in prod)

---

## Scope

Applies to all application deployments managed by Argo CD in this platform.
Infrastructure deployments (Terraform) follow separate approval workflows.

---

## Consequences

### Positive

- Fast feedback in dev/test (seconds to deploy)
- Staging catches issues before prod
- Production protected by explicit approval
- Full audit trail in Git
- Easy rollback at any stage

### Tradeoffs / Risks

- Image Updater adds complexity
- Staging must accurately mirror prod config
- Manual prod approval can become bottleneck

### Mitigation

- Keep staging and prod overlays aligned
- Define clear SLAs for prod approvals
- Enable emergency rollback procedures

### Operational Impact

- Install Argo CD Image Updater
- Configure ECR credentials for Image Updater
- Update Argo CD Applications with correct sync policies
- Document approval process for prod deployments

---

## Alternatives Considered

- **Fully manual promotion:** Rejected. Too slow for dev/test iteration.
- **Fully automated (including prod):** Rejected. Unacceptable risk for production.
- **Branch-based promotion:** Rejected. Adds Git branch management overhead.
- **Flux CD:** Rejected. Already invested in Argo CD ecosystem.

---

## Implementation

### Phase 1: Foundation (Current)

- [x] Kustomize overlays per environment
- [x] Argo CD Applications per environment
- [ ] Install Argo CD Image Updater
- [ ] Configure ECR write-back credentials

### Phase 2: Automation

- [ ] Enable auto-sync for dev/test/staging
- [ ] Configure Image Updater annotations
- [ ] Test image update flow end-to-end

### Phase 3: Production Gates

- [ ] Disable auto-sync for prod
- [ ] Document approval process
- [ ] Add Slack/Teams notification for pending prod syncs

---

## Examples

### Argo CD Application - Dev (Auto-sync)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: hello-goldenpath-dev
  annotations:
    argocd-image-updater.argoproj.io/image-list: app=[AWS_ACCOUNT_ID].dkr.ecr.[AWS_REGION].amazonaws.com/hello-goldenpath
    argocd-image-updater.argoproj.io/app.update-strategy: latest
spec:
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Argo CD Application - Prod (Manual sync)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: hello-goldenpath-prod
  annotations:
    argocd-image-updater.argoproj.io/image-list: app=[AWS_ACCOUNT_ID].dkr.ecr.[AWS_REGION].amazonaws.com/hello-goldenpath
    argocd-image-updater.argoproj.io/app.update-strategy: semver
spec:
  syncPolicy:
    # No automated sync - requires manual approval
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
```

### Rollback Example

```bash
# View deployment history
argocd app history hello-goldenpath-prod

# Rollback to previous revision
argocd app rollback hello-goldenpath-prod 42

# Or revert in Git (recommended for audit)
git revert HEAD
git push origin main
```

---

## Follow-ups

- [ ] Install Argo CD Image Updater
- [ ] Create runbook for prod deployment approval
- [ ] Add monitoring for deployment failures
- [ ] Define SLA for prod approval turnaround

---

## Notes

This strategy balances speed and safety. The key insight is that staging
serves as the final validation gate - if it works in staging, it should
work in prod (assuming staging accurately mirrors prod config).

Production approval is a human checkpoint, not a bureaucratic hurdle.
Keep approvals fast by ensuring staging validation is thorough.
