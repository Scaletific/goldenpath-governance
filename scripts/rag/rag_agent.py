#!/usr/bin/env python3
"""
---
id: SCRIPT-0084
type: script
owner: platform-team
status: active
maturity: 3
last_validated: 2026-02-03
test:
  runner: pytest
  command: "pytest -q tests/unit/test_rag_agent.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0020-rag-maturity-model
  - ADR-0185-graphiti-agent-memory-framework
  - SCRIPT-0079-hybrid-retriever
  - SCRIPT-0082-query-rewriter
  - SCRIPT-0083-result-reranker
---
Purpose: Agentic RAG with LangGraph orchestration (L3.0).

Implements an agent loop using LangGraph StateGraph:
1. Rewrites the user query (L2.0)
2. Searches the knowledge base
3. Evaluates if the results answer the question
4. Refines the query and retries if not
5. Generates a final answer with reasoning trace

This enables "just works" natural language queries where the agent
figures out the right search strategy automatically.

Architecture aligns with ADR-0185: LangGraph for orchestration,
Graphiti for memory persistence.

Example:
    >>> from scripts.rag.rag_agent import run_agent_query
    >>> result = run_agent_query("What are the phases of RAG implementation?")
    >>> print(result.answer)
    >>> print(result.reasoning_trace)  # See the agent's thought process
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any, List, Union, TypedDict, Annotated, Literal
import operator

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    MemorySaver = None

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatPromptTemplate = None

from scripts.rag.hybrid_retriever import HybridRetriever, HybridResult
from scripts.rag.retriever import RetrievalResult


# Constants
MAX_ITERATIONS = 3


def _create_llm(
    provider: str, model: Optional[str] = None, temperature: float = 0.2
) -> Optional[Any]:
    """Create LLM instance for agent."""
    try:
        from scripts.rag.llm_synthesis import _create_llm as create_llm_base

        if model is None:
            if provider == "gemini":
                model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            elif provider == "claude":
                model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
            elif provider == "openai":
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            else:
                model = os.getenv("OLLAMA_MODEL", "llama3.2")

        return create_llm_base(provider=provider, model=model, temperature=temperature)
    except Exception:
        return None


class AgentState(Enum):
    """States in the agent loop."""

    REWRITE = "rewrite"
    SEARCH = "search"
    EVALUATE = "evaluate"
    REFINE = "refine"
    ANSWER = "answer"
    FAILED = "failed"


@dataclass
class AgentStep:
    """A single step in the agent's reasoning trace."""

    state: AgentState
    query: str
    reasoning: str
    results: List[Union[HybridResult, RetrievalResult]] = field(default_factory=list)
    iteration: int = 1
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class AgentResult:
    """Final result from the agent."""

    answer: str
    evidence: List[Union[HybridResult, RetrievalResult]]
    reasoning_trace: List[AgentStep]
    iterations: int
    success: bool
    model: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# Prompt templates
REWRITE_PROMPT_TEMPLATE = """You are a search query optimizer for governance documentation.

Rewrite this user question into an optimized search query:
- Expand abbreviations (TDD, RAG, ADR, etc.)
- Add synonyms for key terms
- Include document type hints (governance, policy, ADR)

User question: {query}

Output ONLY the optimized search query:"""

EVALUATE_PROMPT_TEMPLATE = """You are evaluating search results for a governance documentation system.

User Question: {query}

Search Results:
{results}

Evaluate whether these results can answer the user's question.

Respond with ONLY a JSON object:
{{
  "found_answer": true/false,
  "confidence": 0.0-1.0,
  "answer": "The answer if found, or null",
  "reasoning": "Why you made this decision",
  "relevant_chunks": [list of chunk indices that are relevant],
  "refined_query": "A better search query if answer not found, or null"
}}"""

REFINE_PROMPT_TEMPLATE = """The previous search for "{original_query}" did not find a good answer.

Results were about: {result_summary}

The user wants to know: {user_question}

Suggest a refined search query that might find better results.
Consider:
- Different terminology (phases vs levels vs stages)
- Specific document IDs if mentioned
- Broader or narrower scope

Output ONLY the refined search query:"""

SYNTHESIZE_PROMPT_TEMPLATE = """Based on the search results, answer the user's question.

User Question: {query}

Relevant Information:
{context}

Provide a clear, concise answer based ONLY on the provided information.
Include citations in the format [DOC-ID: Section].
If the information is incomplete, acknowledge what's missing.

Answer:"""


# =============================================================================
# LangGraph State Definition
# =============================================================================


class GraphState(TypedDict):
    """State for the LangGraph agent."""

    # Input
    question: str
    top_k: int

    # Working state
    current_query: str
    iteration: int
    results: List[HybridResult]
    all_results: List[HybridResult]
    eval_result: dict
    found_answer: bool

    # Output
    answer: str
    reasoning_trace: Annotated[List[AgentStep], operator.add]


# =============================================================================
# LangGraph Node Functions
# =============================================================================


def create_rewrite_node(rewriter: Any, llm: Any):
    """Create the rewrite node function."""

    def rewrite_node(state: GraphState) -> dict:
        """Rewrite the query for better search results."""
        current_query = state["current_query"]
        iteration = state["iteration"]

        if rewriter and rewriter.is_available():
            rewritten = rewriter.rewrite(current_query)
            step = AgentStep(
                state=AgentState.REWRITE,
                query=rewritten,
                reasoning=f"Rewrote '{current_query}' to optimize search",
                iteration=iteration,
            )
            return {
                "current_query": rewritten,
                "reasoning_trace": [step],
            }
        return {}

    return rewrite_node


def create_search_node(retriever: HybridRetriever):
    """Create the search node function."""

    def search_node(state: GraphState) -> dict:
        """Search the knowledge base."""
        query = state["current_query"]
        top_k = state["top_k"]
        iteration = state["iteration"]

        results = retriever.query(
            query_text=query,
            top_k=top_k,
            expand_graph=True,
        )

        step = AgentStep(
            state=AgentState.SEARCH,
            query=query,
            reasoning=f"Found {len(results)} results",
            results=results,
            iteration=iteration,
        )

        # Accumulate all results
        all_results = state.get("all_results", []) + results

        return {
            "results": results,
            "all_results": all_results,
            "reasoning_trace": [step],
        }

    return search_node


def create_rerank_node(reranker: Any):
    """Create the rerank node function."""

    def rerank_node(state: GraphState) -> dict:
        """Re-rank results by relevance."""
        if not reranker:
            return {}

        results = state["results"]
        question = state["question"]

        try:
            ranked = reranker.rerank(question, results)
            return {"results": [r.result for r in ranked]}
        except Exception:
            return {}

    return rerank_node


def create_evaluate_node(llm: Any):
    """Create the evaluate node function."""

    def _format_results(results: List[HybridResult]) -> str:
        """Format results for prompts."""
        lines = []
        for i, r in enumerate(results):
            doc_id = r.metadata.get("doc_id", "Unknown")
            section = r.metadata.get("section", "")
            lines.append(f"[{i}] {doc_id}: {section}\n{r.text[:500]}\n")
        return "\n---\n".join(lines)

    def evaluate_node(state: GraphState) -> dict:
        """Evaluate if results answer the question."""
        question = state["question"]
        results = state["results"]
        iteration = state["iteration"]

        if not llm or not LANGCHAIN_AVAILABLE or not results:
            # Without LLM or results, use heuristic
            found = len(results) > 0
            step = AgentStep(
                state=AgentState.EVALUATE,
                query=state["current_query"],
                reasoning="LLM unavailable or no results, using heuristic",
                results=results,
                iteration=iteration,
            )
            return {
                "eval_result": {
                    "found_answer": found,
                    "reasoning": "Heuristic evaluation",
                },
                "found_answer": found,
                "reasoning_trace": [step],
            }

        try:
            results_text = _format_results(results)
            prompt = ChatPromptTemplate.from_template(EVALUATE_PROMPT_TEMPLATE)
            chain = prompt | llm
            response = chain.invoke({"query": question, "results": results_text})

            # Parse JSON response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            eval_result = json.loads(content.strip())
            found = eval_result.get("found_answer", False)

            step = AgentStep(
                state=AgentState.EVALUATE,
                query=state["current_query"],
                reasoning=eval_result.get("reasoning", "Evaluated results"),
                results=results,
                iteration=iteration,
            )

            return {
                "eval_result": eval_result,
                "found_answer": found,
                "reasoning_trace": [step],
            }

        except Exception as e:
            found = len(results) > 0
            step = AgentStep(
                state=AgentState.EVALUATE,
                query=state["current_query"],
                reasoning=f"Evaluation failed: {e}",
                results=results,
                iteration=iteration,
            )
            return {
                "eval_result": {"found_answer": found, "reasoning": f"Error: {e}"},
                "found_answer": found,
                "reasoning_trace": [step],
            }

    return evaluate_node


def create_refine_node(llm: Any):
    """Create the refine node function."""

    def refine_node(state: GraphState) -> dict:
        """Generate a refined search query."""
        question = state["question"]
        current_query = state["current_query"]
        results = state["results"]
        iteration = state["iteration"]
        eval_result = state.get("eval_result", {})

        # Check if evaluation suggested a refined query
        if eval_result.get("refined_query"):
            refined = eval_result["refined_query"]
        elif llm and LANGCHAIN_AVAILABLE:
            try:
                result_summary = (
                    ", ".join(r.metadata.get("doc_id", "unknown") for r in results[:3])
                    if results
                    else "no results"
                )

                prompt = ChatPromptTemplate.from_template(REFINE_PROMPT_TEMPLATE)
                chain = prompt | llm
                response = chain.invoke(
                    {
                        "original_query": current_query,
                        "result_summary": result_summary,
                        "user_question": question,
                    }
                )
                refined = response.content.strip()
            except Exception:
                refined = question
        else:
            refined = question

        step = AgentStep(
            state=AgentState.REFINE,
            query=refined,
            reasoning=f"Refining search: {eval_result.get('reasoning', 'no answer found')}",
            iteration=iteration,
        )

        return {
            "current_query": refined,
            "iteration": iteration + 1,
            "reasoning_trace": [step],
        }

    return refine_node


def create_answer_node(llm: Any):
    """Create the answer node function."""

    def _format_results(results: List[HybridResult]) -> str:
        """Format results for prompts."""
        lines = []
        for i, r in enumerate(results):
            doc_id = r.metadata.get("doc_id", "Unknown")
            section = r.metadata.get("section", "")
            lines.append(f"[{i}] {doc_id}: {section}\n{r.text[:500]}\n")
        return "\n---\n".join(lines)

    def answer_node(state: GraphState) -> dict:
        """Synthesize the final answer."""
        question = state["question"]
        results = state["results"]
        iteration = state["iteration"]
        eval_result = state.get("eval_result", {})

        # Check if evaluation already provided an answer
        if eval_result.get("answer"):
            answer = eval_result["answer"]
        elif llm and LANGCHAIN_AVAILABLE and results:
            try:
                context = _format_results(results)
                prompt = ChatPromptTemplate.from_template(SYNTHESIZE_PROMPT_TEMPLATE)
                chain = prompt | llm
                response = chain.invoke({"query": question, "context": context})
                answer = response.content.strip()
            except Exception as e:
                answer = f"Error synthesizing answer: {e}"
        elif results:
            answer = f"[Without LLM synthesis]\n\n{_format_results(results)}"
        else:
            answer = "I could not find relevant information to answer your question."

        step = AgentStep(
            state=AgentState.ANSWER,
            query=question,
            reasoning="Found satisfactory answer"
            if state.get("found_answer")
            else "Best-effort answer",
            results=results,
            iteration=iteration,
        )

        return {
            "answer": answer,
            "reasoning_trace": [step],
        }

    return answer_node


def create_failed_node():
    """Create the failed node function."""

    def failed_node(state: GraphState) -> dict:
        """Handle max iterations reached."""
        question = state["question"]
        iteration = state["iteration"]
        all_results = state.get("all_results", [])

        step = AgentStep(
            state=AgentState.FAILED,
            query=question,
            reasoning=f"Could not find answer after {iteration} iterations",
            iteration=iteration,
        )

        return {
            "results": all_results[:5] if all_results else [],
            "reasoning_trace": [step],
        }

    return failed_node


# =============================================================================
# Routing Functions
# =============================================================================


def should_continue(
    state: GraphState, max_iterations: int
) -> Literal["answer", "refine", "failed"]:
    """Determine next step after evaluation."""
    if state.get("found_answer"):
        return "answer"
    if state["iteration"] >= max_iterations:
        return "failed"
    return "refine"


# =============================================================================
# RAGAgent Class (LangGraph-based)
# =============================================================================


@dataclass
class RAGAgent:
    """
    Agentic RAG with LangGraph orchestration (L3.0).

    The agent loop (implemented as LangGraph StateGraph):
    1. REWRITE: Optimize the user's query
    2. SEARCH: Query the knowledge base
    3. RERANK: Re-rank results by relevance
    4. EVALUATE: Check if results answer the question
    5. REFINE: If not, generate a better query and retry
    6. ANSWER: Synthesize final response

    Memory persistence (ADR-0185):
    - Uses Graphiti for session memory across queries
    - Captures episodes for learning and context
    - Retrieves relevant memory before each query

    Attributes:
        retriever: HybridRetriever for search.
        rewriter: Optional QueryRewriter (creates if None).
        reranker: Optional ResultReranker (creates if None).
        provider: LLM provider for agent reasoning.
        model: Model name.
        max_iterations: Maximum search iterations (default: 3).
        enable_memory: Enable Graphiti memory persistence (default: True).
    """

    retriever: HybridRetriever = field(default_factory=HybridRetriever)
    rewriter: Any = None
    reranker: Any = None
    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini"))
    model: Optional[str] = None
    max_iterations: int = MAX_ITERATIONS
    enable_memory: bool = True
    _llm: Any = field(default=None, init=False, repr=False)
    _graph: Any = field(default=None, init=False, repr=False)
    _checkpointer: Any = field(default=None, init=False, repr=False)
    _memory: Any = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Initialize components."""
        self._llm = _create_llm(
            provider=self.provider,
            model=self.model,
            temperature=0.2,
        )

        # Initialize rewriter if not provided
        if self.rewriter is None:
            try:
                from scripts.rag.query_rewriter import QueryRewriter

                self.rewriter = QueryRewriter(provider=self.provider, model=self.model)
            except ImportError:
                pass

        # Initialize reranker if not provided
        if self.reranker is None:
            try:
                from scripts.rag.result_reranker import ResultReranker

                self.reranker = ResultReranker(
                    provider=self.provider, model=self.model, relevance_threshold=0.4
                )
            except ImportError:
                pass

        # Initialize Graphiti memory (ADR-0185)
        if self.enable_memory:
            try:
                from scripts.rag.graphiti_client import SyncGraphitiMemory

                self._memory = SyncGraphitiMemory()
                if self._memory.is_available:
                    self._memory.initialize()
            except ImportError:
                self._memory = None

        # Build LangGraph
        self._build_graph()

    def _build_graph(self):
        """Build the LangGraph StateGraph."""
        if not LANGGRAPH_AVAILABLE:
            return

        # Create the graph
        graph = StateGraph(GraphState)

        # Add nodes
        graph.add_node("rewrite", create_rewrite_node(self.rewriter, self._llm))
        graph.add_node("search", create_search_node(self.retriever))
        graph.add_node("rerank", create_rerank_node(self.reranker))
        graph.add_node("evaluate", create_evaluate_node(self._llm))
        graph.add_node("refine", create_refine_node(self._llm))
        graph.add_node("answer", create_answer_node(self._llm))
        graph.add_node("failed", create_failed_node())

        # Set entry point
        graph.set_entry_point("rewrite")

        # Add edges
        graph.add_edge("rewrite", "search")
        graph.add_edge("search", "rerank")
        graph.add_edge("rerank", "evaluate")

        # Conditional edge from evaluate
        max_iter = self.max_iterations
        graph.add_conditional_edges(
            "evaluate",
            lambda state: should_continue(state, max_iter),
            {
                "answer": "answer",
                "refine": "refine",
                "failed": "failed",
            },
        )

        # Refine loops back to rewrite
        graph.add_edge("refine", "rewrite")

        # Terminal nodes
        graph.add_edge("answer", END)
        graph.add_edge(
            "failed", "answer"
        )  # Failed still tries to give best-effort answer

        # Compile graph. Graphiti handles cross-query memory (ADR-0185);
        # MemorySaver is not needed and causes serialization issues with
        # complex state objects (AgentStep, HybridResult).
        self._checkpointer = None
        self._graph = graph.compile()

    def query(self, question: str, top_k: int = 10) -> AgentResult:
        """
        Execute an agentic query with iterative refinement.

        Args:
            question: User's natural language question.
            top_k: Number of results per search iteration.

        Returns:
            AgentResult with answer, evidence, and reasoning trace.
        """
        # Retrieve memory context (ADR-0185)
        memory_context = self._get_memory_context(question)

        if not LANGGRAPH_AVAILABLE or not self._graph:
            # Fallback to simple implementation without LangGraph
            result = self._query_fallback(question, top_k)
        else:
            # Initial state
            initial_state: GraphState = {
                "question": question,
                "top_k": top_k,
                "current_query": question,
                "iteration": 1,
                "results": [],
                "all_results": [],
                "eval_result": {},
                "found_answer": False,
                "answer": "",
                "reasoning_trace": [],
            }

            # Run the graph
            config = {
                "configurable": {"thread_id": f"query-{datetime.now().timestamp()}"}
            }
            final_state = self._graph.invoke(initial_state, config)

            # Build result
            result = AgentResult(
                answer=final_state.get("answer", "No answer generated"),
                evidence=final_state.get("results", []),
                reasoning_trace=final_state.get("reasoning_trace", []),
                iterations=final_state.get("iteration", 1),
                success=final_state.get("found_answer", False),
                model=self.model or self.provider,
            )

        # Capture episode to memory (ADR-0185)
        self._capture_episode(question, result)

        return result

    def _get_memory_context(self, question: str) -> List[str]:
        """Retrieve relevant context from agent memory."""
        if not self._memory:
            return []

        try:
            results = self._memory.search(question, num_results=3)
            return [r.content for r in results]
        except Exception:
            return []

    def _capture_episode(self, question: str, result: AgentResult) -> None:
        """Capture query episode to agent memory."""
        if not self._memory:
            return

        try:
            # Build episode content
            evidence_docs = [
                e.metadata.get("doc_id", "unknown") for e in result.evidence[:5]
            ]
            episode_content = f"""User question: {question}

Agent answer: {result.answer[:500]}

Evidence documents: {', '.join(evidence_docs)}

Success: {result.success}
Iterations: {result.iterations}
"""
            self._memory.add_episode(
                content=episode_content,
                source="rag-agent-query",
            )
        except Exception:
            pass  # Don't fail query if memory capture fails

    def _query_fallback(self, question: str, top_k: int = 10) -> AgentResult:
        """Fallback implementation when LangGraph is not available."""
        trace: List[AgentStep] = []
        current_query = question
        iteration = 0
        all_results: List[HybridResult] = []

        while iteration < self.max_iterations:
            iteration += 1

            # Step 1: Rewrite query
            if self.rewriter and self.rewriter.is_available():
                rewritten = self.rewriter.rewrite(current_query)
                trace.append(
                    AgentStep(
                        state=AgentState.REWRITE,
                        query=rewritten,
                        reasoning=f"Rewrote '{current_query}' to optimize search",
                        iteration=iteration,
                    )
                )
                search_query = rewritten
            else:
                search_query = current_query

            # Step 2: Search
            results = self.retriever.query(
                query_text=search_query,
                top_k=top_k,
                expand_graph=True,
            )
            trace.append(
                AgentStep(
                    state=AgentState.SEARCH,
                    query=search_query,
                    reasoning=f"Found {len(results)} results",
                    results=results,
                    iteration=iteration,
                )
            )

            if not results:
                trace.append(
                    AgentStep(
                        state=AgentState.EVALUATE,
                        query=search_query,
                        reasoning="No results found, will refine query",
                        iteration=iteration,
                    )
                )
                current_query = question
                continue

            # Step 3: Re-rank results
            if self.reranker:
                try:
                    ranked = self.reranker.rerank(question, results)
                    results = [r.result for r in ranked]
                except Exception:
                    pass

            all_results.extend(results)

            # Step 4: Evaluate (simplified without LLM)
            found_answer = len(results) > 0
            trace.append(
                AgentStep(
                    state=AgentState.EVALUATE,
                    query=search_query,
                    reasoning="Evaluated results (fallback mode)",
                    results=results,
                    iteration=iteration,
                )
            )

            if found_answer:
                # Step 5: Simple answer
                answer = self._format_fallback_answer(results)
                trace.append(
                    AgentStep(
                        state=AgentState.ANSWER,
                        query=question,
                        reasoning="Found results (fallback mode)",
                        results=results,
                        iteration=iteration,
                    )
                )

                return AgentResult(
                    answer=answer,
                    evidence=results,
                    reasoning_trace=trace,
                    iterations=iteration,
                    success=True,
                    model=self.model or self.provider,
                )

        # Max iterations reached
        trace.append(
            AgentStep(
                state=AgentState.FAILED,
                query=question,
                reasoning=f"Could not find answer after {iteration} iterations",
                iteration=iteration,
            )
        )

        if all_results:
            answer = self._format_fallback_answer(all_results[:5])
        else:
            answer = "I could not find relevant information to answer your question."

        return AgentResult(
            answer=answer,
            evidence=all_results[:5] if all_results else [],
            reasoning_trace=trace,
            iterations=iteration,
            success=False,
            model=self.model or self.provider,
        )

    def _format_fallback_answer(self, results: List[HybridResult]) -> str:
        """Format results as answer in fallback mode."""
        lines = ["[Fallback mode - LangGraph not available]\n"]
        for r in results[:5]:
            doc_id = r.metadata.get("doc_id", "Unknown")
            section = r.metadata.get("section", "")
            lines.append(f"**{doc_id}**: {section}")
            lines.append(f"{r.text[:300]}...\n")
        return "\n".join(lines)

    def close(self):
        """Close resources."""
        if hasattr(self.retriever, "close"):
            self.retriever.close()
        if self._memory:
            try:
                self._memory.close()
            except Exception:
                pass


def run_agent_query(
    question: str,
    provider: Optional[str] = None,
    max_iterations: int = MAX_ITERATIONS,
) -> AgentResult:
    """
    Convenience function to run an agentic query.

    Args:
        question: User's natural language question.
        provider: LLM provider (default: from env).
        max_iterations: Maximum search iterations.

    Returns:
        AgentResult with answer and reasoning trace.
    """
    agent = RAGAgent(
        provider=provider or os.getenv("LLM_PROVIDER", "gemini"),
        max_iterations=max_iterations,
    )
    try:
        return agent.query(question)
    finally:
        agent.close()


if __name__ == "__main__":
    import sys

    question = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "What are the RAG maturity levels?"
    )

    print(f"Agentic RAG Query (L3.0 - LangGraph)\n{'=' * 50}")
    print(f"LangGraph available: {LANGGRAPH_AVAILABLE}")
    print(f"Question: {question}\n")

    result = run_agent_query(question)

    print(f"Answer: {result.answer}\n")
    print(f"Success: {result.success}")
    print(f"Iterations: {result.iterations}")
    print("\nReasoning Trace:")
    for step in result.reasoning_trace:
        print(f"  [{step.iteration}] {step.state.value}: {step.reasoning}")
