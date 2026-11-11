---
id: PROP-select-tests-by-read-document-paths
title: Select tests by the repository paths they read
summary: "Lets affected-test selection find tests that read a repository path through a root-anchored literal path expression, instead of listing each such test in the selector's data table."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: docs/development/
priority: medium                       # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - scripts/affected_tests.py
    - packages/devkit/tests/e2e/package/test_affected_tests.py
    - docs/development/ci-cd.md
    - docs/architecture/ARCH-07-deployment.md
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-select-tests-by-read-document-paths] Select tests by the repository paths they read

## 1. Background & Hypothesis

`scripts/affected_tests.py` maps a changed non-source file to its readers only through the fixed `DATA` table keyed
by path prefix, and a package source file only through static imports. A test that reads a file its imports do not
reach is skipped when only that file changes. Feedback hygiene fixed two such gaps by adding table entries
(`FB-docs-selection-misses-guidance-contract-tests`, `FB-affected-selection-misses-cross-package-fix-scan`); a
failing test reached `main` while every final affected check passed.

Planning measured the class at this head (`materials/read-path-survey.md`). Every repository document read by
literal path is already listed in `DATA`, so the document case is closed by hand-kept rows only. Seven reader pairs
are missed today: bundle assets of another package, `guides/` and package-root Markdown (which select nothing) and
test data beside its reader.

Hypothesis: collecting the repository paths that tests read through root-anchored literal path expressions lets the
selector map any changed file to its readers without hand-kept rows.

## Source feedback

- `FB-docs-selection-misses-guidance-contract-tests` (resolved by a `DATA` row): the generic read scan for documents.
- `FB-affected-selection-misses-cross-package-fix-scan` (resolved by `ALL_SOURCES_TESTS`): its reader scans a loop
  variable base, which no literal scan resolves, so it keeps its explicit mapping.

## 2. Technical Spike Questions

- **Q1**: Which literal path forms do the existing tests use, and how many are statically recoverable?
  - Answer: 44 of 441 test-tree files read root-anchored paths. 71 reads are `Path(__file__)...parents[N] / "a/b"`
    chains, usually through a module constant, and resolve to an exact path. 28 are `glob`, `rglob` or `iterdir` on
    an anchored base with a literal pattern. 6 join a runtime segment and resolve only to their base. Literal
    `Path("docs/...")` strings build `tmp_path` repositories and are not repository reads.
- **Q2**: How does the scan fit `ADR-test-selection-and-ci` and the conservative full fallback? Should an
  unresolvable dynamic read keep a broad owner row?
  - Answer: the scan only adds tests; full triggers, the full fallback and every `DATA` row stay
    (`ARCH-07-deployment` §1.3). A runtime segment under an anchored base widens to that base directory, so it needs no
    owner row. Readers the scan cannot see (by document ID, by subprocess in the repository root, through an
    unanchored base) keep their rows.
- **Q3**: What is the cost on every `just test-affected` run, and should the scan be cached?
  - Answer: a document-only selection grows from about 0.01 s to about 1.5 s, a source selection from about 4.3 s by
    at most about 0.9 s. No cache: the selector stays stateless and the scan reuses the in-process parsed trees.

## 3. Proposed Design & Impact

The decision and its alternatives are in `PADR-literal-read-test-selection`.

- **Read discovery**: for each test module, collect the root-anchored reads of the module, its applicable conftests
  and the local helpers its import discovery already traverses. A read is an expression evaluated statically from
  `Path(__file__)` through `resolve`, `parent`, `parents[N]`, `/` with string literals, `joinpath` and names bound
  once to such an expression.
- **Matching**: a changed path selects a reader when it equals an exact read, lies under a directory read, matches the
  literal pattern of a `glob` or `rglob` read (relative to its base), or lies under the base of a join with a runtime
  segment or a non-literal pattern.
- **Order**: full triggers and the full fallback for unknown paths keep precedence. Otherwise the readers are added to
  the selection, including for paths that select nothing today (`guides/`, package-root Markdown, other untested
  prefixes) and for a non-test file under `tests/`.
- **Kept**: every `DATA`, `SOURCE_TREE_TESTS` and `ALL_SOURCES_TESTS` entry; no row is removed.
- **Documents**: `docs/development/ci-cd.md` (the `just test-affected` selection bullets and Limits) and
  `ARCH-07-deployment` §1.3 (the read-discovery constraint). No capability documents the selector.
- **Tests**: `packages/devkit/tests/e2e/package/test_affected_tests.py` gains positive fixtures for each read form
  and each measured miss, and negative fixtures for `tmp_path` literals, unanchored strings and a test's own file.

## Planning decisions

- Scope covers every repository path, not only documents: the measured document reads are all listed already, and the
  open misses are bundle assets, untested prefixes and test data (`materials/read-path-survey.md`).
- `target_area` and `boundaries.owns` name the selector, its test, `docs/development/ci-cd.md` and
  `ARCH-07-deployment` instead of `capabilities/governance/`, which documents no part of the selector.
- Glob reads match their literal pattern, not only their base, so `root.glob("packages/*/src/**/*.py")` does not make
  its test a reader of every repository file.
- Retiring `DATA` rows the scan covers is out of scope: it reduces selection and needs the before/after collection
  matrices `ARCH-07-deployment` §1.3 asks for.

## Acceptance outline

- Each measured miss in `materials/read-path-survey.md` selects its reader.
- A change that selects the full suite today still does; a change's selection today stays a subset of its new
  selection on the same revision.
- A `tmp_path` literal, an unanchored string and a read of the test's own file add no reader.
- `docs/development/ci-cd.md` and `ARCH-07-deployment` §1.3 describe read discovery; `guides/` and package-root
  Markdown are no longer described as selecting nothing when a test reads them.
- Baseline for the subset check and the cost: the Planning measurement in `materials/read-path-survey.md` on the same
  machine class, or the worker's head with read discovery disabled.

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
