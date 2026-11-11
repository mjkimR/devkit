---
id: PROP-select-tests-by-read-document-paths
title: Select tests by the repository documents they read
summary: Lets affected-test selection find tests that read repository documents by literal path, instead of listing each such test in the selector's data table.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/governance/
priority: medium                       # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-select-tests-by-read-document-paths] Select tests by the repository documents they read

## 1. Background & Hypothesis

`scripts/affected_tests.py` selects tests that read repository files through a fixed DATA table keyed by path
prefix. About 30 test files read `docs/capabilities` (and other documents) by literal path. Each one missing from the
table is silently skipped when only that document changes. Today's feedback hygiene fixed two such gaps by adding
table entries (`FB-docs-selection-misses-guidance-contract-tests`, `FB-affected-selection-misses-cross-package-fix-scan`).
The class stays open. Observed impact: a failing contract test reached main while every final affected check passed.
Frequency: two occurrences so far.

Hypothesis: collecting literal repository paths that tests read (string constants passed to path joins or reads)
lets the selector map a document change to its readers without hand-maintained rows.

## 2. Technical Spike Questions

- **Q1**: Which literal path forms do the existing tests use (`ROOT / "docs/..."`, `Path("docs/...")`, joined
  segments, glob patterns), and how many are statically recoverable?
- **Q2**: How does the scan fit `ADR-test-selection-and-ci` and the selector's
  conservative full fallback? Should an unresolvable dynamic read keep a broad owner row?
- **Q3**: What is the cost on every `just test-affected` run, and should the scan be cached like the import graph?

## 3. Proposed Design & Impact

- Extend dependency discovery with literal repository-path reads in test modules and their helpers, mapping a
  changed document or directory to the tests that read it. Keep the DATA table for dynamic or glob reads.
- Update `docs/development/ci-cd.md` and the selector tests. No change to the selection tiers or the fallbacks.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr select-tests-by-read-document-paths "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept select-tests-by-read-document-paths --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff select-tests-by-read-document-paths.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
