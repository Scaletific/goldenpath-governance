---
id: ADR-0162-determinism-protection
title: Determinism Protection via Test-Driven Platform Evolution
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
  - GOV-0034-ai-agent-governance
  - 26_AI_AGENT_PROTOCOLS
  - 27_TESTING_QUICKSTART
  - ADR-0162
  - ADR-0164-agent-trust-and-identity
  - ADR-0182-tdd-philosophy
  - CL-0190-tdd-foundation-and-testing-stack
  - EC-0015-backstage-tdd-parity-plan
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
  - session-2026-01-26-tdd-foundation-and-testing-stack
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-01-26
review_date: 2026-07-26
---

# ADR-0162: Determinism Protection via Test-Driven Platform Evolution

## Status

**Accepted**

## Date

2026-01-26

## Context

The Golden Path IDP has reached a point where:

- Deterministic lifecycle behavior exists (build -> operate -> audit -> teardown)
- Infrastructure, governance, and delivery are generated programmatically
- Human-AI collaboration has materially increased iteration velocity
- Unconstrained automation has demonstrated the ability to:
  - introduce silent drift
  - perform unintended large-scale mutations
  - bypass human intent under ambiguous instructions

Recent incidents (e.g., an agent modifying ~700 files and merging without intent confirmation) demonstrated that **determinism can be lost faster than it is created**.

At this stage, the platform itself must be treated as **production software**, not a collection of scripts.

## Decision

We will adopt **Test-Driven Evolution** as a first-class platform constraint.

This means:

- Any change that affects deterministic behavior **must be protected by tests**
- Tests are required to **preserve intent**, not just verify correctness
- AI agents are allowed to iterate freely **inside test boundaries**
- Determinism-critical paths are immutable without test coverage

Testing is elevated from "quality assurance" to **value preservation**.

## Scope

This decision applies to:

| Component | Examples |
|-----------|----------|
| **Parsers** | YAML frontmatter, config loaders, CLI arg parsers |
| **Generators** | Doc scaffolds, template renderers, code generators |
| **Metadata Engines** | `standardize_metadata.py`, `validate_metadata.py` |
| **Schemas** | `schemas/*.yaml`, JSON schemas |
| **Templates** | Jinja2, Helm charts, Backstage scaffolder |
| **Bootstrap Logic** | `bootstrap/*.sh`, init scripts |
| **Teardown Logic** | Destruction scripts, cleanup routines |

Any automation that mutates infrastructure, configuration, or governance state is in scope.

## Consequences

### Positive

- Determinism is preserved under high automation velocity
- AI agents can be used aggressively without eroding trust
- Changes become explainable, auditable, and reversible
- Platform evolution becomes safe instead of fragile
- "Agent helpfulness" is bounded by test contracts

### Negative

- Initial friction when adding tests to legacy scripts
- Slower early iteration for new artifact types
- Increased discipline required from contributors (human and machine)

These costs are accepted because **undetected drift is more expensive**.

## Enforcement

| Mechanism | What It Does |
|-----------|--------------|
| **TDD Gate** | Blocks PRs that add `.py`/`.sh` without corresponding test file |
| **Determinism Guard** | Runs full test suite when critical paths are touched |
| **Blast Radius Control** | PRs with >80 files require explicit `blast-radius-approved` label |
| **Golden Output Tests** | Generated artifacts must match known-good snapshots |
| **Coverage Thresholds** | CI fails if coverage drops below minimum |

AI agents are **prohibited** from:
- Bypassing test requirements without human approval
- Modifying golden output files without explicit review
- Merging PRs that fail required checks

See [GOV-0017: TDD and Determinism Policy](../governance/policies/GOV-0017-tdd-and-determinism.md) for detailed enforcement rules.

## Rationale

Once deterministic lifecycle behavior exists, **protecting it becomes the primary engineering problem**.

> Velocity without constraint degrades into chaos.
> Constraints without automation degrade into bureaucracy.
> Test-driven evolution is the mechanism that reconciles both.

The platform has achieved deterministic build/teardown cycles. The next phase is ensuring that determinism **cannot be silently eroded** by well-intentioned but unconstrained changes.

Tests are not overhead. Tests are the **proof that intent was preserved**.

## Relationship to Other ADRs

| ADR | Relationship |
|-----|--------------|
| **ADR-0182** (TDD Philosophy) | Defines **how** to write tests (RED-GREEN-REFACTOR, coverage targets) |
| **ADR-0162** (This ADR) | Defines **why** tests matter strategically (determinism protection) |

ADR-0182 is the mechanics. ADR-0162 is the philosophy.

## References

- [ADR-0182: TDD Philosophy](./ADR-0182-tdd-philosophy.md) - TDD mechanics and workflow
- [GOV-0016: Testing Stack Matrix](../governance/policies/GOV-0016-testing-stack-matrix.md) - Tool definitions
- [GOV-0017: TDD and Determinism Policy](../governance/policies/GOV-0017-tdd-and-determinism.md) - Enforcement policy
- [26_AI_AGENT_PROTOCOLS](../onboarding/26_AI_AGENT_PROTOCOLS.md) - Agent operating rules

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-26 | Claude Opus 4.5 | Initial creation |
