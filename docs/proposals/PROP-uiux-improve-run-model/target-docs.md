---
id: PROP-uiux-improve-run-model-target
title: Target contracts for task-approved UI/UX runs
summary: "Prospective capability, use-case and decision updates for explicit per-task UI/UX route approval, bounded Git effects, scope growth and report-only documentation follow-up."
status: draft
proposal: PROP-uiux-improve-run-model
created_at: 2026-11-13
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
  - file: docs/decisions/2026-11/20261105-uiux-improvement-workflow-boundary.md
  - file: docs/decisions/2026-11/20261110-impeccable-session-authority.md
---

# [PROP-uiux-improve-run-model-target] Target contracts for task-approved UI/UX runs

These are prospective changes after implementation and acceptance. Current contracts remain in force in Planning.
No product screen is drafted by this instruction-only change.

## 1. Capability: CAP-DLV-uiux-improvement

Rewrite the summary and description to support a task-approved outside-workflow run or the user's chosen consumer
workflow. Preserve rules 1–2, 4–10, 13–15 and 18 and selection-neutral installation.

- **Rule 3 — Consumer authority**: WHEN implementing requested changes, including accepted delegated changes, the
  coordinator MUST follow the route the user authorized for this task while preserving product constraints and
  host permissions. Review: the entry/authority integration assertion.
- **Rule 11 — Verification**: WHEN reporting an improvement on either route, the coordinator MUST report before/after
  interface verification and applicable project-check outcomes separately from design inference and unavailable
  coverage. Review only: representative scenarios; integration assertions check the instruction.
- **Rule 12 — Qualified completion**: retain changed interface/flow or useful partial work and concrete blocker;
  include the selected route, actual check coverage and remaining unauthorized Git effects in the report.
- **Rule 16 — Session brief and routing**: condition only the consumer-workflow pre-implementation step on the route
  the user chose. Keep the brief, recorded base, edit classes, permission controls, coordinator pause and all current
  question/load routing. Review: existing Impeccable delegation integration assertion.
- **Rule 17 — Coordinator acceptance**: retain attribution and file-acceptance checks. The stale-document report
  names each document, its affected statement and the next action through the consumer's documentation process or a
  separate documentation task; the run edits none of those documents. Review: existing acceptance assertion.
- **Rule 19 — Requested setup and cleanup**: retain every explicit user-request and context-file boundary; its final
  route follows rule 3. Review: existing setup/cleanup assertion.
- **Rule 20 — Run choice**: WHEN an implementation request enters the skill, the coordinator MUST obtain explicit
  per-task approval for the announced outside-workflow procedure or use the consumer workflow the user chooses,
  before product edits or write-capable delegation. A task instruction already granting the exact choice is reused;
  absent an answer or approval channel, dependent edits wait. Test: entry/authority assertions and scenario review.
- **Rule 21 — Scope growth**: WHEN proposed work adds a surface or behavior beyond the approved goal or changes a
  user constraint, the coordinator MUST obtain a new user decision before the dependent edit. Test: scope scenarios.
- **Rule 22 — Git effects**: WHEN a commit, integration or publication lacks current task authority, the coordinator
  MUST obtain it for the named remaining effects before acting; route choice alone grants no such authority.
  Test: authority scenarios and entry/authority assertions.

Keep independent roles and reviews optional under rule 6. The skill recommends a useful independent UX or code
check when the changed structure or implementation warrants it; the result names whether it ran. No equal-quality
claim or mandatory review cast is added.

## 2. Use case: UC-improve-an-interface-and-user-flow

Keep the seven-step main scenario. Step 1 recovers the task and the user's route choice; step 5 implements through
that choice. Step 7 reports actual route, verification, stale-document follow-up and remaining delivery authority.
Keep all references to `CAP-DLV-uiux-improvement`.

Add or update extensions for no approval channel/no answer, explicit workflow choice, scope growth, absent Git
authority and a stale-document follow-up without a consumer documentation process. Condition 5c's workflow
pre-implementation wording on the selected route. Keep other Impeccable command and load branches unchanged.

| Case | Given / When / Then |
| --- | --- |
| RM-01 — Outside route | Given a bounded improvement task, when the user explicitly approves the announced outside-workflow procedure, then the agent runs the improvement loop, applicable checks and before/after verification without workflow-specific records |
| RM-02 — Existing approval | Given an explicit task instruction already selecting that procedure, when the entry runs, then it reuses that instruction without another identical approval prompt |
| RM-03 — Workflow route | Given a configured consumer process, when the user chooses it, then the agent completes that process's pre-implementation and delivery steps |
| RM-04 — No answer | Given no prior route approval and no answer or approval channel, when implementation would begin, then dependent product edits and write-capable delegation wait while useful read-only inspection is retained |
| RM-05 — Git authority | Given route approval but no commit/integration authority, when verification finishes, then the agent presents the concrete result and asks once for its named remaining effects; it performs none before authority arrives |
| RM-06 — Scope growth | Given an approved goal, when a proposed new surface or behavior exceeds it, then the agent asks before that edit; an in-goal implementation file addition alone does not trigger a new scope decision |
| RM-07 — Stale documents | Given an accepted change that makes a consumer UX statement stale, when the result is reported, then the document, affected statement and concrete separate follow-up are named and its file remains unedited |
| RM-08 — Host refusal | Given an approved outside route, when the host denies an operation, then the agent preserves useful work and reports the blocker without another access route |
| RM-09 — Optional review | Given unavailable fresh review or the user's declined optional review, when applicable project checks and interface checks finish, then the result names that coverage limit without inventing independent evidence |

The existing review-only scenario still returns findings without product edits.

## 3. Decisions and implementation mirrors

Promote `PADR-uiux-task-approved-run`. Keep both predecessor ADRs accepted and add exact partial-supersession
pointers repeating the source PADR's scope. Existing OOUX and context-file ownership, Impeccable selection, edit-list
acceptance, native host restrictions and no implicit Git authority remain in force.

Update entry description, Boundaries, procedure steps 1 and 6–10 and Completion; update orchestration's local-role
continuation, setup, delegation, acceptance and requested-action route wording; update the human README's execution
and permission explanation. Keep these mirrors workflow-neutral and keep question/load routing unchanged.
