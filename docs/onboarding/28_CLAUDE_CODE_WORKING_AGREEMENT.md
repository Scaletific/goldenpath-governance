---
id: 28_CLAUDE_CODE_WORKING_AGREEMENT
title: Claude Code Working Agreement
type: guide
owner: platform-team
status: active
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 26_AI_AGENT_PROTOCOLS
  - 13_COLLABORATION_GUIDE
  - 24_PR_GATES
  - 27_TESTING_QUICKSTART
supersedes: []
superseded_by: []
tags: []
inheritance: {}
category: platform
supported_until: '2028-01-01'
version: '1.0'
breaking_change: false
---

# Claude Code Working Agreement — GoldenPath IDP

**Purpose:** Maximize the value of human-Claude collaboration by defining delegation patterns, communication norms, and repeatable commands.

**Companion to:** `docs/onboarding/26_AI_AGENT_PROTOCOLS.md` (governance rules). This doc covers *how to work together*, not what's allowed.

---

## 1) Delegation Principles

| Instead of... | Try... |
|---|---|
| Pre-diagnosing the bug, then asking Claude to apply the fix | "The streaming response feels janky — figure out why and fix it" |
| Breaking work into 5 numbered steps | "Add frontend test coverage for the RAG UI components" |
| Asking one question at a time | "Fix the flaky tests, wire them into CI, and update the session capture" |
| Explaining where every file is | Giving the symptom or goal — Claude will find the files |

**Rule of thumb:** Describe the *outcome*, not the *procedure*. Claude will propose a plan for non-trivial work and ask before making architectural choices.

## 2) When to Scope vs. When to Let Go

| Scope tightly when... | Let Claude drive when... |
|---|---|
| You have a specific design preference | You want the idiomatic solution |
| The change is in a sensitive area (IaC, auth, governance) | It's tests, docs, refactoring, or frontend polish |
| You need it done a specific way for reasons Claude can't see | You'd accept any correct solution |

## 3) Feedback Shortcuts

These short commands course-correct without long explanations:

- **"stop"** — Halt current approach, wait for new direction
- **"wrong direction"** — Scrap the approach, propose an alternative
- **"simpler"** — Over-engineered, reduce complexity
- **"just do it"** — Stop planning/asking, execute directly
- **"print to screen first"** — Show the output before writing to disk
- **"commit and push, no PR"** — Exactly what it says
- **Screenshot + short description** — For UI bugs, paste the image and say what's wrong

## 4) Repeatable Command Patterns

### Start of session

```
"Check the branch state, read the latest session summary, and tell me where we left off"
```

### Feature implementation

```
"Implement <feature>. Follow TDD — write tests first, make them pass, then run make quality-gate"
```

### Bug triage

```
"<paste error or screenshot>. Find the root cause and fix it."
```

### Test sweep

```
"Run all tests — Python unit, backend API, frontend Vitest, and TypeScript check. Report failures."
```

### PR creation

```
"Commit everything, push, and create a PR to development with the standard template"
```

### Code review

```
"Review PR #<number> — check for governance compliance, test coverage, and contract alignment"
```

### Broad refactor

```
"Rename <X> to <Y> across the entire codebase, update all tests and imports"
```

### Codebase exploration

```
"How does <system> work? Trace the data flow from <entry point> to <output>"
```

### End of session

```
"Update session capture and session summary with what we did today"
```

## 5) What Claude Tracks Automatically

- **Memory across sessions** — Patterns, mistakes, architecture facts are persisted in `.claude/` memory files
- **Todo progress** — Complex tasks show a live checklist in the status line
- **Plan mode** — For non-trivial work, Claude proposes a plan before writing code

## 6) Maximizing Parallelism

Claude can run multiple operations simultaneously. Phrase requests to enable this:

**Sequential (slower):** "Check if tests pass. If they do, update the docs."

**Parallel (faster):** "Run the tests and update the docs" — Claude runs both at once, handles dependencies internally.

**Fan-out:** "Investigate why the graph ingest, query CLI, and RAG agent tests are failing" — Claude dispatches three parallel research agents.

## 7) Things Claude Won't Do Without Asking

Per `26_AI_AGENT_PROTOCOLS.md` and built-in safety:

- Merge PRs, force-push, delete branches
- Apply Terraform, modify governance policies
- Commit (unless explicitly asked)
- Push to remote (unless explicitly asked)

Override with explicit instruction: "commit and push" or "force-push to the feature branch."
