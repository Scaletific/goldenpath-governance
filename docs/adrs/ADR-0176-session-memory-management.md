---
id: ADR-0176
title: Session Memory Management for Human-Machine Collaboration
type: adr
domain: platform-core
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 4.0
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
  - GOV-0034-ai-agent-governance
  - 2026-01-21-route53-dns-terraform
  - ADR-0163
  - ADR-0167
  - CAPABILITY_LEDGER
  - CL-0163
  - CL-0164
  - FEATURES
  - PRODUCT_THESIS
  - ROADMAP
  - agent_session_summary
  - session_capture_template
supersedes: []
superseded_by: []
tags:
  - agents
  - collaboration
  - memory
  - governance
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-22
deciders:
  - platform-team
---

## Status

Accepted

## Context

This platform is designed to facilitate human-machine collaboration. AI agents
work alongside humans across sessions, but face a fundamental constraint:
context windows are finite while project knowledge accumulates indefinitely.

Without structured memory management:

1. **Context loss**: Each new session starts cold, losing prior learnings
2. **Repeated mistakes**: Issues diagnosed and fixed are rediscovered
3. **Decision amnesia**: Rationale for choices is lost, leading to churn
4. **Unbounded growth**: Append-only logs grow beyond usable size

We need a memory architecture that preserves institutional knowledge while
keeping files bounded for efficient agent context loading.

## Decision

Implement a three-tier session memory system:

### Tier 1: Session Capture (Working Memory)

- **Location**: `session_capture/YYYY-MM-DD-<topic>.md`
- **Purpose**: Active working memory during a session
- **Lifecycle**: One file per context-bounded effort
- **Structure**: Includes Issues Diagnosed/Fixed table, Design Decisions table
- **Template**: `session_capture/session_capture_template.md`

### Tier 2: Session Summary (Long-term Memory)

- **Location**: `session_summary/agent_session_summary.md`
- **Purpose**: Cross-session continuity and pattern recognition
- **Lifecycle**: Append-only, entries accumulate over time
- **Structure**: Timestamped entries with checkpoints, achievements, issues
- **Bounded by**: Archive mechanism (see Tier 3)

### Tier 3: Archive (Historical Memory)

- **Location**: `session_summary/archive/YYYY-MM.md`
- **Purpose**: Searchable history for institutional knowledge
- **Lifecycle**: Entries older than 30 days archived by month
- **Trigger**: Auto-archive when main file exceeds 1000 lines

### Session Start Protocol

At session start, agents run:

```bash
make session-start
```

This command:

1. Checks if `agent_session_summary.md` exceeds 1000 lines
2. Archives entries older than 30 days to monthly files
3. Keeps the main file bounded for efficient context loading

### Key Structures for Context Recovery

Both session capture and session summary include:

| Structure | Purpose |
|-----------|---------|
| **Issues Diagnosed and Fixed** | Searchable troubleshooting history (Issue \| Root Cause \| Fix) |
| **Design Decisions Made** | Preserved rationale (Decision \| Choice \| Rationale) |
| **Outstanding** | Quick scan of pending work |
| **Validation** | Evidence of work done |

## Scope

Applies to all AI agents operating in this repository. Humans may use the same
structures but are not required to follow the protocol.

## Consequences

### Positive

- **Context recovery**: Agents resume work with full session history
- **Pattern recognition**: Issues table enables learning from past fixes
- **Decision preservation**: Rationale survives across sessions and agents
- **Bounded files**: Archive keeps main file under context window limits
- **Searchable history**: `grep` across archives for institutional knowledge

### Tradeoffs / Risks

- Maintenance overhead for session documentation
- Archive script adds complexity
- Discipline required to populate structured tables

### Operational Impact

- Agents must run `make session-start` at session beginning
- Session captures should include Issues and Decisions tables
- Archive runs automatically when thresholds exceeded

## Alternatives Considered

### 1. Single Append-Only Log

**Rejected**: Unbounded growth makes files unusable for context loading.
At 40k+ tokens, the file exceeds model context limits.

### 2. Time-Based Sessions Only

**Rejected**: Sessions are often topic-based, not time-based. Calendar
boundaries don't match mental models of work units.

### 3. No Structured Tables

**Rejected**: Prose is harder to scan and search. The Issue/Root Cause/Fix
table enables quick troubleshooting lookup.

### 4. Database-Backed Memory

**Rejected**: Adds infrastructure dependency. Git-based files are portable,
versionable, and work offline.

## Implementation

| Artifact | Purpose |
|----------|---------|
| `scripts/archive_sessions.py` | Auto-archive when threshold exceeded |
| `Makefile` targets | `session-start`, `session-archive-dry-run`, `session-archive-force` |
| `session_capture/session_capture_template.md` | Updated with Issues/Decisions tables |
| `docs/governance/GOV-0034-ai-agent-governance.md` | Session start protocol documented |

## Follow-ups

1. Monitor archive frequency and adjust thresholds if needed
2. Consider adding search tooling over archived sessions
3. Evaluate whether to extract common issues into a knowledge base
