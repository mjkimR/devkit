---
id: SPEC-viewer-namespace-roadmap
title: Show namespace milestones throughout the repository viewer
summary: "Discovers global and namespace roadmap files in all viewer reading routes and resolves their combined milestone dependencies and proposal membership."
status: in-progress
created: 2026-11-04
related_capabilities: [CAP-VIEW-repository-viewer]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-namespace-roadmap] Show namespace milestones throughout the repository viewer

## 1. Problem Statement & Motivation

The viewer omits namespace milestones because dashboard headers and frontend loaders read only the global roadmap.
Cross-root dependencies and proposal membership cannot resolve over an incomplete set.
`ADR-viewer-namespace-roadmap-discovery` selects structural discovery without registry parsing, preserving the
saved-working-tree reader and generic library sources of `CAP-VIEW-repository-viewer`.

## Source feedback

- `FB-viewer-namespace-roadmap-roots` is promoted to this implementation; its terminal status stays unchanged.

## 2. User Stories

- **US-1**: As a monorepo maintainer, I want every structurally placed milestone visible in dashboard and roadmap.
- **US-2**: As a roadmap reader, I want cross-root dependencies and direct proposals attached to their milestones.

## 3. Non-Goals

1. **Scope Excluded**: Namespace registry validation, filtering, validity badges, config execution and new dependencies.
2. **Scope Excluded**: Screen layout, interactions, approval flows, writer endpoints and milestone lifecycle changes.
3. **Scope Excluded**: Independent filesystem symlink certification by generic sources; they expose host-returned types.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Structural discovery parity
- **Given** global and two package roadmap roots with live and flat archived milestones
- **When** backend dashboard headers, generic dashboard and roadmap documents load
- **Then** all three discover the same matching paths, including saved untracked files, regardless of absent, malformed or unregistered namespace configuration.

### [AC-02] Full-graph readiness and membership
- **Given** dependencies in all three cross-root directions, done/dropped archived prerequisites and direct proposals
- **When** history is hidden and the roadmap is built
- **Then** finished prerequisites satisfy readiness, unfinished and missing IDs retain waiting/unknown states, and each eligible direct proposal appears once while rejected proposals and spec metadata do not.

### [AC-03] Bounded path and read behavior
- **Given** unrelated documents, nested archives, symlinks and optional roadmap roots
- **When** discovery runs
- **Then** it matches only direct global/package MS-*.md and flat _archive files, refuses local symlinks through the existing reader, reads headers only on the optimized route and requires no generic-source interface change.

### [AC-04] Partial errors and cancellation
- **Given** missing optional roots, a listed unreadable root and an aborted request
- **When** discovery and document loading run
- **Then** optional absence is empty, genuine failures name their paths without discarding successful roots, and aborted or errored results do not enter the cache.

### [AC-05] Cache and paging preservation
- **Given** namespace milestones in optimized and generic dashboard sources
- **When** pages, cache expiry, refresh and generation changes occur
- **Then** exact counts, ordering, page sizes, six-request concurrency, fixed 30-second expiry and stale-write rejection retain existing behavior.

### [AC-06] Rebuilt distributable and measured outcome
- **Given** the retained baseline fixture and final implementation
- **When** the fixture is measured and backend/frontend checks and build run
- **Then** the omitted namespace milestone becomes visible, relevant checks pass, and committed viewer assets match the rebuilt frontend.

## 5. Assumptions

Structural discovery includes unregistered package directories and makes no CLI-validity claim.
Only file discovery changes; existing screen contracts need no screen drafts or UX review.
The retained baseline under `docs/materials/2026-11/20261104-viewer-namespace-roadmap/` is measured in this worktree
before and after source edits, without checking out another commit. No new feature edge is needed.
