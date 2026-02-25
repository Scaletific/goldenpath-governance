---
id: ADR-0182-tdd-philosophy
title: Test-Driven Development Philosophy
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 2026-01-26-session-capture-bootstrap-rca-tdd-prd
  - 2026-01-26-session-capture-rds-k8s-provisioning-fix
  - 2026-01-26-session-capture-tdd-quality-gate
  - 2026-01-28-agentic-graph-rag-phase0
  - 24_PR_GATES
  - 25_DAY_ONE_CHECKLIST
  - 26_AI_AGENT_PROTOCOLS
  - 27_TESTING_QUICKSTART
  - ADR-0162-determinism-protection
  - ADR-0164-agent-trust-and-identity
  - AGENT_FIRST_BOOT
  - CL-0190-tdd-foundation-and-testing-stack
  - CL-0191-coverage-enforcement-and-tdd-parity
  - CL-0192-phase1-tdd-test-suite-completion
  - CL-0194-coverage-threshold-enforcement
  - CL-0200-backstage-branch-protection-governance
  - EC-0015-backstage-tdd-parity-plan
  - GOV-0015-build-pipeline-testing-matrix
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
  - GOV-0018-platform-test-matrix
  - GOV-0020-rag-maturity-model
  - PRD-0007-platform-test-health-dashboard
  - PRD-0008-governance-rag-pipeline
  - PRD-0009-integration-test-gap-closure
  - RB-0038
  - RB-0039
  - session-2026-01-26-tdd-foundation-and-testing-stack
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-01-26
review_date: 2026-07-26
---

# ADR-0182: Test-Driven Development Philosophy

## Status

**Accepted**

## Context

The GoldenPath IDP has strong governance and architecture but weak test coverage:

- **Backstage app**: 2 smoke tests (App renders, welcome page loads)
- **Python scripts**: Tests exist but not enforced in CI
- **Shell scripts**: No tests
- **Terraform modules**: No tests
- **CI gates**: `continue-on-error: true` disables enforcement

This creates risk:

1. **Regressions go undetected** until production
2. **Refactoring is dangerous** without test safety net
3. **"Works on my machine"** issues due to untested environments
4. **Determinism is aspirational** rather than enforced

To preserve determinism and enable confident iteration, we adopt **Test-Driven Development** as a core philosophy.

## Decision

### Core Principle

> **"No feature without a test. No merge without green."**

Tests become **executable contracts** that:

1. Define expected behavior **before** implementation
2. Catch regressions **immediately**
3. Enable safe refactoring
4. Document intent through examples

### TDD Workflow

```
1. Write failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor with confidence (REFACTOR)
4. Repeat
```

### Enforcement Mechanisms

| Mechanism | Purpose |
|-----------|---------|
| **TDD Gate Workflow** | Block PRs that add code without corresponding tests |
| **Coverage Thresholds** | Fail CI if coverage drops below minimum |
| **Pre-commit Hooks** | Lint and format before commit |
| **Required Status Checks** | All tests must pass to merge |

### Coverage Targets

| Repo | V1 Target | V2 Target |
|------|-----------|-----------|
| Infra (Python) | 60% | 80% |
| Infra (Shell) | 40% | 60% |
| Backstage | 50% | 70% |
| Terraform | 30% | 50% |

### Test Co-location

Tests live next to the code they test:

```
# Python
scripts/
  platform_health.py
  tests/
    test_platform_health.py

# TypeScript
src/
  components/
    MyComponent.tsx
    MyComponent.test.tsx

# Terraform
modules/eks/
  main.tf
  tests/
    eks.tftest.hcl
```

### What Requires a Test

| Change Type | Test Required | Example |
|-------------|---------------|---------|
| New function/method | Yes | `def parse_request()` needs `test_parse_request()` |
| Bug fix | Yes | Regression test proving bug is fixed |
| New API endpoint | Yes | Request/response validation |
| Config change | Depends | Schema validation if complex |
| Documentation only | No | Pure markdown changes |
| Dependency update | No | Covered by existing tests |

### Exceptions

Tests may be skipped with explicit justification:

```python
# SKIP-TDD: One-time migration script, will be deleted after run
# Approved by: @platform-lead
# Ticket: PLAT-1234
```

All exceptions must be:
- Documented in code
- Approved by tech lead
- Linked to a ticket
- Time-bounded

## Consequences

### Positive

- **Confidence in changes**: Refactoring without fear
- **Documentation**: Tests describe expected behavior
- **Faster debugging**: Failing test pinpoints the problem
- **Quality gate**: Broken code cannot merge
- **Onboarding**: New contributors understand behavior via tests

### Negative

- **Initial velocity decrease**: Writing tests takes time upfront
- **Learning curve**: Team must learn TDD discipline
- **False confidence**: Tests only catch what they test for
- **Maintenance burden**: Tests must be maintained alongside code

### Mitigations

| Risk | Mitigation |
|------|------------|
| Velocity decrease | Provide test templates and examples |
| Learning curve | Pair programming, code review focus on tests |
| False confidence | Coverage thresholds + mutation testing (V2) |
| Maintenance burden | Delete obsolete tests, keep tests focused |

## Implementation

### Phase 1 (V1)

1. Create GOV-0016 Testing Stack Matrix
2. Add TDD gate workflow to both repos
3. Add pytest fixtures and bats infrastructure
4. Add shellcheck, ruff to pre-commit
5. Remove `continue-on-error` from Backstage CI

### Phase 2 (V2)

1. Add coverage enforcement (fail under threshold)
2. Add Terraform native tests
3. Add tox for multi-env Python testing
4. Add mypy for type checking
5. Add kuttl for K8s E2E testing

## References

- [GOV-0016: Testing Stack Matrix](../governance/policies/GOV-0016-testing-stack-matrix.md)
- [GOV-0015: Build Pipeline Testing Matrix](../governance/policies/GOV-0015-build-pipeline-testing-matrix.md)
- [Kent Beck - Test Driven Development: By Example](https://www.oreilly.com/library/view/test-driven-development/0321146530/)
- [Martin Fowler - Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-26 | Claude Opus 4.5 | Initial creation |
