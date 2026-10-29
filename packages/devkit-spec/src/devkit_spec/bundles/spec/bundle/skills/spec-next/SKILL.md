---
name: spec-next
description: Entry skill for orientation; inspect repository state and active specs and recommend the next concrete engineering action.
---

# spec-next: Engineering Workflow Navigator

Recommend one concrete next step with its evidence. Run only the diagnosis commands below; start nothing else until
the user approves.

## Diagnosis

1. `git status -s`, `devkit worktree status` and `devkit worktree status --stale`: report uncommitted changes, the
   checkout kind (feature branch, task worktree, base), leftovers (`devkit worktree finish <branch>`) and stale
   branches with their resume or discard path (§4 of the `spec` skill's `references/branches.md`). Never remove or
   resume one unasked.
2. `devkit docs list spec`: per bundle, tasks done vs pending and pending reconciliation. Spec status `completed`
   does not prove integration; check Git/PR state.
3. `devkit docs list proposal --history`: proposals `reviewing`, `accepted` and waiting for handoff, or `rejected`
   and awaiting cleanup.
4. `devkit docs list feedback --status open --where severity=critical`, and the open count without `--where`.
5. `devkit workflow next --unit <dir>` for each unit the user or steps 2–3 name. Recommend its `[NEXT_SKILL]` with the
   `[UNMET]` evidence and follow any `[FIX]` or `[ACTION]`. For any other line or advisory, read
   [workflow signals](references/workflow-signals.md).

## Recommendation

- If critical open feedback exists, recommend a feedback hygiene pass first (the user invokes `/devkit-playbook` or
  names `spec/feedback-hygiene` when the project has one), then the stage recommendation. Give other open feedback one
  line.
- In progress means a plan-/dev- branch, a reviewing/accepted proposal or an incomplete spec; queued drafts are not.

| State | Recommend |
| :--- | :--- |
| Unit with a `[STAGE]` | Its `[NEXT_SKILL]`. In a multi-skill stage, `spec-specify`, `spec-plan` or `spec-tasks` for the first of `spec.md`, `plan.md`, `tasks.md` an unmet check names. `[NEXT_SKILL: -]`: implement the next unchecked task within its `_Boundary:` and run its tests |
| Proposal `accepted`, `[STAGE: - complete=yes]` | `devkit worktree start dev-<slug>` (or `--no-worktree`, `--existing-branch`), `devkit spec proposal handoff <slug>` there, then in the same change the [post-handoff link check](references/post-handoff.md) |
| Proposal `draft` or `reviewing` | For a queued draft, [next-work selection](references/next-work.md); otherwise review the hypothesis, add research to `materials/`, draft a PADR (`devkit spec proposal padr <slug> <title>`) or delegate a spike to `scout`/`challenger` (`spec-delegate`) |
| Proposal `rejected` | The cleanup the `SPEC_PROPOSAL_REJECTED_PENDING` `[FIX]` names; never back to `reviewing` |
| Nothing in progress | [next-work selection](references/next-work.md) |

## Completion

- The reply names one next step with its evidence (`[UNMET]` lines, Git state, list output), after any critical
  feedback pass, and ends by waiting for the user's instruction.
