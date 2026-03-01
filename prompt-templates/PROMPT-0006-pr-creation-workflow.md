---
id: PROMPT-0006
title: PR Creation Workflow
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-infra
relates_to:
  - PROMPT-0002
  - PROMPT-0003
  - PROMPT-0013
  - ADR-0197
  - GOV-0022
created: 2026-02-14
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are a platform engineer creating a pull request that complies with all PR guardrails on the first attempt.

## Context

The GoldenPath IDP enforces PR guardrails via CI checks (`pr-guardrails` and `require-session-logs`). The PR body must include the exact YAML frontmatter header from `.github/pull_request_template.md` with at least one checkbox checked per section. Agents frequently fail on: wrong labels, missing template header, invalid Change Type options, and missing session documentation.

This prompt encodes all valid values and conventions so you create a compliant PR on the first attempt.

## Your Task

Create a pull request to the correct base branch with a fully compliant PR body, changelog entry (if required), and correct labels.

## Preconditions

- [ ] All code changes are committed and pushed to a feature branch.
- [ ] `pre-commit run --all-files` passes (see PROMPT-0002 if not).
- [ ] **Post-implementation audit completed** — PROMPT-0013 has been executed
      and all critical/high findings resolved. (Skip only for `docs-only` or
      `typo-fix` changes.)
- [ ] You know the target base branch (usually `development`).

## Valid Values Reference

### Branch-to-Base Mapping

| Branch Pattern | Base Branch | Notes |
|---|---|---|
| `feature/*` | `development` | Standard feature work |
| `fix/*` | `development` | Bug fixes |
| `docs/*` | `development` | Documentation changes |
| `hotfix/*` | `main` | Emergency fixes (PROMPT-0004 applies) |
| `sync/*` | `development` | Main-to-development sync |

### Change Type Options (exactly these strings)

- `Feature` — new functionality
- `Bug fix` — fixing broken behavior
- `Infra change` — Terraform, CI/CD, config changes
- `Governance / Policy` — ADRs, GOVs, policies, governance docs

**Invalid examples that will fail:** `Maintenance`, `Docs`, `Refactor`, `Maintenance / Sync`, `Documentation`

### Valid Labels

| Label | When to Use |
|---|---|
| `changelog-exempt` | Formatting-only, typo fixes, or CI config changes |
| `docs-only` | PR contains only documentation changes (note: `docs-only`, NOT `docs`) |
| `typo-fix` | Trivial typo corrections |
| `hotfix` | Emergency fixes following PROMPT-0004 |

### VQ Class Options

| Class | Meaning |
|---|---|
| `HV/HQ` | High Value / High Quality |
| `HV/LQ` | High Value / Low Quality (needs improvement) |
| `LV/HQ` | Low Value / High Quality |
| `LV/LQ` | Low Value / Low Quality |

## Step-by-Step Implementation

### Phase 1: Changelog Entry (skip if `changelog-exempt`)

1. Find the next CL number:

   ```bash
   ls docs/changelog/entries/ | grep -oP 'CL-\K\d+' | sort -n | tail -1
   ```

2. Create `docs/changelog/entries/CL-{NNNN}-{slug}.md` with this frontmatter:

   ```yaml
   ---
   id: CL-{NNNN}
   title: {Short descriptive title}
   type: changelog
   status: active
   owner: platform-team
   domain: platform-core
   applies_to: []
   lifecycle: active
   exempt: false
   risk_profile:
     production_impact: none
     security_risk: none
     coupling_risk: low
   schema_version: 1
   relates_to:
     - {PRD or ADR this relates to}
   supersedes: []
   superseded_by: []
   tags: []
   inheritance: {}
   supported_until: 2028-01-01
   date: {YYYY-MM-DD}
   author: {agent:agent-id or human name}
   breaking_change: false
   ---

   ## CL-{NNNN}: {Title}

   ### What Changed

   * {bullet}

   ### Why

   {reason, reference PRD/ADR}

   ### Migration

   None required.
   ```

3. Commit the changelog: `git add docs/changelog/entries/CL-{NNNN}-*.md && git commit -m "docs: add CL-{NNNN} changelog entry"`

### Phase 2: Push and Create PR

1. Push the branch:

   ```bash
   git push -u origin {branch-name}
   ```

2. Create the PR with the **exact** template body. Use a HEREDOC to preserve formatting:

   ```bash
   gh pr create --base {base-branch} --title "{short title under 70 chars}" --body "$(cat <<'EOF'
   ---
   id: pull_request_template
   title: Pull Request Template
   type: template
   risk_profile:
     production_impact: low
     security_risk: none
     coupling_risk: low
   lifecycle: active
   version: 1.0
   relates_to:
     - 24_PR_GATES
     - GOV-0029-pr-guardrails
   supported_until: 2028-01-01
   breaking_change: false
   ---

   Select at least one checkbox per section by changing `[ ]` to `[x]`.

   ## Change Type
   - [x] {one of: Feature | Bug fix | Infra change | Governance / Policy}

   ## Decision Impact
   - [x] {one of: Requires ADR | Updates existing ADR | No architectural impact}

   ## Production Readiness
   - [x] {one of: Readiness checklist completed | No production impact}

   ## Testing / Validation
   - [x] {one of: Plan/apply link provided | Test command or run ID provided | Not applicable}

   Testing/Validation details:
   - Plan/apply link: {if applicable}
   - Test command/run: {test commands and results}

   ## Code Audit (PROMPT-0013)
   - [x] {one of: Post-implementation audit completed — all critical/high findings resolved | Audit not applicable (docs-only, typo, or config change)}


   ## Risk & Rollback
   - [x] {one of: Rollback plan documented | No data migration | Not applicable}

   Rollback notes/link: {if applicable}

   ## Notes / Summary (optional)
   - VQ Class: {HV/HQ | HV/LQ | LV/HQ | LV/LQ}
   - {additional notes}
   EOF
   )"
   ```

3. Add labels if applicable:

   ```bash
   gh pr edit {PR_NUMBER} --add-label "changelog-exempt"
   ```

### Phase 3: Verify CI Checks

1. Watch CI checks:

   ```bash
   gh pr checks {PR_NUMBER} --watch
   ```

2. If `pr-guardrails` fails: check which section is missing a checkbox selection. Fix with `gh pr edit {PR_NUMBER} --body "..."`.

3. If `require-session-logs` fails: create session capture and summary entries (see PROMPT-0010).

4. If pre-commit or other CI checks fail: follow PROMPT-0003 recursive fix loop.

## Verification Checklist

- [ ] PR body includes the full YAML frontmatter header (lines 1-16 of template).
- [ ] At least one checkbox checked per section (Change Type, Decision Impact, Production Readiness, Testing/Validation, Risk & Rollback).
- [ ] Change Type uses an exact valid option (not invented).
- [ ] Labels use exact valid names (e.g., `docs-only` not `docs`).
- [ ] Base branch is correct for the branch pattern.
- [ ] Changelog entry exists (or `changelog-exempt` label applied).
- [ ] `pr-guardrails` check passes.
- [ ] `require-session-logs` check passes (if touching critical paths).

## Integration Verification

- [ ] PR appears in the correct base branch's PR list.
- [ ] All required CI checks are green or pending (not failed).
- [ ] Changelog entry has valid `relates_to` references.

## Do NOT

- Invent Change Type options — only use: `Feature`, `Bug fix`, `Infra change`, `Governance / Policy`.
- Guess label names — only use labels listed in the Valid Labels table.
- Omit the YAML frontmatter header from the PR body — the `pr-guardrails` check requires it.
- Merge PRs to `main` — agents create PRs, humans merge.
- Use `--no-verify` to skip pre-commit hooks.
- Create PRs without pushing the branch first.

## Output Expected

1. PR URL (e.g., `https://github.com/[GITHUB_ORG]/[REPO_NAME]/pull/NNN`).
2. CI check status (all green or specific failures noted).
3. Changelog entry path (if created).
4. Labels applied.

## Rollback Plan

- Close the PR: `gh pr close {PR_NUMBER}`.
- Delete the remote branch: `git push origin --delete {branch-name}`.
- Revert changelog entry if committed: `git revert <commit>`.

## References

- .github/pull_request_template.md — Source of truth for PR body template
- docs/onboarding/24_PR_GATES.md — PR gate documentation
- PROMPT-0002 — Pre-commit and pre-merge checks reference
- PROMPT-0003 — Recursive PR gate compliance loop
- PROMPT-0013 — Post-implementation recursive audit (must complete before PR)
- ADR-0197 — Decision to codify this workflow
