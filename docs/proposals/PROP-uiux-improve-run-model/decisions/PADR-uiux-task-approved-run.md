---
id: PADR-uiux-task-approved-run
title: Offer task-approved UI/UX runs outside the consumer workflow
summary: "For UI/UX improvement requests, we offer a task-approved run outside the consumer workflow, to reduce process overhead while retaining permissions and checks, accepting that independent reviews remain optional."
proposal: PROP-uiux-improve-run-model
supersedes: [ADR-uiux-improvement-workflow-boundary, ADR-impeccable-session-authority]
status: draft
created_at: 2026-11-13
---

# [PADR-uiux-task-approved-run] Offer task-approved UI/UX runs outside the consumer workflow

## 1. Context & Problem Statement

`CAP-DLV-uiux-improvement` requires every implementation to follow the consumer workflow. The bundle owner wants a
lighter procedure for UI/UX tasks, announced before work and enabled only by explicit task approval. The two pilots
in `MAT-uiux-improve-second-pilot` show less bookkeeping in one outside-workflow run; they do not show equivalent
defect detection. The skill still needs a bounded user goal, checks and attributable changes.

## 2. Decision Drivers

- Preserve the owner's task-approved route without changing installation or configured approach.
- Keep product constraints, host restrictions and actual Git authority effective.
- Keep applicable checks and report incomplete verification honestly.
- Preserve optional roles, consumer files and a workflow-neutral independent installation.

## 3. Considered Options

1. Keep the workflow for every run: retains established process checks and records, with the pilot's overhead.
2. Announce an outside-workflow procedure and require task approval: expresses the owner's preference and avoids
   workflow records for that task, with optional independent reviews and separate stale-document follow-up.
3. Ask neutrally which route to use: retains both choices but omits the owner's announced default and still needs
   an explicit no-answer outcome.

## 4. Decision Outcome

Chosen option: announce the outside-workflow procedure and obtain explicit task approval, while retaining the
consumer workflow when the user chooses it. This gives the user the light route without the skill selecting a
workflow departure on its own.

- Before product edits or write-capable delegation, the coordinator announces the outside-workflow procedure and
  obtains the user's explicit route choice for this task, reusing an exact instruction already given. Without an
  answer or approval channel, dependent edits wait. → `CAP-DLV-uiux-improvement` rule 20 (MUST).
- Requested inline, accepted delegated and explicitly requested setup/cleanup changes follow the selected route,
  retaining product constraints and host permissions. Selecting or invoking the bundle alone changes no configured
  approach or workflow policy. → `CAP-DLV-uiux-improvement` rules 3 and 19 (MUST).
- The outside route uses the improvement loop and applicable project checks and before/after interface verification;
  independent roles and reviews remain optional, with missing coverage reported. → `CAP-DLV-uiux-improvement`
  rules 6 (MAY), 11 (MUST) and 12 (SHOULD).
- Work beyond the approved goal or a change to a user constraint needs a new decision before the dependent edit.
  → `CAP-DLV-uiux-improvement` rule 21 (MUST).
- Route choice grants no commit, integration or publication authority. The coordinator reuses current task authority
  or asks once for the named remaining effects before acting. → `CAP-DLV-uiux-improvement` rule 22 (MUST).
- Stale consumer OOUX and UX documents remain unedited in the run and are reported with the affected statement and a
  concrete separate follow-up through the consumer's documentation process where one exists.
  → `CAP-DLV-uiux-improvement` rule 17 (MUST).
- The selected route determines whether consumer pre-implementation workflow steps apply; the Impeccable brief,
  permission boundaries, question/load routing and coordinator acceptance remain intact.
  → `CAP-DLV-uiux-improvement` rules 16 and 17 (MUST).

Supersedes in part `ADR-uiux-improvement-workflow-boundary`: Decision Outcome clause 2 unconditional continuation through the consumer development workflow. Selection-neutral workflow policy, no implicit Git authority and clauses 1, 3 and 4 remain in force.

Supersedes in part `ADR-impeccable-session-authority`: Decision Outcome clauses requiring unconditional consumer-workflow pre-implementation steps, continuation for accepted implementation and user-requested setup or cleanup, and stale-document updates through the consumer workflow's own step. Implementation and requested actions now follow the user's per-task route choice; stale documents are reported for the consumer's documentation process where present or a separate documentation task otherwise. Host approvals, no implicit Git authority, report-only document ownership, brief, question/load routing and acceptance boundaries remain in force.

## 5. Consequences

- Positive: a task can avoid workflow-specific records on the user's explicit choice without changing project policy.
- Negative: optional reviews can miss defects the first pilot caught; no defect-parity claim follows from the pilots.
- Negative: stale consumer documents need a separate follow-up; the run reports the work instead of reconciling it.
- Risk: a broad route approval could be mistaken for blanket permission; the goal, permission and Git-effect
  boundaries remain explicit and separately checked.
- The existing pilot measurement plan remains evidence guidance for further runs, not a new runtime or gate.

## 6. Confirmation

- Instruction assertions in `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py` check entry
  approval, both routes, prior-authority reuse, permissions, scope bounds, selected-route delegation and stale-doc
  reporting. `PROP-uiux-improve-run-model-target` lists the representative cases.
- The installed-consumer E2E checks independent installation and selection-neutral approach without delivery records.
- Review only: model obedience, actual workflow compatibility in each consumer, design quality and comparative
  defect detection. No test or pilot establishes those outcomes.
