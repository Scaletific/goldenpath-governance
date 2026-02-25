#!/usr/bin/env python3
"""
---
id: SCRIPT-0004
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0004.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Metadata Compliance Audit Tool
Achievement: Performs deep inspection of YAML frontmatter syntax and mandatory field presence.
Value: Used for secondary audits and legacy compliance checks before migrating to the
       unified "Healer" (standardize-metadata.py).
"""
import os
import yaml
import re

REQUIRED_FIELDS = ["id", "title", "type", "category", "version", "owner", "status"]
OPTIONAL_FIELDS = [
    "dependencies",
    "relates_to",
    "risk_profile",
    "reliability",
    "lifecycle",
]


def check_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    errors = []

    # 1. Check for exactly --- terminators
    if not content.startswith("---"):
        return ["Missing frontmatter (must start with ---)"]

    # Check for malformed terminators like ------
    if content.startswith("------"):
        errors.append("Frontmatter starts with more than 3 dashes (found ------)")

    try:
        # Extract frontmatter
        matches = list(re.finditer(r"^---", content, re.MULTILINE))
        if len(matches) < 2:
            return ["Malformed or missing closing --- for frontmatter"]

        # Check if the closing one is exactly ---
        header_text = content[matches[0].end() : matches[1].start()].strip()
        closing_line = content[
            matches[1].start() : matches[1].end() + 3
        ]  # check slightly ahead
        if closing_line.startswith("------"):
            errors.append("Frontmatter ends with more than 3 dashes (found ------)")

        data = yaml.safe_load(header_text)
        if not isinstance(data, dict):
            return ["Frontmatter is not a valid YAML dictionary"]

        # 2. Check for missing required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")
            elif data[field] is None or data[field] == "":
                errors.append(f"Empty required field: '{field}'")

        # 3. Check for recommended fields
        if "dependencies" not in data:
            # Only warn for certain categories? No, let's check everywhere for now.
            pass

        if "relates_to" not in data:
            errors.append("Missing 'relates_to' field")

    except yaml.YAMLError as e:
        errors.append(f"YAML Syntax Error: {e}")
    except Exception as e:
        errors.append(f"Unexpected Error: {e}")

    return errors


def scan_repo(target_path="."):
    compliant = 0
    inconsistent = 0

    if os.path.isfile(target_path):
        if target_path.endswith(".md"):
            errors = check_file(target_path)
            if errors:
                print(f"❌ {target_path}")
                for err in errors:
                    print(f"   - {err}")
                return 0, 1
            else:
                print(f"✅ {target_path} is compliant")
                return 1, 0
        else:
            print(f"Skipping {target_path} (not a markdown file)")
            return 0, 0

    for root, dirs, files in os.walk(target_path):
        # Skip hidden and node_modules
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]

        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                errors = check_file(filepath)
                if errors:
                    inconsistent += 1
                    print(f"❌ {filepath}")
                    for err in errors:
                        print(f"   - {err}")
                else:
                    compliant += 1
                    # Progress indicator for large scans
                    if (compliant + inconsistent) % 50 == 0:
                        print(f"Progress: Checked {compliant + inconsistent} files...")

    return compliant, inconsistent


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."

    c, i = scan_repo(target)

    if len(sys.argv) <= 1 or os.path.isdir(target):
        print("\n" + "=" * 40)
        print(f"Scan Complete for: {target}")
        print(f"✅ Compliant: {c}")
        print(f"❌ Inconsistent: {i}")
        print("=" * 40)
