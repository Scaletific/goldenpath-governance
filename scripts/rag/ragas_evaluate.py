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
  command: "pytest -q tests/unit/test_ragas_evaluate.py"
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
Purpose: RAGAS evaluation script for RAG pipeline quality metrics.

Evaluates retrieval quality using RAGAS metrics:
- context_precision: Are retrieved contexts relevant?
- faithfulness: Is the answer grounded in context?
- answer_relevancy: Does the answer address the question?

Usage:
    python -m scripts.rag.ragas_evaluate
    python -m scripts.rag.ragas_evaluate --questions tests/ragas/questions.json --output reports/ragas_metrics.json
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.rag.retriever import GovernanceRetriever


def load_questions(path: Path) -> List[str]:
    """Load test questions from JSON file."""
    data = json.loads(path.read_text())
    return data.get("questions", [])


def retrieve_contexts(
    questions: List[str],
    retriever: GovernanceRetriever,
    top_k: int = 5,
) -> List[List[str]]:
    """Retrieve contexts for each question."""
    all_contexts = []
    for question in questions:
        results = retriever.query(question, top_k=top_k)
        contexts = [r.text for r in results]
        all_contexts.append(contexts)
    return all_contexts


def generate_answers_simple(
    questions: List[str],
    contexts: List[List[str]],
) -> List[str]:
    """
    Generate simple answers by concatenating top contexts.

    This is a placeholder - for production, use an LLM to synthesize answers.
    """
    answers = []
    for question, ctx_list in zip(questions, contexts):
        if ctx_list:
            # Use first context as answer (simple baseline)
            answer = ctx_list[0][:500] if ctx_list[0] else "No relevant context found."
        else:
            answer = "No relevant context found."
        answers.append(answer)
    return answers


def _create_llm_for_ragas(provider: str = "openai", model: Optional[str] = None):
    """
    Create an LLM wrapper for RAGAS evaluation.

    Args:
        provider: One of "openai", "ollama", "claude", "gemini".
        model: Model name. Defaults based on provider.

    Returns:
        LangChain LLM instance or None.
    """
    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=model or os.getenv("OLLAMA_MODEL", "llama3.2"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.1,
            )
        except ImportError:
            return None
    elif provider == "claude":
        try:
            from langchain_anthropic import ChatAnthropic

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return None
            return ChatAnthropic(
                model=model or os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307"),
                temperature=0.1,
                api_key=api_key,
            )
        except ImportError:
            return None
    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            return ChatOpenAI(
                model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                temperature=0.1,
                api_key=api_key,
            )
        except ImportError:
            return None
    elif provider == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return None
            return ChatGoogleGenerativeAI(
                model=model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                temperature=0.1,
                google_api_key=api_key,
            )
        except ImportError:
            return None
    return None


def evaluate_with_ragas(
    questions: List[str],
    answers: List[str],
    contexts: List[List[str]],
    provider: str = "openai",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run RAGAS evaluation on the retrieval results.

    Args:
        questions: List of test questions.
        answers: Generated answers for each question.
        contexts: Retrieved contexts for each question.
        provider: LLM provider ("openai", "ollama", "claude").
        model: Model name (uses provider default if not specified).

    Returns:
        Dictionary with RAGAS metrics.
    """
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
        )
    except ImportError as e:
        return {
            "error": f"RAGAS import failed: {e}",
            "metrics": {},
        }

    # Create LLM for RAGAS
    llm = _create_llm_for_ragas(provider, model)
    if llm is None:
        return {
            "error": f"Could not create LLM for provider: {provider}",
            "metrics": {},
        }

    # Build RAGAS dataset
    data = {
        "user_input": questions,
        "response": answers,
        "retrieved_contexts": contexts,
    }
    dataset = Dataset.from_dict(data)

    # Select metrics
    metrics = [faithfulness, answer_relevancy]

    try:
        # Run evaluation with custom LLM
        result = evaluate(dataset, metrics=metrics, llm=llm)

        return {
            "provider": provider,
            "model": model or f"{provider}_default",
            "faithfulness": float(result["faithfulness"])
            if "faithfulness" in result
            else None,
            "answer_relevancy": float(result["answer_relevancy"])
            if "answer_relevancy" in result
            else None,
        }
    except Exception as e:
        return {
            "error": str(e),
            "metrics": {},
        }


def compute_retrieval_metrics(
    questions: List[str],
    contexts: List[List[str]],
) -> Dict[str, float]:
    """
    Compute basic retrieval metrics without LLM.

    - avg_contexts_per_query: Average number of contexts retrieved
    - queries_with_results: Percentage of queries that returned results
    """
    total_contexts = sum(len(c) for c in contexts)
    queries_with_results = sum(1 for c in contexts if c)

    return {
        "total_questions": len(questions),
        "avg_contexts_per_query": total_contexts / len(questions) if questions else 0,
        "queries_with_results": queries_with_results,
        "queries_with_results_pct": queries_with_results / len(questions) * 100
        if questions
        else 0,
    }


def run_evaluation(
    questions_path: Path = Path("tests/ragas/questions.json"),
    output_path: Path = Path("reports/ragas_metrics.json"),
    top_k: int = 5,
    skip_llm: bool = False,
    provider: str = "openai",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run full RAGAS evaluation pipeline.

    Args:
        questions_path: Path to questions JSON file.
        output_path: Path to write results.
        top_k: Number of contexts to retrieve per question.
        skip_llm: If True, skip LLM-based metrics (faster, cheaper).
        provider: LLM provider for RAGAS ("openai", "ollama", "claude").
        model: Model name (uses provider default if not specified).

    Returns:
        Evaluation results dictionary.
    """
    # Load questions
    questions = load_questions(questions_path)
    print(f"Loaded {len(questions)} questions")

    # Initialize retriever
    retriever = GovernanceRetriever()

    # Retrieve contexts
    print("Retrieving contexts...")
    contexts = retrieve_contexts(questions, retriever, top_k=top_k)

    # Generate answers
    print("Generating answers...")
    answers = generate_answers_simple(questions, contexts)

    # Compute basic metrics
    basic_metrics = compute_retrieval_metrics(questions, contexts)
    print(f"Basic metrics: {basic_metrics}")

    # Run RAGAS evaluation (if not skipped)
    ragas_metrics = {}
    if not skip_llm:
        print(f"Running RAGAS evaluation with {provider}...")
        ragas_metrics = evaluate_with_ragas(
            questions, answers, contexts, provider=provider, model=model
        )
        print(f"RAGAS metrics: {ragas_metrics}")
    else:
        print("Skipping LLM-based RAGAS metrics")

    # Build result
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "question_count": len(questions),
        "top_k": top_k,
        "provider": provider if not skip_llm else None,
        "model": model if not skip_llm else None,
        "basic_metrics": basic_metrics,
        "ragas_metrics": ragas_metrics,
        "status": "completed" if not ragas_metrics.get("error") else "partial",
    }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(f"Results written to {output_path}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run RAGAS evaluation")
    parser.add_argument(
        "--questions",
        type=Path,
        default=Path("tests/ragas/questions.json"),
        help="Path to questions JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/ragas_metrics.json"),
        help="Path to write results",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of contexts to retrieve per question",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM-based metrics (faster, cheaper)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "ollama", "claude", "gemini"],
        default=os.getenv("LLM_PROVIDER", "gemini"),
        help="LLM provider for RAGAS evaluation (default: from LLM_PROVIDER env or gemini)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name for evaluation (uses provider default if not specified)",
    )

    args = parser.parse_args()
    run_evaluation(
        questions_path=args.questions,
        output_path=args.output,
        top_k=args.top_k,
        skip_llm=args.skip_llm,
        provider=args.provider,
        model=args.model,
    )
