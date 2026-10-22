---
id: PLAN-shared-python-node-index
spec: SPEC-shared-python-node-index
---

# Technical Plan: `SPEC-shared-python-node-index` Walk each Python tree once per rules run

## 1. Constitution & Invariant Review

The design implements `ADR-index-python-ast-nodes-by-type-in-workspacecache` as accepted. It adds `get_python_nodes`
to `WorkspaceCache` without modifying existing `MUST` invariants in `CAP-GOV-rule-authoring`,
`CAP-GOV-evaluation-lifecycle`, or `CAP-GOV-rules-engine`. Living Spec capabilities will document the new accessor,
its return contract, and its invalidation behavior.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py` | Add `_nodes_cache: dict[str, dict[type[ast.AST], tuple[ast.AST, ...]]]`; implement `get_python_nodes(path, *types)`; clear in `invalidate` and `invalidate_all` |
| `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/rule.py` | In `_imports`, replace 4 `ast.walk` loops with queries via `cache.get_python_nodes(path, ast.Import, ast.ImportFrom, ast.Attribute, ast.Call)` |
| `tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/rule.py` | In `_imports`, replace `ast.walk` with `cache.get_python_nodes(path, ast.Import, ast.ImportFrom)` |
| `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/command_boundary/rule.py` | Replace `ast.walk` with `ctx.cache.get_python_nodes(path, ast.FunctionDef, ast.AsyncFunctionDef)` |
| `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/library_output/rule.py` | Replace `ast.walk` in `_aliases` and `check` with `ctx.cache.get_python_nodes` queries |
| `docs/capabilities/governance/` | Document `get_python_nodes` accessor and cache responsibilities |
| `.devkit/installation.json` and `.devkit/managed/` | Refreshed by `devkit sync` after bundle changes |

## 3. Component & Interface Design

### WorkspaceCache.get_python_nodes

```python
class WorkspaceCache:
    _nodes_cache: dict[str, dict[type[ast.AST], tuple[ast.AST, ...]]]

    def get_python_nodes(self, path: str | Path, *types: type[ast.AST]) -> tuple[ast.AST, ...]:
        """Nodes of the requested AST types from a parsed Python module, in document traversal order.

        Builds the file's type-indexed node table on the first call from ``get_python_ast(path)``.
        Returns an immutable tuple of nodes whose exact type matches any of ``types``.
        Raises ``ValueError`` if no types are passed, and re-raises any ``SyntaxError`` or
        ``ValueError`` from ``get_python_ast``.
        """
```

- Index structure:
  - On first request for `key = self._resolve_path(path).as_posix()`, obtain `tree = self.get_python_ast(path)`.
  - Traverse `tree` once using `ast.walk(tree)`.
  - Accumulate nodes into a `defaultdict(list)` keyed by `type(node)`.
  - Convert lists to tuples and store in `self._nodes_cache[key]`.
- Filtering:
  - When queried with `*types`, if a cached node tuple for that specific combination exists or can be assembled:
  - Concatenate `tuple(node for t in types for node in by_type.get(t, ()))` or preserve traversal order by sorting by line/col offset or document sequence.
  - Wait: `ast.walk` yields nodes in traversal order; to keep document order when multiple types are requested, storing the full node list or ordering by `(lineno, col_offset)` or preserving the traversal sequence ensures consistency.
- Invalidation:
  - `invalidate(path)` removes `self._nodes_cache.pop(key, None)`.
  - `invalidate_all()` clears `self._nodes_cache.clear()`.

## 4. Verification & Test Plan

- **Cache Integration Tests**: `packages/devkit/tests/integration/features/rules/workspace/test_cache.py`:
  - Query single and multiple node types, check document order against direct `ast.walk`.
  - Verify cached object identity across calls.
  - Verify error handling on unparsable files and empty `types` argument.
  - Verify invalidation on file modification and cache reset.
- **Rule Tests**:
  - `uv run devkit rules test` for `architecture` and `usecase-boundaries`.
  - `just test devkit-catalog` for `command_boundary` and `library_output`.
- **Workspace Verification**:
  - `uv run devkit rules check --format json` produces byte-identical output on this repository.
  - `just check`, `just lint-check`, `just test-affected`.
