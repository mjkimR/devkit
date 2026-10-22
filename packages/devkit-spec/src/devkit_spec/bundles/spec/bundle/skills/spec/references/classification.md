# Classification, Backlog and inline Planning

The axes and workflows are in the spec constitution (`devkit get-context spec`). This adds the criteria and the start of each depth.

## 1. Classify (Backlog)

- `bugfix` only for a defect against an agreed contract.
- `overall-refactor` only for a change that adds no behavior and restructures several areas at once (package boundaries, conventions, document systems, ledgers), whose direction settles during the work; follow `.devkit/managed/spec/workflows/sdd-overall-refactor.md`. A refactor inside one feature or module is `feature`.
- `task-kind` stays provisional until `plan-accept` or the spec Unit's creation.
- Large but clear work is `spec`; small work whose direction is open is `proposal`.
- Backlog and inline Planning have no `activity-effort`; choose it per later activity ([effort](effort.md)), preserving explicit user choices and required review.
- Run Backlog in `direct` mode per [repository Backlog](backlog.md). Commit only the draft and its intent record before starting Planning from the base HEAD.
- Decompose a request with independently delivered outcomes into drafts first; one proposal hands off to one spec.
- Record a follow-up found during other work as feedback by default, or as a draft proposal in the current checkout.
- To change a depth or end Development without a merge, read [depth changes and close](depth-and-close.md).

## 2. Inline Planning (`session`, `spec`) and the problem rule

- `spec`: start `dev-<slug>` and the Unit per [worktree](worktree.md) §1, or with `--no-worktree` per [branches](branches.md) §2; agree the intent, record `plan-intent` and commit. That committed state is Development's input; a worker or cloud run continues the branch ([branches](branches.md) §3).
- `session`: agree the intent in the conversation and follow `.devkit/managed/spec/workflows/sdd-session-<task_kind>.md` for its mode, branch and completion.
- Keep one Unit when its outcome can be implemented and verified together; sequence shared contracts and conflicting files, and parallelize independent scopes.
- Inside the agreed goal, scope and contract, take the recommended option and record it.
- Only a problem that cannot be solved without changing the agreement stops the work. A worker records it and you resolve it per [worker records](worker-records.md) §3; a scope change needs the user and a close.
- If the work addresses named feedback, follow [source feedback](source-feedback.md).
- Before direct-spec intake or explicit proposal pickup, run the direct unit prerequisite procedure in `spec-next/references/next-work.md`.
