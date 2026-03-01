---
id: GITHUB_WORKFLOW_PERMISSIONS
title: GitHub Workflow Permissions & Setup
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: medium
  coupling_risk: low
reliability:
  rollback_strategy: none
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - 25_DAY_ONE_CHECKLIST
  - CI_WORKFLOWS
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
category: onboarding
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# GitHub Workflow Permissions & Setup

## Context
By default, GitHub Actions workflows are restricted from creating Pull Requests or modifying the repository contents. This prevents the "Creation" workflows (e.g., `Create ECR Registry`, `Scaffold App`) from functioning correctly, as they rely on the `GITHUB_TOKEN` to open PRs for approval.

## Known Error
If this runbook is not followed, workflows will fail with:
```text
Error: GitHub Actions is not permitted to create or approve pull requests.
```

## Solution: Enable PR Creation

A repository admin must perform the following one-time configuration:

1.  Navigate to the Repository on GitHub.
2.  Go to **Settings** > **Actions** > **General**.
3.  Scroll down to the **Workflow permissions** section.
4.  Select **Read and write permissions**.
5.  **Critical**: Check the box **"Allow GitHub Actions to create and approve pull requests"**.
6.  Click **Save**.

## Verification
To verify the fix:
1.  Run the `Create ECR Registry` workflow manually via `workflow_dispatch`.
2.  Provide a test registry name (e.g., `test-permissions`).
3.  The workflow should successfully complete and output a link to a new Pull Request.

## Security Note
This setting grants the `GITHUB_TOKEN` elevated permissions. This is required for the "GitOps Self-Service" model where the robot proposes changes that a human must then approve and merge.
