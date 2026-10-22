---
id: ADR-delivery-classification
title: Classify delivery work by task-kind and planning-depth
summary: "For delivery work, we classify on task-kind, planning-depth and activity-effort with named gates, start sdd-spec-bugfix bundles with spec.md only and allow a queued draft to become a session on the user's decision, to keep one axis per question, accepting a broad rename."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-handoff-workflow-key
  - ADR-bugfix-bundles-start-with-spec-only
  - ADR-task-kind-and-planning-depth
  - ADR-session-reclassification-of-a-queued-draft
---

# [ADR-delivery-classification] Classify delivery work by task-kind and planning-depth

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @mjkimR
- **Involved Components/Capabilities**: `CAP-DLV-delivery-workflows`, `CAP-DLV-proposal-incubation`,
  `CAP-DLV-spec-bundles`, `CAP-DLV-project-policy`, `CAP-HARN-agent-guidance`

---

## 1. Context & Problem Statement

Routes 1 to 4 mixed two questions in one name: what the work does (only `bugfix` said that) and what must be settled
before implementation (the rest). Proposals combined them through a `handoff_workflow` frontmatter key, introduced
because `workflow` and `workflow_hash` in a unit's anchor file are devkit's binding of that unit, `proposal.md` is the
anchor of the proposal unit, and `devkit workflow handoff` rebinds a unit in place and refuses a candidate with another
anchor (`HANDOFF_LAYOUT_MISMATCH`), so it cannot turn a proposal bundle into a spec bundle. The gates were numbered
(G1, G2, G3) while the engine and the UI used names, and Development carried a direction gate that stopped work for
choices the agreed intent already covered. The strategy layer's master flow (workbench
`docs/strategy-layer/01-master-flow.md`) settles the replacement; this record keeps the decision in devkit-spec's
Living Spec.

The bugfix workflow orders its stages differently from a feature: it characterizes the defect before it plans, and
`plan-tasks` writes `plan.md` and `tasks.md`. A skeleton `tasks.md` present at `characterize` would have to cover the
acceptance criteria the characterization produces (`RULE-task-coverage`, run by `lint-clean`) before anyone has planned
the tasks.

Every request not started now is a draft proposal (`SPEC-backlog-roadmap-and-issues`), so a request whose work is
`session` depth (no design choice, no contract impact, verifiable in the session: 01 §2.2, `classification.md` §1)
also waits as a draft once it is queued. Direct acceptance always ends in a spec Unit with `spec.md`, `plan.md`,
`tasks.md` and a reconcile, which is heavier than the session the work needs. Deleting a draft is already Backlog
work, but deleting it in order to do the work as a session lowers the depth the request has by structure (a
proposal), and the lowering rule allows lowering only through a proposal's handoff (01 §2.2, `classification.md` §3,
the bundle `AGENTS.md`, `CAP-HARN-agent-guidance`), because an agent could classify low to save cost. The user chose
to allow it on their explicit decision (`answer-01.yaml`, question `session-reclassification`).

---

## 2. Decision Drivers

- One axis per question, so each combination maps to exactly one workflow without conditional stages.
- Fewer stops: inside the agreed goal, scope and contract the executor decides; only a problem that breaks the
  agreement stops the work.
- Approvals keep their meaning across a handoff: a proposal's acceptance is never re-labelled as another decision.
- Structure is the record: the Unit's kind and its bound workflow show the axes, so no field can disagree with them.
- devkit's binding keys keep devkit's meaning; the follow-up workflow is part of the proposal record that is reviewed
  and approved; the cross-layout move (proposal bundle to spec bundle) needs its own command.
- Every stage's exit checks can be met by doing that stage's work, in order; the bundle exists from the start, so the
  unit has its anchor and binding; what the proposal knew about the target area and boundaries is not lost.
- The risk the lowering rule guards against is the agent's choice; the user's explicit decision answers it, as it
  does for direct acceptance.
- Waiting in the queue must not make work heavier than its depth: a request done today as a session must not need a
  spec Unit because it was filed first.
- Nothing settled is lost: open feedback is preserved, and a draft whose decisions must survive (PADRs, which only a
  handoff promotes to ADRs) is excluded.
- One named route, so the lowering rule states its exception instead of being worked around.

---

## 3. Considered Options

### Option 1: Three axes and named gates (Selected by `ADR-task-kind-and-planning-depth`)
- **Overview**: `task-kind`, `planning-depth` and `activity-effort`; workflows `sdd-<planning-depth>[-<task-kind>]`;
  named gates; no Development direction gate; the handoff target read from the proposal's `task_kind`.
- **Pros**: each axis answers one question; the gate names match the engine's request ids; a `session` task needs no
  Unit at any effort.
- **Cons**: every workflow id, gate name and skill text changes at once.

### Option 2: Keep the routes and rename only the gates (Rejected by `ADR-task-kind-and-planning-depth`)
- **Pros**: smaller change.
- **Cons**: the mixed axis stays, and the Development direction gate keeps stopping work.

### Option 3: A separate key `handoff_workflow` (Selected by `ADR-handoff-workflow-key`, later replaced by `task_kind`)
- **Overview**: `handoff_workflow: <id>` without prefix, written by `devkit spec proposal new --handoff-workflow`;
  `devkit spec proposal handoff` binds `spec.md` to it.
- **Pros**: no clash with devkit's binding; the choice is visible in the proposal under review.
- **Cons**: introduces an additional frontmatter key.

### Option 4: Keep `workflow` for the follow-up workflow (Rejected by `ADR-handoff-workflow-key`)
- **Cons**: the proposal could not be a devkit workflow unit, so its gates could not be evaluated.

### Option 5: Choose the workflow only at handoff time (Rejected by `ADR-handoff-workflow-key`)
- **Cons**: the decision escapes the reviewed record and depends on the agent remembering it.

### Option 6: `spec.md` only for bugfix bundles (Selected by `ADR-bugfix-bundles-start-with-spec-only`)
- **Pros**: `characterize` exits on its own work; `RULE-task-coverage` skips a spec without `tasks.md`.
- **Cons**: bugfix and feature bundles start with different file sets.

### Option 7: All three skeletons, as for features (Rejected by `ADR-bugfix-bundles-start-with-spec-only`)
- **Cons**: `characterize`'s `lint-clean` fails on a placeholder `tasks.md` that cannot match the characterized
  criteria.

### Option 8: No bundle until `plan-tasks` (Rejected by `ADR-bugfix-bundles-start-with-spec-only`)
- **Cons**: no anchor, so no binding, no gates and no `devkit workflow next` during the first stages.

### Option 9: Session reclassification on the user's explicit decision at pickup, as a Backlog deletion (Selected by `ADR-session-reclassification-of-a-queued-draft`)

### Option 10: Not allowed (Rejected by `ADR-session-reclassification-of-a-queued-draft`)
- **Cons**: a session-depth draft would use direct acceptance or Planning and become a spec Unit, making queued
  session work pay for a Unit, Living Spec reconcile and a handoff.

### Option 11: The Host decides alone (Rejected by `ADR-session-reclassification-of-a-queued-draft`)
- **Cons**: that is the under-classification the lowering rule exists to prevent.

### Option 12: Keep the draft with a marker or status for session work (Rejected by `ADR-session-reclassification-of-a-queued-draft`)
- **Cons**: the axes are not stored, and a draft left in the queue would duplicate the session's work.

---

## 4. Decision Outcome

- **Axes**: work is classified on `task-kind` (`feature`, `bugfix`), `planning-depth` (`session`, `spec`, `proposal`)
  and `activity-effort` (`low`, `medium`, `high`) instead of Routes 1 to 4. (ADR-task-kind-and-planning-depth)
- **Workflows**: `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-feature`, `sdd-spec-bugfix`, `sdd-proposal`.
  (ADR-task-kind-and-planning-depth)
- **Gates**: `plan-intent`, `plan-accept` and `dev-integration` are named gates matching the engine's request ids;
  Development has no direction gate. Which gates accept a policy and which values they take is stated in
  `ADR-delivery-decision-boundaries`, which replaced the rule that `plan-intent` and `plan-accept` are always the
  user's with no policy key. (ADR-task-kind-and-planning-depth)
- **Handoff target**: the handoff target is `sdd-spec-<task_kind>`, read from the proposal's `task_kind`, the only
  axis value stored as a field because a proposal is not yet bound to its spec workflow; `handoff_workflow` is replaced
  by `task_kind`; `spec.md` has no `kind` field. The handoff carries `gate:plan-intent` and `gate:plan-accept` under
  their own names. (ADR-task-kind-and-planning-depth)
- **Integration gate semantics**: the approval-gate semantics of `ADR-delivery-decision-boundaries` for integration
  stay under the name `dev-integration`. (ADR-task-kind-and-planning-depth)
- **Envelopes**: Planning's question rounds, the structured question, answer, problem and resolution envelopes and the
  blocked state rest on devkit envelope contracts that are adopted separately. (ADR-task-kind-and-planning-depth)
- **Bugfix bundles**: a spec bundle bound to `sdd-spec-bugfix`, from `devkit spec new` or a proposal handoff, is
  created with `spec.md` alone; `plan.md` and `tasks.md` are written in the workflow's `plan-tasks` stage, so no
  skeleton has to match criteria that characterization has not produced yet. A handoff puts the proposal's target
  area and boundaries into a `### Target Area & Boundaries` section of the carried notes.
  (ADR-bugfix-bundles-start-with-spec-only; workflow id and no `kind` field per ADR-task-kind-and-planning-depth)
- **Session reclassification, who and when**: in Backlog (`direct`), when the user picks a queued draft to start now,
  the Host may propose doing it as a `session` task, with the reason the work meets the `session` criteria; only the
  user's explicit decision allows it, and the Host never deletes silently. Workers and Cloud Agents never do it.
  Before proposing it the Host settles that it can push to the base (or that there is no remote), as for a direct
  acceptance; a protected base keeps the draft on its normal route. The user kept this restriction (`answer-02.yaml`,
  `reclassification-on-protected-base`): on a protected base queued `session`-depth work goes through Planning and a
  spec Unit, and direct acceptance is unavailable there too; the deletion never rides the session's `dev-<slug>` PR.
  (ADR-session-reclassification-of-a-queued-draft)
- **Session reclassification, conditions**: the draft is `status: draft` with no local or fetched `plan-<slug>`
  (`devkit spec proposal check`, fetch first, as for every deletion) and has no `PADR-*.md` in `decisions/` (its
  workflow gate records do not count). The `session` criteria cannot hold for a draft marked `needs_decompose` (not
  yet classified, `classification.md` §1), a draft with `supersedes` or a depth escalation's draft (each exists
  because a direction must be decided first), so the Host does not propose it for them.
  (ADR-session-reclassification-of-a-queued-draft)
- **Session reclassification, the request** names what goes: the draft and its gate records, its `materials/` (kept
  in Git history only), the `milestone` membership (a `session` task cannot be a member; no hygiene check reports the
  lost member, even for a done or dropped milestone, so the user reviews the milestone's exit condition here), and the
  open feedback that is preserved. The same exchange may also agree the session's intent, which has no record file;
  each decision is answered explicitly. (ADR-session-reclassification-of-a-queued-draft)
- **Session reclassification, the deletion** is one Backlog commit on the base checkout, before the session starts,
  outside the worktree and PR policies like other Backlog deletions. This record is its authority. In the same commit
  it preserves open feedback and strikes through incoming references on the base, promoted feedback dispositions
  included, per feedback retirement (steps 1 to 4), so nothing dangles. The message states the user's decision and the
  reason ("depth proposal -> session on the user's decision: <reason>"). Right after committing it, before the session
  starts, the Host names the deletion commit to the user, so a session lost before its report still leaves the way
  back known. (ADR-session-reclassification-of-a-queued-draft)
- **Session reclassification, a new slug**: the session, its `dev-<slug>` and any Unit a later raise adds use a slug
  other than the deleted draft's (01 §7.4: a reused slug blurs the work), so a `PROP-<slug>` mention merged later from
  another branch is never rewritten as a handoff. (ADR-session-reclassification-of-a-queued-draft)
- **Session reclassification, the session** then starts through inline Planning (01 §6.1): its intent is agreed in
  the conversation, since the draft's `plan-intent` record goes with the draft, and it follows the `session` rules,
  raising to `spec` when a lasting design record, a contract change or a Living Spec change turns out to be needed.
  Its final report names the deletion commit. If it ends without integrating, the recovery is `git revert` of the
  deletion commit, on the user's decision, which restores the draft with its intent record, milestone, feedback and
  references when no later commit changed those paths; otherwise the Host resolves the conflicts with the user, and a
  milestone closed since pickup is reviewed again for the restored member (01 §7.2: undo by revert, never a reset).
  (ADR-session-reclassification-of-a-queued-draft)
- **Scope of the exception**: it is the only lowering besides a proposal's handoff, and it applies only to a queued
  draft before Planning; a proposal in review or accepted, and a spec Unit, are never lowered. No command or tool
  check is added: the deletion uses the existing check, the conditions are visible to the Host, and the commit gate's
  link check and `RULE-document-reference` catch a reference left dangling. The strategy layer's 01 §2.2 states the
  exception first. (ADR-session-reclassification-of-a-queued-draft)

---

## 5. Consequences

- **Positive**:
  - Each axis answers one question; a `session` task needs no Unit at any effort. (ADR-task-kind-and-planning-depth)
  - `devkit spec new <slug> --workflow sdd-spec-bugfix` and a handoff of a proposal with `task_kind: bugfix` create a
    bundle the bugfix stages can drive from `characterize` on. (ADR-bugfix-bundles-start-with-spec-only)
- **Negative / Risks**:
  - Every workflow id, gate name and skill text changed at once. (ADR-task-kind-and-planning-depth)
  - A tool or agent expecting `plan.md` in every new bundle must check the bound workflow.
    (ADR-bugfix-bundles-start-with-spec-only)
  - A request deleted by session reclassification leaves no Unit: its record is the deletion commit and the session's
    final report, and a revert of that commit is its only way back to the queue. A milestone may lose a member at
    pickup; the request shows it, so the user can review the milestone. (ADR-session-reclassification-of-a-queued-draft)
- **Follow-ups**:
  - `devkit spec new --workflow` takes `sdd-spec-feature` (default) or `sdd-spec-bugfix`; `devkit spec proposal new`
    takes `--task-kind`, `--supersedes` and `--needs-decompose`; `devkit spec proposal handoff` requires
    `status: accepted` and refuses `needs_decompose: true`. (ADR-task-kind-and-planning-depth)
  - `devkit spec policy` refuses `dev-integration = "off"` and reports `[tool.spec] depth_escalation`.
    (ADR-task-kind-and-planning-depth)
  - The worker role splits into a `planning-worker` and a `development-worker` that write their own records and commit
    at stage boundaries; the reconciler verifies the implementer's reconcile at `activity-effort` `high` instead of
    drafting it. (ADR-task-kind-and-planning-depth)
  - Completed specs bound to the retired workflow ids keep their binding as history. (ADR-task-kind-and-planning-depth)
  - The lowering rule gains one stated exception in 01 §2.2 and Q19, `classification.md` §3, the bundle `AGENTS.md`,
    `CAP-HARN-agent-guidance` and the `CAP-DLV-delivery-workflows` non-goal on depth changes; `backlog.md` grants the
    deletion, and `feedback-retirement.md`, `CAP-DLV-proposal-incubation` §3.1, the `sdd-proposal` feedback paragraph
    and 01 §6.2 list it among the deletions that preserve open feedback.
    (ADR-session-reclassification-of-a-queued-draft)

---

## 6. Confirmation

- `RULE-task-coverage` skips a spec without `tasks.md`, so a bugfix bundle passes `lint-clean` at `characterize`.
- The commit gate's link check and `RULE-document-reference` catch a reference a session reclassification left
  dangling.
- Otherwise review only.
