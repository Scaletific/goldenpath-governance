#!/usr/bin/env python3
"""
---
id: SCRIPT-0010
type: script
owner: platform-team
status: active
maturity: 3
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0010.py
  evidence: ci
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Emoji Policy Enforcer
Achievement: Scans the repository for non-approved emojis and removes them or alerts.
             Strictly forbids ANY emojis in ADRs, Policies, and Schemas.
Value: Ensures professional, unambiguous documentation as per the Emoji Usage Policy.
"""
import os
import re
import argparse

# Approved Set (from GOV-0050-emoji-policy.md)
APPROVED_EMOJIS = [
    "🔴",
    "🟡",
    "🔵",
    "⚫",
    "⚠️",
    "🚫",
    "✅",
    "🔒",
    "🔬",
    "🧪",
    "🧭",
    "📌",
    "🚀",
    "🛡️",
    "🏥",
    "🏆",
    "📈",
    "🏛️",
    "📊",
    "🏗️",
    "💎",
    "🤖",
    "🎯",
    "⭐",
    "⭐⭐",
    "⭐⭐⭐",
    "⭐⭐⭐⭐",
    "⭐⭐⭐⭐⭐",
    "📘",
    "📖",
    "⚡",
    "🚧",
    "🛠️",
]

# Authoritative directories (No emojis allowed at all)
NO_EMOJI_ROOTS = ["docs/adrs", "docs/governance", "schemas", "docs/security"]

# Regex to find all emojis (broad range)
EMOJI_REGEX = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f300-\U0001f5ff"  # symbols & pictographs
    "\U0001f680-\U0001f6ff"  # transport & map symbols
    "\U0001f1e0-\U0001f1ff"  # flags
    "\u2700-\u27bf"  # dingbats
    "\u2b50"  # star
    "\u2600-\u26ff"  # misc symbols
    "\u2300-\u23ff"  # technical
    "\U0001f900-\U0001f9ff"  # supplemental symbols
    "\u200d"  # zero width joiner
    "\ufe0f"  # variation selector
    "]+",
    flags=re.UNICODE,
)


def scan_file(filepath, dry_run=False):
    is_authoritative = any(
        filepath.startswith(root) or root in filepath for root in NO_EMOJI_ROOTS
    )
    # Special case: The policy itself is allowed to have them for reference
    if "GOV-0050-emoji-policy.md" in filepath:
        return 0

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0

    found_emojis = EMOJI_REGEX.findall(content)
    if not found_emojis:
        return 0

    new_content = content
    violations = []

    # VQ Indicators are allowed everywhere as core platform standards
    VQ_INDICATORS = ["🔴", "🟡", "🔵", "⚫"]

    for emoji in set(found_emojis):
        # Skip check for VQ indicators
        if emoji in VQ_INDICATORS:
            continue

        # 1. Authoritative check
        if is_authoritative:
            violations.append(f"Emoji '{emoji}' not allowed in authoritative document.")
            new_content = new_content.replace(emoji, "")
        # 2. Approved set check for non-authoritative
        elif emoji not in APPROVED_EMOJIS:
            violations.append(f"Emoji '{emoji}' is not in the approved set.")
            new_content = new_content.replace(emoji, "")

    if violations:
        print(f"❌ Policy Violation in {filepath}:")
        for v in violations:
            print(f"   - {v}")

        if not dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("   ✅ [FIXED] Removed non-compliant emojis.")
        return len(violations)

    return 0


def main():
    parser = argparse.ArgumentParser(description="Enforce Emoji Usage Policy.")
    parser.add_argument(
        "--root", default=".", help="Directory to scan (ignored if files provided)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Don't apply changes")
    parser.add_argument("files", nargs="*", help="Specific files to scan")
    args = parser.parse_args()

    violation_count = 0
    file_count = 0

    if args.files:
        for filepath in args.files:
            if os.path.isfile(filepath) and filepath.endswith((".md", ".yaml", ".yml")):
                violation_count += scan_file(filepath, args.dry_run)
                file_count += 1
    else:
        for root, _, files in os.walk(args.root):
            if ".git" in root or "node_modules" in root:
                continue

            for file in files:
                if file.endswith((".md", ".yaml", ".yml")):
                    filepath = os.path.join(root, file)
                    violation_count += scan_file(filepath, args.dry_run)
                    file_count += 1

    print("-" * 40)
    print(f"Scan complete. Files checked: {file_count}")
    print(f"Total violations found/fixed: {violation_count}")


if __name__ == "__main__":
    main()
