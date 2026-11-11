---
id: SPEC-select-tests-by-read-document-paths
title: Select tests by the repository paths they read
summary: Lets affected-test selection find tests that read a repository path through a root-anchored literal path expression, instead of listing each such test in the selector's data table.
status: in-progress
created: 2026-11-11
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-select-tests-by-read-document-paths] Select tests by the repository paths they read

## 1. Problem Statement & Motivation

Handed off from proposal PROP-select-tests-by-read-document-paths on 2026-11-11. The decision and its alternatives
are in `ADR-literal-read-test-selection`.

- **Preserved Materials**: `docs/materials/2026-11/20261111-select-tests-by-read-document-paths`

`scripts/affected_tests.py` maps a changed non-source file to its readers only through the fixed `DATA` table keyed
by path prefix, and a package source file only through static imports. A test that reads a file its imports do not
reach is skipped when only that file changes. Feedback hygiene fixed two such gaps by adding table entries
(`FB-docs-selection-misses-guidance-contract-tests`, `FB-affected-selection-misses-cross-package-fix-scan`); a
failing test reached `main` while every final affected check passed.

Planning measured the class (`docs/materials/2026-11/20261111-select-tests-by-read-document-paths/read-path-survey.md`).
Every literal read under `docs/`, `examples/` and `models/` is already listed in `DATA`, so the document case is
closed only by hand-kept rows. 37 reader pairs were missed: helper reads of `.devkit/architecture.toml`, bundle
assets of another package, recipe scripts, `guides/`, `.devkit/config.toml`, a frontend script, package-root
Markdown and test data beside its reader.

Collecting the repository paths that test-tree files read through root-anchored literal path expressions lets the
selector map any changed file to its readers without hand-kept rows.

## 2. User Stories

- **US-1**: As a developer or agent running `just test-affected`, I want a test that reads a repository file by
  literal path to run when only that file changes, so that a failing reader does not reach `main` unnoticed.
- **US-2**: As a maintainer of the selector, I want existing selections and full-suite fallbacks kept, so that read
  discovery never reduces coverage.

## 3. Non-Goals

1. **Scope Excluded**: removing `DATA`, `SOURCE_TREE_TESTS` or `ALL_SOURCES_TESTS` entries the scan now covers.
   **Rationale**: it reduces selection and needs the before/after collection matrices `ARCH-07-deployment` §1.3
   asks for.
2. **Scope Excluded**: a persistent cache of parsed trees or reads; the selector stays stateless.
3. **Scope Excluded**: reads the scan cannot resolve statically: a base imported from another module, a value from a
   function call, `pytest.mark.parametrize` arguments, readers by document ID and subprocess runs in the repository
   root. They keep or gain explicit rows.
4. **Scope Excluded**: recording runtime file access or executing inspected code.
5. **Scope Excluded**: changes to the frontend checks or the `[FRONTEND_CHECK: ...]` command.

## 4. Acceptance Criteria & Behavioral Contracts

### Scenario 1 [AC-01]: Each measured miss group selects its reader

- **Given** the repository at this head
- **When** `select(ROOT, [<changed file>], tier="all")` runs for one representative file of each miss group in the
  survey
- **Then** the returned paths include its reader:
  - `.devkit/architecture.toml` → `packages/devkit-dist/tests/unit/architecture/test_layering.py` and
    `packages/devkit/tests/integration/package/test_layering.py` (helper reads)
  - `.devkit/config.toml` → `tools/devkit-dev/tests/integration/test_handbook_script.py`
  - `scripts/viewer.sh` → `packages/devkit/tests/integration/package/test_viewer_script.py`
  - `scripts/module.sh` → `packages/devkit/tests/e2e/package/test_affected_tests.py`
  - `guides/install.md` → `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`
  - a `devkit-spec` bundle skill file → `test_deep_research.py`
  - a `devkit-catalog` maintenance playbook →
    `packages/devkit-spec/tests/integration/bundles/spec/test_playbook_discovery_guidance.py`
  - `packages/devkit/tests/integration/features/compact/fixtures/<file>.txt` → `test_corpus.py` beside it
  - test modules read as data: `tools/devkit-dev/tests/integration/test_bundle_citations.py` →
    `test_affected_tests.py`; `packages/devkit-viewer/tests/integration/test_cli.py` →
    `packages/devkit/tests/integration/package/test_test_environment.py`
  - package-root Markdown: `packages/devkit-catalog/README.md` →
    `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`.

### Scenario 2 [AC-02]: Read discovery never reduces selection

- **Given** a change that selects the full suite today (a full trigger or an unknown path)
- **When** the selector runs on the same revision
- **Then** the mode is `full` with the same reason.
- **Given** any change that selects partially or nothing today
- **When** the selector runs with read discovery
- **Then** its selection without read discovery is a subset of its new selection, every `DATA` row still applies
  and the reason of a path that had a cause before is unchanged.

### Scenario 3 [AC-03]: Paths no test reads still select nothing

- **Given** `.claude/skills/x/SKILL.md`
- **When** the selector runs
- **Then** the result is `mode=none`, `reason=untested`.
- **Given** `packages/devkit-viewer/frontend/src/lib/App.svelte`, which no test reads
- **When** the command runs
- **Then** stdout is `[TEST_SELECTION: mode=none base=main changed=1 paths=0 reason=frontend]` followed by the
  `[FRONTEND_CHECK: ...]` line.
- **Given** a fixture workspace where a test builds a `tmp_path` path from a literal, joins an unanchored string,
  reads the repository root itself or reads its own file
- **When** a file at that literal path changes
- **Then** that test is not added.

### Scenario 4 [AC-04]: The existing assertions change only as the new behavior requires

- **Given** `packages/devkit/tests/e2e/package/test_affected_tests.py`
- **When** the selector's own tests run
- **Then** they pass with these assertions changed and no other assertion weakened:
  - `guides/install.md` selects `test_deep_research.py`, which reads `guides/**/*.md`; `.claude/` and `.agents/`
    paths still select nothing.
  - `.devkit/config.toml` selects `test_handbook_script.py`.
  - `.devkit/architecture.toml` adds the helper-attributed layering tests to its two `DATA` paths, reason unchanged.
  - `scripts/viewer.sh` alone is `partial` with `test_viewer_script.py`, still `reason=frontend` with the
    `[FRONTEND_CHECK: ...]` line.

### Scenario 5 [AC-05]: The documents describe read discovery

- **Given** `docs/development/ci-cd.md` and `ARCH-07-deployment` §1.3
- **When** `uv run devkit rules check --ci --base main` runs
- **Then** it reports no violation, the documents describe read discovery as only adding tests, and neither
  describes `guides/`, `.devkit/`, package-root Markdown or the frontend as selecting nothing when a test reads them.

### Scenario 6 [AC-06]: Bounded cost

- **Given** a document-only change (`docs/x.md`) on the measuring machine
- **When** `select` runs at this head with and without read discovery, best of 3
- **Then** read discovery adds at most 3 s.

### Scenario 7 [AC-07]: Each read form and attribution is recognized

- **Given** a fixture workspace whose test-tree files read repository paths through `Path(__file__)` chains
- **When** a file at the read path changes
- **Then** the reader is added for each form: a chain nested in a call (`(ROOT / "x").read_text()`), a name bound once,
  `joinpath` and `Path(<anchored>, "<literal>")`, a loop variable over a literal tuple, a literal `glob` or `rglob`
  pattern (including a new subdirectory matching an ancestor segment), `iterdir`, and a join with a runtime segment
  (which reads its base directory).
- **And** a conftest's read selects the test modules under its directory, and a helper's read selects the test modules
  that import it, directly or through another helper.

### Scenario 8 [AC-08]: Subprocess readers of release recipes keep an explicit row

- **Given** `scripts/release.sh` or `justfile`
- **When** the selector runs
- **Then** `packages/devkit/tests/integration/package/test_version_script.py` is selected.

## 5. Source feedback

- `FB-docs-selection-misses-guidance-contract-tests` (resolved by a `DATA` row): the generic read scan for documents.
- `FB-affected-selection-misses-cross-package-fix-scan` (resolved by `ALL_SOURCES_TESTS`): its reader scans an
  unresolved base, which no literal scan sees, so it keeps its explicit mapping.

## 6. Assumptions

- AC-04 names `test_affected_tests.py:121-124`, `:177` and `:335` as the changed assertions. Two more change
  because AC-01 requires them: the `.devkit/architecture.toml` path assertion (`:172`) adds its helper readers, and
  the empty-selection command test (`:322`) uses `.claude/x.md` instead of `guides/x.md`, which
  `test_deep_research.py` now reads through `guides/**/*.md`.
- The survey's 21 package-root Markdown pairs came from package directories read as a whole. At this head the scan
  finds no test that reads a package root as a directory; the package READMEs a test reads by exact path
  (`packages/devkit-catalog/README.md`) select it, and `packages/devkit-spec/README.md`, which no test reads,
  still selects nothing.
- A changed path that had no other cause and gains readers reports the cause `reads` in `reason`; a path with
  another cause (a `DATA` prefix, a source node, `tests`, `frontend`) keeps its reason.
- Names bound once are resolved per function scope with module scope as the fallback; a name bound in several places
  of one scope or an imported name is not resolved. A string literal, an f-string whose parts resolve, or an entry
  of a literal dict counts as a literal segment.
- "A loop variable over a literal tuple or list" includes tuple targets, a name bound once to such a literal and
  the `keys()`, `values()` and `items()` of a literal dict. A function parameter takes the arguments of every call
  of its function in the same file when every use of the function name is such a call; otherwise it is a runtime
  segment. Without this, `test_lockstep.py`'s `_project(directory)` reads the whole `packages/` directory and
  `packages/devkit-viewer/frontend/src/lib/App.svelte` would select it, against AC-03.
- Helper attribution resolves importers only for files with reads, pre-filtered by the helper's module name in the
  importer's text (a package initializer in the importer's own or an ancestor directory skips the filter, because a
  relative package import does not name it), and reuses the selector's per-file import discovery.
- A path bound to a name is read through the name's uses; when no use in the file resolves to the binding (a rebound
  name, a class attribute, a helper constant used only by importers), the bound value itself is the read.
