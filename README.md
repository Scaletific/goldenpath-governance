# GoldenPath Governance Framework

A comprehensive, machine-enforceable governance framework for platform
engineering teams. Born from a real Internal Developer Platform (IDP) build,
this framework demonstrates how governance can be embedded into every layer
of the development lifecycle — from pre-commit hooks to CI/CD gates to
AI agent protocols.

## What's Here

| Directory | Contents |
|-----------|----------|
| `docs/governance/` | 50+ governance policies covering security, testing, metadata, AI agents, and more |
| `docs/adrs/` | Architecture Decision Records focused on governance mechanisms |
| `docs/onboarding/` | Onboarding guides, contribution standards, and agent protocols |
| `prompt-templates/` | AI agent execution prompts — how agents are instructed to follow governance |
| `scripts/` | Governance enforcement scripts (validators, linters, auto-healers) |
| `schemas/` | YAML/JSON schemas for metadata, governance registries, and routing |
| `.github/workflows/` | CI/CD workflows that enforce governance as code |
| `AGENTS.md` | Universal rules for AI agents operating in the repository |

## Key Concepts

### Governance as Code
Every policy has a corresponding enforcement mechanism — a pre-commit hook,
a CI workflow, or a validation script. Policies that aren't enforced don't exist.

### AI Agent Governance
AI agents (Claude, Codex, Copilot) operate under explicit trust boundaries
defined in `AGENTS.md` and enforced via CODEOWNERS. Agents can propose changes
but cannot modify their own constraints.

### Metadata-Driven Automation
Documents, scripts, and ADRs carry structured YAML frontmatter metadata.
Schemas validate this metadata. Auto-healing scripts fix drift. The metadata
powers dashboards, indexes, and audit trails.

### Session Capture & Accountability
Every significant change is documented in session capture files. Multi-agent
work follows coordination protocols with mandatory session summaries.

## Origin

This framework was extracted from a private Internal Developer Platform
repository. Infrastructure-specific details (AWS accounts, domains, cluster
configurations) have been replaced with placeholders. The governance logic,
policies, schemas, and enforcement mechanisms are published as-is.

## License

- **Documentation** (Markdown files, ADRs, policies): [CC BY 4.0](LICENSE-DOCS.md)
- **Code** (scripts, workflows, schemas): [Apache License 2.0](LICENSE-CODE.md)

See [NOTICE.md](NOTICE.md) for attribution requirements.

## Contributing

This is a reference implementation published for study and adaptation.
Issues and discussions are welcome. Pull requests that improve the governance
framework itself (not platform-specific changes) are considered.
