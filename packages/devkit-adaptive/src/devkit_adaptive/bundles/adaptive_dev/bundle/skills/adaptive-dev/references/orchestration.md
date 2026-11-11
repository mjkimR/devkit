# Optional teams, checks and recovery

1. Choose direct work for a bounded task or when coordination costs more than it gains, flat agents for separable scopes, or Host → role lead → child when local coordination helps and the host supports nesting; allow at most two child levels.
2. Allocate capacity across the Host's whole session, including waiting leads; a lead receives a remaining allowance and cannot infer a private pool or grant extra capacity.
3. If nesting is unsupported or capacity is unknown or exhausted, flatten or serialize the assignment, keep its result/check contract and change no host setting.
4. Narrow child authority to the intersection of parent assignment, agent contract and overlay; planners' descendants stay read-only, and verifiers' descendants write only assigned ignored outputs.
5. Before parallel writes, give each writer a separate worktree, source/base identity and exclusive absolute ownership. Create worktrees with the installed harness lifecycle `uv run devkit worktree start|status|finish` on a `dev-<slug>` branch, else by the project's documented Git procedure; without either, or without permission, serialize writers. A parent writes shared glue in a child's checkout only after that child returns.
6. Before dependent concurrent writes, resolve an unsettled shared interface in a bounded contract assignment or sequence the dependent writers.
7. Require each writer to check its changes and return actual paths and source identities; validate its diff before accepting evidence.
8. Require leads to verify their aggregate assignment. The Host alone integrates into the final target through the project's authorized route and verifies the combined result and applicable landed target.
9. Use the consuming project's relevant build, lint, type, tests, document checks and representative usage checks; record the exact checked SHA/artifact, commands, outcomes and unreached scope instead of inferring combined success from child passes.
10. Route failed combined checks to the responsible writer with reproducing evidence, apply the repair and no-progress guidance in `evidence-and-iteration.md`, and report unresolved defects explicitly.
11. On failure or interruption, stop or collect active children before releasing ownership, and return retained commits, dirty paths, active owners and next action to the Host.
12. Preserve active, dirty or unmerged worktrees until results are retained or removal has separate authority; checkpointing does not require passing QA.
13. On interruption and before pause or handoff, the Host runs `uv run devkit adaptive assignment list`, then checkpoints current context per `current-context.md` step 5.

Completion requires collected children, checked actual paths, source-specific check results and a Host checkpoint when resume facts changed. Packaging/projection checks establish no native invocation, path enforcement, performance or all-host support guarantee.

A `swarm-worker` lead records children with `uv run devkit adaptive assignment new --parent <its ID>` only when its payload supplies the ID and permission, and closes all children before returning.
A `swarm-verifier` or `swarm-planner` lead records nothing: the Host records its children from the returned partition or leaves them unrecorded.
Assignment commands accept every present worktree of the repository, however it was created.
