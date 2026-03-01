"""Shared fixtures for rag-web-ui backend tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# Ensure backend is importable
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture
def client():
    """FastAPI test client."""
    from app import app

    return TestClient(app)


@pytest.fixture
def mock_retriever():
    """Mock HybridRetriever that returns canned results."""
    mock = MagicMock()
    mock_result = MagicMock()
    mock_result.text = "TDD is mandatory per GOV-0017."
    mock_result.metadata = {
        "doc_id": "GOV-0017",
        "file_path": "docs/governance/policies/GOV-0017-tdd-and-determinism.md",
    }
    mock.query.return_value = [mock_result]
    return mock


@pytest.fixture
def mock_contract():
    """Mock AnswerContract matching the real dataclass shape."""
    from scripts.rag.llm_synthesis import AnswerContract, EvidenceItem

    return AnswerContract(
        answer="TDD is mandatory. All code changes require tests per ADR-0182.",
        evidence=[
            EvidenceItem(
                graph_ids=["GOV-0017"],
                file_paths=[
                    "docs/governance/policies/GOV-0017-tdd-and-determinism.md"
                ],
                excerpt="No feature without a test.",
                source_sha="abc123",
            )
        ],
        timestamp="2026-02-08T12:00:00Z",
        limitations="This answer covers governance policy only, not implementation details.",
        next_step="Read ADR-0182 for the full TDD philosophy.",
    )


@pytest.fixture
def mock_hybrid_results():
    """Real HybridResult objects returned by retriever.query()."""
    from scripts.rag.hybrid_retriever import HybridResult

    repo_root = str(BACKEND_DIR.parent.parent)
    return [
        HybridResult(
            id="chunk-001",
            text="TDD is mandatory per GOV-0017. All code changes require tests written before implementation.",
            metadata={
                "doc_id": "GOV-0017",
                "section": "Purpose",
                "file_path": f"{repo_root}/docs/governance/policies/GOV-0017-tdd-and-determinism.md",
                "chunk_index": 0,
            },
            score=0.92,
            source="vector",
            related_docs=["ADR-0182"],
            bm25_score=None,
            vector_score=0.92,
        ),
        HybridResult(
            id="chunk-002",
            text="The testing stack matrix defines three tiers: unit tests (Tier 1), golden tests (Tier 2), and integration tests (Tier 3).",
            metadata={
                "doc_id": "GOV-0016",
                "section": "Testing Tiers",
                "file_path": f"{repo_root}/docs/governance/policies/GOV-0016-testing-stack-matrix.md",
                "chunk_index": 1,
            },
            score=0.85,
            source="both",
            related_docs=[],
            bm25_score=0.78,
            vector_score=0.85,
        ),
    ]


@pytest.fixture
def mock_contract_absolute_paths():
    """AnswerContract with absolute file paths (simulates raw ChromaDB output)."""
    from app import REPO_ROOT
    from scripts.rag.llm_synthesis import AnswerContract, EvidenceItem

    return AnswerContract(
        answer="TDD is mandatory.",
        evidence=[
            EvidenceItem(
                graph_ids=["GOV-0017"],
                file_paths=[
                    str(
                        REPO_ROOT
                        / "docs/governance/policies/GOV-0017-tdd-and-determinism.md"
                    ),
                ],
                excerpt="No feature without a test.",
                source_sha="abc123",
            )
        ],
        timestamp="2026-02-08T12:00:00Z",
        limitations="Limited to governance policy.",
        next_step="Read ADR-0182.",
    )
