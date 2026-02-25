---
id: GOV-0017-tdd-and-determinism
title: TDD and Determinism Policy
type: governance
owner: platform-team
status: active
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - 2026-01-26-session-capture-tdd-quality-gate
  - 2026-01-28-agentic-graph-rag-phase0
  - 26_AI_AGENT_PROTOCOLS
  - 27_TESTING_QUICKSTART
  - ADR-0162
  - ADR-0162-determinism-protection
  - ADR-0164-agent-trust-and-identity
  - ADR-0182-tdd-philosophy
  - CL-0190-tdd-foundation-and-testing-stack
  - EC-0013-agent-context-architecture
  - EC-0015-backstage-tdd-parity-plan
  - GOV-0016-testing-stack-matrix
  - PRD-0009-integration-test-gap-closure
  - session-2026-01-26-tdd-foundation-and-testing-stack
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-01-26
review_date: 2026-07-26
---

# GOV-0017: TDD and Determinism Policy

## Purpose

This policy defines the testing and determinism requirements for all code changes in the GoldenPath IDP. It establishes what must be tested, how tests are structured, and how determinism is preserved across the platform.

---

## Core Principle

> **"Nothing that generates infrastructure, parses config, or emits scaffolds may change without tests."**

Tests are not documentation. Tests are **executable contracts** that:
1. Define expected behavior before implementation
2. Catch regressions immediately
3. Enable safe refactoring
4. Preserve determinism across agent and human contributors

---

## Scope of Determinism

The following components are **determinism-critical** and require test coverage before any modification:

| Component | Examples | Why Critical |
|-----------|----------|--------------|
| **Parsers** | YAML frontmatter, config loaders, CLI arg parsers | Incorrect parsing corrupts downstream state |
| **Generators** | Doc scaffolds, template renderers, code generators | Output drift breaks consumers |
| **Metadata Engines** | `standardize_metadata.py`, `validate_metadata.py` | Metadata is the source of truth |
| **Schemas** | `schemas/*.yaml`, JSON schemas | Schema changes break validation |
| **Templates** | Jinja2, Helm charts, Backstage scaffolder | Template bugs multiply across outputs |
| **Bootstrap Logic** | `bootstrap/*.sh`, init scripts | Bootstrap errors are expensive to recover |

---

## Tiered Test Strategy

### Tier 1: Unit / Contract Tests (Required)

Every function that transforms data must have a unit test.

| File Type | Test Location | Framework |
|-----------|---------------|-----------|
| `scripts/*.py` | `tests/unit/test_*.py` | pytest |
| `scripts/*.sh` | `tests/bats/test_*.bats` | bats-core |
| `modules/**/*.tf` | `modules/*/tests/*.tftest.hcl` | terraform test |

**Contract:** Input → Expected Output

```python
def test_parse_frontmatter_extracts_id():
    content = "---\nid: DOC-001\ntitle: Test\n---\n# Content"
    result = parse_frontmatter(content)
    assert result["id"] == "DOC-001"
```

### Tier 2: Golden Output Tests (Required for Generators)

For any code that **generates files**, assert the output matches a known-good snapshot.

**Purpose:** Golden output tests are the primary guardrail against "agent helpfulness" - the tendency of AI agents to make well-intentioned but unauthorized improvements to generated outputs.

#### Philosophy: Why Golden Tests Matter

Golden tests embody a trust model where **humans are the source of truth** for generated output correctness. The philosophy rests on three pillars:

1. **Deterministic Serialization**: Generators must produce byte-identical output across runs:
   - Sorted keys (`sort_keys=True` in JSON, alphabetical YAML)
   - No timestamps, random IDs, or environment-dependent values
   - Consistent whitespace and formatting

2. **Human-Approved Blessing**: Golden files are "blessed" artifacts that represent human-verified correct output:
   - A human reviews the generated output and judges it correct
   - The blessed file becomes the contract - any deviation is a regression
   - Updates require explicit human approval with documented rationale

3. **Output Drift Detection**: Golden tests catch "helpful" changes that would otherwise slip through:
   - AI agents adding "improvements" to templates
   - Refactoring that subtly changes output format
   - Dependency updates that alter generation behavior

**The Blessing Ceremony:** When you bless a golden file, you're making a statement: "This output is correct. Any future deviation from this exact output is a bug until proven otherwise."

#### Standard Parser CLI Contract

All parsers that generate output files MUST support this interface for golden testing:

```bash
python scripts/<parser>.py \
    --request <path/to/request.yaml> \
    --out <output_dir> \
    --format stable \
    --dry-run
```

| Flag | Purpose |
|------|---------|
| `--request` | Path to single request YAML file |
| `--out` | Output directory for generated files |
| `--format stable` | Deterministic output: sorted keys, no timestamps, no random values |
| `--dry-run` | Generate files only, no apply/side-effects |

**Why this matters:** Golden tests call parsers via subprocess using this exact interface. Non-compliant parsers cannot be golden-tested.

#### Golden Test Example

```python
def test_secret_parser_matches_golden(run_parser, compare_directories, clean_tmp, golden_fixtures):
    """Parser output must match blessed golden files."""
    request = golden_fixtures["inputs"] / "SECRET-0001.yaml"
    expected = golden_fixtures["expected"] / "secret/SECRET-0001"
    actual = clean_tmp("secret/SECRET-0001")

    result = run_parser("scripts/secret_request_parser.py", request, actual)
    assert result.returncode == 0, f"Parser failed: {result.stderr}"

    compare_directories(expected, actual)
```

**Golden output locations:**

- `tests/golden/fixtures/inputs/` - Input request fixtures
- `tests/golden/fixtures/expected/` - Blessed output snapshots
- `.tmp/golden/` - Generated outputs during test runs

**Blessing new golden outputs:**

```bash
# 1. Run parser to generate outputs
python scripts/<parser>.py --request tests/golden/fixtures/inputs/FOO-0001.yaml \
    --out .tmp/golden/foo/FOO-0001 --format stable --dry-run

# 2. Review outputs manually
# 3. Copy to expected directory
cp -r .tmp/golden/foo/FOO-0001 tests/golden/fixtures/expected/foo/

# 4. Commit with explanation
```

**Update protocol:** Golden files may only be updated when:
1. The change is intentional and documented
2. A human has reviewed the diff
3. The PR description explains why the output changed

### Tier 3: Integration Tests (Selective)

Integration tests validate component interactions. Required for:
- API endpoints
- Database operations
- External service integrations
- Multi-script workflows

```python
def test_ecr_sync_pushes_to_registry(mock_aws):
    result = ecr_sync(source="local", target="aws")
    assert mock_aws.ecr.image_exists("backstage:latest")
```

---

## AI Agent Constraints

AI agents (Claude, Copilot, etc.) operating in this repository MUST:

1. **Run `make test` before pushing** any code change
2. **Add tests alongside code** - no feature without a test
3. **Never modify golden files** without explicit human approval
4. **Flag coverage drops** - if a change would decrease coverage, pause and ask
5. **Honor SKIP-TDD** exceptions only when explicitly approved by a human

### Agent Test Workflow

```
1. Write/update test first (or simultaneously)
2. Run `make test` locally
3. If TDD Gate fails → add missing test
4. If tests fail → fix code, not test (unless test is wrong)
5. If coverage drops → investigate before proceeding
```

---

## Hotfix Policy

Emergency fixes may bypass the full test cycle with these constraints:

| Condition | Requirement |
|-----------|-------------|
| Severity | Must be P0 (production down) or security critical |
| Approval | Requires human approval with `hotfix` label |
| Follow-up | Test MUST be added within 24 hours |
| Tracking | Create issue linking hotfix PR to follow-up test PR |

**Hotfix without follow-up test = technical debt.** The test PR must reference the original hotfix.

---

## Blast Radius Control

Large changes require additional scrutiny:

| Condition | Requirement |
|-----------|-------------|
| >80 files changed | Requires `blast-radius-approved` label |
| Critical paths touched | Determinism Guard runs full test suite |
| Schema changes | Schema validation runs automatically |

**Critical paths:**
- `modules/`
- `scripts/`
- `bootstrap/`
- `.github/workflows/`
- `envs/*.tf`
- `schemas/`

---

## Enforcement Mechanisms

| Mechanism | Trigger | Action |
|-----------|---------|--------|
| **TDD Gate** (`.github/workflows/tdd-gate.yml`) | `.py` or `.sh` file changed | Blocks PR if no corresponding test file |
| **Determinism Guard** (`.github/workflows/determinism-guard.yml`) | >80 files OR critical paths | Runs pytest + bats, validates schemas |
| **Pre-commit Hooks** (`.pre-commit-config.yaml`) | Every commit | Lints with ruff, shellcheck, shfmt |
| **Makefile Targets** | Manual / CI | `make test`, `make lint`, `make validate-schemas` |
| **Coverage Thresholds** | pytest-cov | Fails if below target (60% V1, 80% V1.1) |

### CI Workflow Matrix

| Workflow | Runs On | Checks |
|----------|---------|--------|
| `tdd-gate.yml` | PR with code changes | Test file existence |
| `determinism-guard.yml` | PR with >80 files or critical paths | Full test suite, schema validation |
| `python-tests.yml` | PR with `.py` changes | pytest with coverage |
| `pre-commit.yml` | All PRs | Linting, formatting, hooks |

---

## Coverage Targets

| Layer | V1 Target | V1.1 Target |
|-------|-----------|-------------|
| Python scripts | 60% | 80% |
| Shell scripts | 40% | 60% |
| Backstage | 50% | 70% |
| Terraform | 30% | 50% |

Coverage is enforced via `pytest-cov --fail-under` in CI.

---

## Exception Process

To skip TDD requirements:

1. Add `SKIP-TDD:reason` to PR description
2. Requires explicit human approval
3. Must document why tests cannot be written
4. Creates follow-up issue for test addition

Valid reasons:
- Pure documentation change (use `docs-only` label instead)
- Emergency hotfix (see Hotfix Policy)
- Third-party code with its own test suite

Invalid reasons:
- "Tests will be added later"
- "This is a small change"
- "The code is simple"

---

## Quick Reference

### Commands

```bash
make test              # Run all tests (Python + Shell)
make test-python       # Run pytest only
make test-shell        # Run bats only
make lint              # Run all linters
make validate-schemas  # Validate YAML schemas
```

### Test File Naming

| Source File | Test File |
|-------------|-----------|
| `scripts/foo.py` | `tests/unit/test_foo.py` |
| `scripts/bar.sh` | `tests/bats/test_bar.bats` |
| `modules/eks/main.tf` | `modules/eks/tests/eks.tftest.hcl` |

---

## Related Documents

- [ADR-0182: TDD Philosophy](../../adrs/ADR-0182-tdd-philosophy.md) - Architectural decision
- [GOV-0016: Testing Stack Matrix](./GOV-0016-testing-stack-matrix.md) - Tool definitions
- [27_TESTING_QUICKSTART](../../80-onboarding/27_TESTING_QUICKSTART.md) - Setup guide
- [26_AI_AGENT_PROTOCOLS](../../80-onboarding/26_AI_AGENT_PROTOCOLS.md) - Agent requirements

---

## Revision History

| Version | Date       | Author          | Changes                                                              |
|---------|------------|-----------------|----------------------------------------------------------------------|
| 1.0     | 2026-01-26 | Claude Opus 4.5 | Initial creation                                                     |
| 1.1     | 2026-01-26 | Claude Opus 4.5 | Added standard parser CLI contract for golden tests                  |
| 1.2     | 2026-01-28 | Claude Opus 4.5 | Added golden test philosophy section (determinism, blessing, drift)  |
