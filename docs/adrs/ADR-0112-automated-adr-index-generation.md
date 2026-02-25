---
id: ADR-0112-automated-adr-index-generation
title: 'ADR-0112: Automated ADR Index Generation'
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0110-idp-knowledge-graph-architecture
  - ADR-0111-platform-documentation-auto-healing
  - ADR-0112-automated-adr-index-generation
  - ADR-0133
  - ADR_INDEX_AUTOMATION_SPEC
  - CL-0068-adr-index-automation
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-06
version: 1.0
date: 2026-01-06
breaking_change: false
---

## ADR-0112: Automated ADR Index Generation

## Context

As the number of Architecture Decision Records (ADRs) grows (currently 100+), keeping the `01_adr_index.md` in sync manually has become error-prone. We frequently observe drift in statuses, dates, and related links. While we have a standardized metadata schema, the index remains a manual "View" that requires constant reconciliation.

## Decision

We will automate the generation of the ADR Index from the source files' metadata.

### Iteration 1: Git-Native Automation

We will implement a `scripts/generate_adr_index.py` tool that:

1. Parses YAML frontmatter from all ADR files.
2. Regenerates the Markdown table and metadata associations.
3. Is enforced by the `ci-index-auto-heal.yml` workflow.

### Transition Plan (Iteration 2)

This Git-native solution is an interim measure to ensure immediate consistency. As the IDP matures, we will transition the ADR lifecycle into **Backstage**. In that phase, the physical index file may be replaced or augmented by a dynamic portal view powered by the Knowledge Graph.

## Consequences

### Positive

- **Single Source of Truth**: The ADR file itself owns its metadata.
- **Zero Drift**: Automation ensures the index always reflects the physical reality.
- **Improved Discoverability**: Context snippets in the index are always up-to-date.

### Negative

- **Build Dependency**: Modifying an ADR metadata field now requires a script run to update the index (handled by auto-healing).

## Alternatives Considered

- **Manual Maintenance**: Rejected due to high overhead and persistent drift.
- **Direct-to-Backstage**: Deferred; requires further portal configuration and Knowledge Graph maturity.
