#!/usr/bin/env bash
# ---
# id: check_session_writer
# title: Check Session Writer Ran (ADR-0192)
# type: script
# lifecycle: active
# owner: platform-team
# maturity: 2
# domain: governance
# test_path: tests/scripts/test_check_session_writer.bats
# risk_profile:
#   production_impact: none
#   security_risk: none
#   coupling_risk: low
# test:
#   runner: bats
#   command: bats tests/scripts/test_check_session_writer.bats
#   evidence: test-results/check_session_writer.xml
# dry_run:
#   supported: true
# supported_until: 2028-01-01
# breaking_change: false
# ---
#
# check_session_writer.sh — Pre-commit hook (Layer 2: Catch)
#
# Detects new agent reports without matching session capture entries.
# If agent-reports/ has new/modified files staged for commit but no
# session_capture/ file is also staged, the commit is blocked.
#
# This enforces ADR-0192's Session Writer protocol:
#   Workers write reports → SW consolidates → then commit.
#
# Usage: Called by pre-commit (see .pre-commit-config.yaml)
#   Or run directly: bash scripts/check_session_writer.sh

set -euo pipefail

# Check for staged agent report files (new or modified)
STAGED_REPORTS=$(git diff --cached --name-only --diff-filter=AM -- 'agent-reports/*.md' | grep -v 'README.md' || true)

if [ -z "$STAGED_REPORTS" ]; then
    # No agent reports staged — nothing to check
    exit 0
fi

# Count staged reports
REPORT_COUNT=$(echo "$STAGED_REPORTS" | wc -l | tr -d ' ')

# Check for staged session capture files
STAGED_CAPTURES=$(git diff --cached --name-only --diff-filter=AM -- 'session_capture/*.md' || true)

if [ -z "$STAGED_CAPTURES" ]; then
    echo ""
    echo "============================================================"
    echo "  SESSION WRITER NOT RUN — ${REPORT_COUNT} orphaned agent report(s)"
    echo "============================================================"
    echo ""
    echo "  Staged agent reports:"
    echo "$STAGED_REPORTS" | sed 's/^/    /'
    echo ""
    echo "  But no session_capture/*.md file is staged."
    echo ""
    echo "  Per ADR-0192, you must run the Session Writer (SW) agent"
    echo "  to consolidate agent reports before committing."
    echo ""
    echo "  Quick fix:"
    echo "    1. Launch SW agent to read reports and write session capture"
    echo "    2. git add session_capture/<new-file>.md"
    echo "    3. git add session_summary/agent_session_summary.md"
    echo "    4. Retry your commit"
    echo ""
    echo "============================================================"
    exit 1
fi

# Both reports and captures are staged — check passes
echo "Session Writer check: ${REPORT_COUNT} report(s) + session capture staged. OK."
exit 0
