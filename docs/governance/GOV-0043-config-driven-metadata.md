---
id: GOV-0043-config-driven-metadata
title: Config-Driven Metadata Governance
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
  - CL-0074-config-driven-metadata-governance
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
aliases:
  - CONFIG_DRIVEN_METADATA
---

## Config-Driven Metadata Governance

## Overview

This document defines the strategy for **Config-Driven Metadata Governance**. Historically, platform rules (standardization and validation) were hardcoded in Python scripts. This strategy moves those rules into **YAML Schemas**, making the governance model easier to evolve and audit.

## The Governance Stack

### 1. The Source of Truth ([`enums.yaml`](../../schemas/metadata/enums.yaml))

Defines the allowed values for all metadata fields (Owners, Domains, Statuses, Risk Levels).

### 2. The Rule Sets (`schemas/metadata/*.schema.yaml`)

Define the structure, required fields, and default values for specific document kinds (ADRs, Changelogs, Runbooks).

### 3. The Control Engine (`scripts/lib/metadata_config.py`)

A shared library that connects the schemas to the enforcement scripts.

## How it Works

1. **Schema Discovery**: When a script runs, it identifies the "Kind" of a file (e.g., `adr`).
2. **Schema Loading**: It loads the corresponding `adr.schema.yaml`.
3. **Dynamic Enforcement**:
   - **Validation**: Ensures every required field from the schema is present and valid according to the enums.
   - **Standardization**: Injects missing fields based on the `default` values defined in the schema.

## Benefits

- **O(1) Schema Evolution**: To add a new required field across the whole repo, you only edit one YAML file.
- **Visual Consistency**: Ensures all metadata blocks use the same casing and order.
- **Zero-Code Rules**: Security and Architects can update platform standards without writing Python.

---
> [!NOTE]
> This model ensures the platform remains "Born Governed" by aligning technical enforcement directly with human-readable architecture definitions.
