#!/usr/bin/env python3
"""
---
id: SCRIPT-0042
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0042.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Decision Routing Compliance Validator
Achievement: Enforces mandatory artifacts (ADRs, Changelogs) based on
             impacted domains and components defined in agent-routing.yaml.
Value: Automates architectural rigor for "Born Governed" platform shifts.
"""
import os
import sys
import yaml
import argparse
from typing import Any, Dict, Set


def load_yaml(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML {path}: {e}")
        return None


def find_frontmatter(md_text: str) -> Dict[str, Any] | None:
    lines = md_text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return None
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() == "---":
            fm_text = "\n".join(lines[1:i])
            try:
                return yaml.safe_load(fm_text) or {}
            except Exception:
                return None
    return None


def get_file_metadata(filepath: str) -> Dict[str, Any]:
    """Extract domain and owner from MD frontmatter or YAML sidecars."""
    if not os.path.exists(filepath):
        return {}

    if filepath.endswith((".yml", ".yaml")):
        doc = load_yaml(filepath)
        if isinstance(doc, dict):
            return doc
    elif filepath.endswith(".md"):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                fm = find_frontmatter(f.read())
                if fm:
                    return fm
        except Exception:
            pass
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--routing", default="schemas/routing/agent-routing.yaml")
    ap.add_argument("files", nargs="+", help="Changed files in the PR")
    args = ap.parse_args()

    routing = load_yaml(args.routing)
    if not routing or "decision_routing" not in routing:
        print(f"❌ Could not load routing rules from {args.routing}")
        sys.exit(1)

    rules = routing["decision_routing"]
    impacted_domains: Set[str] = set()
    impacted_components: Set[str] = set()
    present_artifacts: Set[str] = set()

    # 1. Analyze what's in the PR
    for f in args.files:
        # Identify newly created artifacts
        if "docs/adrs/ADR-" in f:
            present_artifacts.add("adr")
        if "docs/changelog/entries/CL-" in f:
            present_artifacts.add("changelog")

        # Identify impacted domains/components via metadata
        meta = get_file_metadata(f)
        domain = meta.get("domain")
        component = meta.get("component")
        if domain:
            impacted_domains.add(domain)
        if component:
            impacted_components.add(component)

        # Heuristic for component detection based on path
        if "gitops/argocd" in f:
            impacted_components.add("argo")
        if "gitops/" in f:
            impacted_components.add("gitops")
        if "ci/" in f or ".github/workflows" in f:
            impacted_components.add("ci")
        if "infra/" in f:
            impacted_components.add("infra")

    # 2. Determine required artifacts and reviewers
    required_artifacts: Set[str] = set()
    required_reviewers: Set[str] = set()

    for domain in impacted_domains:
        d_rule = rules.get("by_domain", {}).get(domain)
        if d_rule:
            required_artifacts.update(d_rule.get("required_artifacts", []))
            required_reviewers.update(d_rule.get("required_reviewers", []))

    for comp in impacted_components:
        c_rule = rules.get("by_component", {}).get(comp)
        if c_rule:
            required_artifacts.update(c_rule.get("required_artifacts", []))
            required_reviewers.update(c_rule.get("required_reviewers", []))

    # 3. Validate
    errors = []
    for art in required_artifacts:
        if art not in present_artifacts:
            errors.append(
                f"Missing mandatory artifact: {art.upper()} (required by domain/component impact)"
            )

    print("🛡️ Governance Routing Compliance")
    print(f"Impacted Domains: {list(impacted_domains)}")
    print(f"Impacted Components: {list(impacted_components)}")
    print(f"Required Reviewers: {list(required_reviewers)}")
    print("-" * 30)

    if errors:
        for err in errors:
            print(f"❌ {err}")
        sys.exit(1)

    print("✅ Governance compliance verified.")
    sys.exit(0)


if __name__ == "__main__":
    main()
