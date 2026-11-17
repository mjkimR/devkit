---
id: FB-viewer-roadmap-branch-plumbing
title: The viewer roadmap keeps other-branch plumbing no data source can feed
scope: repo
kind: suggestion
category: other
target: packages/devkit-viewer/frontend/src/features/roadmap/RoadmapView.svelte
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-viewer-roadmap-branch-plumbing] The viewer roadmap keeps other-branch plumbing no data source can feed

Dead code left after the viewer became a one-host tool.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `RoadmapView.svelte` keeps an always-empty `branches` array and an `opens(_ref)` helper that
  ignores its argument, and `buildRoadmap` in `api/roadmap.ts` still accepts other-branch documents. The local data
  source has no branch enumeration (`refs` was removed), and the roadmap reads only the registered checkout.
  `normalizeTree` still maps foreign `dir`/`file` item types the local server never returns, and the repository
  `.gitignore` keeps `dist`/`dist-pack` entries of the removed library build.
- **Proposed Procedure**: Drop the branch parameter from `buildRoadmap` and the dead helpers in `RoadmapView`, the
  `dir`/`file` mapping in `normalizeTree`, and the stale `.gitignore` entries, with their tests.
- **Expected Benefit**: Less code and no parameters that suggest other-branch roadmaps exist.
- **Cost & Risk**: Small refactor of the roadmap builder and its tests; roadmap behavior is unchanged.
- **Attempted**: Hypothesis; left out of `SPEC-viewer-internal-simplification`, whose scope named no roadmap change.

## Evidence

```text
RoadmapView.svelte: let branches: BranchDocuments[] = []; const opens = (_ref: string | null) => baseRef === branch;
api/repository.ts normalizeTree: item.type === 'dir' ? 'tree' : item.type === 'file' ? 'blob' : item.type
.gitignore: dist / dist-pack entries for the removed svelte-package and npm pack outputs
```

## Resolution

- **Disposition**: `SPEC-viewer-roadmap-plumbing` resolved it: `buildRoadmap` takes only the checkout's documents
  (`BranchDocuments`, `isActivityBranch` and the member `branch` field removed), `RoadmapView` lost `branches` and
  `opens`, `MilestoneItem` lost its per-branch open props and branch badge, `normalizeTree` keeps the server's
  `tree`/`blob` types, and `.gitignore` dropped the `frontend/dist`/`dist-pack` entries. Verified by
  `just viewer install && just viewer lint && just viewer check && just viewer test && just viewer build` (244 passed)
  and `just test-affected --base main` (194 passed).
