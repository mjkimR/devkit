# Optional teams, checks and recovery

1. Choose direct work for a bounded task, flat agents for separable scopes, or Host → role lead → child when local coordination helps and the host supports nesting; allow at most two child levels.
2. Allocate capacity across the Host's whole session, including waiting leads; a lead receives a remaining allowance and cannot infer a private pool or grant extra capacity.
3. If nesting is unsupported or capacity is unknown/exhausted, flatten or serialize the assignment and retain its result/check contract; change no host setting.
4. Narrow child authority to the intersection of parent assignment, agent contract and overlay; planners' descendants remain read-only, and verifiers' descendants write only assigned ignored outputs.
5. Before parallel writes, give each writer a separate worktree, source/base identity and exclusive absolute ownership; use the project's documented worktree procedure and permitted Git actions without assuming a harness is installed.
6. Before dependent concurrent writes, resolve an unsettled shared interface in a bounded contract assignment or sequence the dependent writers.
7. If coordination costs more than its expected benefit, keep the task direct.
8. If worktrees or permission are unavailable, serialize writers; a parent waits until a child returns before writing shared glue in that child's checkout.
9. Require each writer to check its changes and return actual paths and source identities; validate its diff before accepting evidence.
10. Require leads to verify their aggregate assignment; the Host alone integrates into the final target through the project's authorized route and verifies the combined result and applicable landed target.
11. Use the consuming project's relevant build, lint, type, tests, document checks and representative usage checks; record exact checked SHA/artifact, commands, outcomes and unreached scope rather than inferring combined success from child passes.
12. Route failed combined checks to the responsible writer with reproducing evidence; apply the repair and no-progress guidance in `evidence-and-iteration.md` and report unresolved defects explicitly.
13. On failure or interruption, stop or collect active children before releasing ownership; return retained commits, dirty paths, active owners and next action to the Host.
14. Preserve active, dirty or unmerged worktrees until results are retained or removal has separate authority; checkpointing does not require passing QA.
15. Only the Host updates `.devkit/adaptive-dev.md`; record useful failed checks, unmerged/dirty results, source identity, ownership and recovery steps before pause or handoff.

Completion requires collected children, checked actual paths, source-specific check results and a Host checkpoint when resume facts changed. Packaging/projection checks establish no native invocation, path enforcement, performance or all-host support guarantee.
