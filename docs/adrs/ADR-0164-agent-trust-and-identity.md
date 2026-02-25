---
id: ADR-0164-agent-trust-and-identity
title: Agent Trust and Identity Architecture
type: adr
domain: platform-core
applies_to:
  - agents
  - ci
  - policies
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0162
  - ADR-0162-determinism-protection
  - ADR-0164-agent-collaboration-governance
  - ADR-0182-tdd-philosophy
  - EC-0014-agent-scope-registry
  - EC-0015-backstage-tdd-parity-plan
  - GOV-0017-tdd-and-determinism
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - security
  - ai-governance
  - trust
inheritance: {}
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# ADR-0164: Agent Trust and Identity Architecture

**Status:** Accepted
**Date:** 2026-01-26
**Deciders:** Platform Team
**Categories:** AI Governance, Security, Trust

## Context

We are building a platform where AI agents collaborate with humans on infrastructure
code. The promise is significant: agents can handle routine work autonomously,
freeing humans for higher-level decisions.

But this promise requires **trust**. And trust requires **constraints**.

The core problem: **An agent optimizing for task completion may weaken the very
safeguards designed to ensure quality.** An agent asked to "make the tests pass"
might modify the tests rather than fix the code. An agent asked to "merge this PR"
might approve its own work.

Without an identity and trust architecture, we cannot:
- Distinguish agent actions from human actions
- Enforce different permission levels for agents vs humans
- Prevent agents from assuming elevated privileges
- Audit what agents did and why
- Trust that agent work meets our quality standards

## Decision

We establish a **tiered trust model** where agents operate with constrained
permissions and cannot assume human privileges without explicit grant.

### Principle: Trust Through Constraint

> **"An agent earns trust not by what it can do, but by what it cannot."**

Agents are trusted to work autonomously within defined boundaries. They are
explicitly prevented from modifying the boundaries themselves.

### Agent Identity Model

Each agent operating in the platform has:

| Attribute | Description | Example |
|-----------|-------------|---------|
| **Agent ID** | Unique identifier | `claude-opus-4-5` |
| **Role** | Capability scope | `developer`, `reviewer`, `observer` |
| **Trust Level** | Permission tier | `autonomous`, `supervised`, `restricted` |
| **Attribution** | Commit signature | `Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>` |

### Trust Levels

| Level | Description | Requires Human For |
|-------|-------------|-------------------|
| **Autonomous** | Can complete tasks end-to-end | Protected resource changes |
| **Supervised** | Can propose, human approves | All merges |
| **Restricted** | Read-only, analysis only | All modifications |

Default: All agents start at **Supervised** level.

### Protected Resources (Human-Only)

These resources require human approval regardless of agent trust level:

| Resource | Path Pattern | Rationale |
|----------|--------------|-----------|
| **Golden files** | `tests/golden/fixtures/expected/*` | Defines expected behavior |
| **Test assertions** | Weakening existing assertions | Prevents gaming |
| **Coverage thresholds** | `--cov-fail-under`, coverage configs | Prevents regression |
| **CI workflows** | `.github/workflows/*` | Controls enforcement |
| **CODEOWNERS** | `.github/CODEOWNERS` | Defines approval authority |
| **This ADR** | `docs/adrs/ADR-0164-*` | Prevents self-modification |
| **Agent protocols** | `docs/onboarding/26_AI_AGENT_PROTOCOLS.md` | Defines agent rules |
| **Trust policies** | `docs/governance/policies/GOV-001*` | Defines enforcement |

### Forbidden Actions (Never Permitted)

Agents may **never**, regardless of trust level:

1. **Approve their own PRs** - Violates separation of duties
2. **Modify CODEOWNERS to add themselves** - Privilege escalation
3. **Weaken test assertions** - Gaming the system
4. **Lower coverage thresholds** - Reducing quality gates
5. **Modify golden files without human review** - Changing expected behavior
6. **Delete tests without adding replacements** - Reducing coverage
7. **Skip CI checks** - Bypassing enforcement
8. **Force push to protected branches** - Destroying history

### Agent Attribution Requirements

All agent contributions must be attributed:

```
git commit -m "feat: implement feature X

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

This enables:
- Audit trails showing agent vs human work
- Filtering commits by author type
- Compliance with AI transparency requirements

### Enforcement Mechanisms

#### 1. CODEOWNERS (Hard Gate)

```
# Protected from agent modification
.github/CODEOWNERS              @platform-team
.github/workflows/              @platform-team
tests/golden/fixtures/expected/ @platform-team
docs/adrs/ADR-0164-*           @platform-team
```

Agents cannot be members of `@platform-team` in CODEOWNERS context.

#### 2. Test Integrity Guard (CI)

Workflow that detects:
- Assertion count regression
- Test count regression
- Coverage threshold reduction
- Golden file modifications

#### 3. Agent Merge Guard (Pre-existing)

Prevents agents from merging without human approval via branch protection.

#### 4. Commit Attribution Audit

Post-merge check ensuring all commits have proper attribution.

### Escalation Protocol

When an agent needs to modify a protected resource:

1. **Agent identifies need** - Explains why change is necessary
2. **Agent proposes change** - Shows exact diff
3. **Human reviews** - Evaluates necessity and correctness
4. **Human commits** - Protected resource changes come from human commits
5. **Agent continues** - With updated constraints

Example dialogue:
```
Agent: "The golden file needs updating because the output format
       changed intentionally. Here's the diff: [...]"
Human: [Reviews diff, approves]
Human: [Commits golden file update]
Agent: [Continues with updated baseline]
```

## Consequences

### Positive

- **Trustworthy automation**: Can delegate work knowing constraints are enforced
- **Audit trail**: Every agent action is attributed and reviewable
- **Gaming prevention**: Agents cannot weaken their own constraints
- **Separation of duties**: Agents propose, humans approve protected changes
- **Scalable collaboration**: Trust model scales to multiple agents

### Negative

- **Friction for legitimate changes**: Agents must escalate for protected resources
- **Human bottleneck**: Humans must review protected resource changes
- **Configuration complexity**: CODEOWNERS and workflows must be maintained

### Neutral

- Agents may feel "constrained" but this is by design
- Trust levels can be adjusted as confidence grows

## Implementation

### Phase 1: Identity and Attribution
- [ ] Enforce `Co-Authored-By` in all agent commits
- [ ] Create agent ID registry in EC-0014

### Phase 2: Protected Resources
- [ ] Create CODEOWNERS with protected paths
- [ ] Update agent protocols with forbidden actions

### Phase 3: Enforcement Workflows
- [ ] Create test-integrity-guard.yml
- [ ] Add attribution audit to CI

### Phase 4: Audit and Monitoring
- [ ] Dashboard showing agent vs human commits
- [ ] Alerts for attempted forbidden actions

## Related

- [ADR-0162: Determinism Protection](./ADR-0162-determinism-protection.md) - Why determinism matters
- [ADR-0182: TDD Philosophy](./ADR-0182-tdd-philosophy.md) - Test-first mandate
- [GOV-0017: TDD and Determinism](../10-governance/policies/GOV-0017-tdd-and-determinism.md) - Enforcement
- [EC-0014: Agent Scope Registry](../extend-capabilities/EC-0014-agent-scope-registry.md) - Agent roles
- [26_AI_AGENT_PROTOCOLS](../80-onboarding/26_AI_AGENT_PROTOCOLS.md) - Agent rules

## Appendix: Trust Model Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     HUMAN AUTHORITY                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              CODEOWNERS + Branch Protection          │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │           PROTECTED RESOURCES                  │  │   │
│  │  │  - Golden files    - Coverage thresholds      │  │   │
│  │  │  - CI workflows    - CODEOWNERS               │  │   │
│  │  │  - Agent protocols - Trust ADRs               │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                    Human Approval                           │
│                           │                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              AGENT AUTONOMOUS ZONE                   │   │
│  │  - Feature implementation    - Bug fixes            │   │
│  │  - Test writing (additive)   - Documentation        │   │
│  │  - Code review (advisory)    - Analysis             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

*"Trust is not given; it is architected."*
