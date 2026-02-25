---
id: GOV-0055-prompt-proposal-stack
title: Prompt Template Proposal Stack
type: governance
relates_to:
  - PROMPT_INDEX
  - ADR-0192-multi-agent-coordination-protocol
category: automation
aliases:
  - PROMPT_PROPOSAL_STACK
---

# Prompt Template Proposal Stack

A living registry of repeated workflow patterns observed across sessions that are candidates for codification as PROMPT-XXXX templates.

## How to Use

- **Agents**: When Session Writer detects a repeated pattern, append a row below.
- **Humans**: Review proposals periodically, promote to PROMPT-XXXX or dismiss.

## Status Values

- `proposed` — under consideration (default for new entries)
- `codified` — became a PROMPT-XXXX template (reference in notes)
- `dismissed` — reviewed and decided not worth codifying

## Proposal Stack

| ID | Pattern | Occurrences | First Seen | Last Seen | Sessions | Status |
|---|---|---|---|---|---|---|
| PP-001 | Multi-repo sync after ADR change | 4 | 2026-01-15 | 2026-02-10 | SC-0115, SC-0122, SC-0128, SC-0134 | proposed |
| PP-002 | Governance portal collector + test + endpoint | 3 | 2026-02-08 | 2026-02-14 | SC-0130, SC-0133, SC-0136 | proposed |
| PP-003 | Test execution workflow prompt (smoke/regression/integration) | 1 | 2026-02-14 | 2026-02-14 | SC-0137 | codified |

## Rationale

### PP-001

When an ADR changes, downstream documents across multiple repositories need synchronized updates (backstage catalog, helm values, deployment configs). Without a codified prompt, agents repeat the same multi-repo coordination steps each time -- identifying affected repos, checking out branches, applying changes, running tests, and creating PRs. This pattern has been observed in 4 sessions over 4 weeks.

**Advantages:** Reduces multi-repo sync from ~20 minutes to ~5 minutes per session. Ensures consistency across repos by following a deterministic checklist. Prevents missed updates that create drift between ADR intent and deployed state.

### PP-002

Each new governance portal feature follows an identical scaffolding pattern: create a collector that parses a markdown file, write TDD tests, add a FastAPI endpoint with cache, create a frontend page component, wire up routing and sidebar navigation. This exact sequence has been repeated 3 times (sessions, ADR index, proposal stack) with the same architectural decisions each time.

**Advantages:** Standardizes portal feature development into a repeatable workflow. Reduces scaffolding decisions and onboarding time for new contributors. Ensures consistency in cache strategy, error handling, and response envelope format.

### PP-003

Test execution across the platform follows a three-tier pattern (smoke, regression, integration) but there was no codified prompt defining what each tier means or how to execute them. Agents were improvising test strategies each session. This was codified as PROMPT-0012 during the autopoietic capabilities work.

**Advantages:** Eliminated per-session test strategy improvisation. Now referenced by CLAUDE.md dispatch table for consistent test execution across all agent sessions.
