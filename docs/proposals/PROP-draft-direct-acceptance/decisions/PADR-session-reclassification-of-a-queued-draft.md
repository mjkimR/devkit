---
id: PADR-session-reclassification-of-a-queued-draft
title: Session reclassification of a queued draft
summary: 'A queued draft without PADRs may, on the user''s explicit decision at pickup, be deleted as Backlog work that keeps its open feedback and be done as a session task: the one exception to lowering depth only through a proposal''s handoff.'
proposal: PROP-draft-direct-acceptance
status: draft
created_at: 2026-10-19
---

# [PADR-session-reclassification-of-a-queued-draft] Session reclassification of a queued draft

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

Every request not started now is a draft proposal (`SPEC-backlog-roadmap-and-issues`), so a request whose work is
`session` depth (no design choice, no contract impact, verifiable in the session: 01 §2.2, `classification.md` §1)
also waits as a draft once it is queued. Direct acceptance (`PADR-direct-acceptance-command-and-handoff-guard`) always
ends in a spec Unit with `spec.md`, `plan.md`, `tasks.md` and a reconcile, which is heavier than the session the work
needs. Deleting a draft is already Backlog work, but deleting it in order to do the work as a session lowers the depth
the request has by structure (a proposal), and the lowering rule allows lowering only through a proposal's handoff
(01 §2.2, `classification.md` §3, the bundle `AGENTS.md`, `CAP-HARN-agent-guidance`), because an agent could classify
low to save cost. The user chose to allow it on their explicit decision (`answer-01.yaml`, question
`session-reclassification`).

## 2. Decision Drivers

- The risk the lowering rule guards against is the agent's choice; the user's explicit decision answers it, as it
  does for direct acceptance.
- Waiting in the queue must not make work heavier than its depth: a request done today as a session must not need a
  spec Unit because it was filed first.
- Nothing settled is lost: open feedback is preserved, and a draft whose decisions must survive (PADRs, which only a
  handoff promotes to ADRs) is excluded.
- One named route, so the lowering rule states its exception instead of being worked around.

## 3. Considered Options

- **Allow it on the user's explicit decision at pickup, as a Backlog deletion** (chosen).
- **Not allowed** (a session-depth draft uses direct acceptance or Planning and becomes a spec Unit): rejected; it
  makes queued session work pay for a Unit, Living Spec reconcile and a handoff.
- **The Host decides alone**: rejected; that is the under-classification the lowering rule exists to prevent.
- **Keep the draft with a marker or status for session work**: rejected; the axes are not stored
  (`ADR-task-kind-and-planning-depth`), and a draft left in the queue would duplicate the session's work.

## 4. Decision Outcome

- **Who and when**: in Backlog (`direct`), when the user picks a queued draft to start now, the Host may propose doing
  it as a `session` task, with the reason the work meets the `session` criteria; only the user's explicit decision
  allows it, and the Host never deletes silently. Workers and Cloud Agents never do it.
- **Conditions**: the draft is `status: draft` with no local or fetched `plan-<slug>` (`devkit spec proposal check`,
  fetch first, as for every deletion) and has no PADR in `decisions/`. The `session` criteria cannot hold for a draft
  marked `needs_decompose` (not yet classified, `classification.md` §1), a draft with `supersedes` or a depth
  escalation's draft (each exists because a direction must be decided first), so the Host does not propose it for
  them.
- **The request** names what goes: the draft and its gate records, `materials/` (kept in Git history only), the
  `milestone` membership (a `session` task cannot be a member; the user keeps or reviews the milestone's exit
  condition), and the open feedback that is preserved.
- **The deletion** is one Backlog commit on the base checkout, before the session starts, outside the worktree and
  PR policies like other Backlog deletions; it preserves open feedback per feedback retirement in the same commit,
  and its message states the user's decision and the reason ("depth proposal -> session on the user's decision:
  <reason>").
- **The session** then starts through inline Planning (01 §6.1): its intent is agreed in the conversation, since the
  draft's `plan-intent` record goes with the draft, and it follows the `session` rules, raising to `spec` when a
  lasting design record, a contract change or a Living Spec change turns out to be needed. If it ends without
  integrating, the Host proposes filing the request again as a new draft.
- **Scope of the exception**: it is the only lowering besides a proposal's handoff, and it applies only to a queued
  draft before Planning; a proposal in review or accepted, and a spec Unit, are never lowered.
- No command or tool check is added: the deletion uses the existing check, and the conditions are visible to the
  Host. The ADR this record becomes keeps the exception in devkit-spec's Living Spec; the strategy layer's 01 §2.2
  states it first.

## 5. Consequences

- The lowering rule gains one stated exception in 01 §2.2, `classification.md` §3, the bundle `AGENTS.md` and
  `CAP-HARN-agent-guidance`; `backlog.md` and `feedback-retirement.md` name the deletion.
- A request deleted this way leaves no Unit: its record is the deletion commit and the session's final report.
- A milestone may lose a member at pickup; the request shows it, so the user can review the milestone.
