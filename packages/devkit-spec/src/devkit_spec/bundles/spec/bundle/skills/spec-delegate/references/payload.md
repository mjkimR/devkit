# Payload per role

Read this in Step 2 of `spec-delegate`. Pass starting points; never inject the whole tree.

For a worker, pass the `activity-effort` of the activity. Before spawning, record what [worker](worker.md) lists: the unit's last accepted head (a blocked unit keeps its own, never its current HEAD) and the base checkout's status and HEAD, because a stray write lands there.

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

Source feedback in a worker's boundaries:

- Put only explicitly linked open source feedback that requires direct-fix disposition in its expected boundaries.
  Terminal sources are traceability, not implicit write authority or completion work.
- Include the actual paths of that feedback in a worker's allowed write scope; otherwise the Host updates them at
  completion from the worker's verified result. The unit directory alone does not authorize edits to source
  feedback elsewhere.

## Planning execution context

For a Planning worker:

- Resolve both operational instructions and CLI execution in the assigned worktree.
- If the next turn needs newer base document IDs or CLI features, the Host first refreshes the branch and
  synchronizes installed instructions under existing Git and permission policy, then includes the refreshed context
  in the next payload. The worker never merges.
- The worker returns a dependency discovered during the turn as a problem for Host recovery.

Name an ignored temporary probe path inside the proposal directory and allowed write scope:

- Verify that the path is ignored. If none exists, the Host prepares one under its existing authority before
  delegation.
- The worker removes probe files and throwaway repositories before its last commit, retaining evidence in
  `materials/`.
- When testing sandbox behavior, a path inside `/tmp` is not interchangeable with a repository-local path. If the
  allowed path cannot exercise the condition, the worker reports the needed boundary expansion instead of choosing
  an outside location.
- An ignored path grants neither sandbox access nor authority beyond the payload.

## Evidence reads and link repairs

- For work that depends on external platform facts, name the necessary official documentation reads in the
  payload's read authority, separately from external-service mutation authority. This grants no blanket network
  permission or sandbox exception.
- If the worker cannot perform those reads, the Host supplies verified sources and relevant content. A
  design-critical unverified fact remains an explicit problem or question, not settled design.
- Before delegating an intended move or deletion, the Host checks inbound references (ID references and path links)
  and includes each affected document as an exact link-repair-only write boundary.
- An unexpected target requires a narrow Host boundary expansion before editing; a move grants no general permission
  to edit outside the payload.

## Native worker paths and permissions

- Name the absolute assigned worktree, the command cwd requirement and every nested-role read scope explicitly; the
  initial cwd may be the base checkout.
- Every command, including verification and approvals, sets absolute worktree cwd; every Git command uses
  `git -C <worktree>`.
- A nested-role read scope names the assigned worktree's absolute startup skill and instruction paths (for example its
  `response-style` skill and the effective role contract), because a host skill catalog may list another checkout's
  copies. The role reads them there and reports any read from another checkout as a boundary exception in its return.
- A generic native call also receives the absolute effective managed/override contract path and the assumption that
  its role contract is emulated, with instruction loading permitted.
- Identify required nested roles and necessary approval capabilities before spawning.
- Each operation beyond current sandbox access needs its own exact scoped approval, including sibling writes, shared
  Git, registry and verification network access. Do not provide a broad persistent prefix or infer later permission
  from a successful preflight.
- The payload preserves the worker's refusal/failure procedure; it cannot promise future grants or native path
  confinement.
