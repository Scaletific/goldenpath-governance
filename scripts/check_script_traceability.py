#!/usr/bin/env python3
"""
---
id: SCRIPT-0007
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0007.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Script Traceability Auditor

Purpose: Ensure every automation script is linked to an ADR and a Changelog entry.
Value: Eliminates "Dark History" and Ensures 100% auditability for automation.

Usage:
    python3 scripts/check_script_traceability.py [--validate] [--script <name>]
"""

import os
import sys
import glob

SCRIPTS_DIR = "scripts"
ADRS_DIR = "docs/adrs"
CLS_DIR = "docs/changelog/entries"

# Scripts that are exempted from traceability (e.g., helpers, templates)
EXEMPT_SCRIPTS = [
    "__init__.py",
    "check_script_traceability.py",  # Self-exempt
]


def search_in_dir(query, directory):
    """Search for a query string in all markdown files in a directory."""
    matches = []
    if not os.path.exists(directory):
        return matches

    for file_path in glob.glob(os.path.join(directory, "*.md")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if query in f.read():
                    matches.append(file_path)
        except Exception:
            continue
    return matches


def check_script(script_path):
    """Check a single script for ADR and CL traceability."""
    name = os.path.basename(script_path)
    if name in EXEMPT_SCRIPTS:
        return True, [], []

    adr_matches = search_in_dir(name, ADRS_DIR)
    cl_matches = search_in_dir(name, CLS_DIR)

    is_compliant = len(adr_matches) > 0 and len(cl_matches) > 0
    return is_compliant, adr_matches, cl_matches


def main():
    validate_mode = "--validate" in sys.argv
    target_script = None
    if "--script" in sys.argv:
        idx = sys.argv.index("--script")
        if idx + 1 < len(sys.argv):
            target_script = sys.argv[idx + 1]

    scripts_to_check = []
    if target_script:
        scripts_to_check = [os.path.join(SCRIPTS_DIR, target_script)]
    else:
        scripts_to_check = glob.glob(os.path.join(SCRIPTS_DIR, "*.py")) + glob.glob(
            os.path.join(SCRIPTS_DIR, "*.sh")
        )

    scripts_to_check = [
        s for s in scripts_to_check if os.path.basename(s) not in EXEMPT_SCRIPTS
    ]
    scripts_to_check.sort()

    total = 0
    compliant = 0
    failures = []

    print(f"🔍 Auditing {len(scripts_to_check)} scripts for traceability...")
    print("-" * 60)

    for script in scripts_to_check:
        total += 1
        name = os.path.basename(script)
        is_ok, adrs, cls = check_script(script)

        status = "✅" if is_ok else "❌"
        print(f"{status} {name:<35} | ADRs: {len(adrs):<2} | CLs: {len(cls):<2}")

        if is_ok:
            compliant += 1
        else:
            issues = []
            if not adrs:
                issues.append("Missing ADR")
            if not cls:
                issues.append("Missing CL")
            failures.append(f"{name}: {', '.join(issues)}")

    print("-" * 60)
    print(f"📊 Results: {compliant}/{total} compliant")

    if failures:
        print("\n❌ Traceability Failures:")
        for fail in failures:
            print(f"  - {fail}")

        if validate_mode:
            sys.exit(1)
    else:
        print("\n✅ All scripts are traceable.")
        sys.exit(0)


if __name__ == "__main__":
    main()
