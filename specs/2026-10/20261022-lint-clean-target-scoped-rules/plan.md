---
id: PLAN-lint-clean-target-scoped-rules
spec: SPEC-lint-clean-target-scoped-rules
---

# Technical Plan: `SPEC-lint-clean-target-scoped-rules` Scope target runs to the rules their targets can affect

## 1. Constitution & Invariant Review

None beyond the two accepted ADRs, which this plan implements as decided:
`ADR-rules-declare-their-input-files-undeclared-rules-always-run` (the declaration) and
`ADR-scope-only-explicit-working-tree-targets-in-the-evaluator` (where scoping applies). `CAP-GOV-rules-engine`
principle 5 (one evaluation path) holds: scoping lives in `evaluate_rules`, which every caller reaches. The `Rule`
protocol, the snapshot gates and the `check`/`fix` output are unchanged. `CAP-GOV-evaluation-lifecycle` §3
(Targets: "checked as is, by every rule") and §4 (a targeted `hygiene` run "still evaluates the rule") change with
the scoping contract, as the ADRs record. Layering: models gain the validation, the evaluator (service) reads it,
the use cases and CLI only expose it.

## 2. Architecture Overview & Impact

- `devkit-agt` rules feature (`packages/devkit/src/devkit_agt/features/rules/`):
  - `models/errors.py`: `RuleDefinitionError` derives from `RuleProblem` (gains `rule_id`; still raised at
    construction), so policy validation can collect it.
  - `models/policy.py`: `check_inputs(rule_id, value)` raises `RuleDefinitionError` unless `value` is `None` or a
    non-empty tuple of patterns `validate_pattern` accepts; `validate_inputs(rules)` collects one problem per loaded
    rule whose `getattr(rule, "inputs", None)` fails, with the rule's source file; `validate_policy` adds them, so
    `evaluate_rules`, `phases` and `explain` share the check. Its error list widens to `RuleProblem`.
  - `models/contracts.py`: `RuleContext.targets`, the explicit targets workspace-relative and before `[rules]
    exclude`; `RuleContext.relative_path(path)`, the public form of the existing normalization.
  - `services/builtins/base.py`: `BaseRule.inputs: tuple[str, ...] | None = None`, checked in `__post_init__`.
  - `services/evaluator.py`: `scope_rules(ctx, rules, modified=())` returns the rules to evaluate and the skipped IDs;
    `evaluate_rules` applies it after the phase filter and again before the recheck with the modified files;
    `EvaluationResult.skipped`; an `INFO` log line per evaluation that skipped rules.
  - `usecases/project.py`: `ProjectRun.skipped` (the result's); `ProjectRules.policy_errors` widens to `RuleProblem`.
  - `usecases/explain.py`, `cli/output.py`: `inputs` in the explain entry and `inputs=` on the `[RULE: ...]` line.
  - `services/testing.py`: `opened_files(root)`, a context manager recording the workspace files opened while it is
    active (a process-wide `open` audit hook installed once, active only inside the context), for the completeness
    tests of declared rules.
- Bundle rules: `inputs=` in the three constructors (`tools/devkit-dev/.../rules/architecture/rule.py`,
  `.../usecase-boundaries/rule.py`, `packages/devkit-dist/.../advisory/bundle/rules/unique_code/rule.py`), their
  guides state the inputs, their `tests/test_rule.py` cover AC-06; `devkit sync` refreshes the managed copies and
  `.devkit/installation.json`.
- `spec-rule` skill: names `inputs` for a rule that scans the workspace.
- Living Spec: `CAP-GOV-rule-authoring` §1 (`inputs`) and the testing section (`opened_files`),
  `CAP-GOV-evaluation-lifecycle` §1, §3 and §4 (scoping), Rules Reference (`explain` field, `RuleDefinitionError` row,
  `skipped`).
- No change to `packages/devkit/src/devkit_agt/features/workflow/` or `docs/decisions/`; no new dependency.

## 3. Component & Interface Design

```python
# devkit_agt.features.rules.services.builtins.base
@dataclass
class BaseRule(Rule):
    ...
    inputs: tuple[str, ...] | None = None  # workspace-relative ``**`` patterns of every file the rule reads

# devkit_agt.features.rules.models.policy
def check_inputs(rule_id: str, value: object) -> None: ...          # raises RuleDefinitionError
def validate_inputs(rules: Sequence[Rule]) -> list[RuleDefinitionError]: ...

# devkit_agt.features.rules.services.evaluator
@dataclass
class EvaluationResult:
    violations: list[Violation]
    errors: list[RuleProblem]
    skipped: list[str]  # IDs of the rules the final check pass did not evaluate

def scope_rules(ctx: RuleContext, rules: Sequence[Rule], modified: Iterable[str] = ()) -> tuple[list[Rule], list[str]]: ...

# devkit_agt.features.rules.services.testing
@contextmanager
def opened_files(root: Path) -> Iterator[set[str]]: ...  # workspace-relative POSIX paths opened for reading
```

Skip predicate for a rule with `inputs` set: `ctx.has_targets and ctx.snapshot is None and ".devkit/config.toml" not
in names and not any(match_path(p, n) for p in inputs for n in names)`, where `names` is `ctx.targets` plus the
modified files (recheck only), each workspace-relative.

`explain` text: `[RULE: ... guide=<path>|- inputs=<p1>,<p2>|-]`; JSON: `"inputs": [...] | null`.

## 5. Error Handling & Edge Cases

- `inputs` of a `BaseRule` subclass is checked at construction: the plugin loader turns the raised
  `RuleDefinitionError` into the package's `RULES_LOAD_FAILED`, as for `promote_to`. A protocol-only rule (library
  callers, `RuleRegistry.register`) is caught by `validate_policy`: `RULES_DEFINITION_INVALID` with its `rule_id`
  and source file, returned before any rule runs.
- All explicit targets excluded: `changed_files` is empty but `targets` is not; matching still uses `targets`.
- A fixer that raises: its writes are unknown, so the recheck evaluates every active rule (no scoping) and `skipped`
  is empty.
- A modified path outside the workspace is ignored for matching.
- `.devkit/config.toml` named directly or through a directory target (`.devkit`) disables scoping for the run.

## 6. Verification & Test Plan

- Unit and integration tests in `packages/devkit/tests/`:
  - `unit/features/rules/` (or the existing evaluator/base test modules): AC-01, AC-02, AC-03, AC-04 (a-e), AC-05,
    `skipped` contents, `ProjectRun.skipped`, `opened_files`.
  - `integration/features/rules/cli/test_commands.py`: AC-07 (`explain` text and JSON).
  - an integration test with a seeded architecture violation through `run_project_rules` and the synchronized
    `RULE-architecture` (AC-08).
- Bundle rule tests: each rule's `tests/test_rule.py` (AC-06), run with `uv run devkit rules test RULE-architecture
  RULE-usecase-boundaries RULE-advisory-unique-code` and through `just test-affected`.
- AC-09 equivalence: a probe script in the ignored `.devkit/transient/` scratch path compares
  `run_project_rules(root, targets=...)` with scoping and with `scope_rules` patched to keep every rule, over the
  eight target sets, plus `devkit rules check` without targets before and after; recorded in
  `evidence.md` of this unit.
- AC-10: three cold runs each of `.venv/bin/devkit workflow next --unit specs/2026-10/20261022-writing-style-rules` on
  this head and on the base (scoping disabled through the same patch in a fresh interpreter, equivalent to the base's
  evaluator), medians recorded in `evidence.md`.
- AC-11: `uv run devkit rules check <unit>` and `git diff --name-only 3015be11` against the excluded boundaries.
- Checks: `just lint` and `just check` for `agt`, `dist` and `devkit-dev`; `just test-affected`;
  `uv run devkit rules check`; `uv run devkit sync --check`; `git diff --check`.
