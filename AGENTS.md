# Agent Instructions

Universal rules for all AI agents operating in this repository, regardless
of tool (Claude, Codex, Copilot, or other). Tool-specific configuration
belongs in tool-specific files (e.g., `CLAUDE.md` for Claude Code).

## Absolute Rules (Never Violate)

1. **No `terraform apply` without explicit human authorization**
2. **No merging PRs to `main`** — agents create PRs, humans merge
3. **No deployments without explicit human authorization**
4. **TDD is mandatory** — tests must be written and fail before implementation
5. **Hotfixes must be permanent fixes** — no "fix properly later" allowed
6. **No skipping pre-commit hooks** (e.g., `--no-verify`)
7. **No modifying governance policies without human approval**

## Recursive Self-Improvement

This platform practices explicit recursive self-improvement. Agents observe
their own operational friction — recurring issues, repeated decisions, file
hotspots, incomplete follow-ups — and surface detected patterns as draft
improvement proposals via the Governance Portal's pattern detector. The cycle
is: **Work → Observe → Detect → Propose → Improve → Work better**. When you
notice friction during a session, log it in structured issue tables so the
detector can aggregate signals across sessions and generate actionable
proposals.

## Before Any Code Change

1. Read the relevant governance doc (see Quick Reference below)
2. Identify test tier: unit (Tier 1), golden (Tier 2), or integration (Tier 3)
3. Write failing tests first
4. Implement minimal fix
5. Run `make quality-gate` before declaring done

## Quick Reference

| Topic | Document |
|-------|----------|
| TDD Policy | docs/governance/policies/GOV-0017-tdd-and-determinism.md |
| Testing Stack | docs/governance/policies/GOV-0016-testing-stack-matrix.md |
| PR Gates | docs/onboarding/24_PR_GATES.md |
| Agent Protocols | docs/onboarding/26_AI_AGENT_PROTOCOLS.md |
| ADR Index | docs/adrs/01_adr_index.md |
| Script Index | docs/50-scripts/01_script_index.md |
| Prompt Templates | prompt-templates/README.md |

## Workflow Templates

Standard workflows are codified in `prompt-templates/`. Before inventing a
new approach to PRs, session docs, multi-agent coordination, or script
certification, check if a PROMPT-XXXX template already covers it. See
`prompt-templates/README.md` for the full index.

## Branch Workflow

| Action | Allowed |
|--------|---------|
| Create PR to `development` | Yes |
| Merge PR to `development` | Yes (after CI green) |
| Create PR to `main` | Yes |
| Merge PR to `main` | **NO — Human only** |

## Session Documentation

For significant work, create session capture:

- Path: `session_capture/YYYY-MM-DD-session-capture-<topic>.md`
- Template: `session_capture/session_capture_template.md`
- Rule: Append-only (never delete content)

### When to Update Session Capture

Append an update whenever:

1. **A task is completed** — feature implemented, bug fixed, refactor done
2. **A phase or milestone is reached** — e.g., "Phase 1 complete"
3. **A backlog item is done** — PR created, PR merged, CI fixed
4. **Definition of done is achieved** — tests pass, quality-gate green

Each update must include:

- What changed (files modified, lines added/removed)
- Why it changed (reference to PRD, task, or goal)
- Decisions made (choices between alternatives, with rationale)
- Outstanding items (what's left, what the next session should pick up)

Also append a corresponding entry to `session_summary/agent_session_summary.md`.

## Multi-Agent Coordination (ADR-0192)

When multiple agents work in parallel (multi-repo or multi-task):

### Rules

1. **Single Writer for session docs** — Only the Session Writer (SW) agent
   writes to `session_capture/` and `session_summary/`. Workers MUST NOT
   write to these paths.
2. **Agent reports are mandatory** — Every worker agent writes a structured
   report to `agent-reports/{agent-id}-report.md` before completing.
3. **Agent naming** — Use `W{n}-{task-verb-noun}` convention:
   - `W1-governance-audit` (not `W1-gov` or `W-A`)
   - `W2-portal-backend` (not `W-B`)
   - Session Writer: `SW-{date}-{topic}` (e.g., `SW-2026-02-13-portal`)
   - Include agent ID in commit messages: `[agent:W1-governance-audit]`
4. **Mission ID is required** — Every agent report MUST include a `Mission:`
   metadata field. The orchestrator assigns the mission ID at launch.
   Format: `{topic}-{YYYY-MM-DD}` (e.g., `governance-portal-2026-02-13`).
5. **Platform field is required** — Every agent report MUST include a
   `Platform:` metadata field identifying the producing tool
   (`claude-code`, `codex`, `copilot`, `human`).
6. **Session Writer runs last** — After all workers complete, the
   orchestrator MUST launch a Session Writer agent to consolidate reports.
7. **Report format** — See `agent-reports/README.md` for the mandatory
   template.

### Orchestrator Checklist (MANDATORY)

After all worker agents complete:

- [ ] Verify all worker reports exist in `agent-reports/`
- [ ] Launch Session Writer agent (SW-{date}-{topic})
- [ ] SW reads all reports and produces session capture + summary
- [ ] Verify `session_capture/` entry exists before committing

**Skipping the Session Writer step leaves orphaned agent reports.** The
pre-commit hook will block commits with orphaned reports, and CI will flag
them in PR comments.

### When This Activates

- 2+ agents launched in parallel
- Work spans 2+ repositories
- Orchestrator explicitly declares "multi-agent mode"

For single-agent work, standard session capture rules apply.

## Time Tracking

Every agent MUST record wall-clock timestamps in their agent report:

1. **Record `Started` immediately** — As your first action, write the current
   ISO 8601 timestamp to the `Started:` field in your agent report metadata.
2. **Record `Completed` at the end** — As your last action before signaling
   completion, write the current ISO 8601 timestamp to the `Completed:` field.
3. **Use real timestamps** — Never leave `{ISO8601}` placeholders. CI will
   reject reports with placeholder or missing timestamps.
4. **Format:** `YYYY-MM-DDTHH:MM:SSZ` (e.g., `2026-02-14T10:30:00Z`)

Duration is calculated automatically by the Governance Portal from these
timestamps. Mission-level timing is derived from the earliest agent start to
the latest agent completion.

## Issue Tracking (ADR-0193)

When you discover issues during work, log them in the structured format.

### Issue Table Format

| ID | Severity | Domain | Component | Description | Files | Resolution |
|---|---|---|---|---|---|---|
| {agent-id}-{seq} | critical/high/medium/low | domain | component | description | files | resolution |

### Severity SLA Rules (CI-enforced)

- **critical/high**: MUST be `fix-now` or `needs-human`
- **medium**: 30-day resolution window
- **low**: No SLA, tracked only

### Resolution Paths

- `fix-now` — resolve in this session
- `defer-to-roadmap` — medium/low only, creates GitHub Issue
- `needs-adr` — high only, requires architectural decision
- `needs-human` — any severity, escalates to human
- `blocked` — external dependency, not actionable

## Repository Structure

```
envs/                    # Environment-specific Terraform
modules/                 # Reusable Terraform modules
scripts/                 # Certified automation scripts
agent-reports/           # AI agent work reports (tool-agnostic)
governance-portal/       # Governance & Agent Activity Portal (PRD-0013)
platform-dashboard/      # Platform Health Dashboard (PRD-0012)
rag-web-ui/              # Governance RAG Web UI (PRD-0011)
docs/
  adrs/                  # Architecture Decision Records
  governance/         # Policies and governance docs
  20-contracts/          # PRDs, schemas, resource catalogs
  50-scripts/            # Script documentation
  70-operations/         # Runbooks and operational docs
  onboarding/         # Getting started guides
session_capture/         # Session documentation (append-only)
session_summary/         # Session summary index
.github/workflows/       # CI/CD pipelines
```

## Initiative Context

Before starting significant work, check
`docs/production-readiness-gates/INITIATIVES.md` for active initiatives.
Do NOT modify INITIATIVES.md — it is human-maintained.
