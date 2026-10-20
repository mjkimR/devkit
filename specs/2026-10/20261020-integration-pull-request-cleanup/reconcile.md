---
reconcile_id: REC-integration-pull-request-cleanup
feature: SPEC-integration-pull-request-cleanup
status: pending
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
  - file: docs/development/reference/worktree.md
    resolution: modified
  - file: docs/decisions/2026-10/20261020-github-pull-request-repository-binding.md
    resolution: modified
---

# Reconciliation: PR integration and cleanup

`CAP-INT-mcp-services` owns route-specific approval, process-local pending/resume authority, repository binding,
checked and unchecked landing evidence, local cleanup and network bounds. Its existing integration directory
entrypoint covers the new executor. `CAP-WT-task-worktrees` owns the reusable GitHub adapter and preserves the
local-only CLI refusal; its adapter entrypoint is selected separately from integration orchestration.
`CAP-DLV-project-policy` explains PR-route remote deletion selection without treating configuration as authority.
The two quick references list the entry points and actionable advisory codes. The package README and bundled
spec-integrate procedure mirror these contracts without creating another policy source.

`ADR-github-pull-request-repository-binding` records the approved concrete correction to the accepted adapter design:
explicit repository/host syntax where gh does not accept -R, structured rules and required checks, and synchronous
head-pinned REST merging without implicit enqueue. Existing accepted ADR files are unchanged. No new architecture
layer or domain term is introduced; worktree owns the platform port and integration owns authority/execution.

## Source feedback and retained scope

`FB-pr-remote-and-squash-integration` is partially addressed by the approved no-ff PR route. Its remote authority,
source-preserving landing and cleanup portion is implemented and exercised by offline adapter/bare-repository
regressions and reviewed in the code-review rounds. Squash/rebase provenance and non-ancestor deletion remain
explicit non-goals, so the source stays promoted and continues to track that remaining scope. No required accepted
criterion is deferred. Existing planning feedback stays open; Development added concrete CLI premise observations.

## Evidence boundaries

Platform-verification material records official documentation, measured offline call durations and limits.
No live GitHub mutation or host cancellation experiment establishes server behavior. Local/provider checks can
outlast a host timeout; inspect retained process-local progress, and restart through fresh approval after process
loss. These limits are reflected in the capability, reference and confirmation rather than hidden by success text.


Entrypoint derivation produced broad cross-product candidates from task boundaries. Only the worktree adapter file
was added: the existing integration directory already owns its executor, while delivery policy changes are wording.
Test directories, package README and cross-component skill/provider candidates were rejected as unrelated ownership.
The file-level adapter entrypoint was selected explicitly instead of broadening the existing worktree file entries.
