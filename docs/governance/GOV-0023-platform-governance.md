---
id: GOV-0023-platform-governance
title: Platform Governance Purpose
type: policy
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 00_DOC_INDEX
  - GOV-0056-tag-scoped-policy-template
  - 01_adr_index
  - GOV-0024-governance-model
  - 02_PLATFORM_BOUNDARIES
  - GOV-0025-governance-backstage
  - 05_OBSERVABILITY_DECISIONS
  - GOV-0041-cost-governance
  - 07_REPO_DECOUPLING_OPTIONS
  - 08_INGRESS_STRATEGY
  - 10_INFRA_FAILURE_MODES
  - 10_PLATFORM_REQUIREMENTS
  - 11_NETWORKING
  - 12_GITOPS_AND_CICD
  - 19_DELIVERY_INSIGHTS
  - 33_IAM_ROLES_AND_POLICIES
  - GOV-0042-resource-tagging
  - 40_CHANGELOG_GOVERNANCE
  - 41_STORAGE_AND_PERSISTENCE
  - ADR-0016-platform-ci-environment-separation
  - ADR-0027-platform-design-philosophy
  - ADR-0028-platform-dev-branch-gate
  - ADR-0036-platform-orphan-cleanup-workflow
  - ADR-0037-platform-resource-tagging-policy
  - ADR-0039-platform-tag-scoped-iam-policy-template
  - ADR-0052-platform-kube-prometheus-stack-bundle
  - ADR-0061-platform-observability-provisioning-boundary
  - ADR-0062-platform-app-template-contract
  - ADR-0101-pr-metadata-auto-heal
  - DOCS_ADRS_README
  - agent_session_summary
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
aliases:
  - 01_GOVERNANCE
---

# Platform Governance Purpose

Doc contract:

- Purpose: Define governance principles and default platform decisions.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/20-contracts/02_PLATFORM_BOUNDARIES.md, docs/50-observability/05_OBSERVABILITY_DECISIONS.md, docs/00-foundations/18_BACKSTAGE_MVP.md, docs/governance/GOV-0042-resource-tagging.md, docs/governance/GOV-0041-cost-governance.md, docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md

This document defines how the Internal Developer Platform (IDP) is governed.

Governance exists to encode good decisions into the system so that:

- Teams can move fast without sacrificing safety
- Reliability does not depend on heroics or tribal knowledge
- The platform can scale without fragmenting

Governance is not about restriction.

It is about removing unnecessary decisions so teams can focus on delivering value.

The platform/team boundary is defined in `docs/20-contracts/02_PLATFORM_BOUNDARIES.md`.

## Governance Principles

## 1. Opinionated by Default

V1 provides one recommended way to solve common problems.

Opinionation applies to:

- Cloud provider
- Ingress and API gateway
- Secrets management
- CI/CD and GitOps
- Observability standards
- Automation
- Support

Choice is introduced only when the cost of not offering it exceeds the cost of supporting it.

## 2. Golden Path First

All platform tooling is optimized for the Golden Path:

- Templates
- Pipelines
- Documentation

The platform is the reference implementation for its own delivery rails. The
design philosophy is maintained as a living document, and core docs are tracked
in `docs/90-doc-system/00_DOC_INDEX.md` with a defined review cadence.

Teams may deviate, but deviations:

- Are not optimized
- Are not guaranteed support
- Transfer operational responsibility to the team

Freedom exists — with ownership.

## 3. Contracts Over Customization

The platform exposes stable contracts, not unlimited configuration.

Examples:

- Terraform module inputs/outputs
- Standard ingress and auth patterns
- Defined CI/CD stages
- Observability and SLO expectations

Contracts scale.

Snowflakes do not.

## 4. Preventative Governance

Governance is enforced:

- At design time
- Through defaults and templates
- Via automation and guardrails (e.g., `scripts/pr_guardrails.py`, ADR-0101)

Not through:

- Manual policing
- After-the-fact reviews
- Individual enforcement

If engineers must repeatedly ask “how do I do this?”, governance has failed.

## 5. Tagging for Auditability

GoldenPath requires consistent resource tagging to keep audit trails, cost
attribution, and cleanup reliable. Tagging is a core governance guardrail that
preserves velocity by making ownership and lifecycle status explicit.
The canonical tag set lives in `docs/governance/GOV-0042-resource-tagging.md` and is formalized
in `docs/adrs/ADR-0037-platform-resource-tagging-policy.md`.
Destructive automation must use tag-scoped IAM policies; see
`docs/governance/policies/GOV-0056-tag-scoped-policy-template.md` and
`docs/adrs/ADR-0039-platform-tag-scoped-iam-policy-template.md`.

## 6. Changelog Accountability

Material platform behavior changes must be captured in a changelog entry when
the PR is labeled `changelog-required`. The policy and label rules are defined
in `docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md`. Certain labels (e.g., `docs-only`, `typo-fix`) allow automated bypass if validated conditions are met (see ADR-0101).

## 7. Cost Visibility

Cost impact is surfaced early in CI to drive informed decisions without
blocking delivery. The cost visibility policy is defined in
`docs/governance/GOV-0041-cost-governance.md`.

## Governance Operating Model (V1)

1. **Platform is the product**: governance decisions are versioned, PR-driven,
   and owned by the platform team.
2. **Golden paths before options**: V1 supports a narrow set of archetypes to
   keep outcomes predictable.
3. **Security and observability are prewired**: baseline guardrails ship by
   default so teams do not wire them manually.
4. **Deterministic teardown is mandatory**: cleanup paths are CI-safe and avoid
   manual session dependencies.
5. **Contracts over tool choice**: teams may use different CI runners as long
   as platform contracts are met.

## Responsibilities (V1)

| Domain | Platform Team (R/A) | App Teams (R/A) | Notes |
| --- | --- | --- | --- |
| Infrastructure modules, env overlays | Own design, upkeep, and guardrails | Consume modules; request changes | Platform owns infra contracts |
| CI/CD templates and gates | Provide and maintain templates, quality gates | Use templates; extend via approved hooks | CI remains authoritative |
| Observability stack | Maintain Prometheus/Loki/Grafana baseline | Emit metrics/logs; define service SLOs | See `docs/50-observability/05_OBSERVABILITY_DECISIONS.md` |
| Identity and secrets | Operate IdP and secrets backend | Integrate apps with provided patterns | No ad-hoc secrets |
| Backstage catalog | Seed templates and plugins | Keep metadata/runbooks current | Backstage is the governance lens |

## Backstage Governance Lens (Summary)

Backstage surfaces governance, while enforcement lives elsewhere.

| Area | Backstage does | Does not do | Enforcement lives in |
| --- | --- | --- | --- |
| Golden Path templates | Exposes approved scaffolds | Allow arbitrary templates | Platform repo review + versioning |
| Catalog metadata | Makes ownership and lifecycle visible | Enforce runtime correctness | CI + GitOps promotion gates |
| Observability links | Surfaces dashboards, logs, traces | Generate telemetry | Observability stack |
| Compliance signals | Displays scorecards | Make pass/fail decisions | CI checks and policies |
| Documentation | Centralizes platform and service docs | Replace runbooks | Docs + SRE process |

## V1 Governance Scope & Decisions

## Cloud Provider

Decision: AWS-first

Why:

- Mature managed primitives
- Native integration with Secrets Manager and IAM
- Reduced cognitive and operational overhead
- Faster V1 delivery

Trade-off:

- Limited portability in V1

Future:

- Multi-cloud and bare metal are V2+ considerations once contracts are proven

## Ingress & API Gateway

Decision: Kong

Why Kong:

- Combines ingress + API gateway
- Built-in authentication, rate limiting, traffic policies
- Reduced integration surface
- Aligns with API-first platform design

Why not Gateway API (V1):

- Defines standards, not a full implementation
- Requires additional controllers (Traefik, Istio, Envoy Gateway)
- Increases operational complexity without immediate benefit

Trade-off:

- Stronger opinionation
- Gateway API compatibility can be layered later

## Secrets Management

Decision: AWS Secrets Manager via External Secrets Operator

Model:

- Applications never access secret stores directly
- Secrets are injected into Kubernetes via operators

Why:

- Fully managed
- Native IAM integration
- No unsealing, HA, or storage management

Why not Vault (V1):

- High operational and governance overhead
- Better suited for multi-cloud or dynamic secrets use cases

Future:

- Vault is a V2 extension when maturity and demand justify it

## CI/CD & GitOps

Decision: GitHub + GitHub Actions + Argo CD

Why:

- Ubiquitous familiarity
- Strong ecosystem integration
- Clear audit trail
- Faster onboarding

Reference: `docs/40-delivery/12_GITOPS_AND_CICD.md`.

Principle: CI workflows must enforce environment separation and controlled promotion. Apply or
deployment steps are gated by explicit human approval for higher environments, and access is scoped
per environment to limit blast radius. The exact tooling can vary, but the separation and manual
gates are non-negotiable.

Principle: Contributors must use local pre-commit hooks as the default preflight gate. CI remains
the source of truth, and hooks exist to reduce avoidable failures and shorten feedback loops.

Principle: Pull requests should surface Terraform plan output automatically to avoid manual
copy/paste and to improve review quality.

Principle: Apply workflows must include a post-apply health check that proves platform readiness
(EKS reachable, Argo synced/healthy, ingress health endpoint). A successful apply without health
verification is incomplete.

Principle: Orphan cleanup is a explicit action. It runs as a human-initiated workflow or
CLI step when needed (not an automatic teardown step), so cleanup intent is always clear and
auditable. Console-only deletion is discouraged.

Principle: V2 introduces environment-to-account boundaries. Each environment can map to a
distinct AWS account, and CI roles are scoped per account. See `docs/60-security/33_IAM_ROLES_AND_POLICIES.md`.

Principle: CI image scanning uses Trivy as the default gate. Prod fails on HIGH/CRITICAL;
dev/test warn unless explicitly tightened.

Principle: No manual `kubectl apply` in steady state. GitOps is the default deployment path;
break-glass changes must be captured in Git immediately after.

Principle: GoldenPath V1 enforces a minimal security floor (documented in the V1 checklist).
Advanced DevSecOps controls are intentionally deferred to V2 to preserve delivery speed.

Principle: GoldenPath defines a CD deployment contract to make promotion and rollback deterministic,
auditable, and consistent across environments.

Principle: The `main` branch only accepts merges from `dev`. Both `dev` and `main` are protected,
and promotion requires passing the dev gate.

Principle: Monitoring and observability data is persisted from day one. Storage add-ons are
required so Prometheus/Grafana/Alertmanager data survives pod restarts and rollout cycles. See
`docs/50-observability/41_STORAGE_AND_PERSISTENCE.md` and `docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md`.

This branching strategy is designed to preserve value already created. It encodes the philosophy
that changes should prove themselves in a real environment before they become the platform record.
The goal is not to claim the only “best” approach, but to keep quality, trust, and delivery
confidence intact as the platform evolves. Teams may adopt improvements, but the core principle is
value preservation.

Out of Scope (V1):

- Atlantis
- Terragrunt
- Tekton
- Multiple CI engines

These introduce opinionated workflows and repo coupling that are deferred until patterns stabilize.

## Infrastructure Access & IAM

Decision: IRSA for controller access (Terraform-managed), SSM for node access.

Why:

- IRSA via Terraform keeps IAM bindings auditable and consistent across environments.
- SSM avoids inbound SSH, centralizes access control, and provides session logs.

Trade-off:

- Slightly more setup up front (OIDC provider, IAM roles, SSM agent/permissions).

V1 Guidance:

- Use Terraform to create IAM roles and service accounts for controllers (e.g., AWS Load Balancer Controller).
- Use SSM for node access; SSH is break-glass only and must be documented.
- When SSH break-glass is enabled, pass the AWS EC2 key pair name via CLI vars or `TF_VAR_ssh_key_name` in CI (never commit `.pem` paths).
- Standardize the AWS Load Balancer Controller service account as `aws-load-balancer-controller`

  in the `kube-system` namespace.

- Create the EKS IAM OIDC provider in Terraform so IRSA works without manual inputs.
- When SSH break-glass is enabled, pass the AWS EC2 key pair name via CLI vars or `TF_VAR_ssh_key_name` in CI (never commit `.pem` paths).
- Third‑party apps get dedicated service accounts and least‑privilege IAM roles (no shared controller roles).
- Audit CI and platform IAM roles periodically (or after stability milestones) using CloudTrail
  and Access Analyzer, then tighten permissions based on actual usage.

## Network Exposure

Decision: Platform tooling is internal-only in higher environments, while client
applications may be externally exposed through the approved ingress path.

Why:

- Protects internal services and reduces attack surface.
- Enforces least privilege and auditable access.
- Keeps production changes predictable and reviewed.

Access expectations:

- Dev can be public for speed.
- Staging/Prod require controlled access (VPN, bastion, or SSM-forwarded tunnels).
- As the platform matures, all environments move to internal-facing ingress.

Implementation detail:

- Kong exposure is controlled via Service annotations in per-environment values.
- Networking rationale and options live in `docs/30-architecture/11_NETWORKING.md`.

## VPN Access

Decision: Start with Pritunl (self-hosted) as the default VPN for controlled
access to internal environments, with an upgrade path to Pritunl Enterprise or
AWS Client VPN as teams scale.

Details: `docs/30-architecture/11_NETWORKING.md`.

## Drift Remediation

Terraform state is the source of truth. If a resource exists in AWS but is not in state, decide:

- Import when the resource matches the desired config and you want Terraform to manage it going forward.
- Delete manually when the resource is an orphan or was created by a different workflow/environment.

After resolving drift, run `terraform plan` to confirm no unexpected changes remain.

## Change Management & Release Workflow

Governance is enforced through process, not just policy.

See also: `docs/30-architecture/07_REPO_DECOUPLING_OPTIONS.md` for planned repository split options.
See also: `docs/30-architecture/08_INGRESS_STRATEGY.md` for the front door decision (Kong+NLB vs ALB).

## Failure Modes & Recovery

We treat failed cluster builds as recoverable events. The default response is:

- Use a unique `name_prefix` per build.
- Tag all resources with a `BuildId`.
- Clean up orphans using `bootstrap/60_tear_down_clean_up/cleanup-orphans.sh`.

Details: `docs/70-operations/10_INFRA_FAILURE_MODES.md`.

Preflight checks are mandatory before bootstrap, especially for higher
environments. This prevents predictable failures (routing, IAM, capacity) and
reduces fire-fighting later. See `bootstrap/00_prereqs/10_eks_preflight.sh`.

## Change Flow

```text

Developer

|

v

Pull Request (Git)

|

v

Automated Validation

- Terraform validate / plan

- Policy checks

- Security scans

|

v

Review & Approval

|

v

Merge to Main

|

v

GitOps Sync (Argo CD)

|

v

Environment Promotion

(dev → test → staging → prod)

```

## Key Rules

- All infrastructure and platform changes flow through Git
- No manual changes to live environments
- Drift is detected and reconciled automatically
- Promotion is explicit and auditable

## Golden Path Interface

## What Is Enforced

- Approved templates
- Standard pipelines
- Approved ingress and auth layers
- Default observability
- Namespace and RBAC conventions

## Enforcement Model

- Golden Path is opt-out
- Deviations require:
  - Explicit documentation
  - Ownership acknowledgement
  - Acceptance of operational burden

This keeps flexibility without chaos.

## Observability & Reliability Governance

## Core Principle

The platform owns reliability of the path.

Applications own reliability of behavior.

## Observability Provisioning Boundary

We keep provisioning simple and deterministic by enforcing a clear boundary:

- **Inside Kubernetes:** Helm + GitOps (kube-prometheus-stack, ConfigMaps).
- **Outside Kubernetes / SaaS:** Terraform (Grafana Cloud, Datadog, PagerDuty).
- **Cloud + cluster-adjacent infrastructure:** Terraform remains the backbone
  (VPC, EKS, IAM, DNS, KMS, state backends).

This prevents drift between Terraform and Helm and keeps observability changes
auditable through Git.

## Platform-Owned Golden Signals

These answer: “Is the platform safe to deploy into?”

| **Signal** | **Examples** |
| --- | --- |
| Latency | Ingress routing latency, control plane responsiveness |
| Traffic | Requests entering cluster, gateway throughput |
| Errors | Ingress 5xx, auth failures |
| Saturation | Node CPU/memory, cluster quotas |

Platform SLO examples:

- Ingress availability ≥ 99.99%
- p95 routing latency ≤ 100ms
- Control plane error rate ≤ 0.1%

If breached:

- Platform changes may freeze
- Platform team owns remediation

## Application-Owned Golden Signals

These answer: “Does the service meet its user contract?”

| **Signal** | **Examples** |
| --- | --- |
| Latency | API response times |
| Traffic | Business request volume |
| Errors | Application failures |
| Saturation | Pod CPU/memory, queue depth |

Application teams define and own SLOs using platform-provided templates.

## Shared Signals (Explicit Ownership)

| **Component** | **Platform Owns** | **Application Owns** |
| --- | --- | --- |
| Ingress | TLS, auth enforcement | Routes, upstream config |
| Autoscaling | HPA mechanics | Resource requests/limits |
| Secrets | Secure delivery | Correct usage |

The platform enables capability; teams own outcomes.

## Container Supply Chain Governance

## Supported Registries (V1)

- GitHub Container Registry (GHCR)
- AWS ECR
- Docker Hub (restricted: official images or approved org namespaces)

Default registry is ECR for platform and reference workloads to minimize egress and align with
IAM. GHCR is supported as an alternative, and Docker Hub is permitted for public base images; teams
may choose another registry with justification.

## Controls by Stage

## 1. Pre-Build (Docker Scout)

- Approved base images
- Pinned digests for production
- Block critical vulnerabilities
- Enforce supported OS versions

## 2. CI Gate (Trivy)

- Image vulnerability scanning
- Optional Dockerfile/IaC checks
- Block on critical vulns
- Warn on high vulns (waiver required)

## 3. Runtime (Snyk)

- Continuous monitoring of deployed images
- Alerts on newly disclosed vulnerabilities
- Defined patch SLAs

## Admission Policy (Cluster)

- Only approved registries allowed
- :latest tag blocked
- Immutable references preferred
- Future: signed images (Cosign)

## Exceptions & Waivers

Waivers must include:

- Reason and vuln ID
- Compensating controls
- Expiry date
- Owner

## Deprecation Policy

## Principles

- No breaking changes without notice
- Deprecation before removal
- Predictable timelines

## Process

1. Deprecation announced (docs + release notes)
2. Minimum 90-day compatibility window
3. Migration guidance provided
4. Feature removed after notice period

This prevents legacy accumulation and platform entropy.

## Ownership Model

| **Area** | **Owner** |
| --- | --- |
| Platform core | Platform team |
| Golden Path | Platform team |
| Shared infra | Platform team |
| Application behavior | Application teams |
| Deviations | Owning team |

Ownership is explicit so responsibility is never ambiguous.

## Golden Path Enforcement

Backstage acts as the platform’s governance interface — surfacing golden paths, ownership,
compliance signals, and documentation — while enforcement occurs through CI, admission control,
and runtime policy.

That single sentence makes your intent unambiguous.

## Out of Scope (V1)

Explicitly excluded:

- Multi-cloud support
- Multiple ingress controllers
- Service mesh
- Advanced traffic shaping
- Custom plugins
- Bespoke pipelines

## Delivery Insights (CI/CD Observability)

Delivery Insights provide visibility into the delivery system itself (build,
package, promotion) to help teams understand where time, risk, and cost
accumulate during deployment. This is an opt-in, V2 capability and does not
mandate tooling or enforce performance targets.

See `docs/40-delivery/19_DELIVERY_INSIGHTS.md` for scope, principles, and architectural
approach.

These are revisited only after patterns are proven and demand is validated.

## Architecture Decision Records (ADRs)

ADRs capture important decisions and their reasoning so context is not lost
over time.

## When to write an ADR

Write an ADR when a decision:

- Changes a default or baseline
- Affects multiple teams, services, or environments
- Has security, cost, or governance implications
- Would be expensive or risky to reverse
- Resolves recurring debate or ambiguity

## Decision artifacts (ADR + Governance + Living doc)

For decisions that affect workflow, security, or platform operations:

- **ADR:** capture the decision, scope, and tradeoffs.
- **Governance update:** codify the rule or expectation for teams.
- **Living doc:** document the current implementation at the time.

This trio keeps decisions, rules, and reality aligned as the platform evolves.

## What ADRs are not

- Not required for every change
- Not a ticketing system
- Not a replacement for code review

## How decisions evolve

- Do not edit accepted ADRs to change history
- Create a new ADR that supersedes the old one

## ADR status values

- Proposed
- Accepted
- Deprecated
- Superseded

See `docs/adrs/README.md` for the template and `docs/adrs/01_adr_index.md` for the
current ADR list.

## Final Statement

This platform optimizes for:

- Clarity over flexibility
- Defaults over decisions
- Systems over heroics
- Governance over tribal knowledge

Constraints are intentional.

They are what make scale possible.

This is not a toolset.

It is a system designed to grow without collapsing under its own weight.

If you want, next we can:

- Extract an executive 1-page version
- Create a Platform Constitution
- Or map this governance directly to Backstage scorecards and policy checks

Just tell me where you want to go next.
