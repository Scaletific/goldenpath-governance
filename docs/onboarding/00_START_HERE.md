---
id: 00_START_HERE
title: Start Here
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 2026-01-07_1510_platform-governance-finalization
  - 23_NEW_JOINERS
  - 24_PR_GATES
  - GOLDENPATH_IDP_ROOT_README
  - GOV-0026-governance-vocabulary
  - PLATFORM_DASHBOARDS
  - RB-0027
  - agent_session_summary
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
category: onboarding
supported_until: '2028-01-01'
---

## 🚀 START HERE (5-Minute Onboarding)

Welcome to the **GoldenPath IDP Infra** repository. This guide is designed to get you (Human or Agent) fully operational in under 5 minutes.

---

## For Humans: The "Quick 3"

If you are a new engineer or operator, do this first:

1. **Environment Setup**:

    ```bash
    ./bin/governance setup
    ```

    *This installs dependencies (`pip`), sets up `pre-commit` hooks, and prepares your local linter parity.*

2. **Check the Pulse**:

    ```bash
    ./bin/governance pulse
    ```

    *View the current Platform Mission, total Reclaimed ROI, and V1 Readiness status.*

3. **Discover the Ecosystem**:
    Open [**`PLATFORM_DASHBOARDS.md`**](../../PLATFORM_DASHBOARDS.md) in the root. This is your map to all health, testing, and registry reports.
4. **Frictionless PRs**:
    Review the [**Heal-First Workflow (RB-0027)**](../70-operations/runbooks/RB-0027-frictionless-pr-gates.md) to pass all PR gates automatically.
5. **Doc Scaffolding**:
    Use `scripts/scaffold_doc.py` for any new docs to ensure metadata compliance from day one.

---

## 🤖 For Agents: The "Operational Handshake"

If you are an AI Assistant (Antigravity, etc.), you MUST begin every session here:

1. **Read the Instructions**:
    Open [**`tests/AGENT_INSTRUCTIONS.md`**](../../tests/AGENT_INSTRUCTIONS.md). This defines the "START HERE" block you must include in every test suite you create.

2. **Verify Baseline**:

    ```bash
    ./bin/governance audit
    ```

    *Ensure you are starting from a 100% Green governance state.*

3. **Standardized Scaffolding**:
    Use `./bin/governance test scaffold` for every new feature or script to ensure metadata and test integrity from Step 1.
    Use `scripts/scaffold_doc.py` for any new docs to keep frontmatter compliant.

4. **Auto-Remediation**:
    Always run `bin/governance heal .` before proposing changes to ensure automatic alignment with CI gates.

---

## 💎 The Platform Core Values

To maintain platform velocity without breaking things, internalize these 3 principles:

1. **Rough UX is OK (🟡 HV/LQ)**: Speed over polish for low-risk tools.
2. **Trust is Default (🔴 HV/HQ)**: High-value core systems must be bored/predictable.
3. **Auditability is Non-Negotiable**: If there is no ADR, Changelog entry, or Metadata sidecar, the work does not exist.

---

## 📘 Essential Reading

|Document|Purpose|
|:---|:---|
|[**`NEW_JOINERS.md`**](./23_NEW_JOINERS.md)|Deep-dive for new team members.|
|[**`PR_GATES.md`**](./24_PR_GATES.md)|Detailed breakdown of CI/CD requirements.|
|[**`TESTING_STANDARDS.md`**](../tests/TESTING_STANDARDS.md)|The definitive guide to our 5-phase testing model.|
|[**`GOV-0026-governance-vocabulary.md`**](../governance/GOV-0026-governance-vocabulary.md)|Official list of Owners, Domains, and VQ Classes.|

---

**Certified By:** Platform Governance Office
**Last Updated:** 2026-01-07
