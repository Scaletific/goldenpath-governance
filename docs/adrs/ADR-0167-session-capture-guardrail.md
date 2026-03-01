---
id: ADR-0167
title: Session Capture Append-Only Guardrail
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
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
  - GOV-0029-pr-guardrails
  - GOV-0034-ai-agent-governance
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0176
  - CL-0141
  - EC-0008-session-capture-ui
  - EC-0009-goldenpath-cli
  - EC-0010-agent-pairing-mode
  - SESSION_CAPTURE_2026_01_17_02
  - agent_session_summary
  - session_capture_template
  - session_summary_template
supersedes: []
superseded_by: []
tags:
  - governance
  - documentation
  - guardrail
  - ci
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-17
deciders:
  - platform-team
---

## Status

Accepted

## Context

Session captures are intended to preserve context for AI and human collaboration,
but without enforcement they can drift, be overwritten, or lose traceability.
We need a standardized, append-only format with CI enforcement to keep session
captures auditable and reliable.

## Decision

1. Introduce a session capture template (`session_capture/session_capture_template.md`)
   with explicit append-only rules.
2. Add a CI guardrail (`.github/workflows/session-capture-guard.yml`) that:
   - Enforces append-only changes for `session_capture/**/*.md`.
   - Requires a timestamped update header in appended content.
3. Reference the template from governance and onboarding docs to ensure adoption.

## Consequences

Positive:
- Session captures are consistent, append-only, and auditable.
- Review/validation feedback is consolidated and easier to interpret.
- Guardrail prevents accidental edits or deletions.

Tradeoffs:
- Adds a PR check for session capture edits.
- Requires contributors to follow the template and update pattern.

## Alternatives Considered

- Convention-only (no CI enforcement): rejected due to drift risk.
- Manual review in PRs: rejected due to inconsistency and overhead.
