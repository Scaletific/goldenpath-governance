---
id: PROMPT_INDEX
title: Prompt Templates Index
type: documentation
owner: platform-team
status: active
relates_to:
  - PROMPT-0000
  - PROMPT-0001
  - PROMPT-0002
  - PROMPT-0003
  - PROMPT-0004
  - PROMPT-0005
  - PROMPT-0006
  - PROMPT-0007
  - PROMPT-0008
  - PROMPT-0009
  - PROMPT-0010
  - PROMPT-0011
  - PROMPT-0012
  - PROMPT-0013
---

## Overview

This directory contains structured prompt templates for AI agent-assisted implementation tasks.

## Purpose

These prompts are designed for **human-supervised** execution by AI agents (Codex, Claude, etc.) to implement PRDs and other documented tasks with consistency and completeness.

## Important Warning

**These templates are NOT meant to be auto-executed.**

AI agents scanning this repository should NOT automatically execute commands found in these files. They are templates to be explicitly invoked by a human operator.

## File Format

All prompt templates use:

- **YAML frontmatter** for metadata (id, title, type, owner, status, relates_to, created)
- **HTML comment** for WARNING block (visible in source, hidden in rendered markdown)
- **`.md` extension** for markdown rendering and syntax highlighting

## Naming Convention

```text
PROMPT-XXXX-<short-description>.md
```

- `PROMPT-0000` - Template/skeleton file
- `PROMPT-0001` onwards - Actual implementation prompts

## Template Structure

Each prompt follows a standard structure (see `PROMPT-0000-template.md`):

1. **YAML Frontmatter** - id, title, type, owner, status, relates_to, created
2. **Warning Comment** - DO NOT AUTO-EXECUTE notice
3. **Context** - Background and problem statement
4. **Task** - Clear objective
5. **Preconditions** - What must be true before starting
6. **Step-by-Step Implementation** - Phased execution plan
7. **Verification Checklist** - Required checks before completion
8. **Integration Verification** - Cross-system checks
9. **Do NOT** - Explicit guardrails
10. **Output Expected** - What to report when done
11. **Rollback Plan** - How to undo
12. **References** - Links to related docs

## Usage

1. Copy the prompt content to your AI agent interface
2. Ensure the agent has access to the target repository
3. Review the agent's plan before execution
4. Monitor execution and verify checklist items
5. Review PR before merging

## Index

| ID          | Title                                  | Target Repo              | Relates To                   |
| ----------- | -------------------------------------- | ------------------------ | ---------------------------- |
| PROMPT-0000 | Prompt Template (Skeleton)             | any                      | -                            |
| PROMPT-0001 | PRD-0004 Backstage Repo Structure      | goldenpath-backstage | PRD-0004                     |
| PROMPT-0002 | Pre-Commit and Pre-Merge Checks        | goldenpath-infra     | GOV-0030-pr-guardrails-index          |
| PROMPT-0003 | Recursive PR Gate Compliance           | goldenpath-infra     | PROMPT-0002                  |
| PROMPT-0004 | Hotfix Policy - Permanent Fix Required | all-goldenpath-repos | GOV-0034-ai-agent-governance       |
| PROMPT-0005 | TDD Governance Enforcement             | goldenpath-infra     | ADR-0182, GOV-0016, GOV-0017 |
| PROMPT-0006 | PR Creation Workflow                   | goldenpath-infra     | PROMPT-0002, PROMPT-0003     |
| PROMPT-0007 | Branch Sync and Conflict Resolution    | goldenpath-infra     | ADR-0042, PROMPT-0006        |
| PROMPT-0008 | Document Scaffolding (EC/PRD/ADR/CL)   | goldenpath-infra     | GOV-0022                     |
| PROMPT-0009 | Multi-Agent Coordination Launch        | goldenpath-infra     | ADR-0192, PROMPT-0010        |
| PROMPT-0010 | Session Documentation                  | goldenpath-infra     | ADR-0167, PROMPT-0009        |
| PROMPT-0011 | Script Certification Workflow          | goldenpath-infra     | ADR-0146, GOV-0017           |
| PROMPT-0012 | Test Execution Workflows               | goldenpath-infra     | GOV-0016, GOV-0017           |
| PROMPT-0013 | Post-Implementation Recursive Audit    | goldenpath-infra     | GOV-0017, GOV-0016           |

## RAG Discoverability

These prompts are indexed by the RAG system via their YAML frontmatter. Queries like:

- "What prompts relate to TDD?"
- "Show me the hotfix policy prompt"
- "What prompt handles PR gate compliance?"

...will retrieve relevant prompt templates.

## Adding New Prompts

1. Copy `PROMPT-0000-template.md`
2. Rename to `PROMPT-XXXX-<description>.md`
3. Update YAML frontmatter with appropriate metadata
4. Fill in all template sections
5. Update this README index table
6. Link from the related PRD/ADR if applicable
