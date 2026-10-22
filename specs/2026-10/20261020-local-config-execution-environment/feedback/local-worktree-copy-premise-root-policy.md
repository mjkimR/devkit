---
id: FB-local-worktree-copy-premise-root-policy
title: Worktree copy acceptance should distinguish nested helper paths from project roots
scope: repo
kind: friction
category: spec-ambiguity
target: docs/materials/2026-10/20261020-local-config-execution-environment/configuration-evidence.md
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-20
---

# [FB-local-worktree-copy-premise-root-policy] Worktree copy acceptance should distinguish nested helper paths from project roots

## 1. Friction / Question

- **Context**: Development checked the handed-off worktree copy premises against current project discovery.
- **Expectation**: The requested nested-project copy fixture would map directly to a supported CLI project root.
- **Actual**: The core project contract refuses nested devkit roots inside a Git worktree. The lifecycle copy helper still accepts a corresponding relative project path.
- **Interpretation Chosen**: Preserve discovery and exercise nested copy paths at the helper boundary. Record the distinction in the plan/spec assumption.
- **Suggestion**: During Planning, identify the owning interface for nested-path acceptance explicitly instead of implying that helper-path support changes CLI root resolution.

## Diagnostic Details

- **Reproduction**: Read the carried AC4 and `core/project.py` root-selection contract before implementation.
- **Expected / Actual**: Copy ordering and independent snapshots were implementable; nested CLI root support was outside the accepted scope.
- **Versions**: Handoff base 3564ccbbd48a31282f457dbd40149e0c687aac23.
- **Conditions**: Proposal handoff to a sibling Development worktree; current root policy retained.
- **Workarounds Attempted**: A focused helper regression verifies the corresponding nested destination without altering discovery.
- **Related Assets**: `packages/devkit-dist/src/devkit/core/project.py`, `packages/devkit/src/devkit/worktree/lifecycle.py`.

## Evidence

```text
core/project.py: inside a Git work tree the repository root is the devkit root;
a nested .devkit directory is not a project of its own.
Carried AC4: nested project paths.
Regression: test_nested_project_helper_uses_corresponding_path.
```

- **Disposition**: dismissed. A one-off interpretation in a completed unit, already recorded in its plan and covered by `test_nested_project_helper_uses_corresponding_path`; the target is a dated material and no recurring asset needs a change.
