# Spike evidence: target-scoped rules

Measured on `plan-lint-clean-target-scoped-rules` at 514bdea1 (macOS, Python 3.12, this repository). Probe scripts ran
in the ignored `probe/` directory and were removed; their method is described below.

## 1. Baseline: `devkit workflow next` on a docs-only unit

`lint-clean` runs only at stages that declare it (`sdd-spec-feature`: the specify exit and the build-verify exit), so
a proposal unit in Planning never pays for it (`workflow next` on this proposal: 0.13 s). A spec unit evaluates it at
every call:

| Command | real |
| --- | --- |
| `uv run devkit workflow next --unit specs/2026-10/20261022-writing-style-rules` | 3.74 s |

The unit holds `spec.md`, `plan.md`, `tasks.md`, `reconcile.md`, one decision and six envelopes: 11 targets, no Python.

## 2. Per-rule cost of the same targeted run

Method: `run_project_rules(root, targets=<the unit's files>)` with `evaluator._check_rules` wrapped to time each rule
(4.38 s total under the wrapper; 0 violations, 0 problems).

| Rule | s | Reads | Reports on |
| --- | --- | --- | --- |
| `RULE-usecase-boundaries` | 0.90 | `.devkit/architecture.toml`, every `*.py` under declared roots (own `rglob`, own `ast.parse`) | any file, targets ignored |
| `RULE-architecture` | 0.83 | `.devkit/architecture.toml`, `packages/*/src`, `tools/*/src` and package `tests/` `*.py`, `bundle.toml`, `pyproject.toml` | any file, targets ignored |
| `RULE-advisory-unique-code` | 0.80 | every `*.py` (`find_files`) | targeted `*.py` only (`is_file_targeted`) |
| `RULE-document-reference` | 0.78 | Markdown document index | targeted documents |
| `RULE-id-convention` | 0.27 | Markdown | targeted |
| `RULE-markdown-link` | 0.21 | Markdown catalog | targeted |
| 12 other rules | 0.57 | Markdown, receipt, targets | targeted |

The first three are about 2.5 s and need Python input that a documentation unit never holds. None of them reads a
Markdown file, so no Markdown-only change can alter their result (Q2).

## 3. How the rules apply targets

- **Targets ignored**: `RULE-architecture` and `RULE-usecase-boundaries` call `inspect_architecture(root)` /
  `inspect_usecases(root)` and report every finding of the workspace, whatever the targets.
- **Whole-workspace input, targeted output**: `RULE-advisory-unique-code` indexes every Python file but reports only
  declarations in targeted files; with no `*.py` target its result is empty by construction.
- **Targeted Markdown rules**: `cli_contract`, `markdown_link`, `file_length`, the `authoring` rules and every `spec`
  rule (through `devkit_spec.features.governance.services.documents.reportable`) report only targeted files.
- **Explicit targets only**: `secret_leak`, `clean_artifacts` read `ctx.changed_files`.

`lint-clean` (`workflow/usecases/lint.py`) passes the unit's files to `run_project_rules(root, targets=files)`; the
engine expands them, applies `[rules] exclude` in `RuleContext`, and `evaluate_rules` runs every rule active in the
phase. Nothing between the targets and the rule list narrows the rules today.

## 4. Simulated scoping: equivalence and time

Method: `evaluate_rules` wrapped to drop a rule whose declared patterns match no expanded target, with the
declarations of the proposal (`architecture`: `**/*.py`, `**/pyproject.toml`, `**/bundle.toml`,
`.devkit/architecture.toml`; `usecase-boundaries`: `**/*.py`, `.devkit/architecture.toml`; `unique-code`: `**/*.py`).
Each target set ran unscoped, then scoped, in one process; violations compared as (rule, file, line, message,
severity).

| Targets | unscoped | scoped | equal | skipped |
| --- | --- | --- | --- | --- |
| `specs/2026-10/20261022-writing-style-rules` | 3.59 s | 0.85 s | yes (0/0) | all three |
| `docs/proposals/PROP-lint-clean-target-scoped-rules` | 3.20 s | 0.97 s | yes | all three |
| `docs/capabilities/governance` | 3.26 s | 0.91 s | yes | all three |
| `packages/devkit/.../rules/services/evaluator.py` | 3.40 s | 3.25 s | yes | none |
| `.devkit/architecture.toml` | 3.45 s | 2.45 s | yes | `unique-code` |
| `tools/devkit-dev` | 3.27 s | 3.31 s | yes | none |
| spec unit + `packages/devkit/pyproject.toml` | 3.32 s | 1.67 s | yes | `unique-code`, `usecase-boundaries` |
| `docs` | 3.69 s | 3.67 s | yes | none (`docs/materials/**/*.py` exists) |

On this clean base the scoped and unscoped results are identical, which only shows that scoping hides nothing here;
the seeded tests of the acceptance outcomes cover the difference. That difference is limited to findings a skipped
target-ignoring rule reports for files outside the targets: an architecture violation in a Python file, pre-existing
or introduced by the unit's own uncommitted code, is reported by a full run, by every snapshot run (commit gate, CI)
and by a targeted run that names any Python file, and no longer by a documentation-only targeted run such as
`lint-clean` at the build-verify exit.

## 5. Cold measurement

The section 4 scoped runs followed an unscoped run in one warm process. Measured cold instead, each run a fresh
interpreter on Apple M4 Pro, median of three:

| Command | real |
| --- | --- |
| `.venv/bin/devkit workflow next --unit specs/2026-10/20261022-writing-style-rules` | 3.65 s |
| the same command in a fresh process with the three rules' skip simulated in `evaluate_rules` | 1.37 s |

## 6. Overlap with `SPEC-rule-shared-python-ast`

That proposal shares one `ast.parse` per file through `WorkspaceCache`; it changes how the Python rules read, not
whether they run. The two touch the same three rule modules (here: one constructor argument each) and compose: after
it, the remaining Python runs are cheaper, and documentation runs skip them. No design dependency; the
`workflow next` bound in the acceptance outcomes holds with or without it.
