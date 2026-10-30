---
id: PROP-worker-audit-known-host-advance
title: Keep the worker audit baseline across known Host-owned target advances
summary: "Drop the base-checkout HEAD and status equality from worker validation, so integrations and other sessions need not wait for a running worker; the worker's own range audit stays, and a base escape surfaces through existing head, ancestry and dirty-base checks."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: medium
size: S
planning_effort: high
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
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
base checkout's status and HEAD to match the pre-spawn record; `devkit spec worker inspect` only reports the base
checkout's HEAD and dirty paths as information.

The equality exists to catch a worker write that escapes into the base checkout, because a worker's default cwd may
be the base checkout (`MAT-base-observation-options`). In this repository on 2026-10-30, another session committed
to `main` while a Development worker ran; the Host validated the range with `devkit spec worker inspect --base
<accepted>` without issue.

The hypothesis: the worker's own range audit plus the checks that already exist keep worker escapes from staying
hidden, so the equality can go without a replacement mechanism.

## 2. Technical Spike Questions

- **Q1 Declaration**: How does the Host declare a target advance as its own, and how does inspection verify it?
  Answer: no declaration. The rule protects against a worker write escaping into the base checkout, not against
  advances. A declaration list costs one record per integration plus a durable pre-spawn HEAD, and it still stops on
  another session's commit (`MAT-base-observation-options`, option B).
- **Q2 Boundary**: Which changes still stop the worker? Answer: everything the worker audit checks today: ancestry,
  head, changed paths outside scope, dirty worktree, envelopes, rules and workflow. Base advances never stop
  validation. Escapes surface through existing checks:
  - A worker whose final commit (its `worker` envelope) landed in the base leaves its branch without that envelope,
    so inspection's head or ancestry check fails.
  - An uncommitted write in the base checkout refuses handoff and integration (`WORKTREE_BASE_DIRTY`).
  - A partial committed escape (some worker commits on the base branch, the rest on its branch) is the one case no
    check names; its content still reaches CI on the base branch. No such escape has been observed.
- **Q3 Interaction with light merging**: no base merge is required before validation or acceptance; nothing in this
  proposal reads the base checkout's HEAD.

## 3. Proposed Design & Impact

`PADR-drop-the-base-checkout-equality-from-worker-validation` records the decision; the user's choice among the
options is pending (`MAT-base-observation-options`).

- **Host procedure** (`spec-delegate/references/worker.md`, `payload.md`): drop the pre-spawn record of the base
  checkout's status and HEAD and the requirement that both match. The range passes on the existing conditions:
  ancestry, worktree HEAD, changed paths in the write scope, a clean worktree and the unit's checks. Host
  integrations and other sessions' commits proceed while a worker runs.
- **Inspection**: `devkit spec worker inspect` is unchanged; `base_checkout` stays an observation.
- **Contract**: `CAP-DLV-delivery-workflows` drops "unchanged base" from the acceptance requirements and words the
  base checkout observation as information with no Host comparison. A new ADR supersedes the base-checkout clauses of
  `ADR-orchestration-workers` (committed results and their validation; informational range inspection), and that ADR
  gains a one-line pointer to it. `ADR-reusable-lifecycle-resource-manager` keeps the write audit with the Host
  unchanged.
- **Unchanged**: the worker audit range `<accepted>..<returned>`, its checks and exit codes; Host and foreign commits
  never enter `changed_paths`; integration's dirty-base refusal; completed specs and earlier materials that restate
  the equality stay as history.
- **Alternative held for the user**: the derived scope-overlap warning (option C in `MAT-base-observation-options`)
  names base commits and dirty paths that touch the worker's write scope. Two review rounds found that every window
  variant either drops an escape (committer times do not follow ancestry here) or credits it to a Host merge, unless
  it adds recurring accounting or user confirmation.

### Acceptance

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-08 | An audit base A, base commits B made after spawning (Host, foreign or unknown), and a returned head C | The Host validates the worker's result with `devkit spec worker inspect` | A..C is the audited range with its existing checks; B never enters `changed_paths` or `outside_scope` and never blocks the range; a dirty base checkout and real conflicts stop at handoff or integration through their existing refusals. |
| WAH-01 | The bundle's worker and payload references | `test_role_contracts.py` runs | Neither `worker.md` nor `payload.md` requires a pre-spawn base record or an unchanged base status or HEAD; `worker.md` keeps the ancestry, HEAD, write-scope and clean-worktree conditions. |
| WAH-02 | `CAP-DLV-delivery-workflows` and the new ADR | `devkit rules check` runs on them | No acceptance requirement names an unchanged base; the new ADR supersedes the base-checkout clauses and `ADR-orchestration-workers` points to it. |

### Non-goals

- **Scope Excluded**: a global repository lock or autonomous scheduler.
- **Scope Excluded**: treating a base advance as worker authorship, write permission or a skip of the final
  integration checks.
- **Scope Excluded**: a declaration record of Host advances, a base-advance window in inspection, or a commit-gate
  branch check.
- **Scope Excluded**: changing integration's dirty-base refusal or its handling of moved targets
  (`PROP-integration-merge-moved-target`).

## Planning decisions

- Planning compared dropping the equality (A), a declared-Host-advance list (B) and a derived scope-overlap warning
  (C) (`MAT-base-observation-options`). It first recommended C; `challenger-01` and `challenger-02` showed that C's
  window either loses escapes or needs per-entry accounting, so Planning now recommends A. The user's choice is
  pending.
- GOP-08 is restated, pending the same choice: the parent's "unknown or dirty target changes stop" would stop on every
  foreign commit; under A a dirty base and real conflicts stop at their existing refusals instead.
- The earlier scope-overlap-warning PADR was withdrawn with the switch to A and replaced by
  `PADR-drop-the-base-checkout-equality-from-worker-validation`.
- The new ADR names the superseded clauses in its text and `ADR-orchestration-workers` gets a pointer line; it carries
  no `supersedes` field, because superseding the alias of the committed-results decision in `ADR-orchestration-workers`
  would also retire the worker's Git actions and the rest of that decision.
- `size` is `S`: the change is the bundle references, one capability, one ADR and its pointer, and one contract test.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-worker-audit-known-host-advance`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
