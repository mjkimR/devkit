---
id: PADR-frontmatter-only-decision-status
title: Frontmatter-only decision status and date
summary: "For ADR and PADR status, date and whole supersession, we keep them only in the frontmatter and drop the body metadata block from the template, scaffold, handoff and existing ADRs, to remove a synchronization path and rote fields, accepting a one-time edit of 71 ADR bodies."
proposal: PROP-adr-body-metadata-removal
status: draft
created_at: 2026-11-17
---

# [PADR-frontmatter-only-decision-status] Frontmatter-only decision status and date

## 1. Context & Problem Statement

The decision template opens the body with a metadata list: `- **Status**`, `- **Date**`, `- **Deciders**` and
`- **Involved Components/Capabilities**`. Status and Date copy the frontmatter `status` and `created_at`, and the
superseded form copies `superseded_by`. The PADR scaffold writes `- **Status**: Draft` and `- **Date**`, and the
proposal handoff rewrites the first visible `- **Status**: Draft|Proposed` line to `Accepted` when it promotes a PADR
(`CAP-DLV-proposal-lifecycle` handoff step 4); integration tests pin both.

At this proposal's base, 71 of the 94 ADRs carry the block and every Status and Date value agrees with the
frontmatter; 27 carry Deciders and 45 Involved Components. No rule, viewer module, `devkit docs` command, handbook
script or supersession reader parses any of these lines; every status reader uses the frontmatter
(`materials/body-status-readers.md`). Once an ADR is accepted, nothing updates its body copy when it is later
superseded, so the copy can only drift.

## 2. Decision Drivers

- One owner per fact: status, date and whole supersession already have a frontmatter field that tools read.
- No code path exists only to keep a copy in step.
- Authors fill no field nobody reads.
- The existing ADR corpus reads the same as new ADRs.
- The change edits wording and metadata only, never a decision.

## 3. Considered Options

- **Drop the block everywhere** (selected): template, scaffold, handoff body pass and the 71 existing blocks go; costs
  one mechanical edit of 71 files.
- **Stop writing it, keep existing blocks**: no corpus edit, but 71 unsynchronized copies stay, the corpus shows two
  layouts, and a later whole supersession leaves a stale `Accepted` in the body.
- **Keep the block and add a rule checking it against the frontmatter**: keeps the copy honest, at the cost of a rule
  maintaining a copy nothing reads.
- **Keep the current state**: the handoff keeps its body pass and authors keep filling Deciders and Involved
  Components by rote.

## 4. Decision Outcome

We decided to drop the body metadata block everywhere, because only that option leaves one owner per fact with no
synchronization code and one layout across the corpus.

- An ADR or PADR states its status, date and whole supersession only in the frontmatter; its body has no Status, Date,
  Deciders or Involved Components line.
- The PADR scaffold writes no body metadata lines; the H1 is followed by `## 1. Context & Problem Statement`.
  → `CAP-DLV-proposal-planning` §4.4 (MUST)
- PADR promotion changes only the frontmatter status to `accepted` and leaves the body status text as written.
  → `CAP-DLV-proposal-lifecycle` handoff step 4 (MUST)
- A partly superseded ADR keeps its "Superseded in part by" lines, each a paragraph of its own below the H1.
  → `CAP-DLV-proposal-lifecycle` handoff step 4 (MUST)
- The existing blocks are removed in one wording and metadata repair that changes no decision, which the
  `docs/decisions/` ledger allows without a superseding ADR.

## 5. Consequences

- **Positive**: the handoff loses `_DRAFT_BODY_STATUS` and its body pass; status has one owner; an ADR opens with its
  partial-supersession pointers or its context.
- **Negative / Risks**: a PADR scaffolded before the change and handed off after it keeps `- **Status**: Draft` in
  its accepted ADR body.
- **Follow-ups**: when a promoted ADR still carries the block, the change that integrates it removes the block as the
  same wording repair.

## 6. Confirmation

- `packages/devkit-spec/tests/integration/features/proposals/test_proposal_scaffold.py` asserts the PADR scaffold has
  no `- **Status**` or `- **Date**` line.
- `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py` asserts promotion changes the
  frontmatter status and leaves the body status text unchanged.
- A template test under `packages/devkit-docs/tests/integration/bundles/docs/` asserts the decision template has no
  metadata block.
- Review step: after the repair, `rg '^- \*\*(Status|Date|Deciders|Involved Components/Capabilities)\*\*'
  docs/decisions` finds only body content that is not the block (at this base, the milestone lifecycle item of
  `ADR-roadmap-and-milestones-ledger`).
