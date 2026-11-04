---
id: SPEC-viewer-namespace-roadmap
title: Show namespace milestones throughout the repository viewer
summary: Extends dashboard and roadmap discovery to namespace milestones and resolves dependencies and proposal membership across roadmap roots.
status: planned
created: 2026-11-04
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-viewer-namespace-roadmap] Show namespace milestones throughout the repository viewer

## 1. Problem Statement & Motivation

Handed off from proposal PROP-viewer-namespace-roadmap on 2026-11-04.
- **Preserved Materials**: `docs/materials/2026-11/20261104-viewer-namespace-roadmap`

### 1. Background & Hypothesis

`SPEC-namespace-roadmap` supports milestone roots in registered namespace directories. The viewer dashboard and
roadmap loaders enumerate only `docs/roadmap/` and its flat `_archive/`. A namespace milestone is absent from their
lists, and a dependency or proposal membership targeting it cannot resolve in the loaded graph.
`CAP-VIEW-repository-viewer` specifies the global-only discovery contract.

Ordinary local reads use saved working-tree files, including uncommitted and untracked files. They do not read Git
objects or select another branch. Library hosts supply their own `RepositoryDataSource`; the shared frontend cannot
assume a Python environment or a local server. `ADR-repository-viewer` keeps parsing independent of the repository's
installed devkit version.

Extending structural discovery in the backend, generic dashboard fallback and roadmap loader covers the combined
milestone graph without introducing a namespace configuration parser or a mandatory data-source method.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Show namespace milestones throughout the repository viewer so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### Source feedback

- `FB-viewer-namespace-roadmap-roots`: namespace milestone discovery, cross-root dependencies and proposal membership.
  Its source stays promoted; Planning and eventual implementation do not change that terminal status.

### 2. Technical Spike Questions

#### Q1: Namespace registration policy — recommendation for acceptance

Recommendation: discover structural paths without consulting `[[tool.docs.namespaces]]`.

| Option | Result | Cost and limitation |
| --- | --- | --- |
| Structural paths (recommended) | Display every matching global or package roadmap file. Missing or malformed namespace configuration does not affect discovery. | Unregistered package directories also appear; the viewer does not claim registry validation or exact CLI parity. |
| Registered namespaces only | Display global and registry-listed namespace roots. | Needs a shared registration interpretation for Python and library hosts, plus malformed-config behavior; a backend-only filter leaves generic sources inconsistent. |
| Global roots only | Keep the existing viewer contract. | Namespace milestones and cross-root graph edges remain missing; does not satisfy the requested outcome. |

The recommendation follows the existing book's structural package-directory handling and keeps the viewer a file
reader rather than a governance validator. This guarantee is part of the proposal's direction acceptance and is drafted
in `ADR-viewer-namespace-roadmap-discovery`.

#### Q2: Consistent discovery across reading routes — Planning recommendation

Use one frontend roadmap discovery helper and path predicate for the generic dashboard and roadmap loader. The
Python dashboard header reader implements the same explicit path contract and is verified with the same scenario
matrix. Sharing a policy across languages does not require a runtime policy file or a new endpoint.

Enumerate `docs/`, optional `docs/packages/`, direct package directories, and each discovered `roadmap/` and flat
`_archive/`. Read only candidate frontmatter on the optimized dashboard route. Generic sources retain their existing
selective full-document fallback. Do not recursively read arbitrary package document bodies to discover milestones.

### 3. Proposed Design & Impact

#### Discovery contract

- Match only `docs/roadmap/MS-*.md`, `docs/roadmap/_archive/MS-*.md`,
  `docs/packages/<name>/roadmap/MS-*.md`, and `docs/packages/<name>/roadmap/_archive/MS-*.md`.
- `<name>` is one nonempty directory segment. No registry validity is inferred from that segment. Nested archive
  directories, deeper roadmap directories, `.git`, traversal segments and non-milestone filenames remain outside
  discovery. The local `WorkingTreeReader` continues to omit/refuse filesystem symlinks. Generic discovery uses
  host-returned tree/blob types and cannot independently certify filesystem symlink identity; it adds no host
  obligation or metadata field.
- Under the recommended option, unregistered directories are displayed by path with no claim that they are valid
  namespace milestones. Namespace registration, file format and ID uniqueness remain repository rule concerns.
- Resolve readiness and proposal membership over the complete discovered milestone set before history filtering.
  Done or dropped archived milestones satisfy prerequisites. A truly missing dependency remains unknown.
- Preserve the server's working-tree source, existing `RepositoryDataSource` signatures, proposal Planning overlay
  boundaries, 30-second cache expiry and generation rules, page sizes and ordering, six-request frontend concurrency,
  cancellation and no-cache-on-error behavior.
- Missing optional roots are empty. Listed roots that fail to read report their paths in existing errors and retain
  successfully read roots. A failed discovery must not become a successful empty list.

#### Acceptance scenarios

1. Global and two package roadmap roots, with live and archived milestones, produce the same candidate path set in
   backend header discovery, generic dashboard discovery and the roadmap loader. Uncommitted/untracked local files
   are included. The registration-policy matrix covers present, absent and malformed configuration.
2. Global-to-package, package-to-global and package-to-package dependencies on done/dropped archived prerequisites
   are ready even with history hidden. Known unfinished prerequisites remain waiting; missing IDs remain unknown.
3. A direct proposal naming a package milestone appears on that milestone once; rejected proposals and SPEC
   metadata do not become members. Planning overlay behavior remains as specified by `CAP-VIEW-repository-viewer`.
4. Unregistered structural roots follow the accepted Q1 policy. Missing roots are empty; unreadable roots expose
   errors without discarding successful roots. Local filesystem symlink directories/files, deep nested archives
   and unrelated docs are not enumerated as milestones. Generic-source tests use host-returned tree/blob types
   without claiming independent filesystem symlink detection. The optimized route reads headers only; bodies
   remain page-scoped.
5. Refresh/expiry/generation invalidation, cancellation, cache rejection on errors, fixed list ordering, exact counts,
   archived detail paths and page sizes retain existing behavior. Library sources need no added method or parser.
6. Backend integration tests and frontend discovery/graph tests pass. Run `just lint-check devkit-viewer`,
   `just check devkit-viewer`, the selector's frontend checks, `just viewer lint`, `just viewer check`,
   `just viewer test`, `just viewer build`, and `devkit generated check viewer-assets`; commit the rebuilt page.

#### Delivery and limits

One feature spec implements this outcome. Development updates `CAP-VIEW-repository-viewer` sections 4.1 and 5,
`docs/development/reference/viewer.md`, the package README where its discovery description changes, the application
source/tests, and the committed frontend artifact. The discovery PADR becomes an ADR. No new runtime dependency or
feature edge is required by the recommended design. The README is an exact declared ownership path.

No milestone groups this proposal, and completed namespace milestones stay closed. No writer endpoint, general
namespace browser redesign, registration editor, per-namespace filter or automatic validity badge is included.
No screen layout or interaction changes are proposed, so there are no screen drafts or optional UX review request.

The controlled baseline fixture and observations live in `docs/materials/2026-11/20261104-viewer-namespace-roadmap/baseline.md` and `docs/materials/2026-11/20261104-viewer-namespace-roadmap/baseline.json`.
Development reruns the same fixture in its own worktree with the discovery change disabled and enabled; no checkout
of a different commit is needed. The baseline is a count/path observation, not a performance measurement.

### 4. Planning Decisions

- Keep `task_kind: feature`, `size: M`, and Development effort `medium`; a behavior extension changes the viewer's
  current global-only contract rather than repairing a promise it already makes.
- Keep the viewer independent of `devkit-docs` and the repository's installed environment.
- Recommend Q1's structural discovery as part of accepting this proposal. No additional preference question is
  needed before that direction review. Q2 is an implementation recommendation within the requested scope.

### 5. Lifecycle & Retirement Criteria

Planning returns the proposal in `reviewing` with its challenger evidence and recommended direction. Acceptance
needs the user's `plan-accept` decision; the Host owns acceptance and Planning integration. Development
starts only after authorized handoff. Handoff moves this proposal into one feature spec and promotes its retained
PADR to an ADR. Rejection keeps its reason through the existing lifecycle. Planning changes no production source.

