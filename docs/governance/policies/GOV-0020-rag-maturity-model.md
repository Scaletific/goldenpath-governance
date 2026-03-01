---
id: GOV-0020-rag-maturity-model
title: Agentic Graph RAG Maturity Model
type: governance
owner: platform-team
status: active
domain: platform-core
applies_to:
  - ai-systems
  - knowledge-management
  - agent-orchestration
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - 2026-01-28-agentic-graph-rag-phase0
  - ADR-0182-tdd-philosophy
  - ADR-0184-rag-markdown-header-chunking
  - EC-0013-agent-context-architecture
  - EC-0014-agent-scope-registry
  - EC-0017-platform-distribution-framework
  - GOV-0017-tdd-and-determinism
  - PRD-0008-governance-rag-pipeline
  - RB-0039
  - VQ_TAGGING_GUIDE
  - session-2026-01-28-agentic-graph-rag-reframing
supersedes: []
superseded_by: []
tags:
  - rag
  - ai
  - knowledge-graph
  - agents
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-01-28
review_date: 2026-07-28
---

# GOV-0020: Agentic Graph RAG Maturity Model

## Purpose

This policy defines the maturity model for **Agentic Graph RAG** systems within the GoldenPath IDP. Unlike basic RAG implementations, this architecture integrates:

* **Knowledge Graph (Neo4j)** - Entity relationships from Phase 0, not a later add-on
* **Agentic Capabilities** - Progression toward autonomous tool orchestration
* **Governance-Aware Automation** - Self-correcting agents with human approval workflows

The model establishes progression levels, requirements for advancement, governance controls, and the roadmap for achieving an autonomous, AI-native platform.

### Why "Agentic Graph RAG"?

| Component    | Role                                     | Without It                                        |
| ------------ | ---------------------------------------- | ------------------------------------------------- |
| **Graph**    | Captures relationships between entities  | "What depends on GOV-0017?" is unanswerable       |
| **Agentic**  | Orchestrates tools, self-corrects        | Static Q&A only, no multi-step reasoning          |
| **RAG**      | Grounds responses in real documents      | Hallucination risk, no citations                  |

This is not RAG with optional enhancements—it's a unified architecture where graph traversal and agent orchestration are foundational, not aspirational.

---

## Core Principle

> **"Trust is earned through measured capability. Agents gain autonomy as they prove reliability."**

RAG systems progress through defined maturity levels. Each level unlocks new capabilities while maintaining governance guardrails. Advancement is gated on **measured outcomes**, not feature completion.

---

## Maturity Levels Overview

```
                    TRUST / AUTONOMY
                          ▲
                          │
         L4 ─────────────►│ AUTONOMOUS
                          │ Proposes changes, executes with approval
                          │
         L3 ─────────────►│ AGENTIC
                          │ Multi-tool orchestration, self-correction
                          │
         L2 ─────────────►│ CORRECTIVE
                          │ Confidence scoring, re-retrieval
                          │
         L1 ─────────────►│ HYBRID
                          │ Vector + graph + metadata filtering
                          │
         L0 ─────────────►│ FOUNDATIONAL
                          │ Basic retrieve + generate
                          │
    ──────────────────────┴──────────────────────►
                    CAPABILITY
```

---

## Level Definitions

### L0: Foundational RAG

**Definition:** Basic retrieval-augmented generation with vector search and LLM response.

**Capabilities:**

| Capability | Description |
|------------|-------------|
| Vector search | Semantic similarity retrieval |
| Citation | File-level source attribution |
| CLI interface | Command-line query tool |

**Technical Stack:**

| Component | Implementation |
|-----------|----------------|
| LLM | Ollama (llama3.1:8b) |
| Embeddings | nomic-embed-text |
| Vector DB | ChromaDB |
| Framework | LlamaIndex |

**Requirements:**

| Requirement | Metric |
|-------------|--------|
| Index coverage | 100% of GOV-*, ADR-*, PRD-* docs |
| Index freshness | Rebuilt within 48 hours of doc change |
| Query logging | All queries logged with timestamp |
| Observability | Phoenix tracing enabled |

**Governance Controls:**

- Read-only access to indexed documents
- No external API calls
- No file system writes outside index directory
- Human reviews all outputs (no automation)

---

### L1: Hybrid RAG

**Definition:** Enhanced retrieval combining vector search, knowledge graph, and metadata filtering.

**Capabilities:**

| Capability | Description |
|------------|-------------|
| Knowledge graph | Entity relationships via Neo4j/Graphiti |
| Metadata filtering | Filter by doc_type, domain, status |
| Multi-hop queries | "What depends on GOV-0017?" |
| BM25 hybrid | Sparse + dense retrieval fusion |

**Technical Stack Additions:**

| Component | Implementation |
|-----------|----------------|
| Knowledge Graph | Neo4j + Graphiti |
| Hybrid Search | BM25 + vector fusion |

**Requirements:**

| Requirement | Metric |
|-------------|--------|
| All L0 requirements | Maintained |
| RAGAS context precision | ≥ 0.75 |
| RAGAS faithfulness | ≥ 0.80 |
| Weekly active queries | ≥ 20 |
| Entity extraction coverage | Key docs have entities indexed |

**Governance Controls:**

- All L0 controls maintained
- Graph queries scoped to governance domain
- No entity creation without human review

---

### L2: Corrective RAG

**Definition:** Self-evaluating retrieval with confidence scoring and automatic re-retrieval on low confidence.

**Capabilities:**

| Capability | Description |
|------------|-------------|
| Confidence scoring | LLM evaluates retrieval quality |
| Re-retrieval | Automatic retry with reformulated query |
| Source validation | Cross-reference citations |
| Uncertainty flagging | "I'm not confident" responses |

**Requirements:**

| Requirement | Metric |
|-------------|--------|
| All L1 requirements | Maintained |
| RAGAS context precision | ≥ 0.85 |
| RAGAS answer relevancy | ≥ 0.85 |
| Self-correction success rate | ≥ 70% of low-confidence retries improve |
| False confidence rate | < 5% (confident but wrong) |

**Governance Controls:**

- All L1 controls maintained
- Re-retrieval limited to 3 attempts
- Uncertainty responses required when confidence < threshold
- Audit log of all self-corrections

---

### L3: Agentic RAG

**Definition:** Multi-tool agent orchestration using ReAct pattern with self-correction loops.

**Capabilities:**

| Capability | Description |
|------------|-------------|
| Tool orchestration | Agent selects and chains tools |
| ReAct pattern | Reason → Act → Observe → Repeat |
| Multi-step queries | Complex questions requiring multiple lookups |
| Cross-source synthesis | Combine data from multiple sources |

**Available Tools:**

| Tool | Purpose | Permission Level |
|------|---------|------------------|
| `vector_search` | Semantic document retrieval | Read |
| `graph_query` | Knowledge graph traversal | Read |
| `catalog_lookup` | Backstage catalog queries | Read |
| `file_read` | Read specific files | Read |
| `list_modules` | List Terraform modules | Read |
| `check_tests` | Verify test existence | Read |

**Requirements:**

| Requirement | Metric |
|-------------|--------|
| All L2 requirements | Maintained |
| Task completion rate | ≥ 85% for defined task types |
| Tool selection accuracy | ≥ 90% appropriate tool choices |
| Iteration efficiency | Average < 5 steps for standard queries |
| RAGAS overall score | ≥ 0.85 |

**Governance Controls:**

- All L2 controls maintained
- Tool allowlist enforced (no unapproved tools)
- Maximum 10 iterations per query
- All tool invocations logged
- No write operations

---

### L4: Autonomous IDP

**Definition:** Agents propose and execute platform changes with governance guardrails and human approval workflows.

**Capabilities:**

| Capability | Description |
|------------|-------------|
| Change proposals | Agent suggests PRs, doc updates |
| Compliance auditing | "Are all modules TDD compliant?" |
| Remediation suggestions | "Module X missing tests, here's a fix" |
| Governance enforcement | Flag policy violations automatically |
| Human-in-loop execution | Changes require approval |

**Available Tools (Additions):**

| Tool | Purpose | Permission Level |
|------|---------|------------------|
| `create_issue` | Open GitHub issue | Write (approved) |
| `propose_pr` | Draft PR for review | Write (approved) |
| `run_tests` | Execute test suite | Execute (approved) |
| `update_index` | Refresh RAG index | Write (approved) |

**Requirements:**

| Requirement | Metric |
|-------------|--------|
| All L3 requirements | Maintained |
| Proposal acceptance rate | ≥ 70% of proposals approved |
| False positive rate | < 10% for compliance violations |
| Mean time to remediation | < 24 hours for auto-fixable issues |
| Human override rate | < 20% of approved actions |

**Governance Controls:**

- All L3 controls maintained
- Write operations require human approval
- Approval workflow with timeout (auto-reject after 48h)
- Rollback capability for all changes
- Full audit trail with diff visibility
- Emergency stop mechanism

---

## Exit Criteria Matrix

| Transition | Key Metrics | Minimum Duration |
|------------|-------------|------------------|
| L0 → L1 | RAGAS precision ≥ 0.75, 20+ weekly queries | 2 weeks at L0 |
| L1 → L2 | RAGAS precision ≥ 0.85, faithfulness ≥ 0.85 | 2 weeks at L1 |
| L2 → L3 | Task completion ≥ 85%, tool accuracy ≥ 90% | 4 weeks at L2 |
| L3 → L4 | Proposal acceptance ≥ 70%, false positive < 10% | 8 weeks at L3 |

---

## Roadmap and Deliverables

### VQ Classification Key

Per [VQ_PRINCIPLES.MD](../../00-foundations/product/VQ_PRINCIPLES.MD) and [VQ_TAGGING_GUIDE.md](../../00-foundations/product/VQ_TAGGING_GUIDE.md):

| Class | Meaning | Approach |
|-------|---------|----------|
| 🔴 HV/HQ | High Value, High Quality | Trust-critical, do it right |
| 🟡 HV/LQ | High Value, Low Quality | Ship fast, reversible |
| 🔵 MV/HQ | Medium Value, High Quality | Do once, contain |
| ⚫ LV/LQ | Low Value, Low Quality | Drop it |

---

### Phase 0: Foundational RAG (L0)

**Target:** Prove basic retrieval value

| Deliverable | VQ Class | Impact | Savings/Query | Exit Criteria |
|-------------|----------|--------|---------------|---------------|
| RAG infrastructure setup | 🔴 HV/HQ | tier-1 | Foundation | Services running locally |
| Document indexer | 🔴 HV/HQ | tier-1 | 0.5h | 100% GOV/ADR/PRD coverage |
| CLI query tool | 🟡 HV/LQ | tier-2 | 0.25h | Working CLI with citations |
| Phoenix observability | 🔵 MV/HQ | tier-2 | Debug time | Traces visible in UI |
| RAGAS baseline | 🔴 HV/HQ | tier-1 | Quality gate | 20 test questions scored |

**Value Quantification:**

```yaml
phase_0_vq:
  total_potential_savings: 15h/week  # Based on 20 queries × 0.5h saved
  vq_class_distribution:
    HV_HQ: 3  # Infrastructure, indexer, RAGAS
    HV_LQ: 1  # CLI tool
    MV_HQ: 1  # Phoenix
  justification: |
    Every governance lookup currently takes 10-30 minutes of grep/search/read.
    RAG reduces this to <1 minute with citations. At 20+ queries/week,
    this reclaims ~15 hours of developer time weekly.
```

**Timeline:** 5 days

---

### Phase 1: Hybrid RAG (L1)

**Target:** Enable relationship-aware queries

| Deliverable | VQ Class | Impact | Savings/Query | Exit Criteria |
|-------------|----------|--------|---------------|---------------|
| Knowledge graph integration | 🔴 HV/HQ | tier-1 | 1h | Entities extracted from docs |
| Hybrid retrieval | 🔴 HV/HQ | tier-1 | Precision | Improved RAGAS scores |
| Metadata filtering | 🟡 HV/LQ | tier-2 | 0.1h | Filters working in CLI |
| FastAPI backend | 🟡 HV/LQ | tier-2 | Enables integrations | `/query` endpoint live |
| RAGAS CI integration | 🔴 HV/HQ | tier-1 | Quality gate | Scores tracked per commit |

**Value Quantification:**

```yaml
phase_1_vq:
  total_potential_savings: 25h/week  # Multi-hop queries save more time
  vq_class_distribution:
    HV_HQ: 3  # Graph, hybrid, CI
    HV_LQ: 2  # Filtering, FastAPI
  justification: |
    Multi-hop queries ("What depends on GOV-0017?") currently require
    manual cross-referencing across 10+ docs. Graph traversal answers
    in seconds. Complex queries save 1h+ each.
```

**Timeline:** 2 weeks
**Gate:** RAGAS context precision ≥ 0.75

---

### Phase 2: Corrective RAG (L2)

**Target:** Self-improving retrieval quality

| Deliverable | VQ Class | Impact | Savings/Query | Exit Criteria |
|-------------|----------|--------|---------------|---------------|
| Confidence scoring | 🔴 HV/HQ | tier-1 | Trust | Confidence scores in responses |
| Re-retrieval logic | 🔵 MV/HQ | tier-2 | 0.2h | 70% improvement rate |
| Uncertainty responses | 🔴 HV/HQ | tier-1 | Prevents errors | False confidence < 5% |
| Reranking (optional) | ⚫ LV/LQ | tier-3 | Marginal | Precision improvement measured |

**Value Quantification:**

```yaml
phase_2_vq:
  total_potential_savings: 30h/week  # Higher confidence = fewer verification loops
  vq_class_distribution:
    HV_HQ: 2  # Confidence, uncertainty
    MV_HQ: 1  # Re-retrieval
    LV_LQ: 1  # Reranking (optional, defer if marginal)
  justification: |
    False confidence is expensive - acting on wrong info causes rework.
    Uncertainty flagging ("I'm not sure") prevents downstream errors.
    Saves 2-4h per prevented mistake.
```

**Timeline:** 2 weeks
**Gate:** RAGAS precision ≥ 0.85, faithfulness ≥ 0.85

---

### Phase 3: Agentic RAG (L3)

**Target:** Multi-tool reasoning

| Deliverable | VQ Class | Impact | Savings/Query | Exit Criteria |
|-------------|----------|--------|---------------|---------------|
| Tool definitions | 🔴 HV/HQ | tier-1 | Foundation | 6+ tools defined |
| ReAct implementation | 🔴 HV/HQ | tier-1 | 2h | Agent handles multi-step |
| Tool orchestration | 🔴 HV/HQ | tier-1 | Automation | 90% accuracy |
| Backstage integration | 🟡 HV/LQ | tier-2 | UX | Catalog data accessible |
| Agent evaluation | 🔴 HV/HQ | tier-1 | Quality gate | 85% task completion |

**Value Quantification:**

```yaml
phase_3_vq:
  total_potential_savings: 50h/week  # Complex multi-step tasks automated
  vq_class_distribution:
    HV_HQ: 4  # Tools, ReAct, orchestration, eval
    HV_LQ: 1  # Backstage integration
  justification: |
    Multi-step queries ("Audit all modules for TDD compliance") currently
    require manual iteration across multiple tools. Agentic RAG completes
    these autonomously. Each complex query saves 2-4h.
```

**Timeline:** 4 weeks
**Gate:** Task completion ≥ 85%, tool accuracy ≥ 90%

---

### Phase 4: Autonomous IDP (L4)

**Target:** Governance-aware automation

| Deliverable | VQ Class | Impact | Savings/Query | Exit Criteria |
|-------------|----------|--------|---------------|---------------|
| Compliance scanner | 🔴 HV/HQ | tier-1 | 4h/audit | Violations flagged |
| Change proposals | 🔴 HV/HQ | tier-1 | 1h/PR | PRs created successfully |
| Approval workflow | 🔴 HV/HQ | tier-1 | Trust | Approval flow working |
| Backstage plugin | 🟡 HV/LQ | tier-2 | UX | Plugin deployed |
| Emergency stop | 🔴 HV/HQ | tier-1 | Safety | Stop mechanism tested |

**Value Quantification:**

```yaml
phase_4_vq:
  total_potential_savings: 80h/week  # Autonomous governance enforcement
  vq_class_distribution:
    HV_HQ: 4  # Scanner, proposals, approval, emergency stop
    HV_LQ: 1  # Backstage plugin
  justification: |
    Manual compliance audits take 4-8h each. Automated scanning runs
    continuously. Agent-proposed PRs save 1h each in scaffolding.
    At scale, autonomous governance reclaims significant engineering time.
```

**Timeline:** 8 weeks
**Gate:** Proposal acceptance ≥ 70%, false positive < 10%

---

### Cumulative Value Projection

| Phase | Weekly Savings | Cumulative | VQ Justification |
|-------|----------------|------------|------------------|
| L0 | 15h | 15h | Basic lookup automation |
| L1 | +10h | 25h | Multi-hop relationship queries |
| L2 | +5h | 30h | Reduced verification loops |
| L3 | +20h | 50h | Complex task automation |
| L4 | +30h | 80h | Autonomous governance |

> **Annual value at L4:** 80h/week × 50 weeks = **4,000 hours reclaimed**

---

## Assessment Checklist

### L0 Assessment

- [ ] All GOV-*, ADR-*, PRD-* documents indexed
- [ ] CLI query tool returns results with citations
- [ ] Phoenix shows traces for queries
- [ ] RAGAS baseline scores recorded
- [ ] Query log capturing all requests

### L1 Assessment

- [ ] All L0 items complete
- [ ] Knowledge graph populated with entities
- [ ] Hybrid search (BM25 + vector) enabled
- [ ] Metadata filtering working
- [ ] RAGAS context precision ≥ 0.75
- [ ] 20+ weekly queries sustained for 2 weeks

### L2 Assessment

- [ ] All L1 items complete
- [ ] Confidence scores in all responses
- [ ] Re-retrieval triggers on low confidence
- [ ] Uncertainty responses when appropriate
- [ ] RAGAS precision ≥ 0.85, faithfulness ≥ 0.85
- [ ] False confidence rate < 5%

### L3 Assessment

- [ ] All L2 items complete
- [ ] 6+ tools defined and working
- [ ] ReAct pattern implemented
- [ ] Agent completes multi-step queries
- [ ] Task completion rate ≥ 85%
- [ ] Tool selection accuracy ≥ 90%

### L4 Assessment

- [ ] All L3 items complete
- [ ] Compliance scanner operational
- [ ] Change proposal mechanism working
- [ ] Human approval workflow functional
- [ ] Emergency stop tested
- [ ] Proposal acceptance rate ≥ 70%
- [ ] False positive rate < 10%

---

## Governance Integration

This policy integrates with existing governance:

| Policy | Integration |
|--------|-------------|
| GOV-0017 (TDD) | Agents must follow TDD requirements |
| EC-0014 (Agent Scope) | RAG agents registered in scope registry |
| PRD-0008 | Technical implementation details |

---

## Risk Management

| Risk | Mitigation |
|------|------------|
| Hallucination | Faithfulness scoring, citation requirements |
| Unauthorized actions | Tool allowlists, permission levels |
| Stale knowledge | 48-hour freshness requirement |
| Agent runaway | Iteration limits, emergency stop |
| Trust erosion | Measured progression, human oversight |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-28 | Claude Opus 4.5 | Initial creation |
