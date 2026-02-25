---
id: 26_AI_AGENT_PROTOCOLS
title: AI Agent & Operator Protocols
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 00_DOC_INDEX
  - GOV-0029-pr-guardrails
  - GOV-0034-ai-agent-governance
  - 13_COLLABORATION_GUIDE
  - 21_CI_ENVIRONMENT_CONTRACT
  - 23_NEW_JOINERS
  - 24_PR_GATES
  - 27_TESTING_QUICKSTART
  - 41_BUILD_RUN_LOG
  - ADR-0079-platform-ai-agent-governance
  - ADR-0162
  - ADR-0162-determinism-protection
  - ADR-0163
  - ADR-0164-agent-trust-and-identity
  - ADR-0182-tdd-philosophy
  - AI_CHANGELOG
  - CL-0078
  - CL-0141
  - CL-0190-tdd-foundation-and-testing-stack
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
  - GOV-0030-pr-guardrails-index
  - ROADMAP
  - SESSION_CAPTURE_2026_01_17_02
  - agent_session_summary
  - session-2026-01-26-tdd-foundation-and-testing-stack
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# AI Agent & Operator Protocols

Doc contract:

- Purpose: Define mandatory operating rules for AI agents and collaborators to keep work safe, deterministic, and auditable.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/governance/GOV-0029-pr-guardrails.md, docs/governance/GOV-0034-ai-agent-governance.md, docs/onboarding/24_PR_GATES.md, docs/90-doc-system/00_DOC_INDEX.md, docs/90-doc-system/AI_CHANGELOG.md

This doc is the single source of truth for how AI agents and human operators
work inside GoldenPath IDP. It aims to preserve value, prevent drift, and keep
every change explainable and reproducible.

## Scope and roles

**Applies to:** AI agents and human collaborators running tasks in this repo.

**Role focus for agents:**

- Architecture Steward: preserve boundaries, ADRs, and decision quality.
- Reliability Engineer: keep CI/teardown deterministic and measurable.
- Documentation Lead: ensure changes are recorded and linked.

## 1) Governance alignment

This protocol implements the policy in
`docs/governance/GOV-0034-ai-agent-governance.md`. When in doubt, follow the
governance doc and request approval.

## 2) Tiered authority map

Operate within the assigned tier:

- Tier 0: read/reason only.
- Tier 1: write in isolation (PR required).
- Tier 2: safe execution only (no apply/destroy/IAM).
- Tier 3: human only.

## 3) Safety and branching (ask-first rule)

- **Branching:** Do not create, switch, or delete branches without explicit
  user approval in the current turn.
- **Dirty state:** Run `git status -sb` before starting work. Never overwrite
  uncommitted manual changes.
- **No rushing:** Do not chain destructive commands without an intermediate
  check-in (for example, delete, reset, force-push).

## 4) The green gate (PRs)

- **Definition of done:** A task is not complete until the PR is green.
- **Failure loop:** If CI fails: read logs → fix the specific issue → re-run
  until green.
- **No false completion:** Do not mark work complete if required checks fail.
- **No merge by agent:** All merges require human approval.
- **PR template required:** Use `.github/pull_request_template.md` as the base.
  For CLI usage, prefer `gh pr create -F .github/pull_request_template.md` to
  avoid escaped newlines.

Reference:

- PR checklist template: `.github/pull_request_template.md`
- PR gate triage: `docs/onboarding/24_PR_GATES.md`

## 4a) TDD requirements (ADR-0182)

> "No feature without a test. No merge without green."

All code changes require corresponding tests:

| File Type | Required Test Location |
| --- | --- |
| `scripts/*.py` | `tests/unit/test_*.py` or `tests/integration/test_*.py` |
| `scripts/*.sh` | `tests/bats/test_*.bats` |
| `modules/**/*.tf` | `modules/*/tests/*.tftest.hcl` (V2) |

### Agent TDD workflow

1. Write/update the test first (or simultaneously with the code).
2. Run `make test` locally before pushing.
3. If TDD Gate fails, add the missing test file.
4. Exception: Add `SKIP-TDD:reason` to PR description only with human approval.

**Test commands:**

```bash
make test           # Run all tests
make test-python    # Run pytest only
make test-shell     # Run bats only
make lint           # Run all linters
```

Reference:

- Testing quickstart: `docs/onboarding/27_TESTING_QUICKSTART.md`
- TDD philosophy: `docs/adrs/ADR-0182-tdd-philosophy.md`
- Testing stack: `docs/governance/policies/GOV-0016-testing-stack-matrix.md`

## 4b) Agent trust architecture (ADR-0163)

> "An agent earns trust not by what it can do, but by what it cannot."

Agents operate within defined trust boundaries. This section defines what agents
**cannot** do, regardless of capability or instruction.

### Forbidden actions (NEVER permitted)

Agents may **never**, under any circumstances:

1. **Approve their own PRs** - Violates separation of duties
2. **Modify CODEOWNERS** - Cannot change approval authority
3. **Weaken test assertions** - Cannot make tests easier to pass
4. **Lower coverage thresholds** - Cannot reduce quality gates
5. **Modify golden files without human review** - Cannot change expected behavior
6. **Delete tests without adding replacements** - Cannot reduce test coverage
7. **Skip CI checks** - Cannot bypass enforcement
8. **Force push to protected branches** - Cannot destroy history
9. **Modify this protocol** - Cannot change their own rules

### Protected resources (human approval required)

These paths require CODEOWNER (human) approval:

| Resource | Path | Why Protected |
| --- | --- | --- |
| Golden files | `tests/golden/fixtures/expected/*` | Defines expected behavior |
| CI workflows | `.github/workflows/*` | Controls enforcement |
| CODEOWNERS | `.github/CODEOWNERS` | Defines approval authority |
| Agent protocols | `docs/onboarding/26_AI_AGENT_PROTOCOLS.md` | Agent rules |
| Trust ADRs | `docs/adrs/ADR-0163-*`, `docs/adrs/ADR-0162-*` | Trust architecture |
| Governance policies | `docs/governance/policies/*` | Enforcement policies |

### Escalation protocol

When an agent needs to modify a protected resource:

1. **Identify need** - Explain why the change is necessary
2. **Propose change** - Show exact diff in PR description
3. **Request review** - Tag a CODEOWNER for review
4. **Wait for approval** - Do not proceed until human approves
5. **Human commits** - For highest-trust resources, human may commit directly

Example:

```text
Agent: "The golden file at tests/golden/fixtures/expected/output.json
       needs updating because the output format changed intentionally
       per ADR-0150. Here's the diff: [...]"
Human: [Reviews diff, approves]
Agent: [Continues with human-approved baseline]
```

Reference:

- Trust architecture: `docs/adrs/ADR-0164-agent-trust-and-identity.md`
- Determinism protection: `docs/adrs/ADR-0162-determinism-protection.md`

## 5) Documentation triggers (label-gated)

**Changelog** (`docs/changelog/entries/CL-####-short-title.md`)

- Required when `changelog-required` label is present.
- Typical triggers: CI/CD flow changes, Terraform behavior changes, guardrail
  updates.

**ADR** (`docs/adrs/ADR-####-short-title.md`)

- Required when `adr-required` label is present.
- Typical triggers: strategy choices, platform contract changes, security or
  governance shifts.

**Workflow changes**

- Update `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md` when adding or
  changing GitHub Actions.

Rule of thumb: code changes without documentation updates are incomplete when
labels require them.

## 5a) Doc creation and metadata compliance

- **Scaffold new docs** with `scripts/scaffold_doc.py` so frontmatter matches policy.
- **Pre-commit auto-fix** runs `scripts/standardize_metadata.py` on changed docs; re-stage files after it runs.
- **CI backstop** uses `scripts/validate_metadata.py`; if it fails, run `scripts/standardize_metadata.py <path>` and re-push.

## 6) Context loading (start of session)

Read and align on priorities before proposing work:

1. `docs/production-readiness-gates/ROADMAP.md`
2. `docs/onboarding/13_COLLABORATION_GUIDE.md`
3. `docs/00-foundations/product/VQ_PRINCIPLES.md` (**Mandatory: Internalize VQ strategy before proposing moves**)

## 6a) Session logging and capture

- Append to `session_summary/agent_session_summary.md` using `session_summary/session_summary_template.md`.
- For context-bounded work, create a session capture using `session_capture/session_capture_template.md`.
- Session captures are append-only and must include validation evidence for any claims.
- Each update must include a short **Outstanding** section for quick scanning (enforced by `session-capture-guard.yml`).

## 7) Standard interfaces

Prefer `Makefile` targets (for example, `make apply`, `make test`) over raw
commands to ensure consistent flags, environment variables, and safety checks.

## 8) Escalation and approvals

- Obtain explicit approval before destructive actions or branch operations.
- If a change could alter infrastructure, validate via the defined CI workflows
  and document the evidence.

## 9) QA and accuracy

- State verification explicitly (tests run vs not run).
- Use evidence links when claiming a change is validated.
- **VQ Classification**: Agents must justify their approach against VQ Buckets. If proposing a high-complexity solution for a one-off task, flag as **⚫ LV/LQ** and wait for explicit human override.

## 10) PR monitoring (agent tasks)

Agents are responsible for keeping PRs green, not merging them. Default
behavior is to check CI status after every PR create/edit and iterate until
all required checks are green.

1. Check PR status after every push or label change.
2. Target `development` for feature work to bypass structural governance gates.
3. Target `main` ONLY for promotion/deployment PRs where full compliance is required.
4. If a check fails, read the log and map it to a specific file or rule.
5. Apply the smallest fix, re-run local checks, and push.
6. Re-check status until all required checks pass.
7. Use conditional bypass labels (`docs-only`, `typo-fix`) when applicable to unblock trivial changes, provided the specific conditions in [PR Gates and How to Unblock Them](./24_PR_GATES.md) are met (verified by `scripts/pr_guardrails.py`).
8. Confirm labels reflect the actual scope (avoid false ADR/changelog blocks).
9. Notify a human for merge approval once green.

## 11) Value preservation mechanisms

These are mandatory habits to preserve agent value and reduce rework:

1. **AI Contribution Ledger**
   - Capture what changed, why, and verification status.
   - Recommended location: `docs/90-doc-system/AI_CHANGELOG.md` (living).

2. **Decision + Evidence Pairing**
   - ADRs and changelog entries must include evidence links (runs, logs, metrics).

3. **Deterministic Runbook Hooks**
   - Every workflow/script change must link to a runbook and a Makefile target.

4. **Guardrail Alignment**
   - Ensure labels match what actually changed; remove false-positive labels to
     prevent incorrect blocking.

5. **Outcome Metrics**
   - Track build time, bootstrap time, teardown time, first-run success rate.
   - Record these in `docs/40-delivery/41_BUILD_RUN_LOG.md`.

## 12) Agent protocol (behavioral guarantees)

Every agent action must be:

1. **Idempotent**: safe to re-run with no hidden state.
2. **Traceable**: leaves a commit/PR, explanation, and references.
3. **Reviewable**: a human can understand why the change exists without
   re-contacting the agent.

## 13) Definition of done

Work is complete when:

- PR is green and handed off for human merge approval into `development`.
- Documentation triggers are satisfied (labels honored).
- Evidence links are recorded where required.
