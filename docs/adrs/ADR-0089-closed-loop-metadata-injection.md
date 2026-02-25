---
id: ADR-0089-closed-loop-metadata-injection
title: 'ADR-0089: Closed-Loop Metadata Injection'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0089-closed-loop-metadata-injection
  - CL-0047-closed-loop-governance
  - GOV-0046-metadata-injection-guide
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0089: Closed-Loop Metadata Injection

## Status
Accepted

## Context
We have established a robust metadata governance system using sidecars (`metadata.yaml`). However, this metadata remained isolated from the live running resources in Kubernetes. To enable field-level visibility and auditing in a live cluster, we need a way to propagate this metadata into deployment artifacts.

## Decision
We will implement "Closed-Loop Governance" by automatically injecting metadata from governance sidecars into Kubernetes manifests (Helm values and ArgoCD Applications).

1. **Automated Injection**: `scripts/standardize-metadata.py` will serve as the propagation engine.
2. **Standard Keys**: Metadata will be injected into a `governance` block in `values.yaml` files.
3. **K8s Annotations**: Delivery resources (ArgoCD Apps) will be enriched with `goldenpath.idp/*` annotations.
4. **Template Support**: `render-template.py` will be enhanced to support nested metadata resolution.

## Consequences
- **Positive**: Live resources carry their ownership and risk context, enabling real-time auditing.
- **Positive**: Eliminates manual synchronization between documentation and infrastructure config.
- **Neutral**: `values.yaml` files will now be partially managed by automation.
- **Negative**: Increased complexity in the standardization script.
