#!/usr/bin/env python3
"""
---
id: SCRIPT-0078
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_index_build.py"
  evidence: declared
dry_run:
  supported: true
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0017-tdd-and-determinism
---
Purpose: End-to-end index build (ingest → chunk → index → graph).
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from scripts.rag.loader import load_governance_document, GovernanceDocument
from scripts.rag.chunker import chunk_document
from scripts.rag.indexer import GovernanceIndex
from scripts.rag.scope import filter_paths
from scripts.rag.graph_ingest import ingest_documents
from scripts.rag.graph_client import GraphClientConfig, Neo4jGraphClient
from scripts.rag.index_metadata import (
    build_index_metadata,
    read_index_metadata,
    write_index_metadata,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def collect_markdown_paths(root: Optional[Path] = None) -> List[Path]:
    """
    Collect markdown files under repo root and filter by scope.
    """
    root = root or _repo_root()
    candidates = list(root.rglob("*.md"))
    allowed = filter_paths(candidates)
    return sorted(allowed)


def load_documents(
    paths: List[Path],
) -> Tuple[List[GovernanceDocument], List[Dict[str, Any]]]:
    docs: List[GovernanceDocument] = []
    errors: List[Dict[str, Any]] = []
    for path in paths:
        try:
            docs.append(load_governance_document(path))
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})
            continue
    return docs, errors


def write_index_errors(path: Path, errors: List[Dict[str, Any]]) -> None:
    """
    Write ingestion errors to a JSON artifact for visibility.
    """
    if not errors:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"error_count": len(errors), "errors": errors}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def resolve_document_count(root: Path, metadata_path: Path) -> int:
    """
    Resolve document count consistently across full/incremental/validate paths.

    Prefer existing metadata (previous full build) to avoid chunk-count drift.
    Fall back to scoped markdown path count if metadata is missing.
    """
    existing = read_index_metadata(metadata_path)
    if existing is not None:
        return existing.document_count
    return len(collect_markdown_paths(root))


def _graph_client_from_env() -> Optional[Neo4jGraphClient]:
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")
    if not uri or not user or not password:
        return None
    config = GraphClientConfig(uri=uri, user=user, password=password, database=database)
    return Neo4jGraphClient(config)


def build_index(
    root: Optional[Path] = None, metadata_path: Optional[Path] = None
) -> int:
    """
    Build vector index and ingest graph edges from governance docs.

    Returns:
        Number of documents indexed.
    """
    root = root or _repo_root()
    paths = collect_markdown_paths(root)
    docs, errors = load_documents(paths)

    index = GovernanceIndex()
    chunk_count = 0
    for doc in docs:
        chunks = chunk_document(doc)
        chunk_count += index.add(chunks)

    graph_client = _graph_client_from_env()
    if graph_client is not None:
        ingest_documents(docs, graph_client)
        graph_client.close()

    if errors:
        error_path = root / "reports" / "index_errors.json"
        write_index_errors(error_path, errors)

    meta_path = metadata_path or (root / "reports" / "index_metadata.json")
    write_index_metadata(meta_path, build_index_metadata(document_count=len(docs)))

    return chunk_count


def incremental_update(
    file_paths: List[str],
    persist_dir: Optional[str] = None,
    metadata_path: Optional[Path] = None,
) -> int:
    """
    Incrementally update index with specific files.

    Args:
        file_paths: Comma-separated list of file paths to update.
        persist_dir: ChromaDB persist directory.
        metadata_path: Path to write index metadata.

    Returns:
        Number of chunks updated.
    """
    root = _repo_root()
    paths = [root / p.strip() for p in file_paths.split(",") if p.strip()]
    paths = [p for p in paths if p.exists()]

    if not paths:
        print("No valid files to update")
        return 0

    docs, errors = load_documents(paths)

    # Reuse existing index (don't clear)
    index = GovernanceIndex(persist_dir=persist_dir)
    chunk_count = 0
    for doc in docs:
        chunks = chunk_document(doc)
        chunk_count += index.add(chunks)

    meta_path = metadata_path or (root / "reports" / "index_metadata.json")
    total_docs = resolve_document_count(root, meta_path)
    write_index_metadata(
        meta_path,
        build_index_metadata(document_count=total_docs),
    )

    return chunk_count


def validate_existing_index(
    persist_dir: Optional[str] = None,
    metadata_path: Optional[Path] = None,
) -> int:
    """
    Validate existing index without modifications.

    Args:
        persist_dir: ChromaDB persist directory.
        metadata_path: Path to write index metadata.

    Returns:
        Document count in existing index.
    """
    root = _repo_root()
    meta_path = metadata_path or (root / "reports" / "index_metadata.json")
    doc_count = resolve_document_count(root, meta_path)
    write_index_metadata(
        meta_path,
        build_index_metadata(document_count=doc_count),
    )

    return doc_count


if __name__ == "__main__":
    import argparse
    from collections import Counter

    parser = argparse.ArgumentParser(description="Build governance RAG index")
    parser.add_argument(
        "--persist-dir", default=".chroma", help="ChromaDB persist directory"
    )
    parser.add_argument(
        "--output", default="reports/index_metadata.json", help="Metadata output path"
    )
    parser.add_argument(
        "--incremental", action="store_true", help="Incremental update mode"
    )
    parser.add_argument(
        "--files", default="", help="Comma-separated files to update (for incremental)"
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate existing index"
    )
    args = parser.parse_args()

    root = _repo_root()
    meta_path = root / args.output

    if args.validate_only:
        print("Validating existing index...")
        doc_count = validate_existing_index(
            persist_dir=args.persist_dir,
            metadata_path=meta_path,
        )
        print(f"Index validated: {doc_count} documents")
        print(
            json.dumps({"status": "validated", "document_count": doc_count}, indent=2)
        )

    elif args.incremental and args.files:
        print(f"Incremental update: {args.files}")
        chunk_count = incremental_update(
            file_paths=args.files,
            persist_dir=args.persist_dir,
            metadata_path=meta_path,
        )
        print(f"Updated {chunk_count} chunks")
        print(
            json.dumps(
                {"status": "incremental", "chunks_updated": chunk_count}, indent=2
            )
        )

    else:
        print("Building governance RAG index (full rebuild)...")
        print("Collecting markdown files...")

        paths = collect_markdown_paths(root)

        # Show directory breakdown
        dirs = Counter()
        for p in paths:
            try:
                rel = p.relative_to(root)
                top = rel.parts[0] if rel.parts else "root"
                dirs[top] += 1
            except ValueError:
                dirs["unknown"] += 1

        print(f"\nScope breakdown ({len(paths)} files):")
        print("-" * 30)
        for d, c in sorted(dirs.items(), key=lambda x: -x[1]):
            print(f"  {d}: {c}")
        print("-" * 30)

        print("\nLoading and chunking documents...")
        docs, errors = load_documents(paths)

        index = GovernanceIndex(persist_dir=args.persist_dir)
        chunk_count = 0
        for doc in docs:
            chunks = chunk_document(doc)
            chunk_count += index.add(chunks)

        print(f"Indexed {len(docs)} documents → {chunk_count} chunks")

        graph_client = _graph_client_from_env()
        graph_count = 0
        if graph_client is not None:
            print("Ingesting into Neo4j graph...")
            graph_count = ingest_documents(docs, graph_client)
            graph_client.close()
            print(f"Graph: {graph_count} documents ingested")
        else:
            print("Graph: skipped (NEO4J_* env vars not set)")

        if errors:
            error_path = root / "reports" / "index_errors.json"
            write_index_errors(error_path, errors)
            print(f"Errors: {len(errors)} (see reports/index_errors.json)")

        write_index_metadata(meta_path, build_index_metadata(document_count=len(docs)))

        print(
            "\n"
            + json.dumps(
                {
                    "status": "success",
                    "documents": len(docs),
                    "chunks": chunk_count,
                    "graph_documents": graph_count,
                    "errors": len(errors),
                },
                indent=2,
            )
        )
