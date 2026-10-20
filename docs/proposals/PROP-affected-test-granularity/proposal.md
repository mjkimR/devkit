---
id: PROP-affected-test-granularity
title: Finer affected-test groups and dependency nodes
summary: "Reduce unnecessary affected-test execution with finer test groups and source dependency nodes while preserving conservative fallback and required coverage."
status: draft
created_at: 2026-10-20
target_area: delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - scripts/
    - packages/devkit/tests/
    - packages/devkit-spec/tests/
  excludes:
    - packages/devkit-advisory/src/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-affected-test-granularity] Finer affected-test groups and dependency nodes

## 1. Background & Hypothesis

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

## 2. Technical Spike Questions

- **Q1: Group granularity.** Compare individual test files with subdirectory groups, including conftest fixtures,
  shared helper imports and rule tests shipped under source directories. Quantify reductions and selector cost.
- **Q2: Source granularity.** Split large package nodes such as devkit_spec by real modules or areas. Define root
  imports, re-exports, relative imports and transitive edges so finer tests do not retain a package-wide dependency.
- **Q3: Helpers.** Separate generic Git fixture helpers from gate-specific helpers where coupling is artificial.
  Do not hide a real dependency with deferred imports merely to evade static selection.
- **Q4: Coverage safeguards.** Preserve mode=full triggers and unknown-change fallback, explicit data dependencies,
  layering/CLI checks and frontend selection. Verify additions, removals and renamed paths. Determine representative
  dependency fixtures and repository simulations that detect under-selection rather than merely lower counts.

## 3. Proposed Design & Impact

Start with test-file groups and finer source nodes for devkit_spec; retain broader groups where evidence requires
them. Inspect `packages/devkit/tests/test_affected_tests.py` and helper fixtures before selecting implementation
boundaries. Helper extraction is included only where necessary for demonstrated false-positive propagation.

Expected acceptance evidence:

- Reproducible before/after results identify the base revision, representative changed paths, selected test paths,
  collected counts and selection time. Performance claims come from measurements on the implemented design.
- A dependency used by one test does not select unrelated tests solely because they share a directory; tests with
  actual direct/transitive dependencies remain selected, including shared fixtures and embedded rule tests.
- Narrow devkit_spec changes select relevant subareas instead of the whole package by construction, with tests
  covering cross-area imports and package-root/re-export behavior.
- Shared-foundation and unsupported change cases retain conservative full-suite fallback. Test-only changes,
  data mappings, mandatory structural checks and frontend dispatch continue to follow their contracts.

Scope excluded: changing production package boundaries to reduce test counts, weakening coverage or full fallback,
changing nightly/release verification policy, and optimizing unrelated runtime code. No current selector behavior
or verification policy changes as part of this draft.

## 4. Lifecycle & Retirement Criteria

This is a queued draft, separate from the local-configuration and MCP Planning activities. Resume only when selected
for Planning; first reproduce the supplied analysis, then settle the smallest safe granularity change and its
validation. Draft registration does not authorize implementation. Do not require arbitrary test-count targets at
the expense of demonstrated dependency coverage.
