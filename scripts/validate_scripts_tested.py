#!/usr/bin/env python3
"""
---
id: validate_scripts_tested
type: script
owner: platform-team
status: active
maturity: 3
test:
  runner: pytest
  command: "pytest -q tests/unit/test_validate_scripts_tested.py"
  evidence: ci
dry_run:
  supported: true
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
---
Purpose: Enforces Schema-Driven Script Certification (Acceptance Rule V1)
"""

import os
import sys
import re
import yaml
import argparse
from pathlib import Path

# Add python lib to path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
try:
    from script_metadata import parse_header
except ImportError:
    print("❌ Failed to import script_metadata from lib/")
    sys.exit(1)

# Constants
SCHEMA_PATH = Path("schemas/automation/script.schema.yaml")
PROOF_DIR = Path("test-results/proofs")


def die(msg: str) -> None:
    print(f"❌ FAIL: {msg}", file=sys.stderr)
    return False  # Return False instead of exit to allow counting


def load_schema():
    if not SCHEMA_PATH.exists():
        print(f"❌ Schema not found: {SCHEMA_PATH}")
        sys.exit(1)
    try:
        with open(SCHEMA_PATH, "r") as f:
            full_doc = list(yaml.safe_load_all(f))
            for doc in full_doc:
                if doc and "script" in doc:
                    return doc["script"]
            return full_doc[-1]
    except Exception as e:
        print(f"❌ Failed to load schema: {e}")
        sys.exit(1)


def require(meta: dict, key: str, ctx: str) -> bool:
    # supports nested keys like "test.command"
    cur = meta
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            die(f"Missing required field '{key}' in {ctx}")
            return False
        cur = cur[part]
    return True


def validate_file(filepath, schema, args):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return ["Could not read file"]

    data = parse_header(content)
    if not data:
        return ["Missing Metadata Header (YAML Frontmatter)"]

    errors = []

    # 1. Structural Requirements (Nested)
    req_checks = [
        "test.runner",
        "test.command",
        "test.evidence",
        "dry_run.supported",
        "risk_profile.production_impact",
    ]
    for r in req_checks:
        if not require(data, r, str(filepath)):
            errors.append(f"Missing {r}")

    if errors:
        return errors

    # 2. Logic & Policy Checks

    # Policy: No manual evidence for Medium/High Impact
    impact = data["risk_profile"]["production_impact"]
    evidence = data["test"]["evidence"]
    if impact in ("medium", "high") and evidence == "manual":
        errors.append(
            f"Manual test evidence not allowed for production_impact={impact}"
        )

    # Heuristic: Pytest test file existence
    if data["test"]["runner"] == "pytest":
        cmd = data["test"]["command"]
        # Basic regex to find the test path in the command
        m = re.search(r"(tests/[\w/\-\.]+\.py)", cmd)
        if m:
            test_path = Path(m.group(1))
            if not test_path.exists():
                try:
                    maturity = int(data.get("maturity", 1))
                except:
                    maturity = 1

                if maturity >= 3:
                    errors.append(
                        f"Declared pytest test file not found: {test_path} (Required for Maturity {maturity})"
                    )
                else:
                    print(
                        f"⚠️  [WARNING] {filepath}: Test missing {test_path} (Allowed for Maturity {maturity})"
                    )

    # Shellcheck command check
    if data["test"]["runner"] == "shellcheck":
        cmd = data["test"]["command"]
        if str(filepath) not in cmd and filepath.name not in cmd:
            errors.append("Shellcheck command must include script path")

    # 3. Proof Verification (Maturity 3 Check)
    script_id = data.get("id")
    if evidence == "ci" and args.verify_proofs:
        proof_path = PROOF_DIR / f"proof-{script_id}.json"
        if not proof_path.exists():
            errors.append(f"Missing CI Proof file: {proof_path} (evidence='ci')")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate script metadata contracts")
    parser.add_argument("paths", nargs="*", default=["scripts"], help="Paths to scan")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be checked"
    )
    parser.add_argument(
        "--verify-proofs",
        action="store_true",
        help="Check for existence of proof artifacts",
    )
    args = parser.parse_args()

    schema = load_schema()

    scripts_to_check = []
    for path_str in args.paths:
        p = Path(path_str)
        if p.is_file():
            scripts_to_check.append(p)
        else:
            for r, d, f in os.walk(p):
                for file in f:
                    if file.endswith(".py") or file.endswith(".sh"):
                        scripts_to_check.append(Path(r) / file)

    # Filter out lib/ and exempted paths
    filtered_scripts = []
    for s in scripts_to_check:
        if "lib" in s.parts or s.name == "__init__.py":
            continue
        filtered_scripts.append(s)

    if args.dry_run:
        print(f"[DRY-RUN] Would validate {len(filtered_scripts)} scripts.")
        return

    failure_count = 0
    print(f"🔍 Validating {len(filtered_scripts)} scripts...")

    for script in filtered_scripts:
        errors = validate_file(script, schema, args)
        if errors:
            failure_count += 1
            print(f"❌ {script}")
            for e in errors:
                print(f"   - {e}")
        else:
            print(f"✅ {script}")

    if failure_count > 0:
        sys.exit(1)
    else:
        print("SUCCESS: All scripts compliant.")
        sys.exit(0)


if __name__ == "__main__":
    main()
