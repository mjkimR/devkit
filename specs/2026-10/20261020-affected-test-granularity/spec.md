---
id: SPEC-affected-test-granularity
title: Finer affected-test groups and dependency nodes
summary: Reduce unnecessary affected-test execution with finer test groups and source dependency nodes while preserving conservative fallback and required coverage.
status: in-progress
created: 2026-10-20
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-affected-test-granularity] Finer affected-test groups and dependency nodes

## 1. Problem Statement & Motivation

Handed off from proposal PROP-affected-test-granularity on 2026-10-20.
- **Preserved Materials**: `docs/materials/2026-10/20261020-affected-test-granularity`

### 1. Background & Hypothesis

`scripts/affected_tests.py` selects tests through a static import graph, but area-wide test groups combine unrelated
imports and non-devkit namespace packages such as `devkit_spec` collapse into one source node and one test group.
Consequently a narrow source change can select more than a thousand tests. The structure is confirmed by inspection
of `Workspace.groups`, `node_of`, `sources` and `_source_node`; exact current collection counts remain unverified.

Submitted analysis reports 1,103 devkit-spec tests in one group and selection counts of 1,072 for gate, 2,021 for
workflow, 1,838 for worktree, 2,729 for rules, 2,023 for distribution and 3,000 for compact changes. Its file-group
simulation reports gate 1,072 to 187, worktree 1,838 to 923 and workflow 2,021 to 1,104. These are supplied baseline
claims to reproduce during Planning, not independently verified benchmarks or promised acceptance thresholds.

The hypothesis is that finer test groups and source nodes reduce false-positive selection while preserving the
conservative fallback and actual dependency coverage. A universal target of 100–300 tests is not established.

## 2. User Stories

- **US-1**: As a developer/agent, I want narrower affected-test selection while preserving dependent consumers and conservative fallback.

## 3. Non-Goals

1. **Scope Excluded**: Function-level selection, runtime coverage databases, production refactors and nightly/release policy changes.

## 4. Acceptance Criteria & Behavioral Contracts

### Scenario 1 [AC-01]: File groups and source graph

**Given** the workspace source and test inventory,
**When** a production source path changes,
**Then** the selector applies the following dependency contract.

Build one group per collected-style test_*.py file, including rule tests under src and existing top-level tests.
Discovery stays filesystem/static; selecting tests does not import production modules or run pytest. Keep current
area nodes for devkit namespace packages and broad default behavior for other workspace packages. Opt devkit_spec
into module-level source nodes (including __init__.py) rather than a hand-maintained list of domain names. Keep the
existing CLI sentinel, mode values, --list behavior and frontend directive. Explain reasons deterministically.

Resolve absolute and relative imports, literal import_module/find_spec/resource calls, package initialization,
re-exports, from-package imports and import cycles conservatively. A module import also depends on the initializers
Python executes. A root import or wildcard that cannot be narrowed retains a broad package dependency. Distinguish
modules from imported attributes using the source inventory; do not fabricate a missing module node for every
attribute. When an exact resolution is uncertain, widen within the known owner; never drop the dependency.

Groups combine their own imports with transitive local helper dependencies and applicable ancestor conftest imports.
Resolve helpers against known pytest pythonpath/test roots and relative locations; include function-local imports,
not only module-level statements. Preserve ambiguity as a broad owner dependency instead of guessing between
same-named test helpers. Cache parsed files once per selector run and terminate import cycles deterministically.

For fine-grained spec tests, do not unconditionally add the whole devkit_spec owner node to every file: that defeats
the finer source graph. Retain a broad owner dependency for opaque tests or dependencies that cannot be resolved,
and explicit mappings for known subprocess/entry-point/resource-based consumers. Tests scanning the source tree or
loading the CLI/bundle dynamically remain conservatively broad where their actual contract requires it. Existing
devkit area-owner edges can remain in this first change; this proposal does not claim every area reaches leaf-level
precision. New packages such as devkit-mcp retain broad owner grouping until their mapping is understood.

### Scenario 2 [AC-02]: Conservative behavior

**Given** an unsafe, shared, data, test-only or frontend change,
**When** selection runs,
**Then** the following fallback and dispatch behaviors are preserved.

Keep all existing full-suite triggers: shared core/advisory, CLI assembly, pyproject metadata, uv.lock, shared-helper
changes and conftest changes. Preserve fixed data-path mappings, mandatory SOURCE_TREE_TESTS, frontend dispatch,
unknown-path full fallback, test-only selection and Git merge-base/rename handling. Deleted or renamed fine modules
whose relationships cannot be reconstructed safely select full; do not silently filter away the changed module.
Unparseable relevant source/helper files or ambiguous source inventory likewise select full instead of an empty
result. Readable static dynamic-import uncertainty can use a broad owner dependency; this does not solve arbitrary
runtime discovery. Existing complete nightly/manual/release checks remain the coverage backstop.

No dependency is hidden by moving an import into a function. Helper extraction is not necessary for the selected
first design: keep testsupport.gate's real gate dependency and report its remaining selection cost. This proposal
adds no production refactor or function-level analysis solely to make counts lower.

### Scenario 3 [AC-03]: Acceptance evidence

**Given** independent dependency fixtures and the integrated source revision,
**When** baseline and new selection are verified,
**Then** all following evidence is recorded.

- **AC1:** File groups isolate unrelated test-file imports. A fixture with one external consumer and an unrelated
  sibling proves both positive selection and negative exclusion; applicable conftest/helper imports still select
  the consumer, including nested/function-local imports and cycles.
- **AC2:** Narrow devkit_spec edits select their direct/transitive test consumers without automatically selecting
  unrelated subareas. Cover relative imports, package initializers, re-exports, from-package attributes, wildcard
  broadening and a root CLI/entry-point consumer. Expectations come from authored fixtures, not the same graph code.
- **AC3:** Every existing full trigger, fixed data mapping, required structural check and frontend case remains.
  Tests cover deleted/renamed modules, unknown or unparseable paths and opaque consumers; inability to resolve
  dependency coverage never produces a misleading mode=none.
- **AC4:** At the same source revision, reproduce current and new selected file sets, collected parametrized counts
  and selector timing for gate/workflow/worktree/rules/distribution/compact and at least scope/documents/proposals
  spec changes. Demonstrate gate reduction and at least two independent spec-subarea reductions, while required
  consumers remain selected. Do not substitute a target count or percentage for coverage evidence. Investigate
  material selector overhead and report it rather than promising a hardware-independent bound.
- **AC5:** Keep output/runner behavior and package discovery stable, including new coarse-default packages and
  embedded rules. Update selector tests and the development CI/workflow reference to the actual granularity.

Development is medium: implementation, focused meaningful graph/regression tests, lint/types, affected tests with
full fallback intact, one independent code review and separate reconcile check where required by cross-component
scope. The selector change chooses its own tests through the existing script mapping; verify the future selector
against independent fixtures and collection evidence before trusting its reduced selection.

Scope excluded: generic Python whole-program analysis, test-function selection, persistent coverage databases,
production package splitting, unrelated helper refactoring, changing nightly/release policy and optimization of
unrelated runtime code. No current selector behavior changes during Planning.

## 5. Assumptions and premises

The integrated base retains the selector's area/package grouping and the accepted source interfaces.
The new devkit-mcp package and its explicit runtime consumer mapping are present and must remain covered.
The accepted design in `ADR-select-tests-by-file-with-finer-spec-dependency-nodes` still applies.
Measurements are refreshed on this base; historical counts are not acceptance thresholds.
