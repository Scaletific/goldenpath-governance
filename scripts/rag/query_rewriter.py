#!/usr/bin/env python3
"""
---
id: SCRIPT-0082
type: script
owner: platform-team
status: active
maturity: 2
last_validated: 2026-02-03
test:
  runner: pytest
  command: "pytest -q tests/unit/test_query_rewriter.py"
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
  - SCRIPT-0081-query-expansion
---
Purpose: LLM-based query rewriting for improved retrieval (L2.0).

Transforms user queries into optimized search queries using an LLM.
This enables semantic understanding of user intent and bridges
terminology gaps that static synonym expansion cannot handle.

Example:
    >>> from scripts.rag.query_rewriter import rewrite_query
    >>> rewrite_query("What are the phases of RAG implementation?")
    "Find governance documents about RAG maturity levels L0 L1 L2 L3 L4..."
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Any

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatPromptTemplate = None


# Reuse LLM creation from llm_synthesis
def _create_llm(
    provider: str, model: Optional[str] = None, temperature: float = 0.1
) -> Optional[Any]:
    """Create LLM instance for query rewriting."""
    try:
        from scripts.rag.llm_synthesis import _create_llm as create_llm_base

        # Get default model for provider
        if model is None:
            if provider == "gemini":
                model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            elif provider == "claude":
                model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
            elif provider == "openai":
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            else:
                model = os.getenv("OLLAMA_MODEL", "llama3.2")

        return create_llm_base(provider=provider, model=model, temperature=temperature)
    except Exception:
        return None


# Prompt template for query rewriting
REWRITE_PROMPT_TEMPLATE = """You are a search query optimizer for a governance documentation system.

Your task is to rewrite the user's question into an optimized search query that will find relevant governance documents (policies, ADRs, runbooks).

Guidelines:
1. Expand acronyms and abbreviations (TDD = test-driven development, RAG = retrieval-augmented generation)
2. Add synonyms for key terms (phases = levels = stages = maturity)
3. Include document type hints (governance, policy, ADR, runbook)
4. Keep the core intent but optimize for keyword matching
5. Output ONLY the rewritten query, no explanation

User question: {query}

Optimized search query:"""


@dataclass
class QueryRewriter:
    """
    LLM-based query rewriter for improved retrieval.

    L2.0 Enhancement: Uses an LLM to transform user queries into
    optimized search queries that better match indexed document terminology.

    Attributes:
        provider: LLM provider ("ollama", "claude", "openai", "gemini").
        model: Model name for the provider.
        temperature: LLM temperature (default: 0.1 for consistent rewrites).
    """

    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini"))
    model: Optional[str] = None
    temperature: float = 0.1
    _llm: Any = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Initialize LLM."""
        self._llm = _create_llm(
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
        )

    def is_available(self) -> bool:
        """Check if query rewriting is available."""
        return self._llm is not None and LANGCHAIN_AVAILABLE

    def rewrite(self, query: str) -> str:
        """
        Rewrite a query for improved retrieval.

        Args:
            query: Original user query.

        Returns:
            Optimized search query, or original if rewriting fails.
        """
        if not self.is_available():
            return query

        try:
            prompt = ChatPromptTemplate.from_template(REWRITE_PROMPT_TEMPLATE)
            chain = prompt | self._llm
            response = chain.invoke({"query": query})
            rewritten = response.content.strip()

            # Sanity check: don't return empty or very short rewrites
            if len(rewritten) < 5:
                return query

            return rewritten
        except Exception:
            return query


def rewrite_query(
    query: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """
    Convenience function to rewrite a query.

    Args:
        query: Original user query.
        provider: LLM provider (default: from env).
        model: Model name (default: provider default).

    Returns:
        Optimized search query.
    """
    rewriter = QueryRewriter(
        provider=provider or os.getenv("LLM_PROVIDER", "gemini"),
        model=model,
    )
    return rewriter.rewrite(query)


if __name__ == "__main__":
    # Demo
    test_queries = [
        "What are the phases of RAG implementation?",
        "How do I set up TDD?",
        "What is the coverage target?",
    ]

    print("Query Rewriter Demo (L2.0)\n" + "=" * 50)
    for q in test_queries:
        rewritten = rewrite_query(q)
        print(f"\nOriginal:  {q}")
        print(f"Rewritten: {rewritten}")
