---
id: GOV-0050-emoji-policy
title: Emoji Usage Policy
type: policy
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - CL-0072-emoji-usage-policy-and-enforcement
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: governance
supported_until: 2028-01-06
version: 1.0
breaking_change: false
aliases:
  - EMOJI_POLICY
---

# Emoji Usage Policy

Emojis may be used sparingly and intentionally to improve readability, not to express tone or personality. The goal is to reduce cognitive load, not decorate content.

## 1. Where emojis are allowed

Emojis are permitted only in human-facing, instructional documentation, such as:

- READMEs
- Onboarding guides
- Runbooks
- Operational checklists
- Troubleshooting sections

In these contexts, emojis act as semantic markers to help scanning and comprehension.

## 2. Where emojis are not allowed

Emojis must not be used in authoritative or contractual documents, including:

- Architecture Decision Records (ADRs)
- Governance documents
- Policies
- Contracts
- Schemas (`*.schema.yaml`)
- Metadata definitions
- Security documentation

These documents are long-lived, auditable, and must remain neutral and unambiguous.

## 3. Approved emoji set

Only the following emojis are approved for use:

- ⚠️ Warning / risk
- 🚫 Not allowed / unsupported
- ✅ Required / valid
- 🔒 Security-related note
- 🔴 HV/HQ - Protect at all costs
- 🟡 HV/LQ - Move fast, don't overthink
- 🔵 MV/HQ - Bound and freeze
- ⚫ LV/LQ - Actively resist
- 🔬 Experimental / non-production
- 🧪 Lab / Experimental
- 📖 Reference / Bible
- 📘 Guide / Documentation
- ⚡ Quick Action / Shortcut
- 🚧 In-Progress / Draft
- 📖 Book / Protocol
- 📖 Testing Bible
- ⚡ Quick Reference
- 🧪 Current Test Scenarios
- 🛠️ Maintenance / Eng
- ⭐ 1-Star Maturity
- ⭐⭐ 2-Star Maturity
- ⭐⭐⭐ 3-Star Maturity
- ⭐⭐⭐⭐ 4-Star Maturity
- ⭐⭐⭐⭐⭐ 5-Star Maturity
- 🧭 Guidance / recommendation
- 📌 Important / callout
- 🚀 Platform Activation / Release
- 🛡️ Governance / Security
- 🏥 Health / Compliance
- 🏆 Achievement / Milestone
- 📈 Trend / Metric
- 🏛️ Architecture / Strategy
- 📊 Dashboard / Analysis
- 🏗️ Scaffolding / Setup
- 💎 Value / VQ Class
- 🤖 AI Agent / Automation
- 🎯 Platform Goal

Expressive or celebratory emojis (e.g. 😁 😂 🔥 🙌 😲) are not permitted.

## 4. Usage rules

- **Semantic Reinforcement**: Emojis must reinforce meaning, not add tone.
- **Section-Level**: Use at most one emoji per section or callout.
- **Heading Placement**: Emojis should appear at the start of headings or callouts, not inline mid-sentence.
- **Preference for Text**: If meaning is clear without an emoji, prefer no emoji.
