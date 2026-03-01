"""
---
id: SCRIPT-0022
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0022.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

import os
import glob
import ast

SCRIPTS_DIR = "scripts"
OUTPUT_FILE = "scripts/index.md"

CATEGORIES = {
    "Governance": [
        "standardize_metadata",
        "validate_metadata",
        "pr_guardrails",
        "platform_health",
        "check_compliance",
    ],
    "Documentation": [
        "format_docs",
        "check_doc_freshness",
        "check_doc_index_contract",
        "extract_relationships",
        "generate_workflow_index",
        "generate_catalog_docs",
    ],
    "Delivery": [
        "ecr-build-push",
        "scaffold_ecr",
        "render_template",
        "generate-build-log",
        "generate-teardown-log",
        "resolve-cluster-name",
    ],
    "Utilities": [
        "backfill_metadata",
        "fix_yaml_syntax",
        "test_hotfix",
        "test_platform_health",
        "reliability-metrics",
        "migrate_partial_metadata",
    ],
}


def get_docstring(file_path):
    """Extract docstring or first comment from script."""
    try:
        if file_path.endswith(".py"):
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
            return ast.get_docstring(tree) or "No description provided."
        elif file_path.endswith(".sh"):
            with open(file_path, "r") as f:
                first_line = f.readline()
                if first_line.startswith("#"):
                    # Try to capture a header block if it exists
                    second_line = f.readline()
                    if second_line.startswith("#"):
                        return second_line.strip("# ").strip()
            return "Shell script utility."
    except Exception:
        return "No description available."

    return "No description available."


def get_category(filename):
    base = filename.split(".")[0]
    for cat, scripts in CATEGORIES.items():
        if any(s in base for s in scripts):
            return cat
    return "Utilities"


def generate_index_content():
    scripts = []
    # Find both .py and .sh files
    for file_path in glob.glob(f"{SCRIPTS_DIR}/*.py") + glob.glob(
        f"{SCRIPTS_DIR}/*.sh"
    ):
        name = os.path.basename(file_path)
        if name in ["__init__.py", "generate_script_index.py"]:
            continue

        category = get_category(name)
        description = get_docstring(file_path)
        # Taking just the first line of docstring for brevity in table
        if description:
            description = description.split("\n")[0]

        scripts.append(
            {
                "name": name,
                "category": category,
                "path": file_path,
                "description": description,
            }
        )

    # Sort scripts by category then name
    sorted_scripts = sorted(scripts, key=lambda x: (x["category"], x["name"]))
    current_cat = None
    lines = []

    for script in sorted_scripts:
        if script["category"] != current_cat:
            current_cat = script["category"]
            if lines:
                lines.append("")
            lines.append(f"## {current_cat}")
            lines.append("")
            lines.append("| Script | Description |")
            lines.append("| :--- | :--- |")

        rel_path = os.path.relpath(script["path"], start=os.path.dirname(OUTPUT_FILE))
        link = f"[{script['name']}]({rel_path})"
        desc = script["description"] or "Utility script"
        lines.append(f"| {link} | {desc} |")

    return "\n".join(lines)


def update_index_file(table_content, validate_only=False):
    import re

    if not os.path.exists(OUTPUT_FILE):
        print(f"❌ Error: {OUTPUT_FILE} not found.")
        return False

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    START_MARKER = "<!-- SCRIPTS_TABLE_START -->"
    END_MARKER = "<!-- SCRIPTS_TABLE_END -->"
    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL
    )
    new_block = f"{START_MARKER}\n{table_content}\n{END_MARKER}"
    new_content = pattern.sub(new_block, content)

    if validate_only:
        return new_content.strip() == content.strip()

    if new_content.strip() == content.strip():
        print(f"✅ {OUTPUT_FILE} is already up to date.")
        return True

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content.strip() + "\n")
    print(f"✅ Successfully updated {OUTPUT_FILE}")
    return True


if __name__ == "__main__":
    import sys

    # Check mode: Fail if any script is missing a description
    if "--validate" in sys.argv:
        missing_docs = []
        for file_path in glob.glob(f"{SCRIPTS_DIR}/*.py") + glob.glob(
            f"{SCRIPTS_DIR}/*.sh"
        ):
            name = os.path.basename(file_path)
            if name in ["__init__.py", "generate_script_index.py"]:
                continue
            desc = get_docstring(file_path)
            if not desc or desc.startswith("No description"):
                missing_docs.append(name)

        if missing_docs:
            print("❌ Governance Failure: Scripts missing docstrings:", missing_docs)
            sys.exit(1)

        content = generate_index_content()
        if not update_index_file(content, validate_only=True):
            print(f"❌ Drift Detected in {OUTPUT_FILE}")
            sys.exit(1)
        print("✅ Index is up-to-date.")
        sys.exit(0)

    # Normal mode
    content = generate_index_content()
    update_index_file(content)
