---
id: ADR-scope-only-explicit-working-tree-targets-in-the-evaluator
title: Scope only explicit working-tree targets in the evaluator
summary: For deciding where scoping applies, we filter declared rules in evaluate_rules only for working-tree runs with explicit targets, keeping whole-workspace, commit-gate and CI snapshot runs complete, to speed lint-clean without weakening gates, accepting that the commit gate stays as slow as today.
proposal: SPEC-lint-clean-target-scoped-rules
status: accepted
created_at: 2026-10-22
---

# [ADR-scope-only-explicit-working-tree-targets-in-the-evaluator] Scope only explicit working-tree targets in the evaluator

Superseded in part by `ADR-scope-snapshot-runs-to-diff-paths-including-deletions`: its follow-up section and the
clause that every snapshot run evaluates every active rule.

- **Status**: Accepted
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Rules declare their inputs (`ADR-rules-declare-their-input-files-undeclared-rules-always-run`); the engine must
decide in which runs, at which layer and against which target list a declared rule is skipped. Targets reach the
evaluator from four callers: `devkit rules check|fix FILES`, `lint-clean` (`run_project_rules(root, targets=files)`),
the Git snapshot gates (`check --staged` at commit time, `check --ci`) and library callers of `evaluate_rules`,
including `devkit_agt.features.rules.services.testing.check`. A snapshot's targets are its changed files; its deleted
files are not targets, yet a deletion can change a whole-workspace rule's result (an import of a removed module).

## 2. Decision Drivers

- The commit gate and CI keep evaluating every rule: they are the last check before history.
- `lint-clean` and `devkit rules check FILES` agree, as they do today through `run_project_rules`.
- A rule author can test a declaration with the existing `check(rule, root, files, targets=...)` helper.
- Project policy (`[rules]`) cannot change which findings a skip hides without the run noticing.

## 3. Considered Options

1. **In `lint-clean` only**: the smallest change, but `devkit rules check FILES` would disagree with `lint-clean` on
   the same files, contradicting the one-evaluation-path principle of `CAP-GOV-rules-engine`.
2. **In `run_project_rules`**: covers both CLI and `lint-clean`, but library callers and rule tests bypass it.
3. **In `evaluate_rules`, for runs with explicit targets and no snapshot**: one place for every caller, next to the
   phase filter; snapshot and whole-workspace runs unchanged.
4. **Also in snapshot runs**: would speed the commit gate, but deleted paths are no targets, so a deletion-only change
   to Python could skip `RULE-architecture`.

## 4. Decision Outcome

Option 3, because it keeps the gates complete (driver 1), gives the CLI, `lint-clean` and library callers one
behavior (driver 2) and is reachable from the rule test helper (driver 3):

- After the phase filter, `evaluate_rules` skips a rule with declared `inputs` when `ctx.has_targets` is true,
  `ctx.snapshot` is `None`, and no target matches one of its patterns. A whole-workspace run (`has_targets` false) and
  every snapshot run evaluate every active rule.
- Matching uses the targets as named and expanded, before `[rules] exclude` (kept on `RuleContext` beside
  `changed_files`): the target-ignoring rules do not honor exclusions, so an excluded Python target can still change
  their findings.
- A target that is the project configuration `.devkit/config.toml` disables the skip for that run: `[rules]`
  settings and exclusions can change any rule's findings (driver 4).
- The autofix pass uses the reduced rule list; the convergence recheck decides again against the targets plus the
  files the fixes modified, so a fix that writes a skipped rule's input is rechecked by it. Policy validation still
  covers every loaded rule, so a settings error of a skipped rule is reported as today.
- Skipped rule IDs are returned on `EvaluationResult.skipped` (and so on `ProjectRun`) and logged at `INFO`
  (visible under `-v`); default stdout and the JSON result do not change, because a skip changes no next step.

## 5. Consequences

- Positive: `devkit workflow next` on a documentation-only spec unit drops from 3.65 s to about 1.4 s
  (`docs/materials/2026-10/20261022-lint-clean-target-scoped-rules/spike-evidence.md` §5); `devkit rules check <docs>` gains the same.
- Negative: a documentation-only targeted run no longer reports violations of a skipped target-ignoring rule in
  files outside its targets, whether pre-existing or introduced by uncommitted work. For `lint-clean` at the
  build-verify and fix-verify exits this includes the unit's own code, which lives outside the unit directory; the
  `rules-check` commit gate on each Development commit, `lint-ci-clean` and full runs still report it.
- Negative: the commit gate keeps its present cost.
- Follow-up: scoping snapshot runs needs the deleted paths treated as matching targets; triggered when the commit
  gate's cost becomes a measured problem.

## 6. Confirmation

- Evaluator tests (`packages/devkit/tests/`): skip with explicit non-matching targets; run with a matching target, a
  matching target `[rules] exclude` removes, a `.devkit/config.toml` target, no targets, and a snapshot context;
  undeclared rule always runs; `skipped` lists the skipped IDs; a recheck after a fix that modified a matching file
  evaluates the skipped rule.
- The equivalence comparison of the acceptance outcomes on this repository.
