"""
---
id: SCRIPT-0023
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0023.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Auto-generate CI Workflows Index (CI_WORKFLOWS.md).
Parses GitHub Actions YAML to categorize and document all workflows to prevent drift.
"""
import os
import yaml
import glob
from collections import defaultdict

WORKFLOW_DIR = ".github/workflows"
OUTPUT_FILE = "ci-workflows/CI_WORKFLOWS.md"

# Taxonomy mapping: matches workflow usage to categories
CATEGORY_MAP = {
    "Guardrails / Policy (PR)": [
        "guardrails",
        "policy",
        "lint",
        "check",
        "validation",
        "freshness",
        "pre-commit",
        "guard",
        "approval guard",
        "drift guard",
        "capture guardrail",
    ],
    "Terraform Plan": ["plan", "checks"],
    "Terraform Apply": ["apply", "update"],
    "Bootstrap / Tooling": ["bootstrap", "backstage", "scaffold", "registry"],
    "Teardown / Recovery": ["teardown", "cleanup", "unlock", "recovery"],
    "Ops / Maintenance": ["orphan", "maintenance"],
}


def get_category(name):
    lower_name = name.lower()
    for category, keywords in CATEGORY_MAP.items():
        if any(k in lower_name for k in keywords):
            return category
    return "Uncategorized"


def parse_workflows():
    workflows = []
    for file_path in glob.glob(f"{WORKFLOW_DIR}/*.yml") + glob.glob(
        f"{WORKFLOW_DIR}/*.yaml"
    ):
        with open(file_path, "r") as f:
            try:
                # Read raw content to find Owner comment since YAML parser skips comments
                raw_content = f.read()
                owner = "platform"  # default
                for line in raw_content.splitlines():
                    if line.startswith("# Owner:"):
                        owner = line.split(":", 1)[1].strip()
                        break

                # Parse YAML
                data = yaml.safe_load(raw_content)
                if not data or "name" not in data:
                    continue

                name = data["name"]
                category = get_category(name)

                triggers = []
                if "on" in data:
                    if isinstance(data["on"], dict):
                        triggers = list(data["on"].keys())
                    elif isinstance(data["on"], list):
                        triggers = data["on"]
                    elif isinstance(data["on"], str):
                        triggers = [data["on"]]

                inputs = []
                if (
                    "workflow_dispatch" in data.get("on", {})
                    and data["on"]["workflow_dispatch"]
                ):
                    inputs = list(
                        data["on"]["workflow_dispatch"].get("inputs", {}).keys()
                    )

                workflows.append(
                    {
                        "name": name,
                        "file": os.path.basename(file_path),
                        "category": category,
                        "owner": owner,
                        "triggers": triggers,
                        "inputs": inputs,
                    }
                )
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return workflows


def generate_ascii_tree(workflows_by_category):
    lines = ["```text", "CI Workflows (GitHub Actions)", ""]

    sorted_categories = sorted(workflows_by_category.keys())

    for i, category in enumerate(sorted_categories):
        is_last_cat = i == len(sorted_categories) - 1
        prefix = "└─" if is_last_cat else "├─"
        lines.append(f"{prefix} {category}")

        items = sorted(workflows_by_category[category], key=lambda x: x["name"])
        for j, wf in enumerate(items):
            is_last_item = j == len(items) - 1
            sub_prefix = "   └─" if is_last_item else "   ├─"
            # Use pipe prefix if not last category to continue the line down
            if not is_last_cat:
                sub_prefix = "│" + sub_prefix
            else:
                sub_prefix = " " + sub_prefix

            lines.append(f"{sub_prefix} {wf['name']}")

        if not is_last_cat:
            lines.append("│")

    lines.append("```")
    return "\n".join(lines)


def generate_content(workflows):
    # Group by category
    by_category = defaultdict(list)
    for wf in workflows:
        by_category[wf["category"]].append(wf)

    # Tree
    tree = generate_ascii_tree(by_category)

    # Details
    details = []
    for category in sorted(by_category.keys()):
        details.append(f"## {category}")
        details.append("")
        for wf in sorted(by_category[category], key=lambda x: x["name"]):
            details.append(f"### {wf['name']}")
            details.append(f"- **File**: `{wf['file']}`")
            details.append(f"- **Owner**: {wf['owner']}")
            triggers_str = ", ".join(wf["triggers"])
            details.append(f"- **Triggers**: {triggers_str}".strip())
            if wf["inputs"]:
                inputs_str = ", ".join(wf["inputs"])
                details.append(f"- **Inputs**: {inputs_str}".strip())
            details.append("")

    return tree, "\n".join(details)


def update_index_file(tree_content, details_content, validate_only=False):
    if not os.path.exists(OUTPUT_FILE):
        print(f"❌ Error: {OUTPUT_FILE} not found.")
        return False

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Tree
    t_start, t_end = "<!-- WORKFLOW_TREE_START -->", "<!-- WORKFLOW_TREE_END -->"
    tree_pattern = re.compile(f"{re.escape(t_start)}.*?{re.escape(t_end)}", re.DOTALL)
    new_tree = f"{t_start}\n{tree_content}\n{t_end}"
    new_content = tree_pattern.sub(new_tree, content)

    # Details
    d_start, d_end = "<!-- WORKFLOW_DETAILS_START -->", "<!-- WORKFLOW_DETAILS_END -->"
    details_pattern = re.compile(
        f"{re.escape(d_start)}.*?{re.escape(d_end)}", re.DOTALL
    )
    new_details = f"{d_start}\n{details_content}\n{d_end}"
    new_content = details_pattern.sub(new_details, new_content)

    if validate_only:
        return new_content.strip() == content.strip()

    if new_content.strip() == content.strip():
        print(f"✅ {OUTPUT_FILE} already up to date.")
        return True

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content.strip() + "\n")
    print(f"✅ Successfully updated {OUTPUT_FILE}")
    return True


import re

if __name__ == "__main__":
    import sys

    wfs = parse_workflows()
    tree, details = generate_content(wfs)

    if "--validate" in sys.argv:
        if not update_index_file(tree, details, validate_only=True):
            print(f"❌ Drift Detected in {OUTPUT_FILE}")
            sys.exit(1)
        print("✅ Index is up-to-date.")
        sys.exit(0)

    # Normal mode
    update_index_file(tree, details)
