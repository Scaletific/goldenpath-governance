---
id: GOV-0056-tag-scoped-policy-template
title: Tag-Scoped IAM Policy Template (Living)
type: policy
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
  maturity: 1
schema_version: 1
relates_to:
  - GOV-0023-platform-governance
  - GOV-0042-resource-tagging
  - ADR-0039-platform-tag-scoped-iam-policy-template
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
status: active
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
aliases:
  - 01_TAG_SCOPED_POLICY_TEMPLATE
---

# Tag-Scoped IAM Policy Template (Living)

This document defines the standard template for **tag-scoped** IAM policies
used by automation that deletes or mutates infrastructure. Use it whenever a
role can perform destructive actions (cleanup, teardown, delete).

## Why this exists

Tag scoping reduces blast radius. Deletion is only allowed when the target
resource carries the expected tags (for example `BuildId` and `Environment`).
Read-only actions stay unscoped so discovery still works.

## Required tags

Use the canonical tags from `docs/governance/GOV-0042-resource-tagging.md`. For cleanup and
teardown, **BuildId** and **Environment** are the minimum set.

## Template (preferred)

Use session tags to enforce the exact BuildId/Environment for a run.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyDiscovery",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "eks:Describe*",
        "eks:List*",
        "elasticloadbalancing:Describe*",
        "tag:GetResources"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DeleteTaggedResources",
      "Effect": "Allow",
      "Action": [
        "ec2:TerminateInstances",
        "ec2:DeleteNatGateway",
        "ec2:ReleaseAddress",
        "ec2:DeleteRouteTable",
        "ec2:DeleteSubnet",
        "ec2:DeleteSecurityGroup",
        "ec2:DetachInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:DeleteVpc",
        "eks:DeleteNodegroup",
        "eks:DeleteCluster",
        "elasticloadbalancing:DeleteLoadBalancer"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/BuildId": "${aws:PrincipalTag/BuildId}",
          "aws:ResourceTag/Environment": "${aws:PrincipalTag/Environment}"
        }
      }
    }
  ]
}
```

## Template (minimum safety)

If session tags are not available, use a broad tag match as a safety net.
This is weaker than the preferred template and should be treated as temporary.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DeleteTaggedResources",
      "Effect": "Allow",
      "Action": [
        "ec2:TerminateInstances",
        "eks:DeleteCluster",
        "elasticloadbalancing:DeleteLoadBalancer"
      ],
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "aws:ResourceTag/BuildId": "*",
          "aws:ResourceTag/Environment": "*"
        }
      }
    }
  ]
}
```

## Notes

- If tags are missing, deletes will fail. This is intentional.
- Keep read-only actions unscoped to avoid discovery failures.
- Always update this template when new delete actions are introduced.
