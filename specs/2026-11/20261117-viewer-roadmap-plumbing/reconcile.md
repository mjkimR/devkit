---
reconcile_id: REC-viewer-roadmap-plumbing
status: resolved
targets: []
formal_docs:
  design: "none: no DESIGN document covers the viewer roadmap builder or tree normalization; the change removes frontend internals only"
  domain: "none: no domain term, entity or rule changes; roadmap members and milestones keep their meaning"
  operations: "none: no command, deployment or operating procedure changes; .gitignore drops entries for outputs no build produces"
---

# Reconciliation: `SPEC-viewer-roadmap-plumbing`

## Contract comparison

No Living Spec document changes. `CAP-VIEW-repository-viewer` §5 Source already states that the roadmap reads the
registered working tree, enumerates no other branch and applies no Planning overlay; its Members clause names direct
PROP anchors in that working tree only. The removed code (`BranchDocuments`, `isActivityBranch`, `Member.branch`,
the `branches` argument, `opens`, `canOpenBase`/`canOpenMember` and the branch badge) could only act on other-branch
documents that no data source supplies, so the capability already describes the implemented behavior.

`normalizeTree` now keeps item types as sent. The capability's API table documents the `tree` response as items with
`type`, and the Python readers (`WorkingTreeReader` and the Planning tree reader) emit only `tree` and `blob`, so the
removed `dir`/`file` mapping had no documented or produced input.

The `.gitignore` change touches no documented build output: the capability and
`docs/development/reference/viewer.md` name `src/devkit_viewer/static/` as the committed page, and no document names
`frontend/dist` or `dist-pack`.

Searched without hits outside `docs/materials/`: `buildRoadmap`, `BranchDocuments`, `isActivityBranch`,
`normalizeTree`, `dist-pack`, `frontend/dist`; no use case or UX document describes other-branch roadmap members.

## Entrypoints

No reconcile target, so `devkit spec entrypoints derive` has no document to pair; nothing is written.

## Source feedback

- `FB-viewer-roadmap-branch-plumbing`: resolved by this unit. Every item of its proposed procedure is implemented
  and verified by the frontend check (244 tests) and `just test-affected --base main` (194 passed); the disposition
  is appended to the feedback record.

## Deferred work

None.
