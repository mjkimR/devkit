---
reconcile_id: REC-lint-clean-target-scoped-rules
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
  - file: docs/development/reference/rules-library.md
    resolution: modified
---

# Reconcile: `SPEC-lint-clean-target-scoped-rules`

## Living Spec changes

- `CAP-GOV-rule-authoring`:
  - §1 gains "Optional `inputs`": what to declare, the skip it enables, `None` as "runs in every run", the
    construction check (`RULES_DEFINITION_INVALID`, a loading error for a `BaseRule` package), the policy check of a
    protocol-only rule, and that `devkit rules explain` prints the declaration (AC-01, AC-02, AC-07).
  - §2 names `ctx.targets` and `ctx.relative_path` (`reconcile-check-01.yaml` P3).
  - §6 names `opened_files` and the three tests a declared rule carries (AC-06).
- `CAP-GOV-evaluation-lifecycle`:
  - §1 adds the `inputs` validation to step 2, the scoping to step 3 and the scoped recheck to step 4.
  - §2 states what the recheck evaluates: the targets plus the modified files, or every active rule after a failed fix
    (AC-05).
  - §3 replaces "checked as is, by every rule" with "by every rule the run evaluates" and adds the "Target scoping"
    contract. It covers which runs scope, matching before `[rules] exclude`, the `.devkit/config.toml` exception,
    unscoped whole-workspace and snapshot runs, the accepted loss of findings outside documentation-only targets, and
    `skipped` with its `INFO` log and unchanged stdout and JSON (AC-03, AC-04, AC-08).
  - §4 says a targeted `hygiene` run evaluates a parked rule unless scoping skips it.
- `CAP-GOV-rules-engine`: principle 5 adds that scoping lives in `evaluate_rules`, so every caller agrees on which
  rules run. The layout comments name the `inputs` validation, the scoping, `opened_files` and `BaseRule.inputs`.
- Rules Reference (`docs/development/reference/rules.md`): `check` points to target scoping. `explain` documents the
  `inputs=` field, the `inputs` JSON key and the declaration among what it prints (AC-07). The `RuleDefinitionError`
  row covers `inputs` and the collected protocol-only case.
- Rules library reference (`docs/development/reference/rules-library.md`): documents `run.skipped` and
  `EvaluationResult.skipped`, `validate_policy` returning `RuleDefinitionError`, and `opened_files`.
- Entrypoints (`spec-entrypoints`): `CAP-GOV-evaluation-lifecycle` gains `services/evaluator.py`,
  `CAP-GOV-rule-authoring` gains `services/builtins/base.py` and `services/testing.py`, and `CAP-GOV-rules-engine`
  gains the package `__init__.py` and `usecases/project.py` (all under `packages/devkit/src/devkit_agt/features/rules/`).
  Rejected candidates: models, CLI output, `explain.py` and tests are helpers, not doorways. The bundle rule
  directories and the `spec-rule` skill belong to their own bundles' documents. `.devkit/installation.json` is
  generated.
- Bundle-owned guidance, outside `docs/` and so not a target here: the three rule guides state their inputs, and the
  `spec-rule` skill (`SKILL.md`, `references/templates.md`) names `inputs` and its tests.

## No-impact documents

- `CAP-DLV-workflow-orchestration` (Lint check) and `CAP-DLV-workflow-definitions` (`lint-clean`) state that
  `lint-clean` runs `run_project_rules` on the unit's files and reports their violations. That still holds; which
  rules a targeted run evaluates is the governance contract, which those documents defer to through
  `CAP-GOV-rules-engine`. `packages/devkit/src/devkit_agt/features/workflow/` did not change.
- `CAP-GATE-commit-gates`: the `rules-check` gate evaluates a staged snapshot, which is never scoped.
- `docs/architecture/`: no constraint names the rule set a run evaluates. `ARCH-08-1-agent-output` holds because
  stdout and JSON of `check` and `fix` do not change, and the skip is an `INFO` log line.
- `docs/decisions/`: both accepted ADRs are implemented as decided; neither is changed.
- Use cases: no use case step names `lint-clean`'s rule set or the rules engine's rule selection.

## Deferred work

None. The follow-ups both ADRs name have their own triggers and are not deferred work of this spec: declaring the
Markdown rules' inputs, and scoping snapshot runs with deleted paths. `SPEC-rule-shared-python-ast` is queued
separately.
