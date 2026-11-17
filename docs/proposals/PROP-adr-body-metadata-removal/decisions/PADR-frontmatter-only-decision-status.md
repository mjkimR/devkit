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
script or supersession reader parses any of these lines; every status reader uses the frontmatter. Backticked IDs in
Involved Components lines do count as body references, and in about 20 ADRs that line is their only mention
(`materials/body-status-readers.md`). Once an ADR is accepted, nothing updates its body copy when it is later
superseded, so the copy can only drift.

## 2. Decision Drivers

- One owner per fact: status, date and whole supersession already have a frontmatter field that tools read.
- No code path exists only to keep a copy in step.
- Authors fill no field nobody reads.
- The existing ADR corpus reads the same as new ADRs.
- The change edits wording and metadata only, never a decision.

## 3. Considered Options

- **Drop the block everywhere** (selected): template, scaffold, handoff rewrite and the 71 existing blocks go; costs
  one mechanical edit of 71 files and a small deletion pass for PADRs scaffolded before the change.
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
  → CAP-DLV-proposal-planning §4.4 (MUST, planned wording)
- PADR promotion sets the frontmatter status to `accepted` and rewrites no body status; it deletes the block an earlier
  scaffold wrote, so a PADR scaffolded before the change reaches the ledger without a stale `Draft`.
  → CAP-DLV-proposal-lifecycle handoff step 4 (MUST, planned wording)
- Removing the block leaves every "Superseded in part by" line where it is.
- The existing blocks are removed in one wording and metadata repair that changes no decision, which the
  `docs/decisions/` ledger allows without a superseding ADR. A backticked ID that only the Involved Components line
  mentioned moves into one Context sentence, so reference edges stay.

## 5. Consequences

- **Positive**: the handoff loses `_DRAFT_BODY_STATUS` and its body pass; status has one owner; an ADR opens with its
  partial-supersession pointers or its context.
- **Negative / Risks**: the handoff keeps a small deletion pass for the legacy block; a hand-edited legacy block
  that does not match it (for example a Deciders line) stays in the promoted ADR.
- **Follow-ups**: remove the deletion pass when no supported devkit-spec release scaffolds the block any more; a
  promoted ADR that still carries part of the block gets the same wording repair.

## 6. Confirmation

- `packages/devkit-spec/tests/integration/features/proposals/test_proposal_scaffold.py` asserts the PADR scaffold has
  no `- **Status**` or `- **Date**` line.
- `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py` asserts promotion accepts
  the frontmatter status, deletes a legacy scaffold block and leaves fenced, indented and commented status lines
  unchanged.
- A template test under `packages/devkit-docs/tests/integration/bundles/docs/` asserts the decision template has no
  metadata block.
- `devkit rules check docs/decisions` passes after the repair (`RULE-decision-supersession`,
  `RULE-document-reference`).
- Review step: after the repair, `rg '^- \*\*(Status|Date|Deciders|Involved Components/Capabilities)\*\*'
  docs/decisions` finds only body content that is not the block (at this base, the milestone lifecycle item of
  `ADR-roadmap-and-milestones-ledger`), and no indented continuation line is left directly below the H1 or the
  pointers.
