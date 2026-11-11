---
id: PROP-select-tests-by-read-document-paths
title: Select tests by the repository paths they read
summary: "Lets affected-test selection find tests that read a repository path through a root-anchored literal path expression, instead of listing each such test in the selector's data table."
status: accepted                       # draft | reviewing | accepted | rejected
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

Planning measured the class at this head (`materials/read-path-survey.md`). Every literal read under `docs/`,
`examples/` and `models/` is already listed in `DATA`, so the document case is closed only by hand-kept rows. 37
reader pairs are missed today: helper reads of `.devkit/architecture.toml`, bundle assets of another package, recipe
scripts, `guides/`, `.devkit/config.toml`, a frontend script, package-root Markdown and test data beside its reader.

Hypothesis: collecting the repository paths that tests read through root-anchored literal path expressions lets the
selector map any changed file to its readers without hand-kept rows.

## Source feedback

- `FB-docs-selection-misses-guidance-contract-tests` (resolved by a `DATA` row): the generic read scan for documents.
- `FB-affected-selection-misses-cross-package-fix-scan` (resolved by `ALL_SOURCES_TESTS`): its reader scans an
  unresolved base, which no literal scan sees, so it keeps its explicit mapping.

## 2. Technical Spike Questions

- **Q1**: Which literal path forms do the existing tests use, and how many are statically recoverable?
  - Answer: 54 of 441 test-tree files read root-anchored paths. 324 reads resolve to an exact path, mostly
    `Path(__file__)...parents[N] / "a/b"` chains through a module constant and often nested in a call
    (`(ROOT / "x").read_text()`). 45 are `glob` or `rglob` with a literal pattern, 1 is `iterdir`, and 26 join a
    runtime segment and resolve only to their base. After expanding loops over literal tuples no join is based at
    the repository root. Literal `Path("docs/...")` strings build `tmp_path` repositories and are not repository reads.
- **Q2**: How does the scan fit `ADR-test-selection-and-ci` and the conservative full fallback? Should an
  unresolvable dynamic read keep a broad owner row?
  - Answer: the scan only adds tests; full triggers, the full fallback and every `DATA` row stay
    (`ARCH-07-deployment` §1.3). A runtime segment under an anchored base widens to that base directory, so it needs no
    owner row. A read that resolves to the repository root or not at all adds nothing: it is not an import
    uncertainty. Readers the scan cannot see (by document ID, by subprocess in the repository root, through an
    unresolved base) keep or gain explicit rows.
- **Q3**: What is the cost on every `just test-affected` run, and should the scan be cached?
  - Answer: a document-only selection grows from about 0.01 s to about 2.5 s with reverse helper attribution; a
    source selection, which already runs import discovery, adds about 1.5 s to about 4.3 s. No cache: the selector
    stays stateless and the scan reuses the in-process parsed trees.

## 3. Proposed Design & Impact

The decision and its alternatives are in `PADR-literal-read-test-selection`.

- **Read discovery**: scan every test-tree file once (test modules, embedded rule tests, conftests, helpers). A read
  is a maximal expression evaluated statically from `Path(__file__)` through `resolve`, `parent`, `parents[N]`, `/`
  with string literals, `joinpath` and names bound once to such an expression, wherever it occurs (call receiver or
  argument included). Binding a base to a name is not a read; its uses are. A loop variable over a literal tuple or
  list expands into one read per element.
- **Attribution**: a read in a test module belongs to it; a read in a conftest to the test modules under its
  directory; a read in a local helper to the test modules whose import discovery reaches the helper. Resolve
  importers only for helpers that have reads; `Workspace.imports` exposes the files it visits (today it discards its
  `seen` set) or an equivalent reverse lookup.
- **Matching**: a changed path selects a reader when it equals an exact read or lies under a directory read.
  `iterdir`, a runtime join and a non-literal glob pattern read their base directory. A literal `glob` or `rglob`
  pattern selects when the changed path or one of its ancestors below the base matches it, so a new or deleted
  subdirectory counts; `**` matches zero or more segments (Python 3.12 has no `PurePath.full_match`, and
  `PurePath.match` treats `**` like `*`). A read resolving to the repository root adds nothing.
- **Order**: full triggers and the full fallback for unknown paths keep precedence. Otherwise the readers are added,
  including for paths that select nothing today (`guides/`, package-root Markdown, `.devkit/`, a non-test file
  under `tests/` and the frontend paths). A frontend change keeps `frontend=True`, `reason=frontend` and the
  `[FRONTEND_CHECK: ...]` line; its literal readers make the mode `partial` (`scripts/viewer.sh` selects
  `test_viewer_script.py`), and a frontend path no test reads still selects no pytest test.
- **Kept and added rows**: every `DATA`, `SOURCE_TREE_TESTS` and `ALL_SOURCES_TESTS` entry stays.
  `packages/devkit/tests/integration/package/test_version_script.py` joins the `scripts/release.sh` and `justfile`
  rows, because it runs both by subprocess.
- **Documents**: `docs/development/ci-cd.md` (the `just test-affected` selection bullets, the frontend bullet, the
  "select nothing" bullet and Limits) and `ARCH-07-deployment` §1.3 (read discovery only adds tests; an unresolved read adds nothing and is
  not an import uncertainty). No capability documents the selector.
- **Tests**: `packages/devkit/tests/e2e/package/test_affected_tests.py` gains positive fixtures for each read form
  (nested in a call, loop expansion, helper attribution, glob with a new subdirectory, `iterdir`) and each measured
  miss group, and negative fixtures for `tmp_path` literals, unanchored strings and a test's own file.

## Planning decisions

- Scope covers every repository path, not only documents: the measured document reads are all listed already, and the
  open misses lie elsewhere (`materials/read-path-survey.md`).
- `target_area` and `boundaries.owns` name the selector, its test, `docs/development/ci-cd.md` and
  `ARCH-07-deployment` instead of `capabilities/governance/`, which documents no part of the selector.
- Helper attribution runs in reverse (scan once, resolve importers only for helpers with reads) to keep a
  document-only selection near 2.5 s instead of running the full import discovery.
- Frontend and `.devkit/` paths also select the tests that read them by literal path; a frontend change keeps
  `[FRONTEND_CHECK]` and `reason=frontend`, and paths no test reads still select nothing (user decision, q1).
- Retiring `DATA` rows the scan covers is out of scope: it reduces selection and needs the before/after collection
  matrices `ARCH-07-deployment` §1.3 asks for.

## Acceptance outline

- Each miss group in `materials/read-path-survey.md` selects its reader, `scripts/viewer.sh` and
  `.devkit/config.toml` included.
- A change that selects the full suite today still does; a change's selection today stays a subset of its new
  selection on the same revision.
- `.claude/skills/x/SKILL.md` still selects nothing and
  `packages/devkit-viewer/frontend/src/lib/App.svelte`, which no test reads, still returns `mode=none`,
  `reason=frontend` and the `[FRONTEND_CHECK: ...]` line; a `tmp_path` literal, an unanchored string and a read of the
  test's own file add no reader.
- Existing assertions expected to change: `test_affected_tests.py:121-124` (`guides/install.md` now selects
  `test_deep_research.py`, which reads `guides/**/*.md`), `:177` (`.devkit/config.toml` selects
  `test_handbook_script.py`) and the `scripts/viewer.sh` case of the frontend-only test at `:335` (now `partial`
  with `test_viewer_script.py`, still `reason=frontend` with the `[FRONTEND_CHECK: ...]` line).
- `docs/development/ci-cd.md` and `ARCH-07-deployment` §1.3 describe read discovery; untested prefixes are no longer
  described as selecting nothing when a test reads them.
- Cost: a document-only selection adds at most 3 s over the worker's head with read discovery disabled, measured on
  the same machine; the Planning figures are in `materials/read-path-survey.md`.

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
