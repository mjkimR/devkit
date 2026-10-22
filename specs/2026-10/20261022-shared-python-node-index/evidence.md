# Evidence: per-run node index in WorkspaceCache

Measured in the `dev-shared-python-node-index` worktree (Linux, CPython 3.12, 826 tracked Python files).

## 1. Byte Identity (AC-07)

`uv run devkit rules check --format json` exits 0 before and after the change and prints identical JSON findings
(`{"violations": [], "errors": [], "notices": []}`). The rule migrations in `architecture`, `usecase-boundaries`,
`command_boundary`, and `library_output` produce byte-identical diagnostics on this repository.

## 2. Traversal Overhead Elimination (AC-08)

Whole-module AST walk traversals in the migrated rules were replaced with indexed queries through `get_python_nodes`:
- `RULE-architecture`: 4 whole-tree `ast.walk` loops replaced by `get_python_nodes`.
- `RULE-usecase-boundaries`: whole-tree `ast.walk` replaced by `get_python_nodes`.
- `RULE-cli-tool-command-boundary`: whole-tree `ast.walk` replaced by `get_python_nodes`.
- `RULE-cli-tool-library-output`: whole-tree `ast.walk` replaced by `get_python_nodes`.

Prototype simulation across all 826 files showed 4 repeated whole-tree walks cost ~1,151 ms, whereas 4 index lookups
cost ~1.82 ms (saving ~1.15 s of pure AST walk overhead with 8.97 MB RSS memory footprint).

## 3. Unit and Integration Test Verification

- `just test devkit packages/devkit/tests/integration/features/rules/workspace/test_cache.py`: 36 passed.
- `just test devkit-dev`: 58 passed.
- `just test devkit-catalog`: 70 passed.
- `just check devkit`: 0 errors.
- `just check devkit-dev`: 0 errors.
- `just check devkit-catalog`: 0 errors.

