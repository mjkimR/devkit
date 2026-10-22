---
id: SPEC-shared-python-node-index
title: Walk each Python tree once per rules run
summary: Adds a per-run node index to the rules workspace cache so Python-source rules read the nodes they need from one shared traversal instead of each walking every tree.
status: planned
created: 2026-10-22
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-shared-python-node-index] Walk each Python tree once per rules run

## 1. Problem Statement & Motivation

Handed off from proposal PROP-shared-python-node-index on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-shared-python-node-index`

### 1. Background & Hypothesis

After `SPEC-rule-shared-python-ast` each Python file is parsed once per rules run, but the Python-source rules still
walk every shared tree themselves: a profile of `devkit rules check` (Measured on main at df307e99 (macOS, Python 3.12, about 820 tracked Python files), about 2.9 s) shows about 1.75 million
`ast.walk` steps and 5.4 million `iter_child_nodes` calls, mostly from `RULE-architecture` (`_imports`),
`RULE-advisory-unique-code` and `RULE-usecase-boundaries`, which each traverse the whole tree to find a few node kinds.

Hypothesis, confirmed by prototype measurements on this repository (Linux, Python 3.12, 826 files;
`docs/materials/2026-10/20261022-shared-python-node-index/measurements.md`): building a per-run index mapping node types to node tuples on first request costs only
8.97 MB RSS across all 826 files, and replaces 1,151 ms of repeated `ast.walk` passes with 1.82 ms of index lookups
(saving ~1.15 s of pure traversal time) with byte-identical output.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Walk each Python tree once per rules run so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Which node kinds do the rules read (imports, function and class definitions, calls, string constants), and
  does any rule need traversal order or parent links that a by-type index loses?
  - **Answer**: `architecture`, `usecase-boundaries`, `command_boundary`, and `library_output` read concrete types
    (`Import`, `ImportFrom`, `Attribute`, `Call`, `FunctionDef`, `AsyncFunctionDef`) in document order, with no parent
    links needed. Only `unique_code._calls` (tracking enclosing function lazy imports) and `layers._imports` (skipping
    `if TYPE_CHECKING:`) perform specialized scope/conditional walks; these remain rule-internal, while flat walks
    migrate to the index (`ADR-index-python-ast-nodes-by-type-in-workspacecache`).
- **Q2**: What is the accessor shape (`get_python_nodes(path, *types)` returning a read-only sequence) and its memory
  cost next to the shared tree?
  - **Answer**: `WorkspaceCache.get_python_nodes(path, *types: type[ast.AST]) -> tuple[ast.AST, ...]` returns nodes
    matching any requested type in document traversal order. The index is built lazily on first node query for `path`
    and cleared on cache invalidation; memory cost is ~9 MB across 826 files.

### 3. Planning Decisions

- **D1 — Shared node index in `WorkspaceCache`**: `ADR-index-python-ast-nodes-by-type-in-workspacecache`.
- **D2 — Accessor contract**: `WorkspaceCache.get_python_nodes(path, *types: type[ast.AST]) -> tuple[ast.AST, ...]`:
  returns shared nodes in document traversal order matching any requested type; raises `ValueError` if `types` is empty;
  inherits the read-only contract of `ADR-share-one-read-only-parsed-tree-per-python-file`.
- **D3 — Migration scope**:
  - `RULE-architecture`: replaces 4 `ast.walk` passes in `_imports` with `get_python_nodes(path, ast.Import, ast.ImportFrom, ast.Attribute, ast.Call)`.
  - `RULE-usecase-boundaries`: replaces `_imports` walk with `get_python_nodes(path, ast.Import, ast.ImportFrom)`.
  - `RULE-cli-tool-command-boundary`: replaces `tree` walk with `get_python_nodes(path, ast.FunctionDef, ast.AsyncFunctionDef)`.
  - `RULE-cli-tool-library-output`: replaces `_aliases` and check walks with `get_python_nodes(path, ast.Import, ast.ImportFrom, ast.Call)`.
  - `RULE-advisory-unique-code`: `parse_module` reads top-level nodes through `get_python_nodes`; `_calls` remains rule-internal.
  - `RULE-cli-tool-layers`: custom `_imports` remains rule-internal.
- **D4 — Cache lifecycle**: the index is stored on `WorkspaceCache` beside `_ast_cache` and cleared on `invalidate`,
  `write_text`, `invalidate_many`, `invalidate_all`.

### 4. Proposed Design & Impact

#### WorkspaceCache and RuleContext

- `WorkspaceCache` adds `_nodes_cache: dict[str, dict[type[ast.AST], tuple[ast.AST, ...]]]` and
  `get_python_nodes(path: str | Path, *types: type[ast.AST]) -> tuple[ast.AST, ...]`.
- `invalidate(path)` and `invalidate_all()` clear `_nodes_cache`.

#### Rule migrations

- `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/rule.py`: `_imports` uses `cache.get_python_nodes`.
- `tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/rule.py`: `_imports` uses `cache.get_python_nodes`.
- `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/command_boundary/rule.py`: uses `cache.get_python_nodes`.
- `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/library_output/rule.py`: uses `cache.get_python_nodes`.

#### Living Spec

- `CAP-GOV-rule-authoring`: documents `ctx.cache.get_python_nodes(path, *types)` alongside `get_python_ast`.
- `CAP-GOV-rules-engine`: lists node indexing in `cache.py` responsibilities.

#### Acceptance outcomes

1. `devkit rules check --format json` produces byte-identical output before and after the change on this repository.
2. Migrated rules make 0 whole-module `ast.walk` calls.
3. Median wall time of `devkit rules check --format json` decreases measurably on this repository.
4. Existing rule test suites and cache integration tests pass cleanly.

#### Non-Goals

1. Indexing complex lexical scope hierarchies or AST parent links.
2. Persistent cross-run facts caching (`PROP-persistent-python-facts-cache`).
3. Changing any rule's file matching or finding messages.

### 5. Lifecycle & Retirement Criteria

<!--
- Preliminary decisions: devkit spec proposal padr shared-python-node-index "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept shared-python-node-index --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff shared-python-node-index.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->

