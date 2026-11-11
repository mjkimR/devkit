---
reconcile_id: REC-single-sync-readiness-gate
status: pending
targets:
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/usecases/delivery/UC-import-third-party-agent-assets.md
    resolution: modified
---

# Reconcile: `SPEC-single-sync-readiness-gate`

- `CAP-DIST-sync-and-transactions`: new "Readiness Gate" subsection after "Locked Synchronization" states the
  `sync --check` exit-`0` criterion, that `devkit status` is a receipt-based diagnostic report that misses
  desired-state changes, that planned optional MCP registration writes keep the check at exit `1`, and the clone
  restore order (AC-01).
- `docs/development/reference/distribution.md`: the `devkit status` section closes with the gate and report
  sentence (AC-02).
- `UC-import-third-party-agent-assets`: Scenario 7's Then clause ends with `uv run devkit sync --check` exits `0`
  (AC-03).
- No other Living Spec document is affected: `ADR-mcp-runtime-and-shared-artifacts` already says general status emits
  no `MCP_REGISTRATION_PENDING`, which the help text now matches; no architecture, glossary or UX document changes.
  Guides and bundle text are quick references outside `docs/`, changed in the build commit.
- Entrypoints: none applied. `devkit spec entrypoints derive` offered the guides, bundle text, the `status` help
  module and its test for both documents; all were rejected as not doorways (guides and bundle text are quick
  references, the help string is a docstring of a CLI module the capability reaches through `usecases/sync.py`, the
  use case touched one sentence).
- Deferred work: none; the proposal defers no concrete work. Source feedback: none carried.
