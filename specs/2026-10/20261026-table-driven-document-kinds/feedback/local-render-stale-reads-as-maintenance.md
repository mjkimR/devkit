---
id: FB-local-render-stale-reads-as-maintenance
title: Stale local render evidence tells the agent to stop instead of syncing
scope: repo
kind: change-request
category: tool-error
target: packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/local_render.py
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-local-render-stale-reads-as-maintenance] Stale local render evidence tells the agent to stop instead of syncing

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: In a freshly created task worktree, the first `uv run devkit get-context spec` failed with
  `CONFIG_LOCAL_RENDER_STALE`, rendered as `mode: MAINTENANCE` with the action "A codebase defect or tool failure
  occurred. Report it and stop; repairing the code/tool is a separate task", while its `fix` says to run
  `devkit sync`. `LocalRenderStaleError` sets `input_error = False` and no actor or mode, so it inherits the
  maintenance default.
- **Proposed Procedure**: Give `LocalRenderStaleError` (and likely `LocalChangedError`) the advisory fields of a
  routine, agent-fixable precondition, so the directive tells the agent to run `devkit sync` and retry, matching
  `CAP-DIST-context-and-playbooks` ("Both direct the caller to sync").
- **Expected Benefit**: A worker following the directive literally would stop its whole run at startup; with the fix
  it syncs and continues, as the documented contract intends.
- **Cost & Risk**: One error class's advisory fields; tests asserting its mode or action need updating.
- **Attempted**: Ran `devkit sync` in the worktree (it updated only ignored managed and transient files), after
  which `get-context` succeeded.

## Diagnostic Details

- **Reproduction**: create a task worktree, then run `uv run devkit get-context spec` before any `devkit sync`.
- **Expected / Actual**: Expected a directive to sync and retry; actual is a MAINTENANCE "report and stop" directive.
- **Versions**: base `6a19ff5f`.
- **Conditions**: personal render evidence (`.devkit/transient/local-render.json`) missing or older than the receipt.
- **Workarounds Attempted**: `devkit sync`, then retry: succeeded.
- **Related Assets**: `CAP-DIST-context-and-playbooks` section 3 and its error table; `docs/development/reference/distribution.md`.

## Evidence

```text
"code": "CONFIG_LOCAL_RENDER_STALE", "mode": "MAINTENANCE",
"action": "MAINTENANCE — A codebase defect or tool failure occurred. Report it and stop; ...",
"fix": "Run `devkit sync` in this workspace to refresh personal rendering evidence"
```
