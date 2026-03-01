#!/usr/bin/env python3
"""
---
id: SCRIPT-0079
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_ragas_baseline.py"
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
Purpose: RAGAS baseline harness.

Creates a baseline metrics artifact for Phase 0.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
import json


def load_questions(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def write_baseline(path: Path, question_count: int) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "question_count": question_count,
        "metrics": {
            "context_precision": None,
            "faithfulness": None,
        },
        "status": "pending_ragas_run",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def build_baseline(
    questions_path: Path = Path("tests/ragas/questions.json"),
    output_path: Path = Path("reports/ragas_baseline.json"),
) -> None:
    questions = load_questions(questions_path)
    question_count = len(questions.get("questions", []))
    write_baseline(output_path, question_count)


if __name__ == "__main__":
    build_baseline()
