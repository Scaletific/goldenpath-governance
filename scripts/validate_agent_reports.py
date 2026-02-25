#!/usr/bin/env python3
"""
---
id: validate_agent_reports
type: script
owner: platform-team
status: active
maturity: 3
test:
  runner: pytest
  command: "pytest -q tests/scripts/test_validate_agent_reports.py"
  evidence: ci
dry_run:
  supported: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
relates_to:
  - ADR-0192
  - ADR-0193
---
Purpose: Validates agent report format (metadata fields + required sections).

Pre-commit hook that ensures agent reports have parseable metadata with
required fields (Agent, Mission, Started, Completed, Status) and required
sections (Changes, Issues, Decisions). Supports both ## Metadata bullet
format and YAML frontmatter format.
"""

import re
import sys
from pathlib import Path

_REQUIRED_METADATA_FIELDS = ["Agent", "Mission", "Started", "Completed", "Status"]

# Section names: accept both long ("Changes Made") and short ("Changes")
_REQUIRED_SECTIONS = [
    ("Changes Made", "Changes"),
    ("Issues Found", "Issues"),
    ("Decisions Made", "Decisions"),
]

_METADATA_LINE_RE = re.compile(r"^-\s+(\w[\w\s]*):\s*(.+)$", re.MULTILINE)
_YAML_FM_LINE_RE = re.compile(r"^(\w[\w\s]*):\s*(.+)$", re.MULTILINE)
_H2_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def _parse_metadata(content: str) -> dict[str, str] | None:
    """Extract metadata key-value pairs from agent report content.

    Returns dict of parsed metadata, or None if no metadata block found.
    """
    # Try ## Metadata section first
    meta_match = re.search(r"##\s+Metadata\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if meta_match:
        block = meta_match.group(1)
        result = {}
        for m in _METADATA_LINE_RE.finditer(block):
            result[m.group(1).strip()] = m.group(2).strip().strip('"').strip("'")
        return result

    # Fallback: YAML frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        block = fm_match.group(1)
        result = {}
        for m in _YAML_FM_LINE_RE.finditer(block):
            result[m.group(1).strip()] = m.group(2).strip().strip('"').strip("'")
        return result

    return None


def _find_sections(content: str) -> set[str]:
    """Extract all H2 section names from content."""
    return {m.group(1).strip() for m in _H2_RE.finditer(content)}


def validate_report(filepath: Path) -> list[str]:
    """Validate a single agent report file.

    Returns a list of error messages (empty if valid).
    """
    content = filepath.read_text(encoding="utf-8")
    errors: list[str] = []

    # Check metadata
    meta = _parse_metadata(content)
    if meta is None:
        errors.append(
            f"{filepath.name}: No metadata found (need ## Metadata section "
            "or YAML frontmatter)"
        )
        return errors

    for field in _REQUIRED_METADATA_FIELDS:
        if field not in meta:
            errors.append(f"{filepath.name}: Missing required field: {field}")

    # Check required sections
    sections = _find_sections(content)
    for long_name, short_name in _REQUIRED_SECTIONS:
        if long_name not in sections and short_name not in sections:
            errors.append(
                f"{filepath.name}: Missing required section: "
                f"## {long_name} (or ## {short_name})"
            )

    return errors


def validate_all_reports(repo_root: Path) -> tuple[int, dict[str, list[str]]]:
    """Validate all agent reports in the repository.

    Returns (exit_code, errors_by_file).
    """
    all_errors: dict[str, list[str]] = {}

    for reports_dir in [
        repo_root / "agent-reports",
        repo_root / ".claude" / "agent-reports",
    ]:
        if not reports_dir.exists():
            continue
        for filepath in sorted(reports_dir.glob("*.md")):
            if filepath.name == "README.md":
                continue
            errors = validate_report(filepath)
            if errors:
                all_errors[str(filepath)] = errors

    exit_code = 1 if all_errors else 0
    return exit_code, all_errors


def main() -> int:
    """CLI entrypoint for pre-commit hook.

    When file arguments are provided (pre-commit pass_filenames: true),
    only those files are validated. Otherwise validates all reports.
    """
    filenames = sys.argv[1:]
    all_errors: dict[str, list[str]] = {}

    if filenames:
        # Pre-commit mode: validate only staged files
        for fname in filenames:
            filepath = Path(fname)
            if filepath.name == "README.md":
                continue
            if not filepath.exists():
                continue
            errors = validate_report(filepath)
            if errors:
                all_errors[str(filepath)] = errors
    else:
        # Full scan mode (--all)
        _, all_errors = validate_all_reports(Path.cwd())

    if all_errors:
        print("Agent report validation errors:")
        for filepath, errors in all_errors.items():
            for error in errors:
                print(f"  {error}")
        print()
        print(
            "Fix: Use ## Metadata section with required fields "
            "(Agent, Mission, Started, Completed, Status)"
        )
        print(
            "     and required sections "
            "(## Changes Made, ## Issues Found, ## Decisions Made)"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
