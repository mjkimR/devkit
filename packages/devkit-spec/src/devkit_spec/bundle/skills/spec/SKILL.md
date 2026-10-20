---
name: spec
description: Main entry skill for development intent; conversational router and pair programmer. Classifies the work (task-kind, planning-depth, activity-effort), runs Backlog and inline Planning and drives the spec-driven delivery workflows.
---

# spec: Conversational Router & Pair Programmer

Use this skill for any development task, feature request or troubleshooting. `spec` is the **central human-agent router**: it directs each intent to the spec-driven delivery skill that fits, using **progressive disclosure**.

Read `devkit spec policy` before classifying work; approval and Git policy follow [completion](references/completion.md#policy). Explicit user instructions and authorization already given take precedence. A policy command error stops policy-dependent work.

---

## 1. Operating Invariants

1. **No Session Hijacking (`MUST NOT`)**: never unilaterally declare the user's session finished or stop working on active tasks without user direction.
2. **Contextual Retrospective Reminder (`SHOULD`)**: under `FEEDBACK_POLICY reminder=contextual`, reusable observations from completed work SHOULD prompt an optional `/spec-feedback` sweep, never a completion or merge gate; under `reminder=off`, none. Routine completions, proposal additions and wording edits need no reminder.
3. **Progressive Disclosure (`SHOULD`)**: load only the current phase's instructions, not every template, instruction or playbook up front.

---

## 2. Two-Tier Routing Workflow

When the user enters `/spec <intent>` or asks a general engineering question:

### Classification and Planning
Classify on the three axes of the spec constitution (`devkit get-context spec`): `task-kind`, then `planning-depth`, then per activity the mode and `activity-effort` ([effort](references/effort.md)). Propose the classification and let the user confirm it at `plan-intent`; for a proposal the same request proposes the Planning effort. Backlog, inline Planning, depth changes and closes follow [classification](references/classification.md). Before any bundle or edit, settle the branch and worktree per `GIT_POLICY` ([worktree](references/worktree.md); a branch without a worktree, an existing branch: [branches](references/branches.md)):

| Classification | Workflow | Planning and start |
| :--- | :--- | :--- |
| `session` × `feature` | `sdd-session-feature` | Inline Planning: agree the intent in the conversation (session: no records). Implement, verify and review at the effort, following `devkit workflow show sdd-session-feature` in the session. |
| `session` × `bugfix` | `sdd-session-bugfix` | Same, with the expected behavior agreed; a failing reproduction test first (Red), then the fix (Green), reporting both. |
| `spec` × `feature` | `sdd-spec-feature` | Inline Planning on `dev-<slug>`: `devkit spec new <slug> --title "..." --summary "..."`, record `plan-intent`, commit; Development then runs `spec-specify` ➔ `spec-plan` ➔ `spec-tasks` and the later stages. |
| `spec` × `bugfix` | `sdd-spec-bugfix` | Same with `--workflow sdd-spec-bugfix`; Development characterizes the defect (`spec-specify`, bugfix reference), reproduces with a `red` envelope and verifies with a `green` one. |
| `proposal` (either kind) | `sdd-proposal`, then `sdd-spec-<task_kind>` | Backlog: `devkit spec proposal new <slug> --task-kind feature\|bugfix [--planning-effort ...] [--dev-effort ...]`; the user's confirmation of the draft is `plan-intent`. Planning (its own activity) runs on `plan-<slug>` to `plan-accept` following [planning](references/planning.md), in `direct` mode or by a `planning-worker`, unless the user accepts an eligible draft directly in Backlog ([backlog](references/backlog.md)); Development starts on `dev-<slug>` with `devkit spec proposal handoff <slug>` and the `spec-next` skill's post-handoff link check. |
| Spike, independent review, or reconcile verification in an isolated context | Support role | `spec-delegate` (`scout`, `challenger`, `code-reviewer`, `reconcile-reviewer`), as the `activity-effort` asks. |
| Native approval preparation, or integration after CLI/PR `dev-integration` authorization | Integration | `spec-integrate`: base integration, re-verify changed parts, confirm reconcile, final checks. |

`devkit workflow show --unit <dir>` (or `<workflow-id>` without a bundle) shows a workflow's stages, checks, gates, `exception` stage and returns; external runners use the same definition.

Gates: `plan-intent` and `plan-accept` are always the user's decision, recorded after the user's explicit answer only: `plan-intent` with `devkit workflow answer --unit <dir> --request gate:plan-intent --action accept|decline --by user`, an acceptance of `plan-accept` only with `devkit spec proposal accept <slug> --by user` (it also writes the status), a decline of `plan-accept` with `devkit workflow answer ... --action decline --by user --note "<reason>"`; `dev-integration` follows `GATE_POLICY` ([completion](references/completion.md#policy)). An approval is never inferred or hand-written; `--given` also asserts a runner check (`lint-ci-clean`, `merged`) per run. There is no Development direction gate; a problem that breaks the agreement follows [classification](references/classification.md) §2 (Units: [worker records](references/worker-records.md) §3).

`devkit spec new` and proposal handoff bind the bundle; bind one made otherwise with `devkit workflow bind --unit <dir> --workflow <id>` (definition changes apply without rebinding). Go back within Development with `devkit workflow return --unit <dir> --to <stage>` (voiding later approvals and envelopes); never back to Planning. Envelopes live under the bundle's `envelopes/` ([envelope](references/envelope.md)); a run's questions, problems, answers and resolutions follow [worker records](references/worker-records.md).

### Playbooks
`spec` never searches or routes to playbooks. A playbook runs only when the user invokes `devkit-playbook` for the task or a failing rule's remediation names one; any other operational request is ordinary work.

---

## 3. Completion & Retrospective Guidance

Read [completion](references/completion.md) when approaching review or completion. Before `dev-integration`, run the `collect-feedback` sweep the workflow names (`spec-feedback`; skipped under `[STAGE_POLICY: collect-feedback state=off]`), then present the final change report in the [envelope](references/envelope.md) format. Integrate with `spec-integrate` under the [policy](references/completion.md#policy) and report code-review completion and integration completion as separate facts. PR and worktree choices follow [git policy](references/git-policy.md). Commits are plain `git commit`; the commit gate runs the staged checks.

Planning returns follow [per-run feedback](../spec-feedback/references/sweep.md#planning-run-coverage).
Before deleting a proposal without handoff, follow [feedback retirement](references/feedback-retirement.md).
