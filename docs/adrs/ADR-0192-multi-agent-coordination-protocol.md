---
id: ADR-0192-multi-agent-coordination-protocol
title: 'ADR-0192: Multi-Agent Coordination Protocol'
type: adr
status: proposed
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
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0079-platform-ai-agent-governance
  - ADR-0164-agent-trust-and-identity
supersedes: []
superseded_by: []
tags:
  - ai-governance
  - multi-agent
  - coordination
  - session-capture
inheritance: {}
supported_until: 2028-02-01
version: '1.1'
breaking_change: false
---

# ADR-0192: Multi-Agent Coordination Protocol

- **Status:** Proposed
- **Date:** 2026-02-11
- **Owners:** platform-team
- **Domain:** Platform Core
- **Decision type:** Governance | AI Agent Operations

---

## Context

As the GoldenPath IDP grows in scope, work increasingly spans multiple
repositories and task domains in a single session. Running multiple AI agents
in parallel (the "Agent Pool" pattern) significantly reduces wall-clock time
for large work items, but introduces coordination challenges:

1. **Session documentation conflicts** — Multiple agents writing to
   `session_capture/` simultaneously creates merge conflicts and violates the
   append-only invariant enforced by `session-capture-guard.yml`.
2. **Unstructured handoffs** — Without a defined report format, the
   orchestrator cannot reliably synthesize work from multiple agents.
3. **Identity ambiguity** — When multiple agents produce commits, it is
   unclear which agent made which change.
4. **Scope overlap** — Without explicit scope boundaries, agents may duplicate
   work or make conflicting changes to the same files.

The existing agent governance framework (ADR-0079, ADR-0164, 26_AI_AGENT_PROTOCOLS)
defines rules for single-agent operation. This ADR extends it to multi-agent
scenarios.

## Decision

We adopt the **Agent Pool with Single Writer** pattern for multi-agent
coordination:

### Agent Naming Convention

- **Worker agents:** `W{n}-{task-verb-noun}` — names MUST be
  self-documenting (e.g., `W1-governance-audit`, `W2-portal-backend`,
  `W3-dashboard-frontend`). Avoid opaque abbreviations like `W-A` or
  `W-B`.
- **Session Writer:** `SW-{date}-{topic}` (e.g.,
  `SW-2026-02-13-portal-build`)
- Agent IDs appear in commit messages: `[agent:W1-governance-audit]`

### Single Writer Rule

Only the Session Writer (SW) agent may write to:
- `session_capture/**/*.md`
- `session_summary/**/*.md`

Worker agents MUST NOT write to these paths. This preserves the append-only
invariant and prevents merge conflicts. The existing `session-capture-guard.yml`
and `session-log-required.yml` workflows validate SW output.

### Agent Reports

Every worker agent writes a structured report to
`agent-reports/{agent-id}-report.md` before completing its work. Reports are
the single communication channel between workers and the Session Writer.

> **Note:** Reports were previously stored in `.claude/agent-reports/`. The
> directory has been moved to `agent-reports/` (top-level) to be
> tool-agnostic — any AI tool or human can produce reports, not just Claude.

#### Report Template

```markdown
# Agent Report: {agent-id}

## Metadata
- Agent: {agent-id}
- Platform: claude-code | codex | copilot | human
- Mission: {topic}-{YYYY-MM-DD}
- Orchestrator: {git username}
- Objective: "One-line description of the mission goal"
- Scope: {repository} -- {description of scope}
- Branch: {branch-name}
- Started: {ISO8601 timestamp}       ← record as FIRST action
- Completed: {ISO8601 timestamp}     ← record as LAST action
- Status: complete | partial | blocked

## Changes Made
| File | Action | What and Why |
|---|---|---|
| path/to/file | created/modified/deleted | description |

## Decisions Made
| Decision | Choice | Rationale |
|---|---|---|
| description | what was chosen | why |

## Issues Found
| ID | Severity | Domain | Component | Description | Files | Resolution |
|---|---|---|---|---|---|---|
| {agent-id}-{seq} | critical/high/medium/low | domain | component | description | files | resolution |

## Validation
- Ran: {command} (result: pass/fail)

## Outstanding / Handoff
- {items for next agent or human}
```

### Execution Flow

1. **Orchestrator** declares multi-agent mode, assigns scope boundaries, and
   launches worker agents in parallel.
2. **Worker agents** (W1, W2, ..., Wn) execute their scoped work
   independently. Each writes only to files within their declared scope.
3. **Worker agents** write their report to `agent-reports/` and signal
   completion.
4. **Orchestrator** verifies all workers have completed (or handles partial
   completion).
5. **Session Writer** (SW) reads all agent reports and produces:
   - The official session capture entry in `session_capture/`
   - The session summary entry in `session_summary/`
6. **Orchestrator** commits all changes (or delegates commit to SW).

### Time Tracking

Agent reports MUST include valid ISO 8601 timestamps in the `Started` and
`Completed` metadata fields:

- **Started** — recorded as the agent's first action upon starting work.
- **Completed** — recorded as the agent's last action before signaling done.
- **Format:** `YYYY-MM-DDTHH:MM:SSZ` (e.g., `2026-02-14T10:30:00Z`).
- **Placeholders rejected** — CI hard-blocks reports with `{ISO8601}` or
  missing timestamps.

The Governance Portal (PRD-0013) computes:

- **Per-agent duration** — `Completed - Started` in minutes.
- **Mission wall-clock duration** — earliest agent start to latest agent
  completion.
- **Total agent minutes** — sum of all individual agent durations (captures
  parallel effort).
- **Stats** — `total_agent_hours` and `avg_mission_minutes` across all
  missions.

### Scope Boundaries

Each worker agent is assigned an explicit scope at launch. Scopes are
non-overlapping by default:

- **File-based scope:** Agent W1 owns `envs/**`, Agent W2 owns `backstage-helm/**`
- **Task-based scope:** Agent W1 handles "Terraform changes", Agent W2
  handles "documentation updates"
- **Conflict resolution:** If two agents must modify the same file, the
  orchestrator designates one as primary and the other defers.

### Activation Criteria

This protocol activates when any of:
- 2+ Task agents are launched in parallel
- Work spans 2+ repositories
- Orchestrator explicitly declares "multi-agent mode"

For single-agent work, standard session capture rules from
26_AI_AGENT_PROTOCOLS apply unchanged.

## Scope

**Applies to:**
- All AI agents operating in `goldenpath-infra` and related repositories
- Orchestrator tooling that launches parallel agents
- Session capture and summary workflows

**Does not apply to:**
- Human-only work sessions
- Single-agent sessions (existing protocols apply)

## Consequences

### Positive

- **No session capture conflicts** — Single Writer eliminates merge conflicts
  in append-only files.
- **Structured handoffs** — Agent reports provide a consistent format for
  synthesizing multi-agent work.
- **Traceability** — Agent IDs in commits and reports make it clear which
  agent made which change.
- **Parallelism** — Multiple agents can work simultaneously without
  coordination overhead beyond scope assignment.

### Tradeoffs / Risks

- **Sequential bottleneck** — Session Writer must wait for all workers to
  complete before producing session documentation.
- **Report overhead** — Each worker spends time writing a structured report.
  Acceptable cost for coordination benefits.
- **Scope rigidity** — Strict scope boundaries may require orchestrator
  intervention when unexpected cross-cutting changes are needed.

### Operational Impact

- Reports are stored in `agent-reports/` (top-level, tool-agnostic).
- Update orchestrator tooling to assign agent IDs, mission IDs, and scopes.
- Session Writer agent needs read access to `agent-reports/`.
- Pre-commit hook enforces that new agent reports have matching session
  capture entries (see `scripts/check_session_writer.sh`).

## Alternatives Considered

1. **Free-for-all writes** — All agents write to session capture directly.
   Rejected: guaranteed merge conflicts and append-only violations.

2. **Lock-based coordination** — Agents acquire locks before writing shared
   files. Rejected: adds complexity, risk of deadlocks, and agents cannot
   easily implement distributed locks.

3. **Message queue** — Agents communicate via a message queue (e.g., Redis).
   Rejected: over-engineered for current needs; file-based reports are
   simpler and auditable.

4. **Single agent only** — Never run multiple agents in parallel. Rejected:
   loses the significant time savings of parallel execution.

## Follow-ups

- Implement orchestrator tooling that assigns agent IDs and scope boundaries.
- Add a validation step that checks all worker reports exist before SW runs.
- Consider adding a `--multi-agent` flag to session capture workflows that
  relaxes timing constraints for SW.

## Notes

This protocol is intentionally lightweight. It uses files (agent reports) as
the coordination mechanism rather than introducing external infrastructure.
The pattern is inspired by the MapReduce model: workers produce intermediate
results (reports), and the Session Writer reduces them into final output
(session capture).

Existing enforcement mechanisms (`session-capture-guard.yml`,
`session-log-required.yml`) continue to validate the final session capture
output produced by SW. No changes to these workflows are required.
