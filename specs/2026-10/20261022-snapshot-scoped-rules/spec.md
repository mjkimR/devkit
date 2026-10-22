---
id: SPEC-snapshot-scoped-rules
title: Scope snapshot rules runs to their changed paths
summary: Extends rule target scoping to Git snapshot runs, the rules-check commit gate and CI, by treating deleted paths as matching targets, so a commit stops paying for whole-workspace rules its changes cannot affect.
status: planned
created: 2026-10-22
related_capabilities: [CAP-GOV-evaluation-lifecycle, CAP-GOV-rules-engine]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-snapshot-scoped-rules] Scope snapshot rules runs to their changed paths

## 1. Problem Statement & Motivation

Handed off from proposal PROP-snapshot-scoped-rules on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-snapshot-scoped-rules`
- **Accepted decisions**: `ADR-scope-snapshot-runs-to-diff-paths-including-deletions` (superseding the follow-up of `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`).

The `rules-check` commit gate runs an in-place Git snapshot rules run (`devkit rules check --staged`) on every commit, and CI runs `devkit rules check --ci`.
`ADR-scope-only-explicit-working-tree-targets-in-the-evaluator` introduced rule target scoping for working-tree targeted runs (`lint-clean`, `devkit rules check <files>`), but kept snapshot runs whole-workspace because deleted files were not targets.

On this repository, an in-place staged snapshot run takes about 4.49 s on a documentation-only commit (measured at `56568864`, Linux, Python 3.12, ~820 tracked Python files), spending ~2.93 s evaluating whole-workspace Python rules (`RULE-architecture`, `RULE-usecase-boundaries`, `RULE-advisory-unique-code`) whose inputs the commit cannot affect.

By decoupling candidate scoping paths from evaluation targets and matching deleted, renamed and typechanged paths against rule `inputs`, snapshot runs can safely skip unaffected whole-workspace rules, cutting commit gate latency to ~1.56 s (~65 % reduction) without missing deletion-induced or config violations.

### Design

- **Decoupled scoping paths and evaluation targets**:
  - `RuleContext.targets` continues to hold only existing regular files in the snapshot tree (`snapshot.changed` plus inbound Markdown linkers). Non-existent deleted files are excluded from `ctx.targets` so target-inspecting rules do not attempt to read absent files.
  - In `scope_rules(ctx, rules, modified)`, when `ctx.snapshot is not None`, the matching candidate list `names` is formed from `ctx.targets` plus `ctx.snapshot.deleted` and any non-regular diff paths (e.g. typechanges).
- **Engine lifecycle fix for deletion-only commits**:
  - In `RunProjectRulesUseCase._run`, `has_work` is computed as `bool(targets or (snapshot and snapshot.deleted))`, ensuring deletion-only commits (where `targets` is empty) do not short-circuit before rule loading and `evaluate_rules`.
- **Policy and receipt protection**:
  - If `.devkit/config.toml` (`CONFIG_PATH`) or `.devkit/installation.json` (`RECEIPT_PATH`) is present in `names`, rule skipping is disabled for the run.
- **Reporting and visibility**:
  - Skipped rule IDs are returned on `EvaluationResult.skipped` (and `ProjectRun.skipped`) and logged at `INFO` under `-v`. Default agent stdout and JSON output remain clean and unchanged.

## 2. User Stories

- **US-1**: As an engineer or agent committing documentation or non-code assets, I want the `rules-check` commit gate to skip unaffected whole-workspace Python rules, so that each commit completes in ~1.56 s instead of ~4.49 s.
- **US-2**: As a maintainer, I want snapshot rule scoping to match deleted and renamed files against rule declarations, so that deleting a Python file still evaluates `RULE-architecture` and `RULE-usecase-boundaries`.
- **US-3**: As a maintainer, I want project policy and installation receipt modifications to run every rule, so that rule configuration or receipt changes are always fully validated.

## 3. Non-Goals

1. **Scope Excluded**: Changing the rule declaration contract (`BaseRule.inputs` syntax or validation).
2. **Scope Excluded**: Changing working-tree targeted scoping behavior established in `SPEC-lint-clean-target-scoped-rules`.
3. **Scope Excluded**: New output fields in `devkit rules check` stdout or JSON summaries.
4. **Scope Excluded**: Relaxing full-workspace CI checks (`just rules-check` in `.github/workflows/ci.yml`).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Snapshot runs scope declared rules against diff paths including deletions
- **Given** a snapshot run (`--staged` or `--ci`) whose changed, deleted and typechanged paths match none of the declared `inputs` of a rule,
- **When** `evaluate_rules` runs,
- **Then** the declared rule is skipped, its ID is returned in `EvaluationResult.skipped` (and `ProjectRun.skipped`), and logged at `INFO` (`-v`), while undeclared rules always evaluate.

### [AC-02] Python file deletion or modification triggers declared Python rules in snapshot runs
- **Given** a snapshot run where a Python file (`.py`) is added, modified, or deleted,
- **When** `evaluate_rules` runs,
- **Then** `RULE-architecture`, `RULE-usecase-boundaries`, and `RULE-advisory-unique-code` are not skipped and evaluate against the snapshot workspace.

### [AC-03] Deletion-only commits initialize RuleContext and evaluate matching rules
- **Given** a Git snapshot where files are only deleted (no added or modified files, `snapshot.changed` is empty),
- **When** `RunProjectRulesUseCase` executes,
- **Then** `has_work` evaluates to true, `RuleContext` is instantiated, and rules matching the deleted paths evaluate rather than returning an empty evaluation result.

### [AC-04] Evaluation targets remain limited to existing files in the snapshot workspace
- **Given** a snapshot run with deleted files,
- **When** `RuleContext` is constructed,
- **Then** `RuleContext.targets` contains only regular files present in the snapshot tree (and Markdown linkers); non-existent deleted files are excluded from `ctx.targets`.

### [AC-05] Config or receipt changes disable rule skipping in snapshot runs
- **Given** a snapshot run where `.devkit/config.toml` or `.devkit/installation.json` is modified, added, or deleted,
- **When** `evaluate_rules` runs,
- **Then** no active rule is skipped, regardless of whether other changed files match their `inputs`.

### [AC-06] Whole-workspace runs continue to evaluate all active rules
- **Given** a working-tree run without explicit targets (`targets=None`, `snapshot=None`),
- **When** `evaluate_rules` runs,
- **Then** every active rule evaluates and `EvaluationResult.skipped` is empty.
