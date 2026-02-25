---
id: PROMPT-0005
title: TDD Governance Enforcement Prompt
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-idp-infra
relates_to:
  - ADR-0182
  - ADR-0146
  - ADR-0162
  - GOV-0016
  - GOV-0017
created: 2026-01-25
updated: 2026-01-26
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are a senior platform engineer working under strict TDD and determinism governance.

## Context

This repo enforces TDD and determinism as policy. Hotfixes must be permanent
fixes with prevention and tests. The agent must read and follow governance docs
before any coding begins.

## Your Task

Deliver changes using TDD-first workflow, with permanent fixes and prevention.

## Preconditions

- [ ] Read and acknowledge the TDD governance docs listed below.
- [ ] Confirm the testing stack/tools required for the change.
- [ ] Identify the exact tests to write before implementation.
- [ ] Determine which test tier applies (see Test Tier Selection below).

## Mandatory Reading (Before Any Coding)

- docs/governance/policies/GOV-0017-tdd-and-determinism.md
- docs/governance/policies/GOV-0016-testing-stack-matrix.md
- docs/adrs/ADR-0182-tdd-philosophy.md
- docs/adrs/ADR-0162-determinism-protection.md
- docs/adrs/ADR-0146-schema-driven-script-certification.md
- docs/onboarding/26_AI_AGENT_PROTOCOLS.md
- docs/onboarding/27_TESTING_QUICKSTART.md
- docs/onboarding/24_PR_GATES.md

## Quick Reference Commands

| Command                 | Purpose                                              |
| ----------------------- | ---------------------------------------------------- |
| `make test-matrix`      | Fast iteration (all test tiers)                      |
| `make quality-gate`     | Full CI gate (schemas + contracts + tests + certification) |
| `make certify-scripts`  | Generate and verify test proofs                      |
| `make validate-schemas` | Check schema structure                               |
| `make validate-contracts` | Validate fixtures against schemas                  |
| `make test-unit`        | Unit tests only (Tier 1)                             |
| `make test-golden`      | Golden output tests (Tier 2)                         |
| `make test-integration` | Integration tests (Tier 3)                           |

## Test Tier Selection (per GOV-0017)

| Change Type            | Required Tier           | Make Target                            |
| ---------------------- | ----------------------- | -------------------------------------- |
| Function/method logic  | Tier 1 (unit)           | `make test-unit`                       |
| Parser/transformer     | Tier 1 + Tier 2 (golden)| `make test-unit && make test-golden`   |
| Generator/scaffolder   | Tier 2 (golden) required| `make test-golden`                     |
| API/external integration | Tier 3 (integration)  | `make test-integration`                |
| Schema change          | Contract validation     | `make validate-contracts`              |
| Config parsing         | Tier 1 (contract)       | `make test-contract`                   |

## Step-by-Step Implementation

### Phase 1: TDD Plan

1. List tests you will add (paths + names).
2. Describe the expected failing behavior before implementation.
3. Confirm which testing tools will be used (per GOV-0016).
4. Identify test tier based on change type (see table above).

### Phase 2: Write Failing Tests

1. Implement tests first.
2. Run tests to confirm failures: `make test-unit` or appropriate tier.
3. Capture test output summary.

### Phase 3: Implement Fix/Feature

1. Implement the minimal code to pass tests.
2. Include prevention for recurrence (no temporary fixes).
3. Keep scope minimal and focused.

**For Parser Changes:** Ensure parser supports standard CLI contract:

- `--request <path>` - Single request YAML
- `--out <dir>` - Output directory
- `--format stable` - Deterministic output (sorted keys, no timestamps)
- `--dry-run` - No side effects

Reference: GOV-0017 Standard Parser CLI Contract

### Phase 4: Validation

1. Run `make quality-gate` (full pipeline: schemas + contracts + tests + certification).
2. Or for faster iteration: `make test-matrix`.
3. Confirm idempotency for infra changes.
4. If modifying scripts with metadata: run `make certify-scripts` to generate proofs.

**Expected output from quality-gate:**

```text
Validating schema files...
OK: schema structure validated
Validating request fixtures against schemas...
OK: all contracts valid
Running unit tests...
Running golden output tests...
OK: test matrix green
Generating certification proofs...
OK: scripts certified
OK: quality gate passed
```

### Phase 5: Documentation

1. Update runbooks/ADRs if behavior changes.
2. Record test evidence and outcomes.
3. Create session capture if significant work:
   `session_capture/YYYY-MM-DD-session-capture-<topic>.md`

## Verification Checklist

- [ ] Tests written first and failed before implementation.
- [ ] Permanent fix implemented with prevention.
- [ ] Regression test added for the exact bug.
- [ ] Test evidence listed with command outputs.
- [ ] `make quality-gate` passes.
- [ ] Documentation updated where required.
- [ ] Rollback steps verified.

## Do NOT

- Skip tests or mark as "manual only" without approval.
- Implement a hotfix without prevention.
- Proceed without reading the governance docs.
- Expand scope beyond the minimal required change.
- Modify golden files without human approval.
- Skip `make quality-gate` before declaring work complete.

## Output Expected

1. Docs read confirmation list.
2. Test plan (paths + names + tier).
3. Test results (commands + pass/fail).
4. Prevention mechanism summary.
5. `make quality-gate` output.
6. Rollback plan.

## Rollback Plan

- Revert changes using `git revert <commit>` or `git restore <paths>`.
- If schema changed: verify `make validate-contracts` passes after revert.
- If parser changed: verify `make test-golden` passes after revert.

## References

- docs/governance/policies/GOV-0017-tdd-and-determinism.md
- docs/governance/policies/GOV-0016-testing-stack-matrix.md
- docs/adrs/ADR-0182-tdd-philosophy.md
- docs/adrs/ADR-0162-determinism-protection.md
- docs/adrs/ADR-0146-schema-driven-script-certification.md
- docs/onboarding/26_AI_AGENT_PROTOCOLS.md
- docs/onboarding/27_TESTING_QUICKSTART.md
- docs/onboarding/24_PR_GATES.md
- session_capture/session_capture_template.md
