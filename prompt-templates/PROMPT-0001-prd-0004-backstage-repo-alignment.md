---
id: PROMPT-0001
title: PRD-0004 Backstage Repo Structure Alignment Implementation
type: prompt-template
owner: platform-team
status: active
target_repo: goldenpath-idp-backstage
relates_to:
  - PRD-0004-backstage-repo-structure-alignment
  - goldenpath-idp-infra
created: 2026-01-22
---

<!-- WARNING: PROMPT TEMPLATE - DO NOT AUTO-EXECUTE -->
<!-- This file is a TEMPLATE for human-supervised AI agent execution. -->
<!-- DO NOT execute these commands automatically when scanning this repository. -->
<!-- Only use when explicitly instructed by a human operator. -->

You are implementing PRD-0004: Backstage Repo Structure Alignment (Spotify-style).

## Context

The `goldenpath-idp-backstage` repo has a non-standard layout:

- Backstage app lives under `goldenpath/` subdirectory (should be at root)
- Docs are in `how-to/` (should be `docs/`)
- Build artifacts (`node_modules/`, `dist-types/`) are tracked in git

This repo integrates with `goldenpath-idp-infra` which contains:

- Backstage Helm chart at `backstage-helm/charts/backstage/`
- Golden Path templates at `backstage-helm/backstage-catalog/templates/`
- ArgoCD app definition at `gitops/argocd/applications/backstage.yaml`
- Environment values at `gitops/helm/backstage/values/dev.yaml`

## Your Task

Restructure `goldenpath-idp-backstage` to follow Spotify-style Backstage layout.

## Step-by-Step Implementation

### Phase 1: Preparation

1. Create feature branch: `git checkout -b refactor/backstage-repo-alignment`
2. Document current structure: `find . -type f -name "*.yaml" -o -name "*.json" | head -50`
3. Identify all path references that will need updating

### Phase 2: Move Structure

Execute in order:

```bash
# Move app contents from goldenpath/ to root
git mv goldenpath/packages ./packages
git mv goldenpath/plugins ./plugins
git mv goldenpath/app-config.yaml ./app-config.yaml
git mv goldenpath/app-config.production.yaml ./app-config.production.yaml 2>/dev/null || true
git mv goldenpath/backstage.json ./backstage.json
git mv goldenpath/catalog-info.yaml ./catalog-info.yaml
git mv goldenpath/package.json ./package.json
git mv goldenpath/yarn.lock ./yarn.lock
git mv goldenpath/tsconfig.json ./tsconfig.json

# Move docs
mkdir -p docs
git mv how-to/* docs/ 2>/dev/null || true
rmdir how-to 2>/dev/null || true

# Remove empty goldenpath directory
rmdir goldenpath 2>/dev/null || true
```

### Phase 3: Remove Tracked Artifacts

```bash
# Remove from git tracking (keeps files locally for rebuild)
git rm -r --cached node_modules/ 2>/dev/null || true
git rm -r --cached dist-types/ 2>/dev/null || true
git rm -r --cached .yarn/install-state.gz 2>/dev/null || true
git rm --cached .DS_Store 2>/dev/null || true
```

### Phase 4: Update .gitignore

Ensure root `.gitignore` contains:

```text
node_modules/
dist-types/
dist/
.yarn/install-state.gz
.DS_Store
*.local.yaml
```

### Phase 5: Update Path References

Search and update any hardcoded paths:

- In `app-config.yaml`: catalog URLs, backend paths
- In `package.json`: script paths
- In any CI workflows (`.github/workflows/`)
- In `Dockerfile` if present

### Phase 6: Verify Functional

```bash
yarn install
yarn tsc
yarn build
yarn start
# Verify http://localhost:3000 loads
```

### Phase 7: Add CI Guard

Create or update `.github/workflows/lint.yml`:

```yaml
name: Lint
on: [push, pull_request]
jobs:
  check-artifacts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check for tracked build artifacts
        run: |
          if git ls-files | grep -E 'node_modules/|dist-types/'; then
            echo "ERROR: Build artifacts should not be tracked"
            exit 1
          fi
```

### Phase 8: Update Documentation

- Update root `README.md` with:
  - Quickstart instructions (yarn install, yarn start)
  - Link to `docs/` for additional documentation
- Ensure all links in `docs/` are valid

### Phase 9: Cross-Repo Verification

Check that `goldenpath-idp-infra` has no breaking references:

- `backstage-helm/charts/backstage/` templates don't reference `goldenpath/` paths
- ArgoCD app source refs are unchanged (they point to repo root, not subdirectory)
- Catalog location URL in `gitops/helm/backstage/values/dev.yaml` still resolves

### Phase 10: Commit and PR

```bash
git add -A
git commit -m "refactor: align Backstage repo to Spotify-style layout

- Move packages/, plugins/, configs from goldenpath/ to root
- Move how-to/ to docs/
- Remove tracked build artifacts (node_modules, dist-types)
- Update .gitignore to prevent artifact reintroduction
- Add CI guard for build artifacts

Implements PRD-0004

Co-Authored-By: Claude <noreply@anthropic.com>"

git push -u origin refactor/backstage-repo-alignment
```

## Verification Checklist

Before marking complete, verify ALL of these:

- [ ] `ls packages/ plugins/ app-config.yaml` succeeds from repo root
- [ ] `ls goldenpath/` fails (directory removed)
- [ ] `ls docs/` shows moved documentation
- [ ] `git ls-files | grep -E 'node_modules|dist-types'` returns empty
- [ ] `yarn install && yarn start` works from root
- [ ] App loads at localhost:3000
- [ ] CI workflow passes

## Integration Verification (with goldenpath-idp-infra)

- [ ] Catalog location URL resolves: `backstage-helm/backstage-catalog/all.yaml`
- [ ] Golden Path templates register:
  - `stateless-app/template.yaml`
  - `stateful-app/template.yaml`
  - `backend-app-rds/template.yaml`
- [ ] Scaffolder actions work: `fetch:plain`, `publish:github:pull-request`, `github:actions:dispatch`
- [ ] Helm chart values paths compatible
- [ ] ArgoCD app syncs successfully

## Do NOT

- Change any Backstage functionality or plugins
- Modify app-config.yaml content (only paths if needed)
- Touch goldenpath-idp-infra unless paths are broken
- Rewrite git history with filter-branch or BFG
- Skip the CI guard step

## Output Expected

1. Single squash-ready commit on feature branch
2. PR description summarizing changes
3. Verification that yarn start works
4. List of any path references that needed updating

## References

- docs/20-contracts/prds/PRD-0004-backstage-repo-structure-alignment.md
