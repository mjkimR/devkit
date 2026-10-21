---
name: spec-next
description: Entry skill for orientation; inspect repository state and active specs and recommend the next concrete engineering action.
---

# spec-next: Engineering Workflow Navigator

Use this skill to orient at session start or choose the next action: diagnose state and recommend one concrete step with evidence.

---

## 1. Operating Invariant: No Automatic Execution

> [!IMPORTANT]
> **Pure Recommendation Only (`MUST NOT` auto-execute)**:
> `spec-next` MUST only diagnose state and explain the recommended next step. The agent MUST NOT automatically start implementing, creating files, or executing code without the user's explicit approval.

---

## 2. Diagnosis Workflow

Run Steps 1 to 4; run Step 0 for each unit directory the user, Step 2 or Step 3 names.

### Step 0: Ask the CLI for the current stage

```bash
devkit workflow next --unit specs/<YYYY-MM>/<YYYYMMDD>-<slug>     # a spec bundle
devkit workflow next --unit docs/proposals/PROP-<slug>            # a proposal bundle
```

`[STAGE]` is the diagnosed stage, `[UNMET]` the evidence and `[NEXT_SKILL]` the skill to recommend; follow any `[FIX]` or `[ACTION]`. For any other line (`[GATE]`, `[WAITING]`, `[REQUEST]`, `[DELEGATE]`, `[SKIPPED]`, an error line, ...) or an advisory, read [workflow signals](references/workflow-signals.md). `devkit workflow show --unit <dir>` shows the whole flow. Steps 1 to 4 add what the CLI does not see.

### Step 1: Check Working Tree & Git State
Run `git status -s`:
- Uncommitted or unstaged changes? On a feature branch, a task worktree or the base branch?
- Report leftovers from `devkit worktree status` at any `GIT_POLICY` level, each as `devkit worktree finish <branch>` or user-authorized removal, and stale activity branches from `devkit worktree stale` (also warned by `devkit rules check -p hygiene`), each with its resume or discard path, per §4 of the `spec` skill's `references/branches.md`; never remove or resume any unasked.

### Step 2: Check Active Change Specs (`specs/`)
Run `devkit spec list spec` (completed bundles are left out unless `--history`; follow any `[NEXT_CMD]`) and inspect only the listed directories. Completed specs are work history: pass `--history --status completed` only when a task explicitly needs one.
- `tasks.md`: tasks completed vs pending.
- `reconcile.md`: prioritize pending required reconciliation after implementation review. Distinguish verified/uncommitted, PR review, reconciliation pending and integrated; spec status `completed` does not prove integration, inspect Git/PR state.

### Step 3: Check Incubating Proposals (`docs/proposals/`)
Run `devkit spec list proposal`: proposals in `reviewing` or `accepted` waiting for handoff, and an accepted one ready for `devkit spec proposal handoff <slug>` (on `dev-<slug>`).

### Step 4: Check Open Feedback
Run `devkit spec list feedback --status open --where severity=critical` for the critical items, and the same without `--where` for the count of the rest.

---

## 3. Decision Matrix & Action Guidance

**Critical feedback first.** If open feedback with `severity: critical` exists, the first recommendation is a feedback hygiene pass on those items now (recommend that the user invoke `/devkit-playbook` when the project has a playbook for it; never start a playbook search yourself); the stage recommendation follows as the second item. Lower-severity open feedback gets one line and waits for the next hygiene session.

In-progress means a plan-/dev- branch, a reviewing/accepted proposal, or an incomplete spec; queued drafts are not in progress.

| Diagnosed State | Status Criteria | Recommended Next Action |
| :--- | :--- | :--- |
| **Unit in progress** | Step 0 names a `[STAGE]` | Recommend its `[NEXT_SKILL]` with the `[UNMET]` evidence; gates, waits and other lines as [workflow signals](references/workflow-signals.md) describes. `[NEXT_SKILL]` is only a stage's first skill: in a multi-skill stage recommend `spec-specify`, `spec-plan` or `spec-tasks` for the first of `spec.md`, `plan.md`, `tasks.md` an unmet check names (`not-skeleton(...)`, `file-exists(plan.md)`, `tasks-exists`); `[NEXT_SKILL: -]` (`build-verify`, `fix-verify`) means implement the next unchecked task within its `_Boundary:` and run its tests |
| **Proposal Hand-off** | Proposal `status: accepted` (`plan-accept` given) and `next` reports it complete (`[STAGE: - complete=true]`) | Start or continue `dev-<slug>` (`devkit worktree start dev-<slug>`, `--no-worktree` in this checkout, or `--existing-branch`), run `devkit spec proposal handoff <slug>` there, then the post-handoff link check (§3.1) |
| **Proposal Incubation** | Proposal in `draft` or `reviewing` | For a queued draft, [next-work selection](references/next-work.md) (Planning, direct acceptance or session reclassification). Review the hypothesis, add research to `materials/`, or draft a PADR (`devkit spec proposal padr <slug> <title>`); for a spike, delegate `scout`/`challenger` (`spec-delegate`) |
| **Ended (Rejected)** | Proposal is `rejected` | Planning ended: the cleanup `SPEC_PROPOSAL_REJECTED_PENDING`'s `[FIX]` names (rejection ADR, then deletion; the user may invoke the `feedback-hygiene` playbook); never back to `reviewing` |
| **Idle** | No in-progress Unit | Recommend eligible queued drafts and Backlog actions with [next-work selection](references/next-work.md) |

### 3.1 Post-handoff link check

Run it immediately after every `devkit spec proposal handoff <slug>`, in the same change: [post-handoff link check](references/post-handoff.md).

---

## 4. Output Standard

A concise summary:

```markdown
### Current Status & Next Action Diagnosis

- **Active Stage**: build-verify
- **Active Feature**: `SPEC-feature-name` (specs/2026-10/20261004-feature-name/)
- **Progress**: 2 / 5 tasks completed in `tasks.md`

#### Recommended Next Step:
**Implement Task 2.3: Wire CLI handler**
- **Boundary**: `src/app/cli.py`
- **Verification**: the project's test command

*(Type `proceed` or give instructions to begin this task)*
```
