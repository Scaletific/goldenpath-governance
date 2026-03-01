#!/usr/bin/env python3
"""
---
id: SCRIPT-0070
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_loader.py"
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
  - PRD-0008-governance-rag-pipeline
---
Purpose: RAG Document Loader for GoldenPath governance documents.

Loads markdown documents and extracts YAML frontmatter as metadata.
This module handles the first stage of the RAG pipeline: document ingestion.

Per GOV-0017: Parsers are determinism-critical and require test coverage.

Example:
    >>> from scripts.rag.loader import load_governance_document
    >>> doc = load_governance_document("docs/governance/policies/GOV-0017.md")
    >>> print(doc.metadata["id"])
    'GOV-0017-tdd-and-determinism'
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Union, List
import re

import yaml
import subprocess

try:
    from llama_index.core import Document as LlamaDocument

    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    LLAMA_INDEX_AVAILABLE = False
    LlamaDocument = None


@dataclass
class GovernanceDocument:
    """
    Represents a loaded governance document with separated metadata and content.

    Attributes:
        content: The markdown content without YAML frontmatter.
        metadata: Dictionary of metadata extracted from YAML frontmatter.
        source_path: Path to the original source file.
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_path: Union[str, Path] = ""


# Regex pattern for YAML frontmatter (between --- delimiters)
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL | re.MULTILINE)

# Cache for repo root to avoid repeated subprocess calls
_REPO_ROOT_CACHE: Path | None = None


def get_repo_root() -> Path:
    """
    Get the root directory of the git repository.

    Uses git rev-parse to find the repository root. Result is cached
    to avoid repeated subprocess calls.

    Returns:
        Path to the repository root directory.

    Raises:
        RuntimeError: If not in a git repository.
    """
    global _REPO_ROOT_CACHE

    if _REPO_ROOT_CACHE is not None:
        return _REPO_ROOT_CACHE

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        _REPO_ROOT_CACHE = Path(result.stdout.strip())
        return _REPO_ROOT_CACHE
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Not in a git repository") from e


def normalize_to_repo_relative(path: Path) -> str:
    """
    Normalize an absolute path to be relative to the repository root.

    This ensures portable citations that work regardless of where
    the repo is cloned.

    Args:
        path: Path to normalize (can be absolute or relative).

    Returns:
        String path relative to repo root.

    Example:
        >>> # If repo root is /home/user/goldenpath-infra
        >>> normalize_to_repo_relative(Path("/home/user/goldenpath-infra/docs/GOV-0017.md"))
        'docs/GOV-0017.md'
    """
    try:
        repo_root = get_repo_root()
        abs_path = path.resolve()
        return str(abs_path.relative_to(repo_root))
    except (RuntimeError, ValueError):
        # Not in a git repo or path not under repo - return as-is
        return str(path)


def extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown content potentially containing YAML frontmatter.

    Returns:
        Tuple of (metadata_dict, remaining_content).
        If no frontmatter is found, returns (empty_dict, original_content).

    Example:
        >>> content = "---\\nid: DOC-001\\n---\\n# Title"
        >>> metadata, body = extract_frontmatter(content)
        >>> metadata["id"]
        'DOC-001'
    """
    if not content:
        return {}, ""

    match = FRONTMATTER_PATTERN.match(content)

    if not match:
        return {}, content

    frontmatter_yaml = match.group(1)
    remaining_content = content[match.end() :]

    try:
        metadata = yaml.safe_load(frontmatter_yaml)
        if metadata is None:
            metadata = {}
    except yaml.YAMLError:
        # If YAML parsing fails, return empty metadata but preserve content
        metadata = {}

    return metadata, remaining_content


def load_governance_document(path: Union[str, Path]) -> GovernanceDocument:
    """
    Load a governance document from the filesystem.

    Reads the file, extracts YAML frontmatter as metadata, and returns
    a GovernanceDocument with separated content and metadata.

    Args:
        path: Path to the markdown file to load.

    Returns:
        GovernanceDocument with content, metadata, and source_path.

    Raises:
        FileNotFoundError: If the specified file does not exist.

    Example:
        >>> doc = load_governance_document("docs/GOV-0017.md")
        >>> doc.metadata["title"]
        'TDD and Determinism Policy'
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    raw_content = path.read_text(encoding="utf-8")

    metadata, content = extract_frontmatter(raw_content)

    # Always include file_path in metadata for traceability
    # Normalize to repo-relative path for portable citations
    relative_path = normalize_to_repo_relative(path)
    metadata["file_path"] = relative_path

    return GovernanceDocument(
        content=content,
        metadata=metadata,
        source_path=relative_path,
    )


def to_llama_document(doc: GovernanceDocument) -> "LlamaDocument":
    """
    Convert a GovernanceDocument to a LlamaIndex Document.

    Flattens list metadata (like relates_to) to strings for compatibility
    with vector stores that don't support list types.

    Args:
        doc: GovernanceDocument to convert.

    Returns:
        LlamaIndex Document with metadata preserved.

    Raises:
        ImportError: If llama-index is not installed.

    Example:
        >>> gov_doc = load_governance_document("docs/GOV-0017.md")
        >>> llama_doc = to_llama_document(gov_doc)
        >>> llama_doc.metadata["doc_id"]
        'GOV-0017-tdd-and-determinism'
    """
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError(
            "llama-index is not installed. Install with: pip install llama-index"
        )

    # Flatten metadata for vector store compatibility
    flat_metadata = {}
    for key, value in doc.metadata.items():
        if isinstance(value, list):
            flat_metadata[key] = str(value)
        elif value is None:
            flat_metadata[key] = ""
        else:
            flat_metadata[key] = value

    # Add standard fields expected by downstream components
    flat_metadata["doc_id"] = doc.metadata.get("id", "")
    flat_metadata["doc_title"] = doc.metadata.get("title", "")
    flat_metadata["doc_type"] = doc.metadata.get("type", "")

    return LlamaDocument(
        text=doc.content,
        metadata=flat_metadata,
        doc_id=doc.metadata.get("id", str(doc.source_path)),
    )


def load_as_llama_documents(
    directory: Union[str, Path], pattern: str = "*.md"
) -> List["LlamaDocument"]:
    """
    Load governance documents as LlamaIndex Documents.

    Convenience function that combines load_governance_documents
    and to_llama_document for direct LlamaIndex integration.

    Args:
        directory: Directory to search for documents.
        pattern: Glob pattern for matching files (default: "*.md").

    Returns:
        List of LlamaIndex Document objects.

    Example:
        >>> docs = load_as_llama_documents("docs/governance/policies/")
        >>> len(docs) > 0
        True
    """
    gov_docs = load_governance_documents(directory, pattern)
    return [to_llama_document(doc) for doc in gov_docs]


def load_governance_documents(
    directory: Union[str, Path], pattern: str = "*.md"
) -> list[GovernanceDocument]:
    """
    Load all governance documents from a directory.

    Args:
        directory: Directory to search for documents.
        pattern: Glob pattern for matching files (default: "*.md").

    Returns:
        List of GovernanceDocument objects.

    Example:
        >>> docs = load_governance_documents("docs/governance/policies/")
        >>> len(docs) > 0
        True
    """
    directory = Path(directory)
    documents = []

    for file_path in sorted(directory.glob(pattern)):
        if file_path.is_file():
            try:
                doc = load_governance_document(file_path)
                documents.append(doc)
            except Exception:
                # Skip files that can't be loaded
                continue

    return documents
