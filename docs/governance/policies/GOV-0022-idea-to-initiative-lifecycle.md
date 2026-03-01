---
id: GOV-0022-idea-to-initiative-lifecycle
title: Idea-to-Initiative Lifecycle
type: governance
owner: platform-team
status: active
domain: platform-core
applies_to:
  - platform-core
  - ai-systems
  - infrastructure
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - GOV-0017-tdd-and-determinism
  - GOV-0021-prompt-and-context-engineering
  - ADR-0192-multi-agent-coordination-protocol
  - ADR-0193-native-issue-tracking-pipeline
supersedes: []
superseded_by: []
tags:
  - governance
  - process
  - lifecycle
inheritance: {}
supported_until: 2028-01-01
effective_date: 2026-02-14
review_date: 2026-08-14
---

# GOV-0022: Idea-to-Initiative Lifecycle

## Purpose

Standardize how ideas progress from concept to shipped code. This is not a gate — nothing here blocks work. It describes the natural flow so that new team members (human or agent) know which document type to reach for at each stage.

## The Lifecycle

```
EC (explore) ──→ PRD (commit) ──→ ADR (decide) ──→ CL (ship)
   optional          required        as-needed        required
```

| Stage | Document | When to Use | Who Creates |
|-------|----------|-------------|-------------|
| **Explore** | EC-NNNN | You have an idea worth capturing but aren't ready to build it. Trade-offs are unclear, alternatives exist, or timing is uncertain. | Anyone |
| **Commit** | PRD-NNNN | You're building it. Scope, phases, and acceptance criteria are defined. References the originating EC if one exists. | Human or agent (human approves) |
| **Decide** | ADR-NNNN | A technical decision needs recording during implementation. References the PRD it serves. | Anyone during implementation |
| **Ship** | CL-NNNN | Code is merged. The changelog records what changed, why, and what PRD/ADR it relates to. | Agent (automated) |

## Stage Details

### EC — Extend Capability (Explore)

- **Path:** `docs/extend-capabilities/EC-NNNN-<slug>.md`
- **Status values:** `proposed`, `accepted`, `deferred`, `rejected`
- **Purpose:** Capture the idea, weigh trade-offs, list alternatives. No commitment to build.
- **Graduation:** When scope solidifies and you're ready to commit resources, create a PRD that references the EC. Update the EC status to `accepted`.
- **Parking:** If the idea isn't right for now, set status to `deferred` with a reason. It stays discoverable.

### PRD — Product Requirements Document (Commit)

- **Path:** `docs/20-contracts/prds/PRD-NNNN-<slug>.md`
- **Required fields:** Scope, phases, acceptance criteria, relates_to (EC if applicable)
- **Purpose:** Define what to build, in what order, and how to verify it's done.
- **Rule:** A PRD means you're building it. Don't create PRDs for ideas you're still contemplating — use an EC.

### ADR — Architecture Decision Record (Decide)

- **Path:** `docs/adrs/ADR-NNNN-<slug>.md`
- **Purpose:** Record a specific technical decision made during implementation. Context, options considered, decision, consequences.
- **When:** You chose technology X over Y. You adopted pattern A instead of B. You structured the data this way for these reasons.
- **Not every PRD needs ADRs.** Simple features with obvious implementation paths don't require architectural decisions to be recorded.

### CL — Changelog Entry (Ship)

- **Path:** `docs/changelog/entries/CL-NNNN-<slug>.md`
- **Purpose:** Record what shipped, why it changed, and how to migrate (if applicable).
- **Required:** Every PR that ships code must have a CL entry (unless labeled `changelog-exempt`).
- **Links back:** Every CL references its PRD and any relevant ADRs.

## Flow Examples

### Full lifecycle (complex feature)

```
EC-0019 (agent governance framework)
  └─→ PRD-0013 (governance portal)
        ├─→ ADR-0192 (multi-agent coordination protocol)
        └─→ CL-0212 (governance portal phase 1+2)
```

### Skip EC (clear requirements from the start)

```
PRD-0012 (platform health dashboard)
  ├─→ ADR-0191 (namespace isolation strategy)
  └─→ CL-0211 (dashboard + test namespace parity)
```

### Idea parked (not ready)

```
EC-0021 (semantic agent CLI) ──→ status: proposed
  └─→ (future: PRD-0014 when patterns stabilize)
```

## What This Policy Does NOT Do

- **No approval gates** — ECs don't need sign-off to exist. PRDs need human approval to start work (per CLAUDE.md).
- **No mandatory templates** — Each document type has its own frontmatter schema. Follow it. Beyond that, write what's useful.
- **No sequential enforcement** — You can create an ADR without a PRD if you're recording a standalone decision. You can skip EC entirely if requirements are clear. The lifecycle is a default path, not a mandatory sequence.
- **No review committees** — The existing PR process is the review mechanism.

## For Agents

When you're unsure which document to create:

1. **"Should we build X?"** → EC (you're exploring)
2. **"We're building X, here's the plan"** → PRD (you're committing)
3. **"We chose Y because Z"** → ADR (you're deciding)
4. **"X is shipped"** → CL (you're recording)

If an idea comes up mid-implementation that's unrelated to the current PRD, capture it as an EC rather than scope-creeping the PRD.
