---
id: GOV-0016-testing-stack-matrix
title: Testing Stack Matrix
type: governance
owner: platform-team
status: draft
domain: platform-core
applies_to: []
lifecycle: draft
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - 2026-01-26-session-capture-tdd-quality-gate
  - 26_AI_AGENT_PROTOCOLS
  - 27_TESTING_QUICKSTART
  - ADR-0162-determinism-protection
  - ADR-0180-argocd-orchestrator-contract
  - ADR-0182-tdd-philosophy
  - CL-0190-tdd-foundation-and-testing-stack
  - EC-0015-backstage-tdd-parity-plan
  - GOV-0015-build-pipeline-testing-matrix
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

# GOV-0016: Testing Stack Matrix

## Purpose

Define the standard testing tools, frameworks, and practices for all code in the GoldenPath IDP. This matrix ensures consistency, reproducibility, and determinism across the platform and application layers.

## Scope

- **Infra/Platform Repo**: `goldenpath-idp-infra` (Python, Shell, Terraform, K8s YAML)
- **Application Repo**: `goldenpath-idp-backstage` (TypeScript, React, Node.js)

---

# Part 1: Infrastructure / Platform Stack

## Tool Definitions

| Tool | Category | Purpose |
|------|----------|---------|
| **pytest** | Test Framework | Python unit and integration testing. Supports fixtures, parametrization, and plugins. |
| **pytest-cov** | Coverage | Measures code coverage for Python. Reports lines, branches, and functions tested. |
| **bats-core** | Test Framework | Bash Automated Testing System. Unit tests for shell scripts. |
| **ruff** | Linter + Formatter | Ultra-fast Python linter (replaces flake8, isort, pyupgrade) and formatter (Black-compatible). Written in Rust. |
| **mypy** | Type Checker | Static type analysis for Python. Catches type errors before runtime. Requires type hints. |
| **shellcheck** | Linter | Static analysis for shell scripts. Finds bugs, security issues, and portability problems. |
| **shfmt** | Formatter | Formats shell scripts consistently. Enforces indentation and style. |
| **terraform test** | Test Framework | Native Terraform testing. Validates module behavior with assertions. |
| **tflint** | Linter | Terraform linter. Catches errors, enforces best practices, validates provider-specific rules. |
| **kubeconform** | Validator | Validates Kubernetes manifests against API schemas. Fast, supports CRDs. |
| **kuttl** | Test Framework | Kubernetes Test TooL. Declarative E2E testing for K8s resources. |
| **yamllint** | Linter | YAML syntax and style checker. |
| **tox** | Test Orchestrator | Runs tests in isolated virtualenvs across multiple Python versions and dependency sets. |

## Infrastructure Testing Matrix

| Layer | Test Framework | Linter | Formatter | Type Checker | Coverage | V1 | V2 |
|-------|----------------|--------|-----------|--------------|----------|----|----|
| **Python scripts** | pytest | ruff | ruff | mypy | pytest-cov | Yes | Yes |
| **Shell scripts** | bats-core | shellcheck | shfmt | - | - | Yes | Yes |
| **Terraform modules** | terraform test | tflint | terraform fmt | - | - | Yes | Yes |
| **K8s manifests** | kuttl | kubeconform | yamllint | - | - | - | Yes |
| **Multi-env Python** | tox -> pytest | - | - | - | - | - | Yes |

## Infrastructure CI Pipeline

```
+-------------+     +-------------+     +-------------+     +-------------+
|   Lint      |---->|   Test      |---->|  Coverage   |---->|   Report    |
|             |     |             |     |             |     |             |
| - ruff      |     | - pytest    |     | - pytest-cov|     | - JUnit XML |
| - shellcheck|     | - bats-core |     | - fail < 70%|     | - Coverage  |
| - tflint    |     | - tf test   |     |             |     | - Summary   |
| - kubeconform     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
```

## Python Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_platform_health.py
│   ├── test_validate_metadata.py
│   └── test_scaffold_doc.py
├── integration/
│   └── test_ecr_sync.py
└── bats/
    ├── helpers/
    │   └── common.bash
    ├── test_deploy_backstage.bats
    └── test_ecr_build_push.bats
```

## Terraform Test Structure

```
modules/
├── eks/
│   ├── main.tf
│   ├── variables.tf
│   └── tests/
│       └── eks.tftest.hcl
├── rds/
│   └── tests/
│       └── rds.tftest.hcl
└── vpc/
    └── tests/
        └── vpc.tftest.hcl
```

---

# Part 2: Application Stack (Backstage)

## Tool Definitions

| Tool | Category | Purpose |
|------|----------|---------|
| **Jest** | Test Framework | JavaScript/TypeScript testing. Supports mocking, snapshots, and async testing. |
| **Testing Library** | Component Testing | Tests React components from user perspective. Query by role, text, label. |
| **supertest** | API Testing | HTTP assertions for Express/Node.js backend routes. |
| **Playwright** | E2E Framework | Cross-browser end-to-end testing. Supports Chromium, Firefox, WebKit. |
| **ESLint** | Linter | JavaScript/TypeScript linter. Finds problems, enforces style rules. |
| **Prettier** | Formatter | Opinionated code formatter. Consistent style across codebase. |
| **tsc** | Type Checker | TypeScript compiler. Catches type errors at compile time. |
| **jest-junit** | Reporter | Outputs Jest results in JUnit XML format for CI parsing. |
| **Codecov** | Coverage | Coverage reporting and tracking service. Enforces coverage thresholds. |

## Application Testing Matrix

| Layer | Test Framework | Linter | Formatter | Type Checker | Coverage | V1 | V2 |
|-------|----------------|--------|-----------|--------------|----------|----|----|
| **React components** | Jest + Testing Library | ESLint | Prettier | tsc | jest --coverage | Yes | Yes |
| **Backend API routes** | Jest + supertest | ESLint | Prettier | tsc | jest --coverage | Yes | Yes |
| **Backstage plugins** | Jest | ESLint | Prettier | tsc | jest --coverage | Yes | Yes |
| **E2E browser tests** | Playwright | - | - | tsc | - | Yes | Yes |
| **Scaffolder templates** | Jest (validation) | yamllint | - | - | - | - | Yes |

## Application CI Pipeline

```
+-------------+     +-------------+     +-------------+     +-------------+     +-------------+
|   Lint      |---->|  Type Check |---->|    Test     |---->|     E2E     |---->|   Report    |
|             |     |             |     |             |     |             |     |             |
| - ESLint    |     | - tsc       |     | - Jest      |     | - Playwright|     | - JUnit XML |
| - Prettier  |     |   --noEmit  |     | - supertest |     |   (on build)|     | - Codecov   |
|             |     |             |     | - Testing Lib|    |             |     | - Summary   |
+-------------+     +-------------+     +-------------+     +-------------+     +-------------+
```

## Backstage Test Structure

```
packages/
├── app/
│   ├── src/
│   │   ├── App.tsx
│   │   └── App.test.tsx           # Component test
│   └── e2e-tests/
│       └── app.test.ts            # Playwright E2E
├── backend/
│   └── src/
│       ├── plugins/
│       │   └── catalog/
│       │       ├── router.ts
│       │       └── router.test.ts # API test
│       └── index.ts
└── plugins/
    └── my-plugin/
        └── src/
            ├── components/
            │   ├── MyComponent.tsx
            │   └── MyComponent.test.tsx
            └── api/
                ├── client.ts
                └── client.test.ts
```

---

# Coverage Thresholds

| Repo | V1 Target | V2 Target | Enforcement |
|------|-----------|-----------|-------------|
| **Infra (Python)** | 60% | 80% | pytest-cov --fail-under |
| **Infra (Shell)** | 40% | 60% | Manual review |
| **Backstage** | 50% | 70% | jest --coverageThreshold |

---

# Pre-commit Hooks

## Infrastructure Repo

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.10.0.1
    hooks:
      - id: shellcheck

  - repo: https://github.com/scop/pre-commit-shfmt
    rev: v3.8.0-1
    hooks:
      - id: shfmt
        args: ["-i", "2", "-ci"]

  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.88.0
    hooks:
      - id: terraform_fmt
      - id: terraform_tflint
      - id: terraform_validate

  - repo: https://github.com/yannh/kubeconform
    rev: v0.6.4
    hooks:
      - id: kubeconform
        args: ["-strict", "-ignore-missing-schemas"]
```

## Application Repo

```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
        additional_dependencies:
          - eslint@8.56.0
          - typescript

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, yaml, markdown]
```

---

# Quick Reference

## Makefile Targets (Recommended)

Use Make targets for consistent, portable execution across local and CI environments.

### Infrastructure Repo

| Command | Description |
|---------|-------------|
| `make test` | Run all tests (Python + Shell) |
| `make test-matrix` | Run full test matrix (all tiers) - fast iteration |
| `make quality-gate` | Full CI gate (schemas + tests + certification) |
| `make certify-scripts` | Generate proofs and verify script certification |
| `make test-python` | Run Python tests (emits junit.xml) |
| `make test-shell` | Run Shell tests with bats |
| `make test-unit` | Run unit tests only (Tier 1) |
| `make test-contract` | Run contract tests only (Tier 1) |
| `make test-golden` | Run golden output tests (Tier 2) |
| `make test-integration` | Run integration tests (Tier 3) |
| `make validate-schemas` | Validate schemas against JSON Schema meta-schema |
| `make validate-contracts` | Validate request fixtures against their schemas |
| `make lint` | Run all linters (pre-commit) |

### Application Repo (Backstage)

| Command | Description |
|---------|-------------|
| `make ci-all` | Full CI pipeline (lint + test + build) |
| `make ci-lint` | Run TypeScript, ESLint, Prettier checks |
| `make ci-test` | Run tests with coverage |
| `make ci-build` | Build backend artifacts |
| `make ci-docker` | Build Docker image locally |

## Raw CLI Commands (Without Make)

| Repo | Command | Description |
|------|---------|-------------|
| Infra | `pytest tests/` | Run Python tests |
| Infra | `pytest --cov=scripts` | With coverage |
| Infra | `bats tests/bats/` | Run shell tests |
| Infra | `terraform test` | Run Terraform tests |
| Backstage | `yarn test` | Run Jest tests |
| Backstage | `yarn test --coverage` | With coverage |
| Backstage | `yarn e2e` | Run Playwright |

## V2 Commands (with tox)

| Command | Description |
|---------|-------------|
| `tox` | Run all envs (py310, py311, py312, lint) |
| `tox -e py311` | Run Python 3.11 only |
| `tox -e lint` | Run linters only |
| `tox -e ci` | Fast CI env |

## CI Usage

In GitHub Actions workflows, use Make targets for portability:

```yaml
# Infrastructure repo
- name: Run quality gate
  run: make quality-gate

# Backstage repo
- name: Run CI pipeline
  run: make ci-all
```

This ensures CI behavior matches local development and enables easy migration between CI platforms.

---

# Revision History

| Version | Date       | Author          | Changes                                |
|---------|------------|-----------------|----------------------------------------|
| 1.0     | 2026-01-26 | Claude Opus 4.5 | Initial creation                       |
| 1.1     | 2026-01-26 | Claude Opus 4.5 | Added Makefile targets for portable CI |
