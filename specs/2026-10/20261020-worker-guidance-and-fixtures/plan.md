---
id: PLAN-worker-guidance-and-fixtures
spec: SPEC-worker-guidance-and-fixtures
---

# Technical Plan: `SPEC-worker-guidance-and-fixtures`

## Constitution and invariant review

No conflicts. Preserve strict worker boundaries, pending-question records, and integration approval authority.
`CAP-HARN-agent-guidance` and `CAP-DLV-workflow-envelopes` describe the relevant contracts.

## Components and choices

Clarify unsolicited decisions in worker-records, official reads and link repair in the delegation payload, and
Host sync in spec-integrate. Keep each instruction at its point of use instead of duplicating role contracts.
A scope-suite fixture sets GIT_CEILING_DIRECTORIES above each test root, including resolved paths and existing
ceilings; monkeypatch restores it after each test. Actual test repositories stay below the ceiling.

## Verification

Reproduce the three reported scope failures with basetemp under .pytest_cache before the fix. Run the scope suite
there after the fix; existing locate tests cover plain directories, actual repositories and linked worktrees.
Run just lint-check spec, just check spec, just test-affected --base main and cumulative rules. Independent medium
code review and reconciliation review verify guidance and source-feedback resolutions.
