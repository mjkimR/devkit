---
id: SPEC-viewer-roadmap-plumbing
title: Remove dead other-branch plumbing from the viewer roadmap
summary: Drop the unused branch parameter and helpers from the viewer roadmap, the foreign dir/file mapping in normalizeTree and the stale library-build gitignore entries, with their tests; roadmap behavior is unchanged.
status: in-progress
created: 2026-11-17
related_capabilities: [CAP-VIEW-repository-viewer]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-roadmap-plumbing] Remove dead other-branch plumbing from the viewer roadmap

## 1. Problem Statement & Motivation

The viewer reads one registered working tree and enumerates no other branch (`CAP-VIEW-repository-viewer` §5
Source). Its roadmap code still carries parameters for other-branch roadmaps that no data source can feed:
`RoadmapView.svelte` passes an always-empty `branches` array to `buildRoadmap` and gates every open action through an
`opens(_ref)` helper that ignores its argument; `buildRoadmap` merges other-branch documents with a branch weight,
each roadmap member carries a `branch` that is always `null`, and `MilestoneItem.svelte` renders a branch badge and
per-branch open checks that never vary. `normalizeTree` maps `dir`/`file` item types that the local server never
returns (it emits only `tree` and `blob`), and the repository `.gitignore` keeps `dist`/`dist-pack` entries of the
removed npm library build (the page now builds into `src/devkit_viewer/static/`). The dead code suggests features
that do not exist and costs every reader of the roadmap.

## 2. User Stories

- **US-1**: As a maintainer of the viewer, I want the roadmap code to describe only the single-checkout roadmap it
  shows, so that no parameter or helper suggests other-branch roadmaps exist.

## 3. Non-Goals

1. **Scope Excluded**: Roadmap behavior: discovery, ordering, readiness, membership, history, caching and the
   open actions stay as they are.
2. **Scope Excluded**: The Planning overlay and its branch sources, which belong to other views.
3. **Scope Excluded**: The `.svelte-kit/` and `node_modules/` ignore entries and every other `.gitignore` rule.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The roadmap builder takes only the checkout's documents
- **Given** the frontend source after this change
- **When** `buildRoadmap` is called
- **Then** its signature is `buildRoadmap(documents, { history })`; `rg -n "BranchDocuments|isActivityBranch|opens\(|canOpenMember|canOpenBase" packages/devkit-viewer/frontend/src` prints no line and the `Member` type has no `branch` field

The existing ordering, readiness, membership, rejected-filtering and history tests pass with the new signature, and
`just viewer check` exits 0.

### [AC-02] The roadmap view shows the same roadmap without branch plumbing
- **Given** a checkout with active and archived milestones and direct proposal members
- **When** `RoadmapView` renders it
- **Then** every milestone shows its `View raw` button, every member title is a button that calls `onOpen` with the
  member path, no branch badge renders, and `just viewer test` exits 0

### [AC-03] Tree listings keep the server's item types
- **Given** a tree response whose items carry the server's `tree` and `blob` types
- **When** `normalizeTree` normalizes it
- **Then** it returns the items with their types unchanged, directories before files and each group by name, and
  performs no `dir`/`file` mapping

### [AC-04] The repository ignores no removed library build output
- **Given** the repository `.gitignore`
- **When** it is read
- **Then** it has no `packages/devkit-viewer/frontend/dist/` or `packages/devkit-viewer/frontend/dist-pack/` entry,
  and its comment names only the dependencies and the remaining local build state

## Source feedback

- `FB-viewer-roadmap-branch-plumbing`: the whole suggestion (branch parameter, `RoadmapView` helpers,
  `normalizeTree` mapping, `.gitignore` entries) is in scope.

## Assumptions

- The local server emits only `tree` and `blob` items: the working-tree and Planning tree readers in
  `devkit_viewer.features.browse.repositories` construct no other type.
- `MilestoneItem.svelte` belongs to the same plumbing: its `canOpenBase`/`canOpenMember` props and branch badge only
  carried the dead branch values, so removing them is inside the agreed scope and keeps every open action visible.
