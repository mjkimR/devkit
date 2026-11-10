---
id: FB-containers-say-devkit-docs-ships-no-bundle
title: ARCH-05-1-containers says devkit-docs ships no bundle although it registers the docs bundle
scope: repo
kind: friction
category: docs-mismatch
target: ARCH-05-1-containers
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-containers-say-devkit-docs-ships-no-bundle] ARCH-05-1-containers says devkit-docs ships no bundle although it registers the docs bundle

## 1. Friction / Question (friction, question)

- **Context**: Planning of a package that requires `devkit-docs` had to state which bundles an installation of that
  requirement deploys.
- **Expectation**: `ARCH-05-1-containers` §2.4 describes what the `devkit-docs` wheel ships.
- **Actual**: §2.4 says "It ships no bundle and knows no delivery process". The wheel registers
  `docs = "devkit_docs.bundles.docs"` in `devkit.bundles`, the bundle declares `auto_select = true`, and
  `ARCH-07-deployment` says so. §2.5 of the same document says the `spec` bundle "ships every rule asset, including
  the document rules", while the docs bundle holds document rule assets of its own.
- **Workaround (or Interpretation Chosen)**: The planning evidence follows the code and `ARCH-07-deployment`: every
  installation that carries `devkit-docs` auto-selects `docs:core`.
- **Suggestion**: Correct §2.4 to name the `docs` bundle and its auto-selection, and check the sentence of §2.5 on
  document rules against the two bundles.

## Diagnostic Details

- **Reproduction**: Read `ARCH-05-1-containers` §2.4 beside `packages/devkit-docs/pyproject.toml`.
- **Expected / Actual**: Expected the docs bundle in the contents line; the section denies it.
- **Versions**: Worktree at `fe1f1885`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `ARCH-07-deployment`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml`.

## Evidence

```text
docs/architecture/ARCH-05-1-containers.md:125  "It ships no bundle and knows no delivery process: ..."
packages/devkit-docs/pyproject.toml:17-18      [project.entry-points."devkit.bundles"] docs = "devkit_docs.bundles.docs"
packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml:4-5  default_preset = "core", auto_select = true
docs/architecture/ARCH-07-deployment.md:177    "The devkit-docs wheel registers `docs = "devkit_docs.bundles.docs"` in `devkit.bundles`."
```
