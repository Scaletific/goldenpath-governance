#!/usr/bin/env python3
"""
---
id: SCRIPT-0006
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0006.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Documentation Index Contract Validator.
Verifies that index files (like index.md) exist and adhere to platform linking standards.
"""
import os
import sys


INDEX_PATH = os.path.join("docs", "90-doc-system", "00_DOC_INDEX.md")
REQUIRED_FIELDS = {
    "purpose",
    "owner",
    "status",
    "review cadence",
    "related",
}


def load_index_rows(path):
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if "---" in line:
                continue
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) < 4:
                continue
            if parts[0].lower() == "doc":
                continue
            rows.append(parts)
    return rows


def parse_doc_contract(path, max_lines=80):
    contract = {}
    in_contract = False
    with open(path, "r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            if idx >= max_lines:
                break
            line = line.rstrip()
            if line.startswith("Doc contract:"):
                in_contract = True
                continue
            if not in_contract:
                continue
            if not line.strip():
                continue
            if not line.startswith("-"):
                break
            entry = line.lstrip("-").strip()
            if ":" not in entry:
                continue
            key, value = entry.split(":", 1)
            contract[key.strip().lower()] = value.strip()
    return contract if contract else None


def main():
    if not os.path.exists(INDEX_PATH):
        print(f"ERROR: Missing {INDEX_PATH}")
        return 1

    rows = load_index_rows(INDEX_PATH)
    if not rows:
        print("ERROR: No living docs found in index.")
        return 1

    errors = []

    for row in rows:
        doc_path = row[0]
        owner = row[1]
        review_cycle = row[2]

        if not os.path.exists(doc_path):
            errors.append(f"Missing doc file: {doc_path}")
            continue

        contract = parse_doc_contract(doc_path)
        if contract is None:
            errors.append(f"{doc_path}: missing Doc contract block")
            continue

        missing_fields = REQUIRED_FIELDS - set(contract.keys())
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            errors.append(f"{doc_path}: missing contract fields: {missing}")
            continue

        contract_owner = contract["owner"].lower()
        if contract_owner != owner.lower():
            errors.append(
                f"{doc_path}: owner mismatch (index={owner}, contract={contract['owner']})"
            )

        contract_cycle = contract["review cadence"]
        if contract_cycle != review_cycle:
            errors.append(
                f"{doc_path}: review cadence mismatch "
                f"(index={review_cycle}, contract={contract_cycle})"
            )

        if contract["status"].lower() != "living":
            errors.append(f"{doc_path}: status must be living for indexed docs")

    for item in errors:
        print(f"ERROR: {item}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
