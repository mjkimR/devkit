---
id: ADR-session-reclassification-of-a-queued-draft
title: Session reclassification of a queued draft
summary: 'A queued draft without PADRs may, on the user''s explicit decision at pickup, be deleted as Backlog work that keeps its open feedback and be done as a session task: the one exception to lowering depth only through a proposal''s handoff.'
proposal: SPEC-draft-direct-acceptance
status: accepted
created_at: 2026-10-19
---

# [ADR-session-reclassification-of-a-queued-draft] Session reclassification of a queued draft

- **Status**: Accepted
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

Every request not started now is a draft proposal (`SPEC-backlog-roadmap-and-issues`), so a request whose work is
`session` depth (no design choice, no contract impact, verifiable in the session: 01 §2.2, `classification.md` §1)
also waits as a draft once it is queued. Direct acceptance (`ADR-direct-acceptance-command-and-handoff-guard`) always
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
  allows it, and the Host never deletes silently. Workers and Cloud Agents never do it. Before proposing it the Host
  settles that it can push to the base (or that there is no remote), as for a direct acceptance; a protected base
  keeps the draft on its normal route. The user kept this restriction (`answer-02.yaml`,
  `reclassification-on-protected-base`): on a protected base queued `session`-depth work goes through Planning and a
  spec Unit, and direct acceptance is unavailable there too; the deletion never rides the session's `dev-<slug>` PR.
- **Conditions**: the draft is `status: draft` with no local or fetched `plan-<slug>` (`devkit spec proposal check`,
  fetch first, as for every deletion) and has no `PADR-*.md` in `decisions/` (its workflow gate records do not count).
  The `session` criteria cannot hold for a draft marked `needs_decompose` (not yet classified, `classification.md` §1),
  a draft with `supersedes` or a depth escalation's draft (each exists because a direction must be decided first), so
  the Host does not propose it for them.
- **The request** names what goes: the draft and its gate records, its `materials/` (kept in Git history only), the
  `milestone` membership (a `session` task cannot be a member; no hygiene check reports the lost member, even for a
  done or dropped milestone, so the user reviews the milestone's exit condition here), and the open feedback that is
  preserved. The same exchange may also agree the session's intent, which has no record file; each decision is
  answered explicitly.
- **The deletion** is one Backlog commit on the base checkout, before the session starts, outside the worktree and
  PR policies like other Backlog deletions. This record is its authority. In the same commit it preserves open
  feedback and strikes through incoming references on the base, promoted feedback dispositions included, per
  feedback retirement (steps 1 to 4), so nothing dangles. The message states the user's decision and the reason
  ("depth proposal -> session on the user's decision: <reason>"). Right after committing it, before the session
  starts, the Host names the deletion commit to the user, so a session lost before its report still leaves the way
  back known.
- **A new slug**: the session, its `dev-<slug>` and any Unit a later raise adds use a slug other than the deleted
  draft's (01 §7.4: a reused slug blurs the work), so a `PROP-<slug>` mention merged later from another branch is
  never rewritten as a handoff.
- **The session** then starts through inline Planning (01 §6.1): its intent is agreed in the conversation, since the
  draft's `plan-intent` record goes with the draft, and it follows the `session` rules, raising to `spec` when a
  lasting design record, a contract change or a Living Spec change turns out to be needed. Its final report names the
  deletion commit. If it ends without integrating, the recovery is `git revert` of the deletion commit, on the user's
  decision, which restores the draft with its intent record, milestone, feedback and references when no later commit
  changed those paths; otherwise the Host resolves the conflicts with the user, and a milestone closed since pickup
  is reviewed again for the restored member (01 §7.2: undo by revert, never a reset).
- **Scope of the exception**: it is the only lowering besides a proposal's handoff, and it applies only to a queued
  draft before Planning; a proposal in review or accepted, and a spec Unit, are never lowered.
- No command or tool check is added: the deletion uses the existing check, the conditions are visible to the Host, and
  the commit gate's link check and `RULE-document-reference` catch a reference left dangling. The ADR this record
  becomes keeps the exception in devkit-spec's Living Spec; the strategy layer's 01 §2.2 states it first.

## 5. Consequences

- The lowering rule gains one stated exception in 01 §2.2 and Q19, `classification.md` §3, the bundle `AGENTS.md`,
  `CAP-HARN-agent-guidance` and the `CAP-DLV-delivery-workflows` non-goal on depth changes; `backlog.md` grants the
  deletion, and `feedback-retirement.md`, `CAP-DLV-proposal-incubation` §3.1, the `sdd-proposal` feedback paragraph
  and 01 §6.2 list it among the deletions that preserve open feedback.
- A request deleted this way leaves no Unit: its record is the deletion commit and the session's final report, and a
  revert of that commit is its only way back to the queue.
- A milestone may lose a member at pickup; the request shows it, so the user can review the milestone.
