#!/usr/bin/env python3
"""
---
id: SCRIPT-0073
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_retriever.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - GOV-0017-tdd-and-determinism
  - ADR-0186-llamaindex-retrieval-layer
  - PRD-0008-governance-rag-pipeline
---
Purpose: RAG Retriever for GoldenPath governance documents.

Queries ChromaDB for similar chunks based on vector similarity.
Returns ranked results with source citations for governance documents.

Phase 0 uses ChromaDB's native query for vector search.
Phase 1+ will add LlamaIndex QueryEngine for hybrid search.

Per ADR-0186: Use LlamaIndex for retrieval with ChromaDB backend.
Per PRD-0008: Return results with citations (file path + heading).

Example:
    >>> from scripts.rag.retriever import GovernanceRetriever
    >>> retriever = GovernanceRetriever()
    >>> results = retriever.query("What are the TDD requirements?")
    >>> len(results) > 0
    True
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Union
from pathlib import Path
from datetime import datetime, timezone
import json

try:
    import chromadb
except ImportError:
    chromadb = None  # Allow import without chromadb for testing

from scripts.rag.indexer import DEFAULT_COLLECTION_NAME, DEFAULT_PERSIST_DIR


# Default number of results to return
DEFAULT_TOP_K = 5
DEFAULT_USAGE_LOG = Path("reports/usage_log.jsonl")


@dataclass
class RetrievalResult:
    """
    Represents a single retrieval result with metadata and score.

    Attributes:
        id: Unique identifier for the chunk.
        text: The chunk content.
        metadata: Dictionary of metadata (doc_id, section, file_path, etc.).
        score: Relevance score (lower distance = higher relevance).
    """

    id: str
    text: str
    metadata: Dict[str, Any]
    score: float


def _get_client(persist_dir: Optional[str] = None, in_memory: bool = False):
    """
    Get a ChromaDB client.

    Args:
        persist_dir: Directory for persistent storage. If None, uses DEFAULT_PERSIST_DIR.
        in_memory: If True, use in-memory client (for testing).

    Returns:
        ChromaDB client instance.
    """
    if chromadb is None:
        raise ImportError(
            "chromadb is not installed. Install with: pip install chromadb"
        )

    if in_memory:
        return chromadb.Client()

    persist_path = persist_dir or DEFAULT_PERSIST_DIR
    return chromadb.PersistentClient(path=persist_path)


def retrieve(
    query: str,
    collection=None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_dir: Optional[str] = None,
    in_memory: bool = False,
    top_k: int = DEFAULT_TOP_K,
    filters: Optional[Dict[str, Any]] = None,
) -> List[RetrievalResult]:
    """
    Retrieve similar chunks from ChromaDB.

    Args:
        query: The search query string.
        collection: Optional existing collection. If None, gets by name.
        collection_name: Name of the collection to query.
        persist_dir: Directory for persistent storage.
        in_memory: If True, use in-memory storage.
        top_k: Number of results to return (default: 5).
        filters: Optional metadata filters (e.g., {"doc_id": "GOV-0017"}).

    Returns:
        List of RetrievalResult objects ordered by relevance.

    Example:
        >>> results = retrieve("What are the TDD requirements?")
        >>> len(results)
        5
    """
    if not query or not query.strip():
        return []

    # Get collection
    if collection is None:
        client = _get_client(persist_dir=persist_dir, in_memory=in_memory)
        collection = client.get_collection(name=collection_name)

    # Build query parameters
    query_params = {
        "query_texts": [query],
        "n_results": top_k,
    }

    # Add filters if provided
    if filters:
        query_params["where"] = filters

    # Execute query
    results = collection.query(**query_params)

    # Parse results
    retrieval_results = []

    # ChromaDB returns nested lists
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i, doc_id in enumerate(ids):
        if i < len(documents) and i < len(metadatas) and i < len(distances):
            retrieval_results.append(
                RetrievalResult(
                    id=doc_id,
                    text=documents[i],
                    metadata=metadatas[i],
                    score=distances[i],
                )
            )

    return retrieval_results


def format_citation(result: RetrievalResult) -> str:
    """
    Format a retrieval result as a markdown citation.

    Args:
        result: RetrievalResult to format.

    Returns:
        Markdown-formatted citation string.

    Example:
        >>> citation = format_citation(result)
        >>> "[GOV-0017: Purpose](docs/governance/policies/GOV-0017.md)"
    """
    doc_id = result.metadata.get("doc_id", "Unknown")
    section = result.metadata.get("section", "")
    file_path = result.metadata.get("file_path", "")

    # Format: [DOC-ID: Section](file_path)
    if section:
        label = f"{doc_id}: {section}"
    else:
        label = doc_id

    if file_path:
        return f"[{label}]({file_path})"
    else:
        return f"[{label}]"


def log_usage(
    query: str,
    top_k: int,
    filters: Optional[Dict[str, Any]] = None,
    use_graph: bool = False,
    path: Optional[Union[str, Path]] = DEFAULT_USAGE_LOG,
    timestamp: Optional[str] = None,
) -> None:
    """
    Append a usage log entry for a retrieval query.

    Args:
        query: Query text.
        top_k: Number of results requested.
        filters: Optional metadata filters.
        use_graph: Whether graph retrieval was enabled.
        path: File path for usage log (JSONL). If None, no logging.
        timestamp: Optional ISO timestamp override for determinism in tests.
    """
    if path is None:
        return
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    entry = {
        "ts": ts,
        "query": query,
        "top_k": top_k,
        "filters": filters or {},
        "use_graph": use_graph,
    }
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


@dataclass
class GovernanceRetriever:
    """
    High-level interface for retrieving governance documents.

    Provides a convenient wrapper around ChromaDB query operations
    for the governance document use case.

    Attributes:
        collection_name: Name of the ChromaDB collection.
        persist_dir: Directory for persistent storage.
        in_memory: Whether to use in-memory storage.
        collection: The underlying ChromaDB collection.

    Example:
        >>> retriever = GovernanceRetriever()
        >>> results = retriever.query("What is TDD?")
        >>> len(results) > 0
        True
    """

    collection_name: str = DEFAULT_COLLECTION_NAME
    persist_dir: Optional[str] = None
    in_memory: bool = False
    usage_log_path: Optional[Union[str, Path]] = DEFAULT_USAGE_LOG
    collection: Any = field(default=None)
    _client: Any = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Initialize the collection after dataclass init."""
        if self.collection is None:
            self._client = _get_client(
                persist_dir=self.persist_dir,
                in_memory=self.in_memory,
            )
            self.collection = self._client.get_collection(name=self.collection_name)

    def query(
        self,
        query_text: str,
        top_k: int = DEFAULT_TOP_K,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """
        Query the index for similar chunks.

        Args:
            query_text: The search query string.
            top_k: Number of results to return (default: 5).
            filters: Optional metadata filters.

        Returns:
            List of RetrievalResult objects.
        """
        results = retrieve(
            query=query_text,
            collection=self.collection,
            top_k=top_k,
            filters=filters,
        )
        log_usage(
            query=query_text,
            top_k=top_k,
            filters=filters,
            use_graph=False,
            path=self.usage_log_path,
        )
        return results

    def query_with_citations(
        self,
        query_text: str,
        top_k: int = DEFAULT_TOP_K,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query and return results with formatted citations.

        Args:
            query_text: The search query string.
            top_k: Number of results to return.
            filters: Optional metadata filters.

        Returns:
            List of dicts with 'result' and 'citation' keys.
        """
        results = self.query(query_text, top_k=top_k, filters=filters)

        return [
            {
                "result": result,
                "citation": format_citation(result),
                "text": result.text,
                "score": result.score,
            }
            for result in results
        ]
