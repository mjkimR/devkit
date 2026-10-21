---
id: FB-scope-observation-candidates
title: Scope overlap candidates include observation-only feedback paths
scope: repo
kind: friction
category: spec-ambiguity
target: devkit spec scope update
skill: spec-sync
agent: codex
origin: agent
severity: workaround
recurring: false
status: open
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
