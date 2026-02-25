---
id: 27_TESTING_QUICKSTART
title: Testing Quickstart Guide
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 00_DOC_INDEX
  - 24_PR_GATES
  - 25_DAY_ONE_CHECKLIST
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0162
  - ADR-0162-determinism-protection
  - ADR-0182-tdd-philosophy
  - AGENT_FIRST_BOOT
  - CL-0190-tdd-foundation-and-testing-stack
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
  - session-2026-01-26-tdd-foundation-and-testing-stack
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Testing Quickstart Guide

Doc contract:

- Purpose: Get contributors running tests locally within 5 minutes.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/adrs/ADR-0182-tdd-philosophy.md, docs/governance/policies/GOV-0016-testing-stack-matrix.md

This guide helps you set up and run the testing stack for GoldenPath IDP.
All code changes require tests per ADR-0182.

## TDD Philosophy

> **"No feature without a test. No merge without green."**

Tests are executable contracts that define expected behavior before
implementation. See [ADR-0182](../adrs/ADR-0182-tdd-philosophy.md) for the
full philosophy.

## Quick Setup (5 minutes)

### 1. Install dependencies

```bash
# Python testing tools
pip install pytest pytest-cov pyyaml

# Shell testing tools (macOS)
brew install bats-core

# Shell testing tools (Ubuntu/Debian)
sudo apt-get install bats

# Pre-commit hooks
pip install pre-commit
pre-commit install
```

### 2. Verify installation

```bash
# Check tools are available
pytest --version
bats --version
pre-commit --version
```

### 3. Run all tests

```bash
make test
```

## Test Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests (Python + Shell) |
| `make test-python` | Run Python tests with pytest |
| `make test-shell` | Run Shell tests with bats |
| `make test-unit` | Run unit tests only (Tier 1) |
| `make test-contract` | Run contract tests only (Tier 1) |
| `make test-golden` | Run golden output tests (Tier 2) |
| `make test-integration` | Run integration tests (Tier 3) |
| `make validate-schemas` | Validate YAML schemas |
| `make lint` | Run all linters via pre-commit |

## Running Tests Directly

### Python Tests (pytest)

```bash
# Run all Python tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Run specific test file
pytest tests/unit/test_specific.py

# Run tests matching pattern
pytest tests/ -k "test_metadata"
```

### Shell Tests (bats)

```bash
# Run all bats tests
bats tests/bats/*.bats

# Run specific test file
bats tests/bats/test_example.bats

# Run with verbose output
bats tests/bats/*.bats --verbose-run
```

## Test Structure (Tiered)

Per [GOV-0017](../governance/policies/GOV-0017-tdd-and-determinism.md), tests are organized by tier:

```text
tests/
  conftest.py              # Shared pytest fixtures (auto-loaded)

  unit/                    # Tier 1: Unit tests
    governance/            # Metadata, validation scripts
    scripts/               # Numbered script tests

  contract/                # Tier 1: Contract tests
    test_*_contract.py     # Input/output contract validation
    fixtures/
      requests/            # Request fixtures (valid/invalid)

  golden/                  # Tier 2: Golden output tests
    test_*_golden.py       # Snapshot comparison tests
    fixtures/
      inputs/              # Test inputs
      expected/            # Golden snapshots (immutable)

  integration/             # Tier 3: Integration tests
    test_*_workflow.py     # End-to-end workflow tests

  bats/                    # Shell tests
    helpers/
      common.bash          # Shared bats helpers
    test_*.bats            # Shell tests
```

**Tier Requirements:**

| Tier | Tests | When Required |
|------|-------|---------------|
| Tier 1 | Unit + Contract | Every code change |
| Tier 2 | Golden | Code that generates files |
| Tier 3 | Integration | Multi-component workflows |

## Writing Tests

### Python Test Template

```python
"""Tests for my_module."""

import pytest
from scripts.my_module import my_function

class TestMyFunction:
    """Tests for my_function."""

    def test_returns_expected_value(self):
        """Test that my_function returns expected output."""
        result = my_function("input")
        assert result == "expected"

    def test_handles_edge_case(self):
        """Test edge case handling."""
        result = my_function("")
        assert result is None

    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that requires more time (skipped by default)."""
        # Run with: pytest --runslow
        result = expensive_operation()
        assert result.success
```

### Shell Test Template

```bash
#!/usr/bin/env bats

load 'helpers/common'

setup() {
  export TEST_TEMP_DIR=$(mktemp -d)
}

teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

@test "my_script: returns success on valid input" {
  run bash scripts/my_script.sh --valid
  assert_success
}

@test "my_script: outputs expected message" {
  run bash scripts/my_script.sh --help
  assert_success
  assert_output_contains "Usage:"
}

@test "my_script: fails on invalid input" {
  run bash scripts/my_script.sh --invalid
  assert_failure
}
```

## Using Fixtures

The `tests/conftest.py` provides shared fixtures:

```python
def test_with_temp_dir(temp_dir):
    """temp_dir is auto-cleaned after test."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("hello")
    assert test_file.exists()

def test_with_yaml_file(create_yaml_file):
    """Factory fixture for creating YAML files."""
    yaml_file = create_yaml_file("config.yaml", {"key": "value"})
    assert yaml_file.exists()

def test_with_mock_aws(mock_aws_credentials):
    """AWS credentials are mocked for this test."""
    # AWS_ACCESS_KEY_ID etc. are set to "testing"
    pass
```

Available fixtures:

| Fixture | Description |
|---------|-------------|
| `project_root` | Path to project root |
| `scripts_dir` | Path to scripts/ |
| `temp_dir` | Auto-cleaned temporary directory |
| `temp_file` | Auto-cleaned temporary file |
| `sample_yaml_content` | Sample YAML string |
| `sample_frontmatter` | Sample frontmatter dict |
| `mock_aws_credentials` | Mocked AWS credentials |
| `mock_github_env` | Mocked GitHub Actions env |
| `create_yaml_file` | Factory for YAML files |
| `create_markdown_file` | Factory for MD files |

## CI Workflows

### TDD Gate (`tdd-gate.yml`)

Ensures every Python/Shell change has a corresponding test file.

**Triggered by:** PRs modifying `.py`, `.sh` files

**Bypass:** Add `SKIP-TDD:reason` to PR description for exceptional cases.

### Determinism Guard (`determinism-guard.yml`)

Protects against large or dangerous changes.

**Features:**

- Blast radius check (>80 files requires `blast-radius-approved` label)
- Critical path detection (modules/, scripts/, bootstrap/, workflows)
- Schema validation for YAML schemas
- Test execution for critical path changes

## Coverage Targets

| Layer | V1 Target | V1.1 Target |
|-------|-----------|-------------|
| Python scripts | 60% | 80% |
| Shell scripts | 40% | 60% |
| Backstage | 50% | 70% |

## Troubleshooting

### pytest not found

```bash
pip install pytest
# or if using virtual env
source venv/bin/activate && pip install pytest
```

### bats not found

```bash
# macOS
brew install bats-core

# Ubuntu/Debian
sudo apt-get install bats

# From source
git clone https://github.com/bats-core/bats-core.git
cd bats-core && ./install.sh /usr/local
```

### Tests pass locally but fail in CI

1. Check Python version matches CI (3.11)
2. Ensure all dependencies are in `requirements.txt`
3. Check for environment-specific paths or credentials

### Pre-commit hooks not running

```bash
pre-commit install
pre-commit run --all-files  # Verify hooks work
```

## Related Documentation

- [Determinism Protection (ADR-0162)](../adrs/ADR-0162-determinism-protection.md) - Strategic philosophy
- [TDD Philosophy (ADR-0182)](../adrs/ADR-0182-tdd-philosophy.md) - TDD mechanics
- [TDD and Determinism (GOV-0017)](../governance/policies/GOV-0017-tdd-and-determinism.md) - Enforcement policy
- [Testing Stack Matrix (GOV-0016)](../governance/policies/GOV-0016-testing-stack-matrix.md) - Tool definitions
- [PR Gates](./24_PR_GATES.md)
- [AI Agent Protocols](./26_AI_AGENT_PROTOCOLS.md)
