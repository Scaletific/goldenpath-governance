#!/usr/bin/env python3
"""
---
id: generate_script_matrix
type: script
owner: platform-team
status: active
maturity: 3
test:
  runner: pytest
  command: "pytest -q tests/unit/test_generate_script_matrix.py"
  evidence: ci
dry_run:
  supported: true
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
---
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add python lib to path
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
try:
    from script_metadata import parse_header
except ImportError:
    print("❌ Failed to import script_metadata from lib/")
    sys.exit(1)

SCRIPTS_DIR = Path("scripts")
OUT = Path("docs/governance/GOV-0053-script-certification-matrix.md")
VALUE_LEDGER = Path(".goldenpath/value_ledger.json")


def write_maturity_snapshot(rows: list) -> None:
    """Write maturity distribution snapshot to value_ledger.json."""
    # Calculate maturity distribution
    maturity_counts = {"M0": 0, "M1": 0, "M2": 0, "M3": 0}
    for r in rows:
        mat = str(r.get("maturity", "0"))
        key = f"M{mat}" if mat in ("0", "1", "2", "3") else "M0"
        maturity_counts[key] += 1

    snapshot = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_scripts": len(rows),
        "maturity_distribution": maturity_counts,
        "certification_rate": round(
            (maturity_counts["M3"] / len(rows) * 100) if rows else 0, 1
        ),
    }

    # Read existing ledger
    if VALUE_LEDGER.exists():
        try:
            ledger = json.loads(VALUE_LEDGER.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            ledger = {}
    else:
        ledger = {}

    # Ensure maturity_snapshots array exists
    if "maturity_snapshots" not in ledger:
        ledger["maturity_snapshots"] = []

    # Only append if distribution has changed from last snapshot
    snapshots = ledger["maturity_snapshots"]
    if snapshots:
        last = snapshots[-1]
        if (
            last.get("total_scripts") == snapshot["total_scripts"]
            and last.get("maturity_distribution") == snapshot["maturity_distribution"]
        ):
            # No change in distribution, skip writing
            return

    # Append new snapshot (keep last 30)
    ledger["maturity_snapshots"].append(snapshot)
    ledger["maturity_snapshots"] = ledger["maturity_snapshots"][-30:]

    # Write back
    VALUE_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    VALUE_LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(f"[matrix] wrote maturity snapshot to {VALUE_LEDGER}")


def read_existing_frontmatter() -> dict:
    """Read existing frontmatter from the output file to preserve relates_to."""
    import yaml

    if not OUT.exists():
        return {}
    content = OUT.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        return {}


def get_meta(path: Path) -> dict:
    try:
        txt = path.read_text(encoding="utf-8", errors="replace")
        return parse_header(txt) or {}
    except Exception:
        return {}


def main() -> int:
    rows = []
    # Filter for scripts, exclude dirs and lib/
    scripts = sorted(
        [
            p
            for p in SCRIPTS_DIR.glob("*")
            if p.is_file()
            and p.suffix in (".py", ".sh", ".bash")
            and p.name != "__init__.py"
        ]
    )

    for p in scripts:
        meta = get_meta(p)

        # Safe getters for nested dicts
        dry_run = (
            meta.get("dry_run", {}) if isinstance(meta.get("dry_run"), dict) else {}
        )
        test = meta.get("test", {}) if isinstance(meta.get("test"), dict) else {}
        risk = (
            meta.get("risk_profile", {})
            if isinstance(meta.get("risk_profile"), dict)
            else {}
        )

        rows.append(
            {
                "path": str(p),
                "id": meta.get("id", "MISSING"),
                "owner": meta.get("owner", "MISSING"),
                "maturity": meta.get("maturity", "0"),
                "dry_run": dry_run.get("supported", False),
                "test_runner": test.get("runner", "MISSING"),
                "evidence": test.get("evidence", "MISSING"),
                "prod_impact": risk.get("production_impact", "MISSING"),
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)

    # Preserve existing relates_to from current file
    existing = read_existing_frontmatter()
    relates_to = existing.get("relates_to", [])

    md = []
    md.append("---")
    md.append("id: GOV-0053-script-certification-matrix")
    md.append("title: Script Certification Matrix")
    md.append("type: report")
    if relates_to:
        md.append("relates_to:")
        for rel in relates_to:
            md.append(f"  - {rel}")
    md.append("---")
    md.append("")
    md.append("<!-- AUTO-GENERATED BY scripts/generate_script_matrix.py -->")
    md.append("# Script Certification Matrix")
    md.append(f"**Total Scripts**: {len(rows)}\n")
    md.append(
        "| Script | ID | Owner | Maturity | Dry-run | Test Runner | Evidence | Prod Impact |"
    )
    md.append("|---|---|---|---:|---:|---|---|---|")

    for r in rows:
        # Format booleans nicely
        dry_run_icon = "✅" if r["dry_run"] is True else "🚫"

        # Format maturity
        mat = str(r["maturity"])
        if mat == "3":
            mat = "⭐⭐⭐ 3"
        elif mat == "2":
            mat = "⭐⭐ 2"
        elif mat == "1":
            mat = "⭐ 1"
        else:
            mat = "0"

        md.append(
            f"| `{r['path']}` | `{r['id']}` | `{r['owner']}` | {mat} | {dry_run_icon} | `{r['test_runner']}` | `{r['evidence']}` | `{r['prod_impact']}` |"
        )

    md.append("\n*Generated automatically by CI. Do not edit manually.*")

    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[matrix] wrote {OUT}")

    # Write maturity snapshot to value ledger
    write_maturity_snapshot(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
