# Payload per role

Read this in Step 2 of `spec-delegate`. Pass starting points, never the whole tree.

| Field | Content |
| :--- | :--- |
| `task_goal` | One goal for this call |
| `relevant_files` | Files, acceptance criteria, non-goals and ADRs to read, as starting points |
| `allowed_boundaries` | This task's read scope, write scope and explicitly denied paths, as repository-declared paths, not generic globs |
| `changed_paths` | For both review roles: the paths changed between the compared commits, from `devkit spec worker inspect --format json`, or `git diff --no-renames --name-only <base> <head>` before a worker envelope exists |
| `diff_scope` | Base ref and head of the change under review; required for `code-reviewer`, `reconcile-reviewer` and the workers |
| `expected_output_format` | Summary, comparison table, review envelope, docs draft diff or similar |

At `high`, every reviewer round is a fresh call (the `spec` skill's `references/review-loop.md`): round 1 gets the whole change, and a later round's `diff_scope` covers the fixes since the previous round.

| Role | `relevant_files` | `diff_scope` | Also pass |
| --- | --- | --- | --- |
| `scout` | Starting points | optional | The `materials/` path when an artifact is wanted |
| `challenger` | Proposal or spec, AC, non-goals, ADRs and capabilities as paths (it has no shell); at `high` the `scout` list | optional | The `activity-effort`; in a later round also the earlier rounds' findings (their envelope files) and the round's diff scope |
| `code-reviewer` | `spec.md`, `plan.md`, `tasks.md`, touched capabilities and ADRs | required | Your check results (tests, build, `devkit rules check --staged`); the `activity-effort`; in a later round also the earlier rounds' findings (their envelope files) and the round's diff scope |
| `reconcile-reviewer` | `spec.md`, `reconcile.md`, the deciding review envelope, the targeted and affected docs (`devkit spec refs <ID> --direction in`) | required | The `activity-effort`; in a later round also the earlier rounds' findings (their envelope files) and the round's diff scope |
| `development-worker` | The unit's `spec.md`, `plan.md`, `tasks.md` and the code starting points | required: the last accepted head; the worker returns its own head | The worktree's absolute path; the write scope inside it (the unit's directory, the tasks' `_Boundary:` paths, the Living Spec paths the reconcile targets); the checks to run; the `activity-effort`; a recovery request for an open problem |
| `planning-worker` | The proposal bundle and the starting points | required: the last accepted head; the worker returns its own head | The worktree's absolute path; the proposal directory as write scope; the `activity-effort`; the user's rewritten answers to the recorded questions |

Before spawning a worker, record the base checkout's `git -C <base> status --short` and HEAD, because a stray write lands there. The last accepted head and its exceptions: [worker](worker.md#the-last-accepted-head).

## Source feedback in a worker's boundaries

- Put in the expected boundaries only explicitly linked open source feedback whose disposition is a direct fix. Terminal sources are traceability, not write authority or completion work.
- Include that feedback's actual paths in the worker's write scope; otherwise the Host updates them at completion from the worker's verified result. The unit directory alone does not authorize editing source feedback elsewhere.

## Planning worker context

- The worker resolves operational instructions and CLI execution in its assigned worktree.
- If the next turn needs newer base document IDs or CLI features, refresh the branch and synchronize installed instructions first, under existing Git and permission policy, and include the refreshed context in the payload. The worker never merges.
- The worker returns a dependency it discovers during the turn as a problem for Host recovery.
- Name an ignored temporary probe path inside the proposal directory and the write scope:
  - Verify that the path is ignored. If none exists, prepare one under your existing authority before delegating.
  - The worker removes probe files and throwaway repositories before its last commit and keeps the evidence in `materials/`.
  - A `/tmp` path is not interchangeable with a repository-local one when testing sandbox behavior. If the allowed path cannot exercise the condition, the worker reports the needed boundary expansion instead of choosing an outside location.
  - An ignored path grants neither sandbox access nor authority beyond the payload.

## Evidence reads and link repairs

- If the work depends on external platform facts, name the official documentation reads in the payload's read authority, separately from any external-service mutation authority. This grants no blanket network permission or sandbox exception.
- If the worker cannot perform those reads, supply verified sources and their relevant content. A design-critical unverified fact stays an explicit problem or question, not settled design.
- Before delegating a move or deletion, check inbound references (ID references and path links) and add each affected document as an exact link-repair-only write boundary.
- An unexpected target needs a narrow boundary expansion from you before the worker edits it; a move grants no general permission to edit outside the payload.

## Native worker paths and permissions

- Name the absolute assigned worktree, the command cwd requirement and every nested-role read scope explicitly; the initial cwd can be the base checkout.
- Every command, including verification and approvals, sets absolute worktree cwd; every Git command uses `git -C <worktree>`.
- A nested-role read scope names the assigned worktree's absolute startup skill and instruction paths (for example its `response-style` skill and the effective role contract), because a host skill catalog can list another checkout's copies. The role reads them there and reports any read from another checkout as a boundary exception in its return.
- A generic native call also receives the absolute effective managed/override contract path and the assumption that its role contract is emulated, with instruction loading permitted.
- Each operation beyond the current sandbox access needs its own exact scoped approval, including sibling writes, shared Git, the scope registry and verification network access. Give no broad persistent prefix, and infer no later permission from a successful preflight.
- Keep the worker's refusal and failure procedure in the payload; the payload cannot promise future grants or native path confinement.
