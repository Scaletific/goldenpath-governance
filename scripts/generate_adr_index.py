#!/usr/bin/env python3
"""
---
id: SCRIPT-0016
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0016.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
ADR Index Generator (Iteration 1)
Automates the generation of 01_adr_index.md from ADR-*.md metadata.
"""

import os
import re
import sys
import yaml  # Using PyYAML as it is standardized in this repo

# Paths
ADR_DIR = "docs/adrs"
INDEX_FILE = os.path.join(ADR_DIR, "01_adr_index.md")

# Markers
TABLE_START = "<!-- ADR_TABLE_START -->"
TABLE_END = "<!-- ADR_TABLE_END -->"
RELATE_START = "<!-- ADR_RELATE_START -->"
RELATE_END = "<!-- ADR_RELATE_END -->"


def extract_metadata(file_path):
    """Extract YAML frontmatter and context summary from an ADR file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract YAML
    yaml_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not yaml_match:
        return None

    metadata = yaml.safe_load(yaml_match.group(1))

    # Extract Summary (First non-empty paragraph under ## Context)
    summary = "No context provided."
    context_match = re.search(r"## Context\s*\n+(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if context_match:
        context_text = context_match.group(1).strip()
        # Take the first paragraph
        first_para = context_text.split("\n\n")[0].replace("\n", " ").strip()
        if first_para:
            summary = first_para
            summary = summary.replace("` ", "`").replace(" `", "`")
            # Robust Backtick Cleanup: remove spaces inside ` ... `
            summary = re.sub(r"`\s+([^`]+?)\s+`", r"`\1`", summary)
            summary = re.sub(r"`\s+([^`]+?)`", r"`\1`", summary)
            summary = re.sub(r"`([^`]+?)\s+`", r"`\1`", summary)

            # Truncate summary for table readability if necessary
            if len(summary) > 200:
                summary = summary[:197] + "..."

    metadata["summary"] = summary
    metadata["filename"] = os.path.basename(file_path)
    return metadata


def generate_index_content():
    """Scan ADR files and generate table and relate_to list."""
    adr_files = [
        f for f in os.listdir(ADR_DIR) if f.startswith("ADR-") and f.endswith(".md")
    ]
    all_metadata = []

    for filename in adr_files:
        meta = extract_metadata(os.path.join(ADR_DIR, filename))
        if meta:
            all_metadata.append(meta)

    # Sort by ID (numerical sort) and normalize
    normalized_metadata = []
    for m in all_metadata:
        raw_id = m.get("id", "")
        # Enforce ADR-XXXX format
        id_match = re.search(r"ADR-[0-9]{4}", raw_id)
        if id_match:
            m["id"] = id_match.group(0)
            normalized_metadata.append(m)

    normalized_metadata.sort(key=lambda x: (x.get("id", ""), x.get("filename", "")))

    # Generate Table
    table_lines = []
    for m in normalized_metadata:
        adr_id = m["id"]
        domain = m.get("category", "Platform").capitalize()
        title = m.get("title", "Untitled").replace(adr_id + ": ", "").strip("'\" ")
        # Global Backtick Space Cleanup for title (MD038)
        title = title.replace("` ", "`").replace(" `", "`")

        status = m.get("status", "Proposed").capitalize()
        date = m.get("date", "") or m.get("created_date", "2026-01-0?")
        summary = m.get("summary", "")

        line = f"| [{adr_id}]({m['filename']}) | {domain} | {title} | {status} | {date} | {summary} |"
        table_lines.append(line)

    table_content = "\n".join(table_lines)

    # Generate relates_to list
    relate_lines = [f"  - {m['id']}" for m in normalized_metadata]
    relate_content = "\n".join(relate_lines)

    return table_content, relate_content


def update_index_file(table_content, relate_content, validate_only=False):
    """Inject generated content into the index file."""
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Inject Table
    table_pattern = re.compile(
        f"{re.escape(TABLE_START)}.*?{re.escape(TABLE_END)}", re.DOTALL
    )
    new_table = f"{TABLE_START}\n{table_content}\n{TABLE_END}"

    # Inject Relates
    relate_pattern = re.compile(
        f"{re.escape(RELATE_START)}.*?{re.escape(RELATE_END)}", re.DOTALL
    )
    new_relate = f"{RELATE_START}\n{relate_content}\n{RELATE_END}"

    new_content = table_pattern.sub(new_table, content)
    new_content = relate_pattern.sub(new_relate, new_content)

    if validate_only:
        if new_content != content:
            print("Drift detected in ADR Index!")
            return False
        print("ADR Index is up to date.")
        return True

    if new_content == content:
        print("ADR Index is already up to date.")
        return True

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated ADR Index.")
    return True


def main():
    validate = "--validate" in sys.argv
    table, relate = generate_index_content()
    success = update_index_file(table, relate, validate_only=validate)
    if not success and validate:
        sys.exit(1)


if __name__ == "__main__":
    main()
