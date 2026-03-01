#!/usr/bin/env python3
"""
---
id: SCRIPT-0083
type: script
owner: platform-team
status: active
maturity: 2
last_validated: 2026-02-03
test:
  runner: pytest
  command: "pytest -q tests/unit/test_result_reranker.py"
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
  - SCRIPT-0082-query-rewriter
---
Purpose: LLM-based result re-ranking for improved relevance (L2.5).

Re-ranks retrieval results using an LLM to filter irrelevant chunks
before synthesis. This addresses the issue where keyword/vector search
returns documents with matching terms but unrelated content.

Example:
    >>> from scripts.rag.result_reranker import rerank_results
    >>> ranked = rerank_results("RAG phases", retrieval_results)
    >>> # Only relevant results remain, sorted by relevance
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional, Any, List, Union

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatPromptTemplate = None

from scripts.rag.hybrid_retriever import HybridResult
from scripts.rag.retriever import RetrievalResult


def _create_llm(
    provider: str, model: Optional[str] = None, temperature: float = 0.1
) -> Optional[Any]:
    """Create LLM instance for reranking."""
    try:
        from scripts.rag.llm_synthesis import _create_llm as create_llm_base

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


# Prompt template for result re-ranking
RERANK_PROMPT_TEMPLATE = """You are a relevance judge for a governance documentation search system.

Given a user's question and a list of retrieved text chunks, score each chunk's relevance to answering the question.

User Question: {query}

Retrieved Chunks:
{chunks}

For each chunk, provide a JSON array with objects containing:
- "index": the chunk number (0-indexed)
- "score": relevance score from 0.0 (irrelevant) to 1.0 (directly answers the question)
- "reasoning": brief explanation of the score

Scoring guide:
- 1.0: Directly and completely answers the question
- 0.8: Highly relevant, provides key information
- 0.6: Moderately relevant, provides useful context
- 0.4: Tangentially related, mentions similar topics
- 0.2: Barely related, only shares keywords
- 0.0: Completely irrelevant

Output ONLY valid JSON array, no other text:"""


@dataclass
class RankedResult:
    """Result with relevance score from re-ranking."""

    result: Union[HybridResult, RetrievalResult]
    relevance_score: float
    reasoning: str


@dataclass
class ResultReranker:
    """
    LLM-based result re-ranker for improved relevance filtering.

    L2.5 Enhancement: Uses an LLM to evaluate retrieval results and
    filter out irrelevant chunks before synthesis.

    Attributes:
        provider: LLM provider ("ollama", "claude", "openai", "gemini").
        model: Model name for the provider.
        relevance_threshold: Minimum score to keep (default: 0.5).
        temperature: LLM temperature (default: 0.1).
    """

    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini"))
    model: Optional[str] = None
    relevance_threshold: float = 0.5
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
        """Check if re-ranking is available."""
        return self._llm is not None and LANGCHAIN_AVAILABLE

    def rerank(
        self,
        query: str,
        results: List[Union[HybridResult, RetrievalResult]],
        filter_below_threshold: bool = True,
    ) -> List[RankedResult]:
        """
        Re-rank results by relevance to the query.

        Args:
            query: User's question.
            results: List of retrieval results to re-rank.
            filter_below_threshold: Whether to filter low-scoring results.

        Returns:
            List of RankedResult objects, sorted by relevance descending.
        """
        if not results:
            return []

        if not self.is_available():
            # Return all results with default score if LLM unavailable
            return [
                RankedResult(
                    result=r,
                    relevance_score=0.5,
                    reasoning="LLM unavailable, using default score",
                )
                for r in results
            ]

        try:
            # Format chunks for the prompt
            chunks_text = self._format_chunks(results)

            prompt = ChatPromptTemplate.from_template(RERANK_PROMPT_TEMPLATE)
            chain = prompt | self._llm
            response = chain.invoke({"query": query, "chunks": chunks_text})

            # Parse JSON response
            scores = self._parse_scores(response.content, len(results))

            # Build ranked results
            ranked = []
            for i, result in enumerate(results):
                score_info = scores.get(i, {"score": 0.5, "reasoning": "Not scored"})
                ranked.append(
                    RankedResult(
                        result=result,
                        relevance_score=score_info["score"],
                        reasoning=score_info["reasoning"],
                    )
                )

            # Sort by relevance descending
            ranked.sort(key=lambda x: x.relevance_score, reverse=True)

            # Filter below threshold if requested
            if filter_below_threshold:
                ranked = [
                    r for r in ranked if r.relevance_score >= self.relevance_threshold
                ]

            return ranked

        except Exception as e:
            # On failure, return all results with default scores
            return [
                RankedResult(
                    result=r,
                    relevance_score=0.5,
                    reasoning=f"Reranking failed: {e}",
                )
                for r in results
            ]

    def _format_chunks(
        self, results: List[Union[HybridResult, RetrievalResult]]
    ) -> str:
        """Format chunks for the prompt."""
        lines = []
        for i, result in enumerate(results):
            doc_id = result.metadata.get("doc_id", "Unknown")
            section = result.metadata.get("section", "")
            text = result.text[:500]  # Truncate for prompt length
            lines.append(f"[{i}] {doc_id} - {section}\n{text}\n")
        return "\n---\n".join(lines)

    def _parse_scores(self, response: str, num_results: int) -> dict:
        """Parse LLM response into scores dict."""
        scores = {}

        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            parsed = json.loads(response.strip())

            if isinstance(parsed, list):
                for item in parsed:
                    idx = item.get("index", -1)
                    if 0 <= idx < num_results:
                        scores[idx] = {
                            "score": min(1.0, max(0.0, float(item.get("score", 0.5)))),
                            "reasoning": item.get("reasoning", "No reasoning"),
                        }
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

        return scores


def rerank_results(
    query: str,
    results: List[Union[HybridResult, RetrievalResult]],
    provider: Optional[str] = None,
    threshold: float = 0.5,
) -> List[RankedResult]:
    """
    Convenience function to re-rank results.

    Args:
        query: User's question.
        results: List of retrieval results.
        provider: LLM provider (default: from env).
        threshold: Minimum relevance score to keep.

    Returns:
        List of RankedResult objects, filtered and sorted.
    """
    reranker = ResultReranker(
        provider=provider or os.getenv("LLM_PROVIDER", "gemini"),
        relevance_threshold=threshold,
    )
    return reranker.rerank(query, results)


if __name__ == "__main__":
    print("Result Reranker Demo (L2.5)")
    print("=" * 50)
    print("Use with retrieval results from HybridRetriever")
