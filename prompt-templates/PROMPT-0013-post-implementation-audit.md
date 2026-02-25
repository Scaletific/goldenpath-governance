---
id: PROMPT-0013
title: Post-Implementation Recursive Audit
type: prompt-template
owner: human
status: draft
relates_to:
  - GOV-0017
  - GOV-0016
  - PROMPT-0005
  - PROMPT-0006
created: 2026-02-14
---

<!-- WARNING: PROMPT TEMPLATE — DO NOT AUTO-EXECUTE -->
<!-- This prompt is designed for human-supervised AI execution. -->
<!-- Read fully, adapt to your context, then invoke step by step. -->

# PROMPT-0013: Post-Implementation Recursive Audit

## Context

After a feature, fix, or refactor is implemented, code can ship with subtle
defects that individual unit tests won't catch: unwired components, dead code
paths, inconsistent error handling, proposed-but-unbuilt features referenced in
comments or docs, and missing documentation. This prompt drives a **systematic,
multi-pass audit** that surfaces these issues before a PR is opened.

## Your Task

Perform a thorough recursive audit across all deliverables produced in the
current implementation session. Surface every defect, inconsistency, and gap.
Classify findings by severity. Resolve what you can; escalate what you cannot.

## Preconditions

- [ ] Implementation is functionally complete (all planned code is written)
- [ ] Tests exist and pass locally (`make test-matrix` green)
- [ ] You have read the relevant PRD/ADR/issue that defines "done"
- [ ] You know which files were created or modified in this session

## Mandatory Reading

Before starting the audit, read:

| Document | Why |
|----------|-----|
| The originating PRD/ADR/Issue | Know what was requested vs. what was built |
| `docs/governance/policies/GOV-0017-tdd-and-determinism.md` | Test coverage expectations |
| `docs/governance/policies/GOV-0016-testing-stack-matrix.md` | Which test tiers apply |
| `prompt-templates/PROMPT-0005-tdd-governance-agent.md` | TDD naming and structure rules |

## Step-by-Step Execution

### Phase 1: Inventory & Scope

Establish the blast radius of the implementation.

- [ ] List every file created, modified, or deleted in this session
- [ ] Identify every public function, class, endpoint, or component added
- [ ] Map the dependency graph — what calls what, what imports what
- [ ] Note any files that were *read but not modified* (potential missed updates)

**Output:** A file manifest with change type (new/modified/deleted) for each.

### Phase 2: Correctness & Completeness

Walk every code path and verify it does what it claims.

- [ ] **Dead code**: Find functions, variables, imports, or components that are
      defined but never called or referenced
- [ ] **Unwired components**: Identify UI components, API endpoints, event
      handlers, or hooks that exist but are not connected to the application
      flow (e.g., a button component that's never rendered, a route that's
      defined but unreachable)
- [ ] **Proposed but not implemented**: Search for TODO, FIXME, HACK, XXX,
      "placeholder", "stub", "not yet implemented" — flag any that were
      introduced in this session and represent incomplete work
- [ ] **Partial implementations**: Check for functions with early returns that
      silently skip logic, empty catch/except blocks, pass-through functions
      that don't transform data
- [ ] **Feature parity**: Compare the implementation against the originating
      PRD/ADR/Issue — list every requirement and mark it as implemented,
      partially implemented, or missing
- [ ] **Edge cases**: Verify behavior for empty inputs, null/None values,
      boundary conditions, and error states

### Phase 3: Code Quality & Best Practices

Evaluate craftsmanship and maintainability.

- [ ] **Type safety**: All function signatures have type hints (Python) or
      TypeScript types (TS/TSX). No `Any` types unless justified. No implicit
      `any` in TypeScript.
- [ ] **Error handling**: Every external call (API, DB, file I/O, network) has
      explicit error handling. Errors propagate meaningful messages, not raw
      stack traces. No bare `except:` or `catch(e) {}` blocks.
- [ ] **Input validation**: All user-facing inputs are validated at the boundary.
      Path traversal, injection, and OWASP Top 10 vectors are mitigated.
- [ ] **Naming consistency**: Variables, functions, files, and classes follow the
      codebase's existing conventions (check neighboring files for style).
- [ ] **DRY violations**: Flag duplicated logic that should be extracted — but
      only if it's genuinely repeated (3+ occurrences), not premature
      abstraction.
- [ ] **Import hygiene**: No unused imports. No circular imports. External
      dependencies are justified (not added for trivial functionality).
- [ ] **Magic values**: No hardcoded strings, ports, URLs, or thresholds that
      should be constants or configuration.
- [ ] **Logging & observability**: Significant operations log at appropriate
      levels. No sensitive data in logs. Structured logging preferred.
- [ ] **Performance red flags**: No N+1 queries, no unbounded loops over
      user-controlled input, no synchronous blocking in async contexts, no
      missing pagination on list endpoints.

### Phase 4: Test Coverage Audit

Verify tests are sufficient and correctly structured.

- [ ] **Coverage mapping**: Every public function/endpoint/component has at least
      one test. List any untested code paths.
- [ ] **Test file naming**: Verify test files match the TDD gate convention:
      `<dir>/tests/test_<name>.py` for source file `<dir>/<name>.py`
- [ ] **Happy path + failure path**: Each tested function has at minimum one
      success test and one failure/error test.
- [ ] **Mock correctness**: Mocks target the right import path (where the symbol
      is used, not where it's defined). Mock return values match real return
      types.
- [ ] **Test isolation**: Tests don't depend on execution order, shared mutable
      state, or external services without mocking.
- [ ] **Assertion quality**: Tests assert specific values, not just "no
      exception was raised". No bare `assert True` or `assert result`.
- [ ] **Run the tests**: Execute `make test-matrix` and confirm all pass.

### Phase 5: Coherence & Integration

Verify the implementation works as a unified whole, not just isolated parts.

- [ ] **Data flow continuity**: Trace data from entry point (UI/API) through
      processing to storage/output. Verify no field is dropped, renamed
      inconsistently, or silently transformed.
- [ ] **API contract alignment**: If backend endpoints changed, verify the
      frontend calls match (method, path, request body, response shape).
      Check TypeScript types match Python response models.
- [ ] **State consistency**: If state is managed (React state, database records,
      file artifacts), verify all state transitions are valid and no orphaned
      state is possible.
- [ ] **Configuration coherence**: Environment variables, feature flags, and
      config files are consistent across all layers (backend, frontend, CI,
      Docker, Terraform).
- [ ] **Cross-file consistency**: If a type/interface/schema changed, verify ALL
      consumers are updated — not just the first one found.

### Phase 6: Documentation & Operability

Identify what documentation is needed to support the work long-term.

- [ ] **How-It-Works doc**: If a new subsystem, workflow, or non-obvious
      mechanism was introduced, does a "How It Works" explanation exist?
      Recommend creating one if the code alone is insufficient.
- [ ] **Runbook/Playbook**: If the feature introduces new failure modes,
      operational procedures, or manual steps — recommend a runbook in
      `docs/70-operations/`.
- [ ] **ADR needed?**: If an architectural decision was made during
      implementation (chose library X over Y, chose pattern A over B), flag
      that an ADR should be written.
- [ ] **Script index**: If new scripts were added, verify they appear in
      `docs/50-scripts/01_script_index.md`.
- [ ] **API documentation**: If endpoints were added or changed, verify route
      documentation exists (docstrings, OpenAPI schema, or API docs).
- [ ] **Inline comments**: Complex algorithms, workarounds, or non-obvious
      logic should have brief explanatory comments. Simple code should not
      be over-commented.

## Findings Report Format

Present findings in this table format, grouped by phase:

| # | Phase | Severity | File:Line | Finding | Resolution |
|---|-------|----------|-----------|---------|------------|
| 1 | Correctness | critical | `app.py:42` | `/health` endpoint defined but not mounted on router | Fix now |
| 2 | Quality | medium | `utils.py:18` | Bare `except Exception` swallows all errors | Fix now |
| 3 | Documentation | low | — | No runbook for new cron job failure recovery | Create runbook |

### Severity Definitions

| Severity | Meaning | Action |
|----------|---------|--------|
| **critical** | Broken functionality, security vulnerability, data loss risk | Must fix before PR |
| **high** | Incorrect behavior under realistic conditions, missing validation | Must fix before PR |
| **medium** | Code smell, missing tests, minor inconsistency | Fix now or document in PR |
| **low** | Style nit, documentation gap, nice-to-have improvement | Document; fix if time permits |

## Verification Checklist (Definition of Done)

- [ ] All 6 phases executed and findings documented
- [ ] All critical and high findings resolved
- [ ] Medium findings either resolved or documented in PR description
- [ ] `make test-matrix` passes after all fixes applied
- [ ] `make quality-gate` passes (if available)
- [ ] No new TODOs introduced without a linked issue
- [ ] Feature parity confirmed against originating PRD/ADR/Issue

## Do NOT

- **Do not refactor unrelated code** — audit scope is limited to this session's
  deliverables. Note unrelated issues but don't fix them.
- **Do not add speculative features** — if something wasn't in the requirements,
  don't build it during the audit.
- **Do not weaken tests to make them pass** — if a test fails, fix the code or
  the test expectation, don't delete the test.
- **Do not skip phases** — even if the implementation seems simple, run all 6
  phases. Small PRs still have integration issues.
- **Do not auto-execute this prompt** — it requires human judgement on which
  findings to fix vs. defer.

## Output Expected

When the audit is complete, report:

```
## Audit Summary

**Scope:** [list of files audited]
**Originating work:** [PRD/ADR/Issue reference]
**Findings:** X critical, Y high, Z medium, W low
**Resolved:** N of (X+Y+Z+W)
**Deferred:** [list with justification]

## Findings Table
[table from above]

## Recommended Documentation
- [ ] [doc type]: [description] → [suggested path]

## Remaining Risks
[anything the reviewer should pay attention to]
```

## Rollback Plan

This prompt is read-only analysis with targeted fixes. If a fix introduced
during the audit causes a regression:

1. `git diff` to identify the audit fix that caused the issue
2. `git checkout -- <file>` to revert the specific file
3. Re-run `make test-matrix` to confirm stability
4. Document the reverted fix as a finding that needs a different approach

## References

- [GOV-0017 — TDD and Determinism Policy](../docs/governance/policies/GOV-0017-tdd-and-determinism.md)
- [GOV-0016 — Testing Stack Matrix](../docs/governance/policies/GOV-0016-testing-stack-matrix.md)
- [PROMPT-0005 — TDD Governance Agent](PROMPT-0005-tdd-governance-agent.md)
- [PROMPT-0006 — PR Creation Workflow](PROMPT-0006-pr-creation-workflow.md)
- [PR Gates Guide](../docs/onboarding/24_PR_GATES.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
