---
id: SPEC-targeted-tests
title: Targeted and affected test runs
summary: 'Run only the tests a change needs: area targeting for just test, a diff-based just test-affected selection, and agent guidance that keeps the full suite to one run before integration.'
status: planned
created: 2026-10-19
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-targeted-tests] Targeted and affected test runs

## 1. Problem Statement & Motivation

The workspace suite has about 3,200 tests whose summed duration is about 240 seconds; eight xdist workers bring a run
to 34 to 52 seconds of wall time on a 14-core machine, and more workers do not help because the cost is process
creation (about 13,500 subprocesses per run). Agents run the full suite after every edit because the guidance names
only `just test [module]`, and the `devkit-agt` module alone is about 78% of the suite, so a module run is almost a
full run. `just test <module> <path>` does not narrow either: the path is appended to the module's default paths.

The expected outcome: during development an agent runs only the tests a change can affect, chosen by hand per area or
derived from the Git diff, and the full suite runs once on the reviewed head before integration.

## 2. User Stories

- **US-1**: As a coding agent working in this repository, I want to run the tests of the areas I changed, so that each
  verification step costs seconds instead of the full suite.
- **US-2**: As a coding agent, I want the affected tests derived from my diff, so that I do not have to know the
  dependency graph between areas and packages to choose them.
- **US-3**: As a consumer project's agent following the devkit-spec skills, I want the guidance to say when targeted
  tests are enough and when the full suite is required, so that I neither skip the full run nor repeat it.

## 3. Non-Goals

1. **Scope Excluded**: Reducing the subprocess count of the tests or the product code (template Git repositories,
   caching `git rev-parse`).
   - **Rationale**: It lowers the cost of every run but needs its own design review of safety checks in product code.
   - **When to Reconsider**: The full suite on the reviewed head becomes the dominant wait in a delivery.
2. **Scope Excluded**: Runtime coverage-based selection (pytest-testmon or similar).
   - **Rationale**: It misses subprocess and data-file dependencies just as static selection does, and adds a state
     file and xdist constraints.
3. **Scope Excluded**: Changes to CI, to the xdist worker count or distribution mode, and to `just test-cov` beyond
   accepting the same selectors as `just test`.
4. **Scope Excluded**: Guaranteeing that `just test-affected` never misses a failing test.
   - **Rationale**: Static import analysis cannot see every dependency; the full suite before integration is the
     safety net.

## 4. Acceptance Criteria & Behavioral Contracts

Selectors are the arguments between the module and the first argument that starts with `-`. An area selector names a
directory under the module's `tests/`, or a package directory under its `src/<package>/` that contains tests; a path
selector is an existing file or directory, optionally followed by a pytest node suffix (`::name`).

### [AC-01] One area of a module
- **Given** the `devkit-agt` module with `packages/devkit/tests/gate` and `packages/devkit/src/devkit/gate`
- **When** `just test devkit gate` runs
- **Then** pytest receives exactly the paths `packages/devkit/tests/gate` and `packages/devkit/src/devkit/gate` after
  the xdist options, and neither `packages/devkit/tests` nor `packages/devkit/src` as a whole

### [AC-02] Several areas with pytest arguments
- **Given** the `devkit-agt` module
- **When** `just test devkit gate worktree -k foo` runs
- **Then** pytest receives the paths of both areas followed by `-k foo`, in that order

### [AC-03] A path narrows a module run
- **Given** an existing test file `packages/devkit/tests/gate/test_hooks.py`
- **When** `just test devkit packages/devkit/tests/gate/test_hooks.py::test_commits_run_built_in_gates` runs
- **Then** pytest receives that node ID as its only path and not the module's default paths

### [AC-04] Unknown selector
- **Given** the `devkit-agt` module has no area named `nosuch`
- **When** `just test devkit nosuch` runs
- **Then** the command exits `2`, stderr names `nosuch` and lists the module's area names, and no tool is started

### [AC-05] No selector keeps the module run
- **Given** any module
- **When** `just test <module>` or `just test <module> -k foo` runs without a selector
- **Then** pytest receives the module's `tests/` and `src/` paths exactly as before this change

### [AC-06] A change selects its area and the areas that depend on it
- **Given** a branch whose only change is a file under `packages/devkit/src/devkit/worktree/`
- **When** `just test-affected --list` runs
- **Then** the selection contains `packages/devkit/tests/worktree`, `packages/devkit/tests/integration` (whose source
  imports `devkit.worktree`) and `packages/devkit-spec/tests`, and does not contain `packages/devkit/tests/gate`

### [AC-07] A leaf area selects no unrelated area
- **Given** a branch whose only change is a file under `packages/devkit/src/devkit/gate/`
- **When** `just test-affected --list` runs
- **Then** the selection contains `packages/devkit/tests/gate` and does not contain `packages/devkit/tests/worktree`,
  `packages/devkit/tests/integration` or `packages/devkit/tests/distribution`

### [AC-08] Shared foundations fall back to the full suite
- **Given** a change to any of: a file under `packages/devkit/src/devkit/core/` or `packages/devkit-advisory/`,
  `packages/devkit/src/devkit/cli.py`, `packages/devkit/src/devkit/__main__.py`, any `pyproject.toml`, `uv.lock`, any
  `conftest.py`, or a file under `packages/devkit/tests/testsupport/`
- **When** `just test-affected --list` runs
- **Then** stdout reports `mode=full` with `reason=` naming one triggering path, and `just test-affected` without
  `--list` runs the same pytest command as `just test all` with no path argument

### [AC-09] Files no test reads select nothing
- **Given** a branch whose only changes are under `specs/`, `.claude/`, `.agents/` or `guides/`
- **When** `just test-affected` runs
- **Then** stdout reports `mode=none`, pytest is not started and the exit code is `0`

### [AC-10] Data files select the tests that read them
- **Given** a branch whose only change is a Markdown file under `docs/`
- **When** `just test-affected --list` runs
- **Then** the selection is exactly the tests that read `docs/` (the documented-code tests of `devkit-agt` and
  `devkit-spec`, `packages/devkit/tests/rules/test_docs.py` and `packages/devkit/tests/workflow/test_library.py`)

### [AC-11] Every kind of change is seen
- **Given** changes that are committed since the merge base with the base ref, staged, unstaged, untracked, or a
  rename or deletion
- **When** `just test-affected --list` runs
- **Then** each changed path, including both sides of a rename and a deleted path, contributes to the selection

### [AC-12] Agent-readable result
- **Given** any selection
- **When** `just test-affected` runs
- **Then** stdout's first line is `[TEST_SELECTION: mode=<full|partial|none> base=<ref> changed=<n> paths=<n>
  reason=<text>]`; with `--list` one `[TEST_PATH: <path>]` line follows per selected path and pytest is not started;
  without it the selected paths run through the same pytest command as `just test all <paths>`, and its exit code is
  the command's

### [AC-13] Pytest arguments pass through
- **Given** a partial selection
- **When** `just test-affected -- -k foo -n0` runs
- **Then** pytest receives the selected paths followed by `-k foo -n0`

### [AC-14] Unknown base ref
- **Given** a base ref that does not resolve
- **When** `just test-affected --base nosuch` runs
- **Then** the command exits `2` with an `[ERROR]` advisory whose code is `TEST_BASE_UNKNOWN` on stderr, and pytest is
  not started

### [AC-15] Guidance keeps the full suite to one run
- **Given** this repository's `AGENTS.md` and the devkit-spec bundle skills `spec-review` and `spec-plan`
- **When** an agent reads their verification instructions
- **Then** `AGENTS.md` names `just test-affected` and `just test <module> <area...>` for development and the full
  `just test` once before integration; `spec-review` requires the full suite once on the reviewed head and the
  targeted tests during development; `spec-plan`'s validation commands distinguish the two; and `just rules-check`
  passes with the projected skill copies synchronized

## 5. Assumptions

- The base ref defaults to `main`, the base branch of every activity branch in this repository; `--base` overrides it.
- Selection works on test groups, not test files: an area's `tests/<area>` plus its `src` package, each top-level test
  file of `devkit-agt`, and the `tests/` and `src` of each other package. A group depends on its own area and on every
  devkit area or workspace package its test files import; an area's dependents come from the static imports of the
  production sources. This is coarser than file-level selection and errs toward running more.
- Importing `devkit.cli` in a test counts as depending on `core` only; a change to `cli.py` itself falls back to the
  full suite (AC-08). Tests that run the CLI in a subprocess are covered by their own area's imports and by the full
  suite before integration.
- Docs-only changes still run the four test files that read `docs/` (AC-10); this narrows the agreed "no tests for a
  docs-only change" to the files no test reads, because those four tests fail on documentation edits.
- Any change to `devkit-agt` source also selects the top-level test files of `packages/devkit/tests/` (layering, CLI
  wiring, documented codes), which cost a few seconds; changes to `scripts/` or `justfile` select the test files that
  exercise them.
