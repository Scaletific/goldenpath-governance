---
id: PROMPT-0011
title: Script Certification Workflow
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-idp-infra
relates_to:
  - ADR-0146
  - ADR-0147
  - ADR-0197
  - GOV-0017
  - PROMPT-0005
created: 2026-02-14
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are a platform engineer certifying scripts through the maturity promotion pipeline with correct test coverage and naming conventions.

## Context

The GoldenPath IDP uses a schema-driven script certification model (ADR-0146). Scripts progress through maturity levels (M1 → M2 → M3) based on test coverage, metadata compliance, and certification proofs. The TDD gate requires test files to match a specific naming convention — mismatches silently fail CI.

This prompt encodes the certification workflow, test naming rules, and common patterns so certification campaigns can be executed consistently.

## Your Task

Certify one or more scripts by writing tests, validating metadata, and promoting maturity levels.

## Preconditions

- [ ] Target scripts are identified.
- [ ] You know the script language (Python or Bash).
- [ ] `make certify-scripts` runs without errors on existing scripts.

## Maturity Levels

| Level | Name | Requirements |
|---|---|---|
| M1 | Uncertified | Script exists, no tests |
| M2 | Partial | Some tests exist but coverage is incomplete |
| M3 | Certified | Full test coverage, metadata valid, certification proof generated |

## Test File Naming Convention (Critical)

**This is the #1 source of certification failures.** The TDD gate matches test files to source files using this pattern:

| Source File | Required Test File |
|---|---|
| `scripts/{name}.py` | `scripts/tests/test_{name}.py` |
| `scripts/{name}.sh` | `scripts/tests/test_{name}.bats` |
| `scripts/rag/{name}.py` | `scripts/rag/tests/test_{name}.py` |
| `{dir}/{name}.py` | `{dir}/tests/test_{name}.py` |

**Examples:**

| Source | Test | Valid? |
|---|---|---|
| `scripts/standardize_metadata.py` | `scripts/tests/test_standardize_metadata.py` | Yes |
| `scripts/standardize_metadata.py` | `scripts/tests/test_metadata.py` | **NO** — name mismatch |
| `scripts/standardize_metadata.py` | `tests/test_standardize_metadata.py` | **NO** — wrong directory |
| `scripts/check_session_writer.sh` | `scripts/tests/test_check_session_writer.bats` | Yes |

**Rule:** The test filename MUST be `test_{exact_source_filename}` in a `tests/` subdirectory of the source file's directory.

## Step-by-Step Implementation

### Phase 1: Identify Uncertified Scripts

1. List current script maturity levels:

   ```bash
   make certify-scripts 2>&1 | head -50
   ```

2. Or check the script matrix directly:

   ```bash
   cat docs/50-scripts/01_script_index.md
   ```

3. Identify scripts at M1 (uncertified) or M2 (partial) that need promotion.

### Phase 2: Write Tests (per GOV-0017 — Tests First)

For each script being certified:

#### Python Scripts (pytest)

1. Create the test file at the correct path:

   ```bash
   mkdir -p {dir}/tests
   touch {dir}/tests/__init__.py
   touch {dir}/tests/test_{name}.py
   ```

2. Write tests covering:
   - Happy path (expected input → expected output)
   - Edge cases (empty input, missing files, invalid data)
   - Error handling (bad args, missing dependencies)
   - CLI contract (if script has CLI: `--help`, `--dry-run`, arg parsing)

3. Handle optional dependencies with `conftest.py`:

   ```python
   # {dir}/tests/conftest.py
   import pytest

   def pytest_collection_modifyitems(config, items):
       """Skip tests that require unavailable optional dependencies."""
       for item in items:
           try:
               # Check if required modules are available
               pass
           except ImportError:
               item.add_marker(pytest.mark.skip(reason="Optional dependency not available"))
   ```

4. Run tests:

   ```bash
   pytest {dir}/tests/test_{name}.py -v
   ```

#### Bash Scripts (BATS)

1. Create the test file:

   ```bash
   mkdir -p {dir}/tests
   touch {dir}/tests/test_{name}.bats
   ```

2. Write BATS tests:

   ```bash
   #!/usr/bin/env bats

   setup() {
       # Create temp dirs, set up fixtures
       TEST_DIR="$(mktemp -d)"
   }

   teardown() {
       rm -rf "$TEST_DIR"
   }

   @test "{name}: displays help with --help" {
       run ./{dir}/{name}.sh --help
       [ "$status" -eq 0 ]
   }

   @test "{name}: exits 1 on missing argument" {
       run ./{dir}/{name}.sh
       [ "$status" -eq 1 ]
   }

   @test "{name}: produces expected output" {
       run ./{dir}/{name}.sh valid-arg
       [ "$status" -eq 0 ]
       [[ "$output" == *"expected string"* ]]
   }
   ```

3. Run BATS tests:

   ```bash
   bats {dir}/tests/test_{name}.bats
   ```

### Phase 3: Validate Metadata

1. Ensure the script has governance frontmatter (for shell scripts, check the header comment):

   ```bash
   head -20 {dir}/{name}.sh
   # Should contain: id, title, type, owner, domain, etc.
   ```

2. For Python scripts, check for a docstring or metadata module.

3. Run metadata standardization:

   ```bash
   python3 scripts/standardize_metadata.py docs/
   ```

### Phase 4: Promote and Certify

1. Run certification to generate proofs:

   ```bash
   make certify-scripts
   ```

2. Check the output for the target scripts — they should now show M3.

3. Regenerate the script index:

   ```bash
   pre-commit run generate-script-index --all-files
   ```

4. Stage all changes:

   ```bash
   git add {dir}/tests/ docs/50-scripts/
   ```

### Phase 5: Wave Execution (for bulk campaigns)

When certifying many scripts (10+), use waves:

1. **Wave 1:** High-priority scripts (most-used, critical path).
2. **Wave 2:** Medium-priority scripts.
3. **Wave 3+:** Remaining scripts.

Per wave:
- Write tests for 5-10 scripts.
- Run `make certify-scripts` to validate.
- Commit the wave: `git commit -m "test: certify scripts wave {N} ({count} scripts)"`
- Run `pre-commit run --all-files` to regenerate indexes.
- Commit index updates.

## Verification Checklist

- [ ] Test file naming matches source file: `test_{exact_name}` in `{dir}/tests/`.
- [ ] Tests pass: `pytest -v` or `bats` for each certified script.
- [ ] `make certify-scripts` shows target scripts at M3.
- [ ] Script index is regenerated and up to date.
- [ ] `pre-commit run --all-files` passes.
- [ ] No tests are skipped without explicit `conftest.py` skip markers.

## Integration Verification

- [ ] `make quality-gate` passes (includes certification).
- [ ] Script matrix in `docs/50-scripts/01_script_index.md` reflects correct maturity levels.
- [ ] If new `conftest.py` was created: it handles optional deps gracefully.

## Do NOT

- Name test files incorrectly — `test_api_contract.py` will NOT match source file `app.py`.
- Put test files in the wrong directory — tests MUST be in `{source_dir}/tests/`.
- Skip the `make certify-scripts` step — it generates the certification proofs.
- Manually edit the script index — it's auto-generated by pre-commit hooks.
- Mark scripts as M3 without actual passing tests.
- Write tests that depend on external services without mocking (Tier 1/2 must be offline).

## Output Expected

1. List of scripts certified with their new maturity levels.
2. Test file paths created.
3. Test pass/fail results.
4. `make certify-scripts` output showing M3 for certified scripts.

## Rollback Plan

- Remove test files: `git rm {dir}/tests/test_{name}.py`.
- Re-run `make certify-scripts` — scripts will revert to M1/M2.
- Regenerate script index: `pre-commit run generate-script-index --all-files`.

## References

- docs/adrs/ADR-0146-schema-driven-script-certification.md — Certification model
- docs/adrs/ADR-0147-automated-governance-backfill.md — Backfill protocol
- docs/adrs/ADR-0197-agent-workflow-prompt-codification.md — Decision to codify this workflow
- docs/governance/policies/GOV-0017-tdd-and-determinism.md — TDD policy
- PROMPT-0005 — TDD governance enforcement
