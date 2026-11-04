---
id: ADR-viewer-namespace-roadmap-discovery
title: Discover viewer namespace roadmaps by structural paths
summary: "For viewer roadmap discovery across local and library sources, we match global and namespace roadmap paths without reading the namespace registry, to preserve reader independence, accepting that unregistered directories can appear."
proposal: SPEC-viewer-namespace-roadmap
status: accepted
created_at: 2026-11-04
---

# [ADR-viewer-namespace-roadmap-discovery] Discover viewer namespace roadmaps by structural paths

- **Status**: Accepted.

## 1. Context & Problem Statement

`CAP-VIEW-repository-viewer` limits discovery to global roadmap paths. `CAP-DOCS-namespaces` supports package
roadmap roots, so the viewer omits those milestones and cannot resolve their graph edges. The local server reads
saved working-tree files, while library hosts supply ordinary tree/blob methods. The viewer does not run each
repository's devkit and remains independent of its pinned document-system version (`ADR-repository-viewer`).

## 2. Decision Drivers

- Cover package milestones, archived prerequisites and direct proposal membership on every viewer reading route.
- Keep ordinary reads local, read-only and independent of the repository's installed environment.
- Preserve the existing generic data-source interface and bounded selective document reads.
- State the difference between visible files and governance-valid registered namespace documents.

## 3. Considered Options

- **Structural roadmap paths** (selected): one path policy for Python headers and frontend tree/blob readers;
  no configuration parser, dependency or data-source method; unregistered directories can appear.
- **Registered namespaces only**: closer registry parity with CLI discovery; both languages/hosts need a shared
  registry interpretation and error policy, which expands this file-reader change.
- **Keep global-only discovery**: no implementation cost; fails to display the requested package milestone graph.

## 4. Decision Outcome

Structural roadmap discovery is selected to keep local and library readers independent of namespace configuration.

- Both dashboard routes and the roadmap loader discover global roadmap roots and the same roots directly under
  `docs/packages/<name>/`, including only the reserved flat `_archive/`. → `CAP-VIEW-repository-viewer` 4.1 and 5 (MUST).
- Discovery does not read namespace registration, and matching unregistered paths are visible without a validity
  claim. Absent or malformed namespace configuration does not affect the candidate set.
  → `CAP-VIEW-repository-viewer` 4.1 and 5 (MUST).
- Local filesystem symlink checks remain enforced by `WorkingTreeReader`. Generic discovery trusts the host
  tree/blob representation and cannot independently certify filesystem symlink identity; the interface gains no
  field or host obligation. → `CAP-VIEW-repository-viewer` 2 and 6 (MUST).
- The full discovered milestone set resolves dependency readiness and proposal membership before history
  filtering; existing unknown/waiting and direct-proposal rules remain. → `CAP-VIEW-repository-viewer` 5 (MUST).
- Local reads continue to use the saved checkout; generic hosts keep their existing tree/blob interface. The
  discovery extension adds no write, fetch, Git-ref read, config execution or runtime dependency.
  → `CAP-VIEW-repository-viewer` 2, 3 and 6 (MUST).
- One frontend helper serves both generic routes. Python implements the same path contract with parity scenarios;
  cross-language code sharing is unnecessary.

These clauses extend the discovery contract. They replace no decision of `ADR-repository-viewer`; its distribution,
working-tree reads, independent parsing and Planning-overlay clauses remain in force.

## 5. Consequences

- Package milestones and cross-root graph edges become visible with existing sources.
- Unregistered package directories can appear; the viewer does not certify document validity or exact CLI parity.
- Directory metadata reads grow with the number of package roots; discovery avoids unrelated bodies and respects
  existing concurrency, cache, error and cancellation contracts. No measured speedup is claimed.
- Namespace filtering and governance badges remain outside this decision. Reconsider registry-aware discovery
  when a concrete viewer requirement needs validity filtering rather than visibility.

## 6. Confirmation

- `tests/integration/features/browse/test_namespace_roadmap.py` verifies global/two-package and configuration
  matrices, saved untracked content, header-only reads, local symlinks and partial errors.
- `frontend/src/lib/api/milestones.test.ts` verifies shared generic discovery, host-returned types, cross-root
  readiness and proposal membership, optional/listed root errors, abort/refresh/expiry, six workers and optimized pages.
- Existing dashboard, roadmap and view tests preserve paging, caches, Planning overlays and detail paths.
- `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer pack`, `just viewer build` and
  `devkit generated check viewer-assets` verify the source and committed application build.
- `CAP-VIEW-repository-viewer` sections 2, 4.1, 5 and 6 restate the decision. The retained baseline and observed
  implementation result live under `docs/materials/2026-11/20261104-viewer-namespace-roadmap/`.
