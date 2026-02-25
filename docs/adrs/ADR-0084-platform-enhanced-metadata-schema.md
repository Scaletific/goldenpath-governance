---
id: ADR-0084-platform-enhanced-metadata-schema
title: 'ADR-0084: Enhanced Metadata Schema for Knowledge Graph'
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
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - 02_adr_template
  - ADR-0082-platform-metadata-validation
  - ADR-0083-platform-metadata-backfill-protocol
  - ADR-0084-platform-enhanced-metadata-schema
  - ADR-0088-automated-metadata-remediation
  - ADR-0113-platform-queryable-intelligence-enums
  - ADR-0173-governance-doc-naming-migration
  - CL-0042-metadata-backfill-batch-1
  - CL-0043-complete-metadata-backfill
  - METADATA_STRATEGY
  - METADATA_VALIDATION_GUIDE
  - RB-0018-metadata-backfill-script
  - RB-0019-relationship-extraction-script
  - GOV-0054-script-certification-audit
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
version: 1.0
breaking_change: false
---

# ADR-0084: Enhanced Metadata Schema for Knowledge Graph

**Date:** 2026-01-04
**Status:** Active
**Context:** Metadata backfill initiative
**Related:** ADR-0082 (Graph RAG), ADR-0083 (Metadata Strategy), METADATA_STRATEGY.md

## Context

The repository contains 300+ markdown files across documentation, modules, applications, and infrastructure code. To enable Knowledge Graph capabilities and semantic search, we need a comprehensive metadata schema that captures:

- Document identity and classification
- Inter-document relationships
- Version tracking for Helm charts and components
- Dependency tracking for modules and applications
- Governance and risk information

The existing METADATA_STRATEGY.md defined a baseline schema, but didn't include category taxonomy, version tracking, or dependency management.

## Decision

Implement an enhanced metadata schema with the following fields:

### Core Identity

- `id`: Unique identifier (ADR-0084, CL-0043, module name)
- `title`: Document title (quoted if contains special characters)
- `type`: Document type (adr, changelog, contract, runbook, policy, documentation, template)
- `category`: Directory-based category (00-foundations, 20-contracts, modules, apps, gitops, etc.)
- `version`: Version number (extracted from Helm/ArgoCD or defaults to 1.0)

### Ownership & Status

- `owner`: Responsible team (platform-team)
- `status`: Current status (active, deprecated, archived, draft)

### Dependencies & Relationships

- `dependencies`: Array of module/chart/image dependencies
- `relates_to`: Array of related document IDs, PR references, workflow files

### Governance & Risk

- `risk_profile`: Production impact, security risk, coupling risk
- `reliability`: Rollback strategy, observability tier
- `lifecycle`: Support date, breaking change flag

### Implementation Approach

1. **Automated Backfill Script** (`scripts/backfill-metadata.py`)
   - Scans all .md files repository-wide
   - Extracts category from directory structure
   - Detects version from content (Helm charts, ArgoCD)
   - Extracts dependencies (Terraform modules, Helm charts, container images)
   - Generates complete YAML frontmatter

2. **Relationship Extraction Script** (`scripts/extract-relationships.py`)
   - Detects 13 relationship patterns from content
   - Extracts PR references (`PR-107`)
   - Links to GitHub workflow files (`workflow:pr-labeler`)
   - Populates `relates_to` field automatically

3. **Category Taxonomy**
   - Uses directory structure as source of truth
   - Docs: numerical prefixes (00-foundations, 10-governance, 20-contracts, etc.)
   - Code: top-level directories (modules, apps, gitops, envs, bootstrap, etc.)

4. **Version Detection**
   - Helm charts: Extract from `version:` or `appVersion:` mentions
   - ArgoCD references: Extract from version patterns
   - Default: 1.0 for documentation

5. **Dependency Extraction**
   - Terraform modules: Extract `module "name"` references
   - Helm charts: Extract chart dependencies
   - Apps: Extract container image references (limited to 3)

## Consequences

### Positive

1. **Knowledge Graph Foundation**
   - All 300+ documents become nodes with metadata
   - Relationships form edges between documents
   - Enables graph traversal and semantic queries

2. **Dependency Tracking**
   - Visibility into module dependencies
   - Track Helm chart/ArgoCD versions
   - Identify container image usage

3. **Category Taxonomy**
   - Hierarchical organization (foundations → governance → contracts → operations)
   - Enables category-based queries
   - Automatic from directory structure

4. **Relationship Discovery**
   - 70% auto-populated via 13 detection patterns
   - Links ADRs to implementations
   - Connects PRs to documentation

5. **Automated Maintenance**
   - Scripts can re-run on new files
   - Consistent metadata across repository
   - Validation via CI (validate_metadata.py)

### Negative

1. **Maintenance Overhead**
   - Must keep scripts updated with new patterns
   - Dependencies must be manually curated for accuracy
   - Version tracking requires content parsing

2. **File Size Increase**
   - Each file grows by ~20 lines of YAML frontmatter
   - Not significant for .md files

3. **Migration Effort**
   - Initial backfill requires running scripts
   - Manual refinement needed for 30% of relationships

### Neutral

1. **Not Enforced on Non-Markdown Files**
   - Terraform .tf files use HCL tags (Phase 2)
   - YAML files cannot have frontmatter

## Alternatives Considered

### Alternative 1: External Metadata Database

Store metadata in separate JSON/YAML index files instead of frontmatter.

**Rejected because:**

- Metadata separated from content
- Sync issues between metadata and files
- More complex to maintain

### Alternative 2: Minimal Schema (No Category, Version, Dependencies)

Use only the baseline from METADATA_STRATEGY.md.

**Rejected because:**

- Insufficient for Knowledge Graph queries
- No dependency tracking
- Category taxonomy enables better organization

### Alternative 3: Manual Curation Only

No automation scripts, manually add metadata.

**Rejected because:**

- Not scalable for 300+ files
- Inconsistent metadata quality
- Time-intensive

## Implementation

1. Create backfill script with category, version, dependencies extraction
2. Create relationship extraction script with 13 patterns
3. Run scripts on all markdown files
4. Validate with validate_metadata.py
5. Document in changelog (CL-0043)
6. Commit all changes

## Validation

- Scripts tested on sample files
- Dry-run validates pattern detection
- Expected coverage: 100% metadata, 70% relationships
- Schema aligns with METADATA_STRATEGY.md

## References

- METADATA_STRATEGY.md - Original schema definition
- ADR-0082 - Graph RAG Knowledge Layer
- ADR-0083 - Metadata Strategy ADR
- CL-0042 - Previous metadata backfill batch
