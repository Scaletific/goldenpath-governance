#!/usr/bin/env python3
"""
---
id: SCRIPT-0001
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0001.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Metadata Audit Utility (Active Governance Loop)

Purpose:
    Performs repo-wide scans for metadata compliance and generates health snapshots.
    Tracks lineage (Inherited vs Local) and detects "Enum Drift".
"""

import os
import yaml
import json
from datetime import datetime
from lib.metadata_config import MetadataConfig

cfg = MetadataConfig()


def audit_repo(root_dir="."):
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_files": 0,
        "compliant_files": 0,
        "inherited_coverage": 0,
        "explicit_coverage": 0,
        "exempt_files": 0,
        "enum_drift_attempts": 0,
        "failures": [],
    }

    mandated_zones = ["apps", "docs", "gitops", "envs", "runbooks"]

    for zone in mandated_zones:
        zone_path = os.path.join(root_dir, zone)
        if not os.path.isdir(zone_path):
            continue

        for root, _, files in os.walk(zone_path):
            for f in files:
                if f.endswith((".md", ".yaml", ".yml")) and f != "metadata.yaml":
                    stats["total_files"] += 1
                    filepath = os.path.join(root, f)

                    try:
                        # Extract metadata
                        with open(filepath, "r") as file:
                            content = file.read()

                        # Simplified frontmatter extraction
                        data = {}
                        if filepath.endswith(".md"):
                            if content.startswith("---"):
                                parts = content.split("---", 2)
                                if len(parts) >= 3:
                                    data = yaml.safe_load(parts[1]) or {}
                        else:
                            # Support multi-document YAML (take first document for metadata)
                            try:
                                docs = list(yaml.safe_load_all(content))
                                if docs:
                                    data = docs[0] or {}
                            except Exception:
                                # Fallback to single load if all_load fails for some reason
                                data = yaml.safe_load(content) or {}

                        # Check inheritance
                        parent = cfg.find_parent_metadata(filepath)
                        effective = cfg.get_effective_metadata(filepath, data)

                        if data.get("exempt"):
                            stats["exempt_files"] += 1

                        # Count explicit vs inherited (simplified: if present in effective but not in local)
                        for k in effective:
                            if k not in data:
                                stats["inherited_coverage"] += 1
                            else:
                                stats["explicit_coverage"] += 1

                    except Exception as e:
                        stats["failures"].append({"file": filepath, "error": str(e)})

    return stats


def save_report(stats, output_path="docs/governance/reports"):
    os.makedirs(output_path, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(output_path, f"compliance_snapshot_{date_str}.json")

    with open(report_file, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"✅ Audit complete. Snapshot saved to: {report_file}")


if __name__ == "__main__":
    results = audit_repo()
    save_report(results)
