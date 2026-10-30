---
id: FB-sync-capability-render-stale-remedy-generic
title: The sync capability still names a plain sync as the stale local render remedy
scope: repo
kind: change-request
category: instruction-conflict
target: CAP-DIST-sync-and-transactions
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-sync-capability-render-stale-remedy-generic] The sync capability still names a plain sync as the stale local render remedy

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The personal rendering paragraph of `CAP-DIST-sync-and-transactions` describes
  `CONFIG_LOCAL_RENDER_STALE` as "(exit 1, run sync)". `SPEC-lifecycle-feedback-fixes` changed the advisory's fix,
  `CAP-DIST-context-and-playbooks` and the distribution reference to name `devkit sync --locked` first and a plain
  sync only after `RECEIPT_STALE`; this capability was outside that unit's write scope.
- **Proposed Procedure**: Change the parenthetical to "(exit 1; `devkit sync --locked`, a plain sync only when it
  reports `RECEIPT_STALE`)".
- **Expected Benefit**: The canonical sync contract gives the same remedy as the advisory, so a worker reading it does
  not run a plain sync that writes outside its scope.
- **Cost & Risk**: One phrase in one capability; no behavior change.
- **Attempted**: Found by the second code review of `SPEC-lifecycle-feedback-fixes`; waived there as out of scope.

## Evidence

```text
docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md (Personal rendering and evidence):
  "Missing or stale evidence or changed variables/presentation preferences raise CONFIG_LOCAL_RENDER_STALE (exit 1, run sync)."
local_render.py LocalRenderStaleError.fix: "Run `uv run devkit sync --locked` ... Only if it reports RECEIPT_STALE run a plain `uv run devkit sync` ..."
```
