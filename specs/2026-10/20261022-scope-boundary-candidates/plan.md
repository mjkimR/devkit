---
id: PLAN-scope-boundary-candidates
spec: SPEC-scope-boundary-candidates
---

# Technical Plan: `SPEC-scope-boundary-candidates` Drop entrypoint candidates once a spec declares its code boundary

## 1. Constitution & Invariant Review

None. No accepted ADR or `docs/architecture/` invariant covers entrypoint candidates; `ADR-worktrees-branches-and-scope`
governs registry maintenance and is unaffected. `CAP-COLL-work-scope-registry` rule 2 ("Unknown is not no overlap")
holds: a bundle with declared code has a known code side, and every unresolved reason stays reported
(`SPEC-scope-boundary-candidates` Non-Goal 1). The `_Boundary` parse and path contract stay with
`CAP-TRACE-code-entrypoints` unchanged.

## 2. Architecture Overview & Impact

- `devkit_spec.features.scope.usecases.inputs`: `from_spec` already collects the `tasks.md` `_Boundary` entries
  before the document targets. When at least one entry became a `declared-code` path, it passes
  `candidates=False` to `_add_doc_targets`, which then records the document targets and the `no-entrypoints`
  reason as before but adds no `candidate` code path. `from_proposal` and a bundle without declared code keep
  `candidates=True`. The module docstring states the rule.
- `devkit_spec.features.scope.services.compare`, `models.model` and `cli.commands`: no behavior change; their
  docstrings and help text are checked so that "candidate" is described as the pre-boundary estimate.
- Every caller builds a spec's set through `from_spec` (`collect` for `register` and `update`,
  `CompareScopesUseCase`, `QueryScopesUseCase --spec`), so one change covers AC-01 to AC-05.
- Living Spec: `CAP-COLL-work-scope-registry` §4.1 (input table and a sentence on when candidates apply) and §4.2
  (a spec with declared code compares declared and observed code). No new dependency.

## 3. Component & Interface Design

```python
def _add_doc_targets(
    root: Path, scope: ScopeSet, targets: list[tuple[str, str]], stage: Stage, *, candidates: bool = True
) -> None: ...
```

In `from_spec`, `candidates = not any(path.source is Source.DECLARED_CODE for path in scope.code)` after the
`_Boundary` pass. Output lines, JSON keys, codes, the record schema and `Source` values are unchanged.

## 5. Error Handling & Edge Cases

- A `tasks.md` whose `_Boundary` entries are all `N/A`, placeholders, excluded-tree or invalid paths declares no code:
  candidates stay (AC-03, Non-Goal 3).
- Missing or skeleton `tasks.md`: `missing-tasks` as before, candidates stay (AC-03).
- A target without `entrypoints` keeps `no-entrypoints` whether or not candidates are added (AC-05).
- A record registered before the change keeps stored candidates until its next `update` (Non-Goal 2).

## 6. Verification & Test Plan

- Red then Green in `packages/devkit-spec/tests/integration/features/scope/test_inputs.py`: declared code drops the
  candidates (AC-01), a candidate-only path no longer overlaps (AC-02), candidates stay for a proposal, missing,
  skeleton and code-less `tasks.md` (AC-03), `no-entrypoints` stays with declared code (AC-05). The existing
  `test_from_spec` expectation of `src/shared.py` as a candidate changes to its absence.
- `packages/devkit-spec/tests/integration/features/scope/test_cli.py`: the `compare` pair of the fixture proposal
  one and spec bundle s drops to `code=1`; a registered bundle's `update` records an observed path outside its
  boundary and overlaps a set whose declared code covers it (AC-04).
- `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`, `uv run devkit rules check`,
  `git diff --check`; AC-06 by `spec-review` and the reconcile check.
