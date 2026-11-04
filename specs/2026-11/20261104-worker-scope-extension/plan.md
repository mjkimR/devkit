---
id: PLAN-worker-scope-extension
spec: SPEC-worker-scope-extension
---

# Technical Plan: `SPEC-worker-scope-extension`

## 1. Constitution & Invariant Review

`ADR-recorded-adjacent-path-extensions-for-development-workers` partially supersedes unlisted-path rejection in
`ADR-orchestration-workers`; remaining permissions, Git, cumulative range and sync-output rules hold. Existing
workflow and worker features own all behavior under `ARCH-05-2-components`; no new edge is introduced.

## 2. Architecture Overview & Impact

Workflow owns the optional `ScopeExtension` value, strict parser, worker CLI flag and serialization. Entrypoint
boundary parsing adds annotations and task requirements without changing values. Worker inspection compares those
annotations with committed records across turns, independently of explicit scope selection. Shared worker,
reviewer, tasks and delegation assets restate admission and final validation for local/cloud execution.

## 3. Component & Interface Design

`scope_extensions: [{path: str, task: int, reason: str, requirements: [AC-NN]}]` is optional and worker-only.
`--scope-extensions-file` accepts YAML file/stdin using existing item-file error codes. Inspection adds a list and
check without changing `scope`, `outside_scope` or override semantics. A small worker service checks structural
agreement and recognizable protected paths. Review retains semantic ownership/custom-deny/test-strength judgment.
Annotation reasons precede final record creation; inspection is final evidence and remains optional.

## 4. Storage & State Management

The sole final/emergency worker envelope persists typed records. Inspection reads committed unit records in worker
sequence order; latest metadata wins per exact path. Only retained annotations contribute extension boundaries.
No journal/config/registry is added; ordinary task document changes remain review inputs.

## 5. Error Handling & Edge Cases

Reject empty/malformed list items, bool/nonpositive task numbers, duplicate paths, absolute/parent/glob/noncanonical
paths and invalid requirements. Reject other-kind fields even when empty. Invalid annotation syntax produces a
not-run input cause; structural disagreement/protected trees produce extension failure. Sync outputs remain a
separate recorded admission class. Explicit overrides never gain extension paths implicitly.

## 6. Verification & Test Plan

Task-owned parser/model/CLI/inspect/content tests cover AC-01 through AC-05, compatibility, multi-turn evidence and
full-replacement scope flags. Run relevant Ruff/Pyright, `just test-affected` with its full fallback, CI rules and
`devkit sync --check`; compare before/after probe at the unchanged worktree. One independent medium Code Reviewer
and a cross-package Reconcile Reviewer inspect exact committed snapshots. Records-only commits reuse passing
code tests; repeat checks for actual changes or unresolved concerns. Final cumulative CI rules run before return.
