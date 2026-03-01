#!/usr/bin/env python3
"""
---
id: SCRIPT-0085
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-02-03
test:
  runner: pytest
  command: "pytest -q tests/unit/test_graphiti_client.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - ADR-0185-graphiti-agent-memory-framework
  - PRD-0008-governance-rag-pipeline
  - GOV-0020-rag-maturity-model
  - SCRIPT-0074-graph-client
  - SCRIPT-0084-rag-agent
---
Purpose: Graphiti client wrapper for agent memory persistence.

Implements ADR-0185: Uses Graphiti for temporal knowledge graph storage
on Neo4j. Provides agent memory across sessions:
- Episode capture for conversations
- Entity extraction and relationship detection
- Temporal awareness (when facts were learned/changed)
- Memory retrieval for context

Example:
    >>> from scripts.rag.graphiti_client import GraphitiMemory
    >>> memory = GraphitiMemory()
    >>> await memory.add_episode("Agent found GOV-0017 dependencies")
    >>> results = await memory.search("What do we know about GOV-0017?")
"""

import os
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict

# Graphiti imports
try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType

    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False
    Graphiti = None
    EpisodeType = None


@dataclass
class MemoryResult:
    """Result from memory search."""

    content: str
    score: float
    source: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Episode:
    """An episode captured in memory."""

    name: str
    content: str
    source: str = "agent-session"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)


class GraphitiMemory:
    """
    Graphiti-based agent memory for session persistence.

    Implements ADR-0185: Uses Graphiti temporal knowledge graph on Neo4j
    to preserve agent memory across sessions.

    Features:
    - Episode capture: Record conversations and findings
    - Entity extraction: Automatic entity/relationship detection
    - Temporal awareness: Track when facts were learned
    - Memory search: Retrieve relevant context

    Attributes:
        neo4j_uri: Neo4j connection URI.
        neo4j_user: Neo4j username.
        neo4j_password: Neo4j password.
        llm_model: Model for entity extraction.
    """

    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        llm_model: Optional[str] = None,
    ):
        """
        Initialize Graphiti memory client.

        Args:
            neo4j_uri: Neo4j connection URI (default: from env).
            neo4j_user: Neo4j username (default: from env).
            neo4j_password: Neo4j password (default: from env).
            llm_model: Model for entity extraction (default: from env).
        """
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD", "")
        self.llm_model = llm_model or os.getenv(
            "GRAPHITI_LLM_MODEL", "claude-sonnet-4-20250514"
        )

        self._graphiti: Optional[Graphiti] = None
        self._initialized = False

    @property
    def is_available(self) -> bool:
        """Check if Graphiti is available."""
        return GRAPHITI_AVAILABLE

    async def initialize(self) -> bool:
        """
        Initialize the Graphiti connection.

        Returns:
            True if initialization successful, False otherwise.
        """
        if not GRAPHITI_AVAILABLE:
            return False

        if self._initialized:
            return True

        try:
            self._graphiti = Graphiti(
                neo4j_uri=self.neo4j_uri,
                neo4j_user=self.neo4j_user,
                neo4j_password=self.neo4j_password,
            )
            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize Graphiti: {e}")
            return False

    async def add_episode(
        self,
        content: str,
        name: Optional[str] = None,
        source: str = "agent-session",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Add an episode to agent memory.

        Episodes are the primary way to capture agent interactions.
        Graphiti automatically extracts entities and relationships.

        Args:
            content: The episode content (conversation, finding, etc.).
            name: Episode name (auto-generated if not provided).
            source: Source identifier (default: "agent-session").
            metadata: Additional metadata.

        Returns:
            Episode ID if successful, None otherwise.
        """
        if not await self.initialize():
            return None

        try:
            timestamp = datetime.now(timezone.utc)
            episode_name = name or f"episode-{timestamp.strftime('%Y%m%d-%H%M%S')}"

            # Add episode to Graphiti
            episode = await self._graphiti.add_episode(
                name=episode_name,
                episode_body=content,
                source_description=source,
                reference_time=timestamp,
            )

            return episode.uuid if hasattr(episode, "uuid") else episode_name

        except Exception as e:
            print(f"Failed to add episode: {e}")
            return None

    async def search(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[MemoryResult]:
        """
        Search agent memory for relevant context.

        Uses Graphiti's hybrid search (entity + edge + semantic).

        Args:
            query: Search query.
            num_results: Number of results to return.

        Returns:
            List of MemoryResult objects.
        """
        if not await self.initialize():
            return []

        try:
            results = await self._graphiti.search(
                query=query,
                num_results=num_results,
            )

            memory_results = []
            for r in results:
                memory_results.append(
                    MemoryResult(
                        content=r.fact if hasattr(r, "fact") else str(r),
                        score=r.score if hasattr(r, "score") else 1.0,
                        source=r.source_description
                        if hasattr(r, "source_description")
                        else "graphiti",
                        timestamp=r.created_at.isoformat()
                        if hasattr(r, "created_at")
                        else "",
                        metadata={
                            "uuid": r.uuid if hasattr(r, "uuid") else None,
                            "valid_at": r.valid_at.isoformat()
                            if hasattr(r, "valid_at")
                            else None,
                        },
                    )
                )

            return memory_results

        except Exception as e:
            print(f"Memory search failed: {e}")
            return []

    async def get_entity_context(
        self,
        entity_name: str,
    ) -> List[MemoryResult]:
        """
        Get context about a specific entity.

        Args:
            entity_name: Name of the entity (e.g., "GOV-0017").

        Returns:
            List of related memory results.
        """
        return await self.search(f"What do we know about {entity_name}?")

    async def close(self):
        """Close the Graphiti connection."""
        if self._graphiti:
            try:
                await self._graphiti.close()
            except Exception:
                pass
            self._graphiti = None
            self._initialized = False


class SyncGraphitiMemory:
    """
    Synchronous wrapper for GraphitiMemory.

    Provides blocking API for use in non-async contexts.
    """

    def __init__(self, **kwargs):
        """Initialize with same args as GraphitiMemory."""
        self._async_memory = GraphitiMemory(**kwargs)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop."""
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    def _run(self, coro):
        """Run coroutine synchronously."""
        return self._get_loop().run_until_complete(coro)

    @property
    def is_available(self) -> bool:
        """Check if Graphiti is available."""
        return self._async_memory.is_available

    def initialize(self) -> bool:
        """Initialize the connection."""
        return self._run(self._async_memory.initialize())

    def add_episode(
        self,
        content: str,
        name: Optional[str] = None,
        source: str = "agent-session",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Add an episode to memory."""
        return self._run(
            self._async_memory.add_episode(content, name, source, metadata)
        )

    def search(self, query: str, num_results: int = 10) -> List[MemoryResult]:
        """Search agent memory."""
        return self._run(self._async_memory.search(query, num_results))

    def get_entity_context(self, entity_name: str) -> List[MemoryResult]:
        """Get context about an entity."""
        return self._run(self._async_memory.get_entity_context(entity_name))

    def close(self):
        """Close the connection."""
        self._run(self._async_memory.close())
        if self._loop and not self._loop.is_closed():
            self._loop.close()


def create_memory_client(
    async_mode: bool = False,
    **kwargs,
) -> Any:
    """
    Factory function to create a memory client.

    Args:
        async_mode: If True, return async client. Default False.
        **kwargs: Arguments passed to GraphitiMemory.

    Returns:
        GraphitiMemory (async) or SyncGraphitiMemory (sync).
    """
    if async_mode:
        return GraphitiMemory(**kwargs)
    return SyncGraphitiMemory(**kwargs)


if __name__ == "__main__":
    print("Graphiti Memory Client")
    print("=" * 50)
    print(f"Graphiti available: {GRAPHITI_AVAILABLE}")

    if GRAPHITI_AVAILABLE:
        memory = SyncGraphitiMemory()
        if memory.initialize():
            print("Connected to Graphiti!")

            # Add a test episode
            episode_id = memory.add_episode(
                content="Test episode: User asked about RAG implementation phases.",
                name="test-episode-001",
            )
            print(f"Added episode: {episode_id}")

            # Search memory
            results = memory.search("RAG implementation")
            print(f"Found {len(results)} memory results")
            for r in results:
                print(f"  - {r.content[:100]}...")

            memory.close()
        else:
            print("Failed to connect to Graphiti")
    else:
        print("Graphiti not installed. Run: pip install graphiti-core")
