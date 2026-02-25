#!/usr/bin/env python3
"""
---
id: SCRIPT-0041
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/unit/test_validate_metadata.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: PR Quality Gate & Structural Validator
Achievement: Enforces schema compliance and mandatory sidecar presence in core directories.
             Blocks non-compliant PRs to prevent "Dark Infrastructure" from entering the platform.
Value: Guarantees high-fidelity metadata for every platform resource, ensuring ownership
       and risk data are always present for automated reporting.
"""
import os
import sys
import yaml
import re

# Add lib to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
from metadata_config import MetadataConfig

cfg = MetadataConfig()

# Directories where metadata.yaml is MANDATORY in every direct subdirectory
SIDECAR_MANDATED_ZONES = ["gitops/helm", "idp-tooling", "envs", "apps"]


def extract_metadata(filepath):
    """
    Extracts and parses metadata from a markdown frontmatter or a standalone YAML file.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return None, f"Read error: {e}"

    if filepath.endswith(".yaml") or filepath.endswith(".yml"):
        try:
            # Handle possible multiple documents (e.g. if --- is used as a separator)
            data_iterator = yaml.safe_load_all(content)
            for data in data_iterator:
                if data:  # Return the first non-empty document
                    return data, None
            return None, "Empty YAML file"
        except yaml.YAMLError as e:
            return None, f"Invalid YAML: {e}"

    # Default to Markdown Frontmatter logic
    if not content.startswith("---"):
        return None, "Missing frontmatter (must start with ---)"

    try:
        # Extract content between first and second ---
        frontmatter_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not frontmatter_match:
            return None, "Malformed or unterminated frontmatter"

        raw_frontmatter = frontmatter_match.group(1)
        # Strip HTML comments to allow automated markers like <!-- ADR_RELATE_START -->
        clean_frontmatter = re.sub(r"<!--.*?-->", "", raw_frontmatter)
        data = yaml.safe_load(clean_frontmatter)
        return data, None
    except yaml.YAMLError as e:
        return None, f"Invalid YAML: {e}"


def validate_schema(data, filepath):
    """
    Validates the parsed data against the schema.
    """
    errors = []

    # 0. Inheritance & Safety Valve
    effective_data = cfg.get_effective_metadata(filepath, data)
    is_exempt = effective_data.get("exempt") is True
    doc_type = effective_data.get("type", "documentation")

    # Leak Protection: Block exempt scratchpads from production
    if is_exempt and ("envs/prod/" in filepath or "apps/prod" in filepath):
        errors.append(
            "❌ LEAK PROTECTION: Resources marked as 'exempt: true' cannot be deployed to Production environments."
        )

    # 1. Check Required Fields from Schema
    schema = cfg.get_schema(doc_type)
    if not schema and doc_type in [
        "policy",
        "runbook",
        "strategy",
        "implementation-plan",
        "report",
    ]:
        # These all share the general documentation schema
        schema = cfg.get_schema("documentation")

    if schema:
        required_fields = schema.get("required", [])
    else:
        # Fallback to legacy common fields if no specific schema found at all
        required_fields = [
            "id",
            "type",
            "owner",
            "status",
            "risk_profile",
            "reliability",
            "lifecycle",
        ]

    for field in required_fields:
        # Skip detail fields for exempt resources
        if is_exempt and field in ["risk_profile", "reliability", "lifecycle"]:
            continue

        if field not in effective_data:
            errors.append(
                f"Missing required field: '{field}' (Inherited check included)"
            )
        elif field in ["risk_profile", "reliability"] and not isinstance(
            effective_data[field], dict
        ):
            errors.append(f"Field '{field}' must be a dictionary")

    # 2. Deep Validation against Schema & Enums
    for field, value in effective_data.items():
        field_errors = cfg.validate_field(doc_type, field, value)
        for err in field_errors:
            errors.append(err)

    # 3. ID-Filename/Path Checks (Logic preserved as it's structural)
    if "id" in data:
        filename = os.path.basename(filepath)
        filename_base = os.path.splitext(filename)[0]
        doc_id = str(data["id"])

        if filename == "metadata.yaml" or filename == "metadata.yml":
            # For standalone metadata, ID should relate to directory or be descriptive
            # We don't strictly enforce ID-dirname match yet, but we ensure it's not empty
            if not doc_id:
                errors.append("ID field cannot be empty in metadata.yaml")
        elif filename_base in ["README", "index"]:
            if doc_id.upper() in ["README", "INDEX"]:
                errors.append(
                    f"{filename} files must have a descriptive ID (not just '{doc_id}')"
                )
        elif doc_id != filename_base:
            # Standardized ADR/CL ID pattern matching ADR-XXXX/CL-XXXX prefixes
            is_adr_match = re.match(
                r"^ADR-\d{4}$", doc_id
            ) and filename_base.startswith(doc_id + "-")
            is_cl_match = re.match(r"^CL-\d{4}$", doc_id) and filename_base.startswith(
                doc_id + "-"
            )
            is_rb_match = re.match(r"^RB-\d{4}$", doc_id) and filename_base.startswith(
                doc_id + "-"
            )
            is_sec_match = re.match(
                r"^SEC-\d{4}$", doc_id
            ) and filename_base.startswith(doc_id + "-")
            is_cnt_match = re.match(r"^CNT-\d{3}$", doc_id) and (
                filename_base == doc_id or filename_base.startswith(doc_id + "-")
            )

            if not (
                is_adr_match
                or is_cl_match
                or is_rb_match
                or is_sec_match
                or is_cnt_match
            ):
                errors.append(
                    f"ID mismatch: '{doc_id}' found in header but filename is '{filename_base}'"
                )

    if "owner" in data:
        if not data["owner"]:
            errors.append("Owner field cannot be empty")

    return errors


def verify_injection(base_dir, expected_id):
    """Verifies that the metadata ID has been injected into at least one deployment file."""
    candidates = []
    # 1. Check values.yaml and standalone K8s manifests
    for f in os.listdir(base_dir):
        if f.endswith((".yaml", ".yml")) and f not in ["metadata.yaml", "metadata.yml"]:
            try:
                with open(os.path.join(base_dir, f), "r") as check_f:
                    head = check_f.read(1024)
                    if "apiVersion:" in head or "governance:" in head:
                        candidates.append(os.path.join(base_dir, f))
            except:
                pass

    # 2. Check subdirectories
    for sub in ["values", "deploy"]:
        sub_dir = os.path.join(base_dir, sub)
        if os.path.isdir(sub_dir):
            for root, _, files in os.walk(sub_dir):
                for f in files:
                    if f.endswith((".yaml", ".yml")):
                        candidates.append(os.path.join(root, f))

    # 3. ArgoCD Application Manifests
    if "envs/" not in base_dir:
        argocd_dir = os.path.abspath(
            os.path.join(os.getcwd(), "gitops", "argocd", "apps")
        )
        if os.path.isdir(argocd_dir):
            target_name = os.path.basename(base_dir)
            for root, _, files in os.walk(argocd_dir):
                for f in files:
                    is_match = False
                    if target_name in f and f.endswith((".yaml", ".yml")):
                        if "gitops/helm" in base_dir and "apps/" not in root:
                            is_match = True
                        elif "apps/" in base_dir and "apps/" in root:
                            is_match = True

                    if is_match:
                        candidates.append(os.path.join(root, f))

    # If no candidates found, and it's not a Helm chart, we treat it as documentation-only.
    if not candidates:
        is_helm = os.path.exists(os.path.join(base_dir, "Chart.yaml"))
        return not is_helm

    for cand in candidates:
        if not os.path.exists(cand):
            continue
        try:
            with open(cand, "r", encoding="utf-8") as f:
                content = f.read()

            # Pattern 1: Inline ID (K8s manifests, ArgoCD apps)
            if (
                f"id: {expected_id}" in content
                or f'id: "{expected_id}"' in content
                or f"goldenpath.idp/id: {expected_id}" in content
            ):
                return True

            # Pattern 2: Helm values governance block (e.g., 'governance:\n  id: HELM_LOKI_METADATA')
            # This handles the gitops/helm/*/values/*.yaml pattern
            if "governance:" in content:
                # Quick check before expensive YAML parse
                if f"id: {expected_id}" in content:
                    # Verify it's within a governance block by doing lightweight validation
                    lines = content.split("\n")
                    in_governance_block = False
                    for line in lines:
                        if line.strip().startswith("governance:"):
                            in_governance_block = True
                        elif in_governance_block and line.strip().startswith("id:"):
                            if expected_id in line:
                                return True
                        elif (
                            in_governance_block
                            and line
                            and not line.startswith(" ")
                            and not line.startswith("\t")
                        ):
                            # Exited the governance block (back to root level)
                            in_governance_block = False
        except:
            pass
    return False


def scan_directory(target_path):
    """
    Scans directory for markdown and metadata.yaml files and validates them.
    Also enforces presence of sidecars in mandated zones.
    """
    fail_count = 0
    pass_count = 0

    print(f"🔍 Scanning {target_path} for metadata compliance...")

    files_to_check = []
    # Structural check tracker: { 'path/to/dir': has_sidecar }
    mandatory_checks = {}

    if os.path.isfile(target_path):
        files_to_check = [target_path]
    else:
        for root, dirs, files in os.walk(target_path):
            # Skip hidden and ignored dirs
            dirs[:] = [
                d for d in dirs if not d.startswith(".") and d not in ["node_modules"]
            ]

            # Normalize root for zone checking
            norm_root = os.path.relpath(root, ".")
            if norm_root == ".":
                norm_root = ""

            # Identify if this directory is in a Mandated Zone
            # Example: norm_root = 'gitops/helm/kong' -> parent = 'gitops/helm'
            parent_dir = os.path.dirname(norm_root.rstrip("/"))
            if parent_dir in SIDECAR_MANDATED_ZONES:
                mandatory_checks[norm_root] = False

            for file in files:
                # Check .md files
                if file.endswith(".md") and file not in [
                    "DOC_INDEX.md",
                    "PLATFORM_HEALTH.md",
                ]:
                    files_to_check.append(os.path.join(root, file))

                # Check metadata.yaml sidecars
                if file == "metadata.yaml" or file == "metadata.yml":
                    files_to_check.append(os.path.join(root, file))
                    if norm_root in mandatory_checks:
                        mandatory_checks[norm_root] = True

                # Check SecretRequest YAMLs
                if "catalogs/secrets" in norm_root and file.endswith(".yaml"):
                    files_to_check.append(os.path.join(root, file))

    # 1. Validate Existing Files
    for filepath in files_to_check:
        print(f"DEBUG: Checking {filepath}")
        data, error = extract_metadata(filepath)

        if error:
            print(f"❌ [MISSING/MALFORMED] {filepath}: {error}")
            fail_count += 1
            continue

        validation_errors = validate_schema(data, filepath)
        if validation_errors:
            print(f"❌ [INVALID] {filepath}")
            for err in validation_errors:
                print(f"   - {err}")
            fail_count += 1
        else:
            pass_count += 1

    # 2. Check for Missing Mandatory Sidecars
    for dir_path, has_sidecar in mandatory_checks.items():
        if not has_sidecar:
            print(f"❌ [MISSING] {dir_path}/metadata.yaml (Mandatory in this zone)")
            fail_count += 1
        else:
            # CLOSED-LOOP VERIFICATION: Ensure sidecar data is actually injected
            sidecar_path = os.path.join(dir_path, "metadata.yaml")
            if not os.path.exists(sidecar_path):
                sidecar_path = os.path.join(dir_path, "metadata.yml")

            data, _ = extract_metadata(sidecar_path)
            if data and "id" in data:
                if not verify_injection(dir_path, data["id"]):
                    print(
                        f"❌ [INJECTION FAILURE] {dir_path}: Sidecar ID '{data['id']}' not found in deployment files"
                    )
                    fail_count += 1

    print("-" * 40)
    print(f"✅ Passed: {pass_count}")
    print(f"❌ Failed: {fail_count}")

    if fail_count > 0:
        return 1

    # Log Value Heartbeat on complete success
    try:
        from lib.vq_logger import log_heartbeat

        log_heartbeat("validate_metadata.py")
    except:
        pass

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        target_dir = "."
    else:
        target_dir = sys.argv[1]

    sys.exit(scan_directory(target_dir))
