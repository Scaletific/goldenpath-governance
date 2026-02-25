---
id: GOV-0013-devsecops-security-standards
title: DevSecOps Security Standards
type: governance
owner: platform-team
status: active
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: high
  coupling_risk: medium
schema_version: 1
relates_to:
  - ADR-0170
  - session-2026-01-19-build-pipeline-architecture
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
effective_date: 2026-01-19
review_date: 2026-07-19
related_adrs:
  - ADR-0170
related_govs:
  - GOV-0012
  - GOV-0015
---

# GOV-0013: DevSecOps Security Standards

## Purpose

Define mandatory security tooling, scanning requirements, and shift-left practices for all GoldenPath IDP development.

## Philosophy

**Shift-Left Security**: Enforce early detection before vulnerabilities reach production, staging, or even source code. Security issues caught in a developer's IDE cost orders of magnitude less to fix than those discovered in production.

**Fail Fast, Detect Early**: In DevSecOps, we detect early and eliminate security vulnerabilities as early as possible in the development lifecycle.

---

## 1. Security Tool Categories

### 1.1 Software Composition Analysis (SCA)

**Purpose**: Check all libraries and open-source dependencies for known vulnerabilities.

| Tool | Use Case | GoldenPath Standard |
|------|----------|---------------------|
| **Snyk** | IDE + CI integration | Primary |
| Dependabot | Automated dependency PRs | Complement |
| OWASP Dependency-Check | Free alternative | Budget fallback |

### 1.2 Static Application Security Testing (SAST)

**Purpose**: Check source code for coding errors (SQL injection, buffer overflows, XSS patterns) without executing the code.

| Tool | Use Case | GoldenPath Standard |
|------|----------|---------------------|
| **Semgrep** | Fast, customizable rules | Primary |
| CodeQL | GitHub Advanced Security | Complement |
| SonarQube | Quality + security | Enterprise alternative |

### 1.3 Secret Scanning

**Purpose**: Detect API keys, passwords, tokens committed to repositories.

| Tool | Use Case | GoldenPath Standard |
|------|----------|---------------------|
| **Gitleaks** | Pre-commit + CI | Primary |
| TruffleHog | Deep history scanning | Audits |
| GitHub Secret Scanning | Native detection | Enable by default |

### 1.4 Dynamic Application Security Testing (DAST)

**Purpose**: Test running application for runtime vulnerabilities (SQL injection, XSS, authentication bypass, session hijacking).

| Tool | Use Case | GoldenPath Standard |
|------|----------|---------------------|
| **OWASP ZAP** | CI pipeline testing | Primary |
| Burp Suite | Manual pentesting | Security reviews |
| Nuclei | Template-based scanning | Complement |

### 1.5 Image Scanning

**Purpose**: Scan container images for OS and application vulnerabilities.

| Tool | Use Case | GoldenPath Standard |
|------|----------|---------------------|
| **Trivy** | CI pipeline (SARIF output) | Primary |
| Docker Scout | Local developer scanning | Complement |
| Grype | Syft integration | Alternative |

### 1.6 SBOM Generation

**Purpose**: Create Software Bill of Materials listing all components and dependencies.

| Tool | Use Case | GoldenPath Standard |
|------|----------|---------------------|
| **Syft** | CI artifact generation | Primary |
| Docker Scout SBOM | Docker-native | Alternative |
| Trivy | Combined scan + SBOM | Already in pipeline |

---

## 2. Security Gates by Pipeline Stage

| Stage | Check Type | Tools | Enforcement | Output |
|-------|------------|-------|-------------|--------|
| **IDE** | SCA, SAST, Secrets | Snyk, Semgrep, Gitleaks | Advisory | Developer feedback |
| **Pre-commit** | Secrets scan | Gitleaks hooks | Blocking | Prevents commit |
| **Source (PR)** | SCA, SAST, Secrets | Snyk, Semgrep, Gitleaks | Blocking | PR check status |
| **Build** | SBOM, Image scan | Syft, Trivy | Blocking (HIGH+) | SBOM artifact, SARIF |
| **Test** | DAST | OWASP ZAP | Advisory (V1) | Security report |
| **Release** | Image scan, CVE check | Trivy | Blocking (HIGH+) | Release gate |
| **Periodic** | SCA, SAST, CVE rescan | Scheduled workflows | Alert | Platform health dashboard |

---

## 3. Mandatory Requirements

### 3.1 Developer Tooling

| Requirement | Enforcement | Timeline |
|-------------|-------------|----------|
| Gitleaks pre-commit hook | MUST install | Onboarding |
| Snyk IDE extension | SHOULD install | Encouraged |
| Pre-commit framework | MUST configure | Onboarding |

### 3.2 Build Artifacts

| Artifact | Requirement | Storage |
|----------|-------------|---------|
| SBOM (SPDX or CycloneDX) | MUST generate | Governance registry |
| SARIF security results | MUST upload | GitHub Security tab |
| Image digest | MUST log | Build output |

### 3.3 Image Base Standards

| Image Type | Use Case | Allowed Environments |
|------------|----------|----------------------|
| **Distroless** | Minimal attack surface | All (preferred for prod) |
| **Chainguard** | Signed + SBOM included | All (high-security) |
| **Alpine** | Small with shell | dev/test only |
| Standard (Debian/Ubuntu) | Debugging | local only |

**Production Requirement**: Production images MUST use distroless or Chainguard base images.

---

## 4. Gate Configuration by Environment

### 4.1 Blocking Gates Matrix

| Gate | local | dev | test | staging | prod |
|------|-------|-----|------|---------|------|
| Gitleaks (secrets) | Advisory | Advisory | Blocking | Blocking | Blocking |
| SAST (Semgrep) | Advisory | Advisory | Blocking | Blocking | Blocking |
| SCA (Snyk/Trivy) | Advisory | Advisory | Blocking | Blocking | Blocking |
| Image Scan (Trivy) | Advisory | Advisory | Blocking | Blocking | Blocking |
| DAST (ZAP) | N/A | N/A | Advisory | Advisory | Blocking (V2) |
| SBOM present | Optional | Optional | Required | Required | Required |

### 4.2 Severity Thresholds

| Environment | Blocking Severities | Action |
|-------------|---------------------|--------|
| local/dev | None (advisory) | Log warning |
| test | HIGH, CRITICAL | Fail pipeline |
| staging | HIGH, CRITICAL | Fail pipeline |
| prod | HIGH, CRITICAL | Fail pipeline + alert |

---

## 5. SBOM Requirements

### 5.1 Generation

All production builds MUST generate SBOM:

```yaml
- name: Generate SBOM with Syft
  uses: anchore/sbom-action@v0
  with:
    image: ${{ env.IMAGE }}
    format: spdx-json
    output-file: sbom.spdx.json

- name: Upload SBOM to Governance Registry
  run: |
    cp sbom.spdx.json environments/${{ env.ENV }}/latest/
```

### 5.2 Format

| Format | Use Case | Required |
|--------|----------|----------|
| SPDX JSON | Industry standard | Primary |
| CycloneDX | Alternative | Acceptable |

### 5.3 Storage

SBOMs MUST be stored in:

1. Build artifacts (GitHub Actions)
2. Governance registry branch
3. Associated with image digest

---

## 6. Pre-commit Configuration

### 6.1 Required Hooks

All repositories MUST include `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: local
    hooks:
      - id: semgrep
        name: semgrep
        entry: semgrep --config auto
        language: system
        types: [python, javascript, typescript, go]
        pass_filenames: false
```

### 6.2 Installation

Developers MUST run:

```bash
pip install pre-commit
pre-commit install
```

---

## 7. Periodic Scanning

### 7.1 Schedule

| Scan Type | Frequency | Scope |
|-----------|-----------|-------|
| CVE rescan (images) | Daily | All deployed images |
| SCA (dependencies) | Weekly | All repositories |
| SAST (code) | Weekly | All repositories |
| Full audit | Monthly | Platform-wide |

### 7.2 Reporting

Results MUST feed into:

1. Platform health dashboard
2. Governance registry (historical log)
3. Alert channels (Slack/email for HIGH+)

---

## 8. Docker Scout Integration

### 8.1 Local Developer Use

Developers SHOULD use Docker Scout for local scanning:

```bash
# Scan for CVEs
docker scout cves myimage:tag

# Generate SBOM
docker scout sbom --format spdx-json myimage:tag > sbom.spdx.json

# Quick overview
docker scout quickview myimage:tag
```

### 8.2 CI Integration (Optional)

Docker Scout MAY be used as secondary scanner:

```yaml
- name: Docker Scout CVE Scan
  uses: docker/scout-action@v1
  with:
    command: cves
    image: ${{ env.IMAGE }}
    sarif-file: scout-results.sarif
    exit-code: true
```

---

## 9. Exceptions

### 9.1 Security Gate Exceptions

Exceptions to blocking gates require:

1. ADR documenting the exception and risk acceptance
2. Platform-team approval
3. Time-boxed remediation plan (max 30 days)
4. Compensating controls documented

### 9.2 Tool Exceptions

Alternative tools require:

1. Equivalent security coverage demonstrated
2. Platform-team approval
3. Integration with governance registry

---

## 10. Compliance

### 10.1 Audit Trail

All security scans produce:

- SARIF results in GitHub Security tab
- SBOM in governance registry
- Scan timestamps and results logged
- Exception approvals tracked

### 10.2 Violations

Violations of this policy will:

1. Block the pipeline (for enforced gates)
2. Generate alerts to platform-team and security-team
3. Require remediation before promotion
4. Be tracked in compliance dashboard

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-19 | Initial version | platform-team |

---

## Related Documents

- GOV-0012: Build Pipeline Standards
- GOV-0015: Build Pipeline Testing Matrix
- ADR-0170: Build Pipeline Architecture and Multi-Repo Strategy
- OB-0001: Developer Security Tooling Onboarding
- Session: `session_capture/2026-01-19-build-pipeline-architecture.md`

Signed: platform-team (2026-01-19)
