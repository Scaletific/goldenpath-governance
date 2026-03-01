---
id: PROMPT-0000
title: Prompt Template (Skeleton)
type: prompt-template
owner: platform-team
status: active
target_repo: any
relates_to: []
created: 2026-01-22
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

<Role assignment - who the agent is acting as>

## Context

<Background information the agent needs to understand the task>

- Current state
- Problem being solved
- Dependencies and integrations

## Your Task

<Clear, single-sentence description of the objective>

## Preconditions

<What must be true before starting>

- [ ] Condition 1
- [ ] Condition 2

## Step-by-Step Implementation

### Phase 1: <Phase Name>

<Numbered steps with explicit commands>

### Phase 2: <Phase Name>

<Numbered steps with explicit commands>

### Phase N: Commit and PR

<Standard git workflow>

## Verification Checklist

Before marking complete, verify ALL of these:

- [ ] Check 1
- [ ] Check 2
- [ ] Check N

## Integration Verification

<Cross-system checks if applicable>

- [ ] Integration check 1
- [ ] Integration check 2

## Do NOT

<Explicit guardrails - things the agent must avoid>

- Do not X
- Do not Y
- Do not Z

## Output Expected

<What the agent should produce/report when done>

1. Expected output 1
2. Expected output 2

## Rollback Plan

<How to undo if something goes wrong>

## References

- <Link to PRD>
- <Link to related docs>
- <Link to related ADRs>
