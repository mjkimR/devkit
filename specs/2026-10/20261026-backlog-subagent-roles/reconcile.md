---
reconcile_id: REC-backlog-subagent-roles
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/architecture/ARCH-04-1-ecosystem-boundaries.md
    resolution: modified
  - file: docs/usecases/delivery/UC-route-development-intent.md
    resolution: modified
  - file: docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md
    resolution: modified
---

# Reconcile: SPEC-backlog-subagent-roles

## Living Spec changes

- `CAP-DLV-delivery-workflows`: section 4.6 adds the `triage` and `decomposer` rows (no skill, cited procedure,
  profile and effort, writes nothing, envelope kind none), the seven read-only roles, the snapshot comparison in the
  caller guidance and their Backlog delegation without a stage; the `sdd-proposal` stage list adds the size exit; the
  `worktree start` row names the `plan-` attach refusals.
- `CAP-DLV-proposal-incubation`: the `size` field defines `XL` with one example of each side; `target-docs.md` is
  recommended for `M` or `L`; rule 13 adds the size gate (one predicate, exit check, `accept --direct`, `plan-`
  attach, Planning return), its two exits and the optional `decomposer` delegation; rule 14 adds the size condition.
- `CAP-HARN-agent-guidance`: the subagent asset list, the `spec-delegate` and `feedback-hygiene` rows, the Backlog
  paragraph (decomposer, `XL` gate, judging size at plan-intent, Host verification, reclassification) and the
  spec-next Backlog actions.
- `ARCH-04-1-ecosystem-boundaries`: the Subagent Roles row (also the missing `ux-reviewer`).
- `UC-route-development-intent`: extensions 1a, 1c and 3c.
- `UC-incubate-and-hand-off-a-proposal`: extension 1a (an `XL` draft gets no `plan-intent` and is decomposed),
  the size blocker in 2b and Scenario 6.

Entrypoints: no candidate applied; the new files sit under doorways the documents already declare (reconcile-check-01).

No glossary term changes: `triage` and `decomposer` are role IDs, like the other roles.

## Source feedback

- `FB-support-role-diff-check-on-dirty-tree`: `resolved` with a disposition naming this spec (AC-05,
  `test_the_support_role_snapshot_sees_a_write_to_an_already_modified_file`).

## Dogfood triage run (AC-13)

The projected `triage` role was not in the running session's agent catalog, so it ran as an emulated generic native
call (a read-only `Explore` subagent) with the effective contract `.devkit/managed/spec/subagents/triage.md`, at head
`2f1a0137` over the 4 open feedback items. `git status --porcelain` was empty before and after; the `spec-delegate`
snapshot tree was `70e7a72d` before and after. Return (`status: completed`, 4 groups, no duplicates):

| Group | Ownership | Recommended destination |
| --- | --- | --- |
| `FB-integration-readiness-loads-new-rule-with-base-code` | `repo` | Fix: a `bugfix` task (observed evidence; blocks integration) |
| `FB-entrypoints-apply-ignores-file-codes` | `repo` | Fix: a `bugfix` task (observed evidence) |
| `FB-new-seed-sync-output-outside-boundaries` | `repo` | Fix: a proposal (an open design question between two approaches) |
| `FB-support-role-diff-check-on-dirty-tree` | `repo` | Resolved by this spec; dismissal candidate otherwise (its evidence is a hypothesis) |

Assumption the role reported: equal severity and recurrence, so groups were ordered by impact. No status was changed.
