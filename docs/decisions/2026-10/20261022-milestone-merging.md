---
id: ADR-milestone-merging
title: Loosely managed milestone themes and milestone merging
summary: "For loosely managed milestone themes, we recommend rather than require coarse granularity and let the user merge small milestones of any status into a broader theme that keeps their IDs as aliases, to keep every old ID resolvable, accepting that merged done or dropped files leave the tree."
supersedes:
  - ADR-roadmap-and-milestones
status: accepted
created_at: 2026-10-22
---

# [ADR-milestone-merging] Loosely managed milestone themes and milestone merging

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `CAP-DOCS-document-model`, `CAP-HARN-agent-guidance`, `docs/roadmap/`

---

## 1. Context & Problem Statement

`ADR-roadmap-and-milestones` made a milestone a coarse grouping theme, but the roadmap guidance stated granularity and
exit-condition wording as SHOULD and SHOULD NOT, and its Status outcome kept every `done` and `dropped` milestone as a
historical document. Small milestones created before the coarse-theme guidance therefore stayed as separate files
even when one broader theme owned their scope. The repository merged five of them into `MS-maintenance-operations`
(commit `e048c24f`) as a one-off: the theme lists their IDs in `aliases`, their files were deleted and
`devkit rules fix` moved current references. No decision permitted that, and no guidance described it.

---

## 2. Decision Drivers

- Milestones are loosely managed themes reviewed by user and agent together, not a ledger of delivery units.
- Every milestone ID ever referenced stays resolvable through the document model's `aliases`.
- Completed specs and Git already keep the delivery record; a milestone file adds no evidence of delivery.
- A confirmed completion is never reopened silently: the user owns every status change.
- No new command, field or rule without a demonstrated need.

---

## 3. Considered Options

### Option 1: Recommendation wording and user-decided merging (Selected)
- **Overview**: granularity guidance becomes a recommendation; small milestones of any status may merge into a theme
  that keeps their IDs as aliases, through a documented Backlog procedure.
- **Pros**: the roadmap shows themes; old IDs resolve; existing `aliases` and `devkit rules fix` do the mechanics.
- **Cons**: a merged `done` or `dropped` milestone file leaves the tree; its text remains only in Git.

### Option 2: Keep done and dropped milestones as historical documents
- **Overview**: the Status outcome of `ADR-roadmap-and-milestones`; only `planned` and `active` milestones could be
  folded together.
- **Cons**: legacy fragments stay in the roadmap indefinitely, and the theme cannot own the delivered part of its
  scope.

### Option 3: A merge command
- **Overview**: a CLI that rewrites aliases, deletes files and moves references in one step.
- **Cons**: adds a command contract for an occasional Backlog edit that existing tools already cover.

---

## 4. Decision Outcome

We adopt **Option 1**.

- **Tone**: granularity and exit-condition guidance in the roadmap README and the milestone template is a
  recommendation: a broader multi-unit theme is preferred over a milestone that only sequences one proposal, and
  phase-level exit conditions are recommended.
- **Merging**: small milestones of any status (`planned`, `active`, `done`, `dropped`) MAY merge into a broader theme
  milestone, existing or new, on the user's Backlog decision on a concrete candidate.
  - The theme lists every merged ID in `aliases` and states the combined goal and exit condition.
  - The merged files are deleted in the same commit, and `devkit rules fix` moves current references; `depends_on`
    edges between the merged milestones are removed.
  - Completed specs and Git keep the delivery record.
  - Remaining scope moves to draft proposals in the theme. The theme is `planned` or `active` while scope remains and
    becomes `done` only through both Completion review confirmations.
- **Partial supersession**: this replaces the clause "`done` and `dropped` milestones stay as historical documents"
  of the Status outcome of `ADR-roadmap-and-milestones`. A `done` or `dropped` milestone that is not merged stays a
  historical document as before.
- **Kept**: a merge is not an in-place extension. Extending a `done` milestone's own scope still needs the user's
  reopen to `active` with both assertions reset, or another milestone (Reopen outcome of
  `ADR-roadmap-and-milestones`).

**Rationale**: merging through `aliases` keeps every ID resolvable and leaves delivery evidence where it already is,
while the user's Backlog decision preserves authority over status changes.

---

## 5. Consequences

- **Positive**: the roadmap converges on themes; the `MS-maintenance-operations` merge is the documented procedure.
- **Negative / Risks**: a merged milestone's text is read from Git, not from the tree. A merge reduces the number of
  `done` milestones that the roadmap review of `ADR-roadmap-and-milestones` counts; its date trigger still applies.
- **Follow-ups**: none.

---

## 6. Confirmation

- `packages/devkit-spec/tests/integration/bundles/spec/test_milestone_completion_guidance.py` pins the recommendation
  wording, the merge procedure and the kept reopen rule in the shipped guidance.
- `RULE-document-reference` reports alias references and `depends_on` cycles left by a merge.
