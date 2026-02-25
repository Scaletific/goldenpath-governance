---
id: PROMPT-0009
title: Multi-Agent Coordination Launch
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-idp-infra
relates_to:
  - ADR-0192
  - ADR-0193
  - ADR-0197
  - PROMPT-0010
created: 2026-02-14
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are a platform orchestrator launching and coordinating multiple AI agents to work in parallel on related tasks.

## Context

ADR-0192 defines the multi-agent coordination protocol. When work spans multiple repositories, branches, or task domains, multiple agents can run in parallel to increase throughput. This requires structured coordination: agent naming, report format, session writer designation, and serialization rules for shared resources.

This prompt provides the reusable template for planning and executing multi-agent coordination, so the orchestration is not re-planned from scratch each session.

## Your Task

Plan and launch a coordinated multi-agent mission with proper naming, reporting, and session documentation.

## Preconditions

- [ ] Work requires 2+ parallel agents (otherwise, single-agent mode is sufficient).
- [ ] Each agent's scope is well-defined and non-overlapping.
- [ ] All target branches exist or can be created.
- [ ] Human has approved the multi-agent plan.

## Activation Criteria

Multi-agent coordination activates when ANY of these are true:

- 2+ Task agents launched in parallel
- Work spans 2+ repositories
- Orchestrator explicitly declares "multi-agent mode"

For single-agent work, skip this prompt — standard session capture rules apply.

## Agent Naming Convention

| Role | Pattern | Example |
|---|---|---|
| Worker | `W{n}-{scope}` | `W1-portal`, `W2-rag`, `W3-docs` |
| Session Writer | `SW-{date}` | `SW-2026-02-14` |
| Cross-Branch | `W{n}-cross-branch` | `W4-cross-branch` |

- Workers get sequential numbers starting at W1.
- Scope should be 1-2 words describing the domain.
- Include agent ID in commit messages: `[agent:W1-portal]`.

## Agent Report Format (Mandatory)

Every worker agent MUST write a report to `.claude/agent-reports/{agent-id}-report.md` before completing.

```markdown
# Agent Report: {agent-id}

## Metadata
- agent_id: {W1-portal}
- mission_id: {YYYY-MM-DD-mission-slug}
- start_time: {ISO 8601 timestamp}
- end_time: {ISO 8601 timestamp}
- status: {complete | failed | blocked}
- branch: {branch-name}
- pr_number: #{NNN}

## Files Touched
- `{path}` (added | modified | deleted)

## Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| {what} | {chosen option} | {why} |

## Issues Encountered

| ID | Severity | Description | Resolution |
|---|---|---|---|
| {agent-id}-{seq} | {critical/high/medium/low} | {what happened} | {fix-now/defer/needs-human} |

## Summary
{2-3 sentence summary of what was accomplished}
```

## Step-by-Step Implementation

### Phase 1: Mission Planning

1. Define the mission scope and ID:

   ```
   Mission ID: {YYYY-MM-DD}-{slug}
   Example: 2026-02-14-multi-branch-merge
   ```

2. List worker agents with their scope:

   | Agent ID | Scope | Branch | Task |
   |---|---|---|---|
   | W1-{scope} | {domain} | {branch} | {one-line task} |
   | W2-{scope} | {domain} | {branch} | {one-line task} |
   | SW-{date} | session docs | {any} | Consolidate reports |

3. Identify shared resources and serialization needs:
   - **Sequential:** Branch checkout/commit/push (shared working directory)
   - **Parallel:** CI monitoring, PR creation via `gh` API, report writing

4. Get human approval of the plan before launching.

### Phase 2: Branch Preparation (Sequential)

For each worker that needs a branch:

1. Check out or create the branch.
2. Make any preparatory commits.
3. Push to remote.
4. Move to the next worker's branch.

This phase MUST be sequential because all agents share the same working directory.

### Phase 3: Worker Execution (Parallel where possible)

Launch each worker agent with:

1. Clear task description referencing this mission.
2. Agent ID assignment.
3. Branch assignment.
4. Instructions to write agent report to `.claude/agent-reports/{agent-id}-report.md`.
5. Instructions to follow PROMPT-0002 (pre-commit) and PROMPT-0003 (CI compliance).
6. Explicit rule: **DO NOT write to `session_capture/` or `session_summary/`** — that's the Session Writer's job.

### Phase 4: CI Gate Monitoring (Per Agent)

Each agent monitors its own PR:

```bash
gh pr checks {PR_NUMBER} --watch
```

If checks fail, follow PROMPT-0003 recursive fix loop. If fix would require code logic changes, STOP and flag for human review.

### Phase 5: Session Writer (Runs Last)

After ALL worker agents complete:

1. Read all agent reports:

   ```bash
   ls .claude/agent-reports/
   cat .claude/agent-reports/W1-*-report.md
   cat .claude/agent-reports/W2-*-report.md
   # ... for each worker
   ```

2. Create or append to session capture (see PROMPT-0010):
   - Agent timing table (agent_id, branch, duration, PR#, status)
   - Files touched per agent
   - Decisions made
   - Issues encountered
   - PR URLs and CI status

3. Append summary entry to `session_summary/agent_session_summary.md`.

4. Commit session documentation on the current branch.

## Verification Checklist

- [ ] All worker agents have written reports to `.claude/agent-reports/`.
- [ ] All agent reports contain mandatory fields (agent_id, start_time, end_time, status, branch, pr_number).
- [ ] Session Writer has consolidated reports into session capture.
- [ ] `session_summary/agent_session_summary.md` has been updated.
- [ ] No worker agent wrote to `session_capture/` or `session_summary/` (only SW does).
- [ ] All PRs are created and CI checks are green or pending.

## Integration Verification

- [ ] Agent reports are at `.claude/agent-reports/{agent-id}-report.md`.
- [ ] Session capture references all agent reports.
- [ ] PRs reference each other in notes if interdependent.

## Do NOT

- Let worker agents write to `session_capture/` or `session_summary/` — only the Session Writer does this.
- Run branch checkout/commit/push in parallel — these must be sequential (shared working directory).
- Skip agent reports — they are mandatory per ADR-0192.
- Launch workers without human approval of the mission plan.
- Merge PRs to `main` — agents create PRs, humans merge.
- Have two agents modify the same file concurrently.

## Output Expected

1. Mission plan table (agent ID, scope, branch, task).
2. Per-agent: PR URL, CI status, report path.
3. Session capture path.
4. Overall mission status (all complete / partial / blocked).

## Rollback Plan

- Individual agent rollback: close PR, revert commits on the agent's branch.
- Full mission rollback: close all PRs, delete agent report files.
- Session capture is append-only — add a "Mission Aborted" update rather than deleting.

## References

- docs/adrs/ADR-0192-multi-agent-coordination-protocol.md — Coordination protocol
- docs/adrs/ADR-0193-native-issue-tracking-pipeline.md — Issue tracking format
- docs/adrs/ADR-0197-agent-workflow-prompt-codification.md — Decision to codify this workflow
- PROMPT-0010 — Session documentation workflow
- PROMPT-0006 — PR creation workflow
- PROMPT-0003 — Recursive PR gate compliance
