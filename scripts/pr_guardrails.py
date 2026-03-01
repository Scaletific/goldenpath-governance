#!/usr/bin/env python3
"""
---
id: SCRIPT-0026
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0026.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
PR Guardrails Validator

Purpose: Enforce PR checklist requirements with conditional label bypasses.
Relates-To: 85-how-it-works/governance/PR_GUARDRAILS.md
Value: Ensures consistent PR quality while allowing legitimate exceptions.

Labels:
- docs-only: Bypasses if ALL changed files are .md
- typo-fix: Bypasses if < 50 lines changed in text files
- hotfix: Bypasses if targeting main AND author is platform-team
- build_id: Bypasses if terraform changes AND author is platform-team

Usage:
  python scripts/pr_guardrails.py

Environment Variables:
  PR_BODY: The PR description body
  PR_LABELS: JSON array of label names
  PR_AUTHOR: GitHub username of PR author
  PR_BASE: Target branch (e.g., main, development)
  CHANGED_FILES: Newline-separated list of changed files
  ADDITIONS: Total lines added
  DELETIONS: Total lines deleted

Exit Codes:
  0: All checks passed (or valid bypass)
  1: Validation failed
"""

import os
import sys
import json
import re
from lib.metadata_config import MetadataConfig

# Configuration
cfg = MetadataConfig()
access = cfg.get_access_config()
PLATFORM_TEAM = access.get("platform_team", []) + access.get("service_accounts", [])
TEMPLATE_HEADER = "Select at least one checkbox per section by changing `[ ]` to `[x]`."

SECTIONS = [
    {
        "name": "Change Type",
        "labels": ["Feature", "Bug fix", "Infra change", "Governance / Policy"],
    },
    {
        "name": "Decision Impact",
        "labels": ["Requires ADR", "Updates existing ADR", "No architectural impact"],
    },
    {
        "name": "Production Readiness",
        "labels": ["Readiness checklist completed", "No production impact"],
    },
    {
        "name": "Testing / Validation",
        "labels": [
            "Plan/apply link provided (paste below)",
            "Test command or run ID provided (paste below)",
            "Not applicable",
        ],
    },
    {
        "name": "Code Audit (PROMPT-0013)",
        "labels": [
            "Post-implementation audit completed — all critical/high findings resolved",
            "Audit not applicable (docs-only, typo, or config change)",
        ],
    },
    {
        "name": "Risk & Rollback",
        "labels": [
            "Rollback plan documented (link or notes below)",
            "Data migration required",
            "No data migration",
            "Not applicable",
        ],
    },
]


def get_env(name: str, default: str = "") -> str:
    """Get environment variable with default."""
    return os.environ.get(name, default)


def get_labels() -> list:
    """Parse PR labels from environment."""
    labels_json = get_env("PR_LABELS", "[]")
    try:
        return json.loads(labels_json)
    except json.JSONDecodeError:
        return []


def get_changed_files() -> list:
    """Parse changed files from environment."""
    files = get_env("CHANGED_FILES", "")
    return [f.strip() for f in files.split("\n") if f.strip()]


def is_checked(body: str, label: str) -> bool:
    """Check if a checkbox label is checked in the PR body."""
    pattern = re.compile(rf"- \[[xX]\] {re.escape(label)}")
    return bool(pattern.search(body))


def validate_docs_only(files: list) -> tuple[bool, str]:
    """Validate docs-only label: all files must be .md"""
    if not files:
        return False, "No files changed"

    non_docs = [f for f in files if not f.endswith(".md")]
    if non_docs:
        return (
            False,
            f"docs-only label invalid: non-doc files changed: {', '.join(non_docs[:5])}",
        )

    return True, f"✅ docs-only validated: {len(files)} doc files"


def validate_typo_fix(files: list, additions: int, deletions: int) -> tuple[bool, str]:
    """Validate typo-fix label: < 50 lines, text files only"""
    total_changes = additions + deletions
    if total_changes >= 50:
        return False, f"typo-fix label invalid: {total_changes} lines changed (max 50)"

    binary_extensions = [
        ".png",
        ".jpg",
        ".gif",
        ".ico",
        ".woff",
        ".ttf",
        ".zip",
        ".tar",
        ".gz",
    ]
    binary_files = [
        f for f in files if any(f.endswith(ext) for ext in binary_extensions)
    ]
    if binary_files:
        return (
            False,
            f"typo-fix label invalid: binary files changed: {', '.join(binary_files[:3])}",
        )

    return True, f"✅ typo-fix validated: {total_changes} lines in text files"


def validate_hotfix(author: str, base: str) -> tuple[bool, str]:
    """Validate hotfix label: must target main AND be platform-team"""
    if base != "main":
        return False, f"hotfix label invalid: must target main, not {base}"

    if author not in PLATFORM_TEAM:
        return False, f"hotfix label invalid: author {author} not in platform-team"

    return True, f"✅ hotfix validated: {author} targeting {base}"


def validate_build_id(author: str, files: list) -> tuple[bool, str]:
    """Validate build_id label: must be platform-team AND have terraform changes"""
    if author not in PLATFORM_TEAM:
        return False, f"build_id label invalid: author {author} not in platform-team"

    terraform_patterns = [".tf", ".tfvars", "envs/", "modules/", "backend.tf"]
    has_terraform = any(
        any(pattern in f for pattern in terraform_patterns) for f in files
    )

    if not has_terraform:
        return False, "build_id label invalid: no terraform files changed"

    return True, f"✅ build_id validated: {author} with terraform changes"


def validate_vq_classification(body: str) -> tuple[bool, str]:
    """Ensure PR body has a valid VQ bucket classification (HV/HQ, etc)."""
    vq_pattern = re.compile(r"VQ Class: (HV/HQ|HV/LQ|MV/HQ|LV/LQ)", re.IGNORECASE)
    match = vq_pattern.search(body)

    if not match:
        return False, "Missing VQ Classification (e.g., 'VQ Class: HV/HQ')."

    return True, f"✅ VQ Classification found: {match.group(1).upper()}"


def validate_script_traceability(files: list) -> list[str]:
    """Ensure any changed scripts have ADR and CL traceability."""
    import subprocess

    errors = []
    scripts = [
        f
        for f in files
        if f.startswith("scripts/") and (f.endswith(".py") or f.endswith(".sh"))
    ]

    for script in scripts:
        script_name = os.path.basename(script)
        # Skip exempt scripts
        if script_name in ["check_script_traceability.py", "__init__.py"]:
            continue

        print(f"   🕵️ Checking traceability for {script_name}...")
        result = subprocess.run(
            [
                sys.executable,
                "scripts/check_script_traceability.py",
                "--script",
                script_name,
                "--validate",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(
                f"Script Traceability Failure for {script_name}. Ensure it is mentioned in an ADR and CL entry."
            )

    return errors


def validate_checklist(body: str, author: str, files: list) -> list[str]:
    """Validate PR body has required checkbox selections and VQ for agents."""
    errors = []

    if TEMPLATE_HEADER not in body:
        errors.append(
            "PR body must be based on `.github/pull_request_template.md` (missing template header)."
        )

    # Traceability Enforcement
    trace_errors = validate_script_traceability(files)
    errors.extend(trace_errors)

    # Mandatory VQ for Agents (and recommended for all)
    is_agent = any(
        agent_sig in author.lower()
        for agent_sig in ["antigravity", "agent", "bot", "service-account"]
    )
    vq_valid, vq_msg = validate_vq_classification(body)

    if is_agent and not vq_valid:
        errors.append(f"AI Agents MUST provide Value Quantification: {vq_msg}")
    elif vq_valid:
        print(f"   {vq_msg}")

    missing_sections = []
    for section in SECTIONS:
        if not any(is_checked(body, label) for label in section["labels"]):
            missing_sections.append(section["name"])

    if missing_sections:
        errors.append(
            f"Missing required PR checklist selections: {', '.join(missing_sections)}."
        )

    return errors


def main():
    """Main entry point."""
    # Load environment
    body = get_env("PR_BODY", "")
    labels = get_labels()
    author = get_env("PR_AUTHOR", "")
    base = get_env("PR_BASE", "")
    files = get_changed_files()
    additions = int(get_env("ADDITIONS", "0"))
    deletions = int(get_env("DELETIONS", "0"))

    print("🔍 PR Guardrails Validator")
    print(f"   Author: {author}")
    print(f"   Base: {base}")
    print(f"   Labels: {labels}")
    print(f"   Files changed: {len(files)}")
    print(f"   Lines: +{additions} -{deletions}")
    print()

    # Check conditional bypasses
    if "docs-only" in labels:
        valid, msg = validate_docs_only(files)
        if valid:
            print(msg)
            sys.exit(0)
        else:
            print(f"❌ {msg}")
            sys.exit(1)

    if "typo-fix" in labels:
        valid, msg = validate_typo_fix(files, additions, deletions)
        if valid:
            print(msg)
            sys.exit(0)
        else:
            print(f"❌ {msg}")
            sys.exit(1)

    if "hotfix" in labels:
        valid, msg = validate_hotfix(author, base)
        if valid:
            print(msg)
            sys.exit(0)
        else:
            print(f"❌ {msg}")
            sys.exit(1)

    if "build_id" in labels:
        valid, msg = validate_build_id(author, files)
        if valid:
            print(msg)
            sys.exit(0)
        else:
            print(f"❌ {msg}")
            sys.exit(1)

    # No bypass label - validate checklist
    print("📋 Validating PR checklist...")
    errors = validate_checklist(body, author, files)

    if errors:
        print()
        for error in errors:
            print(f"❌ {error}")
        sys.exit(1)
    else:
        print("✅ All checklist sections completed")
        sys.exit(0)


if __name__ == "__main__":
    main()
