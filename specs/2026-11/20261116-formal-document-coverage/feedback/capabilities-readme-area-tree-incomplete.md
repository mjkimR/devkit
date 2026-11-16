---
id: FB-capabilities-readme-area-tree-incomplete
title: The capabilities README area tree omits six existing areas
scope: repo
kind: friction
category: docs-mismatch
target: docs/capabilities/README.md
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-capabilities-readme-area-tree-incomplete] The capabilities README area tree omits six existing areas

## 1. Friction / Question (friction, question)

- **Context**: Planning inventoried formal-document reader questions across every capability area.
- **Expectation**: The README's Directory Structure lists the capability areas a reader should cover.
- **Actual**: The tree lists 12 areas; `collaboration`, `documents`, `harness`, `mcp`, `traceability` and `viewer` exist under
  `docs/capabilities/` but are absent (18 area directories exist). A reader using the README as the area map misses them.
- **Workaround (or Interpretation Chosen)**: Listed the directory instead of the README.
- **Suggestion**: Add the missing areas to the tree, or replace the tree with a pointer to the directory listing.

## Evidence

```text
docs/capabilities/README.md Directory Structure: distribution, governance, delivery, worktree, gate, compact,
search, host, integration, generated, advisory, cli.
ls docs/capabilities/: advisory cli collaboration compact delivery distribution documents gate generated
governance harness host integration mcp search traceability viewer worktree
```

## Disposition

- **Disposition**: Resolved in SPEC-remaining-feedback-fixes: the capabilities README Directory Structure tree lists all 18 areas, adding collaboration, documents, harness, mcp, traceability and viewer with their ID prefixes.
