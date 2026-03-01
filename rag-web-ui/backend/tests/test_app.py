"""
Tests for rag-web-ui backend API contract compliance.

These tests verify:
- /health returns expected shape (including phoenix status)
- /providers returns list of ProviderInfo
- /ask returns AnswerContract-compliant JSON
- Response types match schema (limitations=string, no top-level source_sha)
- synthesize_contract is called with correct kwargs
- File paths are returned as relative (repo root stripped)
- elapsed_ms is present in response
- sources field contains raw retrieval results
"""

from unittest.mock import patch


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_ok(self, client):
        """Health endpoint returns status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "rag-web-ui"

    def test_health_includes_phoenix_status(self, client):
        """Health endpoint includes phoenix boolean field."""
        response = client.get("/health")
        data = response.json()
        assert "phoenix" in data, "health response should include phoenix field"
        assert isinstance(data["phoenix"], bool)

    def test_health_includes_neo4j_status(self, client):
        """Health endpoint includes neo4j boolean field."""
        response = client.get("/health")
        data = response.json()
        assert "neo4j" in data, "health response should include neo4j field"
        assert isinstance(data["neo4j"], bool)

    def test_health_response_is_json(self, client):
        """Health endpoint returns JSON content type."""
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]


class TestProvidersEndpoint:
    """Tests for GET /providers."""

    def test_providers_returns_list(self, client):
        """Providers endpoint returns a list."""
        response = client.get("/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_provider_shape(self, client):
        """Each provider has id, name, available fields."""
        response = client.get("/providers")
        data = response.json()
        for provider in data:
            assert "id" in provider
            assert "name" in provider
            assert "available" in provider
            assert isinstance(provider["id"], str)
            assert isinstance(provider["name"], str)
            assert isinstance(provider["available"], bool)

    def test_known_providers_present(self, client):
        """Expected provider IDs are present."""
        response = client.get("/providers")
        data = response.json()
        ids = [p["id"] for p in data]
        assert "ollama" in ids
        assert "claude" in ids
        assert "openai" in ids
        assert "gemini" in ids


class TestAskEndpoint:
    """Tests for POST /ask — contract compliance.

    The /ask endpoint uses lazy imports (inside the function body),
    so we patch at the source module path, not at app.*.
    """

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_ask_returns_answer_contract_shape(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Response matches AnswerContract schema fields."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200
        data = response.json()

        # Required fields per schema
        assert "answer" in data
        assert "evidence" in data
        assert "timestamp" in data
        assert "limitations" in data
        assert "next_step" in data

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_limitations_is_string_not_array(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """
        Finding 2: limitations must be a string per schema, not string[].

        Schema says: "limitations": {"type": "string"}
        AnswerContract dataclass says: limitations: str
        """
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(
            data["limitations"], str
        ), f"limitations should be str per schema, got {type(data['limitations'])}"

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_no_top_level_source_sha(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """
        Finding 3: source_sha should NOT be on the top-level response.

        Schema has additionalProperties: false with no source_sha field.
        source_sha belongs on EvidenceItem only.
        """
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200
        data = response.json()
        assert (
            "source_sha" not in data
        ), "source_sha should not be on top-level response (not in schema)"

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_evidence_items_have_correct_shape(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Evidence items match evidenceItem schema definition."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200
        data = response.json()

        assert len(data["evidence"]) > 0
        ev = data["evidence"][0]
        assert "graph_ids" in ev
        assert "file_paths" in ev
        assert isinstance(ev["graph_ids"], list)
        assert isinstance(ev["file_paths"], list)

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_synthesize_contract_called_with_results_kwarg(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """
        Finding 1: synthesize_contract must be called with results=,
        not contexts=. The method signature is:
            synthesize_contract(question, results=None, ...)
        """
        mock_retriever_instance = MockRetriever.return_value
        mock_retriever_instance.query.return_value = mock_hybrid_results

        mock_synth_instance = MockSynthesizer.return_value
        mock_synth_instance.synthesize_contract.return_value = mock_contract

        client.post("/ask", json={"question": "What is TDD?", "provider": "ollama"})

        # Verify the call used results=, not contexts=
        call_kwargs = mock_synth_instance.synthesize_contract.call_args
        assert call_kwargs is not None, "synthesize_contract was not called"
        assert "results" in call_kwargs.kwargs, (
            f"synthesize_contract should be called with results= kwarg, "
            f"got kwargs: {call_kwargs.kwargs}"
        )
        assert (
            "contexts" not in call_kwargs.kwargs
        ), "synthesize_contract should NOT be called with contexts= kwarg"

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_elapsed_ms_in_response(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Response includes elapsed_ms timing field."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200
        data = response.json()
        assert "elapsed_ms" in data
        assert isinstance(data["elapsed_ms"], int)
        assert data["elapsed_ms"] >= 0

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_file_paths_are_relative(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract_absolute_paths,
        mock_hybrid_results,
    ):
        """File paths in evidence should be relative, not absolute."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.synthesize_contract.return_value = mock_contract_absolute_paths

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200
        data = response.json()

        for ev in data["evidence"]:
            for fp in ev["file_paths"]:
                assert not fp.startswith(
                    "/"
                ), f"file_path should be relative, got absolute: {fp}"

    def test_ask_requires_question(self, client):
        """POST /ask without question returns 422."""
        response = client.post("/ask", json={})
        assert response.status_code == 422

    # --- Sources field tests ---

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_sources_field_present_in_response(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Response includes sources list from raw retrieval results."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) == 2

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_source_item_shape(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Each source item has the expected fields."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        data = response.json()
        src = data["sources"][0]

        assert src["doc_id"] == "GOV-0017"
        assert src["section"] == "Purpose"
        assert src["source"] == "vector"
        assert isinstance(src["score"], float)
        assert isinstance(src["related_docs"], list)
        assert "ADR-0182" in src["related_docs"]
        assert "excerpt" in src
        assert "file_path" in src

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_source_file_paths_are_relative(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Source file_path should be relative, not absolute."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        data = response.json()

        for src in data["sources"]:
            assert not src["file_path"].startswith(
                "/"
            ), f"source file_path should be relative, got: {src['file_path']}"

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_source_excerpt_is_truncated(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Source excerpt should be truncated to at most 300 characters."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        data = response.json()

        for src in data["sources"]:
            assert len(src["excerpt"]) <= 303  # 300 + "..."


class TestAskSearchOptions:
    """Tests for extended AskRequest search options (Phase 2).

    Verifies that HybridRetriever.query() parameters are accepted
    by the API and forwarded correctly to the retriever.
    """

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_ask_accepts_expand_graph_false(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """POST /ask with expand_graph=false should pass through to retriever."""
        mock_retriever = MockRetriever.return_value
        mock_retriever.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post(
            "/ask",
            json={
                "question": "What is TDD?",
                "expand_graph": False,
            },
        )
        assert response.status_code == 200

        call_kwargs = mock_retriever.query.call_args
        assert call_kwargs.kwargs.get("expand_graph") is False

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_ask_accepts_use_bm25_false(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """POST /ask with use_bm25=false should pass through to retriever."""
        mock_retriever = MockRetriever.return_value
        mock_retriever.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post(
            "/ask",
            json={
                "question": "What is TDD?",
                "use_bm25": False,
            },
        )
        assert response.status_code == 200

        call_kwargs = mock_retriever.query.call_args
        assert call_kwargs.kwargs.get("use_bm25") is False

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_ask_accepts_point_in_time(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """POST /ask with point_in_time should pass through to retriever."""
        mock_retriever = MockRetriever.return_value
        mock_retriever.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post(
            "/ask",
            json={
                "question": "What is TDD?",
                "point_in_time": "2026-01-01T00:00:00Z",
            },
        )
        assert response.status_code == 200

        call_kwargs = mock_retriever.query.call_args
        assert call_kwargs.kwargs.get("point_in_time") == "2026-01-01T00:00:00Z"

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_ask_accepts_expand_query_synonyms(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """POST /ask with expand_query_synonyms should pass through."""
        mock_retriever = MockRetriever.return_value
        mock_retriever.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post(
            "/ask",
            json={
                "question": "What is TDD?",
                "expand_query_synonyms": False,
            },
        )
        assert response.status_code == 200

        call_kwargs = mock_retriever.query.call_args
        assert call_kwargs.kwargs.get("expand_query_synonyms") is False

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_ask_backward_compatible_minimal_request(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """POST /ask with only question still works (backward compatible)."""
        mock_retriever = MockRetriever.return_value
        mock_retriever.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200

        # Defaults should be: expand_graph=True, use_bm25=True
        call_kwargs = mock_retriever.query.call_args
        expand_graph = call_kwargs.kwargs.get("expand_graph", True)
        use_bm25 = call_kwargs.kwargs.get("use_bm25", True)
        assert expand_graph is True or expand_graph is None
        assert use_bm25 is True or use_bm25 is None

    def test_health_includes_graphiti_status(self, client):
        """Health endpoint should include graphiti status field."""
        response = client.get("/health")
        data = response.json()
        assert "graphiti" in data, "health response should include graphiti field"
        assert isinstance(data["graphiti"], bool)


class TestGraphitiMemory:
    """Tests for Graphiti agent memory integration (Phase 4)."""

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_memory_disabled_skips_graphiti(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """When enable_memory=false, Graphiti should not be called."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        with patch("scripts.rag.graphiti_client.SyncGraphitiMemory") as MockMemory:
            response = client.post(
                "/ask",
                json={
                    "question": "What is TDD?",
                    "enable_memory": False,
                },
            )
            assert response.status_code == 200
            MockMemory.assert_not_called()

    @patch("scripts.rag.graphiti_client.SyncGraphitiMemory")
    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_memory_enabled_calls_search_and_add_episode(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        MockMemory,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """When enable_memory=true and Neo4j connected, search + add_episode called."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        mock_memory_inst = MockMemory.return_value
        mock_memory_inst.is_available = True
        mock_memory_inst.initialize.return_value = True
        mock_memory_inst.search.return_value = []

        with patch("app.NEO4J_CONNECTED", True):
            response = client.post(
                "/ask",
                json={
                    "question": "What is TDD?",
                    "enable_memory": True,
                },
            )
            assert response.status_code == 200
            mock_memory_inst.search.assert_called_once()
            mock_memory_inst.add_episode.assert_called_once()
            mock_memory_inst.close.assert_called_once()

    @patch("scripts.rag.graphiti_client.SyncGraphitiMemory")
    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_memory_failure_does_not_break_query(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        MockMemory,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Memory failure should not prevent the query from returning."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        mock_memory_inst = MockMemory.return_value
        mock_memory_inst.is_available = True
        mock_memory_inst.initialize.side_effect = Exception("Neo4j down")

        with patch("app.NEO4J_CONNECTED", True):
            response = client.post(
                "/ask",
                json={
                    "question": "What is TDD?",
                    "enable_memory": True,
                },
            )
            # Query should still succeed despite memory failure
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data


class TestStreamEndpoint:
    """Tests for POST /ask/stream SSE endpoint (Phase 5)."""

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_stream_endpoint_returns_sse_content_type(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_hybrid_results,
    ):
        """POST /ask/stream should return text/event-stream content type."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.stream_answer.return_value = iter(["Test ", "answer."])
        mock_synth.build_contract_from_results.return_value = {
            "answer": "Test answer.",
            "evidence": [],
            "sources": [],
            "timestamp": "2026-02-08T12:00:00Z",
            "limitations": "Test only.",
            "next_step": "",
        }

        response = client.post("/ask/stream", json={"question": "What is TDD?"})
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_stream_emits_status_and_token_events(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_hybrid_results,
    ):
        """Stream should emit status events then token events."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.stream_answer.return_value = iter(["Hello ", "world."])
        mock_synth.build_contract_from_results.return_value = {
            "answer": "Hello world.",
            "evidence": [],
            "sources": [],
            "timestamp": "2026-02-08T12:00:00Z",
            "limitations": "Test only.",
            "next_step": "",
        }

        response = client.post("/ask/stream", json={"question": "What is TDD?"})
        body = response.text
        assert "event: status" in body
        assert "event: token" in body
        assert "event: complete" in body

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_stream_emits_error_event_on_llm_failure(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_hybrid_results,
    ):
        """Stream should emit error event when LLM fails mid-stream."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        mock_synth = MockSynthesizer.return_value
        mock_synth.stream_answer.side_effect = Exception("LLM timeout")

        response = client.post("/ask/stream", json={"question": "What is TDD?"})
        body = response.text
        assert "event: error" in body

    @patch("scripts.rag.llm_synthesis.RAGSynthesizer")
    @patch("scripts.rag.hybrid_retriever.HybridRetriever")
    @patch("scripts.rag.retriever.GovernanceRetriever")
    def test_non_stream_ask_endpoint_still_works(
        self,
        MockGovRetriever,
        MockRetriever,
        MockSynthesizer,
        client,
        mock_contract,
        mock_hybrid_results,
    ):
        """Original /ask endpoint should still work unchanged."""
        MockRetriever.return_value.query.return_value = mock_hybrid_results
        MockSynthesizer.return_value.synthesize_contract.return_value = mock_contract

        response = client.post("/ask", json={"question": "What is TDD?"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "evidence" in data
