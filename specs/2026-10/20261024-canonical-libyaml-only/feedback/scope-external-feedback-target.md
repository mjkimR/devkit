---
id: FB-scope-external-feedback-target
title: Let scope registration accept explicitly declared source-feedback files
scope: repo
kind: friction
category: tool-error
target: devkit spec scope update
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-24
---

# [FB-scope-external-feedback-target] Let scope registration accept explicitly declared source-feedback files

## 1. Friction / Question

- **Context**: Completing a spec that directly resolves an open feedback file owned by an earlier spec.
- **Expectation**: A source-feedback file explicitly added to the task boundary can be registered as an authorized completion path.
- **Actual**: `devkit spec scope update` reports the path as unresolved with reason `excluded-tree` because it is under another `specs/` bundle, even though the file is declared in the current task boundary.
- **Workaround (or Interpretation Chosen)**: Keep the exact source-feedback path in `tasks.md`, update it directly under the approved task scope, and record the outcome in `reconcile.md`; the unresolved scope diagnostic remains.
- **Suggestion**: Allow explicitly declared, directly linked source-feedback files outside the current unit to be collected as file scopes while keeping other nested spec trees excluded.

## Diagnostic Details

- **Reproduction**: Add an earlier spec's feedback path to the current task's `_Boundary`, then run `uv run devkit spec scope update --spec <unit>`.
- **Expected / Actual**: Expected the declared file to enter the registered scope. Actual output reports `unresolved=1`; `devkit spec scope query --format json` identifies that path with `reason: excluded-tree` and `source: declared-code`.
- **Versions**: devkit worktree at `fd1ad7ce611d470b2c391385ddd90f1cbba07f94`.
- **Conditions**: The direct fix targets a feedback file in a different spec bundle under `specs/`.
- **Workarounds Attempted**: Explicitly declared the source file in the task boundary and applied its disposition; the command continued with no scope overlaps but retained the unresolved entry.
- **Related Assets**: `specs/2026-10/20261024-canonical-libyaml-only/tasks.md`; `specs/2026-10/20261022-frontmatter-libyaml/feedback/canonical-c-yaml-contract.md`.

## Evidence

```text
[SCOPE_ACK: status=applied revision=10 added=2 removed=0 overlaps=0 unresolved=1]
{"value":"specs/2026-10/20261022-frontmatter-libyaml/feedback/canonical-c-yaml-contract.md","reason":"excluded-tree","source":"declared-code"}
```
