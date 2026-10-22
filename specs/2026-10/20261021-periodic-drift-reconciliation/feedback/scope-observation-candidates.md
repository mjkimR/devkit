---
id: FB-scope-observation-candidates
title: Scope overlap candidates include observation-only feedback paths
scope: repo
kind: friction
category: spec-ambiguity
target: devkit spec scope update
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-21
---

# [FB-scope-observation-candidates] Scope overlap candidates include observation-only feedback paths

## 1. Friction / Question

- **Context**: Development narrowed task boundaries to catalog, one installation guide, the unit and one smoke assertion.
- **Expectation**: Observation-only imported feedback would not imply ownership of its prospective fixes.
- **Actual**: Scope update still reported candidate overlaps on spec-delegate and spec-orchestrate, both explicitly denied by the handoff.
- **Workaround**: Kept the explicit write scope authoritative and reported the advisory overlap to the Host; no denied path was edited.
- **Suggestion**: Distinguish observation-derived candidates from authorized task boundaries clearly in overlap output.

## Diagnostic Details

- **Reproduction**: Run devkit spec scope update after narrowing tasks.md; two successive updates retained both candidate paths.
- **Expected / Actual**: Declared implementation scope versus broader candidate overlap advisory.
- **Versions**: Worktree base a7958abb8eb28fd3835a5ba72042e23a9099f207.
- **Conditions**: Imported open feedback naming delegation assets; a concurrent unit owns those assets.
- **Workarounds Attempted**: Explicit denied paths respected; Host notified; no engine change attempted.
- **Related Assets**: scope registry; tasks.md; FB-nested-role-skill-read-scope.

## Evidence

`SCOPE_ACK status=applied revision=2` and revision 3 reported spec-delegate and spec-orchestrate as
`source=candidate`, overlapping SPEC-worker-shared-state-mcp. The authored task boundaries contain neither path.

- **Disposition**: `SPEC-scope-boundary-candidates`: the candidate overlaps came from the `entrypoints` of the broad reconcile target `CAP-DLV-delivery-workflows` (which then listed the `spec-delegate/` and `spec-orchestrate/` skill directories), not from imported feedback. Once a spec bundle's `tasks.md` declares a `_Boundary` code path, its scope set now holds declared and observed code only and no target entrypoint candidate; proposals and bundles without declared code keep the candidates (`CAP-COLL-work-scope-registry` §4.1, §4.2). Verified by `packages/devkit-spec/tests/integration/features/scope/test_inputs.py` (`test_declared_code_replaces_target_entrypoint_candidates`, `test_a_candidate_only_path_no_longer_overlaps`, `test_candidates_stay_before_code_is_declared`) and `test_cli.py` (`test_declared_code_replaces_candidates_and_observed_paths_still_overlap`: a registered update records no `source=candidate` path), with `just test-affected` passing and a code-reviewer PASS.
