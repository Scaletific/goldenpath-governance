---
id: GOV-0040-secrets-catalog-policy
title: Secrets Cataloging Policy (Backstage)
type: policy
domain: security
risk_profile:
  production_impact: low
  security_risk: access
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - GOV-0039-secret-scanning-policy
  - GOV-0042-resource-tagging
  - ADR-0138
  - ADR-0139
  - METADATA_STRATEGY
tags:
  - governance
  - security
  - secrets
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
aliases:
  - 11_SECRETS_CATALOG_POLICY
---

# Secrets Cataloging Policy (Backstage)

Purpose: define when secrets infrastructure is first-class in Backstage and how
to model it without catalog sprawl.

## What is first-class (Resource)

Catalog AWS Secrets Manager resources only when they are:

- shared across services or teams
- medium+ risk or security-critical
- long-lived platform secrets (OIDC clients, shared integrations)
- required for onboarding or audits

## What is not first-class

Do not create a Backstage entity per `ExternalSecret` or per app secret. Link
app-specific secrets from the service entity instead.

## Required Backstage model (V1)

- **System**: `secrets-platform`
- **Component**: `external-secrets-operator`
- **Resources**: `aws-secrets-manager-dev`, `aws-secrets-manager-test`,
  `aws-secrets-manager-staging`, `aws-secrets-manager-prod`

Relationships:

- component -> system
- resource -> system
- resource -> ownedBy (platform-team / security-team)

## Terraform representation (alignment)

Every Secrets Manager resource must include:

- `goldenpath.idp/id` (unique per instance, per environment)
- `goldenpath.idp/logical_id` (shared logical grouping)
- `Owner`, `Environment`, and standard tags per
  `docs/governance/GOV-0042-resource-tagging.md`

## Coupled updates

If tag keys change, update this policy and
`docs/governance/GOV-0042-resource-tagging.md` together in the same PR.

## Enforcement

- Reviewers must reject catalog entries that violate the scope rules above.
- Catalog entities must map to Terraform-managed resources (no manual drift).
