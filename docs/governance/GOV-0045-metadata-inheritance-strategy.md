---
id: GOV-0045-metadata-inheritance-strategy
title: Metadata Inheritance & Active Governance Strategy
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
  - CL-0076-metadata-inheritance-active-governance-and-leak-protection
  - CL-0076-metadata-inheritance-and-active-governance
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
aliases:
  - METADATA_INHERITANCE_STRATEGY
---

# Metadata Inheritance & Active Governance Strategy

## Overview
This strategy defines the **V1 Metadata Contract** for the Golden Path IDP. It balances developer velocity (via inheritance) with strict platform integrity (via versioning and automated loops).

## 1. Inheritance Model (Dry Governance)
To eliminate "copy-paste debt," metadata cascades down the directory tree.

```text
idp-root/
├── apps/
│   ├── metadata.yaml (v:1, owner:platform, domain:delivery)
│   └── my-app/
│       └── metadata.yaml (id:MY_APP) <── [Inherits owner/domain]
```

## 2. The Versioned Contract
Governance rules are versioned to support safe evolution.
- **Enums**: Renames are breaking; new values are safe.
- **Schemas**: Additive by default. Making an optional field required is a breaking change.

## 3. The Governance Loop
A recurring audit mechanism ensures the platform state matches the governance intent.
- **Validation**: Every resource is scanned for alignment with enums.
- **Reporting**: Immutable daily snapshots track maturity and enum drift attempts.
- **Auditing**: Parent metadata requires a 90-day review to stay "Active."

## 4. Zero-Touch Compliance (Auto-Healing)
To ensure users "don't have to think about it," the platform implements an automated discovery and injection loop:

1.  **Discovery**: Whenever a new directory is created in a `SIDECAR_MANDATED_ZONE` (e.g., `apps/`, `gitops/helm/`), the CI gate detects the missing `metadata.yaml`.
2.  **Inheritance Lookup**: The `standardize_metadata.py` script walks up the tree to the nearest parent.
3.  **Automated Injection**:
    - The script generates a local `metadata.yaml`.
    - It injects a unique, deterministic `id`.
    - It pre-populates the file with inherited `owner`, `domain`, and `reliability` data.
4.  **Auto-Commit**: The CI pipeline automatically commits this "initialization" back to the PR branch.

**Result**: A developer simply creates a folder; the platform governs it.

## 5. Migration Path
Schema evolutions are handled via formal migration scripts in `scripts/migrations/`, ensuring a controlled deprecate → migrate → enforce lifecycle.

## 6. CI Gates
PRs are blocked if:
- Metadata violates inheritance/enum rules.
- Schema files themselves are malformed or refer to non-existent enums.
- An asset lacks a unique `id`.
