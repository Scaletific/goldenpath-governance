---
id: ADR-0197
title: Agent Workflow Prompt Codification
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - PROMPT-0002
  - PROMPT-0003
  - PROMPT-0004
  - PROMPT-0005
  - ADR-0192-multi-agent-coordination-protocol
  - ADR-0193-native-issue-tracking-pipeline
  - GOV-0017-tdd-and-determinism
  - GOV-0022-idea-to-initiative-lifecycle
  - EC-0021-semantic-agent-cli
supersedes: []
superseded_by: []
tags:
  - ai
  - agents
  - prompts
  - developer-experience
  - governance
inheritance: {}
supported_until: 2028-01-01
---

# ADR-0197: Agent Workflow Prompt Codification

## Status

Accepted

## Context

AI agents working on the GoldenPath IDP repeatedly execute the same workflow patterns across sessions. Each session rediscovers conventions — PR template formatting, valid label names, conflict resolution strategies, session documentation rules, document frontmatter schemas — burning tokens, introducing errors, and slowing onboarding.

Analysis of 49 session captures and 5 existing prompt templates revealed 6 high-frequency workflow categories that lack codified prompts. The existing prompt library (PROMPT-0001 through PROMPT-0005) covers TDD enforcement, pre-commit checks, recursive CI compliance, and hotfix policy, but leaves significant gaps in day-to-day operational workflows.

### Observed Friction (from session capture analysis)

| Workflow | Sessions Affected | Avg Time Lost | Common Errors |
|----------|-------------------|---------------|---------------|
| PR creation with template compliance | 40+ PRs | 5-15 min/PR | Wrong labels, missing YAML header, invalid Change Type |
| Branch sync and conflict resolution | 8+ sessions | 15-30 min/sync | Wrong merge strategy for append-only files |
| Document scaffolding (EC/PRD/ADR/CL) | 20+ docs created | 5-10 min/doc | Wrong frontmatter schema, incorrect numbering |
| Session documentation | Every session | 5 min/session | Missing updates, wrong format, most common CI failure |
| Multi-agent coordination | 3+ sessions | 30+ min/launch | Re-planned from scratch each time |
| Script certification | 2 campaigns | 60+ min/campaign | Test naming mismatches, maturity promotion errors |

### Existing Prompt Coverage

| ID | Covers | Gap |
|---|---|---|
| PROMPT-0001 | Backstage repo restructuring | One-time task (complete) |
| PROMPT-0002 | Pre-commit hooks reference | Reference doc, not a workflow |
| PROMPT-0003 | Recursive CI failure fix loop | Fixes failures but doesn't prevent them |
| PROMPT-0004 | Hotfix permanent fix policy | Hotfixes only |
| PROMPT-0005 | TDD governance enforcement | Code changes only |

The gap: no prompts cover the operational workflows that agents execute most frequently — creating PRs, syncing branches, scaffolding documents, writing session docs, coordinating multi-agent work, or running certification campaigns.

## Decision

Codify 6 new prompt templates (PROMPT-0006 through PROMPT-0011) covering the highest-frequency agent workflow gaps. Each prompt follows the existing PROMPT-0000 skeleton format and encodes platform conventions, valid values, and governance rules so agents execute correctly on the first attempt.

### PROMPT-0006: PR Creation Workflow

**Problem:** Every PR creation requires agents to discover the PR template, valid Change Type options, label names, and YAML frontmatter format. Errors observed in 30%+ of PR creations — wrong labels (`docs-only` vs `docs`), missing template header, invented checkbox options (`Maintenance / Sync` is not valid).

**What it codifies:**
- Exact PR body template with YAML frontmatter (verbatim from `.github/pull_request_template.md`)
- Valid Change Type options: `Feature`, `Bug fix`, `Infra change`, `Governance / Policy`
- Valid labels and when to use them: `changelog-exempt`, `docs-only`, `typo-fix`, `hotfix`
- Branch-to-base mapping: feature/\* → development, hotfix/\* → main
- Changelog entry creation with correct frontmatter schema
- VQ class selection for PR notes

**ROI:** Eliminates the #1 source of agent errors. Every PR benefits.

### PROMPT-0007: Branch Sync and Conflict Resolution

**Problem:** Syncing `main ↔ development` or merging `development` into feature branches causes repeated friction. Agents don't know which merge strategy to use for append-only files (`agent_session_summary.md`, `01_adr_index.md`, `value_ledger.json`). PR #372 took 30+ minutes to resolve because the agent didn't know to take development's version for formatting conflicts.

**What it codifies:**
- Sync direction rules (main → development, development → feature/*)
- Conflict resolution strategies by file type:
  - Append-only files: take target branch version (newer appends win)
  - Auto-generated indexes: regenerate after merge
  - Config files (CLAUDE.md, Makefile): manual merge, keep both additions
- Protected branch workflow (can't push directly to development, must PR)
- Post-merge validation (pre-commit, index regeneration)

**ROI:** Reduces 30-minute sync sessions to 5-minute scripted workflows.

### PROMPT-0008: Document Scaffolding (EC/PRD/ADR/CL)

**Problem:** Creating new governance documents requires agents to discover the next available number, correct directory path, frontmatter schema, and mandatory fields. GOV-0022 describes *when* to use each type but not *how* to create them correctly. Agents grep for the highest number, copy-paste frontmatter from existing files, and frequently miss required fields.

**What it codifies:**
- Directory paths for each document type (EC, PRD, ADR, CL)
- Frontmatter schema per type with required vs optional fields
- Number allocation: grep for highest existing, increment by 1
- Filename convention: `{TYPE}-{NNNN}-{slug}.md`
- `relates_to` linking rules (EC → PRD → ADR → CL chain)
- Index update requirements (ADR index is auto-generated by pre-commit hook)
- Status values per type

**ROI:** Prevents frontmatter errors on every new document. Especially valuable for agents creating ADRs mid-implementation.

### PROMPT-0009: Multi-Agent Coordination Launch

**Problem:** ADR-0192 defines the coordination protocol but agents re-plan the entire coordination structure from scratch each session. The plan file for the Feb 14 multi-branch merge was 200+ lines of coordination logic that could have been templated.

**What it codifies:**
- Agent naming convention: `W{n}-{scope}` for workers, `SW-{date}` for session writer
- Agent report format (mandatory fields: agent_id, start_time, end_time, status, branch, pr_number, files_touched, decisions, issues)
- Report directory: `.claude/agent-reports/{agent-id}-report.md`
- Session writer rules: runs last, only writer touches `session_capture/` and `session_summary/`
- Serialization rules: branch prep sequential (shared working dir), CI monitoring parallel
- Activation criteria: 2+ agents, 2+ repos, or explicit "multi-agent mode"

**ROI:** Turns 30-minute coordination planning into a fill-in-the-blanks template.

### PROMPT-0010: Session Documentation

**Problem:** Session documentation is the most common CI failure reason. PRs touching critical paths (`docs/adrs/`, `scripts/`, `docs/governance/`) require both `session_capture/*.md` and `session_summary/agent_session_summary.md` updates. Agents forget when to update, what format to use, and which paths trigger the requirement.

**What it codifies:**
- Critical paths that trigger session log requirement
- Session capture format (template reference + required sections)
- When to append updates (after each task completion, not batched)
- `agent_session_summary.md` entry format
- Append-only rule (never delete content from session captures)
- Naming convention: `YYYY-MM-DD-session-capture-{topic}.md`

**ROI:** Eliminates the most frequent CI gate failure. Every session benefits.

### PROMPT-0011: Script Certification Workflow

**Problem:** Script certification campaigns (62 scripts, 49 test files across 5 waves) follow a repeatable pattern but are planned from scratch. Test file naming must match `<dir>/tests/test_<name>.py` for source file `<dir>/<name>.py` — mismatches silently fail the TDD gate.

**What it codifies:**
- Test file naming convention with source-to-test mapping
- Maturity level definitions: M1 (uncertified) → M2 (partial) → M3 (certified)
- Certification campaign workflow: identify → write tests → run → promote → regenerate matrix
- Wave-based execution for large campaigns
- `make certify-scripts` and matrix regeneration commands
- Common patterns: BATS for shell scripts, pytest for Python scripts
- conftest.py patterns for optional dependency handling

**ROI:** Enables repeatable certification campaigns as new scripts are added.

## Alternatives Considered

| Alternative | Pros | Cons |
|---|---|---|
| **Codify as prompt templates** (chosen) | Fits existing pattern, RAG-indexable, human-reviewable, zero new tooling | Templates can drift from reality if not maintained |
| **Build semantic CLI (EC-0021)** | Eliminates rediscovery entirely, machine-executable | Premature — patterns still stabilizing, significant build effort |
| **Add to CLAUDE.md** | Zero new files, always loaded | CLAUDE.md already 100+ lines, adding 6 workflows would make it unmanageable |
| **Inline in governance docs** | Co-located with policies | Mixes reference docs with execution prompts, agents can't find them |
| **Do nothing** | Zero effort | Agents keep rediscovering patterns every session, 30%+ error rate persists |

## Consequences

### Positive

- Agent error rate on PR creation, branch sync, and document scaffolding should drop from ~30% to near zero
- New agents (human or AI) can onboard by reading the prompt library instead of learning from mistakes
- Session documentation CI failures should be eliminated
- Multi-agent coordination setup drops from 30+ minutes of planning to template fill-in
- Prompt templates are RAG-indexed, so agents can discover them via semantic search

### Negative

- 6 new files to maintain — templates can drift if conventions change
- Risk of over-specification — prompts may become rigid if platform evolves

### Neutral

- These prompts may graduate into EC-0021's semantic CLI if the patterns prove stable enough to codify as executable tooling
- The prompt library becomes the "source of truth" for agent workflows until/unless a CLI replaces it

## References

- [PROMPT-0000](../../prompt-templates/PROMPT-0000-template.md) — Prompt skeleton format
- [PROMPT-0002](../../prompt-templates/PROMPT-0002-pre-commit-and-pre-merge-checks.md) — Pre-commit reference
- [PROMPT-0003](../../prompt-templates/PROMPT-0003-recursive-pr-gate-compliance.md) — Recursive CI fix loop
- [ADR-0192](ADR-0192-multi-agent-coordination-protocol.md) — Multi-agent coordination protocol
- [ADR-0193](ADR-0193-native-issue-tracking-pipeline.md) — Issue tracking pipeline
- [GOV-0022](../10-governance/policies/GOV-0022-idea-to-initiative-lifecycle.md) — Idea-to-initiative lifecycle
- [EC-0021](../extend-capabilities/EC-0021-semantic-agent-cli.md) — Semantic agent CLI concept
