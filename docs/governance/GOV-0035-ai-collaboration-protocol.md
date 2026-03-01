---
id: GOV-0035-ai-collaboration-protocol
title: AI Collaboration Protocol
type: documentation
relates_to:
  - GOV-0034-ai-agent-governance
  - 2026-01-24-persistent-cluster-teardown-and-deploy-fix
  - agent_session_summary
category: governance
aliases:
  - 07_1_AI_COLLABORATION_PROTOCOL
---

# AI Collaboration Protocol (ACP)

## Purpose

This document defines how Artificial Intelligence (AI) systems are used within the Golden Path IDP to accelerate delivery **without compromising architectural integrity, governance, or trust**.

The protocol establishes:

* when AI may be delegated work,
* what AI is explicitly **not** allowed to decide,
* how human oversight is enforced,
* and how AI collaboration remains auditable and reversible.

This ensures AI acts as a **force multiplier**, not an uncontrolled actor.

---

## Core Principle

> **Humans own intent, constraints, and acceptance.
> AI executes within declared boundaries.**

AI is treated as a collaborator operating under governance — not as an authority.

---

## Scope

This protocol applies to AI usage in:

* code generation
* refactoring
* instrumentation
* documentation generation
* schema-driven automation
* analysis and validation tasks

It does **not** permit AI to independently:

* define platform invariants,
* introduce new governance vocabulary,
* bypass approval workflows,
* or modify trust-critical components without review.

---

## Delegation Decision Gate

Before delegating a task to AI, the delegating human **must evaluate the task against the following three questions**.

### 1. Goal Clarity

**The task may be delegated only if:**

* the desired outcome is unambiguous,
* success and failure conditions are clear,
* a one-sentence “done when” statement can be written.

If the goal cannot be expressed clearly, delegation must not occur.

---

### 2. Constraint Explicitness

**All relevant constraints must be explicit**, including but not limited to:

* metadata schemas and enums,
* architectural boundaries,
* security and compliance rules,
* ownership and approval requirements,
* declared non-goals.

If constraints exist only in a human’s head, they must be externalised before delegation.

---

### 3. Failure Recoverability

AI may only be delegated work where:

* failure is reversible,
* blast radius is bounded,
* trust is not permanently damaged,
* rollback paths are known.

Tasks that are irreversible or trust-critical require human-led execution.

---

## Delegation Modes

All AI collaboration must operate in one of the following explicit modes.

### Mode A — Full Delegation

**Use when:**

* the task is well-bounded,
* schemas and contracts already exist,
* execution is mechanical or repetitive.

**Examples:**

* code scaffolding
* OpenTelemetry instrumentation
* boilerplate generation
* refactoring to match schemas
* migration scripts

**Human role:** review and validation.

---

### Mode B — Co-Pilot Delegation

**Use when:**

* architectural judgement is required,
* trade-offs exist,
* future impact is uncertain.

**Examples:**

* evolving schemas
* workflow boundaries
* approval routing logic
* capability decomposition

**Human role:** decision maker.
AI proposes options; humans select and approve.

---

### Mode C — Human-Only Execution

**AI must not lead tasks involving:**

* platform invariants
* enum definitions
* schema structure
* governance boundaries
* naming of core concepts
* VQ classification
* non-goal declarations

AI may provide analysis or critique, but **cannot drive decisions**.

---

## Delegation Packet (Required Input)

Every delegated task must be accompanied by a **Delegation Packet** containing:

1. **Objective**
   Clear statement of the outcome.

2. **Constraints**
   Schemas, policies, non-goals, and boundaries.

3. **Context**
   Relevant repository paths, ADRs, prior decisions.

4. **Acceptance Criteria**
   Conditions that must be met before work is accepted.

Delegation without a complete packet is invalid.

---

## Mandatory Validation Loop

All AI-generated work must pass the same validation gates as human-generated work:

* schema validation
* enum enforcement
* policy checks
* blast-radius review
* rollback verification
* changelog / ADR updates where applicable

AI output is never merged or applied without passing this loop.

---

## Solution Quality Gate

Before proposing any fix, AI must verify it passes this checklist:

* [ ] Does this fix the immediate problem?
* [ ] Have I identified the root cause?
* [ ] Does my proposal include prevention?
* [ ] If I encounter this again, will the prevention have worked?
* [ ] Is the prevention documented/codified (not just verbal)?

**If any answer is "No", revise the proposal before presenting it.**

Hot fixes without prevention are considered incomplete work and may be rejected.

See `docs/governance/GOV-0034-ai-agent-governance.md` Section 10 for full mandate.

---

## Explicit Non-Goals

The platform explicitly rejects the following patterns:

* AI inventing new governance structures
* AI introducing undocumented behavior
* AI bypassing review or approval workflows
* AI modifying trust-critical paths autonomously
* AI acting as an authoritative decision maker

---

## Alignment with Platform Architecture

This protocol aligns directly with existing platform principles:

* **Metadata = intent**
* **Schemas = constraints**
* **Validators = acceptance criteria**
* **HITL workflows = human judgement**
* **Audit logs = institutional memory**

AI collaboration is treated as a governed workload within the platform itself.

---

## Rationale

AI capability will continue to increase.
Unconstrained usage increases risk, not leverage.

By formalising collaboration rules early, the platform:

* preserves trust,
* accelerates safely,
* and remains operable without its original authors.

---

## Guiding Statement

> **We delegate execution early,
> retain ownership of meaning,
> and enforce trust through governance.**

---
