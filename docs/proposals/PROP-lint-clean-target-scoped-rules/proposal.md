---
id: PROP-lint-clean-target-scoped-rules
title: Scope target runs to the rules their targets can affect
summary: "Lets a targeted rules run, such as the workflow lint-clean check, skip whole-workspace rules whose inputs the targets cannot change, so devkit workflow next stops paying for a full Python analysis on documentation-only units."
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: medium                       # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - packages/devkit/tests/
    - tools/devkit-dev/src/devkit_dev/bundle/rules/
    - packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-rule/
    - .devkit/installation.json
    - docs/capabilities/governance/
    - docs/development/reference/
  excludes:
    - docs/decisions/
    - packages/devkit/src/devkit_agt/features/workflow/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-lint-clean-target-scoped-rules] Scope target runs to the rules their targets can affect

## 1. Background & Hypothesis

`devkit workflow next --unit <dir>` takes about 3.7 s on a spec unit (measured: 3.74 s on
`specs/2026-10/20261022-writing-style-rules`, 11 Markdown and YAML files, at 514bdea1 on macOS, Python 3.12; this
repository has about 820 tracked Python files and 850 Markdown files), almost all of it in the `lint-clean` check that
the spec workflows evaluate at the specify and build-verify exits. `lint-clean` already passes only the unit's files
as targets (`workflow/usecases/lint.py`, `run_project_rules(root, targets=files)`), yet a unit holding only Markdown
still pays for whole-workspace Python analysis: `RULE-architecture` and `RULE-usecase-boundaries` ignore the targets
and inspect every Python file, and `RULE-advisory-unique-code` indexes every Python file to report the targeted ones.
Together they take about 2.5 s of the run (`materials/spike-evidence.md`).

Hypothesis: when a rule declares which files its result depends on, a targeted run can skip a whole-workspace rule
whose inputs no target can change, without missing a violation the targets introduce.

## 2. Technical Spike Questions

- **Q1**: Which declaration fits the rule contract, and what does an undeclared rule default to?
  **Answer**: an optional `BaseRule` field `inputs: tuple[str, ...] | None`, workspace-relative patterns in the `**`
  grammar of `[rules] exclude`. Extensions alone cannot name `.devkit/architecture.toml`; a separate
  "workspace-wide" flag adds nothing the input set does not imply. An undeclared rule (`None`) runs in every targeted
  run, exactly as today; an empty tuple or an invalid pattern is `RULES_DEFINITION_INVALID`
  (`PADR-rules-declare-their-input-files-undeclared-rules-always-run`).
- **Q2**: Which whole-workspace rules can a Markdown-only change affect, and how is that expressed?
  **Answer**: none of the three Python-source rules reads a Markdown file (`materials/spike-evidence.md` §2-3); the
  Markdown rules (`spec` rules, `markdown_link`, `cli_contract`, `file_length`, `authoring`) report only targeted
  files and stay undeclared, so they run as today. A rule that does read Markdown for a Python check lists the
  Markdown pattern in `inputs`. A `.devkit/config.toml` target turns scoping off for the run, because `[rules]`
  policy can change any rule's findings.

## 3. Proposed Design & Impact

- **Declaration** (`PADR-rules-declare-their-input-files-undeclared-rules-always-run`): `BaseRule` gains `inputs`,
  validated at construction. The `Rule` protocol is unchanged; the engine reads the field with `getattr` and its
  policy validation rejects, for any loaded rule, an `inputs` that is neither `None` nor a non-empty tuple of valid
  patterns (`RULES_DEFINITION_INVALID`, before any rule runs). This
  proposal declares it on `RULE-architecture` (`**/*.py`, `**/pyproject.toml`, `**/bundle.toml`,
  `.devkit/architecture.toml`), `RULE-usecase-boundaries` (`**/*.py`, `.devkit/architecture.toml`) and
  `RULE-advisory-unique-code` (`**/*.py`).
- **Scoping** (`PADR-scope-only-explicit-working-tree-targets-in-the-evaluator`): after the phase filter,
  `evaluate_rules` skips a declared rule when the run has explicit targets (`ctx.has_targets`), is not a Git snapshot
  (`ctx.snapshot is None`), no target is `.devkit/config.toml`, and no target matches one of its patterns. Matching
  uses the expanded targets before `[rules] exclude`, because the target-ignoring rules do not honor exclusions. The
  fix pass uses the reduced list; the recheck evaluates it again against the targets plus the files the fixes
  modified. Whole-workspace runs and the snapshot gates
  (`check --staged`, `check --ci`) evaluate every rule as today. `devkit rules check FILES`, `devkit rules fix FILES`,
  `lint-clean` and library callers of `evaluate_rules` share this behavior.
- **Visibility**: `EvaluationResult.skipped` (and `ProjectRun`) lists the skipped rule IDs, logged at `INFO`
  (`-v`); default stdout and JSON results are unchanged. `devkit rules explain` shows `inputs=` on its `[RULE: ...]`
  line and `inputs` in JSON.
- **Living Spec**: `CAP-GOV-rule-authoring` §1 documents `inputs`; `CAP-GOV-evaluation-lifecycle` replaces "checked
  by every rule" (Targets) and "a `hygiene` run limited to explicit targets still evaluates the rule" (Phase
  overrides) with the scoping contract; the Rules Reference documents the `explain` field; the three rule
  guides state their inputs in §1; the `spec-rule` skill names `inputs` for rules that scan the workspace.
- `workflow/usecases/lint.py` does not change: scoping lives in the engine, so `lint-clean` gains it through
  `run_project_rules`.

### Acceptance outcomes

1. **Declaration contract**: `BaseRule(inputs=())` and each `validate_pattern` rejection raise
   `RuleDefinitionError` (`RULES_DEFINITION_INVALID`); `inputs=None` and a valid tuple construct; a protocol-only rule
   whose `inputs` is a string, a list or an empty tuple fails the run with `RULES_DEFINITION_INVALID` before any rule
   runs.
2. **Scoping contract**: evaluator tests show a declared rule skipped for explicit targets matching none of its
   patterns, and evaluated for a matching target, for a matching target that `[rules] exclude` removes, for a
   `.devkit/config.toml` target, for a whole-workspace run and for a snapshot context; an undeclared rule is evaluated
   in each case; `skipped` lists exactly the skipped IDs; a recheck after a fix that modified a file matching a
   skipped rule's patterns evaluates that rule.
3. **Declared rules**: each of the three rules' `tests/test_rule.py` shows it skipped for a documentation-only
   target set and reporting a seeded violation when the target matches each of its declared patterns, and checks the
   declaration is complete: during a whole-workspace check of a fixture holding every file kind the rule reads, every
   workspace file the rule opens (recorded through an `open` audit hook or an equivalent patch) matches one of its
   `inputs`.
4. **Equivalence**: on this repository at the integration base, for the target sets of
   `materials/spike-evidence.md` §4 (a spec unit, a proposal, `docs/capabilities/governance`, one Python source file,
   `.devkit/architecture.toml`, `tools/devkit-dev`, a spec unit plus a `pyproject.toml`, `docs`), the scoped run's
   violations and problems equal the unscoped targeted run's, and `devkit rules check` without targets is unchanged.
   The comparison is recorded in the unit's evidence.
5. **Intended difference**: a test with a seeded `RULE-architecture` violation in a non-targeted Python file shows it
   reported by the whole-workspace run and by a run targeting a Python file, and not by a documentation-only targeted
   run.
6. **Performance**: `.venv/bin/devkit workflow next --unit specs/2026-10/20261022-writing-style-rules` takes at most
   half the time of the same command on the integration base without the change, both measured on one machine as the
   median of three cold runs and recorded in the unit's evidence (Planning, Apple M4 Pro: 3.65 s unscoped, 1.37 s with
   scoping simulated in a fresh process, `materials/spike-evidence.md` §5).
7. **Boundaries**: `devkit rules check docs/proposals/PROP-lint-clean-target-scoped-rules/proposal.md` reports no
   `RULE-proposal-boundaries` finding.

### Non-Goals

- Scoping Git snapshot runs (commit gate, CI); deleted paths are not targets there.
- Declaring `inputs` on the Markdown rules or the `devkit-catalog` `cli_tool` rules.
- Making the target-ignoring rules report only targeted files, or parsing Python faster (that is
  `PROP-rule-shared-python-ast`).
- New output fields in `devkit rules check` stdout or JSON.

### Sequencing

`PROP-rule-shared-python-ast` (one `ast.parse` per file through `WorkspaceCache`) changes how the three rules read
Python; this proposal changes whether they run and adds one constructor argument to each. There is no design
dependency, so no `depends_on`. The sibling is planned to land first; whichever lands second rebases the three rule
modules and the governance capabilities onto the other. Acceptance outcome 6 is relative to its own base and holds
either way.

### Planning decisions

- `lint-clean` is not changed; the workflow feature is excluded from the boundaries because scoping belongs to the
  engine's one evaluation path (`CAP-GOV-rules-engine` principle 5).
- At the build-verify (feature) and fix-verify (bugfix) exits, `lint-clean` no longer reports architecture and
  use-case boundary violations of the unit's own code, which lives outside the unit directory and was caught there
  only because the two rules ignore targets. The draft already set this direction ("on a documentation-only unit no
  longer runs Python-source rules"); the code is still checked by every snapshot run, that is the `rules-check` commit
  gate on each Development commit and `lint-ci-clean` before integration, and by `devkit rules check <changed files>`.
- The skip predicate lives in the engine, not in each rule: a rule-local guard would copy the snapshot, configuration
  and exclusion conditions into three rules of two bundles and every later rule, hide the declaration from
  `devkit rules explain`, and leave `skipped` unreportable
  (`PADR-rules-declare-their-input-files-undeclared-rules-always-run`, option 6).
- `dev_effort` stays `medium`: the change spans the rules engine, two bundle sources, a skill and the Living Spec,
  with no effect that cannot be undone locally.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr lint-clean-target-scoped-rules "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept lint-clean-target-scoped-rules --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff lint-clean-target-scoped-rules.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
