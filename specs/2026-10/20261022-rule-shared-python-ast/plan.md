---
id: PLAN-rule-shared-python-ast
spec: SPEC-rule-shared-python-ast
---

# Technical Plan: `SPEC-rule-shared-python-ast` Parse each Python file once per rules run

## 1. Constitution & Invariant Review

None. The design implements `ADR-share-one-read-only-parsed-tree-per-python-file`,
`ADR-parse-cached-bytes-once-and-memoize-the-outcome` and `ADR-resolve-rule-paths-once-per-run` as accepted. It adds
one public method to `WorkspaceCache` and changes no `MUST` of `CAP-GOV-rule-authoring`,
`CAP-GOV-evaluation-lifecycle` or `CAP-GOV-rules-engine`; their text gains the accessor, its read-only contract and
the per-run resolution memo. The rules keep reading through `ctx.cache` (`CAP-GOV-rule-authoring` §2), which the two
devkit-dev rules did not do before.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py` | `get_python_ast`; tree and error memo; per-run resolution memo used by `_key` and `read_bytes`; `write_text` resolves afresh; invalidation clears both memos |
| `packages/devkit/src/devkit_agt/features/rules/models/contracts.py` | `RuleContext._relative` resolves only when the lexical form is outside the workspace |
| `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/rule.py` | `inspect_architecture(..., *, cache=None)`; parse through the cache; the rule passes `ctx.cache` |
| `tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/rule.py` | `Index(root, config, cache)` and `inspect_usecases(..., *, cache=None)`; parse through the cache |
| `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/` | `parse_module(rel, tree)`; the rule calls the accessor |
| `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/{layers,heavy_imports,command_boundary,library_output}/rule.py` | replace `ast.parse(ctx.cache.read_text(path), ...)` with `ctx.cache.get_python_ast(path)` |
| `docs/capabilities/governance/` | accessor, read-only contract, invalidation and resolution memo |
| `.devkit/installation.json` and `.devkit/managed/` | refreshed by `devkit sync` after the bundle sources change |

No new dependency.

## 3. Component & Interface Design

```python
class WorkspaceCache:
    def get_python_ast(self, path: str | Path) -> ast.Module:
        """The parsed module of a Python file, shared for the run; never modify it.

        Parses ``read_bytes(path)`` once under the workspace-relative POSIX name (the resolved absolute path outside
        the workspace). Raises a fresh, equal ``SyntaxError``/``ValueError`` on every call for a file that does not
        parse, and ``FileNotFoundError`` for a missing file (not memoized).
        """
```

- Memo layout: `_ast_cache: dict[str, ast.Module | tuple[type[Exception], tuple]]` keyed by the resolved key. An
  error is stored as its type and `args`; each call raises `type(*args)`. `SyntaxError(*args)` rebuilds `msg`,
  `filename`, `lineno`, `offset`, `text`, `end_lineno` and `end_offset` from `args`, so the raised error equals the
  original in type, arguments and attributes, and it carries no traceback of an earlier rule.
- Resolution memo: `_resolved: dict[str | Path, Path]` keyed by the path argument as given (`Path(path)` when a
  string, so `"a.py"` and `Path("a.py")` share an entry). `_resolve_path` uses it; `write_text` calls an uncached
  `_resolve_fresh`. `invalidate` and `invalidate_all` clear it whole. `find_files`, `get_catalog` and the
  `DocumentCatalog` keep their own resolution (Non-Goal 5).
- `RuleContext._relative`: compute the lexical `normpath`; when it is relative to the root return it; otherwise try
  `absolute.resolve()`. The order and candidates are unchanged, so every input whose resolution succeeds maps as
  before.
- Rule-local entry points: `inspect_architecture(root, config_path=..., *, cache: WorkspaceCache | None = None)` and
  `inspect_usecases(root, config_path=..., *, cache=None)` create `WorkspaceCache(root)` when `cache` is `None`. The
  devkit-dev rules keep their `Path.rglob` enumeration; only `ast.parse(path.read_text())` becomes
  `cache.get_python_ast(path)`.

## 4. Error Handling & Edge Cases

| Case | Behavior |
| --- | --- |
| Syntax error | memoized; `architecture` reports `cannot parse source: <error>` (now also on `ValueError`), `usecase-boundaries` aborts with one finding naming the file, `unique_code` and the catalog rules skip |
| Missing file (broken symlink listed by `rglob`) | `FileNotFoundError`, as `path.read_text()` raised before; `usecase-boundaries` reports it as before (`OSError`) |
| BOM, PEP 263 cookie, invalid UTF-8 | parsed as CPython reads source (accepted change, D6) |
| Symlink retargeted outside the cache mid-run | keeps its first key until an invalidation (accepted, `ADR-resolve-rule-paths-once-per-run`) |
| In-workspace symlink loop passed to `_relative` | lexical name instead of `RuntimeError` |

## 5. Verification & Test Plan

- `packages/devkit/tests/integration/features/rules/workspace/test_cache.py`: AC-01 to AC-04.
- `packages/devkit/tests/integration/features/rules/engine/test_context.py`: AC-05.
- Each migrated rule's `tests/test_rule.py`: a shared-tree test (AC-06) and the unparsable-file behavior (AC-07);
  the existing tests unchanged.
- `scratch/count_parse.py` (ignored, method recorded in `evidence.md`): AC-08.
- `devkit rules check --format json` before and after, compared with `cmp`: AC-09; 7 timed runs each: AC-10.
- `just lint` and `just check` for devkit, devkit-dist, devkit-dev and devkit-catalog; `just test-affected`;
  `uv run devkit rules check`; `uv run devkit rules test`; `uv run devkit sync --check`; `git diff --check`: AC-06
  and AC-11.
