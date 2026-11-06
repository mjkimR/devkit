---
reconcile_id: REC-adaptive-swarm-development
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    resolution: modified
  - file: docs/usecases/delivery/UC-advance-an-idea.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-adaptive-development-and-research.md
    resolution: modified
  - file: docs/decisions/2026-11/20261106-skill-local-swarm-roles.md
    resolution: modified
  - file: docs/decisions/2026-11/20261106-worktree-isolated-parallel-workers.md
    resolution: modified
---

# Reconciliation

All AC-01 through AC-10 are reflected in the capability and use case: presets/reuse, caller authority, overlays, bounded teams, isolation, aggregate checks and failure checkpoints. Architecture changes only catalog content ownership. Promoted ADRs point to actual restating rules and retain unverified runtime limits; the earlier ADR pointer preserves its other decisions. No new decision, feature edge or runtime/schema change occurred.

Verification evidence is in materials/verification.md. Native named invocation, native cancellation/confinement, other-host execution and performance remain unverified limits, not deferred requirements. No source feedback was carried from Planning. Executor scheduling friction is recorded as `FB-isolated-execution-group-identity`; synchronous native selected E2E passed under the Host exception, while the unknown executor checkout is preserved.

Entrypoint derivation ran: retained the existing entry skill and selected swarm-worker as the reusable-agent doorway and orchestration reference as the team-flow doorway. Rejected broad source directories and test paths because they are not entry doorways. Fixture aggregate repair passed at 594bae1fcaf0125f37170f0ff5143f8dfd056433 while the interrupted leaf checkpoint stayed dirty and preserved.
