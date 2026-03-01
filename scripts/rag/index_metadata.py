#!/usr/bin/env python3
"""
---
id: SCRIPT-0077
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_index_metadata.py"
  evidence: declared
dry_run:
  supported: true
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0017-tdd-and-determinism
---
Purpose: Index metadata artifact writer.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import json
import subprocess


@dataclass
class IndexMetadata:
    source_sha: str
    generated_at: str
    document_count: int


def _get_source_sha() -> str:
    """Resolve the current git SHA, or return 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def build_index_metadata(
    document_count: int, source_sha: Optional[str] = None
) -> IndexMetadata:
    """Create index metadata with current timestamp."""
    sha = source_sha or _get_source_sha()
    generated_at = datetime.now(timezone.utc).isoformat()
    return IndexMetadata(
        source_sha=sha, generated_at=generated_at, document_count=document_count
    )


def write_index_metadata(path: Path, metadata: IndexMetadata) -> None:
    """Write index metadata JSON artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "source_sha": metadata.source_sha,
        "generated_at": metadata.generated_at,
        "document_count": metadata.document_count,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def read_index_metadata(path: Path) -> Optional[IndexMetadata]:
    """Read index metadata JSON artifact, returning None on missing/invalid."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None
    try:
        return IndexMetadata(
            source_sha=str(data.get("source_sha", "unknown")),
            generated_at=str(data.get("generated_at", "")),
            document_count=int(data.get("document_count", 0)),
        )
    except Exception:
        return None
