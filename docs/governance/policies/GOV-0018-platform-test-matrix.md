---
id: GOV-0018-platform-test-matrix
title: Platform Test Matrix and Staged Implementation
type: governance
owner: platform-team
status: draft
domain: platform-core
applies_to: []
lifecycle: draft
exempt: false
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: medium
schema_version: 1
relates_to:
  - 2026-02-01-phase1-cicd-consolidation
  - ADR-0162
  - ADR-0162-determinism-protection
  - ADR-0182-tdd-philosophy
  - GOV-0015-build-pipeline-testing-matrix
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: high
  potential_savings_hours: 0.0
effective_date: 2026-02-01
review_date: 2026-08-01
related_adrs:
  - ADR-0162
  - ADR-0182
related_govs:
  - GOV-0015
  - GOV-0016
  - GOV-0017
---

# GOV-0018: Platform Test Matrix and Staged Implementation

## Purpose

Define a deterministic, staged testing matrix that prioritizes fast sanity
coverage first, then deep integration, then long-run E2E and security.
This matrix complements:

- **GOV-0015** (build pipeline testing matrix)
- **GOV-0016** (testing stack matrix)
- **GOV-0017** (TDD + determinism policy)

## Scope

Applies to platform systems with high operational impact:

- **RAG / GraphRAG** (retrieval + graph + answer contract)
- **Backstage** (app + CI)
- **CI / Build** (workflows + artifacts)
- **Infra** (Terraform + bootstrap)
- **Security** (SAST, SBOM, vuln scanning)

## Test Tier Definitions

| Tier | Goal | When | Signal |
|------|------|------|--------|
| **T0 Sanity** | "Not broken" | Every PR | Fast, shallow pass/fail |
| **T1 Unit** | Logic correctness | Every PR | Deterministic, isolated |
| **T2 Integration** | Component interoperability | Nightly + pre-release | End-to-end within a subsystem |
| **T3 E2E / Policy** | Org-level confidence | Weekly + release | Cross-system, policy enforced |

## Matrix (V1 Target)

| System | T0 Sanity | T1 Unit | T2 Integration | T3 E2E / Policy | Evidence |
|--------|-----------|---------|----------------|-----------------|----------|
| **RAG / GraphRAG** | `scripts.rag.cli query` returns cited answer or "unknown" | Chunker/indexer/retriever unit tests | Index build + query integration | Answer contract + graph-linked evidence | test logs + artifacts |
| **Backstage** | Server boots + health endpoint | Jest unit tests + coverage | API + catalog sync workflow | User workflow (golden path) | JUnit + coverage + logs |
| **CI / Build** | Lint + build baseline | Workflow unit checks | Docker build + artifact upload | Promote + guardrails pass | workflow summary |
| **Infra** | `make plan` baseline | Terraform unit tests | Bootstrap + verify flow | Teardown + recovery | Terraform logs |
| **Security** | Gitleaks + Trivy presence | Rule checks | SBOM + SARIF | Policy gates enforced | SARIF + SBOM |

## Staged Implementation Plan

### Stage 1: T0 Sanity (P0)
**Goal:** Fast PR gate with minimal surface area but high signal.

Required:
- T0 sanity for each system (5-10 total checks)
- Fail fast on any missing evidence
- Outputs recorded in CI summary

### Stage 2: T2 Integration (P1)
**Goal:** Ensure components work together.

Required:
- RAG pipeline integration (index -> retrieve -> answer contract)
- Backstage workflow integration (catalog sync + API health)
- Infra bootstrap + verify (non-destructive)

### Stage 3: T3 E2E / Policy (P2)
**Goal:** Enforced policy and realistic user workflows.

Required:
- Policy gates (security + governance)
- Golden path workflows (onboarding + deploy)
- Weekly scheduled runs

## Governance Rules

- T0 sanity must run on every PR.
- T1 unit tests must run before merge.
- T2 integration must run nightly or before release.
- T3 E2E must run on a schedule and before major releases.

## Exit Criteria (V1)

- All T0 checks implemented and passing.
- At least one T2 integration path per system.
- Evidence artifacts stored in CI for audit.
