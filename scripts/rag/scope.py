#!/usr/bin/env python3
"""
---
id: SCRIPT-0076
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_scope.py"
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
Purpose: Scope filtering for governance-registry indexing.

Enforces PRD-0008 allowlist and denylist rules for indexed paths.
"""

from pathlib import Path
from typing import Iterable, List, Union


# Allowlist paths (relative to repo root)
ALLOWLIST_PREFIXES = {
    Path("docs"),
    Path("session_capture"),
    Path("docs/changelog/entries"),
    Path("bootstrap"),
    Path("catalog"),
    Path("gitops"),
    Path("idp-tooling"),
    Path("tests"),
}

ALLOWLIST_FILES = {
    Path("PLATFORM_HEALTH.md"),
    Path("PLATFORM_DASHBOARDS.md"),
    Path("scripts/index.md"),
}

# Denylist patterns
DENYLIST_PARTS = {
    ".terraform",
    "node_modules",
    "logs",
}


def _parts_match(path_parts: tuple[str, ...], prefix_parts: tuple[str, ...]) -> bool:
    """
    Check whether prefix_parts appears as a contiguous slice in path_parts.
    """
    if not prefix_parts or len(prefix_parts) > len(path_parts):
        return False
    for i in range(0, len(path_parts) - len(prefix_parts) + 1):
        if path_parts[i : i + len(prefix_parts)] == prefix_parts:
            return True
    return False


def is_allowed_path(path: Union[str, Path]) -> bool:
    """
    Check whether a path is allowed for indexing.

    Args:
        path: Path to evaluate (repo-relative or absolute).

    Returns:
        True if path is allowed by allowlist and not denied.
    """
    path = Path(path)
    # Denylist by path parts (works for absolute + relative)
    for part in path.parts:
        if part in DENYLIST_PARTS:
            return False

    # Allowlist files (match by suffix parts)
    for allowed_file in ALLOWLIST_FILES:
        if tuple(path.parts[-len(allowed_file.parts) :]) == allowed_file.parts:
            return True

    # Allowlist prefixes (match contiguous parts anywhere in absolute path)
    for prefix in ALLOWLIST_PREFIXES:
        if _parts_match(path.parts, prefix.parts):
            return True

    return False


def filter_paths(paths: Iterable[Union[str, Path]]) -> List[Path]:
    """
    Filter an iterable of paths to allowed paths only.

    Args:
        paths: Iterable of paths to filter.

    Returns:
        List of allowed Path objects.
    """
    allowed = []
    for p in paths:
        path = Path(p)
        if is_allowed_path(path):
            allowed.append(path)
    return allowed
