---
id: FB-agt-pyproject-foundation-comment
title: The devkit-agt dependency comment still calls devkit-dist the shared foundation
scope: repo
kind: friction
category: docs-mismatch
target: packages/devkit/pyproject.toml
skill: spec-sync
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-agt-pyproject-foundation-comment] The devkit-agt dependency comment still calls devkit-dist the shared foundation

## 1. Friction / Question (friction, question)

- **Context**: Verifying package ownership for `ADR-foundation-and-mcp-package-ownership`.
- **Expectation**: Package metadata comments match the ownership the ADR records.
- **Actual**: `packages/devkit/pyproject.toml` comments the `devkit-dist` requirement as "the devkit executable and the
  shared foundation"; the same file already requires `devkit-core`, which owns the foundation.
- **Workaround (or Interpretation Chosen)**: Left unchanged: production files were outside the docs-only unit's write
  scope.
- **Suggestion**: Change the comment to "the devkit executable and distribution".

## Evidence

```text
packages/devkit/pyproject.toml [project] dependencies:
"devkit-core==0.1.1",
"devkit-dist==0.1.1",  # the devkit executable and the shared foundation, released in lockstep from the same tag
```
