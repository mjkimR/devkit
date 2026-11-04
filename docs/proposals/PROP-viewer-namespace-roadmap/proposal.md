---
id: PROP-viewer-namespace-roadmap
title: Show namespace milestones throughout the repository viewer
summary: "Extends dashboard and roadmap discovery to namespace milestones and resolves dependencies and proposal membership across roadmap roots."
status: reviewing
created_at: 2026-11-04
target_area: capabilities/viewer/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-viewer/src/devkit_viewer/features/browse/
    - packages/devkit-viewer/tests/integration/features/browse/
    - packages/devkit-viewer/frontend/src/lib/
    - packages/devkit-viewer/src/devkit_viewer/static/
    - docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    - docs/development/reference/viewer.md
    - docs/decisions/2026-11/
  excludes:
    - docs/roadmap/
    - packages/devkit-docs/
    - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-viewer-namespace-roadmap] Show namespace milestones throughout the repository viewer

## 1. Background & Hypothesis

`SPEC-namespace-roadmap` supports milestone roots in registered namespace directories. The viewer dashboard and
roadmap loaders enumerate only `docs/roadmap/` and its flat `_archive/`. A namespace milestone is therefore absent
from their lists, and a dependency or proposal membership targeting it cannot resolve in the loaded graph.
`CAP-VIEW-repository-viewer` specifies the current global-only discovery contract.

Discovering namespace roadmap roots in both loaders will make these views cover the same milestone graph, while
retaining the read-only working-tree model, independent dashboard sections, caching and paging behavior.

## Source feedback

- `FB-viewer-namespace-roadmap-roots`: namespace milestone discovery, cross-root dependencies and proposal membership.

## 2. Technical Spike Questions

- **Q1**: Should discovery require namespace registration, or follow structural roadmap paths and identify
  unregistered roots? Compare reader-only configuration access with the viewer's existing package boundaries and
  browser data sources. Recommend one default with explicit behavior for malformed or absent registration.
- **Q2**: How can the dashboard and roadmap tab apply one discovery policy without duplicate hard-coded path rules,
  while preserving data-source compatibility, optional-root handling, symlink guards and per-root error reporting?

## 3. Proposed Design & Impact

The implementation covers global `docs/roadmap/MS-*.md` and `_archive/MS-*.md`, plus namespace equivalents under
`docs/packages/<name>/roadmap/`. Keep milestone IDs repository-wide. Resolve dependencies and proposal membership
over the combined set, including archived done/dropped milestones. Preserve unknown-target behavior for genuinely
missing milestones. The selected registration policy must be explicit; path matching alone does not prove CLI parity.

No milestone groups this proposal. Existing completed namespace milestones remain closed. No viewer write actions,
proposal lifecycle changes or general namespace browser redesign are included. No new feature dependency is assumed;
Planning identifies any architecture declaration required before Development.

### Expected acceptance checks

1. Global and namespace live/archive milestones appear in both the dashboard and roadmap tab under the chosen policy.
2. A global milestone depending on a completed namespace milestone becomes ready; the reverse direction and
   namespace-to-namespace dependencies also resolve without changing genuinely unknown or unfinished dependencies.
3. Proposals targeting namespace milestones appear in the correct roadmap cards without duplication.
4. Missing optional roots, invalid entries and symlinks retain bounded, explicit handling; unreadable roots do not
   silently erase successful roots. Cache invalidation, paging, cancellation and read-only guarantees remain intact.
5. Backend integration and frontend tests exercise discovery and graph behavior; frontend lint, type checks, tests
   and build pass, and the committed bundled page matches the frontend source.

Planning records a reproducible baseline fixture in `materials/`: one global milestone, one namespace milestone,
a cross-root dependency and a member proposal. Development measures the same fixture with the change disabled and
enabled in its worktree; it need not check out the base to measure the difference.

## 4. Lifecycle & Retirement Criteria

Planning refines the discovery policy and records the independent challenger result. Acceptance needs the user's
`plan-accept` decision; Development starts only after authorized handoff. On handoff, this proposal becomes one
feature spec and any retained PADRs become ADRs. Rejection keeps its reason through the existing proposal lifecycle.
