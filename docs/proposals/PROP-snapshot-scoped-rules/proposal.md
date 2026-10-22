---
id: PROP-snapshot-scoped-rules
title: Scope snapshot rules runs to their changed paths
summary: "Extends rule target scoping to Git snapshot runs, the rules-check commit gate and CI, by treating deleted paths as matching targets, so a commit stops paying for whole-workspace rules its changes cannot affect."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - docs/capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-snapshot-scoped-rules] Scope snapshot rules runs to their changed paths

## 1. Background & Hypothesis

The `rules-check` commit gate runs a Git snapshot rules run on every commit, and CI runs `devkit rules check --ci`.
`ADR-scope-only-explicit-working-tree-targets-in-the-evaluator` kept snapshot runs whole-workspace because deleted
paths are not targets there, so a deletion-only change to Python could skip `RULE-architecture`. A snapshot run takes
about 3.3 s (Measured on main at df307e99 (macOS, Python 3.12, about 820 tracked Python files): `devkit rules check --ci --base HEAD~1` 3.30-3.40 s), paid on every commit even when the commit
touches only documents. The ADR's follow-up names this proposal's trigger: the commit gate's cost.

Hypothesis: treating deleted and renamed-from paths as matching targets lets snapshot runs use the same `inputs`
scoping as working-tree targeted runs without missing a violation a commit introduces.

## 2. Technical Spike Questions

- **Q1**: Which paths must a snapshot run treat as targets (added, modified, deleted, renamed from and to, mode
  changes), and does any declared rule depend on a file a commit can change without it appearing in the diff?
- **Q2**: Does CI keep a whole-workspace run as a safety net (for example on the default branch or nightly), and
  what does the commit gate report when it skips rules?

## 3. Proposed Design & Impact

- Snapshot runs skip a declared rule when no changed path (including deletions) matches its `inputs`; undeclared
  rules and `.devkit/config.toml` changes keep today's behavior.
- Equivalence evidence: for representative commits (documentation-only, Python-only, deletion-only, configuration),
  scoped and unscoped snapshot results are equal; a seeded violation in a non-changed file is still reported by the
  chosen safety-net run.
- The commit gate time on a documentation-only commit is measured before and after.
- Follows `SPEC-lint-clean-target-scoped-rules`; supersedes the follow-up in its ADR rather than reopening it.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr snapshot-scoped-rules "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept snapshot-scoped-rules --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff snapshot-scoped-rules.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
