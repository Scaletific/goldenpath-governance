#!/usr/bin/env python3
"""
---
id: SCRIPT-0081
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-02-03
test:
  runner: pytest
  command: "pytest -q tests/unit/test_query_expansion.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0020-rag-maturity-model
  - SCRIPT-0079-hybrid-retriever
---
Purpose: Query expansion for improved semantic retrieval.

L1.5 Enhancement: Expands user queries with domain-specific synonyms
to improve retrieval when users use different terminology than the
indexed documents.

Example:
    >>> from scripts.rag.query_expansion import expand_query
    >>> expand_query("What are the phases of RAG implementation?")
    "What are the phases levels stages maturity of RAG implementation?"
"""

import re
from typing import Dict, List, Set


# Domain-specific synonym mappings
# Key: term to match (lowercase)
# Value: list of synonyms to add
DOMAIN_SYNONYMS: Dict[str, List[str]] = {
    # Maturity/progression terminology
    "phases": ["levels", "stages", "maturity", "progression", "tiers"],
    "levels": ["phases", "stages", "maturity", "tiers"],
    "stages": ["phases", "levels", "maturity"],
    "maturity": ["levels", "phases", "progression"],
    # Implementation terminology
    "implementation": ["deployment", "rollout", "adoption", "setup"],
    "deployment": ["implementation", "rollout", "release"],
    "setup": ["configuration", "installation", "implementation"],
    # Architecture terminology
    "architecture": ["design", "structure", "framework"],
    "design": ["architecture", "pattern", "structure"],
    "pattern": ["design", "approach", "method"],
    # Testing terminology
    "testing": ["tests", "validation", "verification", "tdd"],
    "tests": ["testing", "specs", "validation"],
    "tdd": ["test-driven", "testing", "tests"],
    "coverage": ["test coverage", "code coverage", "metrics"],
    # Document types
    "policy": ["governance", "rule", "standard", "guideline"],
    "governance": ["policy", "policies", "rules", "standards"],
    "adr": ["decision", "architecture decision", "design decision"],
    "runbook": ["playbook", "procedure", "guide", "howto"],
    # RAG-specific
    "rag": ["retrieval", "retrieval-augmented", "knowledge retrieval"],
    "retrieval": ["search", "query", "fetch", "rag"],
    "embedding": ["vector", "vectorization", "embeddings"],
    "vector": ["embedding", "semantic", "dense"],
    # Graph terminology
    "graph": ["knowledge graph", "neo4j", "relationships"],
    "relationships": ["connections", "links", "edges", "relations"],
    "traversal": ["expansion", "navigation", "walk"],
    # Common variations
    "requirements": ["criteria", "specs", "specifications", "rules"],
    "criteria": ["requirements", "conditions", "rules"],
    "target": ["goal", "threshold", "objective"],
    "threshold": ["target", "limit", "minimum", "gate"],
}

# Compound term mappings (multi-word phrases)
COMPOUND_SYNONYMS: Dict[str, List[str]] = {
    "test driven": ["tdd", "test-driven development"],
    "knowledge graph": ["neo4j", "graph database", "entity graph"],
    "quality gate": ["threshold", "quality check", "gate"],
    "maturity model": ["maturity levels", "progression model", "capability model"],
    "best practice": ["recommendation", "guideline", "standard"],
}


def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase words, filtering tokens <= 2 chars."""
    tokens = re.findall(r"\b[a-z0-9]+(?:-[a-z0-9]+)*\b", text.lower())
    return [t for t in tokens if len(t) > 2]


def expand_query(
    query: str,
    synonyms: Dict[str, List[str]] = None,
    max_expansions_per_term: int = 3,
) -> str:
    """
    Expand a query with domain-specific synonyms.

    Args:
        query: Original query string.
        synonyms: Custom synonym mapping (uses DOMAIN_SYNONYMS if None).
        max_expansions_per_term: Maximum synonyms to add per matched term.

    Returns:
        Expanded query string with synonyms inserted.

    Example:
        >>> expand_query("What are the phases of RAG?")
        "What are the phases levels stages maturity of RAG retrieval?"
    """
    if synonyms is None:
        synonyms = DOMAIN_SYNONYMS

    tokens = _tokenize(query)
    seen_expansions: Set[str] = set(tokens)
    expansions: List[str] = []

    for token in tokens:
        if token in synonyms:
            for syn in synonyms[token][:max_expansions_per_term]:
                if syn.lower() not in seen_expansions:
                    seen_expansions.add(syn.lower())
                    expansions.append(syn)

    # Check compound terms
    query_lower = query.lower()
    for compound, syns in COMPOUND_SYNONYMS.items():
        if compound in query_lower:
            for syn in syns[:max_expansions_per_term]:
                if syn.lower() not in seen_expansions:
                    seen_expansions.add(syn.lower())
                    expansions.append(syn)

    if not expansions:
        return query

    # Append expansions to the original query
    return f"{query} {' '.join(expansions)}"


def get_synonyms(term: str) -> List[str]:
    """
    Get synonyms for a specific term.

    Args:
        term: Term to look up.

    Returns:
        List of synonyms, or empty list if not found.
    """
    return DOMAIN_SYNONYMS.get(term.lower(), [])


def add_custom_synonyms(custom: Dict[str, List[str]]) -> None:
    """
    Add custom synonyms to the domain mapping.

    Args:
        custom: Dictionary of term -> synonyms to add.
    """
    for term, syns in custom.items():
        term_lower = term.lower()
        if term_lower in DOMAIN_SYNONYMS:
            existing = set(DOMAIN_SYNONYMS[term_lower])
            DOMAIN_SYNONYMS[term_lower] = list(existing.union(set(syns)))
        else:
            DOMAIN_SYNONYMS[term_lower] = syns


if __name__ == "__main__":
    # Demo
    test_queries = [
        "What are the phases of RAG implementation?",
        "What are the TDD requirements?",
        "How do I set up the knowledge graph?",
        "What is the coverage target?",
        "Show me the maturity model levels",
    ]

    print("Query Expansion Demo\n" + "=" * 50)
    for q in test_queries:
        expanded = expand_query(q)
        print(f"\nOriginal: {q}")
        print(f"Expanded: {expanded}")
