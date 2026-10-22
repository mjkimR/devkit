---
id: PLAN-spec-rules-shared-document-index
spec: SPEC-spec-rules-shared-document-index
---

# Technical Plan: `SPEC-spec-rules-shared-document-index` Share one document index across a rules run

## 1. Constitution & Invariant Review

- Follows `ADR-share-document-index-and-defer-catalog-build-in-rules-run`: `DocumentIndex` is shared across rules within a single `RuleContext` via `WorkspaceCache.get_or_compute`, and `DocumentCatalog` build is deferred in `RULE-markdown-link`.
- Preserves `ADR-content-keyed-document-parse-memo`: exact content-keyed hash verification in `ParseMemo` is maintained without timestamp heuristics.
- Preserves package boundaries: `devkit-agt` remains completely decoupled from `devkit-spec` by providing a generic `get_or_compute` cache slot on `WorkspaceCache`.

## 2. Architecture Overview & Impact

- **`WorkspaceCache`** (`packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py`):
  - Adds `get_or_compute(key: str, factory: Callable[[], T]) -> T`.
  - Retains computed objects in `_computed_cache: dict[str, Any]`.
  - Clears `_computed_cache` on `invalidate(path)` and `invalidate_all()`.
- **`document_index(ctx)`** (`packages/devkit-spec/src/devkit_spec/features/governance/services/documents.py`):
  - Calls `ctx.cache.get_or_compute("spec.document_index", lambda: DocumentIndex.load(...))`.
  - Guarantees `DocumentIndex.load` executes at most once per rules run.
- **`MarkdownLinkRule`** (`packages/devkit/src/devkit_agt/features/rules/services/builtins/markdown_link/rule.py`):
  - Defers `catalog = ctx.cache.get_catalog(root)` until a local target does not exist and requires candidate lookup.
  - Skips whole-workspace catalog builds for runs with valid targets.
- **Living Spec**:
  - Reflects the shared document index and deferred catalog build in `CAP-GOV-rules-engine` and `CAP-GOV-spec-rules`.

## 3. Component & Interface Design

```python
# devkit_agt.features.rules.repositories.workspace.cache.WorkspaceCache
class WorkspaceCache:
    def __init__(self, ...) -> None:
        ...
        self._computed_cache: dict[str, Any] = {}

    def get_or_compute(self, key: str, factory: Callable[[], T]) -> T:
        """A run-scoped cached object computed once and retained until invalidation."""
        if key not in self._computed_cache:
            self._computed_cache[key] = factory()
        return cast(T, self._computed_cache[key])

    def invalidate(self, path: str | Path) -> None:
        ...
        self._computed_cache.clear()

    def invalidate_all(self) -> None:
        ...
        self._computed_cache.clear()
```

## 4. Storage & State Management

- In-memory only: `_computed_cache` lives on the `WorkspaceCache` instance for the lifetime of `RuleContext`.
- No new persistent files or state directories created.

## 5. Error Handling & Edge Cases

- **File modification during fix**: `write_text` calls `invalidate(path)`, which purges `_computed_cache`. Convergence rechecks automatically re-evaluate fresh indices.
- **Exceptions in factory**: If `factory()` raises an error, it propagates immediately and is not cached.

## 6. Verification & Test Plan

- **WorkspaceCache tests** (`packages/devkit/tests/unit/features/rules/workspace/test_cache.py` or integration test):
  - Verify `get_or_compute` computes once, returns cached result on second call, and invalidates on `write_text` and `invalidate_all`.
- **MarkdownLinkRule tests** (`packages/devkit/src/devkit_agt/features/rules/services/builtins/markdown_link/tests/test_rule.py`):
  - Verify `_catalog` is `None` on `WorkspaceCache` after evaluating a document with all valid links.
  - Verify broken link candidate finding still builds catalog and returns candidate.
- **Spec governance tests** (`packages/devkit-spec/tests/unit/features/governance/`):
  - Verify `document_index(ctx)` returns identical object across calls and only calls `DocumentIndex.load` once.
- **End-to-End & Regression**:
  - `just test-affected` and `just rules-check` pass cleanly.
