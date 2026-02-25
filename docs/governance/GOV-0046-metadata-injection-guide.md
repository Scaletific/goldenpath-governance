---
id: GOV-0046-metadata-injection-guide
title: Metadata Injection Guide
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0089-closed-loop-metadata-injection
  - GOV-0047-metadata-maintenance-guide
  - METADATA_VALIDATION_GUIDE
category: governance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
aliases:
  - METADATA_INJECTION_GUIDE
---

# Metadata Injection Guide

This guide documents the "Closed-Loop Governance" strategy, which propagates metadata from static sidecar files into live Kubernetes resources.

## Concepts

The GoldenPath IDP uses a "Push-Based Governance" model:
1. **Source of Truth**: The `metadata.yaml` sidecar (or Markdown frontmatter).
2. **The Accelerator**: `scripts/standardize-metadata.py` (The Healer).
3. **The Target**: Kubernetes manifests (`values.yaml`, ArgoCD `Application`).

## How it Works

### 1. Automated Injection
When `standardize-metadata.py` processes a `metadata.yaml` file, it triggers a **Governance Injection Pass**. It searches for associated files:
- `values.yaml` in the same directory.
- `values/*.yaml` for multi-environment charts.
- `deploy/**/values.yaml` for application workspaces.
- ArgoCD Applications in `gitops/argocd/apps/`.

### 2. Manifest Enrichment
For Helm charts, the healer injects a `governance` block:
```yaml
governance:
  id: HELM_KONG
  owner: platform-team
  risk_profile:
    production_impact: high
```

For ArgoCD applications, it adds **Kubernetes Annotations**:
```yaml
metadata:
  annotations:
    goldenpath.idp/id: TOOL_KONG
    goldenpath.idp/owner: platform-team
    goldenpath.idp/risk: high
```

### 3. Template Rendering
The `scripts/render-template.py` tool supports nested keys, allowing manifests to consume this data:
```yaml
metadata:
  annotations:
    goldenpath.idp/id: "{{ values.governance.id }}"
```

## Troubleshooting

### Missing Annotations
- Ensure the `metadata.yaml` exists and is standardized.
- Verify that the deployment file path matches the scanner's logic in `standardize-metadata.py`.

### Rendering Failures
- Check that the `values.yaml` has the `governance` block.
- Ensure `render-template.py` is called with the target values file.
