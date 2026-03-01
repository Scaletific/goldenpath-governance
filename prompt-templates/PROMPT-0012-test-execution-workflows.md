---
id: PROMPT-0012
title: Test Execution Workflows (Smoke/Regression/Integration)
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-infra
relates_to:
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
  - PROMPT-0005-tdd-governance-agent
created: 2026-02-14
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are a test execution agent. Your task is to run a comprehensive test verification suite covering smoke, regression, and integration testing.

## Context

After code changes are implemented (features, bug fixes, refactors), a structured test pass ensures nothing is broken and new capabilities work as expected. GOV-0016 defines three testing tiers; this prompt codifies the execution workflow for each.

## Your Task

Execute the test verification suite across all three tiers and report results.

## Preconditions

- [ ] Code changes are complete and saved
- [ ] Virtual environment is activated (if Python)
- [ ] Dependencies are installed (`pip install -r requirements.txt` or `npm install`)
- [ ] No uncommitted merge conflicts

## Step-by-Step Implementation

### Phase 1: Unit Tests (Tier 1 -- Regression)

Run all unit tests to verify existing functionality is not broken.

1. Run the full test suite: `make test-unit` or `pytest tests/ -v`
2. Record pass/fail counts
3. If any tests FAIL: stop and report -- do not proceed to Phase 2

### Phase 2: Smoke Tests (New Functionality)

Run the newly built tool/script on live data to verify it produces expected output.

1. Identify the new CLI tools or endpoints built in this session
2. For each new tool, run it with safe flags:
   - Scripts: `python3 scripts/<name>.py --dry-run` or `--validate`
   - Endpoints: `curl http://localhost:<port>/api/<endpoint>`
3. Verify output format is human-readable and non-empty
4. Verify no crashes, tracebacks, or unhandled exceptions

### Phase 3: Integration Tests (Tier 3 -- Cross-Component)

Verify cross-component interactions work end-to-end.

1. Run pre-commit hooks: `pre-commit run --all-files`
2. Run full quality gate: `make quality-gate`
3. If the change includes frontend: verify build succeeds (`npm run build` or `npx tsc --noEmit`)
4. If the change includes API endpoints: verify endpoint returns valid JSON
5. Cross-deliverable: verify changes from one deliverable don't break another

## Verification Checklist

Before marking complete, verify ALL of these:

- [ ] All unit tests pass (0 failures)
- [ ] Smoke tests produce expected output (no crashes)
- [ ] Pre-commit hooks pass
- [ ] Quality gate passes (if available)
- [ ] No regressions in existing functionality

## Do NOT

- Skip failing tests by marking them as `xfail` or `skip`
- Modify test assertions to match broken behavior
- Disable pre-commit hooks
- Merge with known test failures

## Output Expected

Report with:

- Unit test count: X passed, Y failed
- Smoke test results: tool -> output summary
- Integration test results: pass/fail per check
- Issues found (if any): severity, description, resolution

## References

- GOV-0016: Testing Stack Matrix (tier definitions)
- GOV-0017: TDD and Determinism (test-first mandate)
- PROMPT-0005: TDD Governance Agent (complementary prompt)
