---
id: ADR-0146
title: Schema-Driven Script Certification
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
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 2026-01-26-session-capture-tdd-quality-gate
  - ADR-0126
  - ADR-0126 (Confidence Matrix)
  - ADR-0146
  - ADR-0147
  - BORN_GOVERNED_LIFECYCLE
  - CL-0117
  - CL-0117 (Implementation)
  - CL-0118
  - CL-0120
  - CL-0187-test-proof-generation
  - CNT-001
  - ROADMAP
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-12
context:
  - Scripts are a critical part of the platform control plane.
  - Currently, script quality is enforced heuristically (e.g., check if a test file
    exists), which is brittle and unverifiable.
  - We lack a mechanism to verify that a script supports safety features like Dry-Run
    without executing it.
  - There is no machine-readable link between a script, its test runner, and its execution
    proof in CI.
decision:
  - We will adopt a **Schema-Driven Certification** model for all platform automation
    scripts.
  - Every script MUST contain a structured YAML metadata block (Frontmatter) in its
    header.
  - This metadata MUST conform to `schemas/automation/script.schema.yaml`.
  - The schema defines strict contracts for Identity, Maturity, Dry-Run Support, and
    Testing Strategy.
  - We will enforce this contract using a dedicated validator (`validate_scripts_tested.py`)
    in CI.
consequences:
  - Scripts become self-describing assets with explicit safety profiles.
  - CI can deterministically verify if a specific script is tested, purely by reading
    its contract.
  - Enables advanced policy enforcement (e.g., 'High Impact scripts must use CI proofs').
  - 'Migration cost: Existing scripts must be updated with metadata headers.'
alternatives:
  - 'Continue with file-existence heuristics (Rejected: Too fragile, no dry-run verification).'
  - 'Maintain a central `tests.json` registry (Rejected: High drift risk; metadata
    should live with the code).'
compliance:
  - All scripts in `scripts/` MUST have a `script` type validation block.
  - 'High-risk scripts MUST declare `evidence: ci` and generate proof artifacts.'
---

# ADR-0146: Schema-Driven Script Certification

## Context
The platform currently relies on dozens of Python and Bash scripts to manage critical lifecycle events (metadata standardization, registry mirroring, secret management). While we have a high-level "Confidence Matrix" (ADR-0126), the actual enforcement of this matrix has been manual or heuristic.

There was no way for a machine to look at `scripts/remediate_everything.py` and answer:
1. Is this safe to run? (Dry-run support)
2. How do I test it? (Runner command)
3. Is it production ready? (Maturity level)

## Decision

We are shifting governance **left**, directly into the source code headers.

### 1. The Contract (`script.schema.yaml`)
We define a rigid schema that every script must satisfy. Key fields:

```yaml
test:
  runner: pytest
  command: "pytest tests/unit/test_my_script.py"
  evidence: ci
dry_run:
  supported: true
risk_profile:
  production_impact: high
```

### 2. Implementation Pattern
Metadata is embedded in the native comment format of the language:

**Python:**
```python
"""
---
id: my_script
type: script
...
---
"""
```

**Bash:**
```bash
# ---
# id: my_script
# type: script
# ...
# ---
```

### 3. Verification
A new tool, `scripts/validate_scripts_tested.py`, acts as the **Policy Enforcement Point (PEP)**. It runs in CI/Pre-commit and blocks any script that:
1. Lacks a header.
2. Violates the schema.
3. Claims `evidence: ci` but has no corresponding Test Proof artifact.

## Consequences

### Positive
*   **Transparency:** Developers see the quality contract immediately when opening a file.
*   **Automation:** CI can intelligently selectively test scripts based on their metadata.
*   **Safety:** The `dry_run.supported` flag allows us to build generic "Safe Runners" that can execute any script in preview mode blindly.

### Negative
*   **Boilerplate:** Minimal overhead added to every script file (~15 lines).
*   **Migration:** We need to backfill headers for ~40 existing scripts.

## Compliance
This ADR supersedes heuristic checks. The "Script Certification Audit" document (`GOV-0054-script-certification-audit.md`) will track the migration progress towards 100% compliance.

Implementing tools:
*   `generate_script_matrix.py`: Automated certification reporting.
*   `scaffold_test.py`: Standardized test scaffolding for certification.
*   `check-policy-compliance.py`: Automated policy governance.

## Full Certification Achieved (2026-02-11)

All 62 platform scripts reached M3 (Validated) via PRD-0012 Campaign:

*   Shell scripts certified: `deploy-backstage.sh`, `ecr-build-push.sh`, `generate-build-log.sh`, `generate-teardown-log.sh`, `load-image-to-kind.sh`, `preflight_secrets_check.sh`, `rag-data-sync.sh`, `rds_provision_k8s.sh`, `rds_secrets_preflight.sh`, `record-build-timing.sh`, `record-test-metrics.sh`, `refresh-ecr-secret.sh`, `reliability-metrics.sh`, `resolve-cluster-name.sh`
*   RAG scripts certified: `rag_agent.py`, `graph_ingest.py`, `hybrid_retriever.py`, `llm_synthesis.py`
*   Governance scripts certified: `pr_guardrails.py`, `validate_metadata.py`, `platform_health.py`, `validate_govreg.py`, `validate_scripts_tested.py`
*   See CL-0210 and GOV-0054-script-certification-audit.md for complete details.
