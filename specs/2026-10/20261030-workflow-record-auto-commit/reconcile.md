---
reconcile_id: REC-workflow-record-auto-commit
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-cli-and-output.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-explicit-envelope-commits.md
    resolution: modified
  - file: docs/materials/2026-10/20261030-workflow-record-auto-commit/development-evidence.md
    resolution: modified
---

# Reconcile: `SPEC-workflow-record-auto-commit`

## Contract comparison

- `CAP-DLV-workflow-envelopes` retains explicit single-record eligibility, tracked anchor identity, exact dirty/index scope, preconditions and post-hook verification including symbolic branch identity, same-file retry/idempotence and uncertainty preservation. Runtime and policy tests verify AC-01 through AC-04.
- `CAP-DLV-cli-and-output` retains the command, success sentinel/JSON fields and all four exit-2 codes with recovery targets. CLI and documented-code tests verify the boundary.
- `CAP-DLV-delivery-workflows` and `UC-drive-development-to-integration` retain optional record-only review/reverify/final-report/no-finding-feedback commits, combined manual transactions and preparation ordering. Source guidance and workflow readiness tests verify AC-05. The unchanged integration stale-source regression confirms older preparation is refused after HEAD changes.
- `ADR-explicit-envelope-commits` repairs carried proposal references to the handed-off spec; its accepted decision is unchanged. `MAT-workflow-record-commit-development` records the same-head baseline and verification without speed/cost claims.

No architecture contract changed: the CLI calls a typed BaseUseCase, workflow-owned policy/repository layers reuse foundation Git without an agt-to-spec dependency. Gate/worktree/integration engines are unchanged. No new glossary concept or graphical screen is introduced. No named open source feedback or required scope is deferred.

## Review and verification

Medium independent code review at 8ef6543b reported three findings. The author fixed symbolic HEAD capture, eligible final-report example and workspace-relative targets; focused runtime/guidance 45 passed and affected tests 2090 passed. `reverify-01.yaml` closes every finding against 085f5e5f. Its actual explicit command committed only that envelope at 97aa4c2e while normal repository hooks rewrote metadata. Independent medium reconcile review verified all six targets at 31a03130 with no findings. Before/after snapshots both equal 11957fb158bd3547153dd24ea7cd7fd4d13e4971 and HEAD/worktree were unchanged. The final affected selection on that content passed 2091 tests across 116 selected paths.

The initial sync check passed. `.devkit/installation.json` is the only tracked sync output and is listed in Task 2 with `(sync output)`; managed/projected files were generated, never hand-edited.

## Entrypoints

Select workflow CLI and the explicit commit use case as code doorways for envelope/CLI contracts. Retain workflow source definitions for delivery guidance. Broad task boundaries, helper/model/test directories, unrelated integration engines and evidence-only materials are not new entrypoints.

## Integration verification

The Host incorporated main at eb4d4f37 in merge 082978a4. Conflicts were limited to the delivery capability summary,
use-case entrypoints and example scenario numbering. Both the git-operator lifecycle behavior and explicit envelope
commit behavior are retained; envelope scenarios were renumbered 24 through 28 after the incoming 22 and 23.
No runtime code or accepted decision changed during resolution. The existing independent code/reconcile evidence
remains valid for unchanged implementation. The Host rechecked all six reflection targets against the merged tree.

The base-incorporation affected selection passed 1491 tests; the prior 2091-test source selection remains valid for
unchanged implementation. The cumulative committed rules check against current main passed with zero violations.
Sync is clean and the main-relative diff has no whitespace errors. The only tracked sync output remains the receipt.

The merge exposed a carried reference to the consumed resource-manager proposal. The Host changed it to the
retained SPEC ID in 928fdde5 and reran committed cumulative rules successfully. The earlier
reconcile-check-02 prematurely reported that CI check as passed; reconcile-check-03 corrects and supersedes its
verification claim with the actual successful result. Both records remain immutable history.
