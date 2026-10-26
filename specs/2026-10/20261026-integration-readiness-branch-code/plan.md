---
id: PLAN-integration-readiness-branch-code
spec: SPEC-integration-readiness-branch-code
---

# Technical Plan: `SPEC-integration-readiness-branch-code`

## 1. Constitution & Invariant Review

None conflict. The change follows the existing `INTEGRATION_RECEIPT_READER_CHANGED` design of `CAP-INT-mcp-services`:
a source the running runtime cannot evaluate is named before the readiness provider runs, and the user decides, with
separately granted authority, to run integration from a runtime built from the source's code. No `MUST` of
`docs/architecture/` or an affected capability changes, so no ADR is needed. The guard executes no source code: it
parses the rule modules and resolves imports against the installed runtime only.

Direction chosen and why (inside the agreed intent of `SPEC-integration-readiness-branch-code`): of the two candidate
directions, the diagnosis is taken; evaluating rules in a subprocess of the source worktree's environment is a
Non-Goal. Evidence: the worktree environment is the source's whole runtime (rule engine and readiness provider
included), so it would judge itself; at a build the tree checked is the merged result, which the source environment
does not hold either; and the worktree's interpreter is the one `INTEGRATION_RUNTIME_IN_WORKTREE` refuses. The user's
workaround (a runtime built from the source outside the worktree) stays the recovery and becomes the directive.

## 2. Architecture Overview & Impact

- `devkit_agt.features.integration.repositories.rule_runtime` (new): `check_rule_runtime(root, commit, sources)`
  reads the committed receipt at `commit`, takes each rule asset's module files (`plugin_module_name`, so tests are
  excluded) from the commit tree, or, when Git-ignored, from the first of `sources` whose bytes match the receipt's
  hash, parses each with `ast` and checks every top-level absolute `import` / `from ... import` against the running
  interpreter. An import is missing when its top-level package resolves (`importlib.util.find_spec`) but the module
  does not, or when a `from M import name` names neither a submodule nor an attribute of `M`. Missing imports raise
  `RuleRuntimeMismatchError`. Files that cannot be read or parsed, relative imports, the `__future__` module and
  top-level packages that do not resolve are skipped, so the provider's own `RULES_LOAD_FAILED` stays the outcome.
- `devkit_agt.features.integration.services.providers.check`: after `check_reader`, calls `check_rule_runtime` for
  the source and, at a build, for the result commit, with the worktree (when present) and the base checkout as
  sources.
- `devkit_agt.features.integration.models.errors`: `RuleRuntimeMismatchError`, code
  `INTEGRATION_RULE_RUNTIME_MISMATCH`, `actor=user`, not a guardrail, exported from `devkit_agt.features.integration`.
- Contracts: `CAP-INT-mcp-services` (stable code and its order in readiness), `CAP-GOV-evaluation-lifecycle` (snapshot
  rules import the evaluating process's installed code), `UC-drive-development-to-integration` (extension and
  scenario), `docs/development/reference/integration.md` (code table).

## 3. Component & Interface Design

```python
class RuleRuntimeMismatchError(IntegrationError):
    code = "INTEGRATION_RULE_RUNTIME_MISMATCH"
    actor = Actor.USER

def check_rule_runtime(root: Path, commit: str, sources: Sequence[Path]) -> None: ...
```

Message: `the source's synchronized rules import code this runtime does not provide: <file> imports <module>[.<name>]; ...`.
`target_files` are the rule files. Directive: obtain separately granted authority, build a runtime from the source's
code outside the worktree being removed (for example a `git archive` of the source installed into a scratch
environment) and run `devkit integration integrate <branch>` from the base checkout with it; do not edit the rules,
skip readiness or use the worktree's own runtime.

## 5. Error Handling & Edge Cases

- No receipt, an unreadable receipt or no rule asset: nothing to check (the reader check and the provider report
  receipt problems).
- `from M import name` where `M` imports with an error: treated as missing only when the error is
  `ModuleNotFoundError`/`ImportError`; any other exception is skipped (the provider reports it).
- Imports inside functions, `try` or `if` blocks are not checked: only module-level statements fail at load.

## 6. Verification & Test Plan

- Regression (Red then Green): `packages/devkit-spec/tests/e2e/features/delivery/test_integration_rule_runtime.py`
  reproduces the defect with the real `spec` provider on a synchronized repository (AC-01, AC-04, AC-03).
- `packages/devkit/tests/integration/features/integration/test_rule_runtime.py`: the fixture provider, tracked and
  Git-ignored rule modules, missing module and missing name, pull-request route, build with a result commit, skipped
  cases (AC-01 to AC-05).
- Preserved: `test_receipt_reader.py`, `test_service.py` (runtime-in-worktree) and the devkit-spec e2e integration
  suite.
- Commands: `just test-affected`, `just lint devkit`, `just check devkit`, `uv run devkit rules check --ci --base main`.
