---
id: FB-reconcile-parser-private-reuse
title: Committed-record consumers reuse a private reconciliation parser
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/entrypoints/bundle.py
skill: spec-feedback
agent: codex
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-reconcile-parser-private-reuse] Committed-record consumers reuse a private reconciliation parser

## 2. Suggestion / Change Request

- **Current Procedure**: the worker inspection helper reads committed reconciliation text with Git and imports
  `_targets` from the entrypoint bundle module to preserve the existing parser behavior. The public `load_bundle`
  entry point reads working-tree files, while `parse_boundaries` already accepts text publicly.
- **Proposed Procedure**: expose the existing reconciliation target parser as a public text parser when that
  module is next changed; let both disk and committed-text consumers call it.
- **Expected Benefit**: consumers can reuse the supported parsing contract without a private import or temporary
  filesystem snapshot.
- **Cost & Risk**: a small API ownership change and updates to its callers/tests; grammar must remain unchanged.
- **Attempted**: private reuse is implemented and covered by worker inspection tests; no entrypoint API change
  was made because that source path is outside this worker's write scope.

## Diagnostic Details

- **Reproduction**: inspect `load_bundle`, `parse_boundaries` and `_targets` in the target module, then the imports
  in `packages/devkit-spec/src/devkit_spec/worker/inputs.py`.
- **Expected / Actual**: expected reusable text parsing for committed records; actual public bundle loading takes
  a root path while the reusable target parser is private.
- **Versions**: devkit-spec 0.1.0.
- **Conditions**: read-only committed-record derivation in `SPEC-worker-range-validation`; no snapshot writes.
- **Workarounds Attempted**: reuse `_targets` directly; focused and affected tests pass.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/entrypoints/bundle.py`, worker input derivation.

## Evidence

```text
entrypoints/bundle.py: parse_boundaries(text), load_bundle(root, directory), _targets(text, relative)
worker/inputs.py: from devkit_spec.entrypoints.bundle import _targets, parse_boundaries
```

## Disposition

Directly resolved by `SPEC-feedback-planning-parser`. Public parse_targets(text, relative) replaces the private parser import in committed inspection and is shared with disk bundle loading; parser behavior is unchanged.

Independent medium code review passed all four acceptance criteria without findings. The affected suite passed
1,113 tests, including parser default/order/error cases and existing consumer checks; lint, type checks and
cumulative governance checks passed. This disposition records verified branch work, not integration.
