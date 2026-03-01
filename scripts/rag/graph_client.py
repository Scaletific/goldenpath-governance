#!/usr/bin/env python3
"""
---
id: SCRIPT-0074
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
Purpose: Neo4j graph client for governance document relationships.
SKIP-TDD: Requires Neo4j; tested via test_graph_ingest.py integration.

Provides a minimal client for upserting document nodes and relates_to edges.
Graphiti is expected to share the same Neo4j backend in Phase 1+, but Phase 0
ingestion uses direct Neo4j operations.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None  # Allow import without neo4j for testing


def _utc_now_iso() -> str:
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GraphClientConfig:
    """Connection configuration for Neo4j."""

    uri: str
    user: str
    password: str
    database: Optional[str] = None


class Neo4jGraphClient:
    """
    Minimal Neo4j client for document node and edge operations.

    This client is intentionally small to keep Phase 0 deterministic
    and testable. Graphiti integration will layer on top of the same
    Neo4j backend in Phase 1.
    """

    def __init__(self, config: GraphClientConfig):
        if GraphDatabase is None:
            raise ImportError("neo4j is not installed. Install with: pip install neo4j")
        self._config = config
        self._driver = GraphDatabase.driver(
            config.uri, auth=(config.user, config.password)
        )

    def close(self) -> None:
        """Close the underlying Neo4j driver."""
        if self._driver:
            self._driver.close()

    def upsert_document(
        self,
        doc_id: str,
        props: Dict[str, Any],
        source_sha: Optional[str] = None,
    ) -> None:
        """
        Upsert a document node by id with temporal tracking.

        Per ADR-0185, nodes include:
        - created_at: When node was first created
        - updated_at: Last modification timestamp
        - source_sha: Git commit SHA of source document

        Args:
            doc_id: Document id to upsert.
            props: Properties to set on the node.
            source_sha: Git commit SHA of source document.
        """
        if not doc_id:
            return

        now = _utc_now_iso()
        props_with_temporal = {**props, "updated_at": now}
        if source_sha:
            props_with_temporal["source_sha"] = source_sha

        query = (
            "MERGE (d:Document {id: $id}) "
            "ON CREATE SET d.created_at = $now "
            "SET d += $props "
            "RETURN d.id"
        )
        params = {"id": doc_id, "props": props_with_temporal, "now": now}
        self._run(query, params)

    def relate_documents(
        self,
        src_id: str,
        dst_id: str,
        rel_type: str,
        valid_from: Optional[str] = None,
        valid_to: Optional[str] = None,
        source_sha: Optional[str] = None,
    ) -> None:
        """
        Create a relationship between two documents with temporal properties.

        Per ADR-0185 (Graphiti temporal layer), edges include:
        - valid_from: When this relationship became valid (default: now)
        - valid_to: When this relationship ends (null = currently valid)
        - updated_at: Last modification timestamp
        - source_sha: Git SHA of source document

        Args:
            src_id: Source document id.
            dst_id: Target document id.
            rel_type: Relationship type (e.g., RELATES_TO).
            valid_from: ISO timestamp when relationship started.
            valid_to: ISO timestamp when relationship ended (null = still valid).
            source_sha: Git commit SHA of source document.
        """
        if not src_id or not dst_id:
            return

        now = _utc_now_iso()
        props = {
            "valid_from": valid_from or now,
            "updated_at": now,
        }
        if valid_to:
            props["valid_to"] = valid_to
        if source_sha:
            props["source_sha"] = source_sha

        # Use MERGE with ON CREATE/ON MATCH for temporal tracking
        query = (
            "MERGE (a:Document {id: $src}) "
            "MERGE (b:Document {id: $dst}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "ON CREATE SET r += $props "
            "ON MATCH SET r.updated_at = $now"
        )
        params = {"src": src_id, "dst": dst_id, "props": props, "now": now}
        self._run(query, params)

    def invalidate_relationship(self, src_id: str, dst_id: str, rel_type: str) -> None:
        """
        Mark a relationship as no longer valid (set valid_to = now).

        This supports temporal queries - the edge remains for history
        but is excluded from current-state queries.

        Args:
            src_id: Source document id.
            dst_id: Target document id.
            rel_type: Relationship type.
        """
        if not src_id or not dst_id:
            return

        now = _utc_now_iso()
        query = (
            f"MATCH (a:Document {{id: $src}})-[r:{rel_type}]->(b:Document {{id: $dst}}) "
            "WHERE r.valid_to IS NULL "
            "SET r.valid_to = $now, r.updated_at = $now"
        )
        params = {"src": src_id, "dst": dst_id, "now": now}
        self._run(query, params)

    def get_related_documents(
        self,
        doc_ids: List[str],
        rel_types: Optional[List[str]] = None,
        point_in_time: Optional[str] = None,
        include_expired: bool = False,
        max_depth: int = 1,
    ) -> Dict[str, List[str]]:
        """
        Get related documents with temporal filtering.

        Args:
            doc_ids: List of document IDs to expand from.
            rel_types: Relationship types to follow. Default: all.
            point_in_time: ISO timestamp for point-in-time queries.
            include_expired: Include relationships that have valid_to set.
            max_depth: Maximum relationship hops to traverse (default: 1).

        Returns:
            Dict mapping source doc_id to list of related doc_ids.
        """
        if not doc_ids:
            return {}

        # Build relationship filter
        rel_filter = ""
        if rel_types:
            rel_filter = ":" + "|".join(rel_types)

        depth = max(1, int(max_depth))
        rel_pattern = f"-[r{rel_filter}*1..{depth}]-"

        # Build temporal filter across all hops
        temporal_filter = ""
        if not include_expired:
            if point_in_time:
                temporal_filter = (
                    "AND all(rel IN r WHERE rel.valid_from <= $pit "
                    "AND (rel.valid_to IS NULL OR rel.valid_to > $pit))"
                )
            else:
                temporal_filter = "AND all(rel IN r WHERE rel.valid_to IS NULL)"

        query = f"""
        MATCH (src:Document){rel_pattern}(related:Document)
        WHERE src.id IN $doc_ids {temporal_filter}
        RETURN src.id AS source, collect(DISTINCT related.id) AS related
        """

        params = {"doc_ids": doc_ids}
        if point_in_time:
            params["pit"] = point_in_time

        expanded = {}
        try:
            with self._driver.session() as session:
                result = session.run(query, params)
                for record in result:
                    expanded[record["source"]] = record["related"]
        except Exception:
            pass

        return expanded

    def _run(self, query: str, params: Dict[str, Any]) -> None:
        """Execute a Cypher query with optional database selection."""
        if self._config.database:
            with self._driver.session(database=self._config.database) as session:
                session.run(query, params)
        else:
            with self._driver.session() as session:
                session.run(query, params)

    def health_check(self) -> Dict[str, Any]:
        """Check connection to Neo4j and return server info."""
        try:
            with self._driver.session() as session:
                result = session.run("RETURN 1 AS ok")
                result.single()
            info = self._driver.get_server_info()
            return {
                "status": "healthy",
                "server_version": info.agent if info else "unknown",
                "address": str(info.address) if info else self._config.uri,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


def create_client_from_env() -> Neo4jGraphClient:
    """
    Create a Neo4jGraphClient from environment variables.

    Environment variables:
        NEO4J_URI: Bolt URI (default: bolt://localhost:7687)
        NEO4J_USER: Username (default: neo4j)
        NEO4J_PASSWORD: Password (required)
        NEO4J_DATABASE: Database name (optional)
    """
    import os

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE")

    if not password:
        raise ValueError("NEO4J_PASSWORD environment variable is required")

    config = GraphClientConfig(uri=uri, user=user, password=password, database=database)
    return Neo4jGraphClient(config)


# Alias for convenience
Neo4jClient = Neo4jGraphClient


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "health":
        client = create_client_from_env()
        print(client.health_check())
        client.close()
    else:
        print("Usage: python -m scripts.rag.graph_client health")
