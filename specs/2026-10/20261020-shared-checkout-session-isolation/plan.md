---
id: PLAN-shared-checkout-session-isolation
spec: SPEC-shared-checkout-session-isolation
---

# Technical Plan: Shared checkout session guidance

## 1. Constitution & Invariant Review

None. Preserve `CAP-DLV-project-policy` worktree levels and worker isolation and `CAP-WT-task-worktrees`
command behavior. The four target paths and surrounding interfaces match the accepted handoff premises.
No dependency, runtime change or new policy requires an ADR.

## 2. Components

Add concise branch-sharing guidance beside the session branch bullet in git-policy.md and `--no-worktree`
in branches.md section 2. Reflect the same responsibility boundary in project-policy section 3 item 6 and
worktrees section 2a. Use Host for the local orchestration coordinator. A separate worktree remains optional
for a direct session; local-orchestrated workers continue to require worktrees.

## 3. Verification

Self-review all four additions against AC-01 through AC-03 and the unchanged surrounding policies.
Run targeted rules, `just lint-check spec`, `just check spec`, `just test-affected --base main`, and
`devkit rules check --ci --base main`. No new test or build artifact is needed for Markdown-only changes.
The Host synchronizes installed bundle projections at integration; this worker does not edit them.
