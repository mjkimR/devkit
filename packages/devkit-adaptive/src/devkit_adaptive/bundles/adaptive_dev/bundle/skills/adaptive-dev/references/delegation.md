# Bounded delegation

1. Work directly when a separate context adds no useful evidence; no action requires every role or a fixed team sequence.
2. Select `product-clarifier`, `product-researcher` or `usage-reviewer` for existing product support; keep their no-commit contracts.
3. Select `swarm-planner` for read-only partitioning, `swarm-worker` for bounded implementation, or `swarm-verifier` for source-specific checks with assigned ignored probe/test outputs; compatible external callers can reuse these agents under their own workflow.
4. Invoke a registered agent through the host's registered-role mechanism so its execution settings apply; if unavailable, report the gap and use direct execution or explicitly labelled generic role-file emulation.
5. Resolve `roles/<role>.md` from the directory containing the invoked `SKILL.md`, never the cwd or reference directory; if that location is unavailable, locate and verify the invoked skill first.
6. Verify the chosen role exists and pass its absolute installed path; read only the chosen overlay, not every role body.
7. For an external caller, accept a verified caller-owned absolute role path; require its permissions to be compatible with the agent, project and assignment, and reject incompatible requirements explicitly.
8. Supply one goal, source/base identity, absolute read/write ownership including the role file, governing documents by ID or absolute path or `none`, permitted actions and Git operations, checks, stop condition, depth and Host-wide allowance, and expected return fields.
9. Partition by independently checkable deliverables and dependency edges, not file count or activity labels.
10. For each assignment name one owner, dependency or `none`, completion evidence and the expected integration handoff.
11. If another assignment depends on a shared interface, name its owner and provide its agreed version and source or artifact identity.
12. If a dependent worktree lacks that version, supply the identified contract as an explicit input or defer the assignment.
13. If the interface changes, reassess dependent assignments before accepting their results.
14. On an emulated host, compare actual source/index/HEAD before and after and report the substitute boundaries without claiming native isolation.
15. Wait for each dispatched agent; verify actual changes and evidence, and reject out-of-scope writes or invented authority without resetting another actor's work.
16. Extend projects through distinct prefixed agent IDs in project-owned bundles or bounded role overlays; keep shipped defaults unchanged and one owner per public ID.
17. Leave source model/effort defaults omitted; use existing bundle-qualified project policy such as `adaptive-dev:swarm-worker` when an explicit model level is wanted.

Example assignment: read the verified absolute `roles/builder.md` path, implement the supplied fixture contract in the assigned worktree and paths, commit only if expressly granted, run the named checks and return status, base/final SHA, actual changed paths, commands/outcomes, defects and unverified areas. The payload also supplies depth, allowance and stop condition.

The caller's lifecycle controls required records: adaptive iteration requires no SDD envelope; an SDD caller retains its own records and gates. Agent selection grants no product decision, commit authority or current-context write.

Before dispatching a deliverable, the delegating agent SHOULD record it with `uv run devkit adaptive assignment new`,
passing its governing documents as `--governing` and its literal write paths as `--write`; put the assignment ID in the payload.
After a return, record it with `uv run devkit adaptive assignment return <id>`, then run `uv run devkit adaptive assignment verify <id>`.
Treat `result=fail` as a rejected return and route its codes to repair; exit `1` alone may instead mean a warning under `--strict`.
After integrating or abandoning the result, use `uv run devkit adaptive assignment close <id>` with the outcome and required reason.
On `ADAPTIVE_SCOPE_OVERLAP`, narrow the scope, close a finished assignment, sequence with `--depends-on`, or leave a bounded experiment unrecorded; name only an existing dependency.
On `ADAPTIVE_GOVERNING_UNRESOLVED`, correct the value, bring the document into the assignee's worktree, or pass an absolute path of a readable copy.
If a command cannot record, keep the manual payload, actual diff comparison and retained checkpoint procedure above; report assignments as unrecorded and never reroute a denied write.
