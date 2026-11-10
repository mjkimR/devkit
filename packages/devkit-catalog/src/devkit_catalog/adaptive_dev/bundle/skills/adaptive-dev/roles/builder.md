# Builder

Use with `swarm-worker` or a compatible caller-owned execution contract.

1. Read the assignment's goal, absolute paths, source/base identity, permitted actions, checks and stop condition.
2. Implement and verify the assigned behavior in the exclusively owned worktree and paths.
3. Check implementation against the agreed interface and failure handling; report an unresolved mismatch instead of changing another owner's contract.
4. Treat the assigned governing documents as constraints; report a mismatch with one instead of diverging from it.
5. Keep the execution contract and caller's workflow authoritative; this overlay grants no added tool, Git or write permission.
6. Return status, source/base and final SHA when committed, actual changed paths, commands/outcomes, defects and unverified areas; report unavailable capabilities and preserve partial results.
