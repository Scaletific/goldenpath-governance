#!/usr/bin/env python3
"""
---
id: SCRIPT-0039
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0039.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Enhanced Enum Consistency Validator
Achievement: Implements recursive dot-path validation across MD and YAML artifacts.
             Supports both whole-repo scanning and targeted file validation (CI-friendly).
Value: Deeper enforcement of nested metadata (Risk, Reliability) against enums.
"""
import os
import sys
import yaml
import argparse
from typing import Any, Dict, List, Tuple


def load_yaml(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML {path}: {e}")
        return None


def get_dot(d: Dict[str, Any], path: str) -> Any:
    """Traverses a dictionary using dot notation (e.g., 'risk_profile.security_risk')."""
    if not isinstance(d, dict):
        return None
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def find_frontmatter(md_text: str) -> Dict[str, Any] | None:
    """Parses YAML frontmatter from markdown."""
    lines = md_text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return None
    for i in range(1, min(len(lines), 2000)):
        if lines[i].strip() == "---":
            fm_text = "\n".join(lines[1:i])
            try:
                return yaml.safe_load(fm_text) or {}
            except Exception:
                return {"__parse_error__": True}
    return None


def validate_value(
    file_path: str, field_path: str, value: Any, allowed: List[str], errors: List[str]
) -> None:
    if value is None:
        return
    if not allowed:
        return

    if isinstance(value, list):
        for idx, item in enumerate(value):
            if item not in allowed:
                errors.append(
                    f"{file_path}: {field_path}[{idx}]='{item}' not in enum {allowed}"
                )
    else:
        if value not in allowed:
            errors.append(f"{file_path}: {field_path}='{value}' not in enum {allowed}")


def scan_file(
    filepath: str,
    enums: Dict[str, Any],
    checks: List[Tuple[str, str, List[str]]],
    errors: List[str],
):
    kind_ext = "yaml" if filepath.endswith((".yml", ".yaml")) else "mdfm"

    try:
        if kind_ext == "yaml":
            with open(filepath, "r", encoding="utf-8") as f:
                docs = yaml.safe_load_all(f)
                for doc in docs:
                    if not isinstance(doc, dict):
                        continue
                    for kind, field_path, allowed in checks:
                        if kind == "yaml":
                            val = get_dot(doc, field_path)
                            validate_value(filepath, field_path, val, allowed, errors)
        else:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            fm = find_frontmatter(content)
            if not fm:
                return
            if fm.get("__parse_error__"):
                errors.append(f"{filepath}: invalid YAML frontmatter")
                return
            for kind, field_path, allowed in checks:
                if kind == "mdfm":
                    val = get_dot(fm, field_path)
                    validate_value(filepath, field_path, val, allowed, errors)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--enums", default="schemas/metadata/enums.yaml")
    ap.add_argument(
        "--roots",
        nargs="+",
        default=["docs", "gitops", "envs", "idp-tooling"],
        help="Roots to scan.",
    )
    ap.add_argument("files", nargs="*", help="Specific files to scan (overrides roots)")
    ap.add_argument(
        "--soft",
        action="store_true",
        help="Report errors but don't fail CI (non-zero exit code 0).",
    )
    args = ap.parse_args()

    enums = load_yaml(args.enums)
    if not isinstance(enums, dict):
        print(f"❌ Invalid enums file: {args.enums}", file=sys.stderr)
        return 2

    # Map enums from enums.yaml
    domain_list = enums.get("domains", [])
    owner_list = enums.get("owners", [])
    type_list = enums.get("artifact_type", [])
    cat_list = enums.get("adr_categories", [])
    status_list = enums.get("lifecycle", [])
    tier_list = enums.get("observability_tier", [])
    impact_list = enums.get("risk_profile_production_impact", [])
    sec_risk_list = enums.get("risk_profile_security_risk", [])
    rollback_list = enums.get("rollback_strategy", [])
    coupling_list = enums.get("risk_profile_coupling_risk", [])

    # (file_kind, field_path, allowed_list)
    checks = [
        ("mdfm", "domain", domain_list),
        ("mdfm", "owner", owner_list),
        (
            "mdfm",
            "kind",
            type_list,
        ),  # We use 'kind' in schema, user calls it 'artifact_type'
        ("mdfm", "type", type_list),
        ("mdfm", "category", cat_list),
        ("mdfm", "status", status_list),
        ("mdfm", "reliability.observability_tier", tier_list),
        ("mdfm", "reliability.rollback_strategy", rollback_list),
        ("mdfm", "risk_profile.production_impact", impact_list),
        ("mdfm", "risk_profile.security_risk", sec_risk_list),
        ("mdfm", "risk_profile.coupling_risk", coupling_list),
        ("yaml", "owner", owner_list),
        ("yaml", "domain", domain_list),
        ("yaml", "reliability.observability_tier", tier_list),
        ("yaml", "reliability.rollback_strategy", rollback_list),
        ("yaml", "risk_profile.production_impact", impact_list),
        ("yaml", "risk_profile.security_risk", sec_risk_list),
        ("yaml", "risk_profile.coupling_risk", coupling_list),
    ]

    errors: List[str] = []

    if args.files:
        for f in args.files:
            if os.path.isfile(f) and f.endswith((".md", ".yaml", ".yml")):
                # skip the enums file itself
                if os.path.abspath(f) == os.path.abspath(args.enums):
                    continue
                scan_file(f, enums, checks, errors)
    else:
        for root in args.roots:
            if not os.path.exists(root):
                continue
            for base, _, files in os.walk(root):
                if "node_modules" in base or ".git" in base:
                    continue
                for name in files:
                    if name.endswith((".md", ".yaml", ".yml")):
                        path = os.path.join(base, name)
                        if os.path.abspath(path) == os.path.abspath(args.enums):
                            continue
                        scan_file(path, enums, checks, errors)

    if errors:
        indicator = "⚠️ WARNING" if args.soft else "❌ Enum validation failed"
        print(f"{indicator}:", file=sys.stderr)
        for e in errors[:50]:
            print(f" - {e}", file=sys.stderr)
        if len(errors) > 50:
            print(f" ... and {len(errors)-50} more", file=sys.stderr)

        print("\n💡 ACTION REQUIRED:", file=sys.stderr)
        print(
            "To resolve this, you can propose a new value by opening a PR for 'schemas/metadata/enums.yaml'.",
            file=sys.stderr,
        )
        print(
            "See Runbook: docs/70-operations/runbooks/RB-0015-extending-governance-vocabulary.md",
            file=sys.stderr,
        )

        return 0 if args.soft else 1

    print("✅ Enum validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
