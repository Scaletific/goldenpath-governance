#!/usr/bin/env python3
"""
---
id: SCRIPT-0080
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-29
test:
  runner: pytest
  command: "pytest -q tests/unit/test_llm_synthesis.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0017-tdd-and-determinism
  - SCRIPT-0079-hybrid-retriever
---
Purpose: LLM synthesis for RAG responses using multiple providers.

Supports:
- Ollama (local, free) - llama3.2, mistral, phi3, etc.
- Claude (API) - claude-3-haiku, claude-sonnet-4-20250514, etc.
- OpenAI (API) - gpt-4o-mini, gpt-4o, etc.
- Gemini (API) - gemini-3-flash, gemini-2.5-flash, gemini-2.5-pro, etc.

Phase 1 implementation per PRD-0008.

Example:
    >>> from scripts.rag.llm_synthesis import synthesize_answer
    >>> answer = synthesize_answer("What are TDD requirements?", provider="ollama")
    >>> answer = synthesize_answer("What are TDD requirements?", provider="claude")
    >>> answer = synthesize_answer("What are TDD requirements?", provider="openai")
    >>> answer = synthesize_answer("What are TDD requirements?", provider="gemini")
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

# JSON Schema validation
try:
    from jsonschema import Draft202012Validator, ValidationError

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    Draft202012Validator = None
    ValidationError = Exception

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv

    # Look for .env in repo root (two levels up from scripts/rag/)
    _repo_root = Path(__file__).resolve().parents[2]
    _env_file = _repo_root / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate

    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    LANGCHAIN_CORE_AVAILABLE = False
    ChatPromptTemplate = None

# Ollama
try:
    from langchain_ollama import ChatOllama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ChatOllama = None

# Claude/Anthropic
try:
    from langchain_anthropic import ChatAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    ChatAnthropic = None

# OpenAI
try:
    from langchain_openai import ChatOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    ChatOpenAI = None

# Google Gemini
try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    ChatGoogleGenerativeAI = None

from scripts.rag.hybrid_retriever import HybridRetriever, HybridResult
from scripts.rag.retriever import RetrievalResult, format_citation


# =============================================================================
# Answer Contract (per schemas/metadata/answer_contract.schema.json)
# =============================================================================

# Path to answer contract schema
SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "metadata"
    / "answer_contract.schema.json"
)


def _load_answer_schema() -> Optional[Dict[str, Any]]:
    """Load the answer contract schema if available."""
    if SCHEMA_PATH.exists():
        return json.loads(SCHEMA_PATH.read_text())
    return None


def _get_git_sha() -> Optional[str]:
    """Get current git commit SHA for source tracking."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]
    except Exception:
        pass
    return None


@dataclass
class EvidenceItem:
    """Evidence item for answer contract."""

    graph_ids: List[str]
    file_paths: List[str]
    excerpt: Optional[str] = None
    source_sha: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "graph_ids": self.graph_ids,
            "file_paths": self.file_paths,
        }
        if self.excerpt:
            result["excerpt"] = self.excerpt
        if self.source_sha:
            result["source_sha"] = self.source_sha
        return result


@dataclass
class AnswerContract:
    """
    Contract-compliant RAG answer.

    Per schemas/metadata/answer_contract.schema.json:
    - answer: The response text
    - evidence: List of evidence items with graph_ids and file_paths
    - timestamp: ISO timestamp
    - limitations: What the answer doesn't cover
    - next_step: Suggested follow-up action

    Rule: Either evidence.length >= 1 OR answer === "unknown" (abstention)
    """

    answer: str
    evidence: List[EvidenceItem]
    timestamp: str
    limitations: str
    next_step: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "answer": self.answer,
            "evidence": [e.to_dict() for e in self.evidence],
            "timestamp": self.timestamp,
            "limitations": self.limitations,
            "next_step": self.next_step,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def validate(self) -> bool:
        """
        Validate against the answer contract schema.

        Returns True if valid, raises ValidationError if invalid.
        """
        if not JSONSCHEMA_AVAILABLE:
            # Can't validate without jsonschema, assume valid
            return True

        schema = _load_answer_schema()
        if schema is None:
            return True

        Draft202012Validator(schema).validate(self.to_dict())
        return True

    @classmethod
    def unknown(
        cls, limitations: str = "No relevant information found."
    ) -> "AnswerContract":
        """Create an abstention answer (no evidence available)."""
        return cls(
            answer="unknown",
            evidence=[],
            timestamp=datetime.now(timezone.utc).isoformat(),
            limitations=limitations,
            next_step="Try rephrasing your question or consult the documentation directly.",
        )


class LLMProvider(Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"


# Default settings per provider
DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Legacy aliases
DEFAULT_MODEL = DEFAULT_OLLAMA_MODEL
DEFAULT_BASE_URL = DEFAULT_OLLAMA_URL
LANGCHAIN_AVAILABLE = LANGCHAIN_CORE_AVAILABLE and OLLAMA_AVAILABLE

# System prompt for governance RAG
SYSTEM_PROMPT = """You are a senior platform engineer who knows the GoldenPath IDP inside and out.
You have deep expertise in infrastructure-as-code, governance frameworks, architecture decisions,
and platform engineering best practices.

When answering questions:
- Think through the question carefully before responding
- Explain the "why" behind decisions, not just the "what"
- Connect related concepts across documents when relevant — e.g. if a policy references an ADR, explain how they fit together
- Use markdown formatting for readability: headers, bullet points, code blocks where appropriate
- If something has changed over time (superseded ADRs, updated policies), note the evolution
- When the context is insufficient, say what you'd need to give a better answer
- Cite sources naturally inline using [DOC-ID](file_path) format

Ground your answers in the provided context. If the context doesn't cover the question, be upfront about it rather than speculating."""

RAG_PROMPT_TEMPLATE = """Here are the relevant governance documents:

{context}

---

Question: {question}

Think through this carefully and give a thorough, useful answer. Cite your sources."""

# Contract-compliant prompt for structured output
# NOTE: Double curly braces are escaped for LangChain template
CONTRACT_SYSTEM_PROMPT = """You are a senior platform engineer who knows the GoldenPath IDP inside and out.
You have deep expertise in infrastructure-as-code, governance frameworks, architecture decisions,
and platform engineering best practices.

Think through questions carefully. Explain the reasoning behind decisions, connect related
concepts across documents, and help the user understand not just what the answer is but why
it matters and what they should do next.

Firts respnd with "excerpt": "Key quote from the source that supports your answer"
You MUST respond with a valid JSON object matching this structure:
{{
  "answer": "Your detailed answer here — use markdown formatting (headers, bullets, code blocks) for readability",
  "evidence": [
    {{
      "graph_ids": ["DOC-ID-1", "DOC-ID-2"],
      "file_paths": ["path/to/file1.md", "path/to/file2.md"],
      "excerpt": "Key quote from the source that supports your answer"
    }}
  ],
  "limitations": "What this answer doesn't cover, assumptions made, or areas where you'd want to verify",
  "next_step": "A specific, actionable follow-up — what should the user read, run, or do next"
}}

Guidelines:
1. Ground your answer in the provided context — don't speculate beyond what the documents say
2. The "answer" field should be conversational and thorough, like explaining to a colleague — use markdown for structure
3. Connect dots between documents when multiple sources are relevant — explain how they relate
4. Each evidence item MUST include at least one graph_id and one file_path from the context
5. Make "limitations" genuinely useful — what adjacent topics weren't covered, what might have changed
6. Make "next_step" specific and actionable — a command to run, a doc to read, a decision to make
7. If the context is insufficient, be honest about it in "answer" and suggest where to look in "next_step"
8. Output ONLY the JSON object, no surrounding text"""

CONTRACT_PROMPT_TEMPLATE = """Here are the relevant governance documents:

{context}

---

Question: {question}

Think through this carefully. Give a thorough, conversational answer that helps the user
understand both the "what" and the "why". Respond with the JSON object."""


def _check_ollama_available() -> bool:
    """Check if Ollama is installed and running."""
    if not LANGCHAIN_AVAILABLE:
        return False
    try:
        import httpx

        response = httpx.get(f"{DEFAULT_BASE_URL}/api/tags", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def _format_context(results: List[Union[HybridResult, RetrievalResult]]) -> str:
    """Format retrieval results as context for LLM."""
    context_parts = []

    for i, result in enumerate(results, 1):
        # Get metadata
        if isinstance(result, HybridResult):
            metadata = result.metadata
            text = result.text
        else:
            metadata = result.metadata
            text = result.text

        doc_id = metadata.get("doc_id", "Unknown")
        section = metadata.get("section", "")
        file_path = metadata.get("file_path", "")

        # Format chunk
        header = f"[{i}] {doc_id}"
        if section:
            header += f" - {section}"
        if file_path:
            header += f" ({file_path})"

        context_parts.append(f"{header}\n{text}")

    return "\n\n---\n\n".join(context_parts)


def _format_citations(results: List[Union[HybridResult, RetrievalResult]]) -> str:
    """Format citations list."""
    citations = []
    seen = set()

    for result in results:
        if isinstance(result, HybridResult):
            # Convert to RetrievalResult for format_citation
            rr = RetrievalResult(
                id=result.id,
                text=result.text,
                metadata=result.metadata,
                score=result.score,
            )
        else:
            rr = result

        citation = format_citation(rr)
        doc_id = rr.metadata.get("doc_id", "")

        if doc_id and doc_id not in seen:
            seen.add(doc_id)
            citations.append(citation)

    return "\n".join(f"- {c}" for c in citations)


@dataclass
class SynthesisResult:
    """Result from LLM synthesis."""

    answer: str
    citations: List[str]
    model: str
    context_chunks: int
    source_docs: List[str]


def _create_llm(
    provider: str, model: str, temperature: float = 0.1, base_url: Optional[str] = None
):
    """
    Create an LLM instance for the specified provider.

    Args:
        provider: One of "ollama", "claude", "openai".
        model: Model name for the provider.
        temperature: LLM temperature.
        base_url: Base URL (only for Ollama).

    Returns:
        LangChain chat model instance or None.
    """
    provider = provider.lower()

    if provider == "ollama":
        if not OLLAMA_AVAILABLE:
            return None
        try:
            return ChatOllama(
                model=model,
                base_url=base_url or DEFAULT_OLLAMA_URL,
                temperature=temperature,
            )
        except Exception:
            return None

    elif provider == "claude":
        if not ANTHROPIC_AVAILABLE:
            return None
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        try:
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                api_key=api_key,
            )
        except Exception:
            return None

    elif provider == "openai":
        if not OPENAI_AVAILABLE:
            return None
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=api_key,
            )
        except Exception:
            return None

    elif provider == "gemini":
        if not GEMINI_AVAILABLE:
            return None
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None
        try:
            return ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                google_api_key=api_key,
            )
        except Exception:
            return None

    return None


@dataclass
class RAGSynthesizer:
    """
    LLM synthesizer for RAG responses using multiple providers.

    Attributes:
        provider: LLM provider ("ollama", "claude", "openai").
        model: Model name for the provider.
        base_url: Ollama server URL (only for Ollama provider).
        temperature: LLM temperature (default: 0.1 for factual responses).
        retriever: HybridRetriever for context retrieval.
    """

    provider: str = DEFAULT_PROVIDER
    model: Optional[str] = None
    base_url: str = DEFAULT_OLLAMA_URL
    temperature: float = 0.1
    retriever: Optional[HybridRetriever] = None
    _llm: Any = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Initialize LLM and retriever."""
        if self.retriever is None:
            self.retriever = HybridRetriever()

        # Set default model based on provider if not specified
        if self.model is None:
            if self.provider == "claude":
                self.model = DEFAULT_CLAUDE_MODEL
            elif self.provider == "openai":
                self.model = DEFAULT_OPENAI_MODEL
            elif self.provider == "gemini":
                self.model = DEFAULT_GEMINI_MODEL
            else:
                self.model = DEFAULT_OLLAMA_MODEL

        # Create LLM
        self._llm = _create_llm(
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
            base_url=self.base_url,
        )

    def is_available(self) -> bool:
        """Check if LLM synthesis is available."""
        if self._llm is None:
            return False
        if self.provider == "ollama":
            return _check_ollama_available()
        # For API-based providers, having a valid LLM means we have an API key
        return True

    def synthesize(
        self,
        question: str,
        results: Optional[List[Union[HybridResult, RetrievalResult]]] = None,
        top_k: int = 5,
        expand_graph: bool = True,
    ) -> SynthesisResult:
        """
        Synthesize an answer from retrieved chunks.

        Args:
            question: User's question.
            results: Pre-fetched retrieval results. If None, fetches via retriever.
            top_k: Number of chunks to retrieve (if results not provided).
            expand_graph: Whether to use graph expansion.

        Returns:
            SynthesisResult with answer, citations, and metadata.
        """
        # Fetch results if not provided
        if results is None:
            results = self.retriever.query(
                query_text=question,
                top_k=top_k,
                expand_graph=expand_graph,
            )

        if not results:
            return SynthesisResult(
                answer="I couldn't find any relevant information to answer your question.",
                citations=[],
                model=self.model,
                context_chunks=0,
                source_docs=[],
            )

        # Format context
        context = _format_context(results)

        # Extract source docs
        source_docs = []
        seen_docs = set()
        for r in results:
            doc_id = r.metadata.get("doc_id")
            if doc_id and doc_id not in seen_docs:
                seen_docs.add(doc_id)
                source_docs.append(doc_id)

        # If LLM not available, return formatted context
        if not self.is_available():
            return SynthesisResult(
                answer=f"[LLM not available - raw context]\n\n{context}",
                citations=[
                    format_citation(
                        RetrievalResult(
                            id=r.id, text=r.text, metadata=r.metadata, score=r.score
                        )
                    )
                    for r in results
                ],
                model="none",
                context_chunks=len(results),
                source_docs=source_docs,
            )

        # Build prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", RAG_PROMPT_TEMPLATE),
            ]
        )

        # Generate response
        try:
            chain = prompt | self._llm
            response = chain.invoke(
                {
                    "context": context,
                    "question": question,
                }
            )
            answer = response.content
        except Exception as e:
            answer = f"Error generating response: {e}\n\nContext:\n{context}"

        # Extract citations
        citations = []
        for r in results:
            rr = RetrievalResult(
                id=r.id, text=r.text, metadata=r.metadata, score=r.score
            )
            citations.append(format_citation(rr))

        return SynthesisResult(
            answer=answer,
            citations=citations,
            model=self.model,
            context_chunks=len(results),
            source_docs=source_docs,
        )

    def synthesize_contract(
        self,
        question: str,
        results: Optional[List[Union[HybridResult, RetrievalResult]]] = None,
        top_k: int = 5,
        expand_graph: bool = True,
        validate: bool = True,
    ) -> AnswerContract:
        """
        Synthesize a contract-compliant answer from retrieved chunks.

        Per schemas/metadata/answer_contract.schema.json, the answer includes:
        - answer: Response text
        - evidence: List of evidence items with graph_ids, file_paths
        - timestamp: ISO timestamp
        - limitations: What the answer doesn't cover
        - next_step: Suggested follow-up action

        Args:
            question: User's question.
            results: Pre-fetched retrieval results. If None, fetches via retriever.
            top_k: Number of chunks to retrieve (if results not provided).
            expand_graph: Whether to use graph expansion.
            validate: Whether to validate against JSON schema.

        Returns:
            AnswerContract with validated, structured answer.
        """
        # Fetch results if not provided
        if results is None:
            results = self.retriever.query(
                query_text=question,
                top_k=top_k,
                expand_graph=expand_graph,
            )

        if not results:
            return AnswerContract.unknown(
                limitations="No relevant documents found for this query."
            )

        # Format context with clear markers for LLM
        context = _format_context(results)

        # Get source SHA for provenance
        source_sha = _get_git_sha()

        # If LLM not available, build contract from raw results
        if not self.is_available():
            evidence = []
            for r in results:
                doc_id = r.metadata.get("doc_id", "unknown")
                file_path = r.metadata.get("file_path", "")
                evidence.append(
                    EvidenceItem(
                        graph_ids=[doc_id],
                        file_paths=[file_path] if file_path else ["unknown"],
                        excerpt=r.text[:200] if r.text else None,
                        source_sha=source_sha,
                    )
                )
            contract = AnswerContract(
                answer=f"[LLM not available - raw results]\n\n{context[:500]}...",
                evidence=evidence,
                timestamp=datetime.now(timezone.utc).isoformat(),
                limitations="LLM synthesis unavailable; showing raw retrieval results.",
                next_step="Configure an LLM provider for synthesized answers.",
            )
            if validate:
                contract.validate()
            return contract

        # Build contract-aware prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CONTRACT_SYSTEM_PROMPT),
                ("human", CONTRACT_PROMPT_TEMPLATE),
            ]
        )

        # Generate response
        try:
            chain = prompt | self._llm
            response = chain.invoke(
                {
                    "context": context,
                    "question": question,
                }
            )
            raw_response = response.content

            # Parse JSON from response
            # Handle markdown code blocks if present
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0]
            elif "```" in raw_response:
                raw_response = raw_response.split("```")[1].split("```")[0]

            parsed = json.loads(raw_response.strip())

            # Build evidence items
            evidence = []
            for e in parsed.get("evidence", []):
                evidence.append(
                    EvidenceItem(
                        graph_ids=e.get("graph_ids", []),
                        file_paths=e.get("file_paths", []),
                        excerpt=e.get("excerpt"),
                        source_sha=source_sha,
                    )
                )

            contract = AnswerContract(
                answer=parsed.get("answer", "unknown"),
                evidence=evidence,
                timestamp=datetime.now(timezone.utc).isoformat(),
                limitations=parsed.get("limitations", "No limitations specified."),
                next_step=parsed.get("next_step", "Review the source documents."),
            )

        except json.JSONDecodeError as e:
            # Fallback: construct contract from non-JSON response
            evidence = []
            for r in results:
                doc_id = r.metadata.get("doc_id", "unknown")
                file_path = r.metadata.get("file_path", "")
                evidence.append(
                    EvidenceItem(
                        graph_ids=[doc_id],
                        file_paths=[file_path] if file_path else ["unknown"],
                        excerpt=r.text[:200] if r.text else None,
                        source_sha=source_sha,
                    )
                )
            contract = AnswerContract(
                answer=raw_response
                if "raw_response" in dir()
                else "Error parsing response",
                evidence=evidence,
                timestamp=datetime.now(timezone.utc).isoformat(),
                limitations=f"LLM returned non-JSON response: {e}",
                next_step="Review the raw answer and source documents.",
            )
        except Exception as e:
            contract = AnswerContract(
                answer=f"Error: {e}",
                evidence=[],
                timestamp=datetime.now(timezone.utc).isoformat(),
                limitations=f"Error during synthesis: {e}",
                next_step="Retry the query or check LLM configuration.",
            )

        # Validate against schema if requested
        if validate:
            try:
                contract.validate()
            except ValidationError as e:
                # Log validation error but return the contract anyway
                contract.limitations += f" [Schema validation warning: {e.message}]"

        return contract

    def stream_answer(self, question: str, results: list):
        """Yield LLM tokens for the answer prose only (no JSON).

        Uses a dedicated answer-only prompt — NOT CONTRACT_PROMPT_TEMPLATE.
        """
        context = _format_context(results)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a governance knowledge assistant for the GoldenPath IDP.",
                ),
                (
                    "human",
                    "Based on the context below, provide a clear, comprehensive answer "
                    "to the question. Write in plain prose only — no JSON, no metadata, "
                    "no structured formatting beyond markdown.\n\n"
                    "Context:\n{context}\n\nQuestion: {question}",
                ),
            ]
        )
        chain = prompt | self._llm
        for chunk in chain.stream({"context": context, "question": question}):
            yield chunk.content

    def build_contract_from_results(
        self, answer: str, question: str, results: list
    ) -> dict:
        """Build contract fields from retrieval metadata. No LLM call."""
        evidence = []
        for r in results[:5]:
            if isinstance(r, HybridResult):
                file_path = r.metadata.get("file_path", "")
                excerpt = (r.text or "")[:200]
            else:
                file_path = r.metadata.get("file_path", "")
                excerpt = (r.text or "")[:200]
            evidence.append(
                {
                    "graph_ids": [],
                    "file_paths": [file_path] if file_path else [],
                    "excerpt": excerpt,
                }
            )

        sources = []
        for r in results:
            if isinstance(r, HybridResult):
                sources.append(
                    {
                        "doc_id": r.metadata.get("doc_id", ""),
                        "section": r.metadata.get("section", ""),
                        "file_path": r.metadata.get("file_path", ""),
                        "score": round(r.score, 4) if r.score else 0.0,
                        "source": r.source or "unknown",
                        "excerpt": (r.text or "")[:300],
                        "related_docs": r.related_docs or [],
                    }
                )

        return {
            "answer": answer,
            "evidence": evidence,
            "sources": sources,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "limitations": "Answer synthesized from indexed governance documents only.",
            "next_step": "",
        }

    def close(self):
        """Close retriever resources."""
        if self.retriever is not None:
            self.retriever.close()


def synthesize_answer(
    question: str,
    results: Optional[List[Union[HybridResult, RetrievalResult]]] = None,
    provider: str = DEFAULT_PROVIDER,
    model: Optional[str] = None,
    top_k: int = 5,
    expand_graph: bool = True,
) -> str:
    """
    Convenience function to synthesize an answer.

    Args:
        question: User's question.
        results: Pre-fetched retrieval results.
        provider: LLM provider ("ollama", "claude", "openai").
        model: Model name (uses provider default if not specified).
        top_k: Number of chunks to retrieve.
        expand_graph: Whether to use graph expansion.

    Returns:
        Synthesized answer string.
    """
    synthesizer = RAGSynthesizer(provider=provider, model=model)
    try:
        result = synthesizer.synthesize(
            question=question,
            results=results,
            top_k=top_k,
            expand_graph=expand_graph,
        )
        return result.answer
    finally:
        synthesizer.close()


def check_ollama_status() -> Dict[str, Any]:
    """
    Check Ollama server status and available models.

    Returns:
        Dict with status, available models, and default model.
    """
    status = {
        "available": False,
        "base_url": DEFAULT_OLLAMA_URL,
        "default_model": DEFAULT_OLLAMA_MODEL,
        "models": [],
        "langchain_installed": OLLAMA_AVAILABLE,
    }

    if not OLLAMA_AVAILABLE:
        status["error"] = "langchain-ollama not installed"
        return status

    try:
        import httpx

        response = httpx.get(f"{DEFAULT_OLLAMA_URL}/api/tags", timeout=5.0)
        if response.status_code == 200:
            status["available"] = True
            data = response.json()
            status["models"] = [m["name"] for m in data.get("models", [])]
        else:
            status["error"] = f"HTTP {response.status_code}"
    except Exception as e:
        status["error"] = str(e)

    return status


def check_provider_status(provider: str = None) -> Dict[str, Any]:
    """
    Check status for a specific provider or all providers.

    Args:
        provider: Specific provider to check, or None for all.

    Returns:
        Dict with provider status information.
    """
    if provider:
        provider = provider.lower()

    status = {
        "default_provider": DEFAULT_PROVIDER,
        "providers": {},
    }

    # Check Ollama
    if provider is None or provider == "ollama":
        ollama_status = check_ollama_status()
        status["providers"]["ollama"] = {
            "available": ollama_status["available"],
            "installed": OLLAMA_AVAILABLE,
            "default_model": DEFAULT_OLLAMA_MODEL,
            "models": ollama_status.get("models", []),
            "error": ollama_status.get("error"),
        }

    # Check Claude
    if provider is None or provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        status["providers"]["claude"] = {
            "available": ANTHROPIC_AVAILABLE and bool(api_key),
            "installed": ANTHROPIC_AVAILABLE,
            "default_model": DEFAULT_CLAUDE_MODEL,
            "api_key_set": bool(api_key),
            "error": None
            if ANTHROPIC_AVAILABLE
            else "langchain-anthropic not installed",
        }
        if ANTHROPIC_AVAILABLE and not api_key:
            status["providers"]["claude"]["error"] = "ANTHROPIC_API_KEY not set"

    # Check OpenAI
    if provider is None or provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        status["providers"]["openai"] = {
            "available": OPENAI_AVAILABLE and bool(api_key),
            "installed": OPENAI_AVAILABLE,
            "default_model": DEFAULT_OPENAI_MODEL,
            "api_key_set": bool(api_key),
            "error": None if OPENAI_AVAILABLE else "langchain-openai not installed",
        }
        if OPENAI_AVAILABLE and not api_key:
            status["providers"]["openai"]["error"] = "OPENAI_API_KEY not set"

    # Check Gemini
    if provider is None or provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        status["providers"]["gemini"] = {
            "available": GEMINI_AVAILABLE and bool(api_key),
            "installed": GEMINI_AVAILABLE,
            "default_model": DEFAULT_GEMINI_MODEL,
            "api_key_set": bool(api_key),
            "error": None
            if GEMINI_AVAILABLE
            else "langchain-google-genai not installed",
        }
        if GEMINI_AVAILABLE and not api_key:
            status["providers"]["gemini"]["error"] = "GEMINI_API_KEY not set"

    return status


if __name__ == "__main__":
    import json
    import sys

    # Parse args
    provider = sys.argv[1] if len(sys.argv) > 1 else None

    # Check status
    status = check_provider_status(provider)
    print("LLM Provider Status:")
    print(json.dumps(status, indent=2))

    # Find first available provider
    available_provider = None
    for p, info in status["providers"].items():
        if info["available"]:
            available_provider = p
            break

    if available_provider:
        print(f"\nTest query using {available_provider}:")
        answer = synthesize_answer(
            "What are the TDD requirements?",
            provider=available_provider,
            top_k=3,
            expand_graph=True,
        )
        print(answer)
    else:
        print("\nNo providers available. Set up one of:")
        print("  - Ollama: brew install ollama && ollama serve && ollama pull llama3.2")
        print("  - Claude: export ANTHROPIC_API_KEY='sk-ant-...'")
        print("  - OpenAI: export OPENAI_API_KEY='sk-...'")
        print("  - Gemini: export GEMINI_API_KEY='...'")
        print("\nAnd install the provider package:")
        print("  - pip install langchain-anthropic     # for Claude")
        print("  - pip install langchain-openai        # for OpenAI")
        print("  - pip install langchain-google-genai  # for Gemini")
