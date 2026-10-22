---
id: PROP-lint-clean-target-scoped-rules
title: Scope target runs to the rules their targets can affect
summary: "Lets a targeted rules run, such as the workflow lint-clean check, skip whole-workspace rules whose inputs the targets cannot change, so devkit workflow next stops paying for a full Python analysis on documentation-only units."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: medium                       # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - packages/devkit/src/devkit_agt/features/workflow/
    - docs/capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-lint-clean-target-scoped-rules] Scope target runs to the rules their targets can affect

## 1. Background & Hypothesis

`devkit workflow next --unit <dir>` takes about 3.7 s (Measured on main at 4dbf9c4b (macOS, Python 3.12, this repository: about 820 tracked Python files and 850 Markdown files)), almost all of it in the `lint-clean` check.
`lint-clean` already passes only the unit's files as targets (`workflow/usecases/lint.py`, `run_project_rules(root,
targets=files)`), yet a unit holding only Markdown still pays for whole-workspace Python analysis: rules such as
`architecture`, `usecase-boundaries` and `unique_code` scan every Python file regardless of the targets. Because
`workflow next` runs at every stage boundary, it is the most frequent slow command.

Hypothesis: when a rule declares which files its result depends on, a targeted run can skip a whole-workspace rule
whose inputs no target can change, without missing a violation the targets introduce.

## 2. Technical Spike Questions

- **Q1**: Which declaration fits the rule contract (input extensions or path globs, or a "workspace-wide" flag with
  its input set), and what does an undeclared rule default to so existing rules stay correct?
- **Q2**: Which whole-workspace rules can be affected by a Markdown-only change (for example a document a Python
  rule reads), and how is that dependency expressed?

## 3. Proposed Design & Impact

- Rules declare their inputs; a targeted run evaluates a whole-workspace rule only when a target matches its inputs.
  Full runs (`devkit rules check` without targets, `--ci`, `--staged`) are unchanged.
- `lint-clean` on a documentation-only unit no longer runs Python-source rules; on a unit with Python targets it runs
  them as today. Acceptance compares results of targeted and full runs on representative units and measures
  `workflow next` again.
- Complements `PROP-rule-shared-python-ast`, which makes the runs that remain cheaper.

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
