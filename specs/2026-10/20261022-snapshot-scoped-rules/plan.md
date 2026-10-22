---
id: PLAN-snapshot-scoped-rules
spec: SPEC-snapshot-scoped-rules
---

# Technical Plan: `SPEC-snapshot-scoped-rules` Scope snapshot rules runs to their changed paths

## 1. Constitution & Invariant Review

Follows `ADR-scope-snapshot-runs-to-diff-paths-including-deletions` and supersedes the follow-up in `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`.
`CAP-GOV-rules-engine` principle 5 (one evaluation path) is preserved: scoping logic lives in `evaluate_rules` (via `scope_rules`) which all snapshot and working-tree callers execute.

Invariants maintained:
- Evaluation targets (`RuleContext.targets`) only name files present in the snapshot workspace.
- Deletion-only commits evaluate whole-workspace rules matching deleted paths without short-circuiting.
- Project configuration (`.devkit/config.toml`) and installation receipt (`.devkit/installation.json`) changes disable rule skipping.
- Whole-workspace runs (`targets=None, snapshot=None`) remain completely unscoped.

## 2. Architecture Overview & Impact

- `devkit-agt` rules feature (`packages/devkit/src/devkit_agt/features/rules/`):
  - `services/evaluator.py`:
    - Update `scope_rules(ctx, rules, modified=())` to support snapshot scoping:
      - When `ctx.snapshot is not None`, construct candidate `names` from `ctx.targets` plus `ctx.snapshot.deleted`.
      - Check `CONFIG_PATH in names or RECEIPT_PATH in names` to disable rule skipping.
      - Return `(selected, skipped)` as for working-tree targeted runs.
  - `usecases/project.py`:
    - In `_run(...)`, update `has_work` calculation to account for deleted paths in snapshots:
      `has_work = bool(changed or (snapshot is not None and bool(snapshot.deleted)))`.
    - When `targets` is empty in a snapshot with deletions, ensure `RuleContext` is instantiated so `evaluate_rules` runs.
  - `models/contracts.py`:
    - Ensure `RuleContext` supports snapshot runs where `changed_files` is empty but `snapshot.deleted` is non-empty, so `has_targets` or snapshot presence correctly triggers `scope_rules`.
  - `repositories/workspace/snapshot.py`:
    - In `_changes`, ensure typechanges (`T`) and all diff paths are captured into `changed` or `deleted` so non-regular file transitions are visible to scoping.
- Tests:
  - Unit tests in `packages/devkit/tests/unit/features/rules/engine/test_scoping.py` covering snapshot scoping (no matching inputs skips rule; matching changed or deleted file runs rule; config or receipt changes run all rules; deleted files absent from targets).
  - Integration tests in `packages/devkit/tests/integration/features/rules/engine/test_project.py` covering in-place and materialized snapshot runs with deletions-only, additions, and modifications.
- Living Spec:
  - Update `docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md` and `CAP-GOV-rules-engine.md`.

## 3. Component Breakdown & Interface Contracts

```python
# devkit_agt.features.rules.services.evaluator
def scope_rules(ctx: RuleContext, rules: Sequence[Rule], modified: Iterable[str] = ()) -> tuple[list[Rule], list[str]]:
    if ctx.snapshot is None:
        if not ctx.has_targets:
            return list(rules), []
        names = list(ctx.targets)
    else:
        names = list(ctx.targets) + list(ctx.snapshot.deleted)
        if not names:
            return list(rules), []

    names.extend(relative for path in modified if (relative := ctx.relative_path(path)) is not None)
    if CONFIG_PATH in names or RECEIPT_PATH in names:
        return list(rules), []

    selected: list[Rule] = []
    skipped: list[str] = []
    for rule in rules:
        inputs: tuple[str, ...] | None = getattr(rule, "inputs", None)
        if inputs is None or any(match_path(pattern, name) for pattern in inputs for name in names):
            selected.append(rule)
        else:
            skipped.append(rule.id)
    return selected, skipped
```

## 4. Verification & Test Plan

- Unit tests: `just test devkit unit/features/rules/engine/test_scoping.py`
- Integration tests: `just test devkit integration/features/rules/engine/test_project.py`
- Pre-commit gate check: `just rules-check --staged`
- Snapshot CI check: `just rules-check --ci --base HEAD~1`
- Full affected test run: `just test-affected`
