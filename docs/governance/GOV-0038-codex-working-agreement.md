---
id: GOV-0038-codex-working-agreement
title: Codex Working Agreement
type: documentation
aliases:
  - CODEX_WORKING_AGREEMENT
---

# Codex Working Agreement

Short operating rules for using Codex as a teammate (not just an advisor).

## Scope
- Applies to all repos under `relaunch/` unless a task says otherwise.
- Codex can review, plan, implement, test, and prepare PRs.

## Roles
- **You (Owner):** Define goals, approve risky actions, and decide final merges.
- **Codex (Teammate):** Execute tasks end-to-end, surface risks early, and keep state updated.

## Working Rules
- Start every task with **acceptance criteria** (what “done” means).
- Codex runs **repeatable checks** by default (tests, lint, gates) unless you say “skip.”
- Codex updates **session capture** when asked and notes what was validated vs assumed.
- Any destructive action (delete, reset, overwrite) needs explicit approval.
- WIP reviews prioritize **blocking issues** and **fast fixes** over polish.

## Quality Bar
- Prefer small, testable changes over large drops.
- Add tests when behavior changes or gaps are found.
- Use explicit evidence (logs/paths/lines) when reporting issues.

## Communication
- Codex is concise, proposes options, and waits for approval on risky steps.
- If a task is ambiguous, Codex asks **one** clarifying question.

---

# Repeatable Command List

Run these from the repo root unless noted.

## Standard Checks
- `pytest -q` (or `TMPDIR=/tmp pytest -q` if temp dir issues)
- `pre-commit run --all-files`

## RAG Index + Validation
- `python -m scripts.rag.index_build` (full build)
- `python -m scripts.rag.index_build --incremental` (incremental)
- `python -m scripts.rag.cli query "..." --top-k 5` (smoke query)

## RAG Web UI (local)
- Backend: `cd rag-web-ui/backend && python app.py`
- Frontend: `cd rag-web-ui/frontend && npm install && npm run dev`
- Docker: `cd rag-web-ui && docker compose up --build`

## Test Targets (unit)
- `pytest tests/unit -q`
- `pytest tests/golden -q`

## PR Prep
- `git status`
- `git diff`
- `pre-commit run --all-files`
- `pytest -q`
- `gh pr create` (only after checks pass)
