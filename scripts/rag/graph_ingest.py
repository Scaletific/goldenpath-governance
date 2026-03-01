#!/usr/bin/env python3
"""
---
id: SCRIPT-0075
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_graph_ingest.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - ADR-0185-graphiti-agent-memory-framework
  - GOV-0017-tdd-and-determinism
---
Purpose: Graph ingestion for governance documents (Neo4j).

Takes GovernanceDocument objects and upserts document nodes plus
RELATES_TO edges into Neo4j via graph_client.
"""

import subprocess
from typing import Iterable, Dict, Any, List, Optional

from scripts.rag.loader import GovernanceDocument


# Relationship mappings: frontmatter field -> Neo4j relationship type
RELATIONSHIP_FIELDS = {
    "relates_to": "RELATES_TO",
    "supersedes": "SUPERSEDES",
    "superseded_by": "SUPERSEDED_BY",
    "depends_on": "DEPENDS_ON",
    "dependencies": "DEPENDS_ON",  # 58 docs use this field name
    "related_adrs": "RELATES_TO",  # 5 GOV files
    "related_govs": "RELATES_TO",  # 5 GOV files
    "extends": "EXTENDS",  # 1 ADR (distinct semantics)
}


def _get_git_sha() -> Optional[str]:
    """Get current git commit SHA for source tracking (ADR-0185)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]  # Short SHA
    except Exception:
        pass
    return None


def _document_props(doc: GovernanceDocument) -> Dict[str, Any]:
    """Build graph properties from a governance document."""
    metadata = doc.metadata or {}
    return {
        "id": metadata.get("id"),
        "title": metadata.get("title"),
        "type": metadata.get("type"),
        "domain": metadata.get("domain"),
        "lifecycle": metadata.get("lifecycle"),
        "status": metadata.get("status"),
        "file_path": metadata.get("file_path") or str(doc.source_path),
    }


def _normalize_list(value: Any) -> List[str]:
    """Normalize a metadata value to a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return [str(value)]


def ingest_documents(
    documents: Iterable[GovernanceDocument],
    graph_client,
    source_sha: Optional[str] = None,
) -> Dict[str, int]:
    """
    Ingest governance documents into the graph with temporal tracking.

    Per ADR-0185 (Graphiti temporal layer):
    - All nodes include created_at, updated_at, source_sha
    - All edges include valid_from, updated_at, source_sha

    Args:
        documents: Iterable of GovernanceDocument objects.
        graph_client: Graph client with upsert_document and relate_documents methods.
        source_sha: Git commit SHA for source tracking.

    Returns:
        Dict with counts: documents, and each relationship type.
    """
    counts = {"documents": 0}
    for rel_type in RELATIONSHIP_FIELDS.values():
        counts[rel_type] = 0

    # Get source SHA if not provided
    sha = source_sha or _get_git_sha()

    for doc in documents:
        props = _document_props(doc)
        doc_id = props.get("id")
        if not doc_id:
            continue

        # Upsert document with temporal tracking
        graph_client.upsert_document(doc_id, props, source_sha=sha)

        # Extract all relationship types from frontmatter
        for field_name, rel_type in RELATIONSHIP_FIELDS.items():
            targets = _normalize_list(doc.metadata.get(field_name))
            for target_id in targets:
                graph_client.relate_documents(
                    doc_id, target_id, rel_type, source_sha=sha
                )
                counts[rel_type] += 1

        counts["documents"] += 1

    return counts


def run_ingestion(source_dirs: List[str] = None) -> Dict[str, Any]:
    """
    Run graph ingestion from governance documents.

    Args:
        source_dirs: List of directories to scan. Defaults to PRD-0008 scope.

    Returns:
        Ingestion statistics.
    """
    from pathlib import Path
    from scripts.rag.loader import load_governance_documents
    from scripts.rag.graph_client import create_client_from_env

    # Default scope aligned with scope.py ALLOWLIST_PREFIXES
    if source_dirs is None:
        source_dirs = [
            "docs/",
            "session_capture/",
            "bootstrap/",
            "catalog/",
            "gitops/",
            "idp-tooling/",
            "tests/",
        ]

    all_docs = []
    for source_dir in source_dirs:
        source_path = Path(source_dir)
        if source_path.exists():
            print(f"Loading documents from {source_dir}...")
            docs = load_governance_documents(source_path, pattern="**/*.md")
            print(f"  Found {len(docs)} documents")
            all_docs.extend(docs)

    docs = all_docs
    errors = []
    print(f"Total: {len(docs)} documents ({len(errors)} errors)")

    print("Connecting to Neo4j...")
    client = create_client_from_env()
    health = client.health_check()
    print(
        f"Neo4j status: {health['status']} ({health.get('server_version', 'unknown')})"
    )

    if health["status"] != "healthy":
        client.close()
        return {"status": "failed", "error": "Neo4j not healthy"}

    # Get source SHA for temporal tracking
    source_sha = _get_git_sha()
    print(f"Source SHA: {source_sha or 'unknown'}")

    print("Ingesting documents into graph...")
    counts = ingest_documents(docs, client, source_sha=source_sha)
    print(f"Ingested {counts['documents']} documents")

    # Show relationship counts
    total_rels = 0
    for rel_type in RELATIONSHIP_FIELDS.values():
        rel_count = counts.get(rel_type, 0)
        if rel_count > 0:
            print(f"  {rel_type}: {rel_count}")
        total_rels += rel_count

    # Verify counts from database
    with client._driver.session() as session:
        result = session.run(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count"
        )
        db_counts = {record["type"]: record["count"] for record in result}

    client.close()

    return {
        "status": "success",
        "documents_ingested": counts["documents"],
        "relationships": counts,
        "db_relationship_counts": db_counts,
        "total_relationships": total_rels,
        "source_sha": source_sha,
        "errors": len(errors),
    }


if __name__ == "__main__":
    import sys
    import json

    # Accept multiple directories as args, or use defaults
    source_dirs = sys.argv[1:] if len(sys.argv) > 1 else None
    result = run_ingestion(source_dirs)
    print(json.dumps(result, indent=2))
