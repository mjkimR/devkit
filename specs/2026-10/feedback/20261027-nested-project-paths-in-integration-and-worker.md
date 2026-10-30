---
id: FB-nested-project-paths-in-integration-and-worker
title: Integration readiness and worker runners assume the project is the Git top level
scope: repo
kind: suggestion
category: missing-capability
target: devkit_agt IntegrationContext; devkit-spec delivery integration readiness provider; devkit spec worker inspect
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-27
---

# [FB-nested-project-paths-in-integration-and-worker] Integration readiness and worker runners assume the project is the Git top level

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: Several delivery paths support a devkit project in a subdirectory of its Git repository
  (`native_handoff`, and after the bug-fix pass also composed plan-accept and `worker inspect` scope derivation).
  The integration readiness provider in `devkit_spec.features.delivery.usecases.integration` still treats the
  project as the Git top level: `_snapshot_root`, the materialised `Workspace`, `resolve_unit`, `_unit_advance` and
  `_check_unit_task` → `attach_check` receive project-relative unit paths and resolve them from the tree root.
  `IntegrationContext` (`devkit_agt.features.integration.models.contracts`) carries no project root or prefix, so a
  provider cannot build the repository-relative unit. `worker inspect --unit` is still read as top-level-relative,
  and its wrapped `rules` / `workflow next` runners run at the Git top level.
- **Proposed Procedure**: Carry the project's repository-relative prefix in `IntegrationContext` (built in the
  integration service), apply it throughout the readiness provider, and read `worker inspect --unit` and run the
  wrapped runners relative to the project. Add nested-project tests for integration readiness and worker runners.
- **Expected Benefit**: Plan-accept followed by integration, and worker inspection, work end to end for a project
  nested in a larger repository, consistent with the paths already fixed.
- **Cost & Risk**: Changes the provider extension contract between `devkit-agt` and `devkit-spec` (no external
  consumers yet). Every readiness path must be re-verified for the top-level case.
- **Attempted**: Not attempted; the bug-fix pass fixed only plan-accept and worker scope derivation, because the
  readiness fix needs the contract change.

## Diagnostic Details

- **Reproduction**: unknown for integration (traced, not run end to end); worker scope reproduced and fixed with a
  project at `proj/` in a throwaway repository.
- **Expected / Actual**: Expected readiness to resolve the unit under the project prefix; actual code resolves
  `docs/proposals/PROP-x` from the tree root.
- **Versions**: branch `dev-bug-polish` after commit `2f8c9217`.
- **Conditions**: `.devkit/` in a subdirectory of the Git working tree.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-DLV-delivery-workflows`, `CAP-DLV-proposal-planning`,
  `packages/devkit-spec/tests/integration/features/delivery/test_plan_accept_nested.py`.

## Evidence

```text
IntegrationContext fields: finish, task, network, result_sha (no project root or prefix).
integration.py: _check_unit_task(...) -> attach_check(base, branch, unit_rel, context.finish.source_sha)
with unit_rel project-relative; git show <tip>:<unit_rel> resolves from the tree root.
```

## Disposition

- **Disposition**: dismissed by the user's decision: devkit's root contract (`find_project_root` /
  `require_devkit_root`) makes the Git top level the devkit root and refuses a `.devkit/` below it with
  `DEVKIT_ROOT_NESTED`, so nested projects are unsupported and the partial project-prefix handling in
  `native_handoff`, composed plan-accept, scope, policy, `generated` and `worker inspect` was removed instead.
