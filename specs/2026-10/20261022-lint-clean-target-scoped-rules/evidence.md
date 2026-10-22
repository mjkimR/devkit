# Evidence: target-scoped rules

Measured on `dev-lint-clean-target-scoped-rules` at 1c4fd694 (handoff base 3015be11), Apple M4 Pro, macOS, Python
3.12. Probe scripts ran from the ignored `.devkit/transient/probe/` directory; their method is described below.

## 1. Equivalence (AC-09)

Method: in one process, `run_project_rules(root, targets=...)` ran unscoped (with
`devkit_agt.features.rules.services.evaluator.scope_rules` replaced by a function that keeps every rule, which is the
base's behavior) and then scoped, for each target set of
`docs/materials/2026-10/20261022-lint-clean-target-scoped-rules/spike-evidence.md` §4. Violations were compared as
(rule, file, line, message, severity) and problems as (code, rule ID, message). The proposal of §4 has since moved into
this unit, so the proposal set uses the queued `docs/proposals/PROP-rule-shared-python-ast`.

| Targets | unscoped s | scoped s | violations / problems | equal | skipped |
| --- | --- | --- | --- | --- | --- |
| `specs/2026-10/20261022-writing-style-rules` | 3.58 | 0.88 | 0 / 0 | yes | `RULE-advisory-unique-code`, `RULE-architecture`, `RULE-usecase-boundaries` |
| `docs/proposals/PROP-rule-shared-python-ast` | 3.25 | 0.86 | 0 / 0 | yes | all three |
| `docs/capabilities/governance` | 3.12 | 0.86 | 0 / 0 | yes | all three |
| `packages/devkit/src/devkit_agt/features/rules/services/evaluator.py` | 3.06 | 3.17 | 0 / 0 | yes | none |
| `.devkit/architecture.toml` | 3.15 | 2.37 | 0 / 0 | yes | `RULE-advisory-unique-code` |
| `tools/devkit-dev` | 3.25 | 3.23 | 0 / 0 | yes | none |
| spec unit + `packages/devkit/pyproject.toml` | 3.15 | 1.64 | 0 / 0 | yes | `RULE-advisory-unique-code`, `RULE-usecase-boundaries` |
| `docs` | 3.73 | 3.48 | 0 / 0 | yes | none (`docs/materials/**/*.py` exists) |
| whole workspace (no targets) | 3.43 | 3.52 | 0 / 0 | yes | none |

`devkit rules check` without targets exits 0 with `[SUMMARY: errors=0 warnings=0 infos=0 fixed=0]`, as on the base;
a whole-workspace run never scopes. The seeded difference (AC-08) is covered by
`RULE-architecture`'s `test_a_violation_outside_the_targets_is_reported_only_when_a_python_file_is_targeted`.

## 2. Performance (AC-10)

Method: three cold runs of each command, each a fresh interpreter, `real` from `/usr/bin/time -p`. The base is
measured with the same interpreter and code, scoping disabled through the replacement of section 1 (a wrapper that
patches `scope_rules`, then calls `devkit_dist.cli.cli`), so every rule runs as on the base.

| Command | runs (s) | median (s) |
| --- | --- | --- |
| `.venv/bin/devkit workflow next --unit specs/2026-10/20261022-writing-style-rules` (scoping disabled, base behavior) | 3.75, 3.69, 3.71 | 3.71 |
| `.venv/bin/devkit workflow next --unit specs/2026-10/20261022-writing-style-rules` (this change) | 1.53, 1.51, 1.48 | 1.51 |

Ratio 1.51 / 3.71 = 0.41, within the bound of 0.5. Both commands printed the same `[WORKFLOW: ...]` and `[DONE: ...]`
lines.

## 3. Declaration and boundaries (AC-07, AC-11)

- `.venv/bin/devkit rules explain RULE-architecture` prints
  `... guide=.devkit/managed/devkit-dev/rules/architecture/guide.md inputs=**/*.py,**/pyproject.toml,**/bundle.toml,.devkit/architecture.toml]`
  and `inputs` as that list in JSON; `RULE-markdown-link` prints `inputs=-`; both exit 0.
- `git diff --name-only 3015be11 HEAD` names no path under `docs/decisions/` or
  `packages/devkit/src/devkit_agt/features/workflow/`.
