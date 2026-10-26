---
id: PLAN-entrypoints-apply-file-codes
spec: SPEC-entrypoints-apply-file-codes
---

# Technical Plan: `SPEC-entrypoints-apply-file-codes` Entrypoints apply accepts or refuses file codes

## 1. Constitution & Invariant Review

None. The fix completes the `--code` selection of `CAP-TRACE-code-entrypoints` section 3.5 and adds one refusal with
its own code; derivation, folding and apply rules for runs without `--code` are unchanged, so no ADR is needed. The
layering holds: the use case calls two new service functions of its own feature and raises a package error.

## 2. Architecture Overview & Impact

- `features/entrypoints/services/derive.py`:
  - `adopt_nested_selectors(root, pairs, codes, documents)`, run after `fold_by_directory_selectors`: for each
    normalized `--code` and each document, an exact match with a folded pair is unfolded; a code that contains some
    pair of the document is left to `select`; otherwise, when a pair of the document is an ancestor of the code, a
    pair for the code is synthesized from the nearest such ancestor (its `spec` and `task`, or `count` and `specs`),
    with `state` from the document's declared entrypoints, `exists` from the working tree and no `folded_into`.
  - `unmatched_selectors(pairs, codes, only)`: the `--code` values that cover no selected pair (of the `only`
    documents when given).
- `features/entrypoints/usecases/derive.py`: resolves `--target` before selection, calls both functions and raises
  `EntrypointsCodeUnmatchedError` before `exclude` and `apply`, so nothing is written.
- `base/errors.py`: `EntrypointsCodeUnmatchedError` (`SPEC_ENTRYPOINTS_CODE_UNMATCHED`, `INPUT_ERROR`), next to the
  other entrypoints errors.
- `features/entrypoints/__init__.py`: exports the two functions.

Refusal over notice: the sibling selectors already refuse (`--target` outside the derived documents,
`SPEC_ENTRYPOINTS_TARGET_UNKNOWN`; a trailing-`/` code that is no directory, `SPEC_ENTRYPOINTS_PATH_INVALID`), and a
notice would still exit `0` and let `--apply` write the other `--code` paths of a run with one mistyped path.

## 3. Component & Interface Design

```python
def adopt_nested_selectors(
    root: Path, pairs: Sequence[Pair], codes: Sequence[str], documents: Mapping[str, Document]
) -> list[Pair]: ...
def unmatched_selectors(pairs: Sequence[Pair], codes: Sequence[str], only: set[str] | None = None) -> list[str]: ...
```

| Code | Mode | `[ACTION]` |
| --- | --- | --- |
| `SPEC_ENTRYPOINTS_CODE_UNMATCHED` | INPUT_ERROR | Run the same derive without --code, then pass --code paths equal to, containing or under a candidate the targeted documents list, or drop the --code values in [TARGET] |

## 4. Error Handling & Edge Cases

- A selected file that is absent is a `missing` candidate and `--apply` reports it as `reason=missing-path`.
- A selected file under a directory the document already declares is `declared`; the rerun writes nothing.
- With `--all`, folded pairs are already dropped, so a selected file under an aggregated directory is synthesized
  with that directory's count and specs.
- A `--code` that matches only pairs later dropped by `--exclude` is not unmatched; the exclusion is reported.

## 5. Verification & Test Plan

- Reproduction (kept as regression tests) in `packages/devkit-spec/tests/integration/features/entrypoints/test_cli.py`:
  a file `--code` under a directory candidate is applied (AC-01), a selected folded candidate is applied (AC-02),
  and an unmatched `--code` exits `2` with `SPEC_ENTRYPOINTS_CODE_UNMATCHED` and writes nothing (AC-03), replacing
  `test_target_without_selected_candidates_applies_nothing`.
- Unit coverage of both functions in `test_derive.py`.
- Preservation (AC-04): the entrypoints suites, through `just test-affected`.
- Checks: `just lint spec`, `just check spec`, `uv run devkit rules check`, `git diff --check`.
