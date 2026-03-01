#!/usr/bin/env python3
"""
---
id: SCRIPT-0076
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-29
test:
  runner: pytest
  command: "pytest -q tests/unit/test_query_cli.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
relates_to:
  - GOV-0017-tdd-and-determinism
  - ADR-0186-llamaindex-retrieval-layer
  - PRD-0008-governance-rag-pipeline
  - SCRIPT-0073-retriever
---
Purpose: CLI query tool for GoldenPath governance RAG.
SKIP-TDD: CLI is thin wrapper over retriever; integration tested manually.

Provides command-line interface to query governance documents
using the RAG retriever. Supports text and JSON output formats,
metadata filtering, and citation formatting.

Per PRD-0008: CLI interface for `gov-rag query "..."` pattern.
Per ADR-0186: Returns results with citations (file path + heading).

Example:
    >>> # Query governance documents
    >>> python -m scripts.rag.cli query "What are TDD requirements?"

    >>> # Query with JSON output
    >>> python -m scripts.rag.cli query "coverage targets" --format json

    >>> # Query with filters
    >>> python -m scripts.rag.cli query "testing" --filter doc_type=governance
"""

import argparse
import json
import sys
from enum import Enum
from typing import Any, Dict, List, Optional

from scripts.rag.retriever import GovernanceRetriever, RetrievalResult, format_citation


class OutputFormat(Enum):
    """Output format options for CLI results."""

    TEXT = "text"
    JSON = "json"


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: List of argument strings. If None, uses sys.argv.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="gov-rag",
        description="Query GoldenPath governance documents using RAG",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query governance documents")
    query_parser.add_argument(
        "query",
        nargs="?",
        help="Search query string",
    )
    query_parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)",
    )
    query_parser.add_argument(
        "--filter",
        "-f",
        type=str,
        action="append",
        default=None,
        help="Metadata filter in key=value format (can be repeated, e.g., -f type=policy -f domain=security)",
    )
    query_parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    query_parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="ChromaDB collection name",
    )
    query_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output including query metadata",
    )
    query_parser.add_argument(
        "--no-citations",
        action="store_true",
        help="Exclude citations from output",
    )
    query_parser.add_argument(
        "--hybrid",
        action="store_true",
        help="Use hybrid retrieval (vector + BM25 + graph expansion)",
    )
    query_parser.add_argument(
        "--no-bm25",
        action="store_true",
        help="Disable BM25 sparse retrieval (vector-only)",
    )
    query_parser.add_argument(
        "--no-graph",
        action="store_true",
        help="Disable graph expansion (vector/BM25 only)",
    )
    query_parser.add_argument(
        "--expand-depth",
        type=int,
        default=1,
        help="Graph expansion depth for multi-hop traversal (default: 1)",
    )
    query_parser.add_argument(
        "--point-in-time",
        type=str,
        default=None,
        help="ISO timestamp for temporal graph queries (ADR-0185)",
    )
    query_parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Generate LLM-synthesized answer",
    )
    query_parser.add_argument(
        "--contract",
        action="store_true",
        help="Output contract-compliant JSON (requires --synthesize)",
    )
    query_parser.add_argument(
        "--provider",
        type=str,
        choices=["ollama", "claude", "openai", "gemini"],
        default=None,
        help="LLM provider for synthesis (default: from env)",
    )
    query_parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name for synthesis (provider-specific)",
    )
    query_parser.add_argument(
        "--agentic",
        action="store_true",
        help="Use agentic RAG with iterative query refinement (L3.0)",
    )
    query_parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum iterations for agentic mode (default: 3)",
    )
    query_parser.add_argument(
        "--show-trace",
        action="store_true",
        help="Show reasoning trace in agentic mode",
    )

    return parser.parse_args(args)


def parse_filter_string(filter_string: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Parse a single filter string into a dictionary.

    Args:
        filter_string: Filter in "key=value" format.

    Returns:
        Dictionary with filter key-value pair, or None.
    """
    if not filter_string:
        return None

    if "=" not in filter_string:
        return None

    key, value = filter_string.split("=", 1)
    return {key.strip(): value.strip()}


def parse_filters(filter_list: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    """
    Parse multiple filter strings into a combined dictionary.

    Supports ChromaDB where clause syntax:
    - Single value: {"key": "value"}
    - Multiple values for same key: {"key": {"$in": ["val1", "val2"]}}

    Args:
        filter_list: List of "key=value" strings.

    Returns:
        Combined filter dictionary for ChromaDB where clause.

    Examples:
        >>> parse_filters(["type=policy"])
        {"type": "policy"}
        >>> parse_filters(["type=policy", "domain=security"])
        {"$and": [{"type": "policy"}, {"domain": "security"}]}
    """
    if not filter_list:
        return None

    filters = []
    for f in filter_list:
        parsed = parse_filter_string(f)
        if parsed:
            filters.append(parsed)

    if not filters:
        return None

    if len(filters) == 1:
        return filters[0]

    # Multiple filters: use $and operator
    return {"$and": filters}


def run_query(
    query: str,
    retriever: Optional[GovernanceRetriever] = None,
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    filter_string: Optional[str] = None,
) -> List[RetrievalResult]:
    """
    Execute a retrieval query.

    Args:
        query: Search query string.
        retriever: GovernanceRetriever instance. If None, creates one.
        top_k: Number of results to return.
        filters: Metadata filters as dictionary.
        filter_string: Metadata filter as string (alternative to filters).

    Returns:
        List of RetrievalResult objects.
    """
    if retriever is None:
        retriever = GovernanceRetriever(usage_log_path=None)

    # Parse filter string if provided
    if filter_string and not filters:
        filters = parse_filter_string(filter_string)

    return retriever.query(query, top_k=top_k, filters=filters)


def format_results(
    results: List[RetrievalResult],
    format_type: OutputFormat = OutputFormat.TEXT,
    include_citations: bool = True,
) -> str:
    """
    Format retrieval results for output.

    Args:
        results: List of RetrievalResult objects.
        format_type: Output format (TEXT or JSON).
        include_citations: Whether to include citations.

    Returns:
        Formatted string output.
    """
    if not results:
        if format_type == OutputFormat.JSON:
            return json.dumps({"results": [], "count": 0}, indent=2)
        return "No results found."

    if format_type == OutputFormat.JSON:
        json_results = []
        for result in results:
            item = {
                "id": result.id,
                "text": result.text,
                "metadata": result.metadata,
                "score": result.score,
            }
            if include_citations:
                item["citation"] = format_citation(result)
            json_results.append(item)

        return json.dumps(
            {"results": json_results, "count": len(json_results)}, indent=2
        )

    # Text format
    lines = []
    for i, result in enumerate(results, 1):
        lines.append(f"--- Result {i} ---")
        if include_citations:
            citation = format_citation(result)
            lines.append(f"Source: {citation}")
        lines.append(f"Score: {result.score:.4f}")
        lines.append("")
        lines.append(result.text)
        lines.append("")

    return "\n".join(lines)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.

    Args:
        args: Command-line arguments. If None, uses sys.argv.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        parsed = parse_args(args)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1

    if parsed.command != "query":
        print("Error: Unknown command. Use 'query' subcommand.", file=sys.stderr)
        return 1

    if not parsed.query:
        print("Error: Query argument is required.", file=sys.stderr)
        return 1

    # Validate format
    try:
        output_format = OutputFormat(parsed.format)
    except ValueError:
        print(f"Error: Invalid format '{parsed.format}'.", file=sys.stderr)
        return 1

    # Parse filters (supports multiple -f flags)
    filters = parse_filters(parsed.filter)

    # Handle agentic mode (L3.0 - includes rewriting, reranking, and synthesis)
    if getattr(parsed, "agentic", False):
        try:
            from scripts.rag.rag_agent import RAGAgent
            import os

            provider = parsed.provider or os.getenv("LLM_PROVIDER", "gemini")
            max_iterations = getattr(parsed, "max_iterations", 3)
            show_trace = getattr(parsed, "show_trace", False)

            agent = RAGAgent(
                provider=provider,
                model=parsed.model,
                max_iterations=max_iterations,
            )

            result = agent.query(question=parsed.query, top_k=parsed.top_k)
            agent.close()

            if output_format == OutputFormat.JSON:
                output = json.dumps(
                    {
                        "answer": result.answer,
                        "success": result.success,
                        "iterations": result.iterations,
                        "evidence": [
                            {
                                "doc_id": e.metadata.get("doc_id", "unknown"),
                                "section": e.metadata.get("section", ""),
                                "score": e.score,
                            }
                            for e in result.evidence[:5]
                        ],
                        "reasoning_trace": [
                            {
                                "iteration": s.iteration,
                                "state": s.state.value,
                                "query": s.query,
                                "reasoning": s.reasoning,
                            }
                            for s in result.reasoning_trace
                        ]
                        if show_trace
                        else [],
                        "model": result.model,
                    },
                    indent=2,
                )
            else:
                output = f"{result.answer}\n"
                output += f"\n---\nSuccess: {result.success} | Iterations: {result.iterations} | Model: {result.model}"

                if result.evidence:
                    output += f"\n\nEvidence ({len(result.evidence)} sources):"
                    for e in result.evidence[:5]:
                        doc_id = e.metadata.get("doc_id", "unknown")
                        output += f"\n  - {doc_id}"

                if show_trace:
                    output += "\n\nReasoning Trace:"
                    for step in result.reasoning_trace:
                        output += f"\n  [{step.iteration}] {step.state.value}: {step.reasoning}"

            if parsed.verbose:
                print(f"Query: {parsed.query}", file=sys.stderr)
                print("Mode: Agentic (L3.0)", file=sys.stderr)
                print(f"Provider: {provider}", file=sys.stderr)
                print(f"Max iterations: {max_iterations}", file=sys.stderr)
                print("---", file=sys.stderr)

            print(output)
            return 0

        except ImportError as e:
            print(f"Warning: Agentic RAG not available: {e}", file=sys.stderr)
            print("Falling back to synthesis mode...", file=sys.stderr)
            parsed.synthesize = True

    # Handle synthesize mode (includes hybrid by default)
    if parsed.synthesize:
        try:
            from scripts.rag.llm_synthesis import RAGSynthesizer, check_provider_status

            # Determine provider (use env default if not specified)
            import os

            provider = parsed.provider or os.getenv("LLM_PROVIDER", "ollama")

            # Check provider status
            status = check_provider_status(provider)
            provider_info = status["providers"].get(provider, {})

            if not provider_info.get("available"):
                error = provider_info.get("error", "unknown")
                print(f"Warning: {provider} not available: {error}", file=sys.stderr)
                print("Falling back to raw retrieval...", file=sys.stderr)
                parsed.synthesize = False
            else:
                model = parsed.model or provider_info.get("default_model")
                synthesizer = RAGSynthesizer(provider=provider, model=model)

                # Use contract output if --contract flag is set
                use_contract = getattr(parsed, "contract", False)

                if use_contract:
                    # Contract-compliant output per answer_contract.schema.json
                    contract = synthesizer.synthesize_contract(
                        question=parsed.query,
                        top_k=parsed.top_k,
                        expand_graph=True,
                        validate=True,
                    )
                    synthesizer.close()

                    # Always output JSON for contract mode
                    output = contract.to_json(indent=2)

                    if parsed.verbose:
                        print(f"Query: {parsed.query}", file=sys.stderr)
                        print(f"Model: {synthesizer.model}", file=sys.stderr)
                        print(
                            f"Evidence items: {len(contract.evidence)}", file=sys.stderr
                        )
                        print("---", file=sys.stderr)

                    print(output)
                    return 0

                # Standard synthesis (non-contract)
                result = synthesizer.synthesize(
                    question=parsed.query,
                    top_k=parsed.top_k,
                    expand_graph=True,  # Always use graph with synthesis
                )
                synthesizer.close()

                if output_format == OutputFormat.JSON:
                    output = json.dumps(
                        {
                            "answer": result.answer,
                            "citations": result.citations,
                            "model": result.model,
                            "context_chunks": result.context_chunks,
                            "source_docs": result.source_docs,
                        },
                        indent=2,
                    )
                else:
                    output = f"{result.answer}\n\n---\nSources ({result.context_chunks} chunks from {len(result.source_docs)} docs):\n"
                    for citation in result.citations[:5]:  # Limit citations shown
                        output += f"  - {citation}\n"
                    output += f"\nModel: {result.model}"

                if parsed.verbose:
                    print(f"Query: {parsed.query}", file=sys.stderr)
                    print(f"Model: {result.model}", file=sys.stderr)
                    print(f"Context chunks: {result.context_chunks}", file=sys.stderr)
                    print("---", file=sys.stderr)

                print(output)
                return 0

        except ImportError as e:
            print(f"Warning: LLM synthesis not available: {e}", file=sys.stderr)
            print("Falling back to raw retrieval...", file=sys.stderr)
            parsed.synthesize = False

    # Handle hybrid mode (vector + BM25 + graph)
    if parsed.hybrid:
        try:
            from scripts.rag.hybrid_retriever import HybridRetriever

            # Configure hybrid retriever with CLI flags
            use_bm25 = not getattr(parsed, "no_bm25", False)
            expand_graph = not getattr(parsed, "no_graph", False)
            expand_depth = getattr(parsed, "expand_depth", 1)
            point_in_time = getattr(parsed, "point_in_time", None)

            retriever = HybridRetriever(use_bm25=use_bm25, expand_depth=expand_depth)
            results = retriever.query(
                query_text=parsed.query,
                top_k=parsed.top_k,
                filters=filters,
                expand_graph=expand_graph,
                use_bm25=use_bm25,
                point_in_time=point_in_time,
            )
            retriever.close()

            # Convert HybridResult to RetrievalResult for formatting
            converted_results = [
                RetrievalResult(
                    id=r.id,
                    text=r.text,
                    metadata=r.metadata,
                    score=r.score,
                )
                for r in results
            ]

            if parsed.verbose:
                print(f"BM25 enabled: {use_bm25}", file=sys.stderr)
                print(f"Graph expansion: {expand_graph}", file=sys.stderr)
                print(f"Expand depth: {expand_depth}", file=sys.stderr)
                if point_in_time:
                    print(f"Point-in-time: {point_in_time}", file=sys.stderr)

        except ImportError as e:
            print(f"Warning: Hybrid retrieval not available: {e}", file=sys.stderr)
            print("Falling back to vector-only retrieval...", file=sys.stderr)
            parsed.hybrid = False

    # Standard vector-only retrieval
    if not parsed.hybrid and not parsed.synthesize:
        try:
            retriever_kwargs = {"usage_log_path": None}
            if parsed.collection:
                retriever_kwargs["collection_name"] = parsed.collection
            retriever = GovernanceRetriever(**retriever_kwargs)
        except Exception as e:
            print(f"Error: Failed to initialize retriever: {e}", file=sys.stderr)
            return 1

        try:
            converted_results = run_query(
                query=parsed.query,
                retriever=retriever,
                top_k=parsed.top_k,
                filters=filters,
            )
        except Exception as e:
            print(f"Error: Query failed: {e}", file=sys.stderr)
            return 1

    # Format output for non-synthesis modes
    include_citations = not parsed.no_citations
    output = format_results(
        converted_results,
        format_type=output_format,
        include_citations=include_citations,
    )

    # Print verbose info if requested
    if parsed.verbose:
        print(f"Query: {parsed.query}", file=sys.stderr)
        print(f"Top-K: {parsed.top_k}", file=sys.stderr)
        if filters:
            print(f"Filters: {filters}", file=sys.stderr)
        print(f"Results: {len(converted_results)}", file=sys.stderr)
        print("---", file=sys.stderr)

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
