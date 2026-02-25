---
id: VARIABLE_MAPPING_INDEX
title: IAM Policy-to-Variable Mapping Index
type: policy
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to: []
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
---

## IAM Policy-to-Variable Mapping Index

This index provides the definitive mapping between raw JSON policy fragments and the Terraform variables used to deploy them.

## Mapping Table

|Policy File (JSON)|Terraform Variable|Target Role / Usage|
|:---|:---|:---|
|`[ecr-combined-policy.json](ecr-combined-policy.json)`|`var.ecr_combined_policy_json`|**App/Platform**: Registry Mgmt + Image Push|
|`[ci-teardown-orphan-cleanup.json](ci-teardown-orphan-cleanup.json)`|`var.teardown_policy_json`|**CI Runner**: Delete tagged resources|
|`[ci-apply-iam-instance-profile-read.json](ci-apply-iam-instance-profile-read.json)`|`var.iam_read_policy_json`|**CI Runner**: List Instance Profiles|
|`[ci-teardown-extra-permissions.json](ci-teardown-extra-permissions.json)`|`var.extra_cleanup_policy_json`|**CI Runner**: Supplemental cleanup actions|

---

## Implementation Pattern

### 1. The JSON Source

Policies are kept as "pure" JSON to allow for easy validation and direct usage in the AWS CLI or Console if needed.
Location: `docs/governance/policies/iam/*.json`

### 2. The Terraform Capture

Variables are defined in `modules/aws_iam/variables.tf`:

```hcl
variable "ecr_mgmt_policy_json" {
  type        = string
  description = "JSON policy for ECR registry management"
}
```

### 3. The Deployment

Resource definition in `modules/aws_iam/main.tf`:

```hcl
resource "aws_iam_policy" "ecr_mgmt" {
  name   = "ECRRegistryManagement"
  policy = var.ecr_mgmt_policy_json
}
```

---

## Validation

- **JSON Linting**: All files in this directory are linted via `pre-commit` hooks.
- **Traceability**: Changes to JSON files must be cross-referenced in the `README.md` mapping above.
