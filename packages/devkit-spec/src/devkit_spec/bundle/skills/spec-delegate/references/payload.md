# Payload per role

Read this in Step 2 of `spec-delegate`. Never inject the whole tree. For a worker, pass the `activity-effort` of the activity and record what [worker](worker.md) lists before spawning: the unit's last accepted head (a blocked unit keeps its own, never its current HEAD) and the base checkout's status and HEAD, since a stray write lands there.

A reviewer round at `high` (the `spec` skill's `references/review-loop.md`) is always a fresh call: round 1 gets the whole change; each later round also the earlier rounds' findings and, as `diff_scope`, the fixes since the previous round.

| Field | Content |
| :--- | :--- |
| `task_goal` | One goal for this call |
| `relevant_files` | Files, acceptance criteria, non-goals and ADRs to read; starting points, not a dump |
| `allowed_boundaries` | Read scope and write scope for this task, plus explicitly denied paths; repository-declared paths, not generic globs |
| `changed_paths` | Actual paths changed between the compared commits, from `devkit spec worker inspect --format json` (or `git diff --no-renames --name-only <base> <head>` before a worker envelope exists); pass to both review roles |
| `diff_scope` | Base ref and head of the change under review (required for `code-reviewer`, `reconcile-reviewer` and the workers) |
| `expected_output_format` | Summary, comparison table, review envelope, docs draft diff, etc. |

| Role | `relevant_files` | `diff_scope` | Also pass |
| --- | --- | --- | --- |
| `scout` | Starting points | optional | The `materials/` path when an artifact is wanted |
| `challenger` | Proposal or spec, AC, non-goals, ADRs, capabilities, as paths (it has no shell); at `high` the `scout` list | optional | The `activity-effort`; in a later round also the earlier rounds' findings (their envelope files) and the round's diff scope |
| `code-reviewer` | `spec.md`, `plan.md`, `tasks.md`, touched capabilities and ADRs | required | Your check results (tests, build, `devkit rules check --staged`); the `activity-effort`; in a later round also the earlier rounds' findings (their envelope files) and the round's diff scope |
| `reconcile-reviewer` | `spec.md`, `reconcile.md`, the deciding review envelope, the targeted and likely affected docs (`devkit spec refs <ID> --direction in`) | required | The `activity-effort`; in a later round also the earlier rounds' findings (their envelope files) and the round's diff scope |
| `development-worker` | The unit's `spec.md`, `plan.md`, `tasks.md` and the code starting points | required: the last accepted head; the worker returns its own head | The worktree's absolute path, the write scope inside it (the unit's directory, the tasks' `_Boundary:` paths, the Living Spec paths the reconcile targets), the checks to run, the `activity-effort`, a recovery request for an open problem |
| `planning-worker` | The proposal bundle and the starting points | required: the last accepted head; the worker returns its own head | The worktree's absolute path, the proposal directory as write scope, the `activity-effort`, the user's rewritten answers to the recorded questions |


A Planning or Development worker records its feedback inside its own unit before its last work commit; a Planning run also returns fresh sweep evidence ([run coverage](../../spec-feedback/references/sweep.md#planning-run-coverage)).

Only explicitly linked open source feedback requiring direct-fix disposition belongs in its expected boundaries.
Terminal sources are traceability, not implicit write authority or completion work.
Include their actual paths in a worker's allowed write scope; otherwise the Host updates them at completion from the
worker's verified result. The unit directory alone does not authorize edits to source feedback elsewhere.

## Native worker paths and permissions

Name the absolute assigned worktree, command cwd requirement and every nested-role read scope explicitly; initial
cwd may be the base checkout. Every command, including verification and approvals, sets absolute worktree cwd;
every Git command uses `git -C <worktree>`. A generic native call also receives the absolute effective managed/override
contract path and the assumption that its role contract is emulated, with instruction loading permitted.

Identify required nested roles and necessary approval capabilities before spawning. Each operation beyond current
sandbox access needs its own exact scoped approval, including sibling writes, shared Git, registry and verification
network access. Do not provide a broad persistent prefix or infer later permission from successful preflight. The
payload preserves the worker's refusal/failure procedure; it cannot promise future grants or native path confinement.
