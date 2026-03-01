#!/usr/bin/env python3
"""
---
id: SCRIPT-0088
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-03-01
test:
  runner: pytest
  command: "pytest -q tests/unit/test_mcp_server.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-00governance-rag-mcp-server
  - GOV-0017-tdd-and-determinism
  - SCRIPT-0079-hybrid-retriever
  - SCRIPT-0073-retriever
---
MCP server exposing the Governance RAG pipeline as a tool for AI agents.

Wraps HybridRetriever (BM25 + vector + Neo4j graph expansion) with graceful
fallback to GovernanceRetriever if hybrid init fails.

Any MCP-compatible client (Claude Code, Claude Desktop, LangChain agents) can
call the query_governance tool to retrieve relevant governance context —
ADRs, PRDs, policies, runbooks, and session captures — without manually
searching the repository.

Runtime (via Claude Code):
    Configured in .claude/settings.json — auto-discovered on startup.
    uv run --with mcp python -m scripts.rag.mcp_server

Runtime (standalone):
    uv run --with mcp python -m scripts.rag.mcp_server
"""

from mcp.server.fastmcp import FastMCP

from scripts.rag.hybrid_retriever import HybridRetriever
from scripts.rag.retriever import GovernanceRetriever

mcp = FastMCP("governance-rag")


def _get_retriever():
    """Initialise HybridRetriever; fall back to GovernanceRetriever on failure.

    Returns:
        (retriever, is_hybrid) tuple so callers know which query interface to use.
        HybridRetriever provides BM25 + vector + Neo4j graph expansion.
        GovernanceRetriever provides vector-only search as a safe fallback.
    """
    try:
        return HybridRetriever(use_bm25=True, expand_depth=1), True
    except Exception:
        return GovernanceRetriever(), False


@mcp.tool()
def query_governance(
    question: str,
    top_k: int = 5,
    expand_graph: bool = True,
    use_bm25: bool = True,
    point_in_time: str = "",
) -> str:
    """Query governance documents for context relevant to the question.

    Searches ADRs, PRDs, policies, runbooks, and session captures using
    hybrid retrieval (BM25 + vector similarity + Neo4j graph expansion).
    Returns structured results with document IDs, file paths, relevance
    scores, retrieval source, and related document references.

    Use when answering questions about:
    - Platform architecture decisions (ADRs)
    - Product requirements and implementation status (PRDs)
    - Governance policies (GOV-* documents)
    - Operational procedures and runbooks
    - Historical session context and decisions made

    Args:
        question: The question to search for in governance documents.
        top_k: Number of results to return (default 5, max 20).
        expand_graph: Include Neo4j graph-adjacent documents (default True).
        use_bm25: Enable BM25 sparse retrieval alongside vector search (default True).
        point_in_time: ISO timestamp for temporal filtering, e.g. "2026-01-01T00:00:00Z".
                       Leave empty for current state.
    """
    retriever, is_hybrid = _get_retriever()
    try:
        pit = point_in_time if point_in_time else None

        if is_hybrid:
            results = retriever.query(
                query_text=question,
                top_k=top_k,
                expand_graph=expand_graph,
                use_bm25=use_bm25,
                point_in_time=pit,
            )
        else:
            results = retriever.query(query_text=question, top_k=top_k)

        if not results:
            return "No relevant governance documents found for this query."

        lines = []
        for r in results:
            doc_id = r.metadata.get("doc_id", "unknown")
            file_path = r.metadata.get("file_path", "unknown")
            section = r.metadata.get("section", "")
            source = getattr(r, "source", "vector")
            related = getattr(r, "related_docs", [])
            score = round(r.score, 3)

            lines.append(f"[{doc_id}] {file_path}")
            if section:
                lines.append(f"  Section: {section}")
            lines.append(f"  Score: {score}  Source: {source}")
            if related:
                lines.append(f"  Related: {', '.join(related[:5])}")
            lines.append(f"  {r.text[:400]}")
            lines.append("---")

        return "\n".join(lines)

    except Exception as exc:
        return f"Error querying governance documents: {exc}"

    finally:
        if is_hybrid:
            retriever.close()


if __name__ == "__main__":
    mcp.run()
