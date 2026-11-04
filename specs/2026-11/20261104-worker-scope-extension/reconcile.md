---
reconcile_id: REC-worker-scope-extension
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-recorded-adjacent-path-extensions-for-development-workers.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-orchestration-workers.md
    resolution: waived
    rationale: The accepted handoff already committed its partial-supersession annotation; the Development diff changes neither its remaining decisions nor that approved trace.
  - file: docs/materials/2026-11/20261104-worker-scope-extension/implementation-evidence.md
    resolution: modified
---

# Reconciliation: `SPEC-worker-scope-extension`

## Contract reflection

| Target | Reflected implementation and verification |
| --- | --- |
| `CAP-DLV-delivery-workflows` | Tier A/B/C admission, reviewer judgment, pre-final annotations, final Host evidence, cumulative records/latest sequence, optional structural inspect, complete explicit overrides and independent sync admission. Worker inspect/content tests cover AC-02 through AC-05. |
| `CAP-DLV-workflow-envelopes` | Optional worker-only typed list, strict values and CLI file/stdin authoring; old records remain valid. Workflow integration tests cover AC-01. |
| `ADR-recorded-adjacent-path-extensions-for-development-workers` | Confirmation now names the exact shipped tests; the accepted decision and partial supersession are unchanged. |
| `ADR-orchestration-workers` | Its approved partial-supersession annotation is already present at the Development input. No additional edit is required; Git, permission, range and sync decisions remain in force. |
| Preserved implementation evidence | Before/after API availability and legacy-note reproduction, same-feature implementation choices and emulated boundary measures are recorded without performance or live Hub claims. |

The independent medium Code Reviewer found one P2 manifest omission. `review-01.yaml` records it and
`reverify-01.yaml` closes it after package.json protection, the isolated failure-code regression (21 cases) and
`just test-affected` (2314 passed, partial selector with full fallback retained). Both package lint and type checks
passed; 22 cumulative CI rules and selected-bundle sync checks passed. Independent medium Reconcile Reviewer verification passed without findings at `f65ea22f`;
`reconcile-check-01.yaml` records coverage, feedback verification and unchanged snapshots. No required work is deferred.

## Entrypoints

Existing doorway entries already name the workflow envelope CLI/authoring operations and worker inspection CLI.
Retain them. Reject added candidates that are helper/model/test files or unchanged broad workflow directories;
no new entrypoint or feature edge is needed.

## Source feedback

`FB-entrypoints-derive-boundary-annotations` is directly resolved: balanced legacy parenthetical notes with nested
calls, backticks and commas no longer emit prose as paths. The parser regression retains unquoted literal paths,
and the independent Code Review covered this compatibility change. Its source Disposition names this spec and
verification. This repairs the existing note-stripping behavior; no new entrypoint filtering contract is introduced.

## Retained limits

Semantic adjacency, payload denies, custom protected paths and test weakening remain reviewer judgments. Inspection
is informational and optional in local/cloud execution; no live Hub or native Codex confinement guarantee is made.
The current run used strict initial Host grants and no Tier B extensions. `.devkit/installation.json` is the sole
tracked sync output and is named on Task 3 as `(sync output)`. Scratch/probe paths remain ignored inside the worktree.
