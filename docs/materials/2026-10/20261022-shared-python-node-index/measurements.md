# Planning measurements for PROP-shared-python-node-index

Measured on the `plan-shared-python-node-index` worktree (Linux, CPython 3.12, 826 tracked Python files).

## 1. AST Traversal Baseline & Index Costs

| Measure | Value |
| --- | --- |
| Total Python files parsed | 826 |
| Total AST nodes across workspace | 750,564 |
| Wall time for one single walk across all 826 trees | ~1.81 s |
| Memory overhead for `by_type` index across all 826 files | 8.97 MB (peak 8.97 MB) |
| Total nodes matching target rule types (`Import`, `ImportFrom`, `Attribute`, `Call`, `FunctionDef`, `AsyncFunctionDef`, `ClassDef`) | 100,775 |

## 2. Repeated Walk vs Index Lookup Simulation

Simulating 4 whole-workspace inspection passes across all 826 trees (representative of `architecture`, `usecase-boundaries`, `command_boundary`, and `library_output`):

| Variant | Total time for 4 passes | Speedup |
| --- | --- | --- |
| 4 repeated `ast.walk` passes | 1,151.49 ms | - |
| 4 node index lookups | 1.82 ms | 631x (~1,149.66 ms saved) |

## 3. Rule Analysis (Spike Q1)

| Rule | Current AST Access | Target Node Kinds | Order / Scope Requirements |
| --- | --- | --- | --- |
| `RULE-architecture` | 4 `ast.walk` calls in `_imports` | `ast.Import`, `ast.ImportFrom`, `ast.Attribute`, `ast.Call` | Order: document order preserved by index; no parent links needed. |
| `RULE-usecase-boundaries` | `ast.walk` in `_imports`, and `constructor` walk | `ast.Import`, `ast.ImportFrom`, `ast.Assign` | Module imports can use index; constructor walk is subtree-specific. |
| `RULE-advisory-unique-code` | `parse_module` (top-level), `_calls` (recursive) | `ast.ClassDef`, `ast.Assign`, `ast.AnnAssign`, `ast.Import`, `ast.ImportFrom`, `ast.Call` | `_calls` tracks enclosing function scope for lazy imports (`local`). Can check index for `ast.Call` existence or lack of function imports to skip recursion. |
| `RULE-cli-tool-command-boundary` | `ast.walk` over `tree` | `ast.FunctionDef`, `ast.AsyncFunctionDef` | Evaluates `decorator_list`. Document order preserved. |
| `RULE-cli-tool-library-output` | `_aliases` (`ast.walk`), `check` (`ast.walk`) | `ast.Import`, `ast.ImportFrom`, `ast.Call` | Replaces both walks with index queries. |
| `RULE-cli-tool-heavy-imports` | Iterates `tree.body` directly | - | Does not `ast.walk`; unaffected. |
| `RULE-cli-tool-layers` | Custom recursive `_imports` | `ast.Import`, `ast.ImportFrom` | Skips `if TYPE_CHECKING:` blocks. Custom walk can remain rule-internal. |

## 4. Proposed Accessor Design (Spike Q2)

- `WorkspaceCache.get_python_nodes(path: str | Path, *types: type[ast.AST]) -> tuple[ast.AST, ...]`:
  - Lazily builds `dict[type[ast.AST], tuple[ast.AST, ...]]` on first node request for `path`.
  - Stored beside `_ast_cache` and cleared on `invalidate`, `write_text`, `invalidate_all`.
  - Returned tuples are immutable references to shared AST nodes (inheriting the read-only contract of `ADR-share-one-read-only-parsed-tree-per-python-file`).
  - Filtering: returns concatenation of nodes matching any of the requested `*types`, in document traversal order.
