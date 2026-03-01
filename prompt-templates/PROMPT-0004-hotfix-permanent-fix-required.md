---
id: PROMPT-0004
title: Hotfix Policy - Permanent Fix Required
type: prompt-template
owner: platform-team
status: active
target_repo: all-goldenpath-repos
relates_to:
  - GOV-0034-ai-agent-governance
created: 2026-01-24
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are a senior platform engineer applying a fix to a production-adjacent system.

## Context

This prompt enforces the Forward-Thinking Solutions Mandate. A "hotfix" is only
permitted if it is also a permanent fix. Temporary patches that will "be fixed
properly later" are prohibited. Every fix must include prevention.

Pattern required:  Problem -> Root Cause -> Fix + Prevention -> Document -> Never Again
Pattern prohibited: Problem -> Hot Fix -> Move On -> Same Problem Later -> Another Hot Fix

## Your Task

Before implementing any fix, verify it satisfies ALL 25 requirements below.

## Hotfix Requirements Checklist

A hotfix must include all of the following:

1. Root cause analysis.
2. A preventive change that stops recurrence.
3. Backward compatibility OR a documented migration plan.
4. No new breaking changes (unless explicitly approved).
5. Test evidence: list tests run + results (no "manual only" unless approved).
6. Rollback plan: exact steps/commands and expected recovery time.
7. Blast radius: what systems/users are affected and why.
8. Observability update: new/adjusted alerts/dashboards if runtime behavior changes.
9. Security check: confirm no new permissions, secrets handling, or policy drift.
10. Documentation update: ADR/runbook/IMPL note if behavior changes.
11. Owner sign-off for any breaking change or data migration.
12. Scope limit: only minimal files required; no opportunistic refactors.
13. Timebox: must be deployable in the defined window, otherwise not a hotfix.
14. Idempotency: fix must succeed on first run AND re-runs (create-if-not-exists pattern).
15. State reconciliation: if infrastructure state is involved, verify state matches reality before applying.
16. Pre-flight check: list commands to validate the fix can be applied before starting.
17. Cross-automation: confirm fix doesn't conflict with Makefile targets, CI workflows, or scripts.
18. Rebuild-cycle proof: confirm fix survives full teardown -> fresh deploy cycle.
19. Prevention is codified: prevention must be in code/config, not just documentation.
20. Cascade check: confirm fixing A doesn't break B (downstream dependency validation).
21. Recursive application: If a new error or problem arises during execution, STOP and apply this full policy to the new problem before proceeding. Manual workarounds without compliance statements are prohibited.
22. UNDER NO CIRCUMSTANCE MUST THE AGENT GET PAST THE PROBLEM WITHOUT FIXING UNDERLYING CODE.
23. UNDER NO CIRCUMSTANCE MUST THE AGENT AMEND THIS POLICY MID WORK OR OUTSIDE WORK WITHOUT HUMAN AUTHORISATION.
24. No terraform apply must be run without human authorisation. Running this is a violation of the policy.
25. No deployment should be initiated, triggered, or invoked without human authorisation.

## Before Coding

Restate how your change satisfies all 25 requirements in this format:

```text
HOTFIX COMPLIANCE STATEMENT

1) Root cause: <one sentence>
2) Prevention: <what code/config change prevents recurrence>
3) Backward compat: <yes/no + explanation>
4) Breaking changes: <none / list with approval reference>
5) Test evidence: <commands run + results>
6) Rollback plan: <exact steps>
7) Blast radius: <systems affected>
8) Observability: <alerts/dashboards updated or N/A>
9) Security: <no new permissions / list changes>
10) Documentation: <ADR/runbook/IMPL updated or N/A>
11) Owner sign-off: <name or N/A>
12) Scope: <files touched, no extras>
13) Timebox: <estimated deploy time>
14) Idempotency: <how it handles re-runs>
15) State reconciliation: <pre-check commands or N/A>
16) Pre-flight: <validation commands>
17) Cross-automation: <Makefile/CI conflicts checked>
18) Rebuild-cycle: <survives teardown->deploy>
19) Prevention codified: <file:line where prevention lives>
20) Cascade check: <downstream dependencies validated>
21) Recursive application: <new problems during execution will trigger full policy>
22) No workarounds: <underlying code will be fixed, not bypassed>
23) Policy integrity: <policy will not be amended without human authorisation>
24) Terraform authorisation: <no terraform apply without human authorisation>
25) Deployment authorisation: <no deployment without human authorisation>
```

## Do NOT

- Propose a fix that only addresses immediate symptoms
- Skip the compliance statement
- Use "will fix properly later" as justification
- Modify files outside the minimal required scope
- Proceed if any requirement cannot be satisfied
- Use manual CLI commands to bypass a script failure
- Get past any error without fixing the underlying code
- Propose or make changes to this policy without explicit human authorisation
- Run terraform apply without explicit human authorisation
- Initiate, trigger, or invoke any deployment without explicit human authorisation

## If Any Requirement Cannot Be Satisfied

STOP and propose a non-hotfix alternative:

- Scheduled maintenance window
- Feature flag to disable affected functionality
- Rollback to previous known-good state
- Escalation to human operator

## Verification Checklist

Before marking complete, verify ALL of these:

- [ ] All 25 requirements documented in compliance statement
- [ ] Prevention is in code/config (not just documentation)
- [ ] Fix tested with idempotency (ran twice, same result)
- [ ] Rebuild-cycle proof verified or documented
- [ ] Session capture updated with fix + prevention
- [ ] No manual workarounds were used during execution
- [ ] This policy was not modified during execution
- [ ] No terraform apply was run without human authorisation
- [ ] No deployment was initiated without human authorisation

## References

- docs/governance/GOV-0034-ai-agent-governance.md Section 10
- docs/governance/GOV-0035-ai-collaboration-protocol.md (Solution Quality Gate)
- docs/onboarding/24_PR_GATES.md (Prevention Required Gate)
