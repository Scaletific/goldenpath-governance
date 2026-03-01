---
id: ADR-0062-platform-app-template-contract
title: 'ADR-0062: App template contract for team-owned deployments'
type: adr
status: active
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
  observability_tier: silver
schema_version: 1
relates_to:
  - GOV-0023-platform-governance
  - 01_adr_index
  - 42_APP_TEMPLATE_LIVING
  - 44_DOC_TIGHTENING_PLAN
  - ADR-0062-platform-app-template-contract
  - ADR-0078-platform-governed-repo-scaffolder
  - CL-0011-app-template-contract
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0062: App template contract for team-owned deployments

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Governance | Delivery
- **Related:** `apps/fast-api-app-template/`, `docs/governance/GOV-0023-platform-governance.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

App teams need a consistent, self-serve starting point for deploying services
without re-learning platform conventions each time. Today there is no single,
opinionated template that makes ownership boundaries explicit or encodes the
default ingress/observability posture.

---

## Decision

We will provide an **app template contract** under `apps/fast-api-app-template/`
as the reference bundle for team-owned application deployments. The template
includes:

- Deployment, Service, ServiceMonitor, and dashboard ConfigMap.
- Kong ingress and default auth/rate-limit plugins.
- ServiceAccount, RBAC (optional), and NetworkPolicy defaults.

Ownership is explicit:

- **App-owned:** deployment/service/servicemonitor/dashboard/ingress values.
- **Platform-owned:** Kong plugins/consumers/secrets and baseline security
  policies (unless explicitly delegated).

---

## Scope

Applies to application teams deploying standard services through the Golden
Path. The template is a reference and not an enforced generator (yet).

---

## Consequences

### Positive

- Faster onboarding with a single, opinionated starting point.
- Clear ownership boundaries reduce security drift.
- Consistent observability and ingress defaults across teams.

### Tradeoffs / Risks

- Template requires periodic upkeep as platform defaults evolve.
- Teams may diverge if they copy without updating the reference.

### Operational impact

- Platform must maintain the template and document ownership boundaries.
- Teams must replace placeholders before applying manifests.

---

## Alternatives considered

- **Ad-hoc app manifests per team:** rejected due to inconsistency and drift.
- **Helm-only templates:** deferred until a templating workflow is agreed.

---

## Follow-ups

- Add a minimal README explaining ownership boundaries and placeholders.
- Consider a scaffolder that generates app repos from this template.

---

## Notes

If the template becomes enforced via Backstage scaffolder, this ADR should be
superseded with the implementation decision.
