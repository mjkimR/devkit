# Coordination, checks and recovery

1. Use flat assignments for independent scopes and role leads when local coordination helps.
2. Narrow child authority to the intersection of parent assignment, agent contract and overlay; planners' descendants stay read-only, and verifiers' descendants write only assigned ignored outputs.
3. Before parallel writes, give each writer a separate worktree, source/base identity and exclusive absolute ownership. Create worktrees with the installed harness lifecycle `uv run devkit worktree start|status|finish` on a `dev-<slug>` branch, else by the project's documented Git procedure; without either, or without permission, serialize writers. A parent writes shared glue in a child's checkout only after that child returns.
4. Before dependent concurrent writes, resolve an unsettled shared interface in a bounded contract assignment or sequence the dependent writers.
5. Require each writer to check its changes and return actual paths and source identities; validate its diff before accepting evidence.
6. Require leads to verify their aggregate assignment. The Host alone integrates into the final target through the project's authorized route and verifies the combined result and applicable landed target.
7. Use the consuming project's relevant build, lint, type, tests, document checks and representative usage checks; record the exact checked SHA/artifact, commands, outcomes and unreached scope instead of inferring combined success from child passes.
8. Route failed combined checks to the responsible writer with reproducing evidence, apply the repair and no-progress guidance in `evidence-and-iteration.md`, and report unresolved defects explicitly.
9. On failure or interruption, stop or collect active children before releasing ownership, and return retained commits, dirty paths, active owners and next action to the Host.
10. Preserve active, dirty or unmerged worktrees until results are retained or removal has separate authority; checkpointing does not require passing QA.
11. On interruption and before pause or handoff, the Host runs `uv run devkit adaptive assignment list`, then checkpoints current context per `current-context.md` step 5.

Completion requires collected children, checked actual paths, source-specific check results and a Host checkpoint when resume facts changed. Packaging/projection checks establish no native invocation, path enforcement, performance or all-host support guarantee.

A `swarm-worker` lead records children with `uv run devkit adaptive assignment new --parent <its ID>` only when its payload supplies the ID and permission, and closes all children before returning.
A `swarm-verifier` or `swarm-planner` lead records nothing: the Host records its children from the returned partition or leaves them unrecorded.
Assignment commands accept every present worktree of the repository, however it was created.
