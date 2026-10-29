# Depth changes and close

Read when a task's depth must change, or Development must end without a merge.

## Raising the depth

- Raise it yourself under `[ROUTING_POLICY: depth_escalation=auto]`; under `ask`, confirm with the user first. Workers and Cloud Agents report the need as a problem instead.
- Before Development, change the classification only.
- `session` → `spec` during Development keeps the work, with no close, new slug or new worktree:
  1. On `dev-<slug>`, run `devkit spec new <slug>`. Without that branch, first run `devkit worktree start dev-<slug> --no-worktree` in this checkout, which keeps the uncommitted work.
  2. Record the agreed intent and the work so far.
  3. Run `devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user --note "approved in the session; depth session -> spec: <reason>"`; under `depth_escalation = ask`, name the user's confirmation too.
  4. Continue from the workflow's next stage.
- To `proposal` (the direction must be decided first): a close by depth escalation.

## Close

Only a party that can talk to the user closes; a worker or Cloud Agent records a problem instead.

| Close | When | Steps | Who decides |
| --- | --- | --- | --- |
| Depth escalation | A `session` or `spec` task needs its direction decided first | Add a draft proposal under a new slug, carrying what the attempt learned in its `materials/` | You (`depth_escalation = ask`: the user confirms) |
| Supersede | An accepted proposal's direction is wrong | Add a draft proposal under a new slug with `--supersedes PROP-<old>` and the attempt's material in `materials/`; delete the old accepted proposal in the same commit | The user |
| Abandon | The accepted work is dropped | Write a rejection ADR and delete the accepted proposal | The user |

1. After [feedback retirement](feedback-retirement.md) and the prerequisite disposition in [repository Backlog](backlog.md), commit the close directly to the base as Backlog work. A new draft starts over with `plan-intent` in Backlog.
2. Close the dev PR and remote branch (`gh pr close`, `git push <remote> --delete dev-<slug>`).
3. Once what the branch learned is copied out, run `devkit worktree finish dev-<slug> --discard` from the base checkout; it is the only allowed way to delete an unmerged activity branch.
