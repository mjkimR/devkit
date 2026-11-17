---
id: PLAN-viewer-roadmap-plumbing
spec: SPEC-viewer-roadmap-plumbing
---

# Technical Plan: `SPEC-viewer-roadmap-plumbing` Remove dead other-branch plumbing from the viewer roadmap

## 1. Constitution & Invariant Review

None. `CAP-VIEW-repository-viewer` §5 already states that the roadmap reads the registered working tree and enumerates
no other branch; this change removes code that contradicted nothing observable. `ADR-roadmap-and-milestones-ledger`
and `ADR-internal-repository-viewer` are unchanged. No architecture edge, package or feature is added or removed.
Design, domain and operations documents are unaffected: the change touches only frontend internals and one
`.gitignore` comment block, with no persisted format, identity, ordering or code.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `frontend/src/api/roadmap.ts` | `buildRoadmap(documents, options)`: members come from the given documents only; one member per slug, the first in input order wins, as the old equal-weight rule did. `BranchDocuments`, `isActivityBranch` and `Member.branch` go. |
| `frontend/src/features/roadmap/RoadmapView.svelte` | `branches` and `opens` go; it calls `buildRoadmap(base, { history })`. `baseRef` stays for the "Base: … branch" note. |
| `frontend/src/features/roadmap/MilestoneItem.svelte` | `canOpenBase`, `canOpenMember` and the branch badge with its `.branch` style go; `View raw` and the member title buttons always render, as they did with the always-true helper. |
| `frontend/src/api/repository.ts` | `normalizeTree` keeps item types as the server sends them (`tree`/`blob`). |
| `frontend/src/api/roadmap.test.ts`, `api/milestones.test.ts`, `api/repository.test.ts` | Calls use the new signature; branch-only cases are removed; a `normalizeTree` case pins type passthrough and order. |
| `.gitignore` | Drop `packages/devkit-viewer/frontend/dist/` and `dist-pack/`; the comment names dependencies and local build state. |
| `src/devkit_viewer/static/` | Rebuilt by `just viewer build` (`viewer-assets`). |

## 6. Verification & Test Plan

- `just viewer install`, `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build` (the
  `FRONTEND_CHECK`): AC-01 to AC-03.
- `rg -n "BranchDocuments|isActivityBranch|opens\(|canOpenMember|canOpenBase" packages/devkit-viewer/frontend/src`
  prints nothing: AC-01.
- `rg -n "frontend/dist" .gitignore` prints nothing: AC-04.
- `just lint` and `just test-affected --base main`.
- Outcome baseline: the head with the change disabled is the base `2d247d824`; the measured outcome is the frontend
  test count and result before and after, plus the count of removed plumbing symbols from the `rg` above.
