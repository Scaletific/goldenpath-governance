---
id: ADR-0173-governance-doc-naming-migration
title: 'ADR-0173: Governance Doc Naming Migration Strategy'
type: adr
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
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - 01_adr_index
  - GOV-0029-pr-guardrails
  - ADR-0084-platform-enhanced-metadata-schema
  - METADATA_STRATEGY
supersedes: []
superseded_by: []
tags:
  - governance
  - naming
  - docs
inheritance: {}
supported_until: 2028-01-19
version: '1.0'
breaking_change: false
---

# ADR-0173: Governance Doc Naming Migration Strategy

- **Status:** Accepted
- **Date:** 2026-01-19
- **Owners:** platform-team
- **Domain:** Platform
- **Decision type:** Governance | Operations
- **Related:** `docs/governance/GOV-0029-pr-guardrails.md`, `docs/90-doc-system/METADATA_STRATEGY.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

A new naming convention for governance docs has been proposed:
`GOV-xxxx-description-of-file.md`. The current repository uses a mix of
numerical prefixes (for example `GOV-0029-pr-guardrails.md`) and domain-specific
filenames across governance docs, archives, session captures, and other
artifacts. A bulk rename would improve consistency and readability, but it
also risks breaking references, IDs, and automation tied to filenames.

The platform relies on frontmatter IDs, cross-links, and automated
relationship extraction. A breaking rename would introduce drift and
break visibility unless compatibility is preserved.

---

## Decision

We will adopt a **phased migration strategy** that separates document identity
from filename and avoids a high-risk bulk rename.

1. **New docs only** must use the `GOV-xxxx-description.md` convention.
2. **Existing docs remain** until aliases and tooling support are in place.
3. **Canonical identity** is the `id` field in frontmatter, not the filename.
4. **Alias mapping** will provide compatibility for old paths.
5. **Pilot rename** a small subset before any wider migration.

---

## Scope

**Applies to:** Governance documentation outside ADRs and changelog entries.

**Does not apply to:** ADR filenames (`ADR-xxxx`), changelog entries (`CL-xxxx`),
or session captures which have their own stable naming scheme.

---

## Consequences

### Positive

- Clean, professional naming for new governance documents.
- Reduced risk by keeping IDs stable while migrating filenames.
- Improved future readability without breaking current automation.

### Tradeoffs / Risks

- Two naming conventions will coexist during migration.
- Requires new tooling for alias resolution and validation.

### Operational impact

- Update authoring guidance and templates to enforce GOV naming for new docs.
- Add tooling to resolve old-to-new path aliases in validators and indexers.

---

## Alternatives considered

1. **Big-bang rename** of all governance docs: rejected due to breaking links,
   IDs, and automation.
2. **Do nothing**: rejected because it defers cleanup and increases future cost.
3. **Rename only top-level files**: rejected due to partial inconsistency.

---

## Follow-ups

1. Define the GOV namespace and allocation rules (who assigns GOV-xxxx).
2. Add a path-alias map (old -> new) and update validators to use it.
3. Update doc templates and PR guardrails to enforce GOV naming for new docs.
4. Run a pilot rename on 10-20 documents and validate all links.
5. Decide if and when to extend migration to legacy docs.

---

## Notes

This ADR chooses a conservative migration approach to preserve stability. If
future validation and tooling prove safe, the migration can be widened with a
separate ADR to approve a larger batch rename.
