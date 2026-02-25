---
id: PROMPT-0008
title: Document Scaffolding (EC/PRD/ADR/CL)
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-infra
relates_to:
  - GOV-0022
  - ADR-0197
  - PROMPT-0006
created: 2026-02-14
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are a platform engineer creating governance documents with the correct frontmatter schema, numbering, and directory placement.

## Context

The GoldenPath IDP uses four document types that form a lifecycle (GOV-0022):

```
EC (explore) ──→ PRD (commit) ──→ ADR (decide) ──→ CL (ship)
   optional          required        as-needed        required
```

Each type has a specific directory, frontmatter schema, and naming convention. Agents frequently make errors on: numbering (duplicates or gaps), frontmatter fields (wrong schema for the type), directory placement, and `relates_to` linking.

## Your Task

Scaffold a new governance document with correct numbering, frontmatter, directory placement, and cross-references.

## Preconditions

- [ ] You know which document type to create (see Decision Guide below).
- [ ] You know what the document relates to (PRD, ADR, EC, or standalone).

## Decision Guide (from GOV-0022)

| Question | Document Type |
|---|---|
| "Should we build X?" | EC (you're exploring) |
| "We're building X, here's the plan" | PRD (you're committing) |
| "We chose Y because Z" | ADR (you're deciding) |
| "X is shipped" | CL (you're recording) |

## Document Type Reference

### EC — Extend Capability (Explore)

| Field | Value |
|---|---|
| **Directory** | `docs/extend-capabilities/` |
| **Filename** | `EC-{NNNN}-{slug}.md` |
| **Status values** | `proposed`, `accepted`, `deferred`, `rejected` |
| **Required frontmatter** | id, title, type (`enhancement-concept`), status, lifecycle, risk_profile, relates_to, tags, priority, vq_class, estimated_roi, dependencies, effort_estimate, version |

**Frontmatter template:**

```yaml
---
id: EC-{NNNN}-{slug}
title: 'EC-{NNNN}: {Title}'
type: enhancement-concept
status: proposed
lifecycle: proposed
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
relates_to:
  - {related docs}
tags:
  - {relevant tags}
priority: {low | medium | high}
vq_class: {HV/HQ | HV/LQ | LV/HQ | LV/LQ}
estimated_roi: {one-line ROI description}
dependencies:
  - {dependency docs}
effort_estimate: {time estimate}
version: '1.0'
---
```

**Required sections:** Problem, Proposed Solution/Approach, Alternatives Considered, Open Questions, Graduation Criteria, Current Status.

### PRD — Product Requirements Document (Commit)

| Field | Value |
|---|---|
| **Directory** | `docs/20-contracts/prds/` |
| **Filename** | `PRD-{NNNN}-{slug}.md` |
| **Status values** | `draft`, `active`, `completed`, `deferred` |
| **Required frontmatter** | id, title, type (`prd`), status, owner, domain, lifecycle, risk_profile, schema_version, relates_to |

**Frontmatter template:**

```yaml
---
id: PRD-{NNNN}
title: '{Title}'
type: prd
status: active
owner: platform-team
domain: platform-core
lifecycle: active
exempt: false
risk_profile:
  production_impact: {none | low | medium | high}
  security_risk: {none | low | medium | high}
  coupling_risk: {none | low | medium | high}
schema_version: 1
relates_to:
  - {EC if applicable}
  - {related ADRs}
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
---
```

**Required sections:** Scope, Phases, Acceptance Criteria, relates_to (EC if applicable).

### ADR — Architecture Decision Record (Decide)

| Field | Value |
|---|---|
| **Directory** | `docs/adrs/` |
| **Filename** | `ADR-{NNNN}-{slug}.md` |
| **Status values** | `Proposed`, `Accepted`, `Active`, `Deprecated`, `Superseded` |
| **Required frontmatter** | id, title, type (`adr`), status, owner, domain, lifecycle, risk_profile, schema_version, relates_to |

**Frontmatter template:**

```yaml
---
id: ADR-{NNNN}
title: {Title}
type: adr
status: {Proposed | Accepted}
owner: platform-team
domain: platform-core
lifecycle: active
exempt: false
risk_profile:
  production_impact: {none | low | medium | high}
  security_risk: {none | low | medium | high}
  coupling_risk: {none | low | medium | high}
schema_version: 1
relates_to:
  - {PRD or ADR this serves}
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
---
```

**Required sections:** Status, Context, Decision, Alternatives Considered, Consequences (Positive, Negative, Neutral), References.

### CL — Changelog Entry (Ship)

| Field | Value |
|---|---|
| **Directory** | `docs/changelog/entries/` |
| **Filename** | `CL-{NNNN}-{slug}.md` |
| **Required frontmatter** | id, title, type (`changelog`), status, owner, domain, lifecycle, risk_profile, schema_version, relates_to, date, author, breaking_change |

**Frontmatter template:** See PROMPT-0006, Phase 1.

**Required sections:** What Changed, Why, Migration.

## Step-by-Step Implementation

### Phase 1: Determine Number

1. Find the next available number for the document type:

   ```bash
   # For EC:
   ls docs/extend-capabilities/ | grep -oP 'EC-\K\d+' | sort -n | tail -1

   # For PRD:
   ls docs/20-contracts/prds/ | grep -oP 'PRD-\K\d+' | sort -n | tail -1

   # For ADR:
   ls docs/adrs/ | grep -oP 'ADR-\K\d+' | sort -n | tail -1

   # For CL:
   ls docs/changelog/entries/ | grep -oP 'CL-\K\d+' | sort -n | tail -1
   ```

2. Increment by 1. If the highest is `0196`, the next is `0197`.

### Phase 2: Create Document

1. Create the file at the correct path using the appropriate frontmatter template above.
2. Fill in all required sections for the document type.
3. Set `relates_to` to link back through the lifecycle chain:
   - CL → PRD + relevant ADRs
   - ADR → PRD it serves
   - PRD → EC (if one exists)
   - EC → related ADRs/PRDs/GOVs

### Phase 3: Cross-Reference

1. If creating an ADR, the index at `docs/adrs/01_adr_index.md` is auto-generated by a pre-commit hook — no manual update needed.
2. If the new document supersedes an old one:
   - Add `supersedes: [OLD-ID]` to the new doc.
   - Add `superseded_by: [NEW-ID]` to the old doc.
   - Update the old doc's status to `Superseded` or `deferred`.

### Phase 4: Validate

1. Run pre-commit to validate metadata and regenerate indexes:

   ```bash
   pre-commit run --all-files
   ```

2. If hooks modify files, stage the changes:

   ```bash
   git add .
   ```

## Verification Checklist

- [ ] Document is in the correct directory for its type.
- [ ] Filename follows the `{TYPE}-{NNNN}-{slug}.md` convention.
- [ ] Number does not duplicate an existing document.
- [ ] All required frontmatter fields are present and valid.
- [ ] `relates_to` links exist and reference real documents.
- [ ] Required sections for the document type are filled in.
- [ ] `pre-commit run --all-files` passes.

## Integration Verification

- [ ] If ADR: appears in the auto-generated ADR index after pre-commit runs.
- [ ] If CL: `relates_to` references the PRD/ADR being shipped.
- [ ] If PRD: references originating EC (if one exists).
- [ ] Cross-references are bidirectional (new doc links to related, related links back).

## Do NOT

- Reuse a number that's already taken.
- Use the wrong frontmatter schema for the document type (e.g., `type: adr` on an EC).
- Manually edit `docs/adrs/01_adr_index.md` — the pre-commit hook regenerates it.
- Create a PRD for an idea you're still contemplating — use an EC instead.
- Skip the `relates_to` field — it's how the knowledge graph connects documents.
- Create documents without running `pre-commit run --all-files` afterward.

## Output Expected

1. Document path and filename.
2. Document type and number.
3. `relates_to` links created.
4. Pre-commit validation result.

## Rollback Plan

- Delete the new document: `git rm {path}`.
- If cross-references were updated on related docs: revert those changes.
- Run `pre-commit run --all-files` to regenerate indexes.

## References

- docs/governance/policies/GOV-0022-idea-to-initiative-lifecycle.md — Lifecycle policy
- docs/adrs/ADR-0197-agent-workflow-prompt-codification.md — Decision to codify this workflow
- PROMPT-0006 — PR creation workflow (includes CL frontmatter)
- session_capture/session_capture_template.md — Session capture format
