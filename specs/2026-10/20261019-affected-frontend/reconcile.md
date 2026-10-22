---
reconcile_id: REC-affected-frontend
status: resolved
targets:
  - file: docs/development/ci-cd.md
    resolution: modified
---

# Reconciliation

`ci-cd.md` §2 states the new selection rule (frontend paths select no pytest test; the rebuilt page under
`src/devkit_viewer/static/` stays package source) and the `[FRONTEND_CHECK: ...]` line with its exact command, the
checks of the CI viewer job, in the result bullet. `AGENTS.md` Verification, an agent quick reference outside the
Living Spec, names the line in step.

No capability, story, architecture document or ADR describes `just test-affected` or the viewer's development
commands beyond `docs/development/`, so no other target exists. No deferred work remains.
