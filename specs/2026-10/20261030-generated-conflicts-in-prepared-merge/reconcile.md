---
reconcile_id: REC-generated-conflicts-in-prepared-merge
spec: SPEC-generated-conflicts-in-prepared-merge
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/generated/CAP-GEN-tracked-artifacts.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
  - file: docs/development/reference/worktree.md
    resolution: modified
  - file: docs/development/reference/generated.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-generated-conflicts-in-prepared-merge.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-moved-target-merge.md
    resolution: modified
---

# Reconcile: `SPEC-generated-conflicts-in-prepared-merge`

## Contract comparison

- `CAP-INT-mcp-services` states the settled build: every conflict owned by an enabled artifact of the registry
  committed at the build target, no artifact to regenerate reading another conflict, each path kept at the seed side
  (removed where that side deleted it), the checks on that result, one tree for prepare and integrate, the
  `generated` JSON field, the `seeded=` sentinel field, the printed prepare notices and the
  `INTEGRATION_GENERATED_SEEDED` row; other conflicts refuse with one detail per path; composed acceptance and the
  pull-request route settle nothing (AC-01 to AC-08). Code: `integration/services/seeding.py`,
  `integration/usecases/service.py` (`_prepare`, `_land`, `_compose_execute`), `integration/models/contracts.py`,
  `integration/cli.py`.
- `CAP-WT-task-worktrees` states the `settle` parameter of `build_result` and the `ConflictSettler` contract
  (AC-03, AC-08). Code: `worktree/models/merging.py`, `worktree/services/merging.py`.
- `CAP-GEN-tracked-artifacts` §6 adds local integration as a built-in integration point (AC-01, AC-07). Code:
  `generated/repositories/registry.py` (`load_registry_at`), `generated/services/conflicts.py` (`classify`, shared
  with `resolve`, whose behavior is unchanged).
- `CAP-HARN-agent-guidance` and `UC-drive-development-to-integration` (1b, 7i, new 7j, Scenarios 31 and 32) state the
  disclosure handling and the batch completion regeneration (AC-09), matching the `spec-integrate` and
  `spec-orchestrate` sources.
- The reference documents name the new fields, parameters, functions and code.
- `ADR-generated-conflicts-in-prepared-merge` records the changed decision and supersedes `ADR-moved-target-merge` in
  part; the latter carries the "Superseded in part by" line without a status change.

## No impact

- `CAP-DLV-proposal-planning` and `CAP-DLV-delivery-workflows`: composed acceptance keeps refusing every conflict with
  `WORKTREE_MERGE_CONFLICT`, as they state; the delivery provider is unchanged.
- `docs/development/workflow.md` and `docs/development/ci-cd.md` name the batch test run without its preceding
  `devkit generated check`; both are outside this unit's write scope and stay accurate as summaries of
  `ADR-post-batch-test-run`. Recorded as feedback `FB-workflow-batch-run-omits-generated-check`.
- `ARCH-05-2-components`: the feature graph lives in `.devkit/architecture.toml`, which now declares
  `integration -> generated` (enforced by `RULE-architecture`), and `ADR-generated-conflicts-in-prepared-merge`
  records the edge; the architecture prose lists no per-feature edges that this change contradicts.

## Deferred work and source feedback

No deferred work. The unit has no source feedback.
