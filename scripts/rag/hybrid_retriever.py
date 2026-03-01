#!/usr/bin/env python3
"""
---
id: SCRIPT-0079
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-02-03
test:
  runner: pytest
  command: "pytest -q tests/unit/test_hybrid_retriever.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0020-rag-maturity-model
  - GOV-0017-tdd-and-determinism
  - SCRIPT-0073-retriever
  - SCRIPT-0074-graph-client
  - SCRIPT-0082-query-rewriter
---
Purpose: Hybrid retriever combining vector similarity + BM25 + graph traversal.

Phase 1 (L1) implementation per GOV-0020:
- Vector similarity search (ChromaDB)
- BM25 sparse retrieval (keyword matching)
- Graph expansion (Neo4j relationships)
- Temporal filtering (ADR-0185)
- L2.0: LLM-based query rewriting with static expansion fallback
"""

import os
import re
from collections import Counter
from dataclasses import dataclass, field
from math import log
from typing import List, Optional, Dict, Any, Set, Tuple

from scripts.rag.retriever import (
    GovernanceRetriever,
    RetrievalResult,
    format_citation,
    log_usage,
    DEFAULT_TOP_K,
)
from scripts.rag.query_expansion import expand_query

try:
    from scripts.rag.query_rewriter import QueryRewriter
except ImportError:
    QueryRewriter = None

try:
    from scripts.rag.graph_client import create_client_from_env, Neo4jGraphClient
except ImportError:
    Neo4jGraphClient = None


@dataclass
class HybridResult:
    """Result from hybrid retrieval with source tracking."""

    id: str
    text: str
    metadata: Dict[str, Any]
    score: float
    source: str  # "vector", "graph", "bm25", or "both"
    related_docs: List[str] = field(default_factory=list)
    bm25_score: Optional[float] = None
    vector_score: Optional[float] = None


# =============================================================================
# BM25 Sparse Retrieval (Phase 1 L1)
# =============================================================================


def _tokenize(text: str) -> List[str]:
    """Simple tokenizer for BM25."""
    # Lowercase, split on non-alphanumeric, filter short tokens
    tokens = re.findall(r"\b[a-z0-9]+\b", text.lower())
    return [t for t in tokens if len(t) > 2]


class SimpleBM25:
    """
    Simple BM25 implementation for sparse retrieval.

    BM25 parameters:
    - k1: Term frequency saturation (default: 1.5)
    - b: Length normalization (default: 0.75)
    """

    def __init__(
        self,
        documents: List[str],
        doc_ids: List[str],
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.k1 = k1
        self.b = b
        self.doc_ids = doc_ids
        self.corpus = [_tokenize(doc) for doc in documents]
        self.doc_len = [len(doc) for doc in self.corpus]
        self.avgdl = sum(self.doc_len) / len(self.doc_len) if self.doc_len else 1
        self.N = len(self.corpus)

        # Build document frequency index
        self.df = Counter()
        for doc in self.corpus:
            for term in set(doc):
                self.df[term] += 1

        # Pre-compute IDF
        self.idf = {}
        for term, df in self.df.items():
            self.idf[term] = log((self.N - df + 0.5) / (df + 0.5) + 1)

    def score(self, query: str, doc_idx: int) -> float:
        """Calculate BM25 score for a single document."""
        query_tokens = _tokenize(query)
        doc_tokens = self.corpus[doc_idx]
        doc_len = self.doc_len[doc_idx]

        tf = Counter(doc_tokens)
        score = 0.0

        for term in query_tokens:
            if term not in self.idf:
                continue
            term_freq = tf.get(term, 0)
            numerator = self.idf[term] * term_freq * (self.k1 + 1)
            denominator = term_freq + self.k1 * (
                1 - self.b + self.b * doc_len / self.avgdl
            )
            score += numerator / denominator

        return score

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Search and return top-k (doc_id, score) pairs."""
        scores = []
        for idx in range(self.N):
            s = self.score(query, idx)
            if s > 0:
                scores.append((self.doc_ids[idx], s))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


def _build_bm25_index(retriever: "GovernanceRetriever") -> Optional[SimpleBM25]:
    """
    Build BM25 index from ChromaDB collection.

    Returns None if collection is empty or unavailable.
    """
    try:
        # Get all documents from collection
        collection = retriever.collection
        result = collection.get(include=["documents", "metadatas"])

        if not result or not result.get("ids"):
            return None

        doc_ids = result["ids"]
        documents = result.get("documents", [])

        if not documents:
            return None

        return SimpleBM25(documents=documents, doc_ids=doc_ids)
    except Exception:
        return None


def _graph_client_from_env() -> Optional["Neo4jGraphClient"]:
    """Create graph client if env vars are set."""
    if Neo4jGraphClient is None:
        return None
    uri = os.getenv("NEO4J_URI")
    password = os.getenv("NEO4J_PASSWORD")
    if not uri or not password:
        return None
    try:
        return create_client_from_env()
    except Exception:
        return None


def expand_via_graph(
    doc_ids: Set[str],
    graph_client: "Neo4jGraphClient",
    max_depth: int = 1,
    rel_types: Optional[List[str]] = None,
) -> Dict[str, List[str]]:
    """
    Expand document IDs via graph relationships.

    Args:
        doc_ids: Set of document IDs to expand from.
        graph_client: Neo4j graph client.
        max_depth: How many hops to traverse (default: 1).
        rel_types: Relationship types to follow. Default: all.

    Returns:
        Dict mapping source doc_id to list of related doc_ids.
    """
    if not doc_ids or graph_client is None:
        return {}

    # Build Cypher query with depth-aware expansion
    rel_filter = ""
    if rel_types:
        rel_filter = ":" + "|".join(rel_types)

    depth = max(1, int(max_depth))
    rel_pattern = f"-[r{rel_filter}*1..{depth}]-"

    query = f"""
    MATCH (src:Document){rel_pattern}(related:Document)
    WHERE src.id IN $doc_ids
    RETURN src.id AS source, collect(DISTINCT related.id) AS related
    """

    expanded = {}
    try:
        with graph_client._driver.session() as session:
            result = session.run(query, {"doc_ids": list(doc_ids)})
            for record in result:
                expanded[record["source"]] = record["related"]
    except Exception:
        pass

    return expanded


def fetch_chunks_for_docs(
    doc_ids: List[str],
    retriever: GovernanceRetriever,
    top_k_per_doc: int = 2,
) -> List[RetrievalResult]:
    """
    Fetch chunks for specific document IDs from vector store.

    Args:
        doc_ids: List of document IDs to fetch.
        retriever: GovernanceRetriever instance.
        top_k_per_doc: Max chunks per document.

    Returns:
        List of RetrievalResult objects.
    """
    results = []
    seen_ids = set()

    for doc_id in doc_ids:
        try:
            # Deterministic lookup by metadata (no embedding query)
            collection = retriever.collection
            chunk_data = collection.get(
                where={"doc_id": doc_id},
                include=["documents", "metadatas", "ids"],
            )

            ids = chunk_data.get("ids", []) if chunk_data else []
            documents = chunk_data.get("documents", []) if chunk_data else []
            metadatas = chunk_data.get("metadatas", []) if chunk_data else []

            # Sort by chunk_index (fallback to id for stability)
            packed = []
            for idx, chunk_id in enumerate(ids):
                meta = metadatas[idx] if idx < len(metadatas) else {}
                doc = documents[idx] if idx < len(documents) else ""
                chunk_index = meta.get("chunk_index", idx)
                packed.append((chunk_index, chunk_id, doc, meta))

            packed.sort(key=lambda item: (item[0], item[1]))

            for _, chunk_id, doc, meta in packed[:top_k_per_doc]:
                if chunk_id in seen_ids:
                    continue
                seen_ids.add(chunk_id)
                results.append(
                    RetrievalResult(
                        id=chunk_id,
                        text=doc,
                        metadata=meta,
                        score=0.0,
                    )
                )
        except Exception:
            continue

    return results


@dataclass
class HybridRetriever:
    """
    Hybrid retriever combining vector + BM25 + graph retrieval.

    Phase 1 (L1) implementation per GOV-0020 Agentic Graph RAG Maturity Model.

    Flow:
    1. Query ChromaDB for top-k semantically similar chunks (dense)
    2. Query BM25 for keyword matches (sparse)
    3. Fuse results using Reciprocal Rank Fusion (RRF)
    4. Query Neo4j for related documents (graph expansion)
    5. Fetch chunks for related documents
    6. Return merged and ranked results

    Attributes:
        vector_retriever: GovernanceRetriever for vector search.
        graph_client: Optional Neo4j client for graph expansion.
        query_rewriter: Optional QueryRewriter for LLM-based query rewriting (L2.0).
        expand_depth: Graph traversal depth (default: 1).
        rel_types: Relationship types to follow (default: all).
        use_bm25: Enable BM25 sparse retrieval (default: True).
        bm25_weight: Weight for BM25 scores in fusion (default: 0.3).
        vector_weight: Weight for vector scores in fusion (default: 0.7).
    """

    vector_retriever: GovernanceRetriever = field(default_factory=GovernanceRetriever)
    graph_client: Optional[Any] = None
    query_rewriter: Optional[Any] = None  # L2.0: LLM-based query rewriting
    expand_depth: int = 1
    rel_types: Optional[List[str]] = None
    use_bm25: bool = True
    bm25_weight: float = 0.3
    vector_weight: float = 0.7
    expand_queries: bool = True  # L1.5: Expand queries with domain synonyms
    _auto_close_graph: bool = field(default=False, repr=False)
    _bm25_index: Optional[SimpleBM25] = field(default=None, repr=False)

    def __post_init__(self):
        """Initialize graph client and BM25 index if not provided."""
        if self.graph_client is None:
            self.graph_client = _graph_client_from_env()
            if self.graph_client is not None:
                self._auto_close_graph = True

        # Build BM25 index lazily on first query
        self._bm25_index = None

    def _get_bm25_index(self) -> Optional[SimpleBM25]:
        """Lazily build BM25 index."""
        if self._bm25_index is None and self.use_bm25:
            self._bm25_index = _build_bm25_index(self.vector_retriever)
        return self._bm25_index

    def close(self):
        """Close graph client if auto-created."""
        if self._auto_close_graph and self.graph_client is not None:
            self.graph_client.close()
            self.graph_client = None

    def query(
        self,
        query_text: str,
        top_k: int = DEFAULT_TOP_K,
        filters: Optional[Dict[str, Any]] = None,
        expand_graph: bool = True,
        graph_top_k: int = 3,
        use_bm25: Optional[bool] = None,
        point_in_time: Optional[str] = None,
        expand_query_synonyms: Optional[bool] = None,
    ) -> List[HybridResult]:
        """
        Execute hybrid query combining vector + BM25 + graph retrieval.

        Phase 1 (L1) per GOV-0020: Combines dense (vector) and sparse (BM25)
        retrieval with graph expansion for comprehensive results.

        L2.0 Enhancement: LLM-based query rewriting produces optimized search
        queries. Falls back to L1.5 static synonym expansion if rewriter is
        unavailable or returns the original query unchanged.

        Args:
            query_text: The search query string.
            top_k: Number of results to return.
            filters: Optional metadata filters for vector search.
            expand_graph: Whether to expand via graph (default: True).
            graph_top_k: Max results from graph expansion per source doc.
            use_bm25: Override instance setting for BM25 (default: use instance).
            point_in_time: ISO timestamp for temporal graph queries (ADR-0185).
            expand_query_synonyms: Expand query with synonyms (default: use instance).

        Returns:
            List of HybridResult objects, ranked by relevance.
        """
        should_use_bm25 = use_bm25 if use_bm25 is not None else self.use_bm25
        should_expand = (
            expand_query_synonyms
            if expand_query_synonyms is not None
            else self.expand_queries
        )

        # Query translation: L2.0 LLM rewriting → L1.5 static expansion → raw
        effective_query = query_text
        if should_expand:
            rewritten = None
            if self.query_rewriter is not None and self.query_rewriter.is_available():
                rewritten = self.query_rewriter.rewrite(query_text)

            if rewritten and rewritten != query_text:
                # L2.0: LLM produced a different query — use it directly
                effective_query = rewritten
            else:
                # L1.5 fallback: static synonym expansion
                effective_query = expand_query(query_text)

        # Step 1: Vector search (dense retrieval)
        vector_results = self.vector_retriever.query(
            query_text=effective_query,
            top_k=top_k * 2 if should_use_bm25 else top_k,  # Get more for fusion
            filters=filters,
        )

        # Build result map keyed by chunk ID
        result_map: Dict[str, HybridResult] = {}

        for rank, result in enumerate(vector_results):
            result_map[result.id] = HybridResult(
                id=result.id,
                text=result.text,
                metadata=result.metadata,
                score=result.score,
                source="vector",
                related_docs=[],
                vector_score=result.score,
                bm25_score=None,
            )

        # Step 2: BM25 search (sparse retrieval)
        if should_use_bm25:
            bm25_index = self._get_bm25_index()
            if bm25_index is not None:
                bm25_results = bm25_index.search(effective_query, top_k=top_k * 2)

                for rank, (chunk_id, bm25_score) in enumerate(bm25_results):
                    if chunk_id in result_map:
                        # Update existing result with BM25 score
                        result_map[chunk_id].bm25_score = bm25_score
                        result_map[chunk_id].source = "both"
                    else:
                        # Fetch chunk details from collection
                        try:
                            chunk_data = self.vector_retriever.collection.get(
                                ids=[chunk_id],
                                include=["documents", "metadatas"],
                            )
                            if chunk_data and chunk_data.get("ids"):
                                result_map[chunk_id] = HybridResult(
                                    id=chunk_id,
                                    text=chunk_data["documents"][0]
                                    if chunk_data.get("documents")
                                    else "",
                                    metadata=chunk_data["metadatas"][0]
                                    if chunk_data.get("metadatas")
                                    else {},
                                    score=1.0,  # Will be recalculated
                                    source="bm25",
                                    related_docs=[],
                                    vector_score=None,
                                    bm25_score=bm25_score,
                                )
                        except Exception:
                            pass

        # Step 3: Compute fused scores using Reciprocal Rank Fusion (RRF)
        # Sort by vector score to get ranks
        vector_ranked = sorted(
            [r for r in result_map.values() if r.vector_score is not None],
            key=lambda x: x.vector_score,
        )
        vector_ranks = {r.id: i + 1 for i, r in enumerate(vector_ranked)}

        # Sort by BM25 score (descending) to get ranks
        bm25_ranked = sorted(
            [r for r in result_map.values() if r.bm25_score is not None],
            key=lambda x: x.bm25_score,
            reverse=True,
        )
        bm25_ranks = {r.id: i + 1 for i, r in enumerate(bm25_ranked)}

        # RRF fusion: score = sum(1 / (k + rank)) for each ranker
        k = 60  # RRF constant
        for chunk_id, result in result_map.items():
            rrf_score = 0.0
            if chunk_id in vector_ranks:
                rrf_score += self.vector_weight / (k + vector_ranks[chunk_id])
            if chunk_id in bm25_ranks:
                rrf_score += self.bm25_weight / (k + bm25_ranks[chunk_id])
            # Convert RRF to distance-like score (lower is better)
            result.score = 1.0 - rrf_score if rrf_score > 0 else result.score

        # Step 4: Graph expansion (if enabled and client available)
        seen_chunks = set(result_map.keys())

        if expand_graph and self.graph_client is not None:
            # Extract unique doc_ids from results
            doc_ids = set()
            for result in result_map.values():
                doc_id = result.metadata.get("doc_id")
                if doc_id:
                    doc_ids.add(doc_id)

            # Use temporal-aware graph expansion if client supports it
            if hasattr(self.graph_client, "get_related_documents"):
                expanded = self.graph_client.get_related_documents(
                    doc_ids=list(doc_ids),
                    rel_types=self.rel_types,
                    point_in_time=point_in_time,
                    max_depth=self.expand_depth,
                )
            else:
                expanded = expand_via_graph(
                    doc_ids=doc_ids,
                    graph_client=self.graph_client,
                    max_depth=self.expand_depth,
                    rel_types=self.rel_types,
                )

            # Collect all related doc_ids
            related_doc_ids = set()
            for source_id, related in expanded.items():
                related_doc_ids.update(related)
                # Update source results with related docs
                for result in result_map.values():
                    if result.metadata.get("doc_id") == source_id:
                        result.related_docs = related

            # Remove doc_ids we already have
            new_doc_ids = related_doc_ids - doc_ids

            # Fetch chunks for new related documents
            if new_doc_ids:
                graph_chunks = fetch_chunks_for_docs(
                    doc_ids=list(new_doc_ids)[: graph_top_k * len(doc_ids)],
                    retriever=self.vector_retriever,
                    top_k_per_doc=2,
                )

                # Add graph-sourced results
                for chunk in graph_chunks:
                    if chunk.id not in seen_chunks:
                        seen_chunks.add(chunk.id)
                        result_map[chunk.id] = HybridResult(
                            id=chunk.id,
                            text=chunk.text,
                            metadata=chunk.metadata,
                            score=chunk.score + 0.3,  # Graph penalty
                            source="graph",
                            related_docs=[],
                        )

        # Log usage
        log_usage(
            query=query_text,
            top_k=top_k,
            filters=filters,
            use_graph=expand_graph and self.graph_client is not None,
            path=self.vector_retriever.usage_log_path,
        )

        # Sort by fused score (lower is better) and return top_k
        hybrid_results = sorted(result_map.values(), key=lambda x: x.score)
        return hybrid_results[:top_k]

    def query_with_citations(
        self,
        query_text: str,
        top_k: int = DEFAULT_TOP_K,
        filters: Optional[Dict[str, Any]] = None,
        expand_graph: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Query and return results with formatted citations.

        Args:
            query_text: The search query string.
            top_k: Number of results to return.
            filters: Optional metadata filters.
            expand_graph: Whether to expand via graph.

        Returns:
            List of dicts with result details and citations.
        """
        results = self.query(
            query_text=query_text,
            top_k=top_k,
            filters=filters,
            expand_graph=expand_graph,
        )

        return [
            {
                "id": result.id,
                "text": result.text,
                "citation": format_citation(
                    RetrievalResult(
                        id=result.id,
                        text=result.text,
                        metadata=result.metadata,
                        score=result.score,
                    )
                ),
                "score": result.score,
                "source": result.source,
                "related_docs": result.related_docs,
            }
            for result in results
        ]
