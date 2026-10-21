---
id: FB-module-name-discovery-before-checks
title: Discover accepted module names before running verification recipes
scope: repo
kind: suggestion
category: redundant-step
target: scripts/module.sh and justfile verification recipes
skill: spec-review
agent: codex
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-21
---

# [FB-module-name-discovery-before-checks] Discover accepted module names before running verification recipes

## 2. Suggestion / Change Request

- **Current Procedure**: Verification recipes accept a module argument; this run inferred `agt` and both checks rejected it before doing work. The failure listed `devkit-agt` as the accepted name.
- **Proposed Procedure**: Include an inexpensive module discovery command or the canonical module names alongside the verification recipe help, so a delegated verification payload can validate its names before execution.
- **Expected Benefit**: Avoid failed lint/type invocations and their separate command-scoped permission requests in sibling worktrees.
- **Cost & Risk**: A hard-coded list can drift; derive names from the same source as validation. Adding aliases is not required.
- **Attempted**: Retried with `devkit-agt`; both checks passed. No recipe changes were made.

## Diagnostic Details

- **Reproduction**: `just lint-check agt` and `just check agt`.
- **Expected / Actual**: The inferred abbreviation was invalid; each command exited 1 and printed available full module names.
- **Versions**: Repository implementation at the fix-verify stage of `SPEC-integration-rewritten-merge`; external tool versions not relevant.
- **Conditions**: Codex emulated worker, sibling worktree and command-scoped permission requests.
- **Workarounds Attempted**: Use the diagnostic's canonical module name; lint and Pyright completed successfully.
- **Related Assets**: `scripts/module.sh`, `justfile`.

## Evidence

```text
Unknown module: agt
Available modules: ... devkit-agt
just lint-check devkit-agt: All checks passed; 240 files already formatted
just check devkit-agt: 0 errors, 0 warnings, 0 informations
```
