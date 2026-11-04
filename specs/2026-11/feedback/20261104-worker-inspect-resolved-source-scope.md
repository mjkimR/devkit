---
id: FB-worker-inspect-resolved-source-scope
title: Worker scope inference drops a source feedback file after its authorized resolution
scope: repo
kind: friction
category: tool-error
target: packages/devkit-spec/src/devkit_spec/features/worker/usecases/inputs.py
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-04
---

# [FB-worker-inspect-resolved-source-scope] Worker scope inference drops a source feedback file after its authorized resolution

## 1. Friction / Question

- **Context**: The Host inspected the completed entrypoint-generated-filter worker range. Its initial
  payload explicitly authorized the direct source feedback file. The spec names `FB-entrypoints-derive-offers-managed-paths`
  in Source feedback; the tasks do not repeat its path in a boundary.
- **Expectation**: An authorized open source feedback file remains auditable when this range resolves it through
  the completion procedure. Terminal feedback outside the starting authorization remains excluded.
- **Actual**: Default scope inference reads source status from the returned head and includes only `open` files.
  The range's authorized `resolved` edit is therefore reported outside inferred scope, despite the other checks passing.
- **Workaround**: The Host compared all 19 changed paths with the original grant and ran inspection with the complete
  explicit replacement scope, including the exact source feedback file. All checks passed without code or record edits.
- **Suggestion**: Consider the accepted input's open source feedback when auditing its completion transition, or
  require and retain explicit completion paths before the worker starts. Do not grant unrelated terminal sources
  or infer authorization from a matching target alone. The existing explicit-scope override remains sufficient recovery.

## Diagnostic Details

- **Reproduction**: In the completed worktree, run `uv run devkit spec worker inspect --format json` at
  `a07e64096f359b96245421f2f60b47877f945fb9`; compare with the same range and complete explicit `--scope` arguments.
- **Expected / Actual**: Expected source completion within its initial grant; actual default scope fail, followed
  by a fully passing explicitly scoped inspection.
- **Versions**: Accepted input `00511ae149771e6197b51ba52f706992ff272161`; returned head above;
  cumulative rules base `700c339bba8e89b4d70f63c5628d14d25bd3ffdd`.
- **Conditions**: Direct source feedback starts open, is linked in Source feedback and explicitly granted in the
  Host payload, is not repeated in task boundaries, and is resolved in the returned range.
- **Workarounds Attempted**: Full replacement scope passed; no scope expansion beyond the initial grant and no
  change to the worker inspection implementation.
- **Related Assets**: `CAP-DLV-delivery-workflows`,
  `packages/devkit-spec/src/devkit_spec/features/worker/usecases/inputs.py`, source-feedback completion guidance.

## Evidence

```text
inputs.py source-feedback inference: add source path only when returned-head status == open.
Default inspection: exit1; scope fail; ancestry/head/worktree/scope_extensions/envelopes/rules/workflow pass.
Exact missing path: specs/2026-11/20261104-namespace-roadmap/feedback/entrypoints-derive-offers-managed-paths.md.
Host inspection with original complete scope: exit0, outside_scope=[], every check pass.
```
