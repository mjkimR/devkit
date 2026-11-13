# Delegation

1. Work directly when a separate context adds no useful evidence; no action requires every role or a fixed team sequence.
2. Pick by need and keep each agent's contract: `product-clarifier`, `product-researcher` or `usage-reviewer` for product support, which never commits; `swarm-planner` for read-only partitioning, `swarm-worker` for bounded implementation or document writing with `roles/documenter.md`, `swarm-verifier` for source-specific checks with assigned ignored probe/test outputs. Compatible external callers can reuse the swarm agents under their own workflow.
3. Invoke a registered agent through the host's registered-role mechanism so its execution settings apply; if unavailable, report the gap and work directly or emulate it with an explicitly labelled generic role file.
4. Resolve `roles/<role>.md` from the directory of the invoked `SKILL.md`, never the cwd or a reference directory; if that location is unavailable, locate and verify the invoked skill first. Verify the role exists, pass its absolute installed path and read only that overlay.
5. Accept an external caller's verified absolute role path only when its permissions are compatible with the agent, project and assignment; reject incompatible requirements explicitly.
6. Supply one goal, source/base identity, absolute read/write ownership including the role file, governing documents by ID or absolute path or `none`, permitted actions and Git operations, checks, stop condition and expected return fields.
7. Partition by independently checkable deliverables and dependency edges, not file count or activity labels; give each assignment one owner, its dependency or `none`, completion evidence and integration handoff.
8. For an assignment that depends on a shared interface, name the interface owner, agreed version and source or artifact identity; if the dependent worktree lacks that version, pass the contract as explicit input or defer the assignment. If the interface changes, reassess dependents before accepting their results.
9. On an emulated host, compare actual source/index/HEAD before and after and report the substitute boundaries, claiming no native isolation.
10. Wait for each dispatched agent; verify actual changes and evidence and reject out-of-scope writes or invented authority without resetting another actor's work.
11. Extend through distinct prefixed agent IDs in project-owned bundles or bounded role overlays; keep shipped defaults unchanged and one owner per public ID.
12. Leave source model/effort defaults omitted; set an explicit model level through bundle-qualified project policy such as `adaptive-dev:swarm-worker`.

Example payload: the verified absolute `roles/builder.md` path; implement the supplied fixture contract in the assigned worktree and paths; commit only if expressly granted; run the named checks; return status, base/final SHA, actual changed paths, commands/outcomes, defects and unverified areas; stop condition.

The caller's lifecycle decides required records: adaptive iteration requires no SDD envelope; an SDD caller keeps its own records and gates. Agent selection grants no product decision, commit authority or current-context write.

Before dispatch, the delegating agent SHOULD record the deliverable with `uv run devkit adaptive assignment new`, its governing documents as `--governing` and literal write paths as `--write`, and put the ID in the payload.
After a return, run `uv run devkit adaptive assignment return <id>`, then `uv run devkit adaptive assignment verify <id>`; `result=fail` is a rejected return whose codes go to repair, while exit `1` alone may be a warning under `--strict`.
After integrating or abandoning the result, run `uv run devkit adaptive assignment close <id>` with the outcome and required reason.
On `ADAPTIVE_SCOPE_OVERLAP`, apply its `[FIX]` or leave a bounded experiment unrecorded.
If a command cannot record, keep the manual payload, actual diff comparison and checkpoint procedure, report assignments as unrecorded and never reroute a denied write.
