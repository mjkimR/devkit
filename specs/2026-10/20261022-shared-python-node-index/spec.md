---
id: SPEC-shared-python-node-index
title: Walk each Python tree once per rules run
summary: Adds a per-run node index to the rules workspace cache so Python-source rules read the nodes they need from one shared traversal instead of each walking every tree.
status: completed
created: 2026-10-22
related_capabilities: [CAP-GOV-rule-authoring, CAP-GOV-evaluation-lifecycle, CAP-GOV-rules-engine]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-shared-python-node-index] Walk each Python tree once per rules run

## 1. Problem Statement & Motivation

Handed off from proposal PROP-shared-python-node-index on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-shared-python-node-index`
- **Accepted Decisions**: `ADR-index-python-ast-nodes-by-type-in-workspacecache`

After `SPEC-rule-shared-python-ast` each Python file is parsed once per rules run, but the Python-source rules still
walk every shared tree themselves: a profile of `devkit rules check` (Measured on main at df307e99 (macOS, Python 3.12, about 820 tracked Python files), about 2.9 s) shows about 1.75 million
`ast.walk` steps and 5.4 million `iter_child_nodes` calls, mostly from `RULE-architecture` (`_imports`),
`RULE-advisory-unique-code` and `RULE-usecase-boundaries`, which each traverse the whole tree to find a few node kinds.

Prototype measurements on this repository (`docs/materials/2026-10/20261022-shared-python-node-index/measurements.md`,
Linux, Python 3.12, 826 files) show that building a per-run index mapping node types to node tuples on first request
costs only 8.97 MB RSS across all 826 files, and replaces 1,151 ms of repeated `ast.walk` passes with 1.82 ms of index
lookups (saving ~1.15 s of pure traversal time) with byte-identical output.

## 2. User Stories

- **US-1**: As an agent running `devkit rules check` or a commit gate, I want each Python AST traversed once per run,
  so that Python-source rules avoid redundant whole-tree walks.
- **US-2**: As a rule author, I want a cache accessor `get_python_nodes(path, *types)` that returns nodes of requested
  types in document order, so that new and existing rules can query specific AST nodes without running `ast.walk`.
- **US-3**: As a maintainer, I want rule execution results to remain byte-identical across the repository, so that
  the optimization changes no diagnostics.

## 3. Non-Goals

1. **Scope Excluded**: indexing complex lexical scope hierarchies, enclosing function environments, or AST parent links.
2. **Scope Excluded**: changing rule contracts or findings for valid source files.
3. **Scope Excluded**: persistent cross-run caching of node indices (`PROP-persistent-python-facts-cache`).
4. **Scope Excluded**: forcing rules with specialized conditional traversals (`unique_code._calls`, `layers._imports`)
   to use the index where custom AST logic is required.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Accessor returns matching nodes in document traversal order
- **Given** a workspace with a Python file holding imports, classes, and functions, and a `WorkspaceCache`
- **When** `cache.get_python_nodes(path, ast.Import, ast.ImportFrom)` is called
- **Then** it returns an immutable tuple containing all `ast.Import` and `ast.ImportFrom` nodes in document traversal
  order, exactly matching filtering an `ast.walk` pass on the shared AST

### [AC-02] Repeated queries return cached tuple without re-traversal
- **Given** a parsed Python file and a `WorkspaceCache`
- **When** `cache.get_python_nodes(path, ast.Call)` is called twice on the same path
- **Then** both calls return the identical tuple object without re-walking the tree

### [AC-03] Unparsable or missing file matches get_python_ast behavior
- **Given** an invalid Python file or missing file
- **When** `cache.get_python_nodes(path, ast.Call)` is called
- **Then** it raises `SyntaxError`, `ValueError`, or `FileNotFoundError` matching `cache.get_python_ast(path)`

### [AC-04] Cache invalidation drops the node index
- **Given** a cached node index for a path
- **When** `invalidate(path)`, `write_text(path, ...)`, or `invalidate_all()` is executed
- **Then** the cached node index is cleared and rebuilt on the next query

### [AC-05] Empty node types raises ValueError
- **Given** a valid Python file
- **When** `cache.get_python_nodes(path)` is called with no type arguments
- **Then** it raises `ValueError` stating that at least one node type must be specified

### [AC-06] Migrated rules query AST nodes via get_python_nodes
- **Given** `RULE-architecture`, `RULE-usecase-boundaries`, `RULE-cli-tool-command-boundary`, and
  `RULE-cli-tool-library-output`
- **When** `rule.check(ctx)` runs against target Python files
- **Then** whole-module AST walking is replaced by `ctx.cache.get_python_nodes`, and all existing rule tests pass

### [AC-07] Byte-identical rule findings across this repository
- **Given** this repository before and after the change
- **When** `devkit rules check --format json` runs on the entire workspace
- **Then** both runs exit with code 0 and output identical JSON findings

### [AC-08] Measurable reduction in rules check execution time
- **Given** this repository on main
- **When** `devkit rules check --format json` is benchmarked before and after the change
- **Then** the whole-tree traversal overhead is eliminated and wall time is measurably reduced

### [AC-09] Unit stays within its declared boundaries
- **Given** the finished unit
- **When** `devkit rules check specs/2026-10/20261022-shared-python-node-index` runs and the diff is inspected
- **Then** the check passes and changes are restricted to `packages/devkit`, `tools/devkit-dev`,
  `packages/devkit-dist`, `packages/devkit-catalog`, `docs/capabilities/governance/`, and unit artifacts

## 5. Assumptions

1. `ADR-index-python-ast-nodes-by-type-in-workspacecache` governs the shared read-only node index contract.
2. `unique_code._calls` and `layers._imports` retain their custom scoped traversals as decided in Planning Q1.
3. The catalog `cli_tool` rules (`command_boundary`, `library_output`) are tested in `devkit-catalog` and deployed
   when synchronized.
