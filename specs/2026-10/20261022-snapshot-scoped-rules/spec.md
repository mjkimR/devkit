---
id: SPEC-snapshot-scoped-rules
title: Scope snapshot rules runs to their changed paths
summary: Extends rule target scoping to Git snapshot runs, the rules-check commit gate and CI, by treating deleted paths as matching targets, so a commit stops paying for whole-workspace rules its changes cannot affect.
status: planned
created: 2026-10-22
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-snapshot-scoped-rules] Scope snapshot rules runs to their changed paths

## 1. Problem Statement & Motivation

Handed off from proposal PROP-snapshot-scoped-rules on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-snapshot-scoped-rules`

### 1. Background & Hypothesis

The `rules-check` commit gate runs a Git snapshot rules run on every commit, and CI runs `devkit rules check --ci`.
`ADR-scope-only-explicit-working-tree-targets-in-the-evaluator` kept snapshot runs whole-workspace because deleted
paths were not targets there. A staged snapshot run takes about 4.49 s (measured on `plan-snapshot-scoped-rules`
at `56568864` (Linux, Python 3.12, about 820 tracked Python files)), with ~2.93 s spent evaluating whole-workspace
Python rules even when the commit touches only documentation. The ADR's follow-up names this proposal's trigger:
the commit gate's cost.

Hypothesis: decoupling scoping paths from evaluation targets and matching deleted and renamed-from paths against rule
`inputs` allows snapshot runs to skip unaffected whole-workspace rules, cutting commit gate latency by ~65 % on
non-Python commits without missing deletion-induced violations.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Scope snapshot rules runs to their changed paths so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Which paths must a snapshot run treat as targets (added, modified, deleted, renamed from and to, mode
  changes), and does any declared rule depend on a file a commit can change without it appearing in the diff?
  - *Answer*: `git_snapshot` captures added, modified, deleted, renamed (via `--no-renames` as deletion + addition)
    and typechanged paths. Evaluation targets (`RuleContext.targets`) hold only files present in the snapshot tree,
    while scoping matching paths (`scope_rules`) include `targets` plus `snapshot.deleted`. All declared rules
    (`RULE-architecture`, `RULE-usecase-boundaries`, `RULE-advisory-unique-code`) test that all opened files match
    their declared `inputs`. No declared rule depends on an untracked or uncaptured file.
- **Q2**: Does CI keep a whole-workspace run as a safety net (for example on the default branch or nightly), and
  what does the commit gate report when it skips rules?
  - *Answer*: Yes, `.github/workflows/ci.yml` runs an unscoped `just rules-check` on Linux and macOS, and nightly and
    release workflows run full CI. Skipped rules are returned on `EvaluationResult.skipped` and logged at `INFO`
    under `-v`, keeping default agent stdout and JSON clean.

### 3. Proposed Design & Impact

- Decouple evaluation targets (`RuleContext.targets`) from candidate scoping paths (`names` in `scope_rules`).
- In `scope_rules`, when `ctx.snapshot is not None`, match rule `inputs` against `ctx.targets` plus `ctx.snapshot.deleted`.
- Fix engine lifecycle short-circuit in `RunProjectRulesUseCase._run` so `has_work = bool(targets or (snapshot and snapshot.deleted))`,
  ensuring deletion-only commits initialize context and run matching rules.
- If `.devkit/config.toml` (`CONFIG_PATH`) or `.devkit/installation.json` (`RECEIPT_PATH`) is touched, skip no rules.
- Equivalence evidence: for representative commits (documentation-only, Python-only, deletion-only, configuration),
  scoped and unscoped snapshot results are equal; a seeded violation in a non-changed file is still reported by the
  chosen safety-net run.
- The commit gate time on a documentation-only commit drops from ~4.49 s to ~1.56 s (~2.93 s saved per commit).
- Supersedes the follow-up section of `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`.

### 4. Lifecycle & Retirement Criteria

- Preliminary decision: recorded in `ADR-scope-snapshot-runs-to-diff-paths-including-deletions`.
- Research: collected in `docs/materials/2026-10/20261022-snapshot-scoped-rules/spike-evidence.md`.
- Acceptance: `devkit spec proposal accept snapshot-scoped-rules --by user` records `gate:plan-accept` and `status: accepted`.
  Development starts with `devkit spec proposal handoff snapshot-scoped-rules`.

