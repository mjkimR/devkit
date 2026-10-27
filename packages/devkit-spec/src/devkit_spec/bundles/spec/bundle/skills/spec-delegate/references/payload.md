# Payload per role

Read this when building a payload (`spec-delegate` step 2).

| Field | Content |
| :--- | :--- |
| `task_goal` | One goal for this call |
| `relevant_files` | Starting points to read: files, AC, non-goals, ADRs |
| `allowed_boundaries` | Read scope, write scope and denied paths, as the repository's declared paths |
| `changed_paths` | Review roles: `changed_paths` of `devkit spec worker inspect --format json`, or `git diff --no-renames --name-only <base> <head>` |
| `diff_scope` | Base and head under review; required for the reviewers and the workers |
| `expected_output_format` | Summary, comparison table, envelope or docs diff |

| Role | `relevant_files` | Also pass |
| --- | --- | --- |
| `scout` | Starting points | The `materials/` path when an artifact is wanted |
| `challenger` | Proposal or spec, AC, non-goals, ADRs and capabilities as paths; at `high` the `scout` list | `activity-effort` |
| `code-reviewer` | `spec.md`, `plan.md`, `tasks.md`, touched capabilities and ADRs | Your check results; `activity-effort`; an ignored probe path inside the worktree for throwaway probe tests, preparing one if none exists, and this round's own subdirectory of it (for example `<probe path>/review-NN/`) |
| `ux-reviewer` | The Screens drafts (`spec.md` or `target-docs.md`), the use cases they list, `docs/steering/ux-objects.md` when it exists, the linked Evidence | The round number (at most two) and the earlier round's envelope; the last commit, stating any uncommitted draft |
| `triage` | The open-feedback listing (`devkit spec list feedback --status open --all-namespaces -n 0`) or the subset the user named | The clean base HEAD as `diff_scope.head` |
| `decomposer` | The draft's directory (`proposal.md`, `target-docs.md`, `decisions/`, `envelopes/`, `materials/`) and its `devkit spec refs PROP-<slug> --direction in -n 0` listing | The clean base HEAD as `diff_scope.head`; the trigger (`needs_decompose`, the user's request, `size: XL`); the parent's milestone; edges the user waived |
| `reconcile-reviewer` | `spec.md`, `reconcile.md`, the deciding review envelope, the docs `devkit spec refs <ID> --direction in` lists | `activity-effort` |
| `development-worker` | `spec.md`, `plan.md`, `tasks.md` and the code starting points | Absolute worktree path; write scope (unit directory, `_Boundary:` paths, reconcile targets); checks to run; `activity-effort`; a recovery request for an open problem |
| `planning-worker` | The proposal bundle and starting points | Absolute worktree path; the proposal directory as write scope; `activity-effort`; the user's rewritten answers |

For a later reviewer round at `high`, also pass the earlier rounds' envelope files and set `diff_scope` to the fixes since the previous round (the `spec` skill's `references/review-loop.md`).

## Workers

- Set the `diff_scope` base to the unit's [last accepted head](worker.md#the-last-accepted-head), and record the base checkout's `git status --short` and HEAD before spawning.
- Name absolute paths for nested-role reads: the worktree's own startup skills and instructions and the effective role contract, because a host skill catalog can list another checkout's copies. A generic native call also gets the absolute effective contract path and the emulation assumption.
- If a `_Boundary:` includes a bundle source the project selects, the write scope admits, as a class, every tracked path `devkit sync` writes in the worktree after the change (seeded files, projected files, `.devkit/installation.json` and the managed `AGENTS.md` block), not only the files `devkit sync --check` lists before the change, because the worker runs the sync the change implies and records each output it writes (`ADR-admit-change-sync-outputs`). `.devkit/managed/` is ignored and never a write path.
- Never ask a worker to delete a scratch file or fixture it created: authored scratch files stay in the ignored path inside the worktree, and removing the worktree (`devkit worktree finish` or integration cleanup) cleans them.
- Add linked open source feedback to the write scope, by its actual path, only when the worker fixes it directly; otherwise update it yourself at completion.
- Before delegating a move or deletion, add each document that links to the target as an exact link-repair-only write path.
- Name the official documentation reads the work needs as read authority, separate from any mutation authority; if the worker cannot read them, supply the verified content.
- Planning: when the turn needs newer base IDs or CLI features, refresh the branch and installed instructions first (the worker never merges). Name an ignored probe path inside the proposal directory, preparing one if none exists.
