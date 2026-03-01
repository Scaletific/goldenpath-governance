"""
FastAPI backend for the GoldenPath RAG Web UI.

Thin wrapper around the existing scripts/rag/ package.
No retrieval logic is reimplemented here — all RAG operations
delegate to hybrid_retriever, llm_synthesis, and result_reranker.

API surface:
  POST /ask       — question → AnswerContract JSON
  GET  /health    — service health check
  GET  /providers — available LLM providers
  GET  /document  — full document content by repo-relative path

See: PRD-0011, ADR-0189
"""

import json
import os
import sys
import time
from contextlib import nullcontext
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add repo root to sys.path so we can import scripts.rag.*
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv()

# ---------------------------------------------------------------------------
# Neo4j graph expansion (optional — falls back to vector-only retrieval)
# ---------------------------------------------------------------------------

NEO4J_CONNECTED = bool(os.getenv("NEO4J_URI") and os.getenv("NEO4J_PASSWORD"))

# ---------------------------------------------------------------------------
# Phoenix observability (optional — graceful degradation)
# ---------------------------------------------------------------------------

PHOENIX_ENABLED = False
_tracer = None
_OI_SPAN_KIND = None  # OpenInference span kind attribute key
_OI_KINDS = None  # OpenInference span kind enum values
_OI_ATTRS = None  # OpenInference span attribute keys

try:
    import phoenix as px
    from openinference.instrumentation.langchain import LangChainInstrumentor
    from openinference.semconv.trace import (
        OpenInferenceSpanKindValues as _OI_KINDS,
        SpanAttributes as _OI_ATTRS,
    )
    from opentelemetry import trace
    from phoenix.otel import register

    # Persist trace data across restarts (default is ephemeral /tmp)
    _phoenix_dir = REPO_ROOT / ".phoenix"
    _phoenix_dir.mkdir(exist_ok=True)
    os.environ.setdefault("PHOENIX_WORKING_DIR", str(_phoenix_dir))

    px.launch_app(use_temp_dir=False)
    _tracer_provider = register()
    # Only instrument LangChain — LlamaIndex is not used at runtime
    LangChainInstrumentor().instrument(tracer_provider=_tracer_provider)
    _tracer = trace.get_tracer("rag-web-ui")
    PHOENIX_ENABLED = True
except Exception:
    # Phoenix not installed or failed to start — backend works without it
    pass

app = FastAPI(
    title="GoldenPath RAG API",
    description="Contract-driven governance retrieval API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class AskRequest(BaseModel):
    question: str
    provider: Optional[str] = None
    top_k: Optional[int] = 10
    expand_graph: Optional[bool] = True
    use_bm25: Optional[bool] = True
    point_in_time: Optional[str] = None
    expand_depth: Optional[int] = 1
    expand_query_synonyms: Optional[bool] = True
    enable_memory: Optional[bool] = False


class EvidenceItem(BaseModel):
    graph_ids: list[str]
    file_paths: list[str]
    excerpt: Optional[str] = None
    source_sha: Optional[str] = None


class SourceItem(BaseModel):
    """Raw retrieval result from hybrid search (not LLM-extracted)."""

    doc_id: str
    section: str
    file_path: str
    score: float
    source: str
    excerpt: str
    related_docs: list[str]


class AnswerResponse(BaseModel):
    answer: str
    evidence: list[EvidenceItem]
    timestamp: str
    limitations: str
    next_step: str
    elapsed_ms: Optional[int] = None
    sources: list[SourceItem] = []


class DocumentResponse(BaseModel):
    """Full document content with metadata."""

    file_path: str
    title: str
    content: str
    doc_id: Optional[str] = None
    doc_type: Optional[str] = None


class ProviderInfo(BaseModel):
    id: str
    name: str
    available: bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXCERPT_MAX_LEN = 300


def _hybrid_result_to_source(result, repo_prefix: str) -> SourceItem:
    """Map a HybridResult to a SourceItem for the API response."""
    raw_path = result.metadata.get("file_path", "")
    text = result.text or ""
    excerpt = text[:EXCERPT_MAX_LEN] + "..." if len(text) > EXCERPT_MAX_LEN else text
    return SourceItem(
        doc_id=result.metadata.get("doc_id", ""),
        section=result.metadata.get("section", ""),
        file_path=raw_path.removeprefix(repo_prefix),
        score=round(result.score, 4),
        source=result.source,
        excerpt=excerpt,
        related_docs=result.related_docs or [],
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Service health check."""
    graphiti_available = False
    if NEO4J_CONNECTED:
        try:
            from scripts.rag.graphiti_client import GRAPHITI_AVAILABLE

            graphiti_available = GRAPHITI_AVAILABLE
        except ImportError:
            pass
    return {
        "status": "ok",
        "service": "rag-web-ui",
        "phoenix": PHOENIX_ENABLED,
        "neo4j": NEO4J_CONNECTED,
        "graphiti": graphiti_available,
    }


@app.get("/providers", response_model=list[ProviderInfo])
async def list_providers():
    """Return available LLM providers."""
    providers = [
        ProviderInfo(id="ollama", name="Ollama (Local)", available=True),
        ProviderInfo(id="claude", name="Claude", available=True),
        ProviderInfo(id="openai", name="OpenAI", available=True),
        ProviderInfo(id="gemini", name="Gemini", available=True),
    ]

    # Check if Ollama is actually reachable
    try:
        from scripts.rag.llm_synthesis import _check_ollama_available

        if not _check_ollama_available():
            providers[0].available = False
    except ImportError:
        pass

    return providers


@app.get("/document", response_model=DocumentResponse)
async def get_document(path: str):
    """
    Serve full document content by repo-relative file path.

    Only allows paths within the repo root (no directory traversal).
    """
    from scripts.rag.loader import load_governance_document

    # Reject paths with directory traversal components before any filesystem use
    if ".." in path or path.startswith("/") or path.startswith("\\"):
        raise HTTPException(status_code=403, detail="Path traversal not allowed")

    # Build safe path from validated components
    safe_path = REPO_ROOT.resolve() / Path(path)
    resolved = safe_path.resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise HTTPException(status_code=403, detail="Path traversal not allowed")
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    if not resolved.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    doc = load_governance_document(resolved)
    return DocumentResponse(
        file_path=path,
        title=doc.metadata.get("title", resolved.stem),
        content=doc.content,
        doc_id=doc.metadata.get("id"),
        doc_type=doc.metadata.get("type"),
    )


@app.post("/ask", response_model=AnswerResponse)
async def ask(request: AskRequest):
    """
    Accept a governance question, run hybrid retrieval + LLM synthesis,
    and return an AnswerContract-compliant response.
    """
    try:
        from scripts.rag.hybrid_retriever import HybridRetriever
        from scripts.rag.llm_synthesis import RAGSynthesizer
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"RAG pipeline not available: {e}",
        )

    def _span(name, kind=None):
        """Create an OpenTelemetry span with OpenInference semantic attributes."""
        if not _tracer:
            return nullcontext()
        span = _tracer.start_as_current_span(name)
        return span

    def _set_oi(span, kind, input_val=None, output_val=None):
        """Set OpenInference attributes on a span for Phoenix classification."""
        if span and _OI_ATTRS and _OI_KINDS:
            span.set_attribute(_OI_ATTRS.OPENINFERENCE_SPAN_KIND, kind.value)
            if input_val:
                span.set_attribute(_OI_ATTRS.INPUT_VALUE, str(input_val))
                span.set_attribute(_OI_ATTRS.INPUT_MIME_TYPE, "text/plain")
            if output_val:
                span.set_attribute(_OI_ATTRS.OUTPUT_VALUE, str(output_val))
                span.set_attribute(_OI_ATTRS.OUTPUT_MIME_TYPE, "text/plain")

    start = time.time()

    # Graphiti agent memory — search for context before retrieval
    memory = None
    _memory_context = ""
    if request.enable_memory and NEO4J_CONNECTED:
        try:
            from scripts.rag.graphiti_client import SyncGraphitiMemory

            memory = SyncGraphitiMemory()
            if memory.is_available and memory.initialize():
                mem_results = memory.search(request.question, num_results=3)
                if mem_results:
                    _memory_context = "\n".join(f"- {r.content}" for r in mem_results)
        except Exception:
            memory = None

    with _span("rag.ask") as ask_span:
        _set_oi(ask_span, _OI_KINDS.CHAIN, input_val=request.question)
        if ask_span:
            ask_span.set_attribute("provider", request.provider or "ollama")

        # Retrieve
        with _span("rag.retrieve") as ret_span:
            _set_oi(ret_span, _OI_KINDS.RETRIEVER, input_val=request.question)
            try:
                from scripts.rag.retriever import GovernanceRetriever

                chroma_dir = str(REPO_ROOT / ".chroma")
                vector_retriever = GovernanceRetriever(persist_dir=chroma_dir)
                retriever = HybridRetriever(
                    vector_retriever=vector_retriever,
                    expand_depth=request.expand_depth or 1,
                )
                results = retriever.query(
                    request.question,
                    top_k=request.top_k or 10,
                    expand_graph=request.expand_graph
                    if request.expand_graph is not None
                    else True,
                    use_bm25=request.use_bm25 if request.use_bm25 is not None else True,
                    point_in_time=request.point_in_time,
                    expand_query_synonyms=request.expand_query_synonyms,
                )
                _set_oi(
                    ret_span, _OI_KINDS.RETRIEVER, output_val=f"{len(results)} results"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Retrieval failed: {e}",
                )

        # Synthesize (wraps the LangChain LLM call — child spans auto-captured)
        with _span("rag.synthesize") as syn_span:
            _set_oi(syn_span, _OI_KINDS.CHAIN, input_val=request.question)
            try:
                provider = request.provider or "ollama"
                synthesizer = RAGSynthesizer(provider=provider, retriever=retriever)
                contract = synthesizer.synthesize_contract(
                    question=request.question,
                    results=results,
                )
                _set_oi(syn_span, _OI_KINDS.CHAIN, output_val=contract.answer[:200])
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Synthesis failed: {e}",
                )

        elapsed = time.time() - start

        # Capture episode in Graphiti memory
        if memory:
            try:
                memory.add_episode(
                    content=f"Q: {request.question}\nA: {contract.answer[:500]}",
                    source="rag-web-ui",
                )
                memory.close()
            except Exception:
                pass

        # Validate contract before returning
        with _span("rag.validate") as val_span:
            _set_oi(val_span, _OI_KINDS.GUARDRAIL, input_val="contract validation")
            if not contract.validate():
                raise HTTPException(
                    status_code=500,
                    detail="Answer failed contract validation — refusing to display",
                )

    repo_prefix = str(REPO_ROOT) + "/"

    return AnswerResponse(
        answer=contract.answer,
        evidence=[
            EvidenceItem(
                graph_ids=ev.graph_ids,
                file_paths=[fp.removeprefix(repo_prefix) for fp in ev.file_paths],
                excerpt=ev.excerpt,
                source_sha=ev.source_sha,
            )
            for ev in contract.evidence
        ],
        timestamp=contract.timestamp,
        limitations=contract.limitations,
        next_step=contract.next_step,
        elapsed_ms=int(elapsed * 1000),
        sources=[_hybrid_result_to_source(r, repo_prefix) for r in results],
    )


@app.post("/ask/stream")
async def ask_stream(request: AskRequest):
    """
    Streaming variant of /ask — returns SSE events with token-by-token answer.

    Events:
      status  — phase updates ("retrieving", "synthesizing")
      token   — individual LLM tokens
      complete — final contract JSON
      error   — mid-stream failure
    """
    from sse_starlette.sse import EventSourceResponse

    async def event_generator():
        try:
            from scripts.rag.hybrid_retriever import HybridRetriever
            from scripts.rag.llm_synthesis import RAGSynthesizer
            from scripts.rag.retriever import GovernanceRetriever

            yield {"event": "status", "data": json.dumps({"phase": "retrieving"})}

            chroma_dir = str(REPO_ROOT / ".chroma")
            vector_retriever = GovernanceRetriever(persist_dir=chroma_dir)
            retriever = HybridRetriever(
                vector_retriever=vector_retriever,
                expand_depth=request.expand_depth or 1,
            )
            results = retriever.query(
                request.question,
                top_k=request.top_k or 10,
                expand_graph=request.expand_graph
                if request.expand_graph is not None
                else True,
                use_bm25=request.use_bm25 if request.use_bm25 is not None else True,
                point_in_time=request.point_in_time,
                expand_query_synonyms=request.expand_query_synonyms,
            )

            yield {
                "event": "status",
                "data": json.dumps(
                    {
                        "phase": "synthesizing",
                        "sources_count": len(results),
                    }
                ),
            }

            provider = request.provider or "ollama"
            synthesizer = RAGSynthesizer(provider=provider, retriever=retriever)
            full_answer = ""
            for token in synthesizer.stream_answer(request.question, results):
                full_answer += token
                yield {"event": "token", "data": json.dumps({"text": token})}

            repo_prefix = str(REPO_ROOT) + "/"
            contract = synthesizer.build_contract_from_results(
                full_answer, request.question, results
            )
            # Strip repo prefix from file paths
            for ev in contract.get("evidence", []):
                ev["file_paths"] = [
                    fp.removeprefix(repo_prefix) for fp in ev.get("file_paths", [])
                ]
            for src in contract.get("sources", []):
                src["file_path"] = src.get("file_path", "").removeprefix(repo_prefix)

            yield {"event": "complete", "data": json.dumps(contract)}

        except Exception as e:
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
