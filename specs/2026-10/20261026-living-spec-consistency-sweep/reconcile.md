---
reconcile_id: REC-living-spec-consistency-sweep
status: pending
targets:
  - file: docs/architecture/ARCH-01-introduction-and-goals.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
  - file: docs/capabilities/generated/CAP-GEN-tracked-artifacts.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/host/CAP-HOST-lifecycle-observation.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/mcp/CAP-MCP-runtime-registration.md
    resolution: modified
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
  - file: docs/glossary.md
    resolution: modified
  - file: docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md
    resolution: modified
---

# Reconcile: `SPEC-living-spec-consistency-sweep`

Every target was edited in this Unit to match shipped behavior; the per-item mapping is `plan.md` §2 and the
extensions are `spec.md` §5. No behavior changed except help and docstring text (`devkit worktree`,
`devkit spec list`, the distribution `-w/--workspace-root` help) and the `spec` bundle's classification guidance.

## Source feedback

- `FB-workspace-root-help-resolution-order`: resolved (Disposition added); the distribution `WORKSPACE` option uses the
  shared `WORKSPACE_HELP`, verified with `devkit sync --help` and `devkit playbook search --help`.
- `FB-classification-maintenance-playbook-case`: resolved (Disposition added); `references/classification.md` §1
  names the review-refactor work item case, synchronized with `devkit sync`.

## Deferred work

Observations outside the 22 findings, recorded as feedback in this Unit:

- `FB-plain-handoff-skips-proposal-handoff-policy`: design question whether the plain `devkit spec proposal handoff`
  must read `proposal-handoff`.
- `FB-integration-mcp-glossary-and-actor-row`: the glossary **Integration MCP** entry and the `ARCH-04-1-ecosystem-boundaries` actor row.
- `FB-worktree-module-layout-stale`: `CAP-WT-task-worktrees` §7 module list.
- `FB-sync-config-template-example-stale`: the commented template example in `CAP-DIST-sync-and-transactions`.
- `FB-spec-readme-and-mcp-guide-native-handoff`: the devkit-spec README and `guides/install/mcp.md`, outside the
  write scope.
- `FB-handoff-error-modes-documented-differently`: the documented modes of `SPEC_HANDOFF_NOT_READY` and
  `SPEC_HANDOFF_REPLY_INVALID`.

## Entrypoints

`devkit spec entrypoints derive` joined the `_Boundary` paths with every target into 83 candidates; none was applied,
because every target was edited for wording only and the documents whose behavior gained text already own their
command paths, except `CAP-GEN-tracked-artifacts`, whose `generated/cli.py` is not among the derived candidates.
