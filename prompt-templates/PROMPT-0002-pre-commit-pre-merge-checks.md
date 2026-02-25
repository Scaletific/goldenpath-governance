---
id: PROMPT-0002
title: Pre-Commit and Pre-Merge Checks Reference
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-infra
relates_to:
  - GOV-0030-pr-guardrails-index
  - pre-commit-config
created: 2026-01-22
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are an AI agent assisting with code contributions to the Goldenpath IDP
infrastructure repository. Before committing or creating a PR, ensure all
governance checks pass.

## Context

This repository has strict governance controls enforced via:

- Pre-commit hooks (automatic on git commit)
- CI workflows (run on PR creation)
- Session documentation requirements (for critical paths)

Failing to follow these will result in blocked PRs and CI failures.

## PRE-COMMIT HOOKS (Automatic on git commit)

### Standard Hooks

| Hook                | Purpose                       | Files |
| ------------------- | ----------------------------- | ----- |
| end-of-file-fixer   | Ensure files end with newline | All   |
| trailing-whitespace | Remove trailing whitespace    | All   |
| terraform_fmt       | Format Terraform files        | *.tf  |
| markdownlint        | Lint markdown files           | *.md  |
| gitleaks            | Detect secrets/credentials    | All   |

### Auto-Healing Hooks

| Hook                       | Purpose                     | Files            |
| -------------------------- | --------------------------- | ---------------- |
| doc-metadata-autofix       | Standardize doc frontmatter | docs/**/*.md     |
| emoji-enforcer             | Check emoji policy          | `*.md`, `*.yaml` |
| generate-adr-index         | Regenerate ADR index        | Always runs      |
| generate-script-index      | Regenerate script index     | Always runs      |
| generate-workflow-index    | Regenerate workflow index   | Always runs      |
| generate-script-matrix     | Regenerate script matrix    | Always runs      |
| validate-script-governance | Validate script metadata    | scripts/*        |

## HEALING SCRIPTS (Run manually when needed)

```bash
python3 scripts/standardize_metadata.py docs/
python3 scripts/generate_adr_index.py
python3 scripts/generate_script_index.py
python3 scripts/generate_workflow_index.py
python3 scripts/generate_script_matrix.py
```

## TERRAFORM VALIDATION (Required for .tf changes)

Before committing Terraform changes, validate ALL environments - not just dev.
The CI will validate all envs, so catch errors locally first.

```bash
# Validate all environments (must pass before PR)
for env in dev test staging prod; do
  echo "Validating envs/$env..."
  terraform -chdir=envs/$env init -backend=false -input=false
  terraform -chdir=envs/$env validate
done

# Also validate all modules
for mod in modules/*/; do
  echo "Validating $mod..."
  terraform -chdir=$mod init -backend=false -input=false
  terraform -chdir=$mod validate
done
```

Common terraform validate errors:

| Error                       | Cause                      | Fix                                    |
| --------------------------- | -------------------------- | -------------------------------------- |
| Unsupported argument        | Module interface changed   | Remove/update the argument in env main.tf |
| Missing required argument   | Module added new required var | Add the argument to env main.tf       |
| Reference to undeclared resource | Resource removed/renamed | Update references in env main.tf      |

## PR GUARDRAILS (CI Checks)

### Blocking Checks (Must Pass)

| Workflow                      | Trigger            | Validates                         |
| ----------------------------- | ------------------ | --------------------------------- |
| ci-terraform-lint.yml         | PRs to main w/ .tf | ALL envs + modules syntax         |
| pr-guardrails.yml             | All PRs            | Checklist, template, traceability |
| branch-policy.yml             | PRs to main        | dev/build/hotfix branches only    |
| adr-policy.yml                | adr-required label | ADR file present                  |
| changelog-policy.yml          | changelog-required | Changelog entry present           |
| ci-rds-request-validation.yml | RDS changes        | Schema compliance                 |
| session-capture-guard.yml     | Session changes    | Append-only enforcement           |
| session-log-required.yml      | Critical paths     | Session docs updated              |

### Warning Checks (Non-Blocking)

| Workflow                    | Trigger        | Validates                   |
| --------------------------- | -------------- | --------------------------- |
| rds-size-approval-guard.yml | RDS size       | Large/XLarge needs approval |
| rds-tfvars-drift-guard.yml  | tfvars changes | Coupled/standalone sync     |

## CRITICAL PATH FILES (Require Session Docs)

Changes to these paths require session_capture AND session_summary updates:

```text
.github/workflows/**
gitops/**
bootstrap/**
modules/**
scripts/**
docs/governance/**
docs/adrs/**
docs/70-operations/runbooks/**
```

## PR CHECKLIST TEMPLATE

Include in PR body:

```markdown
## Change Type
- [ ] Feature / Bug Fix / Documentation / Refactor

## Impact
- [ ] Breaking / Non-Breaking / Infrastructure Change

## Testing
- [ ] Unit Tests Pass
- [ ] Integration Tests Pass (if applicable)
- [ ] Manual Testing Completed

## Rollback
- [ ] Rollback Plan Documented / No Rollback Needed
```

## BYPASS LABELS

| Label            | Bypasses                  |
| ---------------- | ------------------------- |
| docs-only        | Script traceability check |
| typo-fix         | Full checklist validation |
| hotfix           | Branch policy             |
| build_id         | PR template requirements  |
| changelog-exempt | Changelog policy          |

## QUICK COMMANDS

```bash
# Run all pre-commit checks
pre-commit run --all-files

# Run all healing scripts
python3 scripts/standardize_metadata.py docs/ && \
python3 scripts/generate_adr_index.py && \
python3 scripts/generate_script_index.py && \
python3 scripts/generate_workflow_index.py && \
python3 scripts/generate_script_matrix.py

# Terraform validate ALL environments (required for .tf changes)
for env in dev test staging prod; do
  terraform -chdir=envs/$env init -backend=false -input=false && \
  terraform -chdir=envs/$env validate
done

# Check for secrets
gitleaks detect --redact

# Verify git status before commit
git status --short
```

## COMMON ISSUES AND FIXES

| Issue                    | Cause                      | Fix                                      |
| ------------------------ | -------------------------- | ---------------------------------------- |
| markdownlint fails       | MD004 (list style)         | Use * not - for lists                    |
| doc-metadata-autofix     | Missing fields             | Let hook fix or run standardize          |
| gitleaks fails           | Potential secret           | Remove credential, use env var           |
| terraform_fmt fails      | Formatting                 | Run terraform fmt -recursive             |
| terraform validate fails | Module interface changed   | Update env main.tf to match module       |
| Unsupported argument     | Arg removed from module    | Remove arg from env main.tf              |
| ci-terraform-lint fails  | Env out of sync w/ module  | Validate ALL envs, fix each one          |
| PR Guardrails fail       | Missing checklist          | Complete PR template                     |
| Changelog policy fail    | Missing entry              | Create docs/changelog/entries/CL-XXXX-*.md |
| Session log required     | Critical path change       | Update session_capture + session_summary |

## References

- docs/governance/GOV-0030-pr-guardrails-index.md
- docs/85-how-it-works/governance/PR_GUARDRAILS.md
- .pre-commit-config.yaml
- docs/governance/GOV-0034-ai-agent-governance.md
