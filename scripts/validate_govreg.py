#!/usr/bin/env python3
"""
---
id: SCRIPT-0040
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0040.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Governance Registry Integrity Validator
Achievement: Enforces the ledger contract on the governance-registry branch by validating:
             1. Required folder structure (no random files)
             2. Chain-of-custody metadata headers in all artifacts
             3. Prevents manual commits without proper provenance
Value: Maintains the governance-registry as a high-integrity audit log, preventing drift
Relates-To: ADR-0145, RB-0028
"""
import re
import sys
import yaml
from pathlib import Path

# Schema-driven configuration
SCHEMA_PATH = (
    Path(__file__).parent.parent / "schemas" / "governance" / "govreg.schema.yaml"
)


def load_schema() -> dict:
    """Load validation rules from the governance registry schema."""
    if not SCHEMA_PATH.exists():
        print(
            f"[govreg-validate] FATAL: Schema not found at {SCHEMA_PATH}",
            file=sys.stderr,
        )
        sys.exit(2)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        try:
            # Parse the YAML, skip frontmatter if present
            content = f.read()
            # Remove frontmatter if present
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2]

            schema = yaml.safe_load(content)
            return schema.get("properties", {})
        except yaml.YAMLError as e:
            print(f"[govreg-validate] FATAL: Invalid schema YAML: {e}", file=sys.stderr)
            sys.exit(2)


# Load configuration from schema
SCHEMA_CONFIG = load_schema()

# Extract validation rules
ALLOWED_TOP_LEVEL = set(SCHEMA_CONFIG.get("allowed_top_level", {}).get("default", []))
REQUIRED_DIRS = SCHEMA_CONFIG.get("required_dirs", {}).get("default", [])
REQUIRED_ENV_SUBDIRS = SCHEMA_CONFIG.get("required_env_subdirs", {}).get("default", [])

markdown_config = SCHEMA_CONFIG.get("markdown", {}).get("properties", {})
frontmatter_config = markdown_config.get("frontmatter", {}).get("properties", {})
REQUIRED_KEYS = frontmatter_config.get("required_keys", {}).get("default", [])

# Basic frontmatter extractor (--- ... ---)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def fail(msg: str) -> None:
    print(f"[govreg-validate] FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"[govreg-validate] WARN: {msg}", file=sys.stderr)


def is_markdown(p: Path) -> bool:
    return p.suffix.lower() in {".md", ".markdown"}


def validate_top_level(root: Path) -> None:
    """Ensure only allowed paths exist at the root of the registry branch."""
    for p in root.iterdir():
        name = p.name
        if name not in ALLOWED_TOP_LEVEL:
            fail(f"Unexpected top-level path in governance-registry: {name}")


def validate_env_layout(root: Path) -> None:
    """Ensure every environment has the required latest/ and history/ folders."""
    for required_dir in REQUIRED_DIRS:
        dir_path = root / required_dir
        if not dir_path.exists():
            fail(f"Missing required directory: {required_dir}/")

    env_root = root / "environments"
    if not env_root.exists():
        return  # Already caught by required_dirs check

    for env_dir in env_root.iterdir():
        if not env_dir.is_dir():
            fail(f"Unexpected non-directory under environments/: {env_dir.name}")

        for subdir_name in REQUIRED_ENV_SUBDIRS:
            subdir = env_dir / subdir_name
            if not subdir.exists():
                fail(f"Missing {env_dir.name}/{subdir_name}/")


def validate_frontmatter(md_file: Path) -> None:
    """Validate that the markdown file contains all required chain-of-custody fields."""
    content = md_file.read_text(encoding="utf-8", errors="replace")
    m = FRONTMATTER_RE.match(content)
    if not m:
        fail(f"Missing YAML frontmatter in: {md_file}")

    fm = m.group(1)
    # Simple presence checks (string-based) to keep this dependency-free
    for k in REQUIRED_KEYS:
        if k not in fm:
            fail(f"Missing required key '{k}' in frontmatter for: {md_file}")


def validate_markdown_headers(root: Path) -> None:
    """Validate frontmatter in all markdown artifacts under latest/ and history/."""
    env_root = root / "environments"
    for md in env_root.rglob("*.md"):
        # Only enforce under environments/*/(latest|history)/**
        parts = md.parts
        if "environments" in parts and ("latest" in parts or "history" in parts):
            validate_frontmatter(md)

    # Validate unified dashboard if present
    dash = root / "UNIFIED_DASHBOARD.md"
    if dash.exists():
        validate_frontmatter(dash)
    else:
        warn("UNIFIED_DASHBOARD.md not found (ok if you haven't enabled it yet)")


def main() -> None:
    root = Path(".").resolve()

    print("[govreg-validate] Validating governance registry integrity...")
    print(f"[govreg-validate] Using schema: {SCHEMA_PATH}")

    validate_top_level(root)
    validate_env_layout(root)
    validate_markdown_headers(root)

    print("[govreg-validate] ✅ OK: governance registry integrity validated")


if __name__ == "__main__":
    main()
