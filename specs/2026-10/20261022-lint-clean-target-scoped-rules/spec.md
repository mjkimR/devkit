---
id: SPEC-lint-clean-target-scoped-rules
title: Scope target runs to the rules their targets can affect
summary: Lets a targeted rules run, such as the workflow lint-clean check, skip whole-workspace rules whose inputs the targets cannot change, so devkit workflow next stops paying for a full Python analysis on documentation-only units.
status: planned
created: 2026-10-22
related_capabilities: [CAP-GOV-rule-authoring, CAP-GOV-evaluation-lifecycle, CAP-GOV-rules-engine]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-lint-clean-target-scoped-rules] Scope target runs to the rules their targets can affect

## 1. Problem Statement & Motivation

Handed off from proposal PROP-lint-clean-target-scoped-rules on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-lint-clean-target-scoped-rules`
- **Accepted decisions**: `ADR-rules-declare-their-input-files-undeclared-rules-always-run`,
  `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`.

`devkit workflow next --unit <dir>` takes about 3.7 s on a spec unit (measured: 3.74 s on
`specs/2026-10/20261022-writing-style-rules`, 11 Markdown and YAML files, at 514bdea1 on macOS, Python 3.12; this
repository has about 820 tracked Python files and 850 Markdown files), almost all of it in the `lint-clean` check that
the spec workflows evaluate at the specify and build-verify exits. `lint-clean` already passes only the unit's files
as targets (`workflow/usecases/lint.py`, `run_project_rules(root, targets=files)`), yet a unit holding only Markdown
still pays for whole-workspace Python analysis: `RULE-architecture` and `RULE-usecase-boundaries` ignore the targets
and inspect every Python file, and `RULE-advisory-unique-code` indexes every Python file to report the targeted ones.
Together they take about 2.5 s of the run (`docs/materials/2026-10/20261022-lint-clean-target-scoped-rules/spike-evidence.md`).

When a rule declares which files its result depends on, a targeted run can skip a whole-workspace rule whose inputs
no target can change, without missing a violation the targets introduce.

### Design

- **Declaration** (`ADR-rules-declare-their-input-files-undeclared-rules-always-run`): `BaseRule` gains
  `inputs: tuple[str, ...] | None = None`, the workspace-relative patterns (the `**` grammar of `[rules] exclude`,
  checked with `validate_pattern`) of every file whose content can change the rule's findings, validated at
  construction. The `Rule` protocol is unchanged; the engine reads the attribute with `getattr`, and its policy
  validation rejects, for every loaded rule, an `inputs` that is neither `None` nor a non-empty tuple of valid
  patterns, with `RULES_DEFINITION_INVALID` before any rule runs. Declared on `RULE-architecture` (`**/*.py`,
  `**/pyproject.toml`, `**/bundle.toml`, `.devkit/architecture.toml`), `RULE-usecase-boundaries` (`**/*.py`,
  `.devkit/architecture.toml`) and `RULE-advisory-unique-code` (`**/*.py`).
- **Scoping** (`ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`): after the phase filter,
  `evaluate_rules` skips a declared rule when the run has explicit targets (`ctx.has_targets`), is not a Git
  snapshot (`ctx.snapshot is None`), no target is `.devkit/config.toml`, and no target matches one of its patterns.
  Matching uses the expanded targets before `[rules] exclude`. The fix pass uses the reduced list; the recheck decides
  again against the targets plus the files the fixes modified. Whole-workspace runs and the snapshot gates evaluate
  every rule as today. `devkit rules check FILES`, `devkit rules fix FILES`, `lint-clean` and library callers of
  `evaluate_rules` share this behavior; `workflow/usecases/lint.py` does not change.
- **Visibility**: `EvaluationResult.skipped` (and `ProjectRun.skipped`) lists the skipped rule IDs, logged at `INFO`
  (`-v`); default stdout and JSON results of `check` and `fix` are unchanged. `devkit rules explain` shows `inputs=`
  on its `[RULE: ...]` line and `inputs` in JSON.

At the build-verify (feature) and fix-verify (bugfix) exits, `lint-clean` on a documentation-only unit no longer
reports architecture and use-case boundary violations of the unit's own code outside the unit directory (accepted
with the proposal); the `rules-check` commit gate, `lint-ci-clean` and `devkit rules check <changed files>` still
report them.

## 2. User Stories

- **US-1**: As an agent running `devkit workflow next` on a documentation-only spec unit, I want the `lint-clean`
  check to skip Python-source rules no unit file can affect, so that each call stops paying about 2.5 s for analysis
  that cannot change its result.
- **US-2**: As a rule author, I want to declare the files my rule reads, so that targeted runs skip it when no target
  can change its findings and still run it whenever one can.
- **US-3**: As a maintainer, I want whole-workspace runs and the Git snapshot gates to keep evaluating every rule, so
  that no finding is lost before history.

## 3. Non-Goals

1. **Scope Excluded**: scoping Git snapshot runs (`check --staged`, `check --ci`); deleted paths are not targets there.
2. **Scope Excluded**: declaring `inputs` on the Markdown rules or the `devkit-catalog` `cli_tool` rules.
3. **Scope Excluded**: making the target-ignoring rules report only targeted files, or parsing Python faster (that is
   `PROP-rule-shared-python-ast`, including any `WorkspaceCache.get_python_ast` accessor).
4. **Scope Excluded**: new output fields in `devkit rules check` or `fix` stdout or JSON, and any change to the
   workflow feature (`lint-clean` gains scoping through `run_project_rules`).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] BaseRule validates its declaration
- **Given** a `BaseRule` subclass
- **When** it is constructed with `inputs=()`, a list, a string, or a tuple holding a pattern `validate_pattern`
  rejects (empty, leading `/`, backslash, `:`, `.` or `..` segment, partial `**`)
- **Then** it raises `RuleDefinitionError` with code `RULES_DEFINITION_INVALID`, while `inputs=None` and a non-empty
  tuple of valid patterns construct and keep the value

### [AC-02] A malformed declaration on a protocol-only rule fails the run before any rule runs
- **Given** a rule that satisfies the `Rule` protocol without subclassing `BaseRule`, whose `inputs` is a string, a
  list or an empty tuple, evaluated together with a well-formed rule
- **When** `evaluate_rules` runs
- **Then** the result's errors hold one problem with code `RULES_DEFINITION_INVALID` and that rule's ID, and neither
  rule's `check` was called

### [AC-03] A targeted working-tree run skips a declared rule no target can affect
- **Given** a rule declaring `inputs=("**/*.py",)` and an undeclared rule, both active
- **When** `evaluate_rules` runs with the explicit target `docs/a.md` only and no snapshot
- **Then** the declared rule's `check` is not called, the undeclared rule's is, and `skipped` equals exactly
  `[<declared rule ID>]`

### [AC-04] Every other run evaluates the declared rule
- **Given** the rules of AC-03
- **When** `evaluate_rules` runs with (a) the target `src/a.py`, (b) the target `src/a.py` that `[rules] exclude`
  removes, (c) the targets `docs/a.md` and `.devkit/config.toml`, (d) no targets, or (e) the target `docs/a.md` with
  a Git snapshot on the context
- **Then** both rules' `check` is called in each case and `skipped` is empty

### [AC-05] The recheck re-decides against the files fixes modified
- **Given** a rule declaring `inputs=("**/*.py",)`, an undeclared autofixable rule whose fix writes `src/b.py`, and
  the explicit target `docs/a.md` with `fix`
- **When** `evaluate_rules` runs
- **Then** the declared rule is neither checked nor fixed in the initial pass, its `check` is called in the recheck
  and its findings are returned, and `skipped` is empty

### [AC-06] The three Python-source rules declare complete inputs
- **Given** `RULE-architecture`, `RULE-usecase-boundaries` and `RULE-advisory-unique-code` with their declared
  `inputs`
- **When** each rule's `tests/test_rule.py` evaluates it through the rule test helper
- **Then** a documentation-only target set skips it; for each one of its declared patterns, a target set holding a
  file that matches that pattern reports a seeded violation; and during a whole-workspace check of a fixture holding
  every file kind the rule reads, every workspace file the rule opens (recorded by an `open` audit hook) matches one
  of its `inputs`

### [AC-07] `devkit rules explain` shows the declaration
- **Given** `RULE-architecture` (declared) and `RULE-markdown-link` (undeclared)
- **When** `devkit rules explain <RULE-id>` runs, in text and with `--format json`
- **Then** the exit code is 0, the `[RULE: ...]` line holds
  `inputs=**/*.py,**/pyproject.toml,**/bundle.toml,.devkit/architecture.toml` or `inputs=-`, and the JSON `rule`
  object holds `inputs` as that list or `null`

### [AC-08] A documentation-only targeted run no longer reports a seeded violation elsewhere
- **Given** a fixture workspace with a seeded `RULE-architecture` violation in a Python file no target names
- **When** the rules run on the whole workspace, on a target set naming another Python file, and on a
  documentation-only target set
- **Then** the first two runs report the seeded violation and the third does not

### [AC-09] Equivalence on this repository
- **Given** this repository at the integration base
- **When** `run_project_rules` runs scoped and unscoped for each target set of spike-evidence §4 (a spec unit, a
  proposal, `docs/capabilities/governance`, one Python source file, `.devkit/architecture.toml`, `tools/devkit-dev`,
  a spec unit plus a `pyproject.toml`, `docs`), and `devkit rules check` runs without targets
- **Then** each scoped run's violations and problems equal the unscoped run's, and the whole-workspace check reports
  the same result as without the change; the comparison is recorded in the unit's evidence

### [AC-10] `devkit workflow next` on a documentation-only unit takes at most half the time
- **Given** one machine, the integration base without the change and the head with it
- **When** `.venv/bin/devkit workflow next --unit specs/2026-10/20261022-writing-style-rules` runs three times cold
  on each
- **Then** the median with the change is at most half the median without it; both are recorded in the unit's evidence

### [AC-11] The unit stays within its boundaries
- **Given** the finished unit
- **When** `devkit rules check specs/2026-10/20261022-lint-clean-target-scoped-rules` runs
- **Then** it exits 0 with no violation, and the diff from the handoff touches no path under `docs/decisions/` or
  `packages/devkit/src/devkit_agt/features/workflow/`

## 5. Assumptions

1. The proposal's acceptance outcome 7 (`devkit rules check` of the proposal reports no `RULE-proposal-boundaries`
   finding) applied while the proposal was in Planning; the proposal now lives in this unit, so AC-11 checks the unit
   and its excluded boundaries instead.
2. A protocol-only rule's malformed `inputs` is collected as a `RULES_DEFINITION_INVALID` problem by the same policy
   validation `phases` and `explain` use: `RuleDefinitionError` becomes a collectable rule problem carrying the rule
   ID while staying raisable at construction.
3. `skipped` lists the rules the final check pass did not evaluate: a rule skipped initially and rechecked after a
   fix is not listed. When a fixer raises, its partial writes are unknown, so the recheck evaluates every active rule.
4. The three rule guides state their inputs in their opening section; the two `devkit-dev` guides have no numbered
   sections, so the statement opens the guide.

## 6. Sequencing

`PROP-rule-shared-python-ast` changes how the three rules read Python; this unit changes whether they run and adds
one constructor argument to each. There is no design dependency. That sibling lands after this unit and rebases the
three rule modules and the governance capabilities onto it.
