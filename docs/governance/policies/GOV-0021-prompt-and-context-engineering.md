---
id: GOV-0021-prompt-and-context-engineering
title: Prompt and Context Engineering Governance
type: governance
owner: platform-team
status: active
domain: platform-core
applies_to:
  - ai-systems
  - inference-platform
  - agent-orchestration
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0164-agent-trust-and-identity
  - ADR-0185-graphiti-agent-memory-framework
  - EC-0019-agent-governance-framework
  - EC-0020-composable-inference-platform
  - GOV-0017-tdd-and-determinism
  - GOV-0020-rag-maturity-model
  - PRD-0008-governance-rag-pipeline
  - PROMPT_INDEX
supersedes: []
superseded_by: []
tags:
  - ai
  - prompts
  - context-engineering
  - governance
  - inference
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-02-09
review_date: 2026-08-09
---

# GOV-0021: Prompt and Context Engineering Governance

## Purpose

GoldenPath IDP treats human-AI collaboration as a first-class architectural concern. Every AI-assisted capability in the platform — from governance RAG queries to agent-driven development to automated code review — depends on prompts and context to produce useful, safe, and governed outputs. These prompts are not configuration. They are not comments. They are **platform code** that directly determines the quality, safety, and coherence of every AI-generated output the platform produces.

This policy establishes the governance requirements for all prompts and context engineering artefacts within the IDP. It applies the same principles the platform enforces on infrastructure code — version control, testing, traceability, and review — to the instructions that govern AI behaviour.

---

## Core Principle

> **"A prompt that governs production inference is platform code. It must be versioned, tested, traceable, and reviewed — the same as any contract or schema."**

An ungoverned prompt is a governance hole. The platform validates inference outputs via contract schemas (`answer_contract.schema.json`) and measures quality via RAGAS metrics — but if the instructions that produce those outputs are hardcoded strings that nobody versions, tests, or reviews, then the governance chain has a gap. This policy closes that gap.

---

## Scope

This policy governs two categories of prompt artefacts:

### Category 1: Agent Execution Prompts

Structured instructions for human-supervised agent tasks. These already exist in `prompt-templates/PROMPT-XXXX-*.md` and follow a documented template structure.

**Current state:** Governed. Versioned in git, structured with YAML frontmatter, indexed in README, discoverable via RAG. This policy formalises their existing practices and extends them.

### Category 2: Inference System Prompts

The system prompts, few-shot examples, chain-of-thought instructions, and context templates embedded in production inference code. These are the prompts that govern how the LLM Gateway synthesises answers, extracts themes, classifies content, or generates documents.

**Current state:** Ungoverned. Hardcoded as string literals in `scripts/rag/llm_synthesis.py` and similar files. Not versioned independently, not tested, not traceable, not reviewed as prompt artefacts.

### Category 3: Context Engineering Templates

The templates that structure what context is provided to the LLM alongside a prompt — retrieval results formatting, graph context serialisation, memory episode rendering, and system context preambles (e.g., CLAUDE.md files, role-specific instruction sets from EC-0019).

**Current state:** Partially governed. CLAUDE.md is versioned and reviewed. Role-specific variants proposed in EC-0019 are not yet implemented. Retrieval result formatting is implicit in code, not explicit as a governed template.

---

## Requirements

### R1: All Prompts Must Be Named and Versioned

Every prompt that governs production behaviour must have:

- **A unique identifier** — following the naming convention for its category
- **A version number** — semantic versioning (major.minor) where major = breaking change to output structure, minor = quality refinement
- **A changelog entry** — what changed, why, and what output behaviour is affected

**Naming conventions:**

| Category | Convention | Example |
| --- | --- | --- |
| Agent execution prompts | `PROMPT-XXXX-<description>.md` | `PROMPT-0005-tdd-governance-agent.md` |
| Inference system prompts | `prompts/<pattern>/<name>.v<N>.md` | `prompts/rag-synthesis/governance-answer.v1.md` |
| Context templates | `prompts/context/<name>.v<N>.md` | `prompts/context/retrieval-results.v1.md` |

### R2: Inference Prompts Must Be Extracted from Code

System prompts must not be hardcoded as string literals in Python source files. They must be:

1. **Stored as standalone files** in the `prompts/` directory
2. **Loaded at runtime** by the inference code (not compiled in)
3. **Referenceable by name and version** — the inference code requests `get_prompt("governance-answer", version=1)`, not `SYSTEM_PROMPT = "You are a..."`

This separation ensures prompts can be reviewed, tested, and versioned independently of the code that executes them.

### R3: Prompts Must Have Tests

Every inference system prompt must have at least one test that validates:

1. **Contract compliance** — given a known input and retrieval context, the prompt produces output that passes contract validation
2. **Safety boundaries** — the prompt does not produce outputs containing prohibited content (PII, credentials, ungrounded claims outside the corpus)
3. **Determinism** — given the same input, the prompt produces structurally consistent outputs across multiple runs (content may vary; structure must not)

Tests follow GOV-0017 (TDD and Determinism). Write the test before modifying the prompt.

### R4: Prompt Changes Require Review

Prompt modifications follow the same PR workflow as code changes:

- **Minor changes** (wording refinement, clarity improvement) — standard PR review
- **Major changes** (output structure change, new capabilities, safety boundary modification) — requires platform team review and contract schema validation

A prompt change that alters the output structure is a breaking change. It must be accompanied by a contract schema update and downstream consumer notification.

### R5: Context Engineering Must Be Explicit

The way retrieval results, graph context, and memory episodes are formatted before being passed to the LLM is a governed concern. These formatting decisions directly affect inference quality:

- How many retrieval results are included and in what order
- How graph relationships are serialised (Cypher results → natural language)
- How Graphiti memory episodes are rendered (temporal ordering, relevance filtering)
- What system context preamble is prepended (role, constraints, output format)

Context templates must be stored in `prompts/context/`, versioned, and testable. A change to how retrieval results are formatted is a prompt change — it must go through the same review and testing process.

### R6: Prompt Observability

Every inference call must log which prompt (name + version) was used. This enables:

- **Root cause analysis** — when the feedback collector (EC-0020) traces a bad answer, the prompt version is part of the trace
- **A/B comparison** — compare quality metrics between prompt versions
- **Audit trail** — know exactly which instructions governed any historical inference call

Phoenix traces must include `prompt.name` and `prompt.version` as span attributes.

---

## Prompt Lifecycle

```text
draft → review → active → deprecated → archived
```

| State | Meaning |
| --- | --- |
| **draft** | Being written/tested, not used in production |
| **review** | Submitted for PR review, tests passing |
| **active** | Deployed to production inference |
| **deprecated** | Replaced by newer version, still available for rollback |
| **archived** | No longer available, preserved for audit |

Only one version of a prompt may be `active` for a given pattern at any time. The previous version moves to `deprecated` and is retained for 90 days before archival.

---

## What This Policy Does NOT Govern

- **Ad-hoc development prompts** — prompts typed into Claude Code or similar tools during development sessions. These are ephemeral and not platform code.
- **CLAUDE.md files** — these are instruction files for agent behaviour, not inference prompts. They are governed by their own review process and EC-0019 role definitions.
- **One-off scripts** — a script that calls an LLM for a one-time task does not need to go through the prompt registry. The policy applies to prompts that govern repeatable, production inference.

---

## Relationship to Existing Governance

### Prompt Templates (`prompt-templates/`)

The existing `prompt-templates/PROMPT-XXXX` directory governs agent execution prompts — structured instructions for human-supervised tasks. This policy formalises their status as governed artefacts and extends the same discipline to inference system prompts, which currently lack it.

The two directories serve different purposes:

| Directory | Purpose | Audience |
| --- | --- | --- |
| `prompt-templates/` | Agent execution instructions | Human operators supervising agents |
| `prompts/` (new) | Inference system prompts + context templates | The inference platform (machine-consumed) |

### GOV-0017 (TDD and Determinism)

Prompt tests are an extension of the TDD requirement. A prompt that governs production inference is determinism-critical — changes to it alter output behaviour. GOV-0017's requirement that "nothing that generates infrastructure, parses config, or emits scaffolds may change without tests" extends naturally to: nothing that generates inference outputs may change without tests.

### EC-0020 (Composable Inference Platform)

The Prompt Registry primitive defined in EC-0020 is the implementation mechanism for this policy. This policy defines the governance requirements; EC-0020 defines the technical primitive that enforces them.

### EC-0019 (Agent Governance Framework)

Role-specific CLAUDE.md variants and agent instruction sets proposed in EC-0019 are context engineering artefacts. When implemented, they fall under Category 3 of this policy and must be versioned and reviewed.

---

## Implementation Path

### Immediate (Week 1)

1. Create `prompts/` directory structure
2. Extract the system prompt from `scripts/rag/llm_synthesis.py` into `prompts/rag-synthesis/governance-answer.v1.md`
3. Write a test that validates the extracted prompt produces contract-compliant output
4. Update `RAGSynthesizer` to load the prompt from file instead of hardcoded string

### Short-term (Week 2-3)

1. Extract context formatting templates into `prompts/context/`
2. Add `prompt.name` and `prompt.version` to Phoenix trace spans
3. Document the prompt registry API (`get_prompt()`, `test_prompt()`)
4. Add prompt version to the `/ask` endpoint response metadata

### Medium-term (Week 4-6)

1. Build prompt quality comparison tooling (compare RAGAS scores between versions)
2. Add prompt linting to pre-commit hooks (structure validation, frontmatter completeness)
3. Create prompt template for new composition patterns (EC-0020 Patterns 2-8)

---

## Compliance

| Requirement | Enforcement |
| --- | --- |
| R1: Named and versioned | Pre-commit hook validates `prompts/` files have frontmatter with id and version |
| R2: Extracted from code | Code review + linting rule: no multiline string literals in synthesis modules |
| R3: Tests exist | CI gate: every file in `prompts/` must have a corresponding test |
| R4: Changes reviewed | Standard PR workflow |
| R5: Context templates explicit | Code review |
| R6: Prompt observability | CI test: Phoenix spans include prompt metadata |

---

## Questions

- Slack: #platform-engineering
- Related EC: EC-0020-composable-inference-platform
- Related prompt index: prompt-templates/README.md

---

**Created**: 2026-02-09
**Author**: platform-team
