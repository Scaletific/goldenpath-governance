#!/usr/bin/env python3
"""
---
id: SCRIPT-0071
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_chunker.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
relates_to:
  - GOV-0017-tdd-and-determinism
  - ADR-0184-rag-markdown-header-chunking
  - ADR-0186-llamaindex-retrieval-layer
  - PRD-0008-governance-rag-pipeline
---
Purpose: RAG Markdown Chunker for GoldenPath governance documents.

Uses LlamaIndex MarkdownNodeParser for robust markdown chunking.
Maintains backward-compatible interface while leveraging battle-tested library.

Per ADR-0186: Use LlamaIndex for chunking to avoid custom brittleness.
Per PRD-0008: Use MarkdownNodeParser for GOV-*, ADR-*, PRD-* documents.

Features:
- MarkdownNodeParser: Header-based chunking for structured documents
- SentenceWindowNodeParser: Context-preserving chunks with surrounding sentences
- Parser instance reuse for performance optimization

Example:
    >>> from scripts.rag.chunker import chunk_document
    >>> from scripts.rag.loader import load_governance_document
    >>> doc = load_governance_document("docs/GOV-0017.md")
    >>> chunks = chunk_document(doc)
    >>> len(chunks) > 0
    True
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from scripts.rag.loader import (
    GovernanceDocument,
    to_llama_document,
    LLAMA_INDEX_AVAILABLE,
)

if LLAMA_INDEX_AVAILABLE:
    from llama_index.core import Document as LlamaDocument
    from llama_index.core.node_parser import (
        MarkdownNodeParser,
        SentenceWindowNodeParser,
    )
    from llama_index.core.schema import TextNode


# ---------------------------------------------------------------------------
# Parser Singletons (Performance Optimization)
# ---------------------------------------------------------------------------

_MARKDOWN_PARSER: Optional["MarkdownNodeParser"] = None
_SENTENCE_WINDOW_PARSER: Optional["SentenceWindowNodeParser"] = None

# Default configuration for SentenceWindowNodeParser
DEFAULT_WINDOW_SIZE = 3  # Sentences before and after
DEFAULT_WINDOW_METADATA_KEY = "surrounding_context"


def _get_markdown_parser() -> "MarkdownNodeParser":
    """
    Get or create the singleton MarkdownNodeParser instance.

    Returns:
        Configured MarkdownNodeParser for reuse across calls.
    """
    global _MARKDOWN_PARSER
    if _MARKDOWN_PARSER is None:
        _MARKDOWN_PARSER = MarkdownNodeParser.from_defaults(
            include_metadata=True,
            include_prev_next_rel=True,
        )
    return _MARKDOWN_PARSER


def _get_sentence_window_parser(
    window_size: int = DEFAULT_WINDOW_SIZE,
) -> "SentenceWindowNodeParser":
    """
    Get or create the singleton SentenceWindowNodeParser instance.

    Note: If window_size differs from cached parser, creates new instance.

    Args:
        window_size: Number of sentences to include before/after each chunk.

    Returns:
        Configured SentenceWindowNodeParser for reuse.
    """
    global _SENTENCE_WINDOW_PARSER
    if (
        _SENTENCE_WINDOW_PARSER is None
        or _SENTENCE_WINDOW_PARSER.window_size != window_size
    ):
        _SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(
            window_size=window_size,
            window_metadata_key=DEFAULT_WINDOW_METADATA_KEY,
            include_metadata=True,
            include_prev_next_rel=True,
        )
    return _SENTENCE_WINDOW_PARSER


@dataclass
class Chunk:
    """
    Represents a chunk of document content with metadata.

    Attributes:
        text: The chunk content including section header.
        metadata: Dictionary of metadata (inherited from doc + section-specific).
    """

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def _node_to_chunk(node: "TextNode", chunk_index: int) -> Chunk:
    """
    Convert a LlamaIndex TextNode to our Chunk dataclass.

    Handles metadata from both MarkdownNodeParser (header_path) and
    SentenceWindowNodeParser (surrounding_context).

    Args:
        node: LlamaIndex TextNode from any node parser.
        chunk_index: Sequential index for this chunk.

    Returns:
        Chunk with text and metadata.
    """
    metadata = dict(node.metadata)
    metadata["chunk_index"] = chunk_index

    # Extract section name from the text content's first line
    # LlamaIndex's header_path shows parent hierarchy, not current section
    text = node.text.strip()
    first_line = text.split("\n")[0] if text else ""

    # Determine header level and section name from text content
    if first_line.startswith("### "):
        metadata["header_level"] = 3
        metadata["section"] = first_line[4:].strip()
    elif first_line.startswith("## "):
        metadata["header_level"] = 2
        metadata["section"] = first_line[3:].strip()
    elif first_line.startswith("# "):
        metadata["header_level"] = 1
        metadata["section"] = first_line[2:].strip()
    else:
        # No header in text, fall back to header_path or mark as sentence chunk
        metadata["header_level"] = 0
        header_path = metadata.get("header_path", "/")
        if header_path and header_path != "/":
            parts = [p for p in header_path.split("/") if p]
            metadata["section"] = parts[-1] if parts else "Content"
        else:
            # Likely a SentenceWindowNodeParser chunk
            metadata["section"] = "Content"

    # Mark if this chunk has surrounding context (from SentenceWindowNodeParser)
    if DEFAULT_WINDOW_METADATA_KEY in metadata:
        metadata["has_context_window"] = True

    return Chunk(text=node.text, metadata=metadata)


def chunk_with_llamaindex(doc: "LlamaDocument") -> List[Chunk]:
    """
    Chunk a LlamaIndex Document using MarkdownNodeParser.

    This is the recommended chunking method per ADR-0186 and PRD-0008.
    Uses singleton parser instance for performance.

    Args:
        doc: LlamaIndex Document to chunk.

    Returns:
        List of Chunk objects with inherited metadata.

    Example:
        >>> from scripts.rag.loader import load_governance_document, to_llama_document
        >>> gov_doc = load_governance_document("docs/GOV-0017.md")
        >>> llama_doc = to_llama_document(gov_doc)
        >>> chunks = chunk_with_llamaindex(llama_doc)
        >>> len(chunks) > 0
        True
    """
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError(
            "llama-index is not installed. Install with: pip install llama-index"
        )

    parser = _get_markdown_parser()
    nodes = parser.get_nodes_from_documents([doc])

    return [_node_to_chunk(node, idx) for idx, node in enumerate(nodes)]


def chunk_with_sentence_window(
    doc: "LlamaDocument",
    window_size: int = DEFAULT_WINDOW_SIZE,
) -> List[Chunk]:
    """
    Chunk a LlamaIndex Document using SentenceWindowNodeParser.

    Creates sentence-level chunks with surrounding context preserved in metadata.
    This enables better retrieval by providing context during synthesis.

    The 'surrounding_context' metadata field contains sentences before and after
    each chunk, allowing the retriever to use expanded context for answers.

    Args:
        doc: LlamaIndex Document to chunk.
        window_size: Number of sentences to include before/after (default: 3).

    Returns:
        List of Chunk objects with context window metadata.

    Example:
        >>> from scripts.rag.loader import load_governance_document, to_llama_document
        >>> gov_doc = load_governance_document("docs/GOV-0017.md")
        >>> llama_doc = to_llama_document(gov_doc)
        >>> chunks = chunk_with_sentence_window(llama_doc, window_size=3)
        >>> chunks[0].metadata.get("has_context_window")
        True
    """
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError(
            "llama-index is not installed. Install with: pip install llama-index"
        )

    parser = _get_sentence_window_parser(window_size)
    nodes = parser.get_nodes_from_documents([doc])

    return [_node_to_chunk(node, idx) for idx, node in enumerate(nodes)]


def chunk_markdown(content: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
    """
    Split markdown content into chunks using LlamaIndex MarkdownNodeParser.

    Backward-compatible interface that uses LlamaIndex under the hood.
    Uses singleton parser instance for performance.

    Args:
        content: Markdown content to chunk.
        base_metadata: Metadata to inherit for all chunks.

    Returns:
        List of Chunk objects.

    Example:
        >>> chunks = chunk_markdown("## A\\nContent A\\n\\n## B\\nContent B", {})
        >>> len(chunks) >= 2
        True
    """
    if not content or not content.strip():
        return []

    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError(
            "llama-index is not installed. Install with: pip install llama-index"
        )

    # Create a LlamaIndex Document with the base metadata
    doc = LlamaDocument(text=content, metadata=base_metadata)

    # Use singleton MarkdownNodeParser
    parser = _get_markdown_parser()
    nodes = parser.get_nodes_from_documents([doc])

    return [_node_to_chunk(node, idx) for idx, node in enumerate(nodes)]


def chunk_document(doc: GovernanceDocument) -> List[Chunk]:
    """
    Chunk a GovernanceDocument into sections using LlamaIndex.

    Converts to LlamaIndex Document, chunks with MarkdownNodeParser,
    and returns Chunk objects with inherited metadata.

    Args:
        doc: GovernanceDocument to chunk.

    Returns:
        List of Chunk objects with inherited document metadata.

    Example:
        >>> from scripts.rag.loader import load_governance_document
        >>> doc = load_governance_document("docs/GOV-0017.md")
        >>> chunks = chunk_document(doc)
        >>> chunks[0].metadata.get("doc_id") is not None
        True
    """
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError(
            "llama-index is not installed. Install with: pip install llama-index"
        )

    # Convert to LlamaIndex Document (handles frontmatter flattening)
    llama_doc = to_llama_document(doc)

    # Chunk with MarkdownNodeParser
    return chunk_with_llamaindex(llama_doc)


def get_nodes_from_documents(docs: List["LlamaDocument"]) -> List["TextNode"]:
    """
    Get LlamaIndex TextNodes directly from Documents.

    Use this when you want to work with LlamaIndex nodes directly
    instead of our Chunk dataclass. Uses singleton parser for performance.

    Args:
        docs: List of LlamaIndex Documents.

    Returns:
        List of LlamaIndex TextNode objects.

    Example:
        >>> from scripts.rag.loader import load_as_llama_documents
        >>> docs = load_as_llama_documents("docs/governance/policies/")
        >>> nodes = get_nodes_from_documents(docs)
        >>> len(nodes) > 0
        True
    """
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError(
            "llama-index is not installed. Install with: pip install llama-index"
        )

    parser = _get_markdown_parser()
    return parser.get_nodes_from_documents(docs)


def chunk_document_with_context(
    doc: GovernanceDocument,
    window_size: int = DEFAULT_WINDOW_SIZE,
) -> List[Chunk]:
    """
    Chunk a GovernanceDocument with surrounding sentence context.

    Use this when you need enhanced retrieval with context windows.
    Each chunk will have 'surrounding_context' metadata containing
    neighboring sentences for better answer synthesis.

    Args:
        doc: GovernanceDocument to chunk.
        window_size: Number of sentences to include before/after (default: 3).

    Returns:
        List of Chunk objects with context window metadata.

    Example:
        >>> from scripts.rag.loader import load_governance_document
        >>> doc = load_governance_document("docs/GOV-0017.md")
        >>> chunks = chunk_document_with_context(doc, window_size=3)
        >>> any(c.metadata.get("has_context_window") for c in chunks)
        True
    """
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError(
            "llama-index is not installed. Install with: pip install llama-index"
        )

    # Convert to LlamaIndex Document
    llama_doc = to_llama_document(doc)

    # Chunk with SentenceWindowNodeParser
    return chunk_with_sentence_window(llama_doc, window_size)
