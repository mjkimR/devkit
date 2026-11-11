---
id: PLAN-shared-fingerprinted-memo
spec: SPEC-shared-fingerprinted-memo
---

# Technical Plan: `SPEC-shared-fingerprinted-memo` One fingerprinted memo store for docs parse and rule facts

## 1. Constitution & Invariant Review

None. `devkit_core.core` holds generic filesystem primitives and is importable by every package
(`ARCH-05-2-components`); the new module uses only the standard library, so `devkit-core` keeps importing no
application package. Both memos already import `devkit_core.core`, so no package or feature edge changes and
`.devkit/architecture.toml` is not edited. No decision changes: the memo locations, formats and writer policy of
`ADR-document-system` and `ADR-rules-run-workspace-cache` stay; the converged path and envelope rule (decision D1,
user) is restated in `CAP-DOCS-document-model` 3.4.3 and `CAP-GOV-rules-engine` 5.3 in place.

## 2. Architecture Overview & Impact

- `packages/devkit-core/src/devkit_core/core/memo.py` (new): `PathRefusal` and `EnvelopeProblem` (`StrEnum`, the
  value a short English reason), `safe_memo_path` and `envelope_problem` (`SPEC-shared-fingerprinted-memo` section 3).
  Not added to `devkit_core/core/__init__.py`, which a concurrent Unit edits; callers import the module path.
- `packages/devkit-docs/src/devkit_docs/features/documents/repositories/memo.py`: `memo_path` and
  `ParseMemo._problem` replaced by the helper calls; `_read` keeps the `lstat` for its read errors and drops the
  non-regular branch the helper now owns.
- `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/facts.py`: `memo_path` delegates the
  component walk; the inline envelope condition becomes `envelope_problem(...) is not None`; `_FRAMEWORK` gains
  `capture_facts_dependency("core.memo", <devkit_core.core.memo source>)`.

## 3. Component & Interface Design

```python
class PathRefusal(StrEnum):
    NO_TRANSIENT = "no .devkit/transient/ directory"
    MISSING = "a missing directory"
    SYMLINK = "a symbolic link"
    NOT_DIRECTORY = "a non-directory on the way"
    MOVED = "a directory that resolves elsewhere"
    NOT_REGULAR = "not a regular file"

class EnvelopeProblem(StrEnum):
    SHAPE = "not the expected shape"
    VERSION = "another version"
    FINGERPRINT = "another fingerprint"

def safe_memo_path(root: Path, parts: Sequence[str], *, create: bool) -> Path | PathRefusal: ...
def envelope_problem(loaded: object, version: int, fingerprint: str) -> EnvelopeProblem | None: ...
```

The `SHAPE` and `VERSION` values equal the docs memo's current reason text, so its log lines stay byte-identical;
only `FINGERPRINT` is mapped by the docs memo to "another parser fingerprint".

## 4. Verification & Test Plan

- `packages/devkit-core/tests/integration/core/test_memo.py`: every `PathRefusal` case of AC-01, creation only below
  `transient/`, no log record; `packages/devkit-core/tests/unit/core/test_memo.py`: every `EnvelopeProblem` case of
  AC-02.
- Existing `packages/devkit-docs/tests/unit/features/documents/test_memo.py`,
  `packages/devkit-docs/tests/integration/features/documents/test_memo_index.py` and
  `packages/devkit/tests/integration/features/rules/workspace/test_file_facts.py` pass; `test_file_facts.py` gains
  the extra-key discard case and `test_memo_index.py` the `.devkit/` symlink case (D1).
- Differential evidence: `evidence/memo_harness.py` on the handoff head 114177caa569febbdc50018276193e43906325b4
  (`evidence/before.md`, committed before any source edit) and on the changed head (`evidence/after.md`), compared
  row by row (AC-03, AC-04).
- `just lint`, `just typecheck`, `just test-affected` (with its `mode=full` fallback),
  `uv run devkit rules check --ci --base main`, `uv run devkit sync --check`.
