#!/usr/bin/env python3
"""
---
id: standardize_metadata
type: script
owner: platform-team
status: active
maturity: 3
test:
  runner: pytest
  command: "pytest -q tests/unit/test_standardize_metadata.py"
  evidence: ci
dry_run:
  supported: true
  command_hint: "--dry-run"
risk_profile:
  production_impact: high
  security_risk: none
  coupling_risk: high
---
Purpose: Automated Remediation Engine ("The Healer")
Achievement: Enables O(1) schema evolution across 300+ files. Merges existing data with
             the canonical governance skeleton, enforces path-based IDs, and creates
             missing metadata sidecars in mandated zones.
Value: Eliminates manual backfills and "governance debt" while bridging the gap
       between documentation and live infrastructure auditability.
"""

import os
import re
import yaml
import copy
import argparse
import sys

# Add lib to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
from lib.metadata_config import (
    MetadataConfig,
    platform_yaml_dump,
    platform_yaml_dump_all,
)

cfg = MetadataConfig()

# Fallback owner and versions if schema lookup fails
OWNER = "platform-team"
VERSION = "1.0"

VQ_DEFAULTS_BY_TYPE = {
    "policy": {
        "vq_class": "🔴 HV/HQ",
        "impact_tier": "tier-1",
        "potential_savings_hours": 2.0,
    },
    "adr": {
        "vq_class": "🔴 HV/HQ",
        "impact_tier": "tier-2",
        "potential_savings_hours": 1.0,
    },
    "runbook": {
        "vq_class": "🔵 MV/HQ",
        "impact_tier": "tier-2",
        "potential_savings_hours": 0.5,
    },
    "automation-script": {
        "vq_class": "🔴 HV/HQ",
        "impact_tier": "tier-1",
        "potential_savings_hours": 1.0,
    },
}


def get_type_from_path(filepath):
    if "adrs/" in filepath:
        return "adr"
    if "changelog/" in filepath:
        return "changelog"
    if "runbooks/" in filepath:
        return "runbook"
    if "governance/" in filepath:
        return "policy"
    if "contracts/" in filepath:
        return "contract"
    if "strategy" in filepath:
        return "strategy"
    return "documentation"


def parse_frontmatter(content):
    match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        try:
            return yaml.safe_load(fm_text), match.end()
        except:
            return None, 0
    return None, 0


SIDECAR_MANDATED_ZONES = ["gitops/helm", "idp-tooling", "envs", "apps"]


def standardize_file(filepath, dry_run=False):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    is_yaml = filepath.endswith(".yaml") or filepath.endswith(".yml")
    data = None
    body = ""

    # 1. Parse existing content
    if is_yaml:
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                data = {}
        except:
            data = {}
    else:
        data, body_start = parse_frontmatter(content)
        if data is None and content.startswith("---"):
            # Handle corrupted or multi-dash blocks
            lines = content.splitlines()
            last_dash_idx = -1
            for i, line in enumerate(lines[:30]):
                if line.strip().startswith("---"):
                    last_dash_idx = i
            body = (
                "\n".join(lines[last_dash_idx + 1 :])
                if last_dash_idx != -1
                else content
            )
        elif data is not None:
            body = content[body_start:]
        else:
            body = content

    filename_base = os.path.splitext(os.path.basename(filepath))[0]
    title_match = re.search(r"^#\s+(.*)", body, re.MULTILINE) if not is_yaml else None
    default_title = title_match.group(1) if title_match else filename_base

    # 2. GET EFFECTIVE CONTEXT (Inheritance)
    effective_data = cfg.get_effective_metadata(filepath, data or {})

    # 3. CONTEXTUAL HEALING (Mapping logic based on location)
    rel_path = os.path.relpath(filepath, ".")

    doc_type = effective_data.get("type") or get_type_from_path(filepath)
    category = effective_data.get("category", "platform")

    # Aggressive contextual mapping
    if "docs/adrs" in rel_path or "docs/30-architecture" in rel_path:
        category, doc_type = "architecture", "adr"
    elif "docs/changelog" in rel_path:
        category, doc_type = "changelog", "changelog"
    elif "runbooks/" in rel_path:
        category, doc_type = "runbooks", "runbook"
    elif "docs/policies" in rel_path or "docs/70-operations" in rel_path:
        category, doc_type = "compliance", "policy"
    elif "idp-tooling/" in rel_path:
        category = "platform"

    # 4. START RECONSTRUCTION
    # We use a skeleton based on the HEALED doc_type
    skeleton = cfg.get_skeleton(doc_type)
    if not skeleton and doc_type in [
        "policy",
        "runbook",
        "strategy",
        "implementation-plan",
        "report",
    ]:
        skeleton = cfg.get_skeleton("documentation")

    if not skeleton:
        skeleton = {
            "id": "",
            "title": "",
            "type": "documentation",
            "owner": OWNER,
            "status": "active",
        }

    # final_data = skeleton + effective_metadata
    new_data = copy.deepcopy(skeleton)
    for k, v in effective_data.items():
        if v not in [None, "", "unknown"]:
            if k in new_data and isinstance(new_data[k], dict) and isinstance(v, dict):
                new_data[k].update(v)
            else:
                new_data[k] = v

    # Re-apply healed category/type
    new_data["category"] = category
    new_data["type"] = doc_type
    if not new_data.get("title"):
        new_data["title"] = default_title

    # 5. ID ENFORCEMENT
    if filename_base in ["README", "metadata", "index"]:
        rel_dir = os.path.relpath(os.path.dirname(filepath), ".")
        if rel_dir == ".":
            new_id = "ROOT_README"
        else:
            prefix = (
                "HELM"
                if "gitops/helm" in rel_dir
                else (
                    "TOOL"
                    if "idp-tooling" in rel_dir
                    else ("ENV" if "envs" in rel_dir else "APPS")
                )
            )
            new_id = f"{prefix}_{os.path.basename(rel_dir).replace('-', '_').upper()}"
            if filename_base in ["index", "metadata"]:
                new_id = f"{new_id}_{filename_base.upper()}"

        current_id = str(new_data.get("id", "")).upper()
        if not current_id or current_id in ["README", "METADATA", "INDEX"]:
            new_data["id"] = new_id
    else:
        if not new_data.get("id"):
            new_data["id"] = filename_base

    # 6. VQ defaults (only when missing)
    vq_defaults = VQ_DEFAULTS_BY_TYPE.get(doc_type)
    if vq_defaults:
        vq_data = new_data.get("value_quantification")
        if not isinstance(vq_data, dict):
            vq_data = {}
        for key, value in vq_defaults.items():
            if key not in vq_data or vq_data[key] in [None, "", "unknown"]:
                vq_data[key] = value
        new_data["value_quantification"] = vq_data

    if (
        isinstance(new_data.get("value_quantification"), dict)
        and not new_data["value_quantification"]
    ):
        del new_data["value_quantification"]

    # 7. PRUNING (Dry Governance)
    # Remove fields from local sidecar if they match the parent EXACTLY
    parent_data = cfg.find_parent_metadata(filepath)
    if parent_data:
        # print(f"DEBUG: Pruning against parent: {parent_data.get('owner')}")
        for k in list(new_data.keys()):
            if k in ["id", "title", "type"]:
                continue  # Keep core identity fields
            if k in parent_data and new_data[k] == parent_data[k]:
                # print(f"DEBUG: Pruning redundant field: {k}")
                del new_data[k]

    # 8. Final Polish
    if "reliability" in new_data and isinstance(new_data["reliability"], dict):
        if not new_data["reliability"].get("observability_tier"):
            new_data["reliability"]["observability_tier"] = "bronze"

    # 9. Reconstruct and Save
    new_fm = platform_yaml_dump(new_data)
    if is_yaml:
        # Standard YAML sidecars should only have a leading marker, trailing marker signals a second document.
        new_content = f"---\n{new_fm}"
    else:
        # Markdown frontmatter MANDATES markers at both ends.
        new_content = f"---\n{new_fm}---\n\n{body.lstrip()}"

    new_content = re.sub(r"\n{3,}", "\n\n", new_content).strip() + "\n"

    if new_content != content:
        if dry_run:
            print(f"[DRY-RUN] Would standardize: {filepath}")
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Standardized: {filepath}")
    else:
        if dry_run:
            # print(f"[DRY-RUN] No changes needed: {filepath}")
            pass
        pass

    # CLOSED-LOOP GOVERNANCE: Inject metadata into associated K8s resources
    # CLOSED-LOOP GOVERNANCE: Inject metadata into associated K8s resources
    if filename_base == "metadata":
        inject_governance(filepath, new_data, dry_run=dry_run)


def inject_governance(sidecar_path, data, dry_run=False):
    """Propagates metadata values into associated values.yaml files."""
    base_dir = os.path.dirname(sidecar_path)
    candidates = []

    # Standalone K8s Manifests in current dir
    for f in os.listdir(base_dir):
        if (
            f.endswith((".yaml", ".yml"))
            and f != "metadata.yaml"
            and f != "metadata.yml"
        ):
            # Check if it looks like a K8s resource
            try:
                with open(os.path.join(base_dir, f), "r") as check_f:
                    if "apiVersion:" in check_f.read(1024):
                        candidates.append(os.path.join(base_dir, f))
            except:
                pass

    # ArgoCD Apps - Only walk and match if we are NOT already in the ArgoCD tree
    # to avoid oscillation between environment-level metadata and app-level metadata.
    argocd_dir = os.path.abspath(os.path.join(os.getcwd(), "gitops", "argocd", "apps"))
    if os.path.isdir(argocd_dir) and "gitops/argocd/apps" not in sidecar_path:
        target_name = os.path.basename(base_dir)
        for root, _, files in os.walk(argocd_dir):
            for f in files:
                is_match = False
                if target_name in f and f.endswith((".yaml", ".yml")):
                    if "gitops/helm" in sidecar_path and "apps/" not in root:
                        is_match = True
                    elif "apps/" in sidecar_path and "apps/" in root:
                        is_match = True

                if is_match:
                    candidates.append(os.path.join(root, f))

    gov_block = {
        "id": data.get("id"),
        "owner": data.get("owner"),
        "risk_profile": data.get("risk_profile"),
        "reliability": data.get("reliability"),
    }

    for cand in candidates:
        try:
            with open(cand, "r", encoding="utf-8") as f:
                v_content = f.read()

            v_docs = list(yaml.safe_load_all(v_content))
            if not v_docs:
                continue

            any_doc_updated = False
            updated_docs = []

            for doc in v_docs:
                if not isinstance(doc, dict):
                    updated_docs.append(doc)
                    continue

                # Check if change is needed for this specific document
                current_gov = doc.get("governance", {})
                current_ann = doc.get("metadata", {}).get("annotations", {})

                is_k8s = doc.get("apiVersion") and doc.get("kind")
                needs_update = False

                if is_k8s:
                    anno_id = current_ann.get("goldenpath.idp/id")
                    anno_owner = current_ann.get("goldenpath.idp/owner")
                    target_id = str(gov_block["id"])
                    target_owner = str(gov_block.get("owner", "unknown"))

                    if anno_id != target_id or anno_owner != target_owner:
                        # Priority check: If the file already has a specific ID and we are applying
                        # environment-level metadata, do not overwrite the specific ID.
                        is_env_metadata = "gitops/argocd/apps" in sidecar_path
                        if is_env_metadata and anno_id and anno_id != "None":
                            # Skip this file, it's already owned by a specific app
                            continue

                        needs_update = True
                        if "metadata" not in doc:
                            doc["metadata"] = {}
                        if "annotations" not in doc["metadata"]:
                            doc["metadata"]["annotations"] = {}
                        doc["metadata"]["annotations"]["goldenpath.idp/id"] = target_id
                        doc["metadata"]["annotations"]["goldenpath.idp/owner"] = (
                            target_owner
                        )
                else:
                    if current_gov != gov_block:
                        needs_update = True
                        doc["governance"] = gov_block

                if needs_update:
                    any_doc_updated = True

                updated_docs.append(doc)

            if any_doc_updated:
                header = "# Managed by scripts/standardize_metadata.py\n"
                if len(updated_docs) > 1:
                    new_v_content = header + platform_yaml_dump_all(updated_docs)
                else:
                    new_v_content = header + platform_yaml_dump(updated_docs[0])

                if new_v_content.strip() != v_content.strip():
                    if dry_run:
                        print(f"[DRY-RUN] Would inject governance into: {cand}")
                    else:
                        with open(cand, "w", encoding="utf-8") as f:
                            f.write(new_v_content.strip() + "\n")
                        print(
                            f"{'🏷️' if is_k8s else '💉'} {'Annotated' if is_k8s else 'Injected'} resource (Multi-doc aware): {cand}"
                        )
        except Exception as e:
            print(f"⚠️ Failed injection for {cand}: {e}")


def log_heartbeat_if_enabled(script_name: str) -> bool:
    if os.getenv("VQ_LOG_DISABLE", "").lower() in {"1", "true", "yes"}:
        return False
    try:
        from lib.vq_logger import log_heartbeat

        log_heartbeat(script_name)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Standardize metadata across the platform."
    )
    parser.add_argument(
        "targets", nargs="*", default=["."], help="Directories or files to scan"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without writing"
    )
    args = parser.parse_args()

    for target in args.targets:
        if not os.path.exists(target):
            print(f"⚠️ Warning: Target {target} not found.")
            continue

        if os.path.isfile(target):
            standardize_file(target, dry_run=args.dry_run)
            continue

        for root, dirs, files in os.walk(target):
            dirs[:] = [
                d
                for d in dirs
                if d not in [".git", ".gemini", "node_modules", "tmp", "__pycache__"]
            ]
            norm_root = os.path.relpath(root, ".")

            # Structural check: Create missing metadata.yaml in mandated zones
            path_parts = norm_root.split(os.sep)
            is_mandated = any(zone in norm_root for zone in SIDECAR_MANDATED_ZONES)

            if is_mandated and len(path_parts) >= 2:
                if "metadata.yaml" not in files and "metadata.yml" not in files:
                    sidecar_path = os.path.join(root, "metadata.yaml")
                    if args.dry_run:
                        print(f"[DRY-RUN] Would create missing sidecar: {sidecar_path}")
                    else:
                        print(f"🩹 Creating missing sidecar: {sidecar_path}")
                        with open(sidecar_path, "w") as f:
                            f.write("---\n# Placeholder\n---\n")
                    files.append("metadata.yaml")

            for file in files:
                is_md = file.endswith(".md") and file not in [
                    "DOC_INDEX.md",
                    "PLATFORM_HEALTH.md",
                ]
                is_meta = file in ["metadata.yaml", "metadata.yml"]
                if is_md or is_meta:
                    standardize_file(os.path.join(root, file), dry_run=args.dry_run)

    # Log Value Heartbeat (skip when disabled for deterministic runs)
    log_heartbeat_if_enabled("standardize_metadata.py")


if __name__ == "__main__":
    main()
