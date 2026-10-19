---
id: PADR-eligibility-for-direct-acceptance
title: Eligibility for direct acceptance
summary: "A draft may skip Planning only with an accepted plan-intent, no needs_decompose, no supersedes, no Planning branch, no envelope hold and a valid task_kind, and when the Host judges its direction leaves nothing to compare; no size limit applies."
proposal: PROP-draft-direct-acceptance
status: draft
created_at: 2026-10-19
---

# [PADR-eligibility-for-direct-acceptance] Eligibility for direct acceptance

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

Every request not started now is a draft proposal (`SPEC-backlog-roadmap-and-issues`), so many drafts carry a
direction that is already settled: a piece split off a larger request, a follow-up promoted from feedback, a request
whose contract is clear. Direct acceptance lets the user accept such a draft without a Planning run. It needs a rule
for which drafts qualify, split into what a tool can check and what only the Host and the user can judge.

## 2. Decision Drivers

- Depth is not size (01 §2.2): small work can need its direction decided, large work can be clear.
- A draft whose existence means the direction is open must never skip Planning: a supersede reverses an earlier
  `plan-accept`, and a depth escalation exists because the direction must be decided first (`classification.md` §4).
- The user's explicit `plan-accept` is the safeguard; the rule must not pretend a tool can judge a direction.

## 3. Considered Options

- **Mechanical checks plus the Host's judgment, no size limit** (chosen).
- **Add a size limit (`S` or `M`)**: rejected; it mixes size into a depth decision and blocks large but clear work,
  which 01 §2.2 classifies as `spec`.
- **A frontmatter marker set in Backlog (for example `direction: settled`)**: rejected; it is a stored depth axis in
  disguise (`ADR-task-kind-and-planning-depth`: the axes are not stored) and would be set when the request is filed,
  not when it is accepted.

## 4. Decision Outcome

- **Checked by the tool**, all at the moment of acceptance: `status: draft`; an effective accepted
  `gate:plan-intent`; no `needs_decompose: true`; no `supersedes`; no local or fetched `plan-<slug>`; `task_kind` is
  `feature` or `bugfix`; no envelope hold (an unresolved problem, a pending question or a malformed envelope). The
  conditions of the chosen path are checked too (for the recommended path: `pull_request = auto` and the checkout is
  on the base branch). The same checks run read-only first, so a refusal leaves nothing behind.
- **Judged by the Host and shown to the user**: the direction leaves nothing to compare (no option to weigh, no
  question to ask), the body has no open spike question, and the draft is not a depth escalation carrying a failed
  attempt's material. The request names the recorded `planning_effort` hint, which the user confirmed at
  `plan-intent`; when it is not `low`, the Host states why Planning is skipped anyway. PADRs already in the draft are
  listed, because the handoff promotes them to accepted ADRs.
- No size limit.

## 5. Consequences

- A draft that fails a mechanical check runs Planning as today; the refusal names the failed condition.
- A draft that passes but that the Host judges unsettled is proposed for Planning, with the reason; the Host never
  proposes direct acceptance silently, and the user may still choose Planning for an eligible draft.
- Depth escalation has no frontmatter marker, so that exclusion stays a judgment; a marker is not added for it.
