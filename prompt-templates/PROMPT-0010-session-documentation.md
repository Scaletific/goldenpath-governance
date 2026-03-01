---
id: PROMPT-0010
title: Session Documentation
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-infra
relates_to:
  - ADR-0167
  - ADR-0192
  - ADR-0197
  - PROMPT-0009
created: 2026-02-14
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are a platform engineer maintaining session documentation to satisfy CI gates and preserve decision context.

## Context

PRs touching critical paths require both a `session_capture/*.md` file AND an update to `session_summary/agent_session_summary.md`. This is enforced by the `require-session-logs` CI check. Missing session documentation is the most common CI gate failure.

This prompt encodes: which paths trigger the requirement, the correct file formats, when to update, and the append-only rules.

## Your Task

Create or update session documentation that satisfies the `require-session-logs` CI gate.

## Preconditions

- [ ] You are working on a PR that touches critical paths (see list below).
- [ ] You know the session topic and scope.

## Critical Paths That Trigger Session Log Requirement

Any PR modifying files in these directories requires session documentation:

| Path | Why |
|---|---|
| `docs/adrs/` | Architectural decisions need decision context |
| `scripts/` | Automation changes need rationale |
| `docs/governance/` | Policy changes need deliberation record |
| `docs/20-contracts/` | Contract changes need justification |
| `docs/extend-capabilities/` | Enhancement concepts need exploration record |
| `envs/` | Infrastructure changes need context |
| `modules/` | Terraform module changes need rationale |
| `.github/workflows/` | CI/CD changes need documentation |

## When to Update

Update session documentation:

- **After each task is completed** — not batched at the end
- **After a phase or milestone is reached** — e.g., "Phase 1 complete"
- **After a backlog item is done** — PR created, CI fixed
- **After definition of done is achieved** — tests pass, quality-gate green

**Rule:** Append-only. Never delete or edit prior entries in session captures.

## Step-by-Step Implementation

### Phase 1: Create Session Capture File

1. Check if a session capture already exists for today's work:

   ```bash
   ls session_capture/ | grep "$(date +%Y-%m-%d)"
   ```

2. If none exists, create a new file:

   **Filename:** `session_capture/YYYY-MM-DD-session-capture-{topic}.md`

   **Example:** `session_capture/2026-02-14-session-capture-prompt-codification.md`

3. Use the template from `session_capture/session_capture_template.md`:

   ```markdown
   ---
   id: {YYYY-MM-DD}-session-capture-{topic}
   title: 'Session Capture: {Topic}'
   type: documentation
   domain: platform-core
   owner: platform-team
   lifecycle: active
   status: active
   schema_version: 1
   risk_profile:
     production_impact: low
     security_risk: none
     coupling_risk: low
   reliability:
     rollback_strategy: git-revert
     observability_tier: bronze
     maturity: 1
   relates_to:
     - {related PRD/ADR}
   ---

   # Session Capture: {Topic}

   ## Session metadata

   **Agent:** {agent-name or human}
   **Date:** {YYYY-MM-DD}
   **Timestamp:** {YYYY-MM-DDTHH:MM:SSZ}
   **Branch:** {branch-name}

   ## Scope

   - {what this session covers}

   ## Work Summary

   - {completed items}

   ## Issues Diagnosed and Fixed

   | Issue | Root Cause | Fix |
   |-------|------------|-----|
   | {symptom} | {why} | {what was done} |

   ## Design Decisions Made

   | Decision | Choice | Rationale |
   |----------|--------|-----------|
   | {what} | {chosen} | {why} |

   ## Artifacts Touched (links)

   ### Modified
   - `{path}`

   ### Added
   - `{path}`

   ## Validation

   - `{command}` ({result})

   ## Current State / Follow-ups

   - {next steps}

   Signed: {agent-name} ({timestamp})
   ```

### Phase 2: Append Updates During Work

As you complete tasks, append updates to the session capture:

```markdown
---

## Updates (append as you go)

### Update - {YYYY-MM-DDTHH:MM:SSZ}

**What changed**
- {completed item}

**Artifacts touched**
- `{path}`

**Validation**
- {command + result}

**Next steps**
- {what's next}

**Outstanding**
- {remaining items}

Signed: {agent-name} ({timestamp})
```

### Phase 3: Update Agent Session Summary

Append an entry to `session_summary/agent_session_summary.md`:

```markdown
### {YYYY-MM-DD} — {Topic}

**Agent:** {agent-name}
**Branch:** {branch-name}
**Duration:** {approximate duration}
**PRs:** #{NNN}

**Summary:**
- {1-3 bullet points of what was accomplished}

**Documents created/modified:**
- `{path}`

**Follow-ups:**
- {next steps}
```

### Phase 4: Commit and Verify

1. Stage session documentation:

   ```bash
   git add session_capture/{filename}.md session_summary/agent_session_summary.md
   ```

2. Commit:

   ```bash
   git commit -m "docs: add session capture for {topic}"
   ```

3. Push and verify the `require-session-logs` check passes:

   ```bash
   git push
   gh pr checks {PR_NUMBER} --watch
   ```

## Verification Checklist

- [ ] Session capture file exists at `session_capture/YYYY-MM-DD-session-capture-{topic}.md`.
- [ ] Session capture has valid frontmatter with all required fields.
- [ ] `session_summary/agent_session_summary.md` has been updated with a new entry.
- [ ] Both files are committed and pushed.
- [ ] `require-session-logs` CI check passes.
- [ ] Updates are appended (no prior content deleted or modified).

## Integration Verification

- [ ] Session capture `relates_to` references match the PRD/ADR being worked on.
- [ ] Agent session summary entry matches the session capture content.
- [ ] If multi-agent mode: only the Session Writer (SW) updated these files, not workers.

## Do NOT

- Delete or edit prior entries in session captures (append-only rule).
- Batch all updates to the end of the session — capture progress as it happens.
- Create session documentation for trivial changes (typo fixes, formatting) unless CI requires it.
- Let worker agents write session docs in multi-agent mode — only the Session Writer does this (PROMPT-0009).
- Forget to update `session_summary/agent_session_summary.md` — both files are required.
- Overwrite an existing session capture file — create a new one or append to it.

## Output Expected

1. Session capture file path.
2. Session summary entry confirmation.
3. `require-session-logs` CI check status.

## Rollback Plan

- Session captures are append-only — if content is incorrect, add a correction update rather than editing.
- If the file itself was created in error: `git rm session_capture/{file}` and amend the commit (before push).

## References

- session_capture/session_capture_template.md — Template format
- session_summary/agent_session_summary.md — Summary log
- docs/adrs/ADR-0167-session-capture-guardrail.md — Session capture policy
- docs/adrs/ADR-0197-agent-workflow-prompt-codification.md — Decision to codify this workflow
- PROMPT-0009 — Multi-agent coordination (session writer rules)
- CLAUDE.md — Session documentation rules
