---
id: PADR-index-python-ast-nodes-by-type-in-workspacecache
title: Index Python AST nodes by type in WorkspaceCache
summary: For Python-source rules traversing shared ASTs, we build a per-run node index by type in WorkspaceCache on first request, to eliminate redundant whole-tree walks across rules, accepting that callers receive shared node tuples that must stay unmodified.
proposal: PROP-shared-python-node-index
status: draft
created_at: 2026-10-22
---

# [PADR-index-python-ast-nodes-by-type-in-workspacecache] Index Python AST nodes by type in WorkspaceCache

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

After `ADR-share-one-read-only-parsed-tree-per-python-file`, `WorkspaceCache` shares one parsed `ast.Module` per Python
file. Multiple Python-source rules (`RULE-architecture`, `RULE-usecase-boundaries`, `RULE-advisory-unique-code`,
`RULE-cli-tool-command-boundary`, `RULE-cli-tool-library-output`) still each walk the shared tree across all workspace
files, taking about 1.75 million `ast.walk` steps and adding about 0.5 s to `devkit rules check`.

## 2. Decision Drivers

- Rule results remain byte-identical to individual tree walks.
- Redundant AST traversals across rules are eliminated from `devkit rules check`.
- Memory overhead for retained node indices remains minimal and predictable.
- The accessor contract remains simple and composable for rule authors.

## 3. Considered Options

- **Per-run node index by type in `WorkspaceCache`**: `WorkspaceCache.get_python_nodes(path, *types)` builds an index
  mapping node types to tuples of nodes lazily on first request. Costs about 9 MB RSS across 826 files and cuts repeated
  walks to under 2 ms.
- **Full syntax-tree and scope graph**: index records lexical scopes, enclosing functions, and conditional blocks.
  Complex to maintain, higher memory footprint, and unneeded for most rules.
- **Keep per-rule `ast.walk`**: no changes, but retains about 0.5 s of redundant traversals in every whole-workspace run.

## 4. Decision Outcome

Chosen: **Per-run node index by type in `WorkspaceCache`**.

- **Accessor**: `WorkspaceCache.get_python_nodes(path, *types: type[ast.AST]) -> tuple[ast.AST, ...]`: returns nodes
  matching any requested type in document traversal order (driver 4).
- **Lazy construction and caching**: the index is built on the first node query for `path` from `get_python_ast(path)`
  and retained under the same invalidation cycle as the parsed AST.
- **Scope of migration**: rules querying flat node types (`architecture`, `usecase-boundaries`, `command_boundary`,
  `library_output`, and module-level `unique_code`) read through `get_python_nodes`; specialized scoped walks
  (`unique_code._calls` and `layers._imports`) remain rule-internal, optionally short-circuiting when target nodes
  are absent (driver 1).
- **Shared read-only contract**: returned tuples contain the shared AST node instances; callers must not modify them.

## 5. Consequences

- Positive: removes repeated `ast.walk` traversals, saving about 0.5 s on whole-workspace runs.
- Positive: rules querying multiple node kinds (e.g. `Import` and `ImportFrom`) can retrieve them in one query.
- Negative: adds about 9 MB of retained memory across 826 files during a full run.
- Risk (accepted): callers must observe the read-only contract for nodes returned by the accessor.

## 6. Confirmation

- Integration tests in `packages/devkit/tests/integration/features/rules/workspace/test_cache.py` verify that
  `get_python_nodes` returns nodes in document order matching direct AST traversals, and that invalidation drops the index.
- Rule unit and integration tests verify byte-identical output across this repository before and after migration.
