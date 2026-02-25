---
id: PROMPT-0003
title: Recursive PR Gate Compliance
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-idp-infra
relates_to:
  - GOV-0030-pr-guardrails-index
  - pre-commit-config
  - PROMPT-0002
created: 2026-01-22
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are an AI agent working on a PR that needs to pass all CI gates. Follow this
recursive process until all checks pass. Never bypass safeguards - always fix
the root cause.

## CRITICAL: MERGING TO MAIN IS HUMAN-ONLY

**AGENTS CAN CREATE PRs targeting main**
**AGENTS CANNOT MERGE PRs targeting main**

WHY: Merging to main triggers production deployments. This requires:

- Human review of all accumulated changes
- Release decision authority (business/product approval)
- Accountability that only humans can provide

AGENT WORKFLOW FOR MAIN:

1. Create the PR (gh pr create --base main --head development)
2. Ensure all CI gates pass (fix failures recursively)
3. STOP and notify human: "PR is ready for human merge"
4. DO NOT run: gh pr merge

WHAT AGENTS CAN MERGE:

- PRs targeting development (after CI passes)

WHAT ONLY HUMANS CAN MERGE:

- Any PR targeting main (regardless of CI status)

## PHASE 1: DIAGNOSE FAILURES

Run these commands to identify what's failing:

```bash
# Check current git state
git status --short

# Run all pre-commit hooks locally
pre-commit run --all-files

# Check for any uncommitted healing script outputs
git diff
```

## PHASE 2: FIX PRE-COMMIT FAILURES (Repeat until clean)

For each failure type, apply the fix:

### markdownlint (MD004, MD007, etc.)

```bash
# Check config for expected style
cat .github/linters/markdownlint.yml
# Fix: Use * for lists, not -. Check indentation (2 spaces).
```

### trailing-whitespace / end-of-file-fixer

```bash
# Let pre-commit auto-fix
pre-commit run trailing-whitespace --all-files
pre-commit run end-of-file-fixer --all-files
git add -u
```

### terraform_fmt

```bash
terraform fmt -recursive
git add -u
```

### gitleaks (secrets detected)

```bash
# NEVER commit secrets. Remove the credential and use env var instead.
# Check what was flagged:
gitleaks detect --redact --verbose
```

### doc-metadata-autofix

```bash
# Let it auto-fix, then stage changes
python3 scripts/standardize_metadata.py docs/
git add docs/
```

### generate-*-index hooks

```bash
# These auto-regenerate indexes. Stage the changes:
python3 scripts/generate_adr_index.py
python3 scripts/generate_script_index.py
python3 scripts/generate_workflow_index.py
python3 scripts/generate_script_matrix.py
git add docs/adrs/01_adr_index.md
git add docs/50-scripts/01_script_index.md
git add docs/40-workflows/01_workflow_index.md
git add docs/50-scripts/GOV-0053-script-certification-matrix.md
```

## PHASE 3: FIX CI WORKFLOW FAILURES

### pr-guardrails.yml - Checklist incomplete

Ensure PR body contains ALL checkboxes marked:

```markdown
## Change Type
- [x] Feature  (or Bug Fix / Documentation / Refactor)

## Impact
- [x] Non-Breaking Change  (or Breaking / Infrastructure)

## Testing
- [x] Unit Tests Pass
- [x] Manual Testing Completed

## Rollback
- [x] No Rollback Needed  (or Rollback Plan Documented)
```

### changelog-policy.yml - Missing changelog

```bash
# Create changelog entry (get next number from existing files)
ls docs/changelog/entries/ | tail -5
# Create: docs/changelog/entries/CL-XXXX-short-description.md
```

### session-log-required.yml - Session docs missing

If you modified critical paths, you MUST update:

```bash
# 1. Create or update session capture
# session_capture/YYYY-MM-DD-description.md

# 2. Append to session summary
# session_summary/agent_session_summary.md
```

## PHASE 4: COMMIT AND VERIFY (Recursive Loop)

```bash
# Stage all fixes
git add -u
git add <any new files>

# Verify pre-commit passes BEFORE committing
pre-commit run --all-files

# If pre-commit fails, go back to PHASE 2
# If pre-commit passes, commit:
git commit -m "fix: address PR gate failures

- <describe each fix>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# Push and check CI
git push

# Monitor CI status
gh pr checks
```

## PHASE 5: RECURSIVE CHECK

After push, wait for CI and check results:

```bash
gh pr checks --watch
```

If ANY check fails:

1. Read the failure message carefully
2. Return to the appropriate PHASE above
3. Fix the specific issue
4. Commit with descriptive message
5. Push and repeat PHASE 5

## RULES - NEVER VIOLATE THESE

1. NEVER use --no-verify to skip pre-commit hooks
2. NEVER force push to shared branches
3. NEVER commit secrets or credentials
4. NEVER delete session capture content (append-only)
5. NEVER skip changelog for non-trivial changes
6. NEVER merge feature branches directly to main
7. NEVER mark PR checkboxes as complete if work wasn't done
8. NEVER use bypass labels unless the situation genuinely qualifies
9. NEVER run `gh pr merge` on PRs targeting main
10. NEVER approve PRs targeting main

## BRANCH WORKFLOW FOR AGENTS

```text
PRs TO DEVELOPMENT (Agent can create AND merge):
  feature/*  --> development    Create PR, Merge after CI green
  bugfix/*   --> development    Create PR, Merge after CI green
  docs/*     --> development    Create PR, Merge after CI green

PRs TO MAIN (Agent can create, HUMAN must merge):
  development --> main          Create PR, STOP - Human merges
  build-*     --> main          Create PR, STOP - Human merges
  hotfix/*    --> main          Create PR, STOP - Human merges
```

## BYPASS LABELS - USE ONLY WHEN LEGITIMATE

| Label            | Use ONLY when...                                  |
| ---------------- | ------------------------------------------------- |
| docs-only        | PR contains ONLY documentation, no code           |
| typo-fix         | PR fixes ONLY typos, no functional changes        |
| hotfix           | Critical production fix requiring immediate merge |
| changelog-exempt | Truly trivial change (whitespace, comments only)  |

## SUCCESS CRITERIA

### For PRs to development

- [ ] pre-commit run --all-files passes locally
- [ ] All CI checks show green
- [ ] PR checklist is honestly completed
- [ ] Session docs updated (if critical paths touched)
- [ ] Changelog entry exists (if non-trivial change)
- [ ] Agent can merge with: `gh pr merge --squash`

### For PRs to main

- [ ] pre-commit run --all-files passes locally
- [ ] All CI checks show green
- [ ] PR checklist is honestly completed
- [ ] Session docs updated (if critical paths touched)
- [ ] Changelog entry exists (if non-trivial change)
- [ ] STOP HERE - Notify human that PR is ready for merge

## WHEN PR TO MAIN IS READY

Once all CI gates are green on a PR targeting main:

```text
PR #{number} is ready for human merge.

URL: {pr_url}
Base: main
Head: development
CI Status: All checks passing

This PR requires human approval to merge as it targets the main branch
which triggers production deployments.

Please review and merge at your discretion:
  gh pr merge {number} --squash
```

THEN STOP. Do not attempt to merge.

## IF STUCK

If you cannot resolve a failure after 3 attempts:

1. Document what you tried in the PR comments
2. Tag @platform-team for assistance
3. Do NOT work around the safeguard
