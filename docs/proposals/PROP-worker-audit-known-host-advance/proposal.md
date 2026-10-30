---
id: PROP-worker-audit-known-host-advance
title: Keep the worker audit baseline across known Host-owned target advances
summary: "Replace the base-checkout HEAD equality in worker validation with a derived warning naming base commits and dirty paths that touch the worker's write scope, so integrations and other sessions need not wait for a running worker while worker escapes stay visible."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: medium
size: M
planning_effort: high
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/features/worker/
    - packages/devkit-spec/src/devkit_spec/base/errors.py
    - docs/decisions/2026-10/20261022-orchestration-workers.md
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-worker-audit-known-host-advance] Keep the worker audit baseline across known Host-owned target advances

## 1. Background & Hypothesis

The exact-base observation rule caused unnecessary serialization in the resource-indexer consumer pilot
(`MAT-git-operator-consumer-pilot`): the Host held independent Planning integrations while a Development worker ran,
solely to preserve its recorded base HEAD. The worker reference (`spec-delegate/references/worker.md`) requires the
base checkout's status and HEAD to match the pre-spawn record, and `devkit spec worker inspect` derives
`base_checkout` in `features/worker/usecases/inspect.py`.

The equality exists to catch a worker write that escapes into the base checkout, because a worker's default cwd may
be the base checkout (`MAT-base-observation-options`). It is prose only: inspection reports the base checkout as
information and the Host compares it by hand. In this repository on 2026-10-30, another session committed to `main`
while a Development worker ran; the Host validated the range with `devkit spec worker inspect --base <accepted>`
without issue.

The hypothesis: inspection can derive the base commits made while the worker ran and name only those, and the base
dirty paths, that touch the worker's write scope. That keeps escapes visible without a declaration, a pre-spawn record
or serialized integrations.

## 2. Technical Spike Questions

- **Q1 Declaration**: How does the Host declare a target advance as its own, and how does inspection verify it?
  Answer: no declaration. The rule protects against a worker write escaping into the base checkout
  (`MAT-base-observation-options`), not against advances. A declaration list costs one record per integration plus a
  durable pre-spawn HEAD, and it still stops on another session's commit, as observed in this repository on
  2026-10-30. Inspection derives the relevant base commits itself and names only those that touch the worker's write
  scope.
- **Q2 Boundary**: Which changes still stop the worker? Answer: an overlap entry the Host cannot account for (a base
  commit after the audit base, or a base dirty path, inside the write scope) blocks the range. Everything the worker
  audit already checks still fails: ancestry, head, changed paths outside scope, dirty worktree, envelopes, rules,
  workflow. Dirty paths outside the write scope are left to integration's `WORKTREE_BASE_DIRTY` refusal; real
  conflicts are integration's concern (`PROP-integration-merge-moved-target`).
- **Q3 Interaction with light merging**: no base merge is required before validation or acceptance; the window is
  derived from the base checkout's HEAD whether or not the Host merged it.

## 3. Proposed Design & Impact

`PADR-replace-the-base-head-equality-with-a-scope-overlap-warning` records the decision; this section is its
contract. The user's choice between this design and dropping the equality outright is pending.

- **Window**: `devkit spec worker inspect` lists the non-merge commits reachable from the base checkout's HEAD and not
  from the returned head (`git rev-list --no-merges <base HEAD> --not <returned>`) whose committer time is at or after
  the committer time of the audit base `<accepted>`. Each commit contributes its own changed paths (renames as both
  names), so an escape is named by itself whatever merge carried it onto the base branch. No merge base is needed.
  The time filter keeps every commit made after `<accepted>`, including an escape, and drops advances the Host saw
  before spawning.
- **Overlap**: a window commit or a base-checkout dirty path inside the inspection's write scope (derived, or the
  `--scope` override) is an entry of `base_checkout.overlap` and raises the `WARNING` `SPEC_WORKER_BASE_OVERLAP`. A
  commit entry carries `commit`, `subject`, `committer_time` and its in-scope `paths`; a dirty entry carries `dirty`
  and its in-scope `paths`. `base_checkout.window_commits` counts every window commit. The warning fails no check:
  the exit code is `0`, and `1` only under `--strict`. Its `[ACTION]` states the accounting rule below.
- **Not computed**: when the scope check is `not-run` or the window cannot be derived (a Git error), `overlap` is
  absent (never `[]`) and a `SPEC_WORKER_CHECK_NOT_RUN` notice names the cause; inspection never exits `2` for it.
  Without a base checkout (inspection run in the base itself), nothing changes.
- **Text output**: one `[BASE_OVERLAP: <commit or dirty> paths=...]` line per entry after `[BASE_CHECKOUT: ...]`, and
  the warning rendered on stderr with its own code and level. `commands.py` stops rebuilding every result notice as
  `WorkerCheckNotRunNotice`.
- **Host procedure** (`spec-delegate/references/worker.md`, `payload.md`): drop the pre-spawn record of the base
  checkout and the "status and HEAD match" requirement. Account for each overlap entry before accepting: a commit
  entry only when the Host made the commit or integrated a source that contains it
  (`git merge-base --is-ancestor <commit> <integrated source head>`), a dirty entry only when the Host wrote the path.
  Any other entry blocks the range unless the user confirms it as another session's write. Host integrations and
  other sessions' commits proceed while a worker runs.
- **Contract**: `CAP-DLV-delivery-workflows` replaces "unchanged base" among the acceptance requirements and describes
  the window, the fields, the sentinel and the code row in Worker result inspection. A new ADR supersedes the
  base-checkout clauses of `ADR-orchestration-workers` (committed results and their validation; informational range
  inspection), and that ADR gains a one-line pointer to it. `ADR-reusable-lifecycle-resource-manager` keeps the
  write audit with the Host unchanged.
- **Unchanged**: the worker audit range `<accepted>..<returned>`, its checks and exit codes; Host and foreign commits
  never enter `changed_paths`; completed specs and earlier materials that restate the equality stay as history.

### Acceptance

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-08 | An audit base A, a Host or foreign base commit B made after A outside the write scope, and a returned head C | `devkit spec worker inspect` runs in the worktree | A..C is the audited range with its existing checks; B is counted in `base_checkout.window_commits` and raises no warning; B's paths never appear in `changed_paths` or `outside_scope`. |
| WAH-01 | A base commit after A that changes a path inside the write scope | inspect runs, in JSON and in text | `base_checkout.overlap` names the commit, subject, committer time and in-scope paths; `SPEC_WORKER_BASE_OVERLAP` is a `WARNING` with an `[ACTION]` in JSON `notices` and on text stderr; text prints its `[BASE_OVERLAP: ...]` line; exit `0`, and `1` under `--strict`. |
| WAH-02 | A base commit committed before A, in scope | inspect runs | No overlap entry. |
| WAH-03 | A base dirty path inside, and another outside, the write scope | inspect runs | Only the inside path is an overlap entry; `dirty_paths` still lists both. |
| WAH-04 | An in-scope commit made on the base after A, then carried by a merge commit (another unit's integration under `ff-only`) | inspect runs | The non-merge commit itself is the overlap entry; the merge commit is not. |
| WAH-05 | The scope check is `not-run`, or the window's Git query fails (the base checkout's HEAD is unborn) | inspect runs | `overlap` is absent, a `SPEC_WORKER_CHECK_NOT_RUN` notice names the cause, and the exit code is the one the other checks give. |
| WAH-06 | The bundle's worker and payload references | `test_role_contracts.py` runs | `worker.md` states the accounting rule for overlap entries; neither file requires a pre-spawn base record or an unchanged base HEAD. |

### Non-goals

- **Scope Excluded**: a global repository lock or autonomous scheduler.
- **Scope Excluded**: treating a base advance as worker authorship, write permission or a skip of the final
  integration checks.
- **Scope Excluded**: a commit-gate branch check or a declaration record of Host advances.
- **Scope Excluded**: changing integration's dirty-base refusal or its handling of moved targets
  (`PROP-integration-merge-moved-target`).

## Planning decisions

- Planning compared dropping the equality, a declared-Host-advance list and the derived overlap warning
  (`MAT-base-observation-options`) and recommends the warning; the user's choice is pending (`challenger-01` finding 4).
- The level is `WARNING`, not `NOTICE`: a condition the Host must act on is a warning under
  `CAP-ADV-agent-advisory-protocol`, and `--strict` counts only warnings (`ARCH-08-1-agent-output`). It still fails no
  check, which keeps the exit-code model of `ADR-orchestration-workers`' informational range inspection.
- The window uses non-merge commits so a merge cannot carry an escape under the Host's own name.
- GOP-08 is restated, pending the same user choice: the parent's "unknown or dirty target changes stop" would stop on
  every foreign commit and on the user's own uncommitted base edits; the restated row and WAH-01 to WAH-06 limit
  detection to the worker's write scope.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-worker-audit-known-host-advance`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
