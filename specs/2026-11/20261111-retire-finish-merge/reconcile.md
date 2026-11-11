---
reconcile_id: REC-retire-finish-merge
status: resolved
targets:
  - file: docs/decisions/2026-11/20261111-single-local-landing-route.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-local-and-pull-request-integration.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-orchestration-workers.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-worktrees-and-scope.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-package-ownership-and-release-version.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-cli-and-output.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/architecture/ARCH-04-2-delivery-policy.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/architecture/ARCH-06-runtime-view.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md
    resolution: modified
  - file: docs/development/reference/worktree.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
---

# Reconciliation: `SPEC-retire-finish-merge`

`ADR-single-local-landing-route` records the decision and supersedes in part the `finish --merge` clauses of
`ADR-local-and-pull-request-integration`, `ADR-orchestration-workers` and `ADR-worktrees-and-scope` and the
`devkit.finish_guard` entry point clause of `ADR-package-ownership-and-release-version`; each earlier ADR carries the
matching pointer line and no decision text of theirs changed.

`CAP-WT-task-worktrees` states the cleanup-only `finish`, the `WORKTREE_MERGE_RETIRED` refusal (AC-01, AC-02), the
network-free cleanup with `--local-only` accepted (AC-03) and the retired guard group (AC-05).
`CAP-DLV-workflow-envelopes` moves the integration hold to the `dev-integration` gate and the Host's
`devkit workflow envelope check` (AC-05). `CAP-INT-mcp-services`, `CAP-DLV-delivery-workflows`,
`CAP-DLV-cli-and-output`, `CAP-DLV-project-policy`, `CAP-DIST-sync-and-transactions`, the three architecture views, the
two delivery use cases and the two development references name `devkit integration integrate --route local` as the
landing route (AC-04, AC-06). No glossary term was introduced or renamed. No work was deferred and no source feedback
was assigned.

The spec bundle text (`references/branches.md`, `references/backlog.md.jinja`, `references/worktree.md.jinja`,
`references/worker-records.md`) is agent guidance, not Living Spec; it is covered by Task 2.4 and its sync output.

Entrypoints are unchanged: every derived candidate joins the whole unit boundary (spec bundle references, tests and
the worktree, integration and workflow sources) with documents this unit changed in content but whose existing
doorways (`devkit_agt.features.worktree.cli`, the integration service) still hold, so no pair was applied.
