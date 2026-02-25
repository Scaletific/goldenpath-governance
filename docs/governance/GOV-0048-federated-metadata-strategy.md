---
id: GOV-0048-federated-metadata-strategy
title: 'Federated Metadata Strategy: Scaling the Knowledge Graph'
type: strategy
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
  maturity: 1
relates_to:
  - CL-0045-federated-governance-onboarding
  - EC-0004-backstage-copilot-plugin
category: governance
supported_until: 2028-12-31
version: 1.0
dependencies:
  - module:governance-engine
breaking_change: false
aliases:
  - FEDERATED_METADATA_STRATEGY
---

# Federated Metadata Strategy

## Purpose
To ensure every workload in the organization is "Discoverable, Owned, and Managed" by enforcing a standard metadata schema at the point of commit.

## The Pillars of Federated Governance

### 1. The Schema as the Contract
All repositories must include a `README.md` or `metadata.yaml` with the following mandatory fields:
- `id`: Unique identifier (UUID or stable alias)
- `owner`: Team responsible for the code (e.g., `squad-alpha`)
- `type`: `app`, `lib`, `infra`, or `tool`
- `status`: `active`, `deprecated`, or `experimental`

### 2. Shift-Left Validation
Compliance is checked in two stages:
1.  **Local (Pre-commit)**: Developers receive immediate feedback during `git commit`.
2.  **Remote (CI)**: GitHub Actions block merges if metadata is missing or invalid.

### 3. Centralized Insights
The data collected from these federated checks feeds directly into:
- **Platform Health Reports**: Real-time ownership and risk maps.
- **Backstage Catalog**: Automated service discovery without manual YAML entry.
- **Security Audits**: Rapid identification of affected owners during vulnerability windows.

## Onboarding a New Repo
1.  Copy `.pre-commit-config.yaml` from the [Golden Template](template-link).
2.  Run `git init` and `pre-commit install`.
3.  Add the mandatory YAML frontmatter to your top-level `README.md`.
4.  Run `gh platform-governance validate` to check compliance.
