---
id: GOV-0042-resource-tagging
title: Resource Tagging (Living)
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
  - GOV-0023-platform-governance
  - GOV-0056-tag-scoped-policy-template
  - 02_PLATFORM_BOUNDARIES
  - GOV-0041-cost-governance
  - GOV-0040-secrets-catalog-policy
  - ADR-0037-platform-resource-tagging-policy
  - ADR-0039-platform-tag-scoped-iam-policy-template
  - ADR-0051-platform-reliability-metrics-contract-minimums
  - METADATA_STRATEGY
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
aliases:
  - 35_RESOURCE_TAGGING
---

# Resource Tagging (Living)

Doc contract:

- Purpose: Define required tags and cleanup implications for platform resources.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/adrs/ADR-0037-platform-resource-tagging-policy.md, docs/governance/policies/GOV-0056-tag-scoped-policy-template.md, docs/governance/GOV-0023-platform-governance.md

This document is the **living index** of platform resource tags. It defines the
required tag set, where tags are applied, and how tagging affects cleanup.

This document is governed by `docs/adrs/ADR-0037-platform-resource-tagging-policy.md`.

---

## Required tags (V1)

| Tag | Required | Source | Example | Notes |
| --- | --- | --- | --- | --- |
| BuildId | Yes | CI / operator input | `26-12-28-02` | Unique per run. Drives cleanup. |
| Environment | Yes | CI / terraform vars | `dev` | Used for audit and scoping. |
| Lifecycle | Yes | CI / terraform vars | `ephemeral` | `ephemeral` or `persistent`. |
| ManagedBy | Yes | Terraform defaults | `terraform` | Ownership signal for automation. |
| Owner | Yes | CI / terraform vars | `platform-team` | Human accountable owner. |
| Project | Yes | Terraform defaults | `goldenpath-idp` | Cost allocation and grouping. |

## Recommended tags (V1)

| Tag | Required | Source | Example | Notes |
| --- | --- | --- | --- | --- |
| Name | Optional | Terraform resource | `goldenpath-dev-26-12-28-02-vpc` | Improves console readability. |
| Tier | Optional | Terraform resource | `public` | Used for subnet/route intent. |

---

## Where tags are applied

- **Terraform-managed AWS resources:** tags come from `var.tags` plus
  environment-specific tag overlays.
- **EKS add-ons and OIDC provider:** explicitly tagged for consistency.
- **Bootstrap tooling:** uses the same tag schema for any AWS resources it creates.
- **Kubernetes resources:** use **labels/annotations** instead of AWS tags
  (e.g., `app.kubernetes.io/*`, `buildId`, `environment`).

---

## Non-taggable resources and how we remove them

Some AWS resources cannot be tagged directly. These are removed **indirectly**
by deleting their parent resources or by Kubernetes-driven cleanup.

### AWS non-taggable resources

Examples:

- IAM policy attachments
- Route table associations
- Some dependency edges (e.g., EKS-managed attachments)

How they are removed:

- **Terraform destroy** removes the parent resource, which removes the attachment.
- **Targeted cleanup steps** remove load balancers or networking resources that
  block dependency deletion.

### Kubernetes-native resources

Examples:

- ServiceAccounts
- Roles/RoleBindings
- Deployments/Services

How they are removed:

- **Namespace deletion** (preferred) removes all child resources.
- **Label/selector cleanup** when a namespace is shared.

---

## Cleanup implications

- **Teardown:** relies on Terraform destroy and cluster deletion. Tags must exist
  for post-destroy cleanup and audit.
- **Orphan cleanup:** uses BuildId + Environment tags to locate resources.
  Missing tags mean **manual cleanup**.
- **IAM cleanup policy:** delete actions are tag-scoped; missing tags will block
  automated cleanup.
- **IAM resources:** IAM policies and roles are **not** deleted by orphan cleanup.

---

## Changing or adding tags

1. Propose changes in a new ADR that supersedes the prior decision.
2. Update this document with the new tag(s).
3. Update Terraform modules and bootstrap tooling to apply the tag(s).
4. Update governance if the tag affects audit or cleanup expectations.
5. Update `docs/governance/GOV-0040-secrets-catalog-policy.md` to keep
   Backstage cataloging and tag keys aligned.

---

## Common failure modes

- **Missing tags:** orphan cleanup skips resources, causing leaks.
- **BuildId reuse:** cleanup can delete active resources.
- **Mixed tag values:** audit and cost reporting become unreliable.

---

## References

- `docs/adrs/ADR-0037-platform-resource-tagging-policy.md`
- `docs/governance/GOV-0023-platform-governance.md`
